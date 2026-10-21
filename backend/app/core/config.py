"""App configuration and clinical constants."""
from typing import List

PROJECT_NAME: str = "EarlyCare Health Risk Screening Engine"
VERSION: str = "1.0.0"
API_V1_STR: str = "/api"

CORS_ORIGINS: List[str] = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "*",
]

MEDICAL_DISCLAIMER: str = (
    "EarlyCare is an early-stage screening and health awareness platform designed "
    "for educational and preventive lifestyle guidance. It does NOT provide formal "
    "clinical diagnoses or replace clinical consultation with a licensed physician. "
    "If you experience red-flag symptoms such as acute chest pain, fainting (syncope), "
    "or severe shortness of breath, contact your campus medical center or emergency services immediately."
)

RISK_TIERS = {
    "LOW": "low",
    "MODERATE": "moderate",
    "ELEVATED": "elevated",
}
