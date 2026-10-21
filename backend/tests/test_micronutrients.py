"""Unit tests for Micronutrient Deficiency Matrix (D3, B12, Calcium, Iron)."""
import pytest
from app.models.enums import RiskTierEnum
from app.models.schemas import StudentIntakeRequest
from app.ml.micronutrients import (
    evaluate_calcium,
    evaluate_micronutrients_risk,
    evaluate_vitamin_b12,
    evaluate_vitamin_d3,
)


def test_micronutrients_healthy_low_risk(healthy_student_payload):
    intake = StudentIntakeRequest(**healthy_student_payload)
    result, details, attribs, overall_pct = evaluate_micronutrients_risk(intake)

    assert result.domain_key == "micronutrients"
    assert 0.0 <= details.vitamin_d3_risk_pct <= 100.0
    assert 0.0 <= details.vitamin_b12_risk_pct <= 100.0
    assert 0.0 <= details.calcium_risk_pct <= 100.0
    assert 0.0 <= details.iron_deficiency_risk_pct <= 100.0
    assert result.tier in (RiskTierEnum.low, RiskTierEnum.moderate)


def test_vitamin_d3_indoor_vs_outdoor():
    intake_indoor = StudentIntakeRequest(
        age=20,
        weekly_sunlight_hours="under_15_min",
        sunscreen_regular_use=True,
        d3_supplementation=False,
        muscle_bone_aches="moderate"
    )
    p_indoor, _ = evaluate_vitamin_d3(intake_indoor)

    intake_outdoor = StudentIntakeRequest(
        age=20,
        weekly_sunlight_hours="over_60_min",
        sunscreen_regular_use=False,
        d3_supplementation=True,
        muscle_bone_aches="none"
    )
    p_outdoor, _ = evaluate_vitamin_d3(intake_outdoor)

    assert p_indoor >= 70.0
    assert p_outdoor < 20.0
    assert p_indoor > p_outdoor


def test_vitamin_b12_vegan_unsupplemented_vs_supplemented():
    intake_vegan = StudentIntakeRequest(
        age=21,
        diet_pattern="vegan",
        b12_supplementation=False,
        peripheral_paresthesia_tingling="frequent",
        brain_fog_difficulty_concentrating="frequent"
    )
    p_unsupp, _ = evaluate_vitamin_b12(intake_vegan)

    intake_supp = StudentIntakeRequest(
        age=21,
        diet_pattern="vegan",
        b12_supplementation=True,
        peripheral_paresthesia_tingling="none",
        brain_fog_difficulty_concentrating="none"
    )
    p_supp, _ = evaluate_vitamin_b12(intake_supp)

    assert p_unsupp >= 70.0
    assert p_supp < 25.0
    assert p_unsupp > p_supp


def test_calcium_cross_d3_interaction():
    intake = StudentIntakeRequest(
        age=22,
        dairy_or_fortified_milk_freq="rarely_never",
        daily_caffeine_cups=4,
        muscle_bone_aches="severe"
    )
    # High D3 deficiency (0.80) should trigger +0.50 interaction weight
    p_ca_high_d3, attr_high = evaluate_calcium(intake, d3_prob=0.85)
    p_ca_low_d3, attr_low = evaluate_calcium(intake, d3_prob=0.20)

    assert p_ca_high_d3 > p_ca_low_d3
    assert attr_high.get("d3_cross_depletion", 0.0) == 0.50
    assert attr_low.get("d3_cross_depletion", 0.0) == 0.0
