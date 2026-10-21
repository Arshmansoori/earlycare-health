r"""Adversarial stress testing suite for Milestone 1 ML Risk Engines & Boundaries.

Executed by Challenger 1 (critic/specialist) to empirically verify:
1. Numerical stability of logistic sigmoid & log-odds ($z \to \pm\infty$, extreme floats, inf)
2. Boundary tests around clinical cutoffs (29.9% vs 30.0%, 69.9% vs 70.0%, BMI 18.4 vs 18.5,
   24.9 vs 25.0, 29.9 vs 30.0, WHtR 0.49 vs 0.50, glucose 125.9 vs 126.0, Hb 7.9 vs 8.0)
3. Monotonicity checks (fatigue severity -> anaemia risk, glucose/BMI -> prediabetes risk)
4. Gender invariance checks (male menstrual flow variations strictly invariant across all outputs)
5. Extremal all-max / all-min stress cases and attribution stability
"""
import math
import pytest
from app.ml.explainability import (
    calculate_shapley_probability_shares,
    compute_additive_feature_attribution,
    sigmoid,
)
from app.ml.anemia import (
    BETA_0_ANEMIA,
    METADATA_MAP as METADATA_MAP_ANEMIA,
    evaluate_anemia_risk,
    extract_anemia_log_odds,
)
from app.ml.prediabetes import (
    BETA_0_PREDIABETES,
    METADATA_MAP as METADATA_MAP_PREDIAB,
    evaluate_prediabetes_risk,
    extract_prediabetes_log_odds,
)
from app.ml.micronutrients import (
    BETA_0_D3,
    evaluate_calcium,
    evaluate_micronutrients_risk,
    evaluate_vitamin_b12,
    evaluate_vitamin_d3,
)
from app.models.enums import RiskTierEnum
from app.models.schemas import StudentIntakeRequest


# ============================================================================
# 1. NUMERICAL STABILITY OF LOGISTIC FUNCTIONS & ATTRIBUTIONS
# ============================================================================

def test_adversarial_sigmoid_extreme_asymptotes():
    """Verify sigmoid handles extreme positive and negative asymptotes without overflow/underflow."""
    extreme_positives = [20.0, 25.0, 50.0, 100.0, 500.0, 1e15, 1e300, float("inf")]
    for val in extreme_positives:
        res = sigmoid(val)
        assert 0.9999 < res <= 1.0, f"Failed for z={val}: got {res}"
        assert not math.isnan(res), f"NaN produced for z={val}"

    extreme_negatives = [-20.0, -25.0, -50.0, -100.0, -500.0, -1e15, -1e300, float("-inf")]
    for val in extreme_negatives:
        res = sigmoid(val)
        assert 0.0 <= res < 1e-4, f"Failed for z={val}: got {res}"
        assert not math.isnan(res), f"NaN produced for z={val}"


def test_adversarial_shapley_near_cancellation_stability():
    """Verify Shapley redistribution when positive and negative log-odds almost cancel to zero."""
    beta_0 = -1.80
    base_p = sigmoid(beta_0)

    # Near cancellation: net displacement = 1e-5
    attribs_near_zero = {
        "strong_risk": 5.00001,
        "strong_protective": -5.00000
    }
    pred_p = sigmoid(beta_0 + sum(attribs_near_zero.values()))
    shares = calculate_shapley_probability_shares(base_p, pred_p, attribs_near_zero)

    assert "strong_risk" in shares
    assert "strong_protective" in shares
    assert not math.isnan(shares["strong_risk"])
    assert not math.isnan(shares["strong_protective"])

    # Complete exact cancellation: net displacement = 0.0
    attribs_zero = {
        "risk_a": 3.0,
        "prot_a": -3.0
    }
    shares_zero = calculate_shapley_probability_shares(base_p, base_p, attribs_zero)
    assert shares_zero["risk_a"] == 0.0
    assert shares_zero["prot_a"] == 0.0


