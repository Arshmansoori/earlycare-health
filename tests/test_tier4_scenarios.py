"""Tier 4: Real-World Student Application Scenarios (>=6 comprehensive workflows).

Tests end-to-end holistic application flows simulating authentic student personas:
- Scenario 1: Strict Vegan Student with Chronic Fatigue
- Scenario 2: Sedentary Student with Family T2D & High Sugary Drinks
- Scenario 3: Outdoor Athlete with Optimal Nutrition & Vitals
- Scenario 4: Female Student with Heavy Menses & Low Iron Diet
- Scenario 5: Minimalist Screen: No Optional Vitals, Normal Demographics
- Scenario 6: Emergency Red-Flag Intercept: Acute Chest Pain / Syncope
"""
import pytest


def test_scenario_1_strict_vegan_student_with_chronic_fatigue(client):
    """Scenario 1: Strict vegan university student presenting with unrefreshing sleep,

    paresthesias, brain fog, and chronic fatigue.
    Expected: Elevated Vitamin B12 and Anaemia risk, normal metabolic profile.
    Full workflow: /api/screen -> /api/explain -> /api/export-sbar.
    """
    persona = {
        "age": 21,
        "sex": "female",
        "height_cm": 164.0,
        "weight_kg": 52.0,
        "waist_circumference_cm": 68.0,
        "diet_pattern": "vegan",
        "iron_rich_food_freq": "rarely_never",
        "dairy_or_fortified_milk_freq": "rarely_never",
        "b12_supplementation": False,
        "d3_supplementation": False,
        "weekly_sunlight_hours": "min_15_to_30",
        "sunscreen_regular_use": False,
        "fatigue_severity_score": 8,
        "unrefreshing_sleep": "frequent",
        "brain_fog_difficulty_concentrating": "frequent",
        "peripheral_paresthesia_tingling": "frequent",
        "orthostatic_dizziness": "frequent",
        "cold_extremities": True,
        "brittle_nails_or_hair_loss": True,
        "menstrual_flow_intensity": "moderate",
        "physical_activity_level": "light",
        "sugary_drinks_weekly_count": 0,
        "family_history_diabetes": False,
        "chest_pain_or_syncope_reported": False,
    }

    # 1. Screen endpoint
    res_screen = client.post("/api/screen", json=persona)
    assert res_screen.status_code == 200
    screen_data = res_screen.json()

    assert screen_data["screening_id"].startswith("EC-")
    anemia_risk = screen_data["conditions"]["anemia"]["calibrated_risk_pct"]
    b12_risk = screen_data["micronutrient_details"]["vitamin_b12_risk_pct"]
    prediab_risk = screen_data["conditions"]["prediabetes"]["calibrated_risk_pct"]

    assert b12_risk >= 70.0, f"Vegan with paresthesias should have elevated B12 risk, got {b12_risk}%"
    assert anemia_risk >= 50.0, f"Expected elevated/moderate anaemia risk, got {anemia_risk}%"
    assert prediab_risk < 30.0, f"Expected low pre-diabetes risk in lean active vegan, got {prediab_risk}%"

    # 2. Explain endpoint
    res_explain = client.post("/api/explain", json=persona)
    assert res_explain.status_code == 200
    explain_data = res_explain.json()
    anemia_exp = explain_data["explanations"].get("anemia")
    assert anemia_exp is not None
    assert len(anemia_exp["positive_drivers"]) > 0

    # 3. SBAR export
    res_sbar = client.post("/api/export-sbar", json=persona)
    assert res_sbar.status_code == 200
    sbar = res_sbar.json()
    assert "situation" in sbar and "assessment" in sbar
    labs = " ".join(sbar.get("confirmatory_labs_suggested", [])).upper()
    assert "B12" in labs or "FERRITIN" in labs or "CBC" in labs or len(labs) > 0


