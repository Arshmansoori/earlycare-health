"""Micronutrient Deficiency Matrix for EarlyCare.

Probabilistic inference engine evaluating four critical young-adult micronutrient domains:
1. Vitamin D3 (indoor lifestyle, sunscreen use, musculoskeletal bone pain)
2. Vitamin B12 (plant-based diet, lack of supplementation, peripheral neuropathy, brain fog)
3. Calcium Deficiency (inadequate dairy/fortified intake, high caffeine, tetany/cramps, D3 interaction)
4. Iron Stores / Ferritin Gap (subclinical tissue iron depletion prior to frank anaemia drop)
"""
from typing import Dict, List, Tuple
from app.models.enums import RiskTierEnum
from app.models.schemas import (
    ConditionRiskResult,
    DriverAttribution,
    MicronutrientDetails,
    StudentIntakeRequest,
)
from app.ml.explainability import (
    compute_additive_feature_attribution,
    sigmoid,
)

BETA_0_D3 = -0.30       # Baseline ~42.5% in predominantly indoor students
BETA_0_B12 = -2.00      # Baseline ~11.9%
BETA_0_CALCIUM = -1.40  # Baseline ~19.8%
BETA_0_IRON = -1.30     # Baseline ~21.4%

METADATA_MAP_MICRO: Dict[str, Dict[str, str]] = {
    "sunlight_uvb_exposure": {
        "label": "Sunlight Exposure (<15m/day)",
        "explanation": "Cutaneous synthesis via solar UVB conversion of 7-dehydrocholesterol is the primary source of Vitamin D3.",
        "rationale": "<15 min/day sun exposure produces insufficient pre-vitamin D3."
    },
    "sunscreen_uvb_block": {
        "label": "Sunscreen / Skin Covering",
        "explanation": "SPF 30+ sunscreen blocks approximately 95-98% of cutaneous UVB photon absorption.",
        "rationale": "High SPF regular application preserves skin from UV damage but reduces endogenous D3 synthesis."
    },
    "d3_supplementation": {
        "label": "Vitamin D3 Supplementation",
        "explanation": "Oral cholecalciferol effectively maintains serum 25(OH)D concentrations.",
        "rationale": "Daily 1,000-2,000 IU or weekly 50,000 IU prevents hypovitaminosis D."
    },
    "musculoskeletal_bone_pain": {
        "label": "Bone & Muscle Aches",
        "explanation": "Osteomalacic dull aching in lower spine, pelvis, and limbs secondary to impaired mineralization.",
        "rationale": "Secondary hyperparathyroidism activates periosteal nociceptors."
    },
    "dietary_cobalamin_sources": {
        "label": "Plant-Based Diet (Cobalamin)",
        "explanation": "Vitamin B12 is synthesized exclusively by microorganisms and absent in unfortified plant foods.",
        "rationale": "Unsupplemented vegans exhaust hepatic cobalamin stores within 2-5 years."
    },
    "b12_supplementation": {
        "label": "Vitamin B12 Supplementation",
        "explanation": "Sublingual or oral cyanocobalamin / methylcobalamin directly sustains metabolic pathways.",
        "rationale": "Essential cofactor for methionine synthase and methylmalonyl-CoA mutase."
    },
    "peripheral_paresthesia_tingling": {
        "label": "Peripheral Tingling (Paresthesias)",
        "explanation": "Subacute combined degeneration of the spinal cord and peripheral myelin sheath damage.",
        "rationale": "Early sensory neuropathy manifest as 'pins and needles' in toes and fingers."
    },
    "neurocognitive_brain_fog": {
        "label": "Brain Fog & Concentration Difficulty",
        "explanation": "Cobalamin deficiency impairs cerebral myelin integrity and monoamine neurotransmitter synthesis.",
        "rationale": "Elevated methylmalonic acid and homocysteine correlate with executive dysfunction."
    },
    "glossitis_oral_lesions": {
        "label": "Tongue Soreness / Glossitis",
        "explanation": "Rapidly dividing mucosal epithelial cells atrophy without cobalamin and folate.",
        "rationale": "Hunter's glossitis: beefy red, smooth depapillated tongue."
    },
    "dairy_calcium_servings": {
        "label": "Calcium Intake (Dairy / Fortified)",
        "explanation": "Dietary calcium maintains bone mineral density and neuromuscular membrane potentials.",
        "rationale": "Recommended daily allowance for young adults is 1,000 mg/day (approx 3 servings)."
    },
    "caffeine_excess": {
        "label": "High Caffeine Intake",
        "explanation": "High caffeine and energy drink consumption induces mild calciuria and decreases renal reabsorption.",
        "rationale": "Competitive adenosine receptor antagonism increases urinary calcium clearance."
    },
    "muscle_cramps_fasciculations": {
        "label": "Muscle Cramps & Spasms",
        "explanation": "Hypocalcemia lowers neuromuscular threshold potentials, causing hyper-excitability and twitching.",
        "rationale": "Inward sodium channel gating increases when extracellular calcium decreases."
    },
    "d3_cross_depletion": {
        "label": "Vitamin D3 Co-Depletion Interaction",
        "explanation": "Active 1,25-dihydroxyvitamin D is required for active intestinal calcium transport (calbindin-D9k).",
        "rationale": "Severe D3 deficiency reduces intestinal calcium absorption from 30-40% down to 10-15%."
    },
    "ferritin_gap_iron_depletion": {
        "label": "Subclinical Iron Store Depletion",
        "explanation": "Tissue ferritin stores are exhausted prior to frank drop in hemoglobin.",
        "rationale": "Serum ferritin <30 ng/mL signifies functional iron deficiency."
    }
}


