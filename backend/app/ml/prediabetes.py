"""Pre-Diabetes / Insulin Resistance Metabolic Risk Engine for EarlyCare.

Implements an adapted FINDRISC / American Diabetes Association young-adult
scoring model combining non-invasive adiposity metrics (BMI, Waist-to-Height Ratio),
lifestyle factors (refined carbohydrates, sugary beverage frequency, physical inactivity,
sleep restriction), family history, acanthosis nigricans, and optional clinic glucose/BP vitals.
"""
from typing import Dict, Tuple
from app.models.enums import RiskTierEnum
from app.models.schemas import ConditionRiskResult, StudentIntakeRequest
from app.ml.explainability import (
    compute_additive_feature_attribution,
    sigmoid,
)

BETA_0_PREDIABETES = -2.20  # Calibrated baseline for young adults (~9.9% prevalence)

METADATA_MAP: Dict[str, Dict[str, str]] = {
    "bmi_adiposity": {
        "label": "Body Mass Index (Adiposity)",
        "explanation": "Elevated BMI reflects systemic adipose accumulation and peripheral insulin insensitivity.",
        "rationale": "ADA criteria: BMI >=25 kg/m2 (or >=23 in Asian populations) triggers pre-diabetes screening."
    },
    "visceral_waist_height_ratio": {
        "label": "Waist-to-Height Ratio (Visceral Fat)",
        "explanation": "WHtR measures central/visceral adiposity, which secretes pro-inflammatory adipokines.",
        "rationale": "WHtR >=0.50 confers higher cardiovascular and insulin resistance sensitivity than BMI alone."
    },
    "family_history_diabetes": {
        "label": "Family History of Type 2 Diabetes",
        "explanation": "Genetic predisposition alters beta-cell secretory reserve and hepatic gluconeogenesis.",
        "rationale": "First-degree relative confers 2-3x increased odds of early glucose intolerance."
    },
    "physical_inactivity": {
        "label": "Physical Inactivity / Sedentary Time",
        "explanation": "Skeletal muscle contractions stimulate insulin-independent GLUT4 glucose translocation.",
        "rationale": "<150 minutes/week of moderate physical activity reduces muscle insulin sensitivity."
    },
    "sugary_drinks_fructose": {
        "label": "Sugary & Energy Beverage Intake",
        "explanation": "Rapidly absorbed liquid fructose drives hepatic de novo lipogenesis and hepatic steatosis.",
        "rationale": "High glycemic spikes increase demand on pancreatic beta cells."
    },
    "refined_carb_frequency": {
        "label": "Refined Carbohydrate Diet",
        "explanation": "Frequent consumption of high-glycemic processed starch causes postprandial glycemic excursions.",
        "rationale": "Chronic postprandial hyperinsulinemia downregulates insulin receptor sensitivity."
    },
    "sleep_deprivation_cortisol": {
        "label": "Sleep Deprivation / Disruption",
        "explanation": "Restricted sleep elevates sympathetic tone and morning cortisol, impairing insulin sensitivity.",
        "rationale": "<6 hours of nightly sleep is clinically linked to reduced insulin sensitivity index."
    },
    "acanthosis_nigricans_skin_marker": {
        "label": "Acanthosis Nigricans / Skin Tags",
        "explanation": "Hyperpigmented velvety cutaneous changes indicate severe compensatory hyperinsulinemia.",
        "rationale": "High circulating insulin stimulates IGF-1 receptors on dermal fibroblasts and keratinocytes."
    },
    "osmotic_polyuria_polydipsia": {
        "label": "Osmotic Indicators (Thirst / Frequent Urination)",
        "explanation": "Early renal osmotic threshold symptoms during transient glucose spikes.",
        "rationale": "Marker of impaired glycemic clearance."
    },
    "fasting_plasma_glucose": {
        "label": "Fasting Plasma Glucose (Clinic Vital)",
        "explanation": "Objective laboratory anchor measuring morning basal hepatic glucose output.",
        "rationale": "ADA classification: 100-125 mg/dL defines Impaired Fasting Glucose (Pre-diabetes); >=126 mg/dL diabetes."
    },
    "systolic_blood_pressure": {
        "label": "Resting Blood Pressure",
        "explanation": "Elevated blood pressure is a hallmark component of the metabolic syndrome cluster.",
        "rationale": "Endothelial dysfunction and hyperinsulinemia drive renal sodium retention."
    }
}


