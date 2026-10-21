"""Tier 3: Pairwise & Cross-Feature Combinatorial Interaction Test Suite (>=15 tests).

Tests multi-variable interactions, compound risk amplifications, countervailing
protective vs risk dynamics, and cross-domain synergy across:
1. Vegan diet + Heavy menstrual flow (compound iron depletion)
2. Outdoor athlete + Family history of T2D (protective fitness vs genetic metabolic risk)
3. Sedentary lifestyle + High sugary drinks (synergistic insulin resistance)
4. Vegan diet + High sunlight exposure (B12 deficiency risk isolated from optimal D3)
5. Omnivore diet + Zero sun exposure + Sunscreen (isolated D3 risk)
6. High caffeine / energy drinks + Zero dairy intake (compound calcium depletion)
7. High fatigue + Low sun + Normal diet (D3 fatigue attribution vs normal haematology)
8. Male + High sugary drinks + Overweight BMI (metabolic risk in male student)
9. Female + Light menses + Iron-rich diet (protective haematology profile)
10. High fatigue + Acanthosis Nigricans + High BMI (metabolic fatigue attribution)
11. Heavy menses + Cold extremities + Brittle nails + High fatigue (iron deficiency cluster)
12. Vegan + No supplements + Tingling paresthesia + Brain fog (neuro-B12 deficiency cluster)
13. High physical activity + Low sugary drinks + High BMI (muscular athlete pattern)
14. Borderline fasting glucose (105 mg/dL) + High sugary drinks + Sedentary (pre-diabetes acceleration)
15. Female with irregular menses + High sugary drinks + Elevated BMI (PCOS-like metabolic pattern)
16. High sun exposure + D3 supplementation + High fatigue (isolating non-D3 fatigue)
17. Pescatarian diet + Regular exercise + Normal vitals (balanced intermediate lifestyle)
18. Normal BMI + Visceral adiposity (high WHtR) (isolated central adiposity risk)
"""
import copy
import pytest


def test_t3_01_vegan_and_heavy_menses_compound_depletion(client, healthy_student_payload):
    """T3.1: Vegan diet paired with heavy menstrual flow accelerates anaemia risk beyond either factor in isolation."""
    p_base = copy.deepcopy(healthy_student_payload)

    # Isolated vegan
    p_vegan = copy.deepcopy(healthy_student_payload)
    p_vegan["diet_pattern"] = "vegan"
    p_vegan["iron_rich_food_freq"] = "rarely_never"

    # Isolated heavy flow
    p_heavy = copy.deepcopy(healthy_student_payload)
    p_heavy["menstrual_flow_intensity"] = "heavy"

    # Compound
    p_both = copy.deepcopy(healthy_student_payload)
    p_both["diet_pattern"] = "vegan"
    p_both["iron_rich_food_freq"] = "rarely_never"
    p_both["menstrual_flow_intensity"] = "heavy"

    r_v = client.post("/api/screen", json=p_vegan).json()["conditions"]["anemia"]["calibrated_risk_pct"]
    r_h = client.post("/api/screen", json=p_heavy).json()["conditions"]["anemia"]["calibrated_risk_pct"]
    r_b = client.post("/api/screen", json=p_both).json()["conditions"]["anemia"]["calibrated_risk_pct"]

    assert r_b > r_v and r_b > r_h, f"Compound {r_b}% must exceed individual components ({r_v}%, {r_h}%)"


def test_t3_02_athlete_fitness_counters_family_t2d(client, healthy_student_payload):
    """T3.2: Vigorous physical activity and zero sugary drinks counterbalances genetic T2D risk."""
    p_sedentary_fam = copy.deepcopy(healthy_student_payload)
    p_sedentary_fam["family_history_diabetes"] = True
    p_sedentary_fam["physical_activity_level"] = "sedentary"
    p_sedentary_fam["physical_activity_min_per_week"] = 30

    p_active_fam = copy.deepcopy(healthy_student_payload)
    p_active_fam["family_history_diabetes"] = True
    p_active_fam["physical_activity_level"] = "active"
    p_active_fam["physical_activity_min_per_week"] = 300
    p_active_fam["sugary_drinks_weekly_count"] = 0

    r_sed = client.post("/api/screen", json=p_sedentary_fam).json()["conditions"]["prediabetes"]["calibrated_risk_pct"]
    r_act = client.post("/api/screen", json=p_active_fam).json()["conditions"]["prediabetes"]["calibrated_risk_pct"]

    assert r_act < r_sed, f"Active lifestyle ({r_act}%) should mitigate genetic T2D risk relative to sedentary ({r_sed}%)"


