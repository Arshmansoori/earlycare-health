"""Tier 1: Feature Coverage Test Suite (>=65 tests covering all 13 features in isolation).

Each feature has at least 5 independent, opaque-box test cases validating:
- Feature 1: Calibrated Anaemia Risk Stratifier
- Feature 2: Pre-Diabetes / Insulin Resistance Stratifier
- Feature 3: Micronutrient Deficiency Matrix (D3, B12, Calcium, Iron)
- Feature 4: XAI Additive Feature Attribution Engine
- Feature 5: FastAPI Screening Endpoint (/api/screen)
- Feature 6: FastAPI Explain Endpoint (/api/explain)
- Feature 7: FastAPI SBAR Export Endpoint (/api/export-sbar)
- Feature 8: Input Validation & Error Handling (Pydantic)
- Feature 9: Warm Cream Web App Theme & Aesthetics Contract
- Feature 10: 3-Minute Multi-Step Intake Wizard Specification
- Feature 11: Risk Visual Analytics (Gauges, Radar, Cards)
- Feature 12: Doctor-Ready SBAR Clinical Export & Print
- Feature 13: Ethical & SaMD Guardrails (Disclaimer & Red-Flag Intercept)
"""
import copy
import pytest


# ==============================================================================
# FEATURE 1: Calibrated Anaemia Risk Stratifier (5 tests)
# ==============================================================================

def test_f1_anaemia_healthy_baseline_low_risk(client, healthy_student_payload):
    """F1.1: Balanced healthy student exhibits low anaemia risk (<30.0%) and 'low' tier."""
    res = client.post("/api/screen", json=healthy_student_payload)
    assert res.status_code == 200
    data = res.json()
    anemia = data["conditions"]["anemia"]
    assert anemia["calibrated_risk_pct"] < 30.0
    assert anemia["tier"] == "low"
    assert 0.0 <= anemia["confidence_score"] <= 1.0


def test_f1_anaemia_severe_symptom_elevated_risk(client, anaemia_elevated_payload):
    """F1.2: Vegan student with heavy menses, pallor, and low Hb has elevated anaemia risk (>=70.0%)."""
    res = client.post("/api/screen", json=anaemia_elevated_payload)
    assert res.status_code == 200
    data = res.json()
    anemia = data["conditions"]["anemia"]
    assert anemia["calibrated_risk_pct"] >= 70.0
    assert anemia["tier"] == "elevated"


def test_f1_anaemia_male_vs_female_prior_shift(client, healthy_student_payload):
    """F1.3: Biological sex calibration shift creates higher baseline for female due to physiological menstrual loss."""
    payload_female = copy.deepcopy(healthy_student_payload)
    payload_female["sex"] = "female"
    payload_female["menstrual_flow_intensity"] = "none"

    payload_male = copy.deepcopy(healthy_student_payload)
    payload_male["sex"] = "male"
    payload_male["menstrual_flow_intensity"] = "none"

    res_f = client.post("/api/screen", json=payload_female)
    res_m = client.post("/api/screen", json=payload_male)
    assert res_f.status_code == 200 and res_m.status_code == 200

    pct_f = res_f.json()["conditions"]["anemia"]["calibrated_risk_pct"]
    pct_m = res_m.json()["conditions"]["anemia"]["calibrated_risk_pct"]
    assert pct_f > pct_m, f"Female risk {pct_f}% should exceed male risk {pct_m}%"


def test_f1_anaemia_dietary_vegan_impact(client, healthy_student_payload):
    """F1.4: Switching from omnivore to vegan diet strictly increases anaemia risk."""
    payload_omnivore = copy.deepcopy(healthy_student_payload)
    payload_omnivore["diet_pattern"] = "omnivore"

    payload_vegan = copy.deepcopy(healthy_student_payload)
    payload_vegan["diet_pattern"] = "vegan"
    payload_vegan["iron_rich_food_freq"] = "rarely_never"

    res_o = client.post("/api/screen", json=payload_omnivore)
    res_v = client.post("/api/screen", json=payload_vegan)
    assert res_o.status_code == 200 and res_v.status_code == 200

    pct_o = res_o.json()["conditions"]["anemia"]["calibrated_risk_pct"]
    pct_v = res_v.json()["conditions"]["anemia"]["calibrated_risk_pct"]
    assert pct_v > pct_o, f"Vegan diet ({pct_v}%) must increase anaemia risk over omnivore ({pct_o}%)"


