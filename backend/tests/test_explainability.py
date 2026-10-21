"""Unit tests for Explainable AI (XAI) Additive Feature Attribution."""
import pytest
from app.ml.explainability import (
    calculate_shapley_probability_shares,
    compute_additive_feature_attribution,
    sigmoid,
)


def test_sigmoid_numerical_stability():
    assert sigmoid(0.0) == 0.5
    assert 0.0 < sigmoid(-100.0) < 1e-4
    assert 0.9999 < sigmoid(100.0) < 1.0


def test_additive_log_odds_conservation():
    beta_0 = -1.80
    attribs = {
        "feat_a": 0.55,
        "feat_b": 0.65,
        "feat_c": -0.30,
        "feat_d": 1.20,
        "feat_e": -0.40
    }
    metadata = {
        k: {"label": k.title(), "explanation": "test", "rationale": "test"}
        for k in attribs
    }

    pos, prot, cons = compute_additive_feature_attribution(
        beta_0=beta_0,
        log_odds_attribs=attribs,
        metadata_map=metadata
    )

    # Verify exact log-odds conservation: sum(phi_i) == z - beta_0
    sum_phi = sum(attribs.values())
    assert abs(cons["log_odds_sum"] - sum_phi) < 1e-4
    assert abs(cons["expected_displacement"] - sum_phi) < 1e-4


def test_probability_redistribution_closure():
    beta_0 = -2.20
    base_prob = sigmoid(beta_0)
    attribs = {
        "risk_1": 1.30,
        "risk_2": 0.90,
        "prot_1": -0.55,
        "prot_2": -0.40
    }
    z = beta_0 + sum(attribs.values())
    pred_prob = sigmoid(z)

    shares = calculate_shapley_probability_shares(base_prob, pred_prob, attribs)

    # Verify closure: sum(shares) approx equal to (pred_prob - base_prob) * 100
    expected_delta_pct = (pred_prob - base_prob) * 100.0
    actual_sum_shares = sum(shares.values())
    assert abs(actual_sum_shares - expected_delta_pct) < 1.5


def test_driver_polarity_and_sorting():
    beta_0 = -1.50
    attribs = {
        "big_risk": 1.20,
        "small_risk": 0.25,
        "neutral": 0.02,
        "big_protective": -0.80,
        "small_protective": -0.20
    }
    metadata = {
        k: {"label": k.title(), "explanation": "exp", "rationale": "rat"}
        for k in attribs
    }

    pos, prot, _ = compute_additive_feature_attribution(beta_0, attribs, metadata)

    # Check positive drivers
    assert len(pos) >= 2
    for d in pos:
        assert d.is_risk_increasing is True
        assert d.direction == "risk_driver"
        assert d.attribution_log_odds >= 0.05
    # Verify sorting
    assert pos[0].contribution_pct >= pos[1].contribution_pct

    # Check protective drivers
    assert len(prot) >= 2
    for d in prot:
        assert d.is_risk_increasing is False
        assert d.direction == "protective"
        assert d.attribution_log_odds <= -0.05
    # Verify sorting
    assert prot[0].contribution_pct >= prot[1].contribution_pct
