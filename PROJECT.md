# Project: EarlyCare — Student Health Risk Screening Platform

## Architecture
EarlyCare is a modern full-stack student health risk screening platform with an explainable ML inference backend and an intuitive, calming warm-cream Next.js frontend.

```
                  +---------------------------------------------------+
                  |             Student / Web Browser                 |
                  |  Next.js 14/15 + TypeScript + Tailwind CSS        |
                  |  Warm white-cream aesthetic (#FAF8F5 / #FDFBF7)   |
                  +-------------------------+-------------------------+
                                            |
                                            | HTTP (JSON, CORS on :8000)
                                            v
                  +---------------------------------------------------+
                  |            FastAPI Backend Service (:8000)        |
                  |  Pydantic v2 validation & error handling          |
                  +-------------------------+-------------------------+
                                            |
         +----------------------------------+----------------------------------+
         |                                  |                                  |
         v                                  v                                  v
+------------------+              +--------------------+              +--------------------+
|  ML Risk Engine  |              |  XAI Attribution   |              | SBAR Handover Gen  |
| - Anaemia        |              | - Additive log-odds|              | - Situation        |
| - Pre-Diabetes   |              |   decomposition    |              | - Background       |
| - Micronutrients |              | - Positive/Negative|              | - Assessment       |
|   (D3, B12, Ca)  |              |   risk drivers     |              | - Recommendation   |
+------------------+              +--------------------+              +--------------------+
```

## Feature Inventory
| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| 1 | Calibrated Anaemia Risk Stratifier | Non-invasive risk scoring for anaemia (diet, fatigue, pallor, menstrual flow, checkup Hb) returning 0-100% calibrated probability & risk tier | M1 | ORIGINAL_REQUEST §R1 |
| 2 | Pre-Diabetes / Insulin Resistance Stratifier | Clinical metabolic risk score (BMI, waist-to-height ratio, family history, sedentary habits, glucose vitals) | M1 | ORIGINAL_REQUEST §R1 |
| 3 | Micronutrient Deficiency Matrix | Probabilistic inference for Vitamin D3, Vitamin B12, and Calcium gaps based on lifestyle & symptoms | M1 | ORIGINAL_REQUEST §R1 |
| 4 | XAI Feature Attribution Engine | Transparent additive feature attribution (positive risk drivers vs protective negative drivers) | M1 | ORIGINAL_REQUEST §R1 |
| 5 | FastAPI Screening & Explanation API | Endpoints `POST /api/screen`, `POST /api/explain`, `GET /api/health` with Pydantic validation and error handling | M1 | ORIGINAL_REQUEST §R2 |
| 6 | Pytest Comprehensive Backend Test Suite | Unit & integration tests for all models, edge cases (all-negative, extreme fatigue, missing vitals), and API routes | M1 | ORIGINAL_REQUEST §R2 |
| 7 | Warm White-Cream Student Web App | Next.js + TypeScript + Tailwind CSS with custom palette (`#FAF8F5`/`#FDFBF7`, warm stone `#FFFFFF`/`#F8F6F0`, soft borders `#E9E4D8`) | M2 | ORIGINAL_REQUEST §R3 |
| 8 | 3-Minute Student Intake Wizard | 4-step progressive questionnaire (Demographics, Nutrition/Lifestyle, Symptoms/Fatigue, Metabolic/Reproductive) with live BMI & WHtR | M2 | ORIGINAL_REQUEST §R3 |
| 9 | Interactive Risk Visual Analytics | Animated SVG risk gauges, 6-axis risk radar chart, and expandable "Why this score?" factor attribution cards | M2 | ORIGINAL_REQUEST §R3 |
| 10 | SBAR Clinical Handover Generator & Export | SBAR (Situation, Background, Assessment, Recommendation) structured clinician summary with one-click print/PDF `@media print` | M3 | ORIGINAL_REQUEST §R4 |
| 11 | Ethical & SaMD Guardrails | Non-diagnostic screening disclaimer, emergency red-flag intercept modal, and zero-PII privacy design | M3 | ORIGINAL_REQUEST §R4 |
| 12 | Opaque-Box E2E Test Suite | 4-tier requirement-driven test suite (Feature, Boundary, Combinatorial, Real-World Scenarios) & TEST_READY.md | E2E-Track | Dual-Track Requirement |
| 13 | Final Integration & Adversarial Hardening | 100% E2E test pass across backend & frontend + Tier 5 adversarial stress testing | M4 | Final Milestone |

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| M1 | Multi-Condition Health Risk ML Engine & FastAPI Backend | Backend service: ML models (Anaemia, Pre-Diabetes, Micronutrients), XAI attribution, Pydantic schemas, FastAPI endpoints, pytest suite | none | DONE |
| M2 | Modern Student Web App & Visual Analytics | Frontend web app: Next.js + TypeScript, Tailwind warm cream theme, 3-min intake wizard, SVG risk gauges, radar chart, XAI cards | M1 Interface Contract | DONE |
| M3 | SBAR Clinical Handover & Ethical SaMD Guardrails | Clinician handover: SBAR report generator/view, print/PDF `@media print`, emergency intercept modal, zero-PII privacy enforcement | M1, M2 | DONE |
| E2E | E2E Testing Track | Independent opaque-box test harness & 4-tier test suite derived from ORIGINAL_REQUEST, publishing TEST_READY.md | none (parallel) | DONE |
| M4 | Final Milestone: 100% E2E Test Suite & Adversarial Hardening | End-to-end integration pass (Tiers 1-4) followed by Tier 5 adversarial testing & forensic audit pass | M1, M2, M3, E2E | DONE |

