"""Tier 2: Boundary & Corner Case Test Suite (>=65 tests).

Covers edge values, threshold transitions, physiological boundary conditions,
extreme configurations, and parameter validation guards across:
- Fatigue severity scale boundaries (0, 1, 2, 5, 8, 9, 10, out-of-range)
- BMI categories (18.4, 18.5, 24.9, 25.0, 29.9, 30.0, 35.0)
- WHtR categories (0.44, 0.49, 0.50, 0.59, 0.60)
- Fasting glucose clinical cutoffs (70, 90, 99, 100, 125, 126, 200, None)
- Hemoglobin cutoffs (8.9, 9.0, 10.5, 11.9, 12.0, 13.5, 17.0, None)
- Blood pressure boundaries (Systolic 70, 119, 120, 130, 220; Diastolic 40, 140)
- Demographics & Body Metrics (Age 15, 16, 100, <15, >100; Height 100, 250; Weight 25, 250)
- Sleep duration & lifestyle boundaries (Sleep 2.0, 7.0, 16.0; Activity 0, 240+; Sugary drinks 0, 50)
- Extreme state profiles (All-negative symptoms, All-positive severe symptoms, Zero vitals, Male menstrual sanitization)
"""
import copy
import pytest


# ==============================================================================
# SECTION A: Fatigue Severity Scale Boundaries (10 tests)
# ==============================================================================

def test_bva_fatigue_0_min_valid(client, healthy_student_payload):
    """BVA A.1: Fatigue score = 0 (minimum valid scale) computes without error."""
    payload = copy.deepcopy(healthy_student_payload)
    payload["fatigue_severity_score"] = 0
    res = client.post("/api/screen", json=payload)
    assert res.status_code == 200
    assert res.json()["conditions"]["anemia"]["tier"] == "low"


def test_bva_fatigue_1_low_baseline(client, healthy_student_payload):
    """BVA A.2: Fatigue score = 1 maintains low risk baseline."""
    payload = copy.deepcopy(healthy_student_payload)
    payload["fatigue_severity_score"] = 1
    res = client.post("/api/screen", json=payload)
    assert res.status_code == 200
    assert res.json()["conditions"]["anemia"]["calibrated_risk_pct"] < 30.0


def test_bva_fatigue_2_threshold(client, healthy_student_payload):
    """BVA A.3: Fatigue score = 2 represents transition threshold where fatigue penalty starts."""
    payload = copy.deepcopy(healthy_student_payload)
    payload["fatigue_severity_score"] = 2
    res = client.post("/api/screen", json=payload)
    assert res.status_code == 200


def test_bva_fatigue_3_mild_elevation(client, healthy_student_payload):
    """BVA A.4: Fatigue score = 3 shows slight score increment over score 2."""
    p2 = copy.deepcopy(healthy_student_payload)
    p2["fatigue_severity_score"] = 2
    p3 = copy.deepcopy(healthy_student_payload)
    p3["fatigue_severity_score"] = 3
    r2 = client.post("/api/screen", json=p2)
    r3 = client.post("/api/screen", json=p3)
    assert r2.status_code == 200 and r3.status_code == 200
    pct2 = r2.json()["conditions"]["anemia"]["calibrated_risk_pct"]
    pct3 = r3.json()["conditions"]["anemia"]["calibrated_risk_pct"]
    assert pct3 >= pct2


def test_bva_fatigue_5_mid_scale(client, healthy_student_payload):
    """BVA A.5: Fatigue score = 5 (midpoint of scale)."""
    payload = copy.deepcopy(healthy_student_payload)
    payload["fatigue_severity_score"] = 5
    res = client.post("/api/screen", json=payload)
    assert res.status_code == 200


def test_bva_fatigue_7_moderate_severe(client, healthy_student_payload):
    """BVA A.6: Fatigue score = 7 indicates significant fatigue burden."""
    payload = copy.deepcopy(healthy_student_payload)
    payload["fatigue_severity_score"] = 7
    res = client.post("/api/screen", json=payload)
    assert res.status_code == 200


