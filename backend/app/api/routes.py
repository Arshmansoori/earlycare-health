"""FastAPI router endpoints for EarlyCare: /screen, /explain, /export-sbar, /health."""
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from fastapi import APIRouter, HTTPException, status, Depends
from app.core.config import MEDICAL_DISCLAIMER, PROJECT_NAME, VERSION
from app.core.security import generate_anonymous_screening_id
from app.core.auth import (
    create_access_token,
    parse_google_credential,
    get_current_user,
    get_optional_current_user,
)
from app.db.database import (
    get_or_create_user,
    save_screening_for_user,
    get_user_screenings,
    get_screening_by_id,
    delete_user_screening,
)
from app.models.enums import RiskTierEnum
from app.models.schemas import (
    CalculatedVitals,
    ConditionExplanation,
    ExplainResponse,
    HealthStatusResponse,
    RadarAxis,
    SbarResponse,
    ScreenResponse,
    StudentIntakeRequest,
    CounterfactualSimulationRequest,
    CounterfactualSimulationResponse,
    SevenDayDietBlueprint,
    GoogleAuthRequest,
    UserProfileResponse,
    AuthResponse,
    SaveScreeningRequest,
    SavedScreeningSummary,
)
from app.ml.anemia import (
    BETA_0_ANEMIA,
    METADATA_MAP as METADATA_MAP_ANEMIA,
    evaluate_anemia_risk,
)
from app.ml.prediabetes import (
    BETA_0_PREDIABETES,
    METADATA_MAP as METADATA_MAP_PREDIAB,
    evaluate_prediabetes_risk,
)
from app.ml.micronutrients import (
    BETA_0_D3,
    METADATA_MAP_MICRO,
    evaluate_micronutrients_risk,
)
from app.ml.explainability import compute_additive_feature_attribution
from app.ml.simulation import run_counterfactual_simulation, generate_campus_diet_blueprint
from app.sbar.generator import generate_sbar_report

router = APIRouter()


@router.get("/health", response_model=HealthStatusResponse, tags=["Health"])
async def get_health_status() -> HealthStatusResponse:
    """Service health check returning model registry status and SaMD compliance mode."""
    return HealthStatusResponse(
        status="healthy",
        service=PROJECT_NAME,
        version=VERSION,
        calibrated_models=[
            "anemia",
            "prediabetes",
            "micronutrients",
            "vitamin_d3",
            "vitamin_b12",
            "calcium",
            "iron"
        ],
        samd_status="non_diagnostic_screening_v1"
    )


