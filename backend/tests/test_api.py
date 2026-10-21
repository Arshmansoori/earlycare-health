"""Integration tests for EarlyCare FastAPI Endpoints."""
import pytest
from fastapi.testclient import TestClient


def test_health_check(client: TestClient):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "EarlyCare" in data["service"]
    assert "anemia" in data["calibrated_models"]
    assert "prediabetes" in data["calibrated_models"]
    assert "micronutrients" in data["calibrated_models"]


def test_root_endpoint(client: TestClient):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"


def test_screen_healthy_student(client: TestClient, healthy_student_payload):
    response = client.post("/api/screen", json=healthy_student_payload)
    assert response.status_code == 200
    data = response.json()

    assert data["screening_id"].startswith("EC-")
    assert "conditions" in data
    assert "anemia" in data["conditions"]
    assert "prediabetes" in data["conditions"]
    assert "micronutrients" in data["conditions"]

    # Verify radar axes (6 axes)
    assert len(data["radar_axes"]) == 6
    axis_labels = [a["axis_label"] for a in data["radar_axes"]]
    assert "Hematological" in axis_labels
    assert "Metabolic" in axis_labels
    assert "Vitamin D3" in axis_labels
    assert "Vitamin B12" in axis_labels
    assert "Bone & Calcium" in axis_labels
    assert "Fatigue Index" in axis_labels

    # Verify calculated vitals
    assert "calculated_vitals" in data
    assert data["calculated_vitals"]["bmi"] > 0
    assert data["calculated_vitals"]["whtr"] > 0

    # Verify non-diagnostic disclaimer
    assert "disclaimer" in data
    assert len(data["disclaimer"]) > 20


def test_screen_elevated_anemia(client: TestClient, elevated_anemia_payload):
    response = client.post("/api/screen", json=elevated_anemia_payload)
    assert response.status_code == 200
    data = response.json()

    anemia = data["conditions"]["anemia"]
    assert anemia["calibrated_risk_pct"] >= 70.0
    assert anemia["tier"] == "elevated"
    assert len(anemia["positive_drivers"]) > 0


def test_screen_elevated_prediabetes(client: TestClient, elevated_prediabetes_payload):
    response = client.post("/api/screen", json=elevated_prediabetes_payload)
    assert response.status_code == 200
    data = response.json()

    prediab = data["conditions"]["prediabetes"]
    assert prediab["calibrated_risk_pct"] >= 70.0
    assert prediab["tier"] == "elevated"


def test_screen_minimal_no_vitals(client: TestClient, minimal_student_no_vitals):
    response = client.post("/api/screen", json=minimal_student_no_vitals)
    assert response.status_code == 200
    data = response.json()
    assert "conditions" in data
    assert data["calculated_vitals"]["bmi"] > 0


def test_screen_male_flow_sanitization(client: TestClient, male_with_null_flow_payload):
    response = client.post("/api/screen", json=male_with_null_flow_payload)
    assert response.status_code == 200
    data = response.json()
    # Male should have 0 menstrual flow risk impact
    anemia = data["conditions"]["anemia"]
    driver_names = [d["feature_name"] for d in anemia["positive_drivers"]]
    assert "menstrual_blood_loss" not in driver_names


def test_screen_urgent_consult_flags(
    client: TestClient,
    urgent_consult_glucose_payload,
    urgent_consult_chest_pain_payload
):
    # Glucose alert
    res_glu = client.post("/api/screen", json=urgent_consult_glucose_payload)
    assert res_glu.status_code == 200
    assert res_glu.json()["urgent_consult_flag"] is True
    assert "glucose" in res_glu.json()["urgent_consult_reason"].lower()

    # Chest pain alert
    res_cp = client.post("/api/screen", json=urgent_consult_chest_pain_payload)
    assert res_cp.status_code == 200
    assert res_cp.json()["urgent_consult_flag"] is True
    assert "chest pain" in res_cp.json()["urgent_consult_reason"].lower()


