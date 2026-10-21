"""Pytest configuration and fixtures for EarlyCare E2E Opaque-Box Test Suite."""
import os
import sys
from typing import Any, Dict, Generator
import pytest
import httpx

# Ensure backend and root paths are available for imports
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BACKEND_DIR = os.path.join(ROOT_DIR, "backend")

for p in (ROOT_DIR, BACKEND_DIR):
    if p not in sys.path:
        sys.path.insert(0, p)


class TestClientWrapper:
    """Unified wrapper around httpx.Client or FastAPI TestClient."""

    def __init__(self, target_client: Any, is_live: bool = False):
        self._client = target_client
        self.is_live = is_live

    def get(self, url: str, **kwargs: Any) -> Any:
        return self._client.get(url, **kwargs)

    def post(self, url: str, **kwargs: Any) -> Any:
        return self._client.post(url, **kwargs)

    def put(self, url: str, **kwargs: Any) -> Any:
        return self._client.put(url, **kwargs)

    def delete(self, url: str, **kwargs: Any) -> Any:
        return self._client.delete(url, **kwargs)


@pytest.fixture(scope="session")
def client() -> Generator[TestClientWrapper, None, None]:
    """Yield an active API client targeting live service or in-process TestClient."""
    live_url = "http://127.0.0.1:8000"
    try:
        r = httpx.get(f"{live_url}/api/health", timeout=0.8)
        if r.status_code == 200:
            with httpx.Client(base_url=live_url, timeout=15.0) as http_client:
                yield TestClientWrapper(http_client, is_live=True)
                return
    except Exception:
        pass

    # Fallback to TestClient
    from starlette.testclient import TestClient
    from app.main import app

    with TestClient(app) as test_client:
        yield TestClientWrapper(test_client, is_live=False)


@pytest.fixture
def healthy_student_payload() -> Dict[str, Any]:
    """Balanced young adult student with healthy lifestyle and optimal vitals."""
    return {
        "age": 20,
        "sex": "female",
        "height_cm": 168.0,
        "weight_kg": 58.0,
        "waist_circumference_cm": 70.0,
        "resting_heart_rate": 72,
        "blood_pressure_systolic": 115,
        "blood_pressure_diastolic": 75,
        "fasting_blood_glucose_mgdl": 85.0,
        "hemoglobin_g_dl": 13.5,
        "diet_pattern": "omnivore",
        "iron_rich_food_freq": "frequently",
        "dairy_or_fortified_milk_freq": "sometimes",
        "daily_water_intake": "8_plus",
        "weekly_sunlight_hours": "min_30_to_60",
        "sunscreen_regular_use": False,
        "physical_activity_level": "moderate",
        "physical_activity_min_per_week": 180,
        "sugary_drinks_weekly_count": 0,
        "refined_carb_freq": "sometimes",
        "daily_caffeine_cups": 1,
        "sleep_hours_per_night": 7.5,
        "unrefreshing_sleep": "never",
        "fatigue_severity_score": 1,
        "brain_fog_difficulty_concentrating": "never",
        "orthostatic_dizziness": "never",
        "cold_extremities": False,
        "exertional_shortness_of_breath": "never",
        "muscle_bone_aches": "never",
        "peripheral_paresthesia_tingling": "never",
        "brittle_nails_or_hair_loss": False,
        "mucosal_pallor": "none",
        "pica_cravings": False,
        "polyuria_polydipsia": "none",
        "acanthosis_nigricans_signs": False,
        "chest_pain_or_syncope_reported": False,
        "menstrual_flow_intensity": "light",
        "menstrual_cycle_irregular": False,
        "family_history_diabetes": False,
        "family_history_anemia": False,
        "reactive_hypoglycemia_post_meal_crash": "never",
        "b12_supplementation": False,
        "d3_supplementation": True,
    }