def test_t3_03_sedentary_and_sugary_drinks_synergy(client, healthy_student_payload):
    """T3.3: Sedentary habit combined with high sugary drinks produces synergistic metabolic risk increase."""
    p_base = copy.deepcopy(healthy_student_payload)
    p_base["fasting_blood_glucose_mgdl"] = None

    p_synergy = copy.deepcopy(healthy_student_payload)
    p_synergy["fasting_blood_glucose_mgdl"] = None
    p_synergy["physical_activity_level"] = "sedentary"
    p_synergy["physical_activity_min_per_week"] = 0
    p_synergy["sugary_drinks_weekly_count"] = 10

    r_base = client.post("/api/screen", json=p_base).json()["conditions"]["prediabetes"]["calibrated_risk_pct"]
    r_syn = client.post("/api/screen", json=p_synergy).json()["conditions"]["prediabetes"]["calibrated_risk_pct"]

    assert r_syn > r_base + 5.0, f"Synergistic risk {r_syn}% must exceed baseline {r_base}%"


def test_t3_04_vegan_diet_with_optimal_sun_isolates_b12(client, healthy_student_payload):
    """T3.4: Vegan student with plentiful sunlight exhibits elevated B12 risk but low D3 risk."""
    payload = copy.deepcopy(healthy_student_payload)
    payload["diet_pattern"] = "vegan"
    payload["b12_supplementation"] = False
    payload["weekly_sunlight_hours"] = "over_60_min"
    payload["sunscreen_regular_use"] = False

    res = client.post("/api/screen", json=payload)
    assert res.status_code == 200
    micro = res.json()["micronutrient_details"]
    assert micro["vitamin_b12_risk_pct"] >= 45.0
    assert micro["vitamin_d3_risk_pct"] < 35.0


def test_t3_05_omnivore_with_zero_sun_isolates_d3(client, healthy_student_payload):
    """T3.5: Omnivore with regular meat/dairy but zero sunlight exhibits high D3 risk with low B12 risk."""
    payload = copy.deepcopy(healthy_student_payload)
    payload["diet_pattern"] = "omnivore"
    payload["weekly_sunlight_hours"] = "under_15_min"
    payload["sunscreen_regular_use"] = True
    payload["d3_supplementation"] = False

    res = client.post("/api/screen", json=payload)
    assert res.status_code == 200
    micro = res.json()["micronutrient_details"]
    assert micro["vitamin_d3_risk_pct"] > 65.0
    assert micro["vitamin_b12_risk_pct"] < 30.0


def test_t3_06_high_caffeine_and_zero_dairy_calcium_gap(client, healthy_student_payload):
    """T3.6: Excessive caffeine with zero dairy intake increases calcium deficiency risk."""
    payload = copy.deepcopy(healthy_student_payload)
    payload["dairy_or_fortified_milk_freq"] = "rarely_never"
    payload["daily_caffeine_cups"] = 4
    payload["muscle_bone_aches"] = "occasional"

    res = client.post("/api/screen", json=payload)
    assert res.status_code == 200
    micro = res.json()["micronutrient_details"]
    assert micro["calcium_risk_pct"] > 45.0


def test_t3_07_d3_fatigue_attribution_with_normal_hb(client, healthy_student_payload):
    """T3.7: High fatigue in indoor student with normal Hb attributes fatigue to D3 rather than anaemia."""
    payload = copy.deepcopy(healthy_student_payload)
    payload["weekly_sunlight_hours"] = "under_15_min"
    payload["d3_supplementation"] = False
    payload["fatigue_severity_score"] = 7
    payload["hemoglobin_g_dl"] = 14.0  # optimal Hb

    res = client.post("/api/screen", json=payload)
    assert res.status_code == 200
    conditions = res.json()["conditions"]
    assert conditions["anemia"]["tier"] == "low"
    assert res.json()["micronutrient_details"]["vitamin_d3_risk_pct"] > 60.0