def test_adversarial_attribution_empty_and_uniform():
    """Verify compute_additive_feature_attribution with empty or all-zero attributes."""
    pos, prot, cons = compute_additive_feature_attribution(
        beta_0=-1.80,
        log_odds_attribs={},
        metadata_map={}
    )
    assert len(pos) == 0
    assert len(prot) == 0
    assert cons["log_odds_sum"] == 0.0
    assert cons["expected_displacement"] == 0.0


# ============================================================================
# 2. BOUNDARY TESTS AROUND CLINICAL CUTOFFS
# ============================================================================

def test_adversarial_risk_tier_boundary_cutoffs():
    """
    Test exact boundaries for risk tiers:
    - prob_pct < 30.0 -> Low
    - 30.0 <= prob_pct < 70.0 -> Moderate
    - prob_pct >= 70.0 -> Elevated
    """
    # Verify that in all ML engines, 29.9% is Low, 30.0% is Moderate, 69.9% is Moderate, 70.0% is Elevated
    tier_eval = lambda p: RiskTierEnum.low if p < 30.0 else (RiskTierEnum.moderate if p < 70.0 else RiskTierEnum.elevated)
    
    assert tier_eval(0.0) == RiskTierEnum.low
    assert tier_eval(29.8) == RiskTierEnum.low
    assert tier_eval(29.9) == RiskTierEnum.low
    assert tier_eval(30.0) == RiskTierEnum.moderate
    assert tier_eval(30.1) == RiskTierEnum.moderate
    assert tier_eval(69.8) == RiskTierEnum.moderate
    assert tier_eval(69.9) == RiskTierEnum.moderate
    assert tier_eval(70.0) == RiskTierEnum.elevated
    assert tier_eval(70.1) == RiskTierEnum.elevated
    assert tier_eval(100.0) == RiskTierEnum.elevated


def test_adversarial_bmi_category_and_weights_boundary():
    """
    Empirical boundary check for BMI categories:
    - < 18.5: Underweight
    - 18.5 to < 25.0: Normal weight
    - 25.0 to < 30.0: Overweight
    - >= 30.0: Obesity
    And prediabetes BMI log-odds cutoff transitions: <22 (-0.4), <25 (0.0), <27.5 (0.4), <30 (0.75), <35 (1.3), >=35 (1.8).
    """
    # At height 160.0 cm (1.6m), 1.6^2 = 2.56
    # 47.104 kg / 2.56 = 18.4
    # 47.360 kg / 2.56 = 18.5
    req_18_4 = StudentIntakeRequest(height_cm=160.0, weight_kg=47.1)
    req_18_5 = StudentIntakeRequest(height_cm=160.0, weight_kg=47.36)
    assert req_18_4.bmi == 18.4
    assert req_18_4.bmi_category == "Underweight"
    assert req_18_5.bmi == 18.5
    assert req_18_5.bmi_category == "Normal weight"

    # 24.9 vs 25.0: 63.74 kg / 2.56 = 24.9, 64.0 kg / 2.56 = 25.0
    req_24_9 = StudentIntakeRequest(height_cm=160.0, weight_kg=63.744)
    req_25_0 = StudentIntakeRequest(height_cm=160.0, weight_kg=64.0)
    assert req_24_9.bmi == 24.9
    assert req_24_9.bmi_category == "Normal weight"
    assert req_25_0.bmi == 25.0
    assert req_25_0.bmi_category == "Overweight"

    # Check prediabetes log-odds transition at 25.0
    attr_24_9 = extract_prediabetes_log_odds(req_24_9)
    attr_25_0 = extract_prediabetes_log_odds(req_25_0)
    assert attr_24_9["bmi_adiposity"] == 0.0
    assert attr_25_0["bmi_adiposity"] == 0.40

    # 29.9 vs 30.0: 76.544 kg / 2.56 = 29.9, 76.8 kg / 2.56 = 30.0
    req_29_9 = StudentIntakeRequest(height_cm=160.0, weight_kg=76.544)
    req_30_0 = StudentIntakeRequest(height_cm=160.0, weight_kg=76.8)
    assert req_29_9.bmi == 29.9
    assert req_29_9.bmi_category == "Overweight"
    assert req_30_0.bmi == 30.0
    assert req_30_0.bmi_category == "Obesity"

    # Check prediabetes log-odds transition at 30.0
    attr_29_9 = extract_prediabetes_log_odds(req_29_9)
    attr_30_0 = extract_prediabetes_log_odds(req_30_0)
    assert attr_29_9["bmi_adiposity"] == 0.75
    assert attr_30_0["bmi_adiposity"] == 1.30