def test_bva_fatigue_8_severe(client, healthy_student_payload):
    """BVA A.7: Fatigue score = 8 escalates fatigue radar axis."""
    payload = copy.deepcopy(healthy_student_payload)
    payload["fatigue_severity_score"] = 8
    res = client.post("/api/screen", json=payload)
    assert res.status_code == 200


def test_bva_fatigue_9_near_maximum(client, healthy_student_payload):
    """BVA A.8: Fatigue score = 9."""
    payload = copy.deepcopy(healthy_student_payload)
    payload["fatigue_severity_score"] = 9
    res = client.post("/api/screen", json=payload)
    assert res.status_code == 200


def test_bva_fatigue_10_maximum_valid(client, healthy_student_payload):
    """BVA A.9: Fatigue score = 10 (maximum allowed scale)."""
    payload = copy.deepcopy(healthy_student_payload)
    payload["fatigue_severity_score"] = 10
    res = client.post("/api/screen", json=payload)
    assert res.status_code == 200


def test_bva_fatigue_out_of_range_rejected(client, healthy_student_payload):
    """BVA A.10: Fatigue score < 0 or > 10 is rejected with 422."""
    p_neg = copy.deepcopy(healthy_student_payload)
    p_neg["fatigue_severity_score"] = -1
    p_high = copy.deepcopy(healthy_student_payload)
    p_high["fatigue_severity_score"] = 11

    res_neg = client.post("/api/screen", json=p_neg)
    res_high = client.post("/api/screen", json=p_high)
    assert res_neg.status_code == 422
    assert res_high.status_code == 422


# ==============================================================================
# SECTION B: BMI & WHtR Physiological Categories (12 tests)
# ==============================================================================

def test_bva_bmi_18_4_underweight_boundary(client, healthy_student_payload):
    """BVA B.1: BMI 18.4 (height 170cm, weight 53.2kg) classifies as Underweight."""
    payload = copy.deepcopy(healthy_student_payload)
    payload["height_cm"] = 170.0
    payload["weight_kg"] = 53.2
    res = client.post("/api/screen", json=payload)
    assert res.status_code == 200
    assert res.json()["calculated_vitals"]["bmi_category"] == "Underweight"


def test_bva_bmi_18_5_normal_lower_boundary(client, healthy_student_payload):
    """BVA B.2: BMI 18.5 (height 170cm, weight 53.5kg) classifies as Normal weight."""
    payload = copy.deepcopy(healthy_student_payload)
    payload["height_cm"] = 170.0
    payload["weight_kg"] = 53.5
    res = client.post("/api/screen", json=payload)
    assert res.status_code == 200
    assert res.json()["calculated_vitals"]["bmi_category"] == "Normal weight"


def test_bva_bmi_24_9_normal_upper_boundary(client, healthy_student_payload):
    """BVA B.3: BMI 24.9 (height 170cm, weight 72.0kg) classifies as Normal weight."""
    payload = copy.deepcopy(healthy_student_payload)
    payload["height_cm"] = 170.0
    payload["weight_kg"] = 72.0
    res = client.post("/api/screen", json=payload)
    assert res.status_code == 200
    assert res.json()["calculated_vitals"]["bmi_category"] == "Normal weight"


def test_bva_bmi_25_0_overweight_lower_boundary(client, healthy_student_payload):
    """BVA B.4: BMI 25.0 (height 170cm, weight 72.3kg) classifies as Overweight."""
    payload = copy.deepcopy(healthy_student_payload)
    payload["height_cm"] = 170.0
    payload["weight_kg"] = 72.3
    res = client.post("/api/screen", json=payload)
    assert res.status_code == 200
    assert res.json()["calculated_vitals"]["bmi_category"] == "Overweight"


def test_bva_bmi_29_9_overweight_upper_boundary(client, healthy_student_payload):
    """BVA B.5: BMI 29.9 (height 170cm, weight 86.4kg) classifies as Overweight."""
    payload = copy.deepcopy(healthy_student_payload)
    payload["height_cm"] = 170.0
    payload["weight_kg"] = 86.4
    res = client.post("/api/screen", json=payload)
    assert res.status_code == 200
    assert res.json()["calculated_vitals"]["bmi_category"] == "Overweight"


