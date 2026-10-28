from fastapi.testclient import TestClient

import pytest

from app.main import create_app


@pytest.fixture(autouse=True)
def test_credentials(monkeypatch):
    # These API tests exercise deterministic paths and never call OpenAI.
    monkeypatch.setenv("OPENAI_API_KEY", "test-placeholder-not-a-real-key")


def test_health_endpoint() -> None:
    with TestClient(create_app()) as client:
        response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_urgent_chat_is_safe_and_does_not_call_openai() -> None:
    with TestClient(create_app()) as client:
        response = client.post("/api/chat", json={"message": "I have chest pain after my workout."})
    assert response.status_code == 200
    body = response.json()
    assert body["urgent"] is True
    assert body["decision_basis"] == "urgent_medical_safety"


def test_production_origin_is_allowed(monkeypatch):
    monkeypatch.setenv("ALLOWED_ORIGINS", "https://stride-project.vercel.app")
    with TestClient(create_app()) as client:
        response = client.options("/api/chat", headers={
            "Origin": "https://stride-project.vercel.app",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        })
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "https://stride-project.vercel.app"