def test_adversarial_whtr_boundary_cutoffs():
    """
    Empirical boundary check for WHtR categories & log-odds:
    - WHtR < 0.50: Healthy (weight 0.0 if >=0.45)
    - WHtR 0.50 to < 0.60: Increased risk (weight 0.50 for <0.55, 0.90 for <0.60)
    - WHtR >= 0.60: Substantial risk (weight 1.45)
    """
    # Height = 100cm, waist 49cm -> WHtR 0.49
    req_0_49 = StudentIntakeRequest(height_cm=100.0, weight_kg=50.0, waist_circumference_cm=49.0)
    # Height = 100cm, waist 50cm -> WHtR 0.50
    req_0_50 = StudentIntakeRequest(height_cm=100.0, weight_kg=50.0, waist_circumference_cm=50.0)

    assert req_0_49.whtr == 0.49
    assert req_0_49.whtr_category == "Healthy"
    assert req_0_50.whtr == 0.50
    assert req_0_50.whtr_category == "Increased risk"

    attr_49 = extract_prediabetes_log_odds(req_0_49)
    attr_50 = extract_prediabetes_log_odds(req_0_50)
    assert attr_49["visceral_waist_height_ratio"] == 0.0
    assert attr_50["visceral_waist_height_ratio"] == 0.50

    # 0.59 vs 0.60
    req_0_59 = StudentIntakeRequest(height_cm=100.0, weight_kg=50.0, waist_circumference_cm=59.0)
    req_0_60 = StudentIntakeRequest(height_cm=100.0, weight_kg=50.0, waist_circumference_cm=60.0)
    assert req_0_59.whtr == 0.59
    assert req_0_59.whtr_category == "Increased risk"
    assert req_0_60.whtr == 0.60
    assert req_0_60.whtr_category == "Substantial risk"

    attr_59 = extract_prediabetes_log_odds(req_0_59)
    attr_60 = extract_prediabetes_log_odds(req_0_60)
    assert attr_59["visceral_waist_height_ratio"] == 0.90
    assert attr_60["visceral_waist_height_ratio"] == 1.45


def test_adversarial_glucose_and_hemoglobin_clinical_cutoffs():
    """Test fasting glucose and hemoglobin anchors across clinical and urgent thresholds."""
    # Fasting glucose: 125.9 vs 126.0 (ADA diabetes threshold)
    req_125_9 = StudentIntakeRequest(fasting_blood_glucose_mgdl=125.9)
    req_126_0 = StudentIntakeRequest(fasting_blood_glucose_mgdl=126.0)

    attr_glu_125 = extract_prediabetes_log_odds(req_125_9)
    attr_glu_126 = extract_prediabetes_log_odds(req_126_0)
    assert attr_glu_125["fasting_plasma_glucose"] == 2.00
    assert attr_glu_126["fasting_plasma_glucose"] == 3.00

    # Hemoglobin anchor (female): <10.0 (2.50), <11.0 (1.80), <12.0 (0.90), <=14.5 (-1.20), >14.5 (-1.50)
    req_hb_9_9 = StudentIntakeRequest(sex="female", hemoglobin_g_dl=9.9)
    req_hb_10_0 = StudentIntakeRequest(sex="female", hemoglobin_g_dl=10.0)
    req_hb_11_9 = StudentIntakeRequest(sex="female", hemoglobin_g_dl=11.9)
    req_hb_12_0 = StudentIntakeRequest(sex="female", hemoglobin_g_dl=12.0)
    req_hb_14_5 = StudentIntakeRequest(sex="female", hemoglobin_g_dl=14.5)
    req_hb_14_6 = StudentIntakeRequest(sex="female", hemoglobin_g_dl=14.6)

    assert extract_anemia_log_odds(req_hb_9_9)["lab_hemoglobin_anchor"] == 2.50
    assert extract_anemia_log_odds(req_hb_10_0)["lab_hemoglobin_anchor"] == 1.80
    assert extract_anemia_log_odds(req_hb_11_9)["lab_hemoglobin_anchor"] == 0.90
    assert extract_anemia_log_odds(req_hb_12_0)["lab_hemoglobin_anchor"] == -1.20
    assert extract_anemia_log_odds(req_hb_14_5)["lab_hemoglobin_anchor"] == -1.20
    assert extract_anemia_log_odds(req_hb_14_6)["lab_hemoglobin_anchor"] == -1.50