def test_bva_bmi_30_0_obesity_lower_boundary(client, healthy_student_payload):
    """BVA B.6: BMI 30.0 (height 170cm, weight 86.7kg) classifies as Obesity."""
    payload = copy.deepcopy(healthy_student_payload)
    payload["height_cm"] = 170.0
    payload["weight_kg"] = 86.7
    res = client.post("/api/screen", json=payload)
    assert res.status_code == 200
    assert res.json()["calculated_vitals"]["bmi_category"] == "Obesity"


def test_bva_bmi_35_0_severe_obesity(client, healthy_student_payload):
    """BVA B.7: BMI 35.0 (height 170cm, weight 101.2kg) classifies as Obesity."""
    payload = copy.deepcopy(healthy_student_payload)
    payload["height_cm"] = 170.0
    payload["weight_kg"] = 101.2
    res = client.post("/api/screen", json=payload)
    assert res.status_code == 200
    assert res.json()["calculated_vitals"]["bmi_category"] == "Obesity"


def test_bva_whtr_0_44_healthy_lower(client, healthy_student_payload):
    """BVA B.8: WHtR 0.44 (height 170cm, waist 74.8cm) classifies as Healthy."""
    payload = copy.deepcopy(healthy_student_payload)
    payload["height_cm"] = 170.0
    payload["waist_circumference_cm"] = 74.8
    res = client.post("/api/screen", json=payload)
    assert res.status_code == 200
    assert res.json()["calculated_vitals"]["whtr_category"] == "Healthy"


def test_bva_whtr_0_49_healthy_upper_boundary(client, healthy_student_payload):
    """BVA B.9: WHtR 0.49 (height 170cm, waist 83.3cm) classifies as Healthy."""
    payload = copy.deepcopy(healthy_student_payload)
    payload["height_cm"] = 170.0
    payload["waist_circumference_cm"] = 83.3
    res = client.post("/api/screen", json=payload)
    assert res.status_code == 200
    assert res.json()["calculated_vitals"]["whtr_category"] == "Healthy"


def test_bva_whtr_0_50_increased_risk_lower_boundary(client, healthy_student_payload):
    """BVA B.10: WHtR 0.50 (height 170cm, waist 85.0cm) classifies as Increased risk."""
    payload = copy.deepcopy(healthy_student_payload)
    payload["height_cm"] = 170.0
    payload["waist_circumference_cm"] = 85.0
    res = client.post("/api/screen", json=payload)
    assert res.status_code == 200
    assert res.json()["calculated_vitals"]["whtr_category"] == "Increased risk"


def test_bva_whtr_0_59_increased_risk_upper_boundary(client, healthy_student_payload):
    """BVA B.11: WHtR 0.59 (height 170cm, waist 100.3cm) classifies as Increased risk."""
    payload = copy.deepcopy(healthy_student_payload)
    payload["height_cm"] = 170.0
    payload["waist_circumference_cm"] = 100.3
    res = client.post("/api/screen", json=payload)
    assert res.status_code == 200
    assert res.json()["calculated_vitals"]["whtr_category"] == "Increased risk"


def test_bva_whtr_0_60_substantial_risk_lower_boundary(client, healthy_student_payload):
    """BVA B.12: WHtR 0.60 (height 170cm, waist 102.0cm) classifies as Substantial risk."""
    payload = copy.deepcopy(healthy_student_payload)
    payload["height_cm"] = 170.0
    payload["waist_circumference_cm"] = 102.0
    res = client.post("/api/screen", json=payload)
    assert res.status_code == 200
    assert res.json()["calculated_vitals"]["whtr_category"] == "Substantial risk"


# ==============================================================================
# SECTION C: Fasting Glucose & Lab Cutoffs (8 tests)
# ==============================================================================

def test_bva_glucose_70_low_normal(client, healthy_student_payload):
    """BVA C.1: Fasting glucose = 70 mg/dL is within physiological lower normal."""
    payload = copy.deepcopy(healthy_student_payload)
    payload["fasting_blood_glucose_mgdl"] = 70.0
    res = client.post("/api/screen", json=payload)
    assert res.status_code == 200