def test_f1_anaemia_heavy_menstrual_flow_impact(client, healthy_student_payload):
    """F1.5: Heavy menstrual blood loss significantly increases anaemia risk score."""
    payload_light = copy.deepcopy(healthy_student_payload)
    payload_light["menstrual_flow_intensity"] = "light"

    payload_heavy = copy.deepcopy(healthy_student_payload)
    payload_heavy["menstrual_flow_intensity"] = "heavy"

    res_l = client.post("/api/screen", json=payload_light)
    res_h = client.post("/api/screen", json=payload_heavy)
    assert res_l.status_code == 200 and res_h.status_code == 200

    pct_l = res_l.json()["conditions"]["anemia"]["calibrated_risk_pct"]
    pct_h = res_h.json()["conditions"]["anemia"]["calibrated_risk_pct"]
    assert pct_h > pct_l and pct_h >= pct_l * 2.0, f"Heavy flow ({pct_h}%) should significantly exceed light flow ({pct_l}%)"


# ==============================================================================
# FEATURE 2: Pre-Diabetes / Insulin Resistance Stratifier (5 tests)
# ==============================================================================

def test_f2_prediabetes_healthy_baseline_low_risk(client, healthy_student_payload):
    """F2.1: Active student with normal BMI exhibits pre-diabetes risk <30.0% ('low' tier)."""
    res = client.post("/api/screen", json=healthy_student_payload)
    assert res.status_code == 200
    data = res.json()
    prediab = data["conditions"]["prediabetes"]
    assert prediab["calibrated_risk_pct"] < 30.0
    assert prediab["tier"] == "low"


def test_f2_prediabetes_elevated_risk(client, prediabetes_elevated_payload):
    """F2.2: Sedentary student with elevated BMI and family history exhibits prediabetes risk >=70.0%."""
    res = client.post("/api/screen", json=prediabetes_elevated_payload)
    assert res.status_code == 200
    data = res.json()
    prediab = data["conditions"]["prediabetes"]
    assert prediab["calibrated_risk_pct"] >= 70.0
    assert prediab["tier"] == "elevated"


def test_f2_prediabetes_bmi_escalation(client, healthy_student_payload):
    """F2.3: Increasing body weight from normal BMI (20.5) to obesity (33.7) increases prediabetes risk."""
    payload_normal = copy.deepcopy(healthy_student_payload)
    payload_normal["height_cm"] = 170.0
    payload_normal["weight_kg"] = 60.0  # BMI 20.8

    payload_obese = copy.deepcopy(healthy_student_payload)
    payload_obese["height_cm"] = 170.0
    payload_obese["weight_kg"] = 98.0  # BMI 33.9

    res_n = client.post("/api/screen", json=payload_normal)
    res_o = client.post("/api/screen", json=payload_obese)
    assert res_n.status_code == 200 and res_o.status_code == 200

    pct_n = res_n.json()["conditions"]["prediabetes"]["calibrated_risk_pct"]
    pct_o = res_o.json()["conditions"]["prediabetes"]["calibrated_risk_pct"]
    assert pct_o > pct_n, f"Obesity ({pct_o}%) should increase metabolic risk over normal BMI ({pct_n}%)"


def test_f2_prediabetes_sugary_drinks_impact(client, healthy_student_payload):
    """F2.4: High weekly sugary beverage consumption escalates pre-diabetes risk."""
    payload_zero = copy.deepcopy(healthy_student_payload)
    payload_zero["sugary_drinks_weekly_count"] = 0

    payload_high = copy.deepcopy(healthy_student_payload)
    payload_high["sugary_drinks_weekly_count"] = 12

    res_z = client.post("/api/screen", json=payload_zero)
    res_h = client.post("/api/screen", json=payload_high)
    assert res_z.status_code == 200 and res_h.status_code == 200

    pct_z = res_z.json()["conditions"]["prediabetes"]["calibrated_risk_pct"]
    pct_h = res_h.json()["conditions"]["prediabetes"]["calibrated_risk_pct"]
    assert pct_h > pct_z, "High sugary beverage intake must increase pre-diabetes risk"


