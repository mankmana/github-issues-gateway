import hashlib
import hmac
import json

from fastapi.testclient import TestClient

import main
from config import settings
from main import app


client = TestClient(app)


def create_signed_headers(payload, event_name, delivery_id):
    raw_body = json.dumps(
        payload,
        separators=(",", ":"),
    ).encode()

    signature = hmac.new(
        settings.webhook_secret.encode(),
        raw_body,
        hashlib.sha256,
    ).hexdigest()

    headers = {
        "Content-Type": "application/json",
        "X-GitHub-Event": event_name,
        "X-GitHub-Delivery": delivery_id,
        "X-Hub-Signature-256": f"sha256={signature}",
    }

    return raw_body, headers


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


def test_webhook_rejects_invalid_signature():
    response = client.post(
        "/webhooks/github",
        content=b'{"action":"opened"}',
        headers={
            "Content-Type": "application/json",
            "X-GitHub-Event": "issues",
            "X-GitHub-Delivery": "invalid-test-001",
            "X-Hub-Signature-256": "sha256=invalid",
        },
    )

    assert response.status_code == 401


def test_webhook_accepts_issue_comment(monkeypatch):
    saved_events = []

    monkeypatch.setattr(
        main,
        "save_event",
        lambda **kwargs: saved_events.append(kwargs),
    )

    payload = {
        "action": "created",
        "issue": {"number": 1},
        "comment": {"body": "Test comment"},
    }

    raw_body, headers = create_signed_headers(
        payload,
        "issue_comment",
        "comment-test-001",
    )

    response = client.post(
        "/webhooks/github",
        content=raw_body,
        headers=headers,
    )

    assert response.status_code == 204
    assert saved_events[0]["event_name"] == "issue_comment"
    assert saved_events[0]["delivery_id"] == "comment-test-001"


def test_webhook_rejects_unknown_event():
    payload = {"action": "opened"}

    raw_body, headers = create_signed_headers(
        payload,
        "unknown_event",
        "unknown-test-001",
    )

    response = client.post(
        "/webhooks/github",
        content=raw_body,
        headers=headers,
    )

    assert response.status_code == 400


def test_issue_list_rejects_invalid_state():
    response = client.get("/issues?state=invalid")

    assert response.status_code == 400


def test_issue_list_rejects_invalid_page_size():
    response = client.get("/issues?per_page=101")

    assert response.status_code == 400
