"""Empirical verification test suite for Challenger 2 (Milestones 2 & 3 Integration).

Verifies:
1. API Schema matching between frontend (lib/types.ts, lib/api.ts) and backend (app/models/schemas.py).
2. Emergency Red-Flag Intercept behavior (UI halting logic, backend urgent consult flags).
3. @media print CSS rules (hidden interactive elements, white backgrounds, non-clipping tables).
4. End-to-end data flow with sanitized frontend payloads against FastAPI endpoints.
"""
import re
from pathlib import Path
import pytest
from starlette.testclient import TestClient
from app.main import app
from app.models.schemas import (
    StudentIntakeRequest,
    ScreenResponse,
    ExplainResponse,
    SbarResponse,
)

ROOT_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = ROOT_DIR / "frontend"


@pytest.fixture
def client():
    return TestClient(app)


class TestApiSchemaMatching:
    """Verifies frontend TypeScript definitions match backend Pydantic models."""

    def test_frontend_intake_fields_match_backend_schema(self):
        types_file = FRONTEND_DIR / "src" / "lib" / "types.ts"
        assert types_file.exists(), f"Frontend types file missing: {types_file}"
        content = types_file.read_text(encoding="utf-8")

        # Extract fields from StudentIntakeData interface
        match = re.search(r"export interface StudentIntakeData\s*\{([^}]+)\}", content, re.DOTALL)
        assert match, "Could not locate StudentIntakeData interface in types.ts"

        intake_block = match.group(1)
        # Parse field names (lines with `field_name: ...` or `field_name?: ...`)
        field_matches = re.findall(r"^\s*([a-zA-Z0-9_]+)\??\s*:", intake_block, re.MULTILINE)
        frontend_fields = set(field_matches)

        backend_fields = set(StudentIntakeRequest.model_fields.keys())

        # Check every frontend field exists in backend schema
        for f in frontend_fields:
            assert f in backend_fields, f"Frontend field '{f}' not found in backend StudentIntakeRequest schema"

    def test_frontend_screening_result_fields_match_backend_schema(self):
        types_file = FRONTEND_DIR / "src" / "lib" / "types.ts"
        content = types_file.read_text(encoding="utf-8")

        match = re.search(r"export interface ScreeningResult\s*\{(.*?)\}\s*export interface ConditionExplanation", content, re.DOTALL)
        assert match, "Could not locate ScreeningResult interface in types.ts"

        screening_block = match.group(1)
        field_matches = re.findall(r"^\s*([a-zA-Z0-9_]+)\??\s*:", screening_block, re.MULTILINE)
        frontend_fields = set(field_matches)

        backend_fields = set(ScreenResponse.model_fields.keys())

        # All key backend fields must be captured by frontend interface
        required_keys = {
            "screening_id", "timestamp_utc", "overall_risk_summary", "overall_risk_tier",
            "highest_risk_condition", "urgent_consult_flag", "conditions",
            "micronutrient_details", "radar_axes", "calculated_vitals", "sbar_report",
            "recommendations", "disclaimer"
        }
        for k in required_keys:
            assert k in frontend_fields, f"Required response field '{k}' missing from frontend ScreeningResult"
            assert k in backend_fields, f"Required response field '{k}' missing from backend ScreenResponse"

    def test_frontend_sbar_report_fields_match_backend_schema(self):
        types_file = FRONTEND_DIR / "src" / "lib" / "types.ts"
        content = types_file.read_text(encoding="utf-8")

        match = re.search(r"export interface SbarReportPayload\s*\{([^}]+)\}", content, re.DOTALL)
        assert match, "Could not locate SbarReportPayload in types.ts"

        sbar_block = match.group(1)
        field_matches = re.findall(r"^\s*([a-zA-Z0-9_]+)\??\s*:", sbar_block, re.MULTILINE)
        frontend_fields = set(field_matches)

        backend_fields = set(SbarResponse.model_fields.keys())
        expected_sbar_fields = {
            "screening_id", "timestamp", "situation", "background",
            "assessment", "recommendation", "confirmatory_labs_suggested"
        }
        for f in expected_sbar_fields:
            assert f in frontend_fields, f"SBAR field '{f}' missing from frontend SbarReportPayload"
            assert f in backend_fields, f"SBAR field '{f}' missing from backend SbarResponse"


