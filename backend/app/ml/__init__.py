"""Machine learning and risk stratification engines for EarlyCare."""
from app.ml.anemia import evaluate_anemia_risk
from app.ml.prediabetes import evaluate_prediabetes_risk
from app.ml.micronutrients import evaluate_micronutrients_risk
from app.ml.explainability import compute_additive_feature_attribution

__all__ = [
    "evaluate_anemia_risk",
    "evaluate_prediabetes_risk",
    "evaluate_micronutrients_risk",
    "compute_additive_feature_attribution",
]