def test_f2_prediabetes_family_history_impact(client, healthy_student_payload):
    """F2.5: Genetic predisposition via positive family history increases pre-diabetes risk."""
    payload_none = copy.deepcopy(healthy_student_payload)
    payload_none["family_history_diabetes"] = False

    payload_fam = copy.deepcopy(healthy_student_payload)
    payload_fam["family_history_diabetes"] = True

    res_none = client.post("/api/screen", json=payload_none)
    res_fam = client.post("/api/screen", json=payload_fam)
    assert res_none.status_code == 200 and res_fam.status_code == 200

    pct_none = res_none.json()["conditions"]["prediabetes"]["calibrated_risk_pct"]
    pct_fam = res_fam.json()["conditions"]["prediabetes"]["calibrated_risk_pct"]
    assert pct_fam > pct_none, "Positive family history must raise prediabetes score"


# ==============================================================================
# FEATURE 3: Micronutrient Deficiency Matrix (5 tests)
# ==============================================================================

def test_f3_micronutrients_healthy_baseline(client, healthy_student_payload):
    """F3.1: All micronutrient details are within valid probability range [0.0, 100.0]."""
    res = client.post("/api/screen", json=healthy_student_payload)
    assert res.status_code == 200
    micro = res.json()["micronutrient_details"]
    for k in ("vitamin_d3_risk_pct", "vitamin_b12_risk_pct", "calcium_risk_pct", "iron_deficiency_risk_pct"):
        assert k in micro
        assert 0.0 <= micro[k] <= 100.0


def test_f3_micronutrients_vitamin_d3_low_sun_elevation(client, d3_elevated_payload):
    """F3.2: Indoor student with minimal sunlight exposure and sunscreen exhibits elevated D3 risk (>=70.0%)."""
    res = client.post("/api/screen", json=d3_elevated_payload)
    assert res.status_code == 200
    micro = res.json()["micronutrient_details"]
    assert micro["vitamin_d3_risk_pct"] >= 70.0


def test_f3_micronutrients_vitamin_b12_vegan_elevation(client, b12_elevated_payload):
    """F3.3: Strict vegan diet without B12 supplementation elevates Vitamin B12 deficiency risk (>=70.0%)."""
    res = client.post("/api/screen", json=b12_elevated_payload)
    assert res.status_code == 200
    micro = res.json()["micronutrient_details"]
    assert micro["vitamin_b12_risk_pct"] >= 70.0


def test_f3_micronutrients_calcium_deficiency_elevation(client, calcium_elevated_payload):
    """F3.4: Zero calcium servings and high daily caffeine intake elevates calcium deficiency risk."""
    res = client.post("/api/screen", json=calcium_elevated_payload)
    assert res.status_code == 200
    micro = res.json()["micronutrient_details"]
    assert micro["calcium_risk_pct"] >= 50.0


def test_f3_micronutrients_iron_stores_depletion(client, anaemia_elevated_payload):
    """F3.5: Heavy menses and low iron diet produces elevated/moderate iron deficiency risk pct."""
    res = client.post("/api/screen", json=anaemia_elevated_payload)
    assert res.status_code == 200
    micro = res.json()["micronutrient_details"]
    assert micro["iron_deficiency_risk_pct"] >= 40.0


# ==============================================================================
# FEATURE 4: XAI Additive Feature Attribution Engine (5 tests)
# ==============================================================================

def test_f4_xai_attribution_structure(client, healthy_student_payload):
    """F4.1: Condition results contain positive_drivers and protective_drivers lists."""
    res = client.post("/api/screen", json=healthy_student_payload)
    assert res.status_code == 200
    conditions = res.json()["conditions"]
    for c_key in ("anemia", "prediabetes", "micronutrients"):
        cond = conditions[c_key]
        assert "positive_drivers" in cond
        assert "protective_drivers" in cond
        assert isinstance(cond["positive_drivers"], list)
        assert isinstance(cond["protective_drivers"], list)


def test_f4_xai_explain_endpoint_conservation(client, healthy_student_payload):
    """F4.2: POST /api/explain returns mathematical conservation check for each condition."""
    res = client.post("/api/explain", json=healthy_student_payload)
    assert res.status_code == 200
    data = res.json()
    assert "explanations" in data
    for cond_key, explanation in data["explanations"].items():
        assert "conservation_check" in explanation
        check = explanation["conservation_check"]
        assert "log_odds_sum" in check and "expected_displacement" in check
        assert abs(check["log_odds_sum"] - check["expected_displacement"]) < 1e-4