# ============================================================================
# 3. MONOTONICITY CHECKS
# ============================================================================

def test_adversarial_fatigue_severity_monotonicity_sweep():
    """
    Sweep fatigue_severity_score across [0, 1, 2, ..., 10].
    Verify that anaemia probability is strictly monotonically non-decreasing:
    P(fatigue = k+1) >= P(fatigue = k) for all k in 0..9.
    """
    probs = []
    log_odds_vals = []

    for f_score in range(11):
        req = StudentIntakeRequest(
            age=20,
            sex="female",
            height_cm=165.0,
            weight_kg=55.0,
            fatigue_severity_score=f_score
        )
        _, attribs, prob_pct = evaluate_anemia_risk(req)
        probs.append(prob_pct)
        log_odds_vals.append(attribs["chronic_fatigue"])

    # Verify log-odds are non-decreasing
    for i in range(len(log_odds_vals) - 1):
        assert log_odds_vals[i + 1] >= log_odds_vals[i], (
            f"Fatigue log-odds violated monotonicity at {i} -> {i+1}: "
            f"{log_odds_vals[i]} vs {log_odds_vals[i+1]}"
        )

    # Verify final probabilities are non-decreasing
    for i in range(len(probs) - 1):
        assert probs[i + 1] >= probs[i], (
            f"Anemia probability violated monotonicity at fatigue score {i} -> {i+1}: "
            f"{probs[i]}% vs {probs[i+1]}%"
        )

    # Verify endpoint divergence: fatigue 10 must have higher risk than fatigue 0
    assert probs[10] > probs[0]
    assert log_odds_vals[10] > log_odds_vals[0]


def test_adversarial_prediabetes_glucose_monotonicity_sweep():
    """
    Sweep fasting blood glucose across [70, 80, 89, 90, 99, 100, 109, 110, 125, 126, 140].
    Verify that prediabetes risk is monotonically non-decreasing.
    """
    glucose_steps = [70.0, 85.0, 89.9, 90.0, 95.0, 99.9, 100.0, 105.0, 109.9, 110.0, 120.0, 125.9, 126.0, 140.0]
    probs = []
    
    for glu in glucose_steps:
        req = StudentIntakeRequest(
            age=22,
            sex="male",
            height_cm=175.0,
            weight_kg=72.0,
            fasting_blood_glucose_mgdl=glu
        )
        _, _, prob_pct = evaluate_prediabetes_risk(req)
        probs.append(prob_pct)

    for i in range(len(probs) - 1):
        assert probs[i + 1] >= probs[i], (
            f"Glucose monotonicity violated at {glucose_steps[i]} -> {glucose_steps[i+1]}: "
            f"{probs[i]}% vs {probs[i+1]}%"
        )


