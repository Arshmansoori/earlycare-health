# E2E Test Infra: EarlyCare Student Health Screening Platform

## Test Philosophy
- Opaque-box, requirement-driven testing. Derived strictly from `ORIGINAL_REQUEST.md` and user-facing specifications, independent of internal module implementation.
- Methodology: Category-Partition, Boundary Value Analysis (BVA), Pairwise Combinatorial Testing, and Real-World Student Workload Testing.

## Feature Inventory & Test Coverage Mapping
| # | Feature | Source (Requirement) | Tier 1 (Coverage >=5) | Tier 2 (Boundary >=5) | Tier 3 (Pairwise) | Tier 4 (Scenario) |
|---|---------|----------------------|:---------------------:|:---------------------:|:-----------------:|:-----------------:|
| 1 | Anaemia Risk Stratifier | ORIGINAL_REQUEST §R1 | 5 | 5 | ✓ | ✓ |
| 2 | Pre-Diabetes Risk Stratifier | ORIGINAL_REQUEST §R1 | 5 | 5 | ✓ | ✓ |
| 3 | Micronutrient Matrix (D3, B12, Ca) | ORIGINAL_REQUEST §R1 | 5 | 5 | ✓ | ✓ |
| 4 | XAI Additive Feature Attribution | ORIGINAL_REQUEST §R1 | 5 | 5 | ✓ | ✓ |
| 5 | FastAPI Screening Endpoint (`/api/screen`) | ORIGINAL_REQUEST §R2 | 5 | 5 | ✓ | ✓ |
| 6 | FastAPI Explain Endpoint (`/api/explain`) | ORIGINAL_REQUEST §R2 | 5 | 5 | ✓ | ✓ |
| 7 | FastAPI SBAR Export Endpoint (`/api/export-sbar`) | ORIGINAL_REQUEST §R2 | 5 | 5 | ✓ | ✓ |
| 8 | Input Validation & Error Handling (Pydantic) | ORIGINAL_REQUEST §R2 | 5 | 5 | ✓ | ✓ |
| 9 | Warm Cream Web App Theme & Aesthetics | ORIGINAL_REQUEST §R3 | 5 | 5 | ✓ | ✓ |
| 10 | 3-Minute Multi-Step Intake Wizard | ORIGINAL_REQUEST §R3 | 5 | 5 | ✓ | ✓ |
| 11 | Risk Visual Analytics (Gauges, Radar, Cards) | ORIGINAL_REQUEST §R3 | 5 | 5 | ✓ | ✓ |
| 12 | Doctor-Ready SBAR Clinical Export & Print | ORIGINAL_REQUEST §R4 | 5 | 5 | ✓ | ✓ |
| 13 | Ethical & SaMD Guardrails (Disclaimer & Red-Flag) | ORIGINAL_REQUEST §R4 | 5 | 5 | ✓ | ✓ |

## Test Architecture
- **Location**: `proto\tests\`
- **Test Runner**: Python-based runner executing with PATH-fixed Python 3.12:
  `$env:PATH = "C:\Program Files\nodejs;C:\Users\arsh2\AppData\Local\Programs\Python\Python312;C:\Users\arsh2\AppData\Local\Programs\Python\Python312\Scripts;C:\Users\arsh2\AppData\Local\Programs\Git\cmd;" + $env:PATH; python -m pytest tests/`
- **Output Artifact**: Generates structured reports and publishes `TEST_READY.md` upon suite completion.

## Real-World Application Scenarios (Tier 4)
| # | Scenario | Features Exercised | Target Profile |
|---|----------|--------------------|----------------|
| 1 | Strict Vegan Student with Fatigue | F1, F3, F4, F5, F7, F10, F11, F12 | Elevated B12 & Anaemia risk, high fatigue, normal glycemic |
| 2 | Sedentary Student with Family T2D & High Sugary Drinks | F2, F4, F5, F7, F10, F11, F12 | Elevated Pre-Diabetes risk (high BMI, WHtR > 0.5), low anaemia |
| 3 | Outdoor Athlete with Optimal Nutrition & Vitals | F1, F2, F3, F4, F5, F7, F10, F11 | Low risk across all domains, negative protective attributions |
| 4 | Female Student with Heavy Menses & Low Iron Diet | F1, F3, F4, F5, F7, F10, F12 | Severe Anaemia risk, Ferritin gap, recommended CBC/Ferritin workup |
| 5 | Minimalist Screen: No Optional Vitals, Normal Demographics | F1, F2, F3, F5, F8, F10, F13 | Graceful default imputation, no crashes, balanced assessment |
| 6 | Emergency Red-Flag Intercept: Acute Chest Pain / Syncope | F10, F13 | Calculation halted, urgent care modal triggered |

## Coverage Thresholds
- **Tier 1 (Feature Coverage)**: ≥65 test cases (≥5 per feature across 13 features)
- **Tier 2 (Boundary & Corner)**: ≥65 test cases (≥5 per feature across 13 features)
- **Tier 3 (Cross-Feature Combinations)**: ≥15 pairwise interaction tests
- **Tier 4 (Real-World Scenarios)**: ≥6 comprehensive application-level scenarios
- **Total Minimum Target**: ≥151 verifiable test cases