@pytest.fixture
def anaemia_elevated_payload() -> Dict[str, Any]:
    """Female student with heavy menstrual loss, low iron intake, severe fatigue."""
    return {
        "age": 21,
        "sex": "female",
        "height_cm": 162.0,
        "weight_kg": 49.0,
        "waist_circumference_cm": 65.0,
        "diet_pattern": "vegan",
        "iron_rich_food_freq": "rarely_never",
        "menstrual_flow_intensity": "heavy",
        "menstrual_cycle_irregular": False,
        "fatigue_severity_score": 8,
        "cold_extremities": True,
        "orthostatic_dizziness": "frequent",
        "brittle_nails_or_hair_loss": True,
        "mucosal_pallor": "distinct",
        "pica_cravings": True,
        "hemoglobin_g_dl": 9.5,
        "physical_activity_level": "sedentary",
        "family_history_anemia": True,
        "chest_pain_or_syncope_reported": False,
    }


@pytest.fixture
def prediabetes_elevated_payload() -> Dict[str, Any]:
    """Sedentary student with elevated BMI, family history, high sugary beverages."""
    return {
        "age": 23,
        "sex": "male",
        "height_cm": 172.0,
        "weight_kg": 96.0,  # BMI ~ 32.4
        "waist_circumference_cm": 105.0,  # WHtR ~ 0.61
        "physical_activity_level": "sedentary",
        "physical_activity_min_per_week": 30,
        "sugary_drinks_weekly_count": 8,
        "refined_carb_freq": "frequently",
        "family_history_diabetes": True,
        "acanthosis_nigricans_signs": True,
        "fasting_blood_glucose_mgdl": 112.0,
        "blood_pressure_systolic": 132,
        "blood_pressure_diastolic": 86,
        "polyuria_polydipsia": "mild",
        "fatigue_severity_score": 4,
        "chest_pain_or_syncope_reported": False,
    }


@pytest.fixture
def d3_elevated_payload() -> Dict[str, Any]:
    """Indoor student with minimal sun exposure and bone/muscle aches."""
    return {
        "age": 20,
        "sex": "female",
        "height_cm": 165.0,
        "weight_kg": 55.0,
        "weekly_sunlight_hours": "under_15_min",
        "sunscreen_regular_use": True,
        "d3_supplementation": False,
        "muscle_bone_aches": "frequent",
        "fatigue_severity_score": 6,
        "diet_pattern": "omnivore",
        "chest_pain_or_syncope_reported": False,
    }


@pytest.fixture
def b12_elevated_payload() -> Dict[str, Any]:
    """Vegan student without B12 supplementation experiencing paresthesias and brain fog."""
    return {
        "age": 22,
        "sex": "male",
        "height_cm": 175.0,
        "weight_kg": 65.0,
        "diet_pattern": "vegan",
        "b12_supplementation": False,
        "peripheral_paresthesia_tingling": "frequent",
        "brain_fog_difficulty_concentrating": "frequent",
        "fatigue_severity_score": 7,
        "chest_pain_or_syncope_reported": False,
    }


@pytest.fixture
def calcium_elevated_payload() -> Dict[str, Any]:
    """Student with zero dairy/calcium servings and heavy daily caffeine."""
    return {
        "age": 21,
        "sex": "female",
        "height_cm": 160.0,
        "weight_kg": 52.0,
        "dairy_or_fortified_milk_freq": "rarely_never",
        "daily_caffeine_cups": 4,
        "muscle_bone_aches": "frequent",
        "fatigue_severity_score": 5,
        "weekly_sunlight_hours": "under_15_min",
        "d3_supplementation": False,
        "chest_pain_or_syncope_reported": False,
    }


@pytest.fixture
def minimal_student_payload() -> Dict[str, Any]:
    """Minimal student intake with only core demographic fields and no optional vitals."""
    return {
        "age": 20,
        "sex": "male",
        "height_cm": 170.0,
        "weight_kg": 65.0,
    }


@pytest.fixture
def emergency_red_flag_payload() -> Dict[str, Any]:
    """Student presenting with acute chest pain / syncope red-flag trigger."""
    return {
        "age": 22,
        "sex": "female",
        "height_cm": 165.0,
        "weight_kg": 58.0,
        "fatigue_severity_score": 9,
        "chest_pain_or_syncope_reported": True,
    }