@router.post("/screen", response_model=ScreenResponse, tags=["Screening"])
async def run_screening(
    intake: StudentIntakeRequest,
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_current_user),
) -> ScreenResponse:
    """
    Evaluates multi-condition health risk across hematological, metabolic, and micronutrient axes.
    Returns calibrated percentage probabilities, risk tiers, XAI driver badges, radar axes,
    calculated vitals, and SBAR report summary.
    """
    screening_id = generate_anonymous_screening_id()
    timestamp_utc = datetime.now(timezone.utc).isoformat()

    # 1. Run ML Stratifiers
    anemia_res, anemia_attribs, anemia_pct = evaluate_anemia_risk(intake)
    prediab_res, prediab_attribs, prediab_pct = evaluate_prediabetes_risk(intake)
    micro_res, micro_details, micro_attribs, micro_pct = evaluate_micronutrients_risk(intake)

    conditions = {
        "anemia": anemia_res,
        "prediabetes": prediab_res,
        "micronutrients": micro_res
    }

    # 2. Check for Red-Flag / Urgent Consultation Signals
    urgent_flag = False
    urgent_reason: Optional[str] = None

    if intake.chest_pain_or_syncope_reported:
        urgent_flag = True
        urgent_reason = "Student reported chest pain or fainting episode (syncope)"
    elif intake.fasting_blood_glucose_mgdl is not None and intake.fasting_blood_glucose_mgdl >= 126.0:
        urgent_flag = True
        urgent_reason = f"Markedly elevated fasting glucose ({intake.fasting_blood_glucose_mgdl} mg/dL) in diagnostic range"
    elif intake.hemoglobin_g_dl is not None and intake.hemoglobin_g_dl < 8.0:
        urgent_flag = True
        urgent_reason = f"Critical hemoglobin level ({intake.hemoglobin_g_dl} g/dL) requiring prompt medical evaluation"
    elif intake.fatigue_severity_score >= 9 and str(intake.orthostatic_dizziness).lower() in ("daily", "3"):
        urgent_flag = True
        urgent_reason = "Severe disabling fatigue (score >=9) accompanied by daily postural dizziness"

    # 3. Overall Risk Tier & Highest Condition
    scores = {
        "anemia": anemia_pct,
        "prediabetes": prediab_pct,
        "micronutrients": micro_pct
    }
    highest_condition_key = max(scores, key=scores.get)
    highest_score = scores[highest_condition_key]

    if highest_score >= 70.0:
        overall_tier = RiskTierEnum.elevated
    elif highest_score >= 30.0:
        overall_tier = RiskTierEnum.moderate
    else:
        overall_tier = RiskTierEnum.low

    # Formulate overall clinical summary
    elevated_names = [c.title for c in conditions.values() if c.tier == RiskTierEnum.elevated]
    moderate_names = [c.title for c in conditions.values() if c.tier == RiskTierEnum.moderate]

    if elevated_names:
        overall_summary = f"Elevated risk pattern observed in: {', '.join(elevated_names)}. Prompt clinical review recommended."
    elif moderate_names:
        overall_summary = f"Moderate lifestyle risk pattern detected in: {', '.join(moderate_names)}. Targeted lifestyle adjustments advised."
    else:
        overall_summary = "All evaluated health domains are currently within low-risk maintenance thresholds."

    # 4. Construct Radar Chart Axes (6 Axes)
    fatigue_axis_score = round(min(intake.fatigue_severity_score * 10.0, 100.0), 1)
    radar_axes = [
        RadarAxis(axis_label="Hematological", risk_score=anemia_pct),
        RadarAxis(axis_label="Metabolic", risk_score=prediab_pct),
        RadarAxis(axis_label="Vitamin D3", risk_score=micro_details.vitamin_d3_risk_pct),
        RadarAxis(axis_label="Vitamin B12", risk_score=micro_details.vitamin_b12_risk_pct),
        RadarAxis(axis_label="Bone & Calcium", risk_score=micro_details.calcium_risk_pct),
        RadarAxis(axis_label="Fatigue Index", risk_score=fatigue_axis_score)
    ]

    # 5. Calculated Anthropometrics
    calc_vitals = CalculatedVitals(
        bmi=intake.bmi,
        bmi_category=intake.bmi_category,
        whtr=intake.whtr,
        whtr_category=intake.whtr_category
    )

    # 6. SBAR Report Generation
    sbar_report = generate_sbar_report(
        intake=intake,
        conditions=conditions,
        micronutrient_details=micro_details,
        screening_id=screening_id,
        urgent_flag=urgent_flag,
        urgent_reason=urgent_reason
    )

    # 7. Collect All Actionable Recommendations
    all_recs: List[str] = []
    for c in conditions.values():
        all_recs.extend(c.lifestyle_recommendations)

    screen_res = ScreenResponse(
        screening_id=screening_id,
        session_id=screening_id,
        timestamp_utc=timestamp_utc,
        timestamp=timestamp_utc,
        overall_risk_summary=overall_summary,
        overall_risk_tier=overall_tier,
        highest_risk_condition=highest_condition_key,
        urgent_consult_flag=urgent_flag,
        urgent_consult_reason=urgent_reason,
        conditions=conditions,
        micronutrient_details=micro_details,
        radar_axes=radar_axes,
        calculated_vitals=calc_vitals,
        sbar_report=sbar_report,
        recommendations=all_recs,
        disclaimer=MEDICAL_DISCLAIMER
    )

    if current_user:
        try:
            save_screening_for_user(
                user_id=current_user["id"],
                screening_id=screening_id,
                intake_data=intake.model_dump(),
                result_data=screen_res.model_dump()
            )
        except Exception:
            pass

    return screen_res