def test_explain_endpoint(client: TestClient, healthy_student_payload):
    response = client.post("/api/explain", json=healthy_student_payload)
    assert response.status_code == 200
    data = response.json()

    assert "explanations" in data
    assert "anemia" in data["explanations"]
    assert "prediabetes" in data["explanations"]
    assert "micronutrients" in data["explanations"]

    for cond_key in ("anemia", "prediabetes", "micronutrients"):
        expl = data["explanations"][cond_key]
        assert "predicted_probability_pct" in expl
        assert "baseline_probability_pct" in expl
        assert "conservation_check" in expl


def test_export_sbar_endpoint(client: TestClient, elevated_anemia_payload):
    response = client.post("/api/export-sbar", json=elevated_anemia_payload)
    assert response.status_code == 200
    data = response.json()

    assert "situation" in data
    assert "background" in data
    assert "assessment" in data
    assert "recommendation" in data
    assert len(data["confirmatory_labs_suggested"]) > 0
    # CBC / Ferritin should be suggested for elevated anaemia
    labs_str = " ".join(data["confirmatory_labs_suggested"])
    assert "CBC" in labs_str or "Ferritin" in labs_str


def test_validation_errors(client: TestClient):
    # Invalid age (too young)
    res_age = client.post("/api/screen", json={"age": 10})
    assert res_age.status_code == 422

    # Invalid fatigue score (> 10)
    res_fatigue = client.post("/api/screen", json={"fatigue_severity_score": 15})
    assert res_fatigue.status_code == 422

    # Invalid height (too short)
    res_height = client.post("/api/screen", json={"height_cm": 50.0})
    assert res_height.status_code == 422


def test_screen_nested_structure(client: TestClient):
    nested_payload = {
        "demographics": {
            "age": 20,
            "sex": "female",
            "height_cm": 165.0,
            "weight_kg": 54.0,
            "waist_cm": 68.0
        },
        "lifestyle": {
            "diet_type": "vegetarian",
            "iron_rich_food_freq": "sometimes",
            "dairy_calcium_servings": 2,
            "physical_activity_min_per_week": 120,
            "daily_sun_exposure": "min_15_to_30"
        },
        "symptoms": {
            "fatigue_level": 3,
            "dizziness_freq": 1,
            "pallor_observed": 0,
            "cold_extremities": 1,
            "bone_muscle_aches": 0,
            "tingling_numbness": 0,
            "brain_fog": 1,
            "menstrual_flow": "moderate"
        },
        "vitals": {
            "routine_hb_g_dl": 12.8,
            "fasting_glucose_mg_dl": 92.0
        }
    }
    response = client.post("/api/screen", json=nested_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["screening_id"].startswith("EC-")
    assert data["calculated_vitals"]["bmi"] > 0
    assert "anemia" in data["conditions"]


def test_all_zero_symptoms(client: TestClient):
    payload = {
        "age": 20,
        "sex": "female",
        "height_cm": 165.0,
        "weight_kg": 55.0,
        "weekly_sunlight_hours": "over_60_min",
        "d3_supplementation": True,
        "fatigue_severity_score": 0,
        "orthostatic_dizziness": "never",
        "muscle_bone_aches": "none",
        "peripheral_paresthesia_tingling": "none",
        "brain_fog_difficulty_concentrating": "none",
        "cold_extremities": False,
        "mucosal_pallor": "none"
    }
    response = client.post("/api/screen", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["overall_risk_tier"] == "low"


def test_extreme_fatigue_and_dizziness_urgent_flag(client: TestClient):
    payload = {
        "age": 22,
        "sex": "female",
        "height_cm": 160.0,
        "weight_kg": 52.0,
        "fatigue_severity_score": 10,
        "orthostatic_dizziness": "daily"
    }
    response = client.post("/api/screen", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["urgent_consult_flag"] is True
    assert "fatigue" in data["urgent_consult_reason"].lower()
