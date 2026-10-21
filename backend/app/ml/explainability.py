"""Mathematical Additive Explainable AI (XAI) Feature Attribution for EarlyCare.

Implements exact Shapley-style additive decomposition over log-odds with
normalized probability impact redistribution:
1. Local efficiency: sum(phi_i) == z - beta_0
2. Probability closure: sum(Delta P_i) == P(x) - P_base
3. Polarity separation: risk drivers (phi_i > 0) vs protective factors (phi_i < 0)
"""
import math
from typing import Dict, List, Optional, Tuple
from app.models.schemas import DriverAttribution


def sigmoid(z: float) -> float:
    """Clamped numerically stable sigmoid."""
    clamped_z = max(min(z, 20.0), -20.0)
    return 1.0 / (1.0 + math.exp(-clamped_z))


def calculate_shapley_probability_shares(
    base_prob: float,
    predicted_prob: float,
    log_odds_attribs: Dict[str, float]
) -> Dict[str, float]:
    """
    Distributes the net probability shift (P - P_base) proportionally
    to the log-odds weight of each feature, preserving exact mathematical conservation
    sum(shares) == P - P_base.
    """
    delta_p = predicted_prob - base_prob
    net_displacement = sum(log_odds_attribs.values())
    if abs(net_displacement) < 1e-6 or abs(delta_p) < 1e-6:
        return {k: 0.0 for k in log_odds_attribs}

    shares: Dict[str, float] = {}
    for k, v in log_odds_attribs.items():
        if abs(v) < 1e-6:
            shares[k] = 0.0
        else:
            feature_share = delta_p * (v / net_displacement)
            shares[k] = round(feature_share * 100.0, 1)
    return shares


def compute_additive_feature_attribution(
    beta_0: float,
    log_odds_attribs: Dict[str, float],
    metadata_map: Dict[str, Dict[str, str]]
) -> Tuple[List[DriverAttribution], List[DriverAttribution], Dict[str, float]]:
    """
    Computes positive and protective driver attributions and checks conservation.

    metadata_map maps feature_key to:
    {
        "label": "Display Label",
        "explanation": "Plain language clinical explanation",
        "rationale": "Medical rationale details"
    }
    """
    total_z = beta_0 + sum(log_odds_attribs.values())
    predicted_prob = sigmoid(total_z)
    base_prob = sigmoid(beta_0)

    prob_shares = calculate_shapley_probability_shares(
        base_prob=base_prob,
        predicted_prob=predicted_prob,
        log_odds_attribs=log_odds_attribs
    )

    positive_drivers: List[DriverAttribution] = []
    protective_drivers: List[DriverAttribution] = []

    for feat_key, phi in log_odds_attribs.items():
        meta = metadata_map.get(feat_key, {
            "label": feat_key.replace("_", " ").title(),
            "explanation": "Observed factor influencing baseline health risk.",
            "rationale": "Empirical risk correlation in student health cohort."
        })
        pct_share = prob_shares.get(feat_key, 0.0)

        # Classify polarity
        if phi >= 0.05:
            attr = DriverAttribution(
                feature_name=feat_key,
                feature_id=feat_key,
                display_label=meta.get("label", feat_key),
                contribution_pct=abs(pct_share),
                is_risk_increasing=True,
                direction="risk_driver",
                attribution_log_odds=round(phi, 3),
                plain_explanation=meta.get("explanation", ""),
                clinical_rationale=meta.get("rationale", "")
            )
            positive_drivers.append(attr)
        elif phi <= -0.05:
            attr = DriverAttribution(
                feature_name=feat_key,
                feature_id=feat_key,
                display_label=meta.get("label", feat_key),
                contribution_pct=abs(pct_share),
                is_risk_increasing=False,
                direction="protective",
                attribution_log_odds=round(phi, 3),
                plain_explanation=meta.get("explanation", ""),
                clinical_rationale=meta.get("rationale", "")
            )
            protective_drivers.append(attr)

    # Sort descending by contribution magnitude
    positive_drivers.sort(key=lambda d: d.contribution_pct, reverse=True)
    protective_drivers.sort(key=lambda d: d.contribution_pct, reverse=True)

    conservation_check = {
        "log_odds_sum": round(sum(log_odds_attribs.values()), 4),
        "expected_displacement": round(total_z - beta_0, 4),
        "prob_pct": round(predicted_prob * 100.0, 1),
        "baseline_prob_pct": round(base_prob * 100.0, 1),
        "net_displacement_pct": round((predicted_prob - base_prob) * 100.0, 1)
    }

    return positive_drivers, protective_drivers, conservation_check