def evaluate_vitamin_d3(intake: StudentIntakeRequest) -> Tuple[float, Dict[str, float]]:
    """Evaluates Vitamin D3 deficiency risk."""
    attribs: Dict[str, float] = {}

    # Sun Exposure
    sun = str(intake.weekly_sunlight_hours).lower()
    if "under_15" in sun or "under_2" in sun:
        attribs["sunlight_uvb_exposure"] = 0.90
    elif "15_to_30" in sun or "2_to_5" in sun:
        attribs["sunlight_uvb_exposure"] = 0.20
    elif "30_to_60" in sun:
        attribs["sunlight_uvb_exposure"] = -0.45
    else:  # over 60 min or over 5 hrs
        attribs["sunlight_uvb_exposure"] = -0.90

    # Sunscreen
    if intake.sunscreen_regular_use:
        attribs["sunscreen_uvb_block"] = 0.40
    else:
        attribs["sunscreen_uvb_block"] = -0.20

    # Supplementation
    if intake.d3_supplementation:
        attribs["d3_supplementation"] = -1.50
    else:
        attribs["d3_supplementation"] = 0.35

    # Musculoskeletal bone pain
    aches = str(intake.muscle_bone_aches).lower()
    if aches in ("severe", "3"):
        attribs["musculoskeletal_bone_pain"] = 1.00
    elif aches in ("moderate", "occasional", "2"):
        attribs["musculoskeletal_bone_pain"] = 0.60
    elif aches in ("mild", "1"):
        attribs["musculoskeletal_bone_pain"] = 0.15
    else:
        attribs["musculoskeletal_bone_pain"] = -0.20

    z = BETA_0_D3 + sum(attribs.values())
    prob = sigmoid(z)
    return round(prob * 100.0, 1), attribs