def test_scenario_2_sedentary_student_metabolic_risk(client):
    """Scenario 2: Computer science student with sedentary lifestyle, high energy drink

    and soda intake, elevated BMI (33.5), positive family history of T2D, and Acanthosis Nigricans.
    Expected: Elevated Pre-Diabetes risk (>=70%), normal/low anaemia.
    """
    persona = {
        "age": 22,
        "sex": "male",
        "height_cm": 174.0,
        "weight_kg": 101.0,  # BMI ~ 33.4 (Obesity)
        "waist_circumference_cm": 108.0,  # WHtR ~ 0.62 (Substantial risk)
        "physical_activity_level": "sedentary",
        "physical_activity_min_per_week": 20,
        "sugary_drinks_weekly_count": 10,
        "refined_carb_freq": "frequently",
        "diet_pattern": "omnivore",
        "iron_rich_food_freq": "sometimes",
        "sleep_hours_per_night": 5.0,
        "family_history_diabetes": True,
        "acanthosis_nigricans_signs": True,
        "polyuria_polydipsia": "mild",
        "fatigue_severity_score": 4,
        "blood_pressure_systolic": 134,
        "blood_pressure_diastolic": 88,
        "fasting_blood_glucose_mgdl": 110.0,
        "chest_pain_or_syncope_reported": False,
    }

    # 1. Screen
    res = client.post("/api/screen", json=persona)
    assert res.status_code == 200
    data = res.json()
    prediab = data["conditions"]["prediabetes"]
    assert prediab["calibrated_risk_pct"] >= 70.0
    assert prediab["tier"] == "elevated"
    assert data["calculated_vitals"]["bmi_category"] == "Obesity"
    assert data["calculated_vitals"]["whtr_category"] == "Substantial risk"

    # 2. Explain
    res_exp = client.post("/api/explain", json=persona)
    assert res_exp.status_code == 200
    drivers = res_exp.json()["explanations"]["prediabetes"]["positive_drivers"]
    driver_names = [d["display_label"].lower() for d in drivers]
    assert any("bmi" in name or "weight" in name or "glucose" in name or "family" in name for name in driver_names)

    # 3. SBAR
    res_sbar = client.post("/api/export-sbar", json=persona)
    assert res_sbar.status_code == 200
    labs = " ".join(res_sbar.json().get("confirmatory_labs_suggested", [])).upper()
    assert "GLUCOSE" in labs or "HBA1C" in labs or "LIPID" in labs


def test_scenario_3_outdoor_athlete_optimal_wellness(client):
    """Scenario 3: University track athlete with 300+ min weekly training, outdoor sun,

    diverse omnivore diet, optimal vitals.
    Expected: Low risk across all domains (<30%), protective attributions dominating.
    """
    persona = {
        "age": 20,
        "sex": "male",
        "height_cm": 182.0,
        "weight_kg": 72.0,  # BMI ~ 21.7 (Normal)
        "waist_circumference_cm": 74.0,  # WHtR ~ 0.41 (Healthy)
        "resting_heart_rate": 54,
        "blood_pressure_systolic": 110,
        "blood_pressure_diastolic": 68,
        "fasting_blood_glucose_mgdl": 82.0,
        "hemoglobin_g_dl": 15.2,
        "diet_pattern": "omnivore",
        "iron_rich_food_freq": "frequently",
        "dairy_or_fortified_milk_freq": "frequently",
        "daily_water_intake": "8_plus",
        "weekly_sunlight_hours": "over_60_min",
        "sunscreen_regular_use": False,
        "physical_activity_level": "active",
        "physical_activity_min_per_week": 360,
        "sugary_drinks_weekly_count": 0,
        "refined_carb_freq": "rarely_never",
        "sleep_hours_per_night": 8.0,
        "fatigue_severity_score": 1,
        "unrefreshing_sleep": "never",
        "chest_pain_or_syncope_reported": False,
    }

    res = client.post("/api/screen", json=persona)
    assert res.status_code == 200
    data = res.json()

    assert data["overall_risk_tier"] == "low"
    for cond_key in ("anemia", "prediabetes", "micronutrients"):
        assert data["conditions"][cond_key]["tier"] == "low"
        assert data["conditions"][cond_key]["calibrated_risk_pct"] < 30.0

    # Explain shows robust protective factors
    res_exp = client.post("/api/explain", json=persona)
    assert res_exp.status_code == 200
    anemia_prot = res_exp.json()["explanations"]["anemia"]["protective_drivers"]
    assert len(anemia_prot) > 0