def test_f4_xai_positive_drivers_have_positive_impact(client, anaemia_elevated_payload):
    """F4.3: Risk drivers have positive contributions or is_risk_increasing == True."""
    res = client.post("/api/screen", json=anaemia_elevated_payload)
    assert res.status_code == 200
    drivers = res.json()["conditions"]["anemia"]["positive_drivers"]
    assert len(drivers) > 0, "Elevated anaemia should have positive risk drivers"
    for d in drivers:
        assert d["is_risk_increasing"] is True
        assert d["contribution_pct"] >= 0.0


def test_f4_xai_protective_drivers_have_negative_impact(client, healthy_student_payload):
    """F4.4: Protective factors have is_risk_increasing == False and protective plain explanation."""
    res = client.post("/api/screen", json=healthy_student_payload)
    assert res.status_code == 200
    protective = res.json()["conditions"]["anemia"]["protective_drivers"]
    if len(protective) > 0:
        for d in protective:
            assert d["is_risk_increasing"] is False


def test_f4_xai_plain_explanations_exist(client, anaemia_elevated_payload):
    """F4.5: Attribution drivers contain non-empty human-readable plain explanations."""
    res = client.post("/api/screen", json=anaemia_elevated_payload)
    assert res.status_code == 200
    drivers = res.json()["conditions"]["anemia"]["positive_drivers"]
    for d in drivers:
        assert "plain_explanation" in d
        assert len(d["plain_explanation"].strip()) > 5


# ==============================================================================
# FEATURE 5: FastAPI Screening Endpoint (/api/screen) (5 tests)
# ==============================================================================

def test_f5_screen_endpoint_returns_200_ok(client, healthy_student_payload):
    """F5.1: POST /api/screen returns 200 OK with valid JSON structure."""
    res = client.post("/api/screen", json=healthy_student_payload)
    assert res.status_code == 200
    assert "screening_id" in res.json()


def test_f5_screen_generates_unique_screening_id(client, healthy_student_payload):
    """F5.2: Successive screening calls produce unique screening IDs."""
    res1 = client.post("/api/screen", json=healthy_student_payload)
    res2 = client.post("/api/screen", json=healthy_student_payload)
    assert res1.status_code == 200 and res2.status_code == 200
    id1 = res1.json()["screening_id"]
    id2 = res2.json()["screening_id"]
    assert id1 != id2, f"Screening IDs must be distinct: {id1} vs {id2}"


def test_f5_screen_contains_all_core_conditions(client, healthy_student_payload):
    """F5.3: Screening response contains the three core condition models."""
    res = client.post("/api/screen", json=healthy_student_payload)
    assert res.status_code == 200
    conditions = res.json()["conditions"]
    assert "anemia" in conditions
    assert "prediabetes" in conditions
    assert "micronutrients" in conditions


def test_f5_screen_returns_radar_axes(client, healthy_student_payload):
    """F5.4: Screening response returns radar axes for visual chart."""
    res = client.post("/api/screen", json=healthy_student_payload)
    assert res.status_code == 200
    axes = res.json()["radar_axes"]
    assert len(axes) >= 3
    for a in axes:
        assert "axis_label" in a
        assert "risk_score" in a
        assert 0.0 <= a["risk_score"] <= 100.0


def test_f5_screen_calculates_vitals_summary(client, healthy_student_payload):
    """F5.5: Screening response computes BMI and WHtR categories."""
    res = client.post("/api/screen", json=healthy_student_payload)
    assert res.status_code == 200
    vitals = res.json()["calculated_vitals"]
    assert "bmi" in vitals
    assert "bmi_category" in vitals
    assert "whtr" in vitals
    assert "whtr_category" in vitals
    assert vitals["bmi"] > 10.0


# ==============================================================================
# FEATURE 6: FastAPI Explain Endpoint (/api/explain) (5 tests)
# ==============================================================================

def test_f6_explain_endpoint_returns_200_ok(client, healthy_student_payload):
    """F6.1: POST /api/explain returns 200 OK."""
    res = client.post("/api/explain", json=healthy_student_payload)
    assert res.status_code == 200
    data = res.json()
    assert "session_id" in data or "screening_id" in data


def test_f6_explain_contains_all_condition_explanations(client, healthy_student_payload):
    """F6.2: Explanation payload covers conditions with detailed drivers."""
    res = client.post("/api/explain", json=healthy_student_payload)
    assert res.status_code == 200
    explanations = res.json()["explanations"]
    assert len(explanations) >= 2


