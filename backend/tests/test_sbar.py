"""Unit tests for SBAR Clinical Report Generator."""
import pytest
from app.models.schemas import StudentIntakeRequest
from app.ml.anemia import evaluate_anemia_risk
from app.ml.prediabetes import evaluate_prediabetes_risk
from app.ml.micronutrients import evaluate_micronutrients_risk
from app.sbar.generator import generate_sbar_report


def test_sbar_generation_elevated_conditions(elevated_anemia_payload):
    intake = StudentIntakeRequest(**elevated_anemia_payload)
    anemia_res, _, _ = evaluate_anemia_risk(intake)
    prediab_res, _, _ = evaluate_prediabetes_risk(intake)
    micro_res, micro_details, _, _ = evaluate_micronutrients_risk(intake)

    conditions = {
        "anemia": anemia_res,
        "prediabetes": prediab_res,
        "micronutrients": micro_res
    }

    report = generate_sbar_report(
        intake=intake,
        conditions=conditions,
        micronutrient_details=micro_details,
        screening_id="EC-2026-TEST01",
        urgent_flag=False
    )

    # Check 4 sections
    assert report.situation.title == "Situation"
    assert len(report.situation.bullet_points) > 0
    assert "female" in report.situation.content.lower()

    assert report.background.title == "Background"
    assert "BMI" in " ".join(report.background.bullet_points)

    assert report.assessment.title == "Assessment"
    assert "Anaemia" in " ".join(report.assessment.bullet_points)

    assert report.recommendation.title == "Recommendation"
    assert len(report.confirmatory_labs_suggested) > 0
    assert any("Ferritin" in lab or "CBC" in lab for lab in report.confirmatory_labs_suggested)

    # Non-diagnostic disclaimer check
    assert report.disclaimer is not None
    assert "not provide" in report.disclaimer.lower() or "screening" in report.disclaimer.lower()


def test_sbar_urgent_flag_alert():
    intake = StudentIntakeRequest(
        age=20,
        sex="female",
        height_cm=165.0,
        weight_kg=60.0,
        chest_pain_or_syncope_reported=True
    )
    anemia_res, _, _ = evaluate_anemia_risk(intake)
    prediab_res, _, _ = evaluate_prediabetes_risk(intake)
    micro_res, micro_details, _, _ = evaluate_micronutrients_risk(intake)

    report = generate_sbar_report(
        intake=intake,
        conditions={"anemia": anemia_res, "prediabetes": prediab_res, "micronutrients": micro_res},
        micronutrient_details=micro_details,
        screening_id="EC-2026-URGENT",
        urgent_flag=True,
        urgent_reason="Chest pain reported"
    )

    assert "RED FLAG" in report.situation.bullet_points[0]