def test_t3_08_male_with_high_soda_and_high_bmi(client, healthy_student_payload):
    """T3.8: Young male student with obesity and sugary beverages has elevated metabolic risk."""
    payload = copy.deepcopy(healthy_student_payload)
    payload["sex"] = "male"
    payload["height_cm"] = 175.0
    payload["weight_kg"] = 98.0  # BMI 32.0
    payload["waist_circumference_cm"] = 102.0  # WHtR ~ 0.58
    payload["fasting_blood_glucose_mgdl"] = None
    payload["physical_activity_min_per_week"] = 0
    payload["sugary_drinks_weekly_count"] = 8
    payload["physical_activity_level"] = "sedentary"

    res = client.post("/api/screen", json=payload)
    assert res.status_code == 200
    assert res.json()["conditions"]["prediabetes"]["tier"] in ("moderate", "elevated")


def test_t3_09_female_light_menses_and_iron_rich_diet_protective(client, healthy_student_payload):
    """T3.9: Female student with light menses and iron-rich diet maintains low anaemia risk."""
    payload = copy.deepcopy(healthy_student_payload)
    payload["sex"] = "female"
    payload["menstrual_flow_intensity"] = "light"
    payload["iron_rich_food_freq"] = "frequently"
    payload["fatigue_severity_score"] = 1

    res = client.post("/api/screen", json=payload)
    assert res.status_code == 200
    assert res.json()["conditions"]["anemia"]["calibrated_risk_pct"] < 25.0


def test_t3_10_fatigue_with_acanthosis_and_obesity(client, healthy_student_payload):
    """T3.10: High fatigue in the presence of Acanthosis Nigricans and high BMI reflects insulin resistance."""
    payload = copy.deepcopy(healthy_student_payload)
    payload["height_cm"] = 168.0
    payload["weight_kg"] = 92.0  # BMI 32.6
    payload["waist_circumference_cm"] = 100.0  # WHtR ~ 0.60
    payload["fasting_blood_glucose_mgdl"] = None
    payload["physical_activity_min_per_week"] = 0
    payload["acanthosis_nigricans_signs"] = True
    payload["fatigue_severity_score"] = 8

    res = client.post("/api/screen", json=payload)
    assert res.status_code == 200
    prediab = res.json()["conditions"]["prediabetes"]
    assert prediab["calibrated_risk_pct"] > 40.0


def test_t3_11_iron_deficiency_clinical_cluster(client, healthy_student_payload):
    """T3.11: Heavy flow, cold extremities, brittle nails, and high fatigue cluster in elevated/moderate anaemia tier."""
    payload = copy.deepcopy(healthy_student_payload)
    payload["hemoglobin_g_dl"] = None
    payload["diet_pattern"] = "vegetarian"
    payload["iron_rich_food_freq"] = "rarely_never"
    payload["menstrual_flow_intensity"] = "heavy"
    payload["cold_extremities"] = True
    payload["brittle_nails_or_hair_loss"] = True
    payload["fatigue_severity_score"] = 8

    res = client.post("/api/screen", json=payload)
    assert res.status_code == 200
    anemia = res.json()["conditions"]["anemia"]
    assert anemia["tier"] in ("moderate", "elevated")
    assert anemia["calibrated_risk_pct"] > 50.0


def test_t3_12_vegan_neuro_b12_cluster(client, healthy_student_payload):
    """T3.12: Vegan + unsupplemented + paresthesias + brain fog triggers elevated B12 deficiency risk."""
    payload = copy.deepcopy(healthy_student_payload)
    payload["diet_pattern"] = "vegan"
    payload["b12_supplementation"] = False
    payload["peripheral_paresthesia_tingling"] = "frequent"
    payload["brain_fog_difficulty_concentrating"] = "frequent"

    res = client.post("/api/screen", json=payload)
    assert res.status_code == 200
    micro = res.json()["micronutrient_details"]
    assert micro["vitamin_b12_risk_pct"] >= 70.0


