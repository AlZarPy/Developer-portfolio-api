from fastapi.testclient import TestClient


def test_metrics(client: TestClient, contact_payload: dict[str, str | None]) -> None:
    client.post("/api/contact", json=contact_payload)

    response = client.get("/api/metrics")

    assert response.status_code == 200
    body = response.json()
    assert body["total"] >= 1
    assert body["by_category"]["project_request"] >= 1
    assert body["by_source"]["website"] >= 1