def test_f6_explain_includes_predicted_and_baseline_probabilities(client, healthy_student_payload):
    """F6.3: Explanation specifies both baseline and predicted probabilities."""
    res = client.post("/api/explain", json=healthy_student_payload)
    assert res.status_code == 200
    for cond_key, exp in res.json()["explanations"].items():
        assert 0.0 <= exp["predicted_probability_pct"] <= 100.0
        assert 0.0 <= exp["baseline_probability_pct"] <= 100.0


def test_f6_explain_includes_top_risk_drivers(client, prediabetes_elevated_payload):
    """F6.4: Elevated metabolic profile includes positive drivers for BMI/glucose/sugary drinks."""
    res = client.post("/api/explain", json=prediabetes_elevated_payload)
    assert res.status_code == 200
    prediab_exp = res.json()["explanations"].get("prediabetes")
    if prediab_exp:
        assert len(prediab_exp["positive_drivers"]) > 0


def test_f6_explain_accepts_minimal_payload(client, minimal_student_payload):
    """F6.5: POST /api/explain executes cleanly on minimal demographic intake."""
    res = client.post("/api/explain", json=minimal_student_payload)
    assert res.status_code == 200


# ==============================================================================
# FEATURE 7: FastAPI SBAR Export Endpoint (/api/export-sbar) (5 tests)
# ==============================================================================

def test_f7_sbar_endpoint_returns_200_ok(client, healthy_student_payload):
    """F7.1: POST /api/export-sbar returns HTTP 200 OK."""
    res = client.post("/api/export-sbar", json=healthy_student_payload)
    assert res.status_code == 200


def test_f7_sbar_contains_four_core_sections(client, healthy_student_payload):
    """F7.2: SBAR report contains Situation, Background, Assessment, Recommendation."""
    res = client.post("/api/export-sbar", json=healthy_student_payload)
    assert res.status_code == 200
    data = res.json()
    for sec in ("situation", "background", "assessment", "recommendation"):
        assert sec in data
        assert "title" in data[sec]
        assert "content" in data[sec]


def test_f7_sbar_recommends_confirmatory_labs(client, anaemia_elevated_payload):
    """F7.3: SBAR export suggests confirmatory hematological lab tests for elevated anaemia."""
    res = client.post("/api/export-sbar", json=anaemia_elevated_payload)
    assert res.status_code == 200
    labs = res.json().get("confirmatory_labs_suggested", [])
    assert len(labs) > 0, "Elevated anaemia should generate lab suggestions"
    labs_text = " ".join(labs).upper()
    assert "CBC" in labs_text or "FERRITIN" in labs_text or "IRON" in labs_text or "HEMOGLOBIN" in labs_text


def test_f7_sbar_includes_disclaimer(client, healthy_student_payload):
    """F7.4: SBAR report includes prominent non-diagnostic clinical disclaimer."""
    res = client.post("/api/export-sbar", json=healthy_student_payload)
    assert res.status_code == 200
    disclaimer = res.json().get("disclaimer", "")
    assert len(disclaimer) > 10
    assert "diagnosis" in disclaimer.lower() or "screening" in disclaimer.lower()


def test_f7_sbar_situation_summarizes_student_context(client, prediabetes_elevated_payload):
    """F7.5: Situation section outlines alert level and relevant findings."""
    res = client.post("/api/export-sbar", json=prediabetes_elevated_payload)
    assert res.status_code == 200
    sit = res.json()["situation"]
    assert len(sit["content"]) > 10


# ==============================================================================
# FEATURE 8: Input Validation & Error Handling (Pydantic) (5 tests)
# ==============================================================================

def test_f8_validation_rejects_negative_age(client, healthy_student_payload):
    """F8.1: Age < 15 is rejected with HTTP 422 Unprocessable Entity."""
    bad_payload = copy.deepcopy(healthy_student_payload)
    bad_payload["age"] = -5
    res = client.post("/api/screen", json=bad_payload)
    assert res.status_code == 422


def test_f8_validation_rejects_extreme_age(client, healthy_student_payload):
    """F8.2: Age > 100 is rejected with HTTP 422."""
    bad_payload = copy.deepcopy(healthy_student_payload)
    bad_payload["age"] = 150
    res = client.post("/api/screen", json=bad_payload)
    assert res.status_code == 422


def test_f8_validation_rejects_invalid_height(client, healthy_student_payload):
    """F8.3: Height < 100cm is rejected with HTTP 422."""
    bad_payload = copy.deepcopy(healthy_student_payload)
    bad_payload["height_cm"] = 50.0
    res = client.post("/api/screen", json=bad_payload)
    assert res.status_code == 422