def extract_prediabetes_log_odds(intake: StudentIntakeRequest) -> Dict[str, float]:
    """Calculates additive log-odds weights for all pre-diabetes metabolic features."""
    attribs: Dict[str, float] = {}

    # 1. BMI
    bmi = intake.bmi
    if bmi < 22.0:
        w_bmi = -0.40
    elif bmi < 25.0:
        w_bmi = 0.0
    elif bmi < 27.5:
        w_bmi = 0.40
    elif bmi < 30.0:
        w_bmi = 0.75
    elif bmi < 35.0:
        w_bmi = 1.30
    else:
        w_bmi = 1.80
    attribs["bmi_adiposity"] = w_bmi

    # 2. WHtR (Waist-to-Height Ratio)
    whtr = intake.whtr
    if whtr < 0.45:
        w_whtr = -0.35
    elif whtr < 0.50:
        w_whtr = 0.0
    elif whtr < 0.55:
        w_whtr = 0.50
    elif whtr < 0.60:
        w_whtr = 0.90
    else:
        w_whtr = 1.45
    attribs["visceral_waist_height_ratio"] = w_whtr

    # 3. Family History
    fam = intake.family_history_diabetes
    if isinstance(fam, bool):
        w_fam = 0.85 if fam else -0.20
    elif isinstance(fam, int):
        fam_map = {0: -0.20, 1: 0.35, 2: 0.85, 3: 1.40}
        w_fam = fam_map.get(fam, 0.0)
    else:
        s_fam = str(fam).lower()
        if "both" in s_fam or "3" in s_fam:
            w_fam = 1.40
        elif "first" in s_fam or "parent" in s_fam or "true" in s_fam or "2" in s_fam:
            w_fam = 0.85
        elif "second" in s_fam or "grandparent" in s_fam or "1" in s_fam:
            w_fam = 0.35
        else:
            w_fam = -0.20
    attribs["family_history_diabetes"] = w_fam

    # 4. Physical Inactivity
    if intake.physical_activity_min_per_week is not None:
        mins = intake.physical_activity_min_per_week
        if mins >= 240:
            w_act = -0.55
        elif mins >= 150:
            w_act = -0.30
        elif mins >= 60:
            w_act = 0.15
        else:
            w_act = 0.60
    else:
        act_lvl = str(intake.physical_activity_level).lower()
        if act_lvl == "active":
            w_act = -0.55
        elif act_lvl == "moderate":
            w_act = -0.30
        elif act_lvl == "light":
            w_act = 0.15
        else:  # sedentary
            w_act = 0.60
    attribs["physical_inactivity"] = w_act

    # 5. Sugary / Energy Beverages
    sugary = intake.sugary_drinks_weekly_count
    if sugary == 0:
        attribs["sugary_drinks_fructose"] = -0.25
    elif sugary <= 2:
        attribs["sugary_drinks_fructose"] = 0.35
    else:
        attribs["sugary_drinks_fructose"] = 0.80

    # 6. Refined Carbohydrates
    carb_str = str(intake.refined_carb_freq).lower()
    if "low" in carb_str or "rare" in carb_str:
        attribs["refined_carb_frequency"] = -0.20
    elif "high" in carb_str or "frequent" in carb_str:
        attribs["refined_carb_frequency"] = 0.45
    else:
        attribs["refined_carb_frequency"] = 0.15

    # 7. Sleep Deprivation
    sleep = intake.sleep_hours_per_night or 7.0
    if sleep >= 7.0:
        attribs["sleep_deprivation_cortisol"] = -0.20
    elif sleep >= 5.0:
        attribs["sleep_deprivation_cortisol"] = 0.35
    else:
        attribs["sleep_deprivation_cortisol"] = 0.65

    # 8. Acanthosis Nigricans / Skin Tags
    attribs["acanthosis_nigricans_skin_marker"] = 1.50 if intake.acanthosis_nigricans_signs else 0.0

    # 9. Osmotic Symptoms
    poly = str(intake.polyuria_polydipsia).lower()
    if poly in ("marked", "severe", "2", "true"):
        attribs["osmotic_polyuria_polydipsia"] = 0.75
    elif poly in ("mild", "occasional", "1"):
        attribs["osmotic_polyuria_polydipsia"] = 0.30
    else:
        attribs["osmotic_polyuria_polydipsia"] = 0.0

    # 10. Optional Fasting Glucose Anchor
    if intake.fasting_blood_glucose_mgdl is not None:
        glu = intake.fasting_blood_glucose_mgdl
        if glu < 90.0:
            w_glu = -0.80
        elif glu < 100.0:
            w_glu = 0.0
        elif glu < 110.0:
            w_glu = 1.20
        elif glu < 126.0:
            w_glu = 2.00
        else:
            w_glu = 3.00
        attribs["fasting_plasma_glucose"] = w_glu

    # 11. Optional Systolic Blood Pressure Anchor
    if intake.blood_pressure_systolic is not None:
        bp = intake.blood_pressure_systolic
        if bp < 120:
            w_bp = -0.20
        elif bp < 130:
            w_bp = 0.20
        else:
            w_bp = 0.50
        attribs["systolic_blood_pressure"] = w_bp

    return attribs


