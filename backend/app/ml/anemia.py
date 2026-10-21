"""Calibrated Anaemia Risk Stratifier for EarlyCare.

Predicts calibrated anaemia risk probability using non-invasive indicators
(dietary iron bioavailability, menstrual blood loss, fatigue score, postural dizziness,
mucosal pallor, pica cravings, brittle nails) and optional clinic hemoglobin vitals.
"""
from typing import Dict, Tuple
from app.models.enums import RiskTierEnum
from app.models.schemas import ConditionRiskResult, StudentIntakeRequest
from app.ml.explainability import (
    compute_additive_feature_attribution,
    sigmoid,
)

BETA_0_ANEMIA = -1.80  # University student baseline prior (~14.2% base prevalence)

METADATA_MAP: Dict[str, Dict[str, str]] = {
    "biological_sex": {
        "label": "Biological Sex",
        "explanation": "Females experience baseline hematological vulnerability due to regular menstrual cycles.",
        "rationale": "WHO adolescent and young adult physiological risk reference."
    },
    "dietary_iron_bioavailability": {
        "label": "Dietary Pattern",
        "explanation": "Plant-based diets contain non-heme iron which has lower bioavailability than heme iron.",
        "rationale": "Bioavailability of non-heme iron ranges from 5-12% compared to 15-35% for heme iron."
    },
    "iron_rich_food_intake": {
        "label": "Iron-Rich Food Frequency",
        "explanation": "Frequent consumption of legumes, seeds, and fortified grains preserves iron balance.",
        "rationale": "Dietary frequency directly sustains daily transferrin saturation."
    },
    "menstrual_blood_loss": {
        "label": "Menstrual Blood Loss",
        "explanation": "Heavy or prolonged menstrual flow is the leading non-pathological cause of iron depletion.",
        "rationale": "Blood loss >80 mL/cycle depletes reticuloendothelial iron stores rapidly."
    },
    "chronic_fatigue": {
        "label": "Chronic Fatigue Severity",
        "explanation": "Impaired cellular oxygen delivery from subclinical iron deficiency causes persistent fatigue.",
        "rationale": "Correlates with reduced hemoglobin oxygen carrying capacity."
    },
    "orthostatic_dizziness": {
        "label": "Postural Dizziness",
        "explanation": "Frequent lightheadedness upon standing reflects autonomic strain from reduced blood viscosity.",
        "rationale": "Compensatory tachycardia and baroreceptor sensitivity in early hypochromia."
    },
    "mucosal_pallor": {
        "label": "Conjunctival / Palmar Pallor",
        "explanation": "Physical sign indicating decreased microvascular hemoglobin concentration.",
        "rationale": "High diagnostic specificity (>85%) for moderate-to-severe hemoglobin drop."
    },
    "cold_extremities": {
        "label": "Cold Hands & Feet",
        "explanation": "Peripheral vasoconstriction shunts oxygenated blood toward central organs.",
        "rationale": "Thermoregulatory compromise secondary to low tissue ferritin."
    },
    "pica_cravings": {
        "label": "Pica Cravings (Ice / Chalk)",
        "explanation": "Pagophagia (ice chewing) is a classic pathognomonic symptom of profound iron depletion.",
        "rationale": "Directly linked to subcortical dopamine receptor alterations in iron deficiency."
    },
    "brittle_nails_hair": {
        "label": "Brittle Nails / Hair Loss",
        "explanation": "Keratin synthesis relies on iron-dependent ribonucleotide reductase enzymes.",
        "rationale": "Koilonychia and telogen effluvium indicate depleted tissue iron reserves."
    },
    "family_history_anemia": {
        "label": "Family History of Anemia",
        "explanation": "Familial predisposition to hemoglobinopathies or low iron absorption efficiency.",
        "rationale": "Genetic variants in HFE, TMPRSS6, and hemoglobin beta chains."
    },
    "lab_hemoglobin_anchor": {
        "label": "Campus Clinic Hemoglobin",
        "explanation": "Objective point-of-care laboratory measurement validating screening probability.",
        "rationale": "WHO threshold: Hb <12.0 g/dL (females) or <13.0 g/dL (males) defines anaemia."
    }
}