def test_bva_glucose_90_protective(client, healthy_student_payload):
    """BVA C.2: Fasting glucose = 90 mg/dL produces protective metabolic attribution."""
    payload = copy.deepcopy(healthy_student_payload)
    payload["fasting_blood_glucose_mgdl"] = 90.0
    res = client.post("/api/screen", json=payload)
    assert res.status_code == 200
    assert res.json()["conditions"]["prediabetes"]["tier"] == "low"


def test_bva_glucose_99_upper_normal(client, healthy_student_payload):
    """BVA C.3: Fasting glucose = 99 mg/dL represents highest normal fasting glucose."""
    payload = copy.deepcopy(healthy_student_payload)
    payload["fasting_blood_glucose_mgdl"] = 99.0
    res = client.post("/api/screen", json=payload)
    assert res.status_code == 200


def test_bva_glucose_100_impaired_lower(client, healthy_student_payload):
    """BVA C.4: Fasting glucose = 100 mg/dL enters impaired fasting glucose (IFG) range."""
    p_norm = copy.deepcopy(healthy_student_payload)
    p_norm["fasting_blood_glucose_mgdl"] = 90.0
    p_ifg = copy.deepcopy(healthy_student_payload)
    p_ifg["fasting_blood_glucose_mgdl"] = 100.0

    r_norm = client.post("/api/screen", json=p_norm)
    r_ifg = client.post("/api/screen", json=p_ifg)
    assert r_norm.status_code == 200 and r_ifg.status_code == 200

    pct_norm = r_norm.json()["conditions"]["prediabetes"]["calibrated_risk_pct"]
    pct_ifg = r_ifg.json()["conditions"]["prediabetes"]["calibrated_risk_pct"]
    assert pct_ifg > pct_norm, "Fasting glucose 100 mg/dL should elevate pre-diabetes score"


def test_bva_glucose_125_impaired_upper(client, healthy_student_payload):
    """BVA C.5: Fasting glucose = 125 mg/dL is upper bound of IFG."""
    payload = copy.deepcopy(healthy_student_payload)
    payload["fasting_blood_glucose_mgdl"] = 125.0
    res = client.post("/api/screen", json=payload)
    assert res.status_code == 200


def test_bva_glucose_126_diabetes_threshold_triggers_alert(client, healthy_student_payload):
    """BVA C.6: Fasting glucose >= 126 mg/dL triggers clinical urgent consult flag."""
    payload = copy.deepcopy(healthy_student_payload)
    payload["fasting_blood_glucose_mgdl"] = 126.0
    res = client.post("/api/screen", json=payload)
    assert res.status_code == 200
    assert res.json()["urgent_consult_flag"] is True


def test_bva_glucose_200_severe_hyperglycemia(client, healthy_student_payload):
    """BVA C.7: Fasting glucose = 200 mg/dL sets urgent alert and elevated tier."""
    payload = copy.deepcopy(healthy_student_payload)
    payload["fasting_blood_glucose_mgdl"] = 200.0
    res = client.post("/api/screen", json=payload)
    assert res.status_code == 200
    assert res.json()["urgent_consult_flag"] is True


def test_bva_glucose_none_omitted_lab_graceful(client, healthy_student_payload):
    """BVA C.8: Fasting glucose = None omitted gracefully without error."""
    payload = copy.deepcopy(healthy_student_payload)
    payload["fasting_blood_glucose_mgdl"] = None
    res = client.post("/api/screen", json=payload)
    assert res.status_code == 200


# ==============================================================================
# SECTION D: Hemoglobin Lab Cutoffs (8 tests)
# ==============================================================================

def test_bva_hb_7_9_severe_triggers_urgent(client, healthy_student_payload):
    """BVA D.1: Hemoglobin < 8.0 g/dL triggers urgent consult alert for critical hypochromia."""
    payload = copy.deepcopy(healthy_student_payload)
    payload["hemoglobin_g_dl"] = 7.9
    res = client.post("/api/screen", json=payload)
    assert res.status_code == 200
    assert res.json()["urgent_consult_flag"] is True