## Interface Contracts

### Backend API ↔ Frontend Web App (`/api/screen`)
- **Request Method**: `POST /api/screen`
- **Request Body (JSON)**:
```json
{
  "age": 20,
  "sex": "female",
  "height_cm": 165.0,
  "weight_kg": 52.0,
  "waist_circumference_cm": 68.0,
  "resting_heart_rate": 78,
  "blood_pressure_systolic": 112,
  "blood_pressure_diastolic": 72,
  "fasting_blood_glucose_mgdl": null,
  "hemoglobin_g_dl": null,
  "diet_pattern": "vegetarian",
  "iron_rich_food_freq": "rarely_never",
  "dairy_or_fortified_milk_freq": "rarely_never",
  "daily_water_intake": "4_to_7",
  "weekly_sunlight_hours": "under_2",
  "sunscreen_regular_use": true,
  "physical_activity_level": "light",
  "sugary_drinks_weekly_count": 1,
  "fatigue_severity_score": 8,
  "unrefreshing_sleep": "frequent",
  "brain_fog_difficulty_concentrating": "frequent",
  "orthostatic_dizziness": "frequent",
  "cold_extremities": true,
  "exertional_shortness_of_breath": "occasional",
  "muscle_bone_aches": "occasional",
  "peripheral_paresthesia_tingling": "frequent",
  "brittle_nails_or_hair_loss": true,
  "menstrual_flow_intensity": "heavy",
  "menstrual_cycle_irregular": false,
  "family_history_diabetes": false,
  "family_history_anemia": true,
  "reactive_hypoglycemia_post_meal_crash": "occasional",
  "acanthosis_nigricans_signs": false,
  "chest_pain_or_syncope_reported": false
}
```
- **Response Body (JSON)**:
```json
{
  "screening_id": "EC-2026-8941",
  "timestamp_utc": "2026-10-21T17:15:00Z",
  "overall_risk_summary": "Elevated anaemia and micronutrient risk indicators observed.",
  "conditions": {
    "anemia": {
      "domain_key": "anemia",
      "title": "Anaemia Risk Stratification",
      "calibrated_risk_pct": 76.0,
      "tier": "elevated",
      "confidence_score": 0.88,
      "clinical_summary": "High risk pattern driven by heavy menstrual blood loss and low iron intake.",
      "positive_drivers": [
        {"feature_name": "menstrual_flow_intensity", "display_label": "Heavy Menstrual Flow", "contribution_pct": 26.0, "is_risk_increasing": true, "plain_explanation": "Significant monthly iron loss."}
      ],
      "protective_drivers": [
        {"feature_name": "age", "display_label": "Young Adult", "contribution_pct": 4.0, "is_risk_increasing": false, "plain_explanation": "No age-related bone marrow suppression."}
      ],
      "lifestyle_recommendations": ["Incorporate iron-rich plant pairings with citrus."]
    },
    "prediabetes": {
      "domain_key": "prediabetes",
      "title": "Pre-Diabetes / Metabolic Risk",
      "calibrated_risk_pct": 16.0,
      "tier": "low",
      "confidence_score": 0.90,
      "clinical_summary": "Low metabolic risk profile.",
      "positive_drivers": [],
      "protective_drivers": [
        {"feature_name": "bmi", "display_label": "Normal BMI (19.1)", "contribution_pct": 15.0, "is_risk_increasing": false, "plain_explanation": "Healthy body mass index."}
      ],
      "lifestyle_recommendations": ["Maintain current physical activity."]
    },
    "micronutrients": {
      "domain_key": "micronutrients",
      "title": "Micronutrient Deficiency Matrix",
      "calibrated_risk_pct": 68.0,
      "tier": "moderate",
      "confidence_score": 0.85,
      "clinical_summary": "Elevated Vitamin B12 and Vitamin D3 risk indices.",
      "positive_drivers": [],
      "protective_drivers": [],
      "lifestyle_recommendations": ["Discuss Vitamin D3 and B12 supplementation with physician."]
    }
  },
  "micronutrient_details": {
    "vitamin_d3_risk_pct": 54.0,
    "vitamin_b12_risk_pct": 68.0,
    "calcium_risk_pct": 28.0,
    "iron_deficiency_risk_pct": 74.0
  },
  "radar_axes": [
    {"axis_label": "Hematological", "risk_score": 76.0},
    {"axis_label": "Metabolic", "risk_score": 16.0},
    {"axis_label": "Vitamin D3", "risk_score": 54.0},
    {"axis_label": "Vitamin B12", "risk_score": 68.0},
    {"axis_label": "Bone & Calcium", "risk_score": 28.0},
    {"axis_label": "Fatigue Index", "risk_score": 80.0}
  ],
  "calculated_vitals": {
    "bmi": 19.1,
    "bmi_category": "Normal weight",
    "whtr": 0.41,
    "whtr_category": "Healthy"
  },
  "sbar_report": {
    "screening_id": "EC-2026-8941",
    "timestamp": "2026-10-21T17:15:00Z",
    "situation": {...},
    "background": {...},
    "assessment": {...},
    "recommendation": {...}
  }
}
```

