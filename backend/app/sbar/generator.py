"""SBAR (Situation, Background, Assessment, Recommendation) Clinical Report Generator.

Transforms student intake data and explainable ML risk outputs into a structured,
standardized clinician handover document optimized for campus medical centers.
"""
from datetime import datetime, timezone
from typing import Dict, List, Optional
from app.core.config import MEDICAL_DISCLAIMER
from app.models.enums import RiskTierEnum
from app.models.schemas import (
    ConditionRiskResult,
    MicronutrientDetails,
    SbarReport,
    SbarSection,
    StudentIntakeRequest,
)


def generate_sbar_report(
    intake: StudentIntakeRequest,
    conditions: Dict[str, ConditionRiskResult],
    micronutrient_details: MicronutrientDetails,
    screening_id: str,
    urgent_flag: bool = False,
    urgent_reason: Optional[str] = None
) -> SbarReport:
    """Generates a complete SBAR clinical report object."""
    timestamp = datetime.now(timezone.utc).isoformat()

    # 1. SITUATION
    anemia_res = conditions.get("anemia")
    prediab_res = conditions.get("prediabetes")
    micro_res = conditions.get("micronutrients")

    elevated_conditions = [
        f"{c.title} ({c.calibrated_risk_pct}%)"
        for c in conditions.values()
        if c.tier == RiskTierEnum.elevated
    ]
    moderate_conditions = [
        f"{c.title} ({c.calibrated_risk_pct}%)"
        for c in conditions.values()
        if c.tier == RiskTierEnum.moderate
    ]

    situation_lead = (
        f"{intake.age}-year-old {intake.sex} student completed non-invasive multi-condition health risk screening. "
    )
    if elevated_conditions:
        situation_lead += f"Urgent/Elevated risk pattern identified in: {', '.join(elevated_conditions)}. "
    elif moderate_conditions:
        situation_lead += f"Moderate risk pattern identified in: {', '.join(moderate_conditions)}. "
    else:
        situation_lead += "All primary screening domains fall within low-risk maintenance thresholds. "

    if urgent_flag and urgent_reason:
        situation_lead += f"CLINICAL ATTENTION REQUIRED: {urgent_reason}."

    situation_bullets = [
        f"Student Age & Sex: {intake.age} yo, {intake.sex}",
        f"Screening Reference ID: {screening_id}",
        f"Elevated Domains: {', '.join(elevated_conditions) if elevated_conditions else 'None'}",
        f"Moderate Domains: {', '.join(moderate_conditions) if moderate_conditions else 'None'}"
    ]
    if urgent_flag:
        situation_bullets.insert(0, f"RED FLAG ALERT: {urgent_reason or 'Critical symptom threshold exceeded'}")

    situation_section = SbarSection(
        title="Situation",
        content=situation_lead.strip(),
        bullet_points=situation_bullets
    )

    # 2. BACKGROUND
    bg_bullets = [
        f"Anthropometrics: Height {intake.height_cm} cm, Weight {intake.weight_kg} kg | BMI {intake.bmi} kg/m² ({intake.bmi_category}) | WHtR {intake.whtr} ({intake.whtr_category})",
        f"Dietary Regimen: {intake.diet_pattern.title()} pattern, iron food frequency '{intake.iron_rich_food_freq}'",
        f"Sunlight & Activity: Sunlight '{intake.weekly_sunlight_hours}', Sunscreen regular use: {intake.sunscreen_regular_use}, Activity level: {intake.physical_activity_level}",
        f"Sleep & Fatigue: Nightly sleep {intake.sleep_hours_per_night or 7.0}h, Subjective fatigue score {intake.fatigue_severity_score}/10"
    ]
    if intake.sex == "female":
        bg_bullets.append(
            f"Reproductive Indicators: Menstrual flow '{intake.menstrual_flow_intensity}', Irregular cycles: {intake.menstrual_cycle_irregular}"
        )
    if intake.family_history_diabetes or intake.family_history_anemia:
        bg_bullets.append(
            f"Family History: Diabetes ({intake.family_history_diabetes}), Anemia ({intake.family_history_anemia})"
        )
    if intake.resting_heart_rate or intake.blood_pressure_systolic:
        bp_str = f"{intake.blood_pressure_systolic}/{intake.blood_pressure_diastolic} mmHg" if intake.blood_pressure_systolic else "Unrecorded"
        bg_bullets.append(f"Recorded Vitals: Resting HR {intake.resting_heart_rate or 'N/A'} bpm, BP {bp_str}")

    background_section = SbarSection(
        title="Background",
        content=(
            f"Patient is a university student with self-reported lifestyle profile: {intake.diet_pattern} diet, "
            f"sleep duration of {intake.sleep_hours_per_night or 7.0} hours, and fatigue score {intake.fatigue_severity_score}/10."
        ),
        bullet_points=bg_bullets
    )

    # 3. ASSESSMENT
    assess_bullets = []
    if anemia_res:
        top_anemia = ", ".join([d.display_label for d in anemia_res.positive_drivers[:2]]) or "No dominant risk drivers"
        assess_bullets.append(
            f"Anaemia Risk: {anemia_res.calibrated_risk_pct}% [{anemia_res.tier.value.upper()}] — Key factors: {top_anemia}"
        )
    if prediab_res:
        top_prediab = ", ".join([d.display_label for d in prediab_res.positive_drivers[:2]]) or "No dominant risk drivers"
        assess_bullets.append(
            f"Pre-Diabetes / Metabolic Risk: {prediab_res.calibrated_risk_pct}% [{prediab_res.tier.value.upper()}] — Key factors: {top_prediab}"
        )
    if micro_res:
        assess_bullets.append(
            f"Micronutrient Deficiency Index: {micro_res.calibrated_risk_pct}% [{micro_res.tier.value.upper()}] — "
            f"D3: {micronutrient_details.vitamin_d3_risk_pct}%, B12: {micronutrient_details.vitamin_b12_risk_pct}%, "
            f"Calcium: {micronutrient_details.calcium_risk_pct}%, Functional Iron Gap: {micronutrient_details.iron_deficiency_risk_pct}%"
        )

    assessment_section = SbarSection(
        title="Assessment",
        content=(
            "Multivariate risk model outputs highlight specific physiological vulnerabilities requiring targeted evaluation."
        ),
        bullet_points=assess_bullets
    )

    # 4. RECOMMENDATION
    recs: List[str] = []
    labs: List[str] = []

    # Lab recommendations based on risk tiers
    if anemia_res and anemia_res.calibrated_risk_pct >= 40.0:
        labs.extend(["Complete Blood Count (CBC) with RBC Indices (MCV, MCH)", "Serum Ferritin & Total Iron Binding Capacity (TIBC)"])
        recs.append("Assess for microcytic hypochromic anaemia; evaluate dietary iron bioavailability and menstrual volume.")

    if prediab_res and prediab_res.calibrated_risk_pct >= 30.0:
        labs.extend(["Fasting Plasma Glucose (FPG)", "Glycated Hemoglobin (HbA1c)", "Fasting Lipid Profile"])
        recs.append("Screen for impaired fasting glucose / insulin resistance; provide dietary guidance on glycemic load and physical activity.")

    if micronutrient_details.vitamin_d3_risk_pct >= 45.0:
        labs.append("Serum 25-Hydroxyvitamin D [25(OH)D]")
        recs.append("Consider Vitamin D3 supplementation (1,000-2,000 IU/day) or clinical repletion protocol if deficient.")

    if micronutrient_details.vitamin_b12_risk_pct >= 45.0:
        labs.extend(["Serum Vitamin B12", "Serum Folate", "Serum Methylmalonic Acid (MMA)"])
        recs.append("Recommend sublingual cobalamin supplementation for plant-based nutrition.")

    if micronutrient_details.calcium_risk_pct >= 45.0:
        labs.append("Serum Total & Ionized Calcium, Serum Albumin")
        recs.append("Evaluate dietary calcium adequacy and review caffeine intake.")

    if not recs:
        recs.append("No immediate laboratory workup indicated. Reiterate routine annual wellness examination and balanced campus lifestyle.")

    if not labs:
        labs.append("Routine annual wellness screening panel as indicated by campus health protocol.")

    # Deduplicate labs while preserving order
    unique_labs = list(dict.fromkeys(labs))

    recommendation_section = SbarSection(
        title="Recommendation",
        content="Suggested clinical follow-up and diagnostic panel confirmation for campus medical provider consideration.",
        bullet_points=recs
    )

    return SbarReport(
        screening_id=screening_id,
        session_id=screening_id,
        timestamp=timestamp,
        generated_at=timestamp,
        situation=situation_section,
        background=background_section,
        assessment=assessment_section,
        recommendation=recommendation_section,
        confirmatory_labs_suggested=unique_labs,
        disclaimer=MEDICAL_DISCLAIMER
    )