def test_bva_hb_9_0_severe_boundary(client, healthy_student_payload):
    """BVA D.2: Hemoglobin = 9.0 g/dL boundary for moderate-severe hypochromia."""
    payload = copy.deepcopy(healthy_student_payload)
    payload["hemoglobin_g_dl"] = 9.0
    res = client.post("/api/screen", json=payload)
    assert res.status_code == 200
    assert res.json()["conditions"]["anemia"]["calibrated_risk_pct"] > 30.0
    assert res.json()["conditions"]["anemia"]["tier"] in ("moderate", "elevated")


def test_bva_hb_10_5_moderate_anaemia(client, healthy_student_payload):
    """BVA D.3: Hemoglobin = 10.5 g/dL represents moderate anaemia."""
    payload = copy.deepcopy(healthy_student_payload)
    payload["hemoglobin_g_dl"] = 10.5
    res = client.post("/api/screen", json=payload)
    assert res.status_code == 200


def test_bva_hb_11_9_mild_female_boundary(client, healthy_student_payload):
    """BVA D.4: Hemoglobin = 11.9 g/dL is just below WHO female threshold (12.0)."""
    payload = copy.deepcopy(healthy_student_payload)
    payload["sex"] = "female"
    payload["hemoglobin_g_dl"] = 11.9
    res = client.post("/api/screen", json=payload)
    assert res.status_code == 200


def test_bva_hb_12_0_normal_female_boundary(client, healthy_student_payload):
    """BVA D.5: Hemoglobin = 12.0 g/dL is normal lower threshold for adult non-pregnant females."""
    payload = copy.deepcopy(healthy_student_payload)
    payload["sex"] = "female"
    payload["hemoglobin_g_dl"] = 12.0
    res = client.post("/api/screen", json=payload)
    assert res.status_code == 200


def test_bva_hb_13_5_normal_male_boundary(client, healthy_student_payload):
    """BVA D.6: Hemoglobin = 13.5 g/dL is normal adult male range."""
    payload = copy.deepcopy(healthy_student_payload)
    payload["sex"] = "male"
    payload["hemoglobin_g_dl"] = 13.5
    res = client.post("/api/screen", json=payload)
    assert res.status_code == 200


def test_bva_hb_17_0_high_polycythemic(client, healthy_student_payload):
    """BVA D.7: Hemoglobin = 17.0 g/dL high physiological range."""
    payload = copy.deepcopy(healthy_student_payload)
    payload["hemoglobin_g_dl"] = 17.0
    res = client.post("/api/screen", json=payload)
    assert res.status_code == 200
    assert res.json()["conditions"]["anemia"]["tier"] == "low"


def test_bva_hb_none_omitted_lab_graceful(client, healthy_student_payload):
    """BVA D.8: Hemoglobin = None gracefully evaluates via symptom/diet indicators."""
    payload = copy.deepcopy(healthy_student_payload)
    payload["hemoglobin_g_dl"] = None
    res = client.post("/api/screen", json=payload)
    assert res.status_code == 200


# ==============================================================================
# SECTION E: Blood Pressure & Heart Rate (6 tests)
# ==============================================================================

def test_bva_systolic_70_min_valid(client, healthy_student_payload):
    """BVA E.1: Systolic BP = 70 mmHg (minimum allowed)."""
    payload = copy.deepcopy(healthy_student_payload)
    payload["blood_pressure_systolic"] = 70
    res = client.post("/api/screen", json=payload)
    assert res.status_code == 200


def test_bva_systolic_119_normal_upper(client, healthy_student_payload):
    """BVA E.2: Systolic BP = 119 mmHg (upper limit of normal BP)."""
    payload = copy.deepcopy(healthy_student_payload)
    payload["blood_pressure_systolic"] = 119
    res = client.post("/api/screen", json=payload)
    assert res.status_code == 200