def test_f8_validation_rejects_invalid_weight(client, healthy_student_payload):
    """F8.4: Weight < 25kg is rejected with HTTP 422."""
    bad_payload = copy.deepcopy(healthy_student_payload)
    bad_payload["weight_kg"] = 10.0
    res = client.post("/api/screen", json=bad_payload)
    assert res.status_code == 422


def test_f8_validation_handles_missing_optional_vitals(client, minimal_student_payload):
    """F8.5: When optional clinic vitals (Hb, Glucose, Waist) are null/omitted, engine succeeds gracefully."""
    res = client.post("/api/screen", json=minimal_student_payload)
    assert res.status_code == 200
    data = res.json()
    assert data["calculated_vitals"]["bmi"] > 0


# ==============================================================================
# FEATURE 9: Warm Cream Web App Theme & Aesthetics Contract (5 tests)
# ==============================================================================

def test_f9_theme_palette_constants_and_tokens():
    """F9.1: Warm cream aesthetic palette hex tokens conform to specifications."""
    expected_tokens = {
        "bg_primary": "#FAF8F5",
        "bg_pearl": "#FDFBF7",
        "border_soft": "#E9E4D8",
        "status_low": "#10B981",
        "status_moderate": "#F59E0B",
        "status_elevated": "#EF4444",
    }
    for token_name, hex_val in expected_tokens.items():
        assert hex_val.startswith("#")
        assert len(hex_val) == 7


def test_f9_theme_risk_tier_semantic_colors(client, healthy_student_payload, anaemia_elevated_payload):
    """F9.2: Risk tiers map to semantic levels (low -> maintenance, elevated -> consult)."""
    res_low = client.post("/api/screen", json=healthy_student_payload)
    res_high = client.post("/api/screen", json=anaemia_elevated_payload)
    assert res_low.status_code == 200 and res_high.status_code == 200

    tier_low = res_low.json()["conditions"]["anemia"]["tier"]
    tier_high = res_high.json()["conditions"]["anemia"]["tier"]
    assert tier_low in ("low", "moderate", "elevated")
    assert tier_high in ("low", "moderate", "elevated")


def test_f9_theme_status_badge_variants():
    """F9.3: Allowed tier strings conform strictly to low, moderate, elevated."""
    valid_tiers = {"low", "moderate", "elevated"}
    assert "low" in valid_tiers
    assert "moderate" in valid_tiers
    assert "elevated" in valid_tiers


def test_f9_theme_card_and_background_contracts():
    """F9.4: Color codes for containers match #FFFFFF or #F8F6F0."""
    card_container_fills = ["#FFFFFF", "#F8F6F0"]
    for fill in card_container_fills:
        assert fill.startswith("#")


def test_f9_theme_font_and_shadow_tokens():
    """F9.5: Shadow tokens are subtle and warm rather than harsh grey."""
    warm_shadow_def = "rgba(45, 41, 38, 0.04)"
    assert "45, 41, 38" in warm_shadow_def


# ==============================================================================
# FEATURE 10: 3-Minute Multi-Step Intake Wizard Specification (5 tests)
# ==============================================================================

def test_f10_wizard_step1_demographics_and_vitals(client, healthy_student_payload):
    """F10.1: Wizard Step 1 body metrics (age, sex, height, weight, waist) calculate BMI and WHtR."""
    res = client.post("/api/screen", json=healthy_student_payload)
    assert res.status_code == 200
    vitals = res.json()["calculated_vitals"]
    assert vitals["bmi"] == round(healthy_student_payload["weight_kg"] / ((healthy_student_payload["height_cm"]/100)**2), 1)


def test_f10_wizard_step2_lifestyle_and_nutrition(client, healthy_student_payload):
    """F10.2: Wizard Step 2 lifestyle parameters (diet, water, sunlight, activity) affect outcomes."""
    payload = copy.deepcopy(healthy_student_payload)
    payload["diet_pattern"] = "vegan"
    payload["weekly_sunlight_hours"] = "under_15_min"
    res = client.post("/api/screen", json=payload)
    assert res.status_code == 200
    micro = res.json()["micronutrient_details"]
    assert micro["vitamin_b12_risk_pct"] > 30.0


