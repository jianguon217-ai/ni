from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_dry_run_job_does_not_call_provider():
    response = client.post("/v1/jobs", json={
        "prompt": "A presenter speaks naturally to camera",
        "aspect_ratio": "9:16",
        "dry_run": True,
    })
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "planned"
    assert "no credits were consumed" in body["message"]


def test_live_generation_is_blocked_until_adapter_is_verified():
    response = client.post("/v1/jobs", json={
        "prompt": "A presenter speaks naturally to camera",
        "dry_run": False,
    })
    assert response.status_code == 501


def test_job_lookup():
    created = client.post("/v1/jobs", json={"prompt": "test"}).json()
    fetched = client.get(f"/v1/jobs/{created['id']}")
    assert fetched.status_code == 200
    assert fetched.json()["id"] == created["id"]