def test_t3_13_athletic_high_bmi_healthy_whtr(client, healthy_student_payload):
    """T3.13: Athletic student with high BMI (muscular build) but narrow waist (healthy WHtR)."""
    payload = copy.deepcopy(healthy_student_payload)
    payload["height_cm"] = 180.0
    payload["weight_kg"] = 86.0  # BMI 26.5 (Overweight)
    payload["waist_circumference_cm"] = 78.0  # WHtR 0.43 (Healthy)
    payload["physical_activity_level"] = "active"
    payload["physical_activity_min_per_week"] = 300

    res = client.post("/api/screen", json=payload)
    assert res.status_code == 200
    vitals = res.json()["calculated_vitals"]
    assert vitals["whtr_category"] == "Healthy"
    # Pre-diabetes risk should be low due to high activity and healthy waist
    assert res.json()["conditions"]["prediabetes"]["tier"] in ("low", "moderate")


def test_t3_14_borderline_glucose_sedentary_soda_acceleration(client, healthy_student_payload):
    """T3.14: Fasting glucose 105 mg/dL paired with high sugary drinks and inactivity elevates risk."""
    payload = copy.deepcopy(healthy_student_payload)
    payload["fasting_blood_glucose_mgdl"] = 105.0
    payload["sugary_drinks_weekly_count"] = 6
    payload["physical_activity_level"] = "sedentary"
    payload["physical_activity_min_per_week"] = 0
    payload["waist_circumference_cm"] = 88.0

    res = client.post("/api/screen", json=payload)
    assert res.status_code == 200
    assert res.json()["conditions"]["prediabetes"]["calibrated_risk_pct"] > 30.0


def test_t3_15_irregular_menses_soda_high_bmi_pattern(client, healthy_student_payload):
    """T3.15: Irregular menstrual cycle with elevated BMI and sugary drinks."""
    payload = copy.deepcopy(healthy_student_payload)
    payload["height_cm"] = 163.0
    payload["weight_kg"] = 75.0  # BMI ~ 28.2
    payload["fasting_blood_glucose_mgdl"] = None
    payload["physical_activity_min_per_week"] = 0
    payload["waist_circumference_cm"] = 88.0
    payload["menstrual_cycle_irregular"] = True
    payload["sugary_drinks_weekly_count"] = 5

    res = client.post("/api/screen", json=payload)
    assert res.status_code == 200
    assert res.json()["conditions"]["prediabetes"]["calibrated_risk_pct"] > 15.0


def test_t3_16_optimal_sun_and_d3_with_fatigue_isolates_etiology(client, healthy_student_payload):
    """T3.16: Abundant sun and D3 supplementation with fatigue shows low D3 risk, ruling out D3 deficit."""
    payload = copy.deepcopy(healthy_student_payload)
    payload["weekly_sunlight_hours"] = "over_60_min"
    payload["d3_supplementation"] = True
    payload["fatigue_severity_score"] = 8

    res = client.post("/api/screen", json=payload)
    assert res.status_code == 200
    micro = res.json()["micronutrient_details"]
    assert micro["vitamin_d3_risk_pct"] < 30.0


def test_t3_17_pescatarian_active_balanced_profile(client, healthy_student_payload):
    """T3.17: Pescatarian active student demonstrates balanced low-to-moderate risk distribution."""
    payload = copy.deepcopy(healthy_student_payload)
    payload["diet_pattern"] = "pescatarian"
    payload["physical_activity_level"] = "moderate"
    payload["daily_water_intake"] = "8_plus"

    res = client.post("/api/screen", json=payload)
    assert res.status_code == 200
    assert res.json()["overall_risk_tier"] in ("low", "moderate")


def test_t3_18_normal_bmi_with_elevated_whtr_visceral_adiposity(client, healthy_student_payload):
    """T3.18: Normal BMI (23.5) with central adiposity (waist 88cm, WHtR 0.53) elevates metabolic risk."""
    payload = copy.deepcopy(healthy_student_payload)
    payload["height_cm"] = 165.0
    payload["weight_kg"] = 64.0  # BMI 23.5 (Normal)
    payload["waist_circumference_cm"] = 88.0  # WHtR 0.53 (Increased risk)

    res = client.post("/api/screen", json=payload)
    assert res.status_code == 200
    assert res.json()["calculated_vitals"]["whtr_category"] == "Increased risk"