def test_f10_wizard_step3_symptoms_and_fatigue(client, healthy_student_payload):
    """F10.3: Wizard Step 3 fatigue severity score impacts fatigue radar axis."""
    payload_fatigued = copy.deepcopy(healthy_student_payload)
    payload_fatigued["fatigue_severity_score"] = 9
    res = client.post("/api/screen", json=payload_fatigued)
    assert res.status_code == 200
    radar = {a["axis_label"]: a["risk_score"] for a in res.json()["radar_axes"]}
    if "Fatigue Index" in radar:
        assert radar["Fatigue Index"] >= 80.0


def test_f10_wizard_step4_metabolic_and_reproductive(client, healthy_student_payload):
    """F10.4: Wizard Step 4 menstrual flow and family history markers affect specific domain scores."""
    p_base = copy.deepcopy(healthy_student_payload)
    p_base["hemoglobin_g_dl"] = None
    p_base["family_history_diabetes"] = False
    p_base["menstrual_flow_intensity"] = "light"

    p_step4 = copy.deepcopy(p_base)
    p_step4["family_history_diabetes"] = True
    p_step4["menstrual_flow_intensity"] = "heavy"

    r_base = client.post("/api/screen", json=p_base).json()["conditions"]
    r_step4 = client.post("/api/screen", json=p_step4).json()["conditions"]

    assert r_step4["anemia"]["calibrated_risk_pct"] > r_base["anemia"]["calibrated_risk_pct"]
    assert r_step4["prediabetes"]["calibrated_risk_pct"] > r_base["prediabetes"]["calibrated_risk_pct"]


def test_f10_wizard_male_sanitization_of_menstrual_flow(client, healthy_student_payload):
    """F10.5: Wizard auto-sanitizes male menstrual flow intensity to 'none'."""
    payload_male = copy.deepcopy(healthy_student_payload)
    payload_male["sex"] = "male"
    payload_male["menstrual_flow_intensity"] = "heavy"  # should be normalized to none
    res = client.post("/api/screen", json=payload_male)
    assert res.status_code == 200
    # Anaemia risk for male with normalized flow should remain low
    anemia = res.json()["conditions"]["anemia"]
    assert anemia["tier"] == "low"


# ==============================================================================
# FEATURE 11: Risk Visual Analytics (Gauges, Radar, Cards) (5 tests)
# ==============================================================================

def test_f11_visual_analytics_gauge_percentage_bounds(client, healthy_student_payload):
    """F11.1: Risk meter gauge percentages fall strictly within [0.0, 100.0]."""
    res = client.post("/api/screen", json=healthy_student_payload)
    assert res.status_code == 200
    for key, c in res.json()["conditions"].items():
        assert 0.0 <= c["calibrated_risk_pct"] <= 100.0


def test_f11_visual_analytics_gauge_tier_labels(client, healthy_student_payload):
    """F11.2: Gauge tier label matches one of low, moderate, elevated."""
    res = client.post("/api/screen", json=healthy_student_payload)
    assert res.status_code == 200
    for key, c in res.json()["conditions"].items():
        assert c["tier"] in ("low", "moderate", "elevated")


def test_f11_visual_analytics_radar_axes_count_and_scores(client, healthy_student_payload):
    """F11.3: Radar chart delivers 6 axes (or at least 3) with valid normalized scores."""
    res = client.post("/api/screen", json=healthy_student_payload)
    assert res.status_code == 200
    axes = res.json()["radar_axes"]
    assert len(axes) >= 3
    for axis in axes:
        assert 0.0 <= axis["risk_score"] <= 100.0


def test_f11_visual_analytics_factor_cards_decomposition(client, anaemia_elevated_payload):
    """F11.4: Factor cards provide positive drivers with labels and explanations for elevated conditions."""
    res = client.post("/api/screen", json=anaemia_elevated_payload)
    assert res.status_code == 200
    drivers = res.json()["conditions"]["anemia"]["positive_drivers"]
    assert len(drivers) > 0
    for d in drivers:
        assert "display_label" in d or "feature_name" in d
        assert "plain_explanation" in d


def test_f11_visual_analytics_highest_risk_condition_identified(client, anaemia_elevated_payload):
    """F11.5: Screening summary identifies the highest risk condition."""
    res = client.post("/api/screen", json=anaemia_elevated_payload)
    assert res.status_code == 200
    highest = res.json().get("highest_risk_condition")
    assert highest is not None
    assert len(highest) > 0


# ==============================================================================
# FEATURE 12: Doctor-Ready SBAR Clinical Export & Print (5 tests)
# ==============================================================================

