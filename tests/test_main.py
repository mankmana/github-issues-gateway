from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


def test_health_check():
    response = client.get("/healthz")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_webhook_requires_signature():
    response = client.post(
        "/webhooks/github",
        json={"action": "opened"},
    )

    assert response.status_code == 401
