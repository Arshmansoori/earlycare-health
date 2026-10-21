"""Unit tests for Pre-Diabetes / Metabolic Risk Engine."""
import pytest
from app.models.enums import RiskTierEnum
from app.models.schemas import StudentIntakeRequest
from app.ml.prediabetes import evaluate_prediabetes_risk, extract_prediabetes_log_odds


def test_prediabetes_healthy_low_risk(healthy_student_payload):
    intake = StudentIntakeRequest(**healthy_student_payload)
    result, attribs, prob_pct = evaluate_prediabetes_risk(intake)

    assert result.domain_key == "prediabetes"
    assert prob_pct < 30.0
    assert result.tier == RiskTierEnum.low
    assert 0.0 <= prob_pct <= 100.0


def test_prediabetes_elevated_risk(elevated_prediabetes_payload):
    intake = StudentIntakeRequest(**elevated_prediabetes_payload)
    result, attribs, prob_pct = evaluate_prediabetes_risk(intake)

    assert prob_pct >= 70.0
    assert result.tier == RiskTierEnum.elevated
    driver_names = [d.feature_name for d in result.positive_drivers]
    assert "bmi_adiposity" in driver_names
    assert "visceral_waist_height_ratio" in driver_names
    assert "acanthosis_nigricans_skin_marker" in driver_names


def test_prediabetes_glucose_thresholds():
    base = {
        "age": 22,
        "sex": "male",
        "height_cm": 175.0,
        "weight_kg": 75.0,
    }
    # Normal glucose
    intake_normal = StudentIntakeRequest(**base, fasting_blood_glucose_mgdl=85.0)
    _, _, p_normal = evaluate_prediabetes_risk(intake_normal)

    # Impaired fasting glucose
    intake_ifg = StudentIntakeRequest(**base, fasting_blood_glucose_mgdl=115.0)
    _, _, p_ifg = evaluate_prediabetes_risk(intake_ifg)

    # Diabetic threshold
    intake_dm = StudentIntakeRequest(**base, fasting_blood_glucose_mgdl=135.0)
    _, _, p_dm = evaluate_prediabetes_risk(intake_dm)

    assert p_normal < p_ifg < p_dm


def test_prediabetes_physical_activity_impact():
    base = {
        "age": 21,
        "sex": "female",
        "height_cm": 165.0,
        "weight_kg": 65.0,
    }
    intake_active = StudentIntakeRequest(**base, physical_activity_min_per_week=250)
    intake_sedentary = StudentIntakeRequest(**base, physical_activity_min_per_week=20)

    _, _, p_active = evaluate_prediabetes_risk(intake_active)
    _, _, p_sedentary = evaluate_prediabetes_risk(intake_sedentary)

    assert p_sedentary > p_active