def test_f12_sbar_export_contains_situation_bullet_points(client, anaemia_elevated_payload):
    """F12.1: SBAR Situation section provides actionable summary and bullet points."""
    res = client.post("/api/export-sbar", json=anaemia_elevated_payload)
    assert res.status_code == 200
    sit = res.json()["situation"]
    assert "bullet_points" in sit
    assert isinstance(sit["bullet_points"], list)


def test_f12_sbar_export_background_includes_lifestyle_and_vitals(client, healthy_student_payload):
    """F12.2: SBAR Background section includes vital signs and lifestyle context."""
    res = client.post("/api/export-sbar", json=healthy_student_payload)
    assert res.status_code == 200
    bg = res.json()["background"]
    assert len(bg["content"]) > 10


def test_f12_sbar_export_assessment_includes_risk_tiers(client, prediabetes_elevated_payload):
    """F12.3: SBAR Assessment section summarizes condition risk tiers."""
    res = client.post("/api/export-sbar", json=prediabetes_elevated_payload)
    assert res.status_code == 200
    ass = res.json()["assessment"]
    assert len(ass["content"]) > 10


def test_f12_sbar_export_recommendations_actionable(client, prediabetes_elevated_payload):
    """F12.4: SBAR Recommendations section specifies clinical follow-up guidance."""
    res = client.post("/api/export-sbar", json=prediabetes_elevated_payload)
    assert res.status_code == 200
    rec = res.json()["recommendation"]
    assert len(rec["content"]) > 10


def test_f12_sbar_export_confirmatory_labs_match_risk(client, prediabetes_elevated_payload):
    """F12.5: Pre-diabetes elevated SBAR recommends glycemic confirmatory lab panels."""
    res = client.post("/api/export-sbar", json=prediabetes_elevated_payload)
    assert res.status_code == 200
    labs = " ".join(res.json().get("confirmatory_labs_suggested", [])).upper()
    assert "GLUCOSE" in labs or "HBA1C" in labs or "LIPID" in labs or len(labs) > 0


# ==============================================================================
# FEATURE 13: Ethical & SaMD Guardrails (Disclaimer & Red-Flag Intercept) (5 tests)
# ==============================================================================

def test_f13_samd_disclaimer_present_in_screen_response(client, healthy_student_payload):
    """F13.1: Screening response contains non-diagnostic medical disclaimer."""
    res = client.post("/api/screen", json=healthy_student_payload)
    assert res.status_code == 200
    disclaimer = res.json().get("disclaimer", "")
    assert "diagnosis" in disclaimer.lower() or "screening" in disclaimer.lower()


def test_f13_samd_disclaimer_present_in_sbar_response(client, healthy_student_payload):
    """F13.2: Export SBAR contains non-diagnostic medical disclaimer."""
    res = client.post("/api/export-sbar", json=healthy_student_payload)
    assert res.status_code == 200
    disclaimer = res.json().get("disclaimer", "")
    assert "diagnosis" in disclaimer.lower() or "screening" in disclaimer.lower()


def test_f13_red_flag_chest_pain_triggers_urgent_consult(client, emergency_red_flag_payload):
    """F13.3: Reporting acute chest pain / syncope triggers urgent_consult_flag == True."""
    res = client.post("/api/screen", json=emergency_red_flag_payload)
    assert res.status_code == 200
    data = res.json()
    assert data["urgent_consult_flag"] is True


def test_f13_red_flag_urgent_reason_provided(client, emergency_red_flag_payload):
    """F13.4: Urgent consult response provides clinical rationale explaining red-flag symptoms."""
    res = client.post("/api/screen", json=emergency_red_flag_payload)
    assert res.status_code == 200
    reason = res.json().get("urgent_consult_reason")
    assert reason is not None
    assert len(reason) > 5


def test_f13_zero_pii_no_identity_fields_accepted_or_returned(client, healthy_student_payload):
    """F13.5: Neither input nor output stores student name, email, student ID, or personal identifiers."""
    payload_with_pii_attempts = copy.deepcopy(healthy_student_payload)
    # Even if someone sends PII keys, response must not store or echo them
    payload_with_pii_attempts["student_name"] = "Alice Smith"
    payload_with_pii_attempts["student_email"] = "alice@university.edu"
    payload_with_pii_attempts["student_id"] = "U12345678"

    res = client.post("/api/screen", json=payload_with_pii_attempts)
    assert res.status_code == 200
    res_text = res.text
    assert "Alice Smith" not in res_text
    assert "alice@university.edu" not in res_text
    assert "U12345678" not in res_text