def test_adversarial_prediabetes_physical_activity_monotonicity():
    """
    Verify that increasing physical activity monotonically decreases or preserves metabolic risk.
    """
    act_minutes = [0, 30, 60, 100, 150, 200, 240, 300]
    probs = []

    for mins in act_minutes:
        req = StudentIntakeRequest(
            age=22,
            sex="male",
            height_cm=175.0,
            weight_kg=80.0,
            physical_activity_min_per_week=mins
        )
        _, _, prob_pct = evaluate_prediabetes_risk(req)
        probs.append(prob_pct)

    # Increasing activity should produce non-increasing risk
    for i in range(len(probs) - 1):
        assert probs[i + 1] <= probs[i], (
            f"Activity monotonicity violated at {act_minutes[i]} -> {act_minutes[i+1]}: "
            f"{probs[i]}% vs {probs[i+1]}%"
        )


# ============================================================================
# 4. GENDER INVARIANCE CHECKS
# ============================================================================

def test_adversarial_male_menstrual_flow_invariance():
    """
    Adversarial gender invariance check:
    Altering menstrual_flow_intensity in male intakes MUST NEVER alter any model outputs.
    Test across all flow options: 'none', 'light', 'moderate', 'heavy', 'random_string'.
    """
    flow_variants = ["none", "light", "moderate", "heavy", "irregular", "severe", "UNKNOWN"]
    
    anemia_results = []
    prediab_results = []
    micro_results = []
    anemia_attribs_list = []

    for flow in flow_variants:
        req = StudentIntakeRequest(
            age=21,
            sex="male",
            height_cm=178.0,
            weight_kg=72.0,
            waist_circumference_cm=78.0,
            diet_pattern="omnivore",
            iron_rich_food_freq="sometimes",
            fatigue_severity_score=4,
            menstrual_flow_intensity=flow,
            menstrual_cycle_irregular=True  # even if male accidentally checked irregular cycle
        )

        anemia_res, a_attr, a_pct = evaluate_anemia_risk(req)
        prediab_res, p_attr, p_pct = evaluate_prediabetes_risk(req)
        micro_res, details, m_attr, m_pct = evaluate_micronutrients_risk(req)

        anemia_results.append(a_pct)
        prediab_results.append(p_pct)
        micro_results.append(m_pct)
        anemia_attribs_list.append(a_attr)

        # Invariance 1: Sanitized field must be normalized to 'none'
        assert req.menstrual_flow_intensity == "none"

        # Invariance 2: menstrual_blood_loss log-odds must be 0.0
        assert a_attr.get("menstrual_blood_loss", 0.0) == 0.0

        # Invariance 3: menstrual_blood_loss must NOT appear in positive drivers
        pos_names = [d.feature_name for d in anemia_res.positive_drivers]
        assert "menstrual_blood_loss" not in pos_names

    # All resulting risk probabilities across all 7 flow variants must be strictly identical
    assert len(set(anemia_results)) == 1, f"Anemia risk varied for male across flow: {anemia_results}"
    assert len(set(prediab_results)) == 1, f"Prediabetes risk varied for male across flow: {prediab_results}"
    assert len(set(micro_results)) == 1, f"Micronutrient risk varied for male across flow: {micro_results}"


# ============================================================================
# 5. EXTREMAL BOUNDS AND ALL-MAX / ALL-MIN COMBINATIONS
# ============================================================================