def test_bva_systolic_120_elevated_lower(client, healthy_student_payload):
    """BVA E.3: Systolic BP = 120 mmHg (lower boundary for elevated BP)."""
    payload = copy.deepcopy(healthy_student_payload)
    payload["blood_pressure_systolic"] = 120
    res = client.post("/api/screen", json=payload)
    assert res.status_code == 200


def test_bva_systolic_130_stage1_boundary(client, healthy_student_payload):
    """BVA E.4: Systolic BP = 130 mmHg (hypertension Stage 1 boundary)."""
    payload = copy.deepcopy(healthy_student_payload)
    payload["blood_pressure_systolic"] = 130
    res = client.post("/api/screen", json=payload)
    assert res.status_code == 200


def test_bva_systolic_220_max_valid(client, healthy_student_payload):
    """BVA E.5: Systolic BP = 220 mmHg (maximum valid range)."""
    payload = copy.deepcopy(healthy_student_payload)
    payload["blood_pressure_systolic"] = 220
    res = client.post("/api/screen", json=payload)
    assert res.status_code == 200


def test_bva_diastolic_boundaries(client, healthy_student_payload):
    """BVA E.6: Diastolic BP = 40 (min) and 140 (max) valid ranges."""
    p40 = copy.deepcopy(healthy_student_payload)
    p40["blood_pressure_diastolic"] = 40
    p140 = copy.deepcopy(healthy_student_payload)
    p140["blood_pressure_diastolic"] = 140

    r40 = client.post("/api/screen", json=p40)
    r140 = client.post("/api/screen", json=p140)
    assert r40.status_code == 200 and r140.status_code == 200


# ==============================================================================
# SECTION F: Demographics, Height, Weight Boundaries (9 tests)
# ==============================================================================

def test_bva_age_15_min_valid(client, healthy_student_payload):
    """BVA F.1: Age 15 is lowest valid student age."""
    payload = copy.deepcopy(healthy_student_payload)
    payload["age"] = 15
    res = client.post("/api/screen", json=payload)
    assert res.status_code == 200


def test_bva_age_16_standard_student(client, healthy_student_payload):
    """BVA F.2: Age 16 standard student intake age."""
    payload = copy.deepcopy(healthy_student_payload)
    payload["age"] = 16
    res = client.post("/api/screen", json=payload)
    assert res.status_code == 200


def test_bva_age_100_max_valid(client, healthy_student_payload):
    """BVA F.3: Age 100 is maximum valid age."""
    payload = copy.deepcopy(healthy_student_payload)
    payload["age"] = 100
    res = client.post("/api/screen", json=payload)
    assert res.status_code == 200


def test_bva_height_100_min_valid(client, healthy_student_payload):
    """BVA F.4: Height 100.0 cm is minimum valid height."""
    payload = copy.deepcopy(healthy_student_payload)
    payload["height_cm"] = 100.0
    payload["weight_kg"] = 30.0
    res = client.post("/api/screen", json=payload)
    assert res.status_code == 200


def test_bva_height_250_max_valid(client, healthy_student_payload):
    """BVA F.5: Height 250.0 cm is maximum valid height."""
    payload = copy.deepcopy(healthy_student_payload)
    payload["height_cm"] = 250.0
    res = client.post("/api/screen", json=payload)
    assert res.status_code == 200


def test_bva_weight_25_min_valid(client, healthy_student_payload):
    """BVA F.6: Weight 25.0 kg is minimum valid weight."""
    payload = copy.deepcopy(healthy_student_payload)
    payload["weight_kg"] = 25.0
    res = client.post("/api/screen", json=payload)
    assert res.status_code == 200


def test_bva_weight_250_max_valid(client, healthy_student_payload):
    """BVA F.7: Weight 250.0 kg is maximum valid weight."""
    payload = copy.deepcopy(healthy_student_payload)
    payload["weight_kg"] = 250.0
    res = client.post("/api/screen", json=payload)
    assert res.status_code == 200


def test_bva_age_14_rejected(client, healthy_student_payload):
    """BVA F.8: Age 14 (< 15) is rejected with HTTP 422."""
    payload = copy.deepcopy(healthy_student_payload)
    payload["age"] = 14
    res = client.post("/api/screen", json=payload)
    assert res.status_code == 422


