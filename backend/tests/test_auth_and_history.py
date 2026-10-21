"""Unit & Integration Tests for User Accounts, Google Auth, and Screening History."""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.database import init_db

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_database():
    init_db()


def test_auth_google_direct_email_login():
    """Tests signing in directly with email and name (student profile mode)."""
    payload = {
        "email": "test.student@campus.edu",
        "name": "Test Student",
        "picture": "https://example.com/avatar.jpg"
    }
    resp = client.post("/api/auth/google", json=payload)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "Bearer"
    assert data["user"]["email"] == "test.student@campus.edu"
    assert data["user"]["name"] == "Test Student"


def test_auth_me_protected_endpoint():
    """Tests /api/auth/me requiring valid Bearer JWT."""
    # 1. Unauthenticated request should fail
    resp_unauth = client.get("/api/auth/me")
    assert resp_unauth.status_code == 401

    # 2. Authenticate
    login_resp = client.post("/api/auth/google", json={"email": "me.test@campus.edu", "name": "Me Tester"})
    token = login_resp.json()["access_token"]

    # 3. Authenticated request should succeed
    resp_auth = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp_auth.status_code == 200
    assert resp_auth.json()["email"] == "me.test@campus.edu"


def test_screen_automatic_save_when_authenticated():
    """Tests that /api/screen automatically persists the screening if Bearer token is provided."""
    # 1. Authenticate user
    login_resp = client.post("/api/auth/google", json={"email": "autosave.student@campus.edu", "name": "Auto Saver"})
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. History should initially be empty
    hist_before = client.get("/api/results/history", headers=headers).json()
    initial_count = len(hist_before)

    # 3. Perform screening with Authorization header
    intake_data = {
        "age": 21,
        "sex": "female",
        "height_cm": 165.0,
        "weight_kg": 54.0,
        "diet_pattern": "vegetarian",
        "fatigue_severity_score": 7,
        "unrefreshing_sleep": "frequent"
    }
    screen_resp = client.post("/api/screen", json=intake_data, headers=headers)
    assert screen_resp.status_code == 200
    screening_id = screen_resp.json()["screening_id"]

    # 4. History should now contain the new screening
    hist_after = client.get("/api/results/history", headers=headers).json()
    assert len(hist_after) == initial_count + 1
    latest = hist_after[0]
    assert latest["screening_id"] == screening_id
    assert latest["anemia_risk_pct"] > 0

    # 5. Fetch detail of saved screening
    detail_resp = client.get(f"/api/results/{screening_id}", headers=headers)
    assert detail_resp.status_code == 200
    detail = detail_resp.json()
    assert detail["screening_id"] == screening_id
    assert "result_data" in detail
    assert "intake_data" in detail

    # 6. Delete screening
    del_resp = client.delete(f"/api/results/{screening_id}", headers=headers)
    assert del_resp.status_code == 200

    hist_final = client.get("/api/results/history", headers=headers).json()
    assert len(hist_final) == initial_count
