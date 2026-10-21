"""Tests for Counterfactual Simulator, 7-Day Diet Blueprint, and Pallor Biomarker."""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models.schemas import StudentIntakeRequest
from app.ml.simulation import run_counterfactual_simulation, generate_campus_diet_blueprint
from app.ml.anemia import evaluate_anemia_risk

client = TestClient(app)

def test_camera_pallor_score_increases_anemia_risk():
    """Validates that optical pallor score >= 0.7 elevates anaemia calibrated risk."""
    base = StudentIntakeRequest(
        age=20,
        sex="female",
        height_cm=165,
        weight_kg=58,
        fatigue_severity_score=4,
        camera_pallor_score=None
    )
    with_pallor = StudentIntakeRequest(
        age=20,
        sex="female",
        height_cm=165,
        weight_kg=58,
        fatigue_severity_score=4,
        camera_pallor_score=0.85  # Severe optical pallor
    )

    res_base, _, prob_base = evaluate_anemia_risk(base)
    res_pallor, _, prob_pallor = evaluate_anemia_risk(with_pallor)

    assert prob_pallor > prob_base, "High optical pallor must elevate calibrated anaemia risk"
    assert any(d.feature_name == "camera_pallor_biomarker" for d in res_pallor.positive_drivers)

def test_simulate_endpoint_returns_valid_reductions():
    """Validates the /api/simulate endpoint reduces risk when positive habits are introduced."""
    payload = {
        "baseline_intake": {
            "age": 21,
            "sex": "female",
            "height_cm": 160,
            "weight_kg": 65,
            "diet_pattern": "vegetarian",
            "fatigue_severity_score": 7,
            "orthostatic_dizziness": "frequent",
            "cold_extremities": True,
            "daily_caffeine_cups": 3,
            "sleep_hours_per_night": 5.0,
            "sugary_drinks_weekly_count": 5
        },
        "modifications": {
            "sleep_hours": 8.0,
            "eliminate_post_meal_tea": True,
            "add_post_meal_walk": True,
            "sugary_drinks_weekly_count": 0,
            "weekly_sunlight_hours": "min_30_plus"
        }
    }
    resp = client.post("/api/simulate", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "baseline_risk_pcts" in data
    assert "counterfactual_risk_pcts" in data
    assert "risk_reductions_pct" in data
    assert data["counterfactual_risk_pcts"]["anemia"] < data["baseline_risk_pcts"]["anemia"]
    assert data["counterfactual_risk_pcts"]["prediabetes"] < data["baseline_risk_pcts"]["prediabetes"]

def test_diet_blueprint_endpoint():
    """Validates the /api/diet-blueprint endpoint outputs structured 7-day plan with hostel hacks."""
    payload = {
        "age": 20,
        "sex": "male",
        "height_cm": 175,
        "weight_kg": 72,
        "diet_pattern": "vegetarian",
        "fatigue_severity_score": 6
    }
    resp = client.post("/api/diet-blueprint", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "daily_schedule" in data
    assert len(data["daily_schedule"]) == 7
    assert "absorption_golden_rules" in data
    assert len(data["absorption_golden_rules"]) >= 4
    assert "estimated_weekly_budget_inr" in data
    # Check that day 1 has actionable student hostel hack
    assert len(data["daily_schedule"][0]["canteen_hostel_hack"]) > 10