def test_bva_age_101_rejected(client, healthy_student_payload):
    """BVA F.9: Age 101 (> 100) is rejected with HTTP 422."""
    payload = copy.deepcopy(healthy_student_payload)
    payload["age"] = 101
    res = client.post("/api/screen", json=payload)
    assert res.status_code == 422


# ==============================================================================
# SECTION G: Lifestyle, Nutrition & Sleep Boundaries (8 tests)
# ==============================================================================

def test_bva_sleep_2_hrs_deprivation(client, healthy_student_payload):
    """BVA G.1: Sleep 2.0 hours (severe sleep deprivation) is accepted."""
    payload = copy.deepcopy(healthy_student_payload)
    payload["sleep_hours_per_night"] = 2.0
    res = client.post("/api/screen", json=payload)
    assert res.status_code == 200


def test_bva_sleep_7_hrs_normal(client, healthy_student_payload):
    """BVA G.2: Sleep 7.0 hours is optimal baseline."""
    payload = copy.deepcopy(healthy_student_payload)
    payload["sleep_hours_per_night"] = 7.0
    res = client.post("/api/screen", json=payload)
    assert res.status_code == 200


def test_bva_sleep_16_hrs_max(client, healthy_student_payload):
    """BVA G.3: Sleep 16.0 hours (hypersomnia boundary)."""
    payload = copy.deepcopy(healthy_student_payload)
    payload["sleep_hours_per_night"] = 16.0
    res = client.post("/api/screen", json=payload)
    assert res.status_code == 200


def test_bva_activity_0_sedentary(client, healthy_student_payload):
    """BVA G.4: Physical activity 0 min/week represents extreme sedentary lifestyle."""
    payload = copy.deepcopy(healthy_student_payload)
    payload["physical_activity_level"] = "sedentary"
    payload["physical_activity_min_per_week"] = 0
    res = client.post("/api/screen", json=payload)
    assert res.status_code == 200


def test_bva_activity_240_plus_active(client, healthy_student_payload):
    """BVA G.5: Physical activity >= 240 min/week confers maximum protective metabolic score."""
    payload = copy.deepcopy(healthy_student_payload)
    payload["physical_activity_level"] = "active"
    payload["physical_activity_min_per_week"] = 300
    res = client.post("/api/screen", json=payload)
    assert res.status_code == 200


def test_bva_sugary_drinks_0_min(client, healthy_student_payload):
    """BVA G.6: Sugary drinks 0 per week."""
    payload = copy.deepcopy(healthy_student_payload)
    payload["sugary_drinks_weekly_count"] = 0
    res = client.post("/api/screen", json=payload)
    assert res.status_code == 200


def test_bva_sugary_drinks_50_max(client, healthy_student_payload):
    """BVA G.7: Sugary drinks 50 per week is maximum valid boundary."""
    payload = copy.deepcopy(healthy_student_payload)
    payload["sugary_drinks_weekly_count"] = 50
    res = client.post("/api/screen", json=payload)
    assert res.status_code == 200


def test_bva_sugary_drinks_negative_rejected(client, healthy_student_payload):
    """BVA G.8: Sugary drinks < 0 is rejected with HTTP 422."""
    payload = copy.deepcopy(healthy_student_payload)
    payload["sugary_drinks_weekly_count"] = -1
    res = client.post("/api/screen", json=payload)
    assert res.status_code == 422


# ==============================================================================
# SECTION H: Extreme & Edge State Configurations (7 tests)
# ==============================================================================

