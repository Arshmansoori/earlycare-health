"""Unit tests for Pydantic v2 schemas and models."""
import pytest
from pydantic import ValidationError
from app.models.schemas import StudentIntakeRequest, CalculatedVitals, DriverAttribution


def test_bmi_and_whtr_calculations():
    # 1. Normal weight student
    req = StudentIntakeRequest(
        age=20,
        sex="female",
        height_cm=165.0,
        weight_kg=54.0,
        waist_circumference_cm=68.0
    )
    # BMI = 54 / (1.65^2) = 19.83 -> 19.8
    assert req.bmi == 19.8
    assert req.bmi_category == "Normal weight"
    # WHtR = 68 / 165 = 0.41
    assert req.whtr == 0.41
    assert req.whtr_category == "Healthy"

    # 2. Overweight / Obese with unmeasured waist (regression fallback)
    req_heavy = StudentIntakeRequest(
        age=24,
        sex="male",
        height_cm=175.0,
        weight_kg=105.0,
        waist_circumference_cm=None
    )
    # BMI = 105 / (1.75^2) = 34.29 -> 34.3
    assert req_heavy.bmi == 34.3
    assert req_heavy.bmi_category == "Obesity"
    # Fallback WHtR = round(34.3 * 0.0175 + 0.10, 2) = 0.70
    assert req_heavy.whtr >= 0.60
    assert req_heavy.whtr_category == "Substantial risk"


def test_intake_validation_bounds():
    # Negative age raises ValidationError
    with pytest.raises(ValidationError):
        StudentIntakeRequest(age=-5)

    # Impossible height (> 250 cm) raises ValidationError
    with pytest.raises(ValidationError):
        StudentIntakeRequest(height_cm=300.0)

    # Impossible weight (< 25 kg) raises ValidationError
    with pytest.raises(ValidationError):
        StudentIntakeRequest(weight_kg=15.0)

    # Fatigue severity > 10 raises ValidationError
    with pytest.raises(ValidationError):
        StudentIntakeRequest(fatigue_severity_score=11)


def test_driver_attribution_structure():
    driver = DriverAttribution(
        feature_name="menstrual_blood_loss",
        display_label="Heavy Flow",
        contribution_pct=26.5,
        is_risk_increasing=True,
        plain_explanation="Significant blood loss",
        attribution_log_odds=1.20,
        direction="risk_driver"
    )
    assert driver.feature_name == "menstrual_blood_loss"
    assert driver.is_risk_increasing is True
    assert driver.contribution_pct == 26.5
