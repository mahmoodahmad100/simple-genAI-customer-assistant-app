from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health() -> None:
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_chat_returns_contract() -> None:
    response = client.post(
        "/api/v1/chat",
        json={"user_id": "usr_123", "message": "Is water damage covered?"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["response"] == "Received message from usr_123."
    assert body["sources"] == []
    assert body["tool_calls"] == []


def test_chat_rejects_blank_message() -> None:
    response = client.post(
        "/api/v1/chat",
        json={"user_id": "usr_123", "message": "   "},
    )

    assert response.status_code == 422