def evaluate_prediabetes_risk(intake: StudentIntakeRequest) -> Tuple[ConditionRiskResult, Dict[str, float], float]:
    """
    Evaluates calibrated pre-diabetes / insulin resistance risk for a student intake.
    Returns (ConditionRiskResult, log_odds_attribs, prob_pct).
    """
    attribs = extract_prediabetes_log_odds(intake)
    total_z = BETA_0_PREDIABETES + sum(attribs.values())
    prob = sigmoid(total_z)
    prob_pct = round(prob * 100.0, 1)

    # Determine risk tier
    if prob_pct < 30.0:
        tier = RiskTierEnum.low
    elif prob_pct < 70.0:
        tier = RiskTierEnum.moderate
    else:
        tier = RiskTierEnum.elevated

    # Confidence score
    confidence = 0.95 if intake.fasting_blood_glucose_mgdl is not None else 0.89

    # Additive XAI attribution
    pos_drivers, prot_drivers, _ = compute_additive_feature_attribution(
        beta_0=BETA_0_PREDIABETES,
        log_odds_attribs=attribs,
        metadata_map=METADATA_MAP
    )

    # Clinical summary & recommendations
    if tier == RiskTierEnum.elevated:
        summary = (
            f"Elevated metabolic risk ({prob_pct}%). Indicators suggest reduced insulin "
            "sensitivity and predisposition to impaired fasting glucose."
        )
        recommendations = [
            "Request a fasting plasma glucose or HbA1c test during your next campus clinic visit.",
            "Incorporate 150+ minutes of brisk walking or resistance exercise per week to enhance GLUT4 uptake.",
            "Replace sugary beverages, sweetened coffees, and energy drinks with water or herbal infusions.",
            "Focus meals on high-fiber whole foods (beans, vegetables, oats) to stabilize postprandial glucose."
        ]
    elif tier == RiskTierEnum.moderate:
        summary = (
            f"Moderate metabolic risk ({prob_pct}%). Mild lifestyle or adiposity factors "
            "indicate an opportunity for early preventive lifestyle optimization."
        )
        recommendations = [
            "Aim for 30 minutes of moderate activity 4-5 days a week.",
            "Limit high-glycemic snacks and refined white starches during late-night study sessions.",
            "Maintain consistent sleep hygiene (7-8 hours) to support circadian insulin sensitivity."
        ]
    else:
        summary = f"Low metabolic risk ({prob_pct}%). Healthy insulin sensitivity and lifestyle metrics observed."
        recommendations = [
            "Continue your healthy dietary and physical activity habits.",
            "Maintain regular hydration and sleep consistency during academic stress periods."
        ]

    result = ConditionRiskResult(
        domain_key="prediabetes",
        title="Pre-Diabetes / Metabolic Risk",
        calibrated_risk_pct=prob_pct,
        tier=tier,
        confidence_score=confidence,
        clinical_summary=summary,
        positive_drivers=pos_drivers,
        protective_drivers=prot_drivers,
        lifestyle_recommendations=recommendations
    )

    return result, attribs, prob_pct