@router.post("/explain", response_model=ExplainResponse, tags=["Explainability"])
async def explain_risk_factors(intake: StudentIntakeRequest) -> ExplainResponse:
    """
    Dedicated Explainable AI endpoint providing mathematical additive feature attribution,
    log-odds displacement, and probability impact breakdown for all conditions.
    """
    session_id = generate_anonymous_screening_id()
    timestamp_utc = datetime.now(timezone.utc).isoformat()

    # 1. Anaemia Attribution
    anemia_res, anemia_attribs, anemia_pct = evaluate_anemia_risk(intake)
    anemia_pos, anemia_prot, anemia_cons = compute_additive_feature_attribution(
        beta_0=BETA_0_ANEMIA,
        log_odds_attribs=anemia_attribs,
        metadata_map=METADATA_MAP_ANEMIA
    )
    anemia_expl = ConditionExplanation(
        condition_id="anemia",
        condition_name="Anaemia Risk Stratification",
        predicted_probability_pct=anemia_pct,
        baseline_probability_pct=anemia_cons["baseline_prob_pct"],
        net_displacement_pct=anemia_cons["net_displacement_pct"],
        positive_drivers=anemia_pos,
        protective_drivers=anemia_prot,
        conservation_check=anemia_cons
    )

    # 2. Pre-Diabetes Attribution
    prediab_res, prediab_attribs, prediab_pct = evaluate_prediabetes_risk(intake)
    prediab_pos, prediab_prot, prediab_cons = compute_additive_feature_attribution(
        beta_0=BETA_0_PREDIABETES,
        log_odds_attribs=prediab_attribs,
        metadata_map=METADATA_MAP_PREDIAB
    )
    prediab_expl = ConditionExplanation(
        condition_id="prediabetes",
        condition_name="Pre-Diabetes / Metabolic Risk",
        predicted_probability_pct=prediab_pct,
        baseline_probability_pct=prediab_cons["baseline_prob_pct"],
        net_displacement_pct=prediab_cons["net_displacement_pct"],
        positive_drivers=prediab_pos,
        protective_drivers=prediab_prot,
        conservation_check=prediab_cons
    )

    # 3. Micronutrients Attribution
    micro_res, micro_details, micro_attribs, micro_pct = evaluate_micronutrients_risk(intake)
    micro_pos, micro_prot, micro_cons = compute_additive_feature_attribution(
        beta_0=BETA_0_D3,
        log_odds_attribs=micro_attribs,
        metadata_map=METADATA_MAP_MICRO
    )
    micro_expl = ConditionExplanation(
        condition_id="micronutrients",
        condition_name="Micronutrient Deficiency Matrix",
        predicted_probability_pct=micro_pct,
        baseline_probability_pct=micro_cons["baseline_prob_pct"],
        net_displacement_pct=micro_cons["net_displacement_pct"],
        positive_drivers=micro_pos,
        protective_drivers=micro_prot,
        conservation_check=micro_cons
    )

    return ExplainResponse(
        session_id=session_id,
        screening_id=session_id,
        timestamp_utc=timestamp_utc,
        explanations={
            "anemia": anemia_expl,
            "prediabetes": prediab_expl,
            "micronutrients": micro_expl
        }
    )


@router.post("/export-sbar", response_model=SbarResponse, tags=["Clinical Handover"])
async def export_sbar_report(intake: StudentIntakeRequest) -> SbarResponse:
    """
    Exports a structured SBAR (Situation, Background, Assessment, Recommendation)
    clinical summary report complete with suggested confirmatory laboratory tests.
    """
    screening_id = generate_anonymous_screening_id()

    anemia_res, _, _ = evaluate_anemia_risk(intake)
    prediab_res, _, _ = evaluate_prediabetes_risk(intake)
    micro_res, micro_details, _, _ = evaluate_micronutrients_risk(intake)

    conditions = {
        "anemia": anemia_res,
        "prediabetes": prediab_res,
        "micronutrients": micro_res
    }

    # Red-flag evaluation
    urgent_flag = False
    urgent_reason = None
    if intake.chest_pain_or_syncope_reported:
        urgent_flag = True
        urgent_reason = "Reported chest pain or fainting episode (syncope)"
    elif intake.fasting_blood_glucose_mgdl is not None and intake.fasting_blood_glucose_mgdl >= 126.0:
        urgent_flag = True
        urgent_reason = "Fasting glucose >= 126 mg/dL in diabetic threshold"

    report = generate_sbar_report(
        intake=intake,
        conditions=conditions,
        micronutrient_details=micro_details,
        screening_id=screening_id,
        urgent_flag=urgent_flag,
        urgent_reason=urgent_reason
    )

    return SbarResponse(**report.model_dump())


@router.post("/simulate", response_model=CounterfactualSimulationResponse, tags=["What-If Counterfactual"])
async def simulate_lifestyle_impact(req: CounterfactualSimulationRequest) -> CounterfactualSimulationResponse:
    """
    Simulates lifestyle counterfactuals (sleep, timing tea away from meals, post-meal walks,
    sun exposure) and returns absolute risk percentage improvements in real time.
    """
    return run_counterfactual_simulation(req)


