from fastapi.testclient import TestClient


def test_contact_success(client: TestClient, contact_payload: dict[str, str | None]) -> None:
    response = client.post("/api/contact", json=contact_payload)

    assert response.status_code == 201
    body = response.json()
    assert body["success"] is True
    assert body["id"] >= 1
    assert body["category"] == "project_request"
    assert body["sentiment"] == "positive"
    assert body["category_label"] == "Project Request"


def test_contact_validation(client: TestClient, contact_payload: dict[str, str | None]) -> None:
    invalid_payload = {**contact_payload, "email": "not-an-email", "message": "short"}

    response = client.post("/api/contact", json=invalid_payload)

    assert response.status_code == 422
    assert response.json()["error"] == "validation_error"


def test_contact_rate_limit(client: TestClient, contact_payload: dict[str, str | None]) -> None:
    first = client.post("/api/contact", json=contact_payload)
    second = client.post("/api/contact", json={**contact_payload, "email": "second@example.com"})
    third = client.post("/api/contact", json={**contact_payload, "email": "third@example.com"})

    assert first.status_code == 201
    assert second.status_code == 201
    assert third.status_code == 429
    assert third.json()["error"] == "rate_limit_exceeded"