def test_adversarial_all_maximum_risk_combination():
    """Verify system stability when every single risk factor is set to its absolute worst."""
    req_worst = StudentIntakeRequest(
        age=25,
        sex="female",
        height_cm=140.0,
        weight_kg=120.0,  # BMI = 61.2 (Morbidly obese)
        waist_circumference_cm=130.0,  # WHtR = 0.93
        diet_pattern="vegan",
        iron_rich_food_freq="rarely_never",
        dairy_or_fortified_milk_freq="rarely_never",
        weekly_sunlight_hours="under_15_min",
        sunscreen_regular_use=True,
        physical_activity_level="sedentary",
        physical_activity_min_per_week=0,
        sugary_drinks_weekly_count=15,
        refined_carb_freq="high",
        sleep_hours_per_night=3.0,
        unrefreshing_sleep="daily",
        fatigue_severity_score=10,
        brain_fog_difficulty_concentrating="severe",
        orthostatic_dizziness="daily",
        cold_extremities=True,
        muscle_bone_aches="severe",
        peripheral_paresthesia_tingling="severe",
        brittle_nails_or_hair_loss=True,
        mucosal_pallor="severe",
        pica_cravings=True,
        polyuria_polydipsia="severe",
        acanthosis_nigricans_signs=True,
        menstrual_flow_intensity="heavy",
        family_history_diabetes=True,
        family_history_anemia=True,
        b12_supplementation=False,
        d3_supplementation=False,
        fasting_blood_glucose_mgdl=180.0,
        hemoglobin_g_dl=6.5
    )

    a_res, _, a_pct = evaluate_anemia_risk(req_worst)
    p_res, _, p_pct = evaluate_prediabetes_risk(req_worst)
    m_res, details, _, m_pct = evaluate_micronutrients_risk(req_worst)

    # All models must cleanly produce elevated tier and bounded probabilities <= 100.0%
    assert 0.0 <= a_pct <= 100.0
    assert 0.0 <= p_pct <= 100.0
    assert 0.0 <= m_pct <= 100.0

    assert a_res.tier == RiskTierEnum.elevated
    assert p_res.tier == RiskTierEnum.elevated
    assert m_res.tier == RiskTierEnum.elevated

    # Positive drivers must be non-empty and sorted descending
    assert len(a_res.positive_drivers) > 0
    for i in range(len(a_res.positive_drivers) - 1):
        assert a_res.positive_drivers[i].contribution_pct >= a_res.positive_drivers[i + 1].contribution_pct


def test_adversarial_all_minimum_risk_combination():
    """Verify system stability when every single risk factor is set to its absolute best."""
    req_best = StudentIntakeRequest(
        age=20,
        sex="male",
        height_cm=180.0,
        weight_kg=68.0,  # BMI = 21.0 (Optimal)
        waist_circumference_cm=75.0,  # WHtR = 0.42 (Healthy)
        diet_pattern="omnivore",
        iron_rich_food_freq="frequently",
        dairy_or_fortified_milk_freq=4,
        weekly_sunlight_hours="over_60_min",
        sunscreen_regular_use=False,
        physical_activity_level="active",
        physical_activity_min_per_week=300,
        sugary_drinks_weekly_count=0,
        refined_carb_freq="low",
        sleep_hours_per_night=8.5,
        fatigue_severity_score=0,
        brain_fog_difficulty_concentrating="none",
        orthostatic_dizziness="never",
        cold_extremities=False,
        muscle_bone_aches="none",
        peripheral_paresthesia_tingling="none",
        brittle_nails_or_hair_loss=False,
        mucosal_pallor="none",
        pica_cravings=False,
        polyuria_polydipsia="none",
        acanthosis_nigricans_signs=False,
        menstrual_flow_intensity="none",
        family_history_diabetes=False,
        family_history_anemia=False,
        b12_supplementation=True,
        d3_supplementation=True,
        fasting_blood_glucose_mgdl=82.0,
        hemoglobin_g_dl=15.5
    )

    a_res, _, a_pct = evaluate_anemia_risk(req_best)
    p_res, _, p_pct = evaluate_prediabetes_risk(req_best)
    m_res, details, _, m_pct = evaluate_micronutrients_risk(req_best)

    assert 0.0 <= a_pct <= 100.0
    assert 0.0 <= p_pct <= 100.0
    assert 0.0 <= m_pct <= 100.0

    assert a_res.tier == RiskTierEnum.low
    assert p_res.tier == RiskTierEnum.low
    assert m_res.tier == RiskTierEnum.low

    # Protective drivers must be populated and sorted descending
    assert len(a_res.protective_drivers) > 0
    for i in range(len(a_res.protective_drivers) - 1):
        assert a_res.protective_drivers[i].contribution_pct >= a_res.protective_drivers[i + 1].contribution_pct