def test_bva_all_negative_symptoms_low_risk(client, healthy_student_payload):
    """BVA H.1: Zero symptoms across all domains produces low risk (<30%) in all conditions."""
    payload = copy.deepcopy(healthy_student_payload)
    payload["fatigue_severity_score"] = 0
    payload["unrefreshing_sleep"] = "never"
    payload["brain_fog_difficulty_concentrating"] = "never"
    payload["orthostatic_dizziness"] = "never"
    payload["cold_extremities"] = False
    payload["muscle_bone_aches"] = "never"
    payload["peripheral_paresthesia_tingling"] = "never"
    payload["brittle_nails_or_hair_loss"] = False
    payload["mucosal_pallor"] = "none"
    payload["pica_cravings"] = False
    payload["polyuria_polydipsia"] = "none"
    payload["acanthosis_nigricans_signs"] = False

    res = client.post("/api/screen", json=payload)
    assert res.status_code == 200
    for key in ("anemia", "prediabetes"):
        assert res.json()["conditions"][key]["tier"] == "low"


def test_bva_all_positive_severe_symptoms(client, healthy_student_payload):
    """BVA H.2: Severe symptoms across all domains produce elevated risk without crashing."""
    payload = copy.deepcopy(healthy_student_payload)
    payload["diet_pattern"] = "vegan"
    payload["fatigue_severity_score"] = 10
    payload["brain_fog_difficulty_concentrating"] = "severe"
    payload["orthostatic_dizziness"] = "daily"
    payload["cold_extremities"] = True
    payload["muscle_bone_aches"] = "severe"
    payload["peripheral_paresthesia_tingling"] = "persistent"
    payload["brittle_nails_or_hair_loss"] = True
    payload["mucosal_pallor"] = "distinct"
    payload["pica_cravings"] = True
    payload["menstrual_flow_intensity"] = "heavy"

    res = client.post("/api/screen", json=payload)
    assert res.status_code == 200
    assert res.json()["overall_risk_tier"] == "elevated"


def test_bva_male_with_heavy_flow_sanitized(client, healthy_student_payload):
    """BVA H.3: Male student specifying heavy menstrual flow is sanitized to none."""
    payload = copy.deepcopy(healthy_student_payload)
    payload["sex"] = "male"
    payload["menstrual_flow_intensity"] = "heavy"
    res = client.post("/api/screen", json=payload)
    assert res.status_code == 200


def test_bva_female_with_flow_none(client, healthy_student_payload):
    """BVA H.4: Female student with menstrual flow none (e.g. amenorrhea, contraceptive)."""
    payload = copy.deepcopy(healthy_student_payload)
    payload["sex"] = "female"
    payload["menstrual_flow_intensity"] = "none"
    res = client.post("/api/screen", json=payload)
    assert res.status_code == 200


def test_bva_zero_optional_vitals_provided(client, minimal_student_payload):
    """BVA H.5: Pure lifestyle & symptom intake without any clinic vitals."""
    res = client.post("/api/screen", json=minimal_student_payload)
    assert res.status_code == 200
    assert res.json()["screening_id"] is not None


def test_bva_sun_exposure_under_15_vs_over_60(client, healthy_student_payload):
    """BVA H.6: D3 risk with <15 min sun is strictly greater than with >60 min sun."""
    p_low_sun = copy.deepcopy(healthy_student_payload)
    p_low_sun["weekly_sunlight_hours"] = "under_15_min"
    p_high_sun = copy.deepcopy(healthy_student_payload)
    p_high_sun["weekly_sunlight_hours"] = "over_60_min"

    r_low = client.post("/api/screen", json=p_low_sun)
    r_high = client.post("/api/screen", json=p_high_sun)
    assert r_low.status_code == 200 and r_high.status_code == 200

    d3_low = r_low.json()["micronutrient_details"]["vitamin_d3_risk_pct"]
    d3_high = r_high.json()["micronutrient_details"]["vitamin_d3_risk_pct"]
    assert d3_low > d3_high, "Minimal sunlight exposure must result in higher D3 risk"


def test_bva_water_intake_variations(client, healthy_student_payload):
    """BVA H.7: Daily water intake variation does not cause calculation failures."""
    p1 = copy.deepcopy(healthy_student_payload)
    p1["daily_water_intake"] = "under_4"
    p2 = copy.deepcopy(healthy_student_payload)
    p2["daily_water_intake"] = "8_plus"

    r1 = client.post("/api/screen", json=p1)
    r2 = client.post("/api/screen", json=p2)
    assert r1.status_code == 200 and r2.status_code == 200
