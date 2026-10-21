"""Unit tests for Anaemia Risk Stratifier."""
import pytest
from app.models.enums import RiskTierEnum
from app.models.schemas import StudentIntakeRequest
from app.ml.anemia import evaluate_anemia_risk, extract_anemia_log_odds


def test_anemia_healthy_student_low_risk(healthy_student_payload):
    intake = StudentIntakeRequest(**healthy_student_payload)
    result, attribs, prob_pct = evaluate_anemia_risk(intake)

    assert result.domain_key == "anemia"
    assert prob_pct < 30.0
    assert result.tier == RiskTierEnum.low
    assert 0.0 <= prob_pct <= 100.0
    assert len(result.protective_drivers) > 0


def test_anemia_elevated_risk(elevated_anemia_payload):
    intake = StudentIntakeRequest(**elevated_anemia_payload)
    result, attribs, prob_pct = evaluate_anemia_risk(intake)

    assert prob_pct >= 70.0
    assert result.tier == RiskTierEnum.elevated
    assert len(result.positive_drivers) > 0

    # Ensure heavy menstrual flow and pica are flagged as positive drivers
    driver_names = [d.feature_name for d in result.positive_drivers]
    assert "menstrual_blood_loss" in driver_names
    assert "pica_cravings" in driver_names


def test_anemia_fatigue_monotonicity():
    base_data = {
        "age": 20,
        "sex": "female",
        "height_cm": 165.0,
        "weight_kg": 55.0,
        "fatigue_severity_score": 1
    }
    intake_low_fatigue = StudentIntakeRequest(**base_data)
    _, _, prob_low = evaluate_anemia_risk(intake_low_fatigue)

    base_data["fatigue_severity_score"] = 9
    intake_high_fatigue = StudentIntakeRequest(**base_data)
    _, _, prob_high = evaluate_anemia_risk(intake_high_fatigue)

    assert prob_high > prob_low


def test_anemia_hemoglobin_anchor():
    # Low Hb should markedly increase risk
    low_hb_req = StudentIntakeRequest(
        age=20,
        sex="female",
        height_cm=165.0,
        weight_kg=55.0,
        hemoglobin_g_dl=9.5
    )
    _, _, prob_low_hb = evaluate_anemia_risk(low_hb_req)

    # Normal Hb should decrease risk
    normal_hb_req = StudentIntakeRequest(
        age=20,
        sex="female",
        height_cm=165.0,
        weight_kg=55.0,
        hemoglobin_g_dl=13.8
    )
    _, _, prob_normal_hb = evaluate_anemia_risk(normal_hb_req)

    assert prob_low_hb > prob_normal_hb
    assert prob_low_hb >= 50.0


def test_anemia_male_ignores_menstrual_flow():
    req = StudentIntakeRequest(
        age=22,
        sex="male",
        height_cm=175.0,
        weight_kg=70.0,
        menstrual_flow_intensity="heavy"
    )
    attribs = extract_anemia_log_odds(req)
    # Menstrual blood loss must be 0 for males
    assert attribs.get("menstrual_blood_loss", 0.0) == 0.0