def evaluate_vitamin_b12(intake: StudentIntakeRequest) -> Tuple[float, Dict[str, float]]:
    """Evaluates Vitamin B12 deficiency risk."""
    attribs: Dict[str, float] = {}

    diet = intake.diet_pattern.lower()
    if diet == "vegan":
        attribs["dietary_cobalamin_sources"] = 1.75
    elif diet == "vegetarian":
        attribs["dietary_cobalamin_sources"] = 0.95
    elif diet == "pescatarian":
        attribs["dietary_cobalamin_sources"] = -0.30
    else:
        attribs["dietary_cobalamin_sources"] = -0.60

    if intake.b12_supplementation:
        attribs["b12_supplementation"] = -2.10
    else:
        attribs["b12_supplementation"] = 0.50

    ting = str(intake.peripheral_paresthesia_tingling).lower()
    if ting in ("persistent", "severe", "3"):
        attribs["peripheral_paresthesia_tingling"] = 1.50
    elif ting in ("frequent", "2"):
        attribs["peripheral_paresthesia_tingling"] = 0.85
    elif ting in ("rare", "occasional", "1"):
        attribs["peripheral_paresthesia_tingling"] = 0.30
    else:
        attribs["peripheral_paresthesia_tingling"] = -0.20

    fog = str(intake.brain_fog_difficulty_concentrating).lower()
    if fog in ("severe", "3"):
        attribs["neurocognitive_brain_fog"] = 0.90
    elif fog in ("moderate", "frequent", "2"):
        attribs["neurocognitive_brain_fog"] = 0.55
    elif fog in ("mild", "occasional", "1"):
        attribs["neurocognitive_brain_fog"] = 0.20
    else:
        attribs["neurocognitive_brain_fog"] = -0.15

    # Brittle nails or mouth sores proxy
    attribs["glossitis_oral_lesions"] = 0.60 if intake.brittle_nails_or_hair_loss else 0.0

    z = BETA_0_B12 + sum(attribs.values())
    prob = sigmoid(z)
    return round(prob * 100.0, 1), attribs


def evaluate_calcium(intake: StudentIntakeRequest, d3_prob: float) -> Tuple[float, Dict[str, float]]:
    """Evaluates Calcium deficiency risk."""
    attribs: Dict[str, float] = {}

    # Dairy / fortified milk servings or freq
    dairy = intake.dairy_or_fortified_milk_freq
    if isinstance(dairy, (int, float)):
        if dairy >= 3:
            w_dairy = -0.80
        elif dairy >= 1:
            w_dairy = -0.20
        else:
            w_dairy = 0.90
    else:
        s_dairy = str(dairy).lower()
        if "frequent" in s_dairy or "daily" in s_dairy:
            w_dairy = -0.80
        elif "sometimes" in s_dairy:
            w_dairy = -0.20
        else:  # rarely_never or none
            w_dairy = 0.90
    attribs["dairy_calcium_servings"] = w_dairy

    # Caffeine / energy drinks
    caff = intake.daily_caffeine_cups or 1
    if caff >= 3:
        attribs["caffeine_excess"] = 0.40
    else:
        attribs["caffeine_excess"] = -0.10

    # Muscle cramps / aches
    aches = str(intake.muscle_bone_aches).lower()
    if aches in ("severe", "3"):
        attribs["muscle_cramps_fasciculations"] = 1.40
    elif aches in ("frequent", "2"):
        attribs["muscle_cramps_fasciculations"] = 0.75
    elif aches in ("occasional", "moderate", "1"):
        attribs["muscle_cramps_fasciculations"] = 0.25
    else:
        attribs["muscle_cramps_fasciculations"] = -0.20

    # D3 cross depletion interaction
    if d3_prob >= 0.70:
        attribs["d3_cross_depletion"] = 0.50
    else:
        attribs["d3_cross_depletion"] = 0.0

    z = BETA_0_CALCIUM + sum(attribs.values())
    prob = sigmoid(z)
    return round(prob * 100.0, 1), attribs


def evaluate_iron_depletion(intake: StudentIntakeRequest) -> Tuple[float, Dict[str, float]]:
    """Evaluates functional Iron / Ferritin gap risk."""
    attribs: Dict[str, float] = {}

    iron_freq = str(intake.iron_rich_food_freq).lower()
    if "rare" in iron_freq or "never" in iron_freq:
        attribs["ferritin_gap_iron_depletion"] = 0.60
    elif "frequent" in iron_freq:
        attribs["ferritin_gap_iron_depletion"] = -0.45
    else:
        attribs["ferritin_gap_iron_depletion"] = 0.0

    if intake.sex == "female" and str(intake.menstrual_flow_intensity).lower() == "heavy":
        attribs["ferritin_gap_iron_depletion"] += 0.50

    z = BETA_0_IRON + sum(attribs.values())
    prob = sigmoid(z)
    return round(prob * 100.0, 1), attribs