## Code Layout
```
c:\Users\arsh2\OneDrive\Desktop\proto\
├── backend\
│   ├── app\
│   │   ├── __init__.py
│   │   ├── main.py               # FastAPI entrypoint, CORS configuration
│   │   ├── api\
│   │   │   ├── __init__.py
│   │   │   └── routes.py         # /api/screen, /api/explain, /api/export-sbar, /api/health
│   │   ├── core\
│   │   │   ├── __init__.py
│   │   │   └── config.py         # App configuration & constants
│   │   ├── models\
│   │   │   ├── __init__.py
│   │   │   └── schemas.py        # Pydantic models for intake, response, and SBAR
│   │   ├── ml\
│   │   │   ├── __init__.py
│   │   │   ├── anemia.py         # Anaemia risk stratifier
│   │   │   ├── prediabetes.py    # Pre-diabetes / metabolic risk engine
│   │   │   ├── micronutrients.py # Vitamin D3, B12, Calcium gap matrix
│   │   │   └── explainability.py # Additive feature attribution decomposition
│   │   └── sbar\
│   │       ├── __init__.py
│   │       └── generator.py      # SBAR clinical report generator
│   ├── tests\
│   │   ├── __init__.py
│   │   ├── conftest.py           # Test fixtures & test clients
│   │   ├── test_anemia.py        # Model tests
│   │   ├── test_prediabetes.py
│   │   ├── test_micronutrients.py
│   │   ├── test_explainability.py
│   │   ├── test_api.py           # Integration & schema validation tests
│   │   └── test_sbar.py
│   ├── requirements.txt          # fastapi, uvicorn, pydantic, numpy, pytest, httpx
│   └── pytest.ini
├── frontend\
│   ├── src\
│   │   ├── app\
│   │   │   ├── layout.tsx        # Base warm white-cream layout & metadata
│   │   │   ├── page.tsx          # Main intake & results single-page/dashboard
│   │   │   ├── globals.css       # Tailwind directives & @media print stylesheet
│   │   ├── components\
│   │   │   ├── intake\           # 4-Step Intake Wizard
│   │   │   ├── analytics\        # SVG Risk Gauge, Radar Chart, XAI Factor Cards
│   │   │   ├── clinical\         # SBAR Modal, Print Layout, SaMD Disclaimer, Emergency Intercept
│   │   │   └── ui\               # Card, Button, Badge, Slider primitives
│   │   └── lib\
│   │       ├── api.ts            # Typed client for backend communication
│   │       ├── types.ts          # TypeScript interfaces
│   │       └── calculations.ts   # Client-side BMI/WHtR calculations
│   ├── package.json
│   ├── tsconfig.json
│   ├── tailwind.config.ts
│   └── next.config.mjs
├── tests\                        # E2E Testing Track Opaque-Box Suite
│   ├── e2e_runner.py             # E2E test runner (Tiers 1-4)
│   ├── test_tier1_features.py    # Tier 1: Feature coverage
│   ├── test_tier2_boundaries.py  # Tier 2: Boundary & corner cases
│   ├── test_tier3_combinations.py# Tier 3: Cross-feature combinations
│   └── test_tier4_scenarios.py   # Tier 4: Real-world student scenarios
├── TEST_INFRA.md
├── TEST_READY.md
└── PROJECT.md
```

## Mandatory Integrity Forensics & Coding Rules
1. Zero cheating, zero hardcoding: Models must calculate real probabilities and attributions from inputs.
2. Zero PII storage: No student names, emails, IDs, or IP addresses may be requested or stored.
3. Medical disclaimer must be non-diagnostic and visible on both intake and results screens.
4. All commands must use the PATH-prefix remediation for Node and Python.