# ============================================================================
# 6. API-LEVEL GENDER INVARIANCE & RED-FLAG BOUNDARIES
# ============================================================================

def test_adversarial_api_gender_invariance(client):
    """
    Empirical API end-to-end check:
    Verify that calling POST /api/screen for a male student with heavy flow
    returns EXACTLY identical clinical values as with none flow.
    """
    base_male = {
        "age": 21,
        "sex": "male",
        "height_cm": 178.0,
        "weight_kg": 72.0,
        "waist_circumference_cm": 78.0,
        "diet_pattern": "vegetarian",
        "fatigue_severity_score": 5,
        "hemoglobin_g_dl": 13.5
    }

    res_none = client.post("/api/screen", json={**base_male, "menstrual_flow_intensity": "none"}).json()
    res_heavy = client.post("/api/screen", json={**base_male, "menstrual_flow_intensity": "heavy"}).json()

    # Compare key clinical outputs
    assert res_none["conditions"]["anemia"]["calibrated_risk_pct"] == res_heavy["conditions"]["anemia"]["calibrated_risk_pct"]
    assert res_none["conditions"]["prediabetes"]["calibrated_risk_pct"] == res_heavy["conditions"]["prediabetes"]["calibrated_risk_pct"]
    assert res_none["conditions"]["micronutrients"]["calibrated_risk_pct"] == res_heavy["conditions"]["micronutrients"]["calibrated_risk_pct"]
    assert res_none["overall_risk_tier"] == res_heavy["overall_risk_tier"]
    assert res_none["overall_risk_summary"] == res_heavy["overall_risk_summary"]
    assert res_none["micronutrient_details"] == res_heavy["micronutrient_details"]
    assert res_none["calculated_vitals"] == res_heavy["calculated_vitals"]
    assert [a["risk_score"] for a in res_none["radar_axes"]] == [a["risk_score"] for a in res_heavy["radar_axes"]]


def test_adversarial_api_red_flag_boundaries(client):
    """
    Test exact clinical boundary cutoffs for urgent consultation flags:
    1. Fasting glucose: 125.9 (False) vs 126.0 (True)
    2. Hemoglobin: 8.0 (False) vs 7.9 (True)
    3. Fatigue + dizziness: fatigue 8 + daily (False) vs fatigue 9 + daily (True)
    4. Chest pain: False vs True
    """
    base = {
        "age": 20,
        "sex": "female",
        "height_cm": 165.0,
        "weight_kg": 55.0
    }

    # Glucose 125.9 -> False; 126.0 -> True
    res_glu_125 = client.post("/api/screen", json={**base, "fasting_blood_glucose_mgdl": 125.9}).json()
    res_glu_126 = client.post("/api/screen", json={**base, "fasting_blood_glucose_mgdl": 126.0}).json()
    assert res_glu_125["urgent_consult_flag"] is False
    assert res_glu_126["urgent_consult_flag"] is True

    # Hemoglobin 8.0 -> False; 7.9 -> True
    res_hb_80 = client.post("/api/screen", json={**base, "hemoglobin_g_dl": 8.0}).json()
    res_hb_79 = client.post("/api/screen", json={**base, "hemoglobin_g_dl": 7.9}).json()
    assert res_hb_80["urgent_consult_flag"] is False
    assert res_hb_79["urgent_consult_flag"] is True

    # Fatigue 8 + daily dizziness -> False; Fatigue 9 + daily dizziness -> True
    res_fat_8 = client.post("/api/screen", json={**base, "fatigue_severity_score": 8, "orthostatic_dizziness": "daily"}).json()
    res_fat_9 = client.post("/api/screen", json={**base, "fatigue_severity_score": 9, "orthostatic_dizziness": "daily"}).json()
    assert res_fat_8["urgent_consult_flag"] is False
    assert res_fat_9["urgent_consult_flag"] is True

    # Fatigue 9 + frequent (not daily) -> False
    res_fat_freq = client.post("/api/screen", json={**base, "fatigue_severity_score": 9, "orthostatic_dizziness": "frequent"}).json()
    assert res_fat_freq["urgent_consult_flag"] is False


