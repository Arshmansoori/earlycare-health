"""Shared fixtures and mock payloads for EarlyCare backend tests."""
import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture(scope="session")
def client() -> TestClient:
    """FastAPI TestClient fixture."""
    return TestClient(app)


@pytest.fixture
def healthy_student_payload() -> dict:
    """Low risk across all domains: normal BMI, omnivore, active, no symptoms."""
    return {
        "age": 20,
        "sex": "female",
        "height_cm": 165.0,
        "weight_kg": 58.0,
        "waist_circumference_cm": 70.0,
        "resting_heart_rate": 72,
        "blood_pressure_systolic": 115,
        "blood_pressure_diastolic": 75,
        "fasting_blood_glucose_mgdl": 88.0,
        "hemoglobin_g_dl": 13.5,
        "diet_pattern": "omnivore",
        "iron_rich_food_freq": "frequently",
        "dairy_or_fortified_milk_freq": "frequently",
        "daily_water_intake": "4_to_7",
        "weekly_sunlight_hours": "min_30_to_60",
        "sunscreen_regular_use": False,
        "physical_activity_level": "moderate",
        "physical_activity_min_per_week": 180,
        "sugary_drinks_weekly_count": 0,
        "fatigue_severity_score": 1,
        "unrefreshing_sleep": "never",
        "sleep_hours_per_night": 8.0,
        "brain_fog_difficulty_concentrating": "none",
        "orthostatic_dizziness": "never",
        "cold_extremities": False,
        "exertional_shortness_of_breath": "none",
        "muscle_bone_aches": "none",
        "peripheral_paresthesia_tingling": "none",
        "brittle_nails_or_hair_loss": False,
        "menstrual_flow_intensity": "light",
        "menstrual_cycle_irregular": False,
        "family_history_diabetes": False,
        "family_history_anemia": False,
        "reactive_hypoglycemia_post_meal_crash": "none",
        "acanthosis_nigricans_signs": False,
        "chest_pain_or_syncope_reported": False
    }


@pytest.fixture
def elevated_anemia_payload() -> dict:
    """Elevated anaemia profile: female, heavy flow, vegan, low iron food, fatigue 8, pallor, dizziness."""
    return {
        "age": 21,
        "sex": "female",
        "height_cm": 162.0,
        "weight_kg": 50.0,
        "waist_circumference_cm": 66.0,
        "resting_heart_rate": 84,
        "blood_pressure_systolic": 108,
        "blood_pressure_diastolic": 68,
        "fasting_blood_glucose_mgdl": None,
        "hemoglobin_g_dl": None,
        "diet_pattern": "vegan",
        "iron_rich_food_freq": "rarely_never",
        "dairy_or_fortified_milk_freq": "rarely_never",
        "daily_water_intake": "4_to_7",
        "weekly_sunlight_hours": "min_15_to_30",
        "sunscreen_regular_use": False,
        "physical_activity_level": "light",
        "sugary_drinks_weekly_count": 0,
        "fatigue_severity_score": 8,
        "unrefreshing_sleep": "frequent",
        "brain_fog_difficulty_concentrating": "occasional",
        "orthostatic_dizziness": "frequent",
        "cold_extremities": True,
        "exertional_shortness_of_breath": "occasional",
        "muscle_bone_aches": "none",
        "peripheral_paresthesia_tingling": "none",
        "brittle_nails_or_hair_loss": True,
        "menstrual_flow_intensity": "heavy",
        "menstrual_cycle_irregular": False,
        "family_history_diabetes": False,
        "family_history_anemia": True,
        "mucosal_pallor": "distinct",
        "pica_cravings": True,
        "chest_pain_or_syncope_reported": False
    }


@pytest.fixture
def elevated_prediabetes_payload() -> dict:
    """Elevated metabolic risk profile: high BMI, visceral waist, family history, sedentary, sodas, acanthosis."""
    return {
        "age": 23,
        "sex": "male",
        "height_cm": 175.0,
        "weight_kg": 98.0,
        "waist_circumference_cm": 105.0,
        "resting_heart_rate": 82,
        "blood_pressure_systolic": 134,
        "blood_pressure_diastolic": 86,
        "fasting_blood_glucose_mgdl": 112.0,
        "diet_pattern": "omnivore",
        "iron_rich_food_freq": "sometimes",
        "dairy_or_fortified_milk_freq": "sometimes",
        "physical_activity_level": "sedentary",
        "physical_activity_min_per_week": 30,
        "sugary_drinks_weekly_count": 8,
        "refined_carb_freq": "frequently",
        "sleep_hours_per_night": 4.5,
        "fatigue_severity_score": 6,
        "family_history_diabetes": 2,
        "acanthosis_nigricans_signs": True,
        "polyuria_polydipsia": "mild"
    }


@pytest.fixture
def elevated_d3_payload() -> dict:
    """Elevated D3 deficiency: indoor lifestyle, sunscreen, bone aches, no supplements."""
    return {
        "age": 22,
        "sex": "female",
        "height_cm": 168.0,
        "weight_kg": 62.0,
        "weekly_sunlight_hours": "under_15_min",
        "sunscreen_regular_use": True,
        "d3_supplementation": False,
        "muscle_bone_aches": "severe"
    }


@pytest.fixture
def elevated_b12_payload() -> dict:
    """Elevated B12 deficiency: strict unsupplemented vegan, paresthesias, brain fog."""
    return {
        "age": 20,
        "sex": "female",
        "height_cm": 160.0,
        "weight_kg": 54.0,
        "diet_pattern": "vegan",
        "b12_supplementation": False,
        "peripheral_paresthesia_tingling": "persistent",
        "brain_fog_difficulty_concentrating": "severe"
    }


@pytest.fixture
def minimal_student_no_vitals() -> dict:
    """Minimal student intake with zero vitals and only mandatory fields."""
    return {
        "age": 19,
        "sex": "male",
        "height_cm": 178.0,
        "weight_kg": 72.0
    }


@pytest.fixture
def male_with_null_flow_payload() -> dict:
    """Male student with menstrual flow submitted to test cross-field sanitization."""
    return {
        "age": 22,
        "sex": "male",
        "height_cm": 180.0,
        "weight_kg": 75.0,
        "menstrual_flow_intensity": "heavy"
    }


@pytest.fixture
def urgent_consult_glucose_payload() -> dict:
    """Student with fasting glucose in diabetes threshold (>=126 mg/dL)."""
    return {
        "age": 24,
        "sex": "male",
        "height_cm": 170.0,
        "weight_kg": 85.0,
        "fasting_blood_glucose_mgdl": 138.0
    }


@pytest.fixture
def urgent_consult_chest_pain_payload() -> dict:
    """Student reporting acute chest pain/syncope red flag."""
    return {
        "age": 20,
        "sex": "female",
        "height_cm": 165.0,
        "weight_kg": 60.0,
        "chest_pain_or_syncope_reported": True
    }