class TestEmergencyRedFlagIntercept:
    """Verifies that acute red flags trigger emergency takeover and halt normal flow."""

    def test_frontend_step4_red_flag_triggers_emergency_takeover(self):
        step4_file = FRONTEND_DIR / "src" / "components" / "intake" / "Step4ReproductiveMetabolic.tsx"
        assert step4_file.exists()
        content = step4_file.read_text(encoding="utf-8")

        # Verify handleRedFlagToggle immediately invokes onTriggerEmergency
        assert "onTriggerEmergency();" in content, "Step4 does not immediately call onTriggerEmergency on toggle"
        assert "chest_pain_or_syncope_reported" in content, "Step4 does not bind chest_pain_or_syncope_reported"

    def test_frontend_intake_page_halts_submission_on_red_flag(self):
        intake_file = FRONTEND_DIR / "src" / "app" / "intake" / "page.tsx"
        assert intake_file.exists()
        content = intake_file.read_text(encoding="utf-8")

        # Verify handleSubmit checks chest_pain_or_syncope_reported and returns immediately without screening
        pattern = r"if\s*\(\s*data\.chest_pain_or_syncope_reported\s*\)\s*\{\s*setIsEmergencyModalOpen\(true\);\s*return;\s*\}"
        assert re.search(pattern, content), "intake/page.tsx does not immediately halt handleSubmit on chest_pain_or_syncope_reported"

    def test_emergency_modal_contains_urgent_resources(self):
        modal_file = FRONTEND_DIR / "src" / "components" / "clinical" / "EmergencyModal.tsx"
        assert modal_file.exists()
        content = modal_file.read_text(encoding="utf-8")

        assert "tel:911" in content, "EmergencyModal missing 911 phone dial action"
        assert "Emergency Services" in content
        assert "Campus Student Health" in content
        assert "Do Not Proceed with Routine Online Screening" in content
        assert "halted routine wellness calculations" in content

    def test_backend_screen_sets_urgent_consult_flag(self, client):
        payload = {
            "age": 20,
            "sex": "female",
            "height_cm": 165.0,
            "weight_kg": 55.0,
            "chest_pain_or_syncope_reported": True
        }
        res = client.post("/api/screen", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["urgent_consult_flag"] is True
        assert "chest pain" in data["urgent_consult_reason"].lower() or "fainting" in data["urgent_consult_reason"].lower()


class TestMediaPrintCssRules:
    """Verifies that @media print styling satisfies ink-saving and layout constraints."""

    def test_print_media_query_exists(self):
        css_file = FRONTEND_DIR / "src" / "app" / "globals.css"
        assert css_file.exists()
        css = css_file.read_text(encoding="utf-8")

        assert "@media print" in css, "globals.css missing @media print block"

    def test_interactive_controls_hidden_in_print(self):
        css_file = FRONTEND_DIR / "src" / "app" / "globals.css"
        css = css_file.read_text(encoding="utf-8")

        # Check that nav, header, footer, button, .no-print are hidden with !important
        assert re.search(r"button[^{]*\{[^}]*display:\s*none\s*!important", css, re.DOTALL)
        assert re.search(r"\.no-print[^{]*\{[^}]*display:\s*none\s*!important", css, re.DOTALL)
        assert re.search(r"nav[^{]*\{[^}]*display:\s*none\s*!important", css, re.DOTALL)
        assert re.search(r"header[^{]*\{[^}]*display:\s*none\s*!important", css, re.DOTALL)
        assert re.search(r"footer[^{]*\{[^}]*display:\s*none\s*!important", css, re.DOTALL)

    def test_print_background_white_and_text_black(self):
        css_file = FRONTEND_DIR / "src" / "app" / "globals.css"
        css = css_file.read_text(encoding="utf-8")

        assert "background-color: #ffffff !important" in css
        assert "color: #000000 !important" in css

    def test_tables_and_cards_prevent_clipping(self):
        css_file = FRONTEND_DIR / "src" / "app" / "globals.css"
        css = css_file.read_text(encoding="utf-8")

        assert "border-collapse: collapse !important" in css
        assert "page-break-inside: avoid !important" in css or "break-inside: avoid !important" in css

    def test_sbar_print_template_has_print_only_class(self):
        template_file = FRONTEND_DIR / "src" / "components" / "clinical" / "SbarPrintTemplate.tsx"
        assert template_file.exists()
        content = template_file.read_text(encoding="utf-8")

        assert "print-only" in content, "SbarPrintTemplate must use 'print-only' class for print rendering"
        assert "Campus Student Health Center" in content
        assert "Physician Signature" in content
        assert "Zero-PII Anonymous" in content


class TestEndToEndApiPayloadIntegration:
    """Simulates real student submission exactly as generated by frontend lib/api.ts."""

    def test_sanitized_sample_profile_executes_cleanly(self, client):
        # Sample payload matching SAMPLE_STUDENT_PROFILE in frontend/src/app/intake/page.tsx
        frontend_data = {
            "age": 20,
            "sex": "female",
            "height_cm": 165.0,
            "weight_kg": 52.0,
            "waist_circumference_cm": 68.0,
            "resting_heart_rate": 78,
            "blood_pressure_systolic": 112,
            "blood_pressure_diastolic": 72,
            "fasting_blood_glucose_mgdl": None,
            "hemoglobin_g_dl": None,
            "diet_pattern": "vegetarian",
            "iron_rich_food_freq": "rarely_never",
            "dairy_or_fortified_milk_freq": "rarely_never",
            "daily_water_intake": "4_to_7",
            "weekly_sunlight_hours": "under_15_min",
            "sunscreen_regular_use": True,
            "physical_activity_level": "light",
            "sugary_drinks_weekly_count": 1,
            "b12_supplementation": False,
            "d3_supplementation": False,
            "fatigue_severity_score": 8,
            "unrefreshing_sleep": "frequent",
            "brain_fog_difficulty_concentrating": "frequent",
            "orthostatic_dizziness": "frequent",
            "cold_extremities": True,
            "exertional_shortness_of_breath": "occasional",
            "muscle_bone_aches": "occasional",
            "peripheral_paresthesia_tingling": "frequent",
            "brittle_nails_or_hair_loss": True,
            "menstrual_flow_intensity": "heavy",
            "menstrual_cycle_irregular": False,
            "family_history_diabetes": False,
            "family_history_anemia": True,
            "reactive_hypoglycemia_post_meal_crash": "occasional",
            "acanthosis_nigricans_signs": False,
            "chest_pain_or_syncope_reported": False,
        }

        # 1. Test /api/screen
        res_screen = client.post("/api/screen", json=frontend_data)
        assert res_screen.status_code == 200, f"Screen failed: {res_screen.text}"
        screen_json = res_screen.json()
        assert screen_json["overall_risk_tier"] in ("low", "moderate", "elevated")
        assert len(screen_json["radar_axes"]) == 6
        assert screen_json["calculated_vitals"]["bmi"] == 19.1
        assert "anemia" in screen_json["conditions"]
        assert "prediabetes" in screen_json["conditions"]
        assert "micronutrients" in screen_json["conditions"]

        # 2. Test /api/explain
        res_explain = client.post("/api/explain", json=frontend_data)
        assert res_explain.status_code == 200, f"Explain failed: {res_explain.text}"
        explain_json = res_explain.json()
        assert "anemia" in explain_json["explanations"]
        assert "prediabetes" in explain_json["explanations"]
        assert "micronutrients" in explain_json["explanations"]

        # 3. Test /api/export-sbar
        res_sbar = client.post("/api/export-sbar", json=frontend_data)
        assert res_sbar.status_code == 200, f"Export SBAR failed: {res_sbar.text}"
        sbar_json = res_sbar.json()
        assert "situation" in sbar_json
        assert "background" in sbar_json
        assert "assessment" in sbar_json
        assert "recommendation" in sbar_json
        assert len(sbar_json["confirmatory_labs_suggested"]) > 0

        # 4. Test /api/health
        res_health = client.get("/api/health")
        assert res_health.status_code == 200
        assert res_health.json()["status"] == "healthy"