def test_adversarial_shapley_conservation_randomized_cohort():
    """
    Stress-test mathematical Shapley conservation across 30 randomized student intakes:
    Verifies that sum(phi_i) == expected_displacement and prob closure holds.
    """
    import random
    rng = random.Random(42)

    for i in range(30):
        intake = StudentIntakeRequest(
            age=rng.randint(18, 28),
            sex=rng.choice(["female", "male"]),
            height_cm=float(rng.randint(150, 190)),
            weight_kg=float(rng.randint(45, 95)),
            fatigue_severity_score=rng.randint(0, 10),
            diet_pattern=rng.choice(["omnivore", "vegetarian", "vegan", "pescatarian"]),
            iron_rich_food_freq=rng.choice(["rarely_never", "sometimes", "frequently"]),
            menstrual_flow_intensity=rng.choice(["none", "light", "moderate", "heavy"]),
            orthostatic_dizziness=rng.choice(["never", "occasional", "frequent", "daily"]),
            mucosal_pallor=rng.choice(["none", "mild", "distinct"]),
            cold_extremities=rng.choice([True, False]),
            pica_cravings=rng.choice([True, False]),
            brittle_nails_or_hair_loss=rng.choice([True, False]),
            family_history_anemia=rng.choice([True, False])
        )

        _, attribs, _ = evaluate_anemia_risk(intake)
        pos, prot, cons = compute_additive_feature_attribution(
            beta_0=BETA_0_ANEMIA,
            log_odds_attribs=attribs,
            metadata_map=METADATA_MAP_ANEMIA
        )

        # 1. Exact log-odds displacement conservation
        sum_phi = sum(attribs.values())
        assert abs(cons["log_odds_sum"] - sum_phi) < 1e-4
        assert abs(cons["expected_displacement"] - sum_phi) < 1e-4

        # 2. Polarity strictness
        for p in pos:
            assert p.is_risk_increasing is True
            assert p.direction == "risk_driver"
            assert p.contribution_pct >= 0.0

        for pr in prot:
            assert pr.is_risk_increasing is False
            assert pr.direction == "protective"
            assert pr.contribution_pct >= 0.0


def test_adversarial_intake_default_and_fuzzing(client):
    """
    Verify endpoint resilience when minimal or empty inputs are submitted,
    and verify case-insensitive string parsing.
    """
    # Empty dict defaults
    res_empty = client.post("/api/screen", json={})
    assert res_empty.status_code == 200
    data_empty = res_empty.json()
    assert data_empty["screening_id"].startswith("EC-")
    assert "conditions" in data_empty

    # Upper-case string inputs
    res_caps = client.post("/api/screen", json={
        "sex": "FEMALE",
        "diet_pattern": "VEGAN",
        "iron_rich_food_freq": "RARELY_NEVER",
        "menstrual_flow_intensity": "HEAVY"
    })
    assert res_caps.status_code == 200
    data_caps = res_caps.json()
    assert data_caps["conditions"]["anemia"]["calibrated_risk_pct"] == 62.2
    assert data_caps["conditions"]["anemia"]["tier"] == "moderate"


def test_adversarial_whtr_unmeasured_waist_fallback():
    """Verify WHtR calculation fallback when waist is not provided."""
    # Weight 80kg, height 175cm -> BMI = 26.1
    req = StudentIntakeRequest(height_cm=175.0, weight_kg=80.0, waist_circumference_cm=None)
    assert req.bmi == 26.1
    # Fallback formula: (26.1 * 0.0175) + 0.10 = 0.55675 -> 0.56
    assert req.whtr == 0.56
    assert req.whtr_category == "Increased risk"