@router.post("/diet-blueprint", response_model=SevenDayDietBlueprint, tags=["Campus Nutrition"])
async def get_campus_diet_blueprint(intake: StudentIntakeRequest) -> SevenDayDietBlueprint:
    """
    Generates a personalized, budget-friendly 7-day campus meal and habit blueprint
    tailored to the student's detected risk domains and dietary preferences.
    """
    _, _, a_pct = evaluate_anemia_risk(intake)
    _, _, p_pct = evaluate_prediabetes_risk(intake)
    _, micro_details, _, _ = evaluate_micronutrients_risk(intake)

    return generate_campus_diet_blueprint(
        intake=intake,
        a_risk=a_pct,
        p_risk=p_pct,
        d3_risk=micro_details.vitamin_d3_risk_pct
    )


# ==============================================================================
# Authentication & User Profile Endpoints
# ==============================================================================

@router.post("/auth/google", response_model=AuthResponse, tags=["Authentication"])
async def authenticate_with_google(req: GoogleAuthRequest) -> AuthResponse:
    """Authenticates student via Google ID token or campus student profile."""
    email = None
    name = req.name
    picture = req.picture
    google_id = None

    if req.credential:
        parsed = parse_google_credential(req.credential)
        if parsed:
            email = parsed["email"]
            name = parsed.get("name") or name
            picture = parsed.get("picture") or picture
            google_id = parsed.get("google_id")
    
    if not email and req.email:
        email = req.email.strip().lower()

    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Valid Google credential or student email address required for authentication."
        )

    user = get_or_create_user(email=email, name=name, picture=picture, google_id=google_id)
    token = create_access_token(user_id=user["id"], email=user["email"])

    return AuthResponse(
        access_token=token,
        token_type="Bearer",
        user=UserProfileResponse(
            id=user["id"],
            email=user["email"],
            name=user["name"],
            picture=user["picture"] or "",
            created_at=user["created_at"],
            last_login=user["last_login"]
        )
    )


@router.get("/auth/me", response_model=UserProfileResponse, tags=["Authentication"])
async def get_current_user_profile(user: Dict[str, Any] = Depends(get_current_user)) -> UserProfileResponse:
    """Returns the authenticated student's profile."""
    return UserProfileResponse(
        id=user["id"],
        email=user["email"],
        name=user["name"],
        picture=user["picture"] or "",
        created_at=user["created_at"],
        last_login=user["last_login"]
    )


# ==============================================================================
# Saved Screenings & Timeline History Endpoints
# ==============================================================================

@router.post("/results/save", tags=["Screening History"])
async def save_existing_screening(
    req: SaveScreeningRequest,
    user: Dict[str, Any] = Depends(get_current_user)
):
    """Associates a completed screening report with the logged-in user account."""
    res = save_screening_for_user(
        user_id=user["id"],
        screening_id=req.screening_id,
        intake_data=req.intake_data,
        result_data=req.result_data
    )
    return {"status": "saved", "screening_id": req.screening_id, "record_id": res["id"]}


@router.get("/results/history", response_model=List[SavedScreeningSummary], tags=["Screening History"])
async def list_user_screening_history(
    user: Dict[str, Any] = Depends(get_current_user),
    limit: int = 50
) -> List[SavedScreeningSummary]:
    """Returns chronologically ordered health screening summaries for the user."""
    rows = get_user_screenings(user_id=user["id"], limit=limit)
    return [
        SavedScreeningSummary(
            id=r["id"],
            screening_id=r["screening_id"],
            created_at=r["created_at"],
            overall_risk_tier=r["overall_risk_tier"],
            highest_risk_condition=r["highest_risk_condition"],
            anemia_risk_pct=r["anemia_risk_pct"],
            prediabetes_risk_pct=r["prediabetes_risk_pct"],
            micronutrients_risk_pct=r["micronutrients_risk_pct"],
            urgent_consult_flag=bool(r["urgent_consult_flag"])
        )
        for r in rows
    ]


@router.get("/results/{screening_id}", tags=["Screening History"])
async def get_saved_screening_detail(
    screening_id: str,
    user: Dict[str, Any] = Depends(get_current_user)
):
    """Retrieves full original payload and screening result for a past session."""
    data = get_screening_by_id(user_id=user["id"], screening_id=screening_id)
    if not data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Screening record not found")
    return {
        "screening_id": data["screening_id"],
        "created_at": data["created_at"],
        "intake_data": data["intake_data"],
        "result_data": data["result_data"],
    }


@router.delete("/results/{screening_id}", tags=["Screening History"])
async def delete_saved_screening(
    screening_id: str,
    user: Dict[str, Any] = Depends(get_current_user)
):
    """Removes a screening report from user history."""
    deleted = delete_user_screening(user_id=user["id"], screening_id=screening_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Screening record not found")
    return {"status": "deleted", "screening_id": screening_id}