def extract_anemia_log_odds(intake: StudentIntakeRequest) -> Dict[str, float]:
    """Calculates additive log-odds weights for all anaemia features."""
    attribs: Dict[str, float] = {}

    # 1. Biological Sex
    if intake.sex == "female":
        attribs["biological_sex"] = 0.55
    elif intake.sex == "male":
        attribs["biological_sex"] = -0.35
    else:
        attribs["biological_sex"] = 0.0

    # 2. Dietary Pattern
    diet = intake.diet_pattern.lower()
    if diet == "vegan":
        attribs["dietary_iron_bioavailability"] = 0.65
    elif diet == "vegetarian":
        attribs["dietary_iron_bioavailability"] = 0.45
    elif diet == "pescatarian":
        attribs["dietary_iron_bioavailability"] = 0.10
    else:
        attribs["dietary_iron_bioavailability"] = -0.30

    # 3. Iron Rich Food Frequency
    iron_freq = str(intake.iron_rich_food_freq).lower()
    if "rare" in iron_freq or "never" in iron_freq:
        attribs["iron_rich_food_intake"] = 0.50
    elif "frequent" in iron_freq:
        attribs["iron_rich_food_intake"] = -0.40
    else:
        attribs["iron_rich_food_intake"] = 0.0

    # 4. Menstrual Blood Loss (females only)
    if intake.sex == "female":
        flow = str(intake.menstrual_flow_intensity).lower()
        if flow == "heavy":
            attribs["menstrual_blood_loss"] = 1.20
        elif flow == "moderate":
            attribs["menstrual_blood_loss"] = 0.20
        elif flow == "light":
            attribs["menstrual_blood_loss"] = -0.30
        else:
            attribs["menstrual_blood_loss"] = -0.20
    else:
        attribs["menstrual_blood_loss"] = 0.0

    # 5. Chronic Fatigue Score (0-10)
    fatigue = intake.fatigue_severity_score
    if fatigue <= 1:
        attribs["chronic_fatigue"] = -0.20
    else:
        attribs["chronic_fatigue"] = round(0.12 * max(0, fatigue - 2), 3)

    # 6. Orthostatic Dizziness
    diz = str(intake.orthostatic_dizziness).lower()
    if diz in ("daily", "3"):
        attribs["orthostatic_dizziness"] = 0.80
    elif diz in ("frequent", "2"):
        attribs["orthostatic_dizziness"] = 0.45
    elif diz in ("occasional", "rare", "1"):
        attribs["orthostatic_dizziness"] = 0.15
    else:
        attribs["orthostatic_dizziness"] = -0.20

    # 7. Mucosal Pallor
    pal = str(intake.mucosal_pallor).lower()
    if pal in ("distinct", "severe", "2", "true"):
        attribs["mucosal_pallor"] = 0.95
    elif pal in ("mild", "1"):
        attribs["mucosal_pallor"] = 0.40
    else:
        attribs["mucosal_pallor"] = -0.25

    # 8. Cold Extremities
    cold = str(intake.cold_extremities).lower()
    if cold in ("frequently", "2", "true"):
        attribs["cold_extremities"] = 0.50
    elif cold in ("sometimes", "1"):
        attribs["cold_extremities"] = 0.20
    else:
        attribs["cold_extremities"] = -0.15

    # 9. Pica Cravings
    attribs["pica_cravings"] = 0.90 if intake.pica_cravings else 0.0

    # 10. Brittle Nails / Hair Thinning
    attribs["brittle_nails_hair"] = 0.35 if intake.brittle_nails_or_hair_loss else 0.0

    # 11. Family History
    attribs["family_history_anemia"] = 0.30 if intake.family_history_anemia else 0.0

    # 12. Optional Lab Hemoglobin Anchor
    if intake.hemoglobin_g_dl is not None:
        hb = intake.hemoglobin_g_dl
        if intake.sex == "female":
            if hb < 10.0:
                w_hb = 2.50
            elif hb < 11.0:
                w_hb = 1.80
            elif hb < 12.0:
                w_hb = 0.90
            elif hb <= 14.5:
                w_hb = -1.20
            else:
                w_hb = -1.50
        elif intake.sex == "male":
            if hb < 11.0:
                w_hb = 2.50
            elif hb < 12.5:
                w_hb = 1.80
            elif hb < 13.5:
                w_hb = 0.90
            elif hb <= 16.5:
                w_hb = -1.20
            else:
                w_hb = -1.50
        else:
            if hb < 10.5:
                w_hb = 2.50
            elif hb < 12.0:
                w_hb = 1.50
            elif hb <= 15.0:
                w_hb = -1.20
            else:
                w_hb = -1.50
        attribs["lab_hemoglobin_anchor"] = w_hb

    return attribs


def evaluate_anemia_risk(intake: StudentIntakeRequest) -> Tuple[ConditionRiskResult, Dict[str, float], float]:
    """
    Evaluates calibrated anaemia risk for a student intake.
    Returns (ConditionRiskResult, log_odds_attribs, prob_pct).
    """
    attribs = extract_anemia_log_odds(intake)
    total_z = BETA_0_ANEMIA + sum(attribs.values())
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
    confidence = 0.95 if intake.hemoglobin_g_dl is not None else 0.88

    # Additive XAI attribution
    pos_drivers, prot_drivers, _ = compute_additive_feature_attribution(
        beta_0=BETA_0_ANEMIA,
        log_odds_attribs=attribs,
        metadata_map=METADATA_MAP
    )

    # Clinical summary & recommendations
    if tier == RiskTierEnum.elevated:
        summary = (
            f"Elevated anaemia risk ({prob_pct}%). Clinical indicators suggest "
            "potential iron-deficiency anaemia or functional hemoglobin depletion."
        )
        recommendations = [
            "Schedule a campus medical center visit for a CBC and Serum Ferritin panel.",
            "Combine plant-based iron (lentils, spinach) with Vitamin C to enhance absorption.",
            "Avoid tea or coffee within 1 hour of meals to prevent tannin interference.",
            "Discuss iron supplementation with a clinician before initiating over-the-counter tablets."
        ]
    elif tier == RiskTierEnum.moderate:
        summary = (
            f"Moderate anaemia risk ({prob_pct}%). Mild iron loss or low intake "
            "detected without severe overt symptoms."
        )
        recommendations = [
            "Increase iron-rich foods (legumes, tofu, fortified oats, seeds, leafy greens).",
            "Monitor energy levels during academic exam periods and menstrual cycles.",
            "Consider a routine annual campus health checkup with complete blood count."
        ]
    else:
        summary = f"Low anaemia risk ({prob_pct}%). Normal iron balance indicators observed."
        recommendations = [
            "Maintain balanced, colorful nutrition with diverse iron and micronutrient sources.",
            "Continue regular physical activity and proper hydration."
        ]

    result = ConditionRiskResult(
        domain_key="anemia",
        title="Anaemia Risk Stratification",
        calibrated_risk_pct=prob_pct,
        tier=tier,
        confidence_score=confidence,
        clinical_summary=summary,
        positive_drivers=pos_drivers,
        protective_drivers=prot_drivers,
        lifestyle_recommendations=recommendations
    )

    return result, attribs, prob_pct