def test_scenario_4_female_student_heavy_menses_and_low_iron(client):
    """Scenario 4: Female student with heavy menstrual bleeding, paleness,

    pagophagia (ice cravings), cold hands, low hemoglobin (9.4 g/dL).
    Expected: Elevated Anaemia risk (>=70%), high Iron deficiency percentage, CBC/Ferritin recommendation.
    """
    persona = {
        "age": 19,
        "sex": "female",
        "height_cm": 160.0,
        "weight_kg": 48.0,
        "diet_pattern": "vegetarian",
        "iron_rich_food_freq": "rarely_never",
        "menstrual_flow_intensity": "heavy",
        "menstrual_cycle_irregular": False,
        "hemoglobin_g_dl": 9.4,
        "fatigue_severity_score": 9,
        "mucosal_pallor": "distinct",
        "pica_cravings": True,
        "cold_extremities": True,
        "brittle_nails_or_hair_loss": True,
        "orthostatic_dizziness": "frequent",
        "family_history_anemia": True,
        "chest_pain_or_syncope_reported": False,
    }

    res = client.post("/api/screen", json=persona)
    assert res.status_code == 200
    data = res.json()

    assert data["conditions"]["anemia"]["tier"] == "elevated"
    assert data["conditions"]["anemia"]["calibrated_risk_pct"] >= 70.0
    assert data["micronutrient_details"]["iron_deficiency_risk_pct"] >= 40.0

    # SBAR should recommend Ferritin & CBC
    res_sbar = client.post("/api/export-sbar", json=persona)
    assert res_sbar.status_code == 200
    labs = " ".join(res_sbar.json().get("confirmatory_labs_suggested", [])).upper()
    assert "FERRITIN" in labs or "CBC" in labs or "IRON" in labs


def test_scenario_5_minimalist_routine_check(client):
    """Scenario 5: Student providing only mandatory demographics with zero clinic vitals.

    Expected: Graceful imputation, valid scores, no exceptions.
    """
    persona = {
        "age": 20,
        "sex": "male",
        "height_cm": 172.0,
        "weight_kg": 68.0,
    }

    res = client.post("/api/screen", json=persona)
    assert res.status_code == 200
    data = res.json()
    assert "screening_id" in data
    assert 0.0 <= data["conditions"]["anemia"]["calibrated_risk_pct"] <= 100.0
    assert 0.0 <= data["conditions"]["prediabetes"]["calibrated_risk_pct"] <= 100.0
    assert 0.0 <= data["conditions"]["micronutrients"]["calibrated_risk_pct"] <= 100.0
    assert data["calculated_vitals"]["bmi"] == 23.0


def test_scenario_6_emergency_red_flag_symptom_presentation(client):
    """Scenario 6: Student reporting acute chest pain or syncope during screening.

    Expected: Urgent consult flag triggered, prompt clinical intercept instructions.
    """
    persona = {
        "age": 21,
        "sex": "female",
        "height_cm": 165.0,
        "weight_kg": 56.0,
        "fatigue_severity_score": 9,
        "chest_pain_or_syncope_reported": True,
    }

    res = client.post("/api/screen", json=persona)
    assert res.status_code == 200
    data = res.json()
    assert data["urgent_consult_flag"] is True
    assert data["urgent_consult_reason"] is not None
    assert len(data["urgent_consult_reason"]) > 5

    res_sbar = client.post("/api/export-sbar", json=persona)
    assert res_sbar.status_code == 200
    sit = res_sbar.json()["situation"]
    sit_str = (sit["content"] + " " + " ".join(sit.get("bullet_points", []))).lower()
    assert "urgent" in sit_str or "emergency" in sit_str or "alert" in sit_str or "chest" in sit_str
