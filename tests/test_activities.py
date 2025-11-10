import os
import sys
from fastapi.testclient import TestClient

# Ensure repo root is on path (pytest runs with repo root as cwd, but be defensive)
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src import app as app_module

client = TestClient(app_module.app)


def test_get_activities():
    r = client.get("/activities")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, dict)
    # Verify a known activity exists
    assert "Chess Club" in data


def test_signup_success_and_duplicate():
    activity = "Chess Club"
    email = "teststudent@example.com"

    # Ensure clean state for this test
    if email in app_module.activities[activity]["participants"]:
        app_module.activities[activity]["participants"].remove(email)

    # Sign up (happy path)
    r = client.post(f"/activities/{activity}/signup?email={email}")
    assert r.status_code == 200
    json_body = r.json()
    assert "Signed up" in json_body.get("message", "")
    assert email in app_module.activities[activity]["participants"]

    # Duplicate signup should return 400
    r2 = client.post(f"/activities/{activity}/signup?email={email}")
    assert r2.status_code == 400
    assert r2.json().get("detail") == "Student already signed up"

    # Cleanup: remove the test email
    app_module.activities[activity]["participants"].remove(email)


def test_signup_activity_not_found():
    r = client.post("/activities/NoSuchActivity/signup?email=someone@example.com")
    assert r.status_code == 404
    assert r.json().get("detail") == "Activity not found"