def evaluate_micronutrients_risk(
    intake: StudentIntakeRequest
) -> Tuple[ConditionRiskResult, MicronutrientDetails, Dict[str, float], float]:
    """
    Evaluates multi-domain micronutrient deficiency risk.
    Returns (ConditionRiskResult, MicronutrientDetails, combined_attribs, overall_pct).
    """
    d3_pct, d3_attribs = evaluate_vitamin_d3(intake)
    b12_pct, b12_attribs = evaluate_vitamin_b12(intake)
    ca_pct, ca_attribs = evaluate_calcium(intake, d3_pct / 100.0)
    iron_pct, iron_attribs = evaluate_iron_depletion(intake)

    details = MicronutrientDetails(
        vitamin_d3_risk_pct=d3_pct,
        vitamin_b12_risk_pct=b12_pct,
        calcium_risk_pct=ca_pct,
        iron_deficiency_risk_pct=iron_pct
    )

    # Composite risk is governed by the highest individual deficiency index
    overall_pct = max(d3_pct, b12_pct, ca_pct, iron_pct)

    if overall_pct < 30.0:
        tier = RiskTierEnum.low
    elif overall_pct < 70.0:
        tier = RiskTierEnum.moderate
    else:
        tier = RiskTierEnum.elevated

    # Combine key attributes for XAI attribution
    combined_attribs: Dict[str, float] = {}
    combined_attribs.update(d3_attribs)
    combined_attribs.update(b12_attribs)
    combined_attribs.update(ca_attribs)

    # Attribution decomposition relative to D3 baseline
    pos_drivers, prot_drivers, _ = compute_additive_feature_attribution(
        beta_0=BETA_0_D3,
        log_odds_attribs=combined_attribs,
        metadata_map=METADATA_MAP_MICRO
    )

    # Formulate summary and recommendations
    flagged = []
    if d3_pct >= 60.0:
        flagged.append(f"Vitamin D3 ({d3_pct}%)")
    if b12_pct >= 60.0:
        flagged.append(f"Vitamin B12 ({b12_pct}%)")
    if ca_pct >= 60.0:
        flagged.append(f"Calcium ({ca_pct}%)")
    if iron_pct >= 60.0:
        flagged.append(f"Iron Stores ({iron_pct}%)")

    if tier == RiskTierEnum.elevated:
        summary = (
            f"Elevated micronutrient risk ({overall_pct}%). High probability of deficiency "
            f"observed in: {', '.join(flagged) if flagged else 'critical micronutrient reserves'}."
        )
        recommendations = [
            "Request a Serum 25(OH)D and Serum B12 / Folate panel from your campus health center.",
            "If following a vegan or vegetarian diet, incorporate daily Vitamin B12 supplementation (1,000 mcg).",
            "Consider 15-20 minutes of safe mid-day sun exposure or daily Vitamin D3 supplementation (1,000-2,000 IU).",
            "Ensure 3 daily servings of calcium-rich foods (fortified plant milks, sesame seeds, leafy greens, or dairy)."
        ]
    elif tier == RiskTierEnum.moderate:
        summary = (
            f"Moderate micronutrient risk ({overall_pct}%). Mild dietary or sunlight exposure "
            "gaps detected across student lifestyle markers."
        )
        recommendations = [
            "Incorporate a daily student multivitamin with bioavailable D3 and B12.",
            "Schedule outdoor study breaks during sunny daylight hours.",
            "Include calcium and magnesium-rich nuts, seeds, and fortified products in daily snacking."
        ]
    else:
        summary = f"Low micronutrient deficiency risk ({overall_pct}%). Adequate lifestyle and nutritional indicators."
        recommendations = [
            "Maintain diverse dietary intake with whole food sources.",
            "Continue regular outdoor activities and balanced nutrition."
        ]

    result = ConditionRiskResult(
        domain_key="micronutrients",
        title="Micronutrient Deficiency Matrix",
        calibrated_risk_pct=overall_pct,
        tier=tier,
        confidence_score=0.87,
        clinical_summary=summary,
        positive_drivers=pos_drivers,
        protective_drivers=prot_drivers,
        lifestyle_recommendations=recommendations
    )

    return result, details, combined_attribs, overall_pct
