import asyncio

from fastapi.testclient import TestClient
from sqlalchemy import select

from app.api.dependencies import get_email_service
from app.db.database import SessionLocal
from app.db.models import Lead
from app.providers.base import AIAnalysis
from app.schemas.lead import ContactRequest


class FailedEmailService:
    async def send_contact_emails(self, contact: ContactRequest, analysis: AIAnalysis) -> bool:
        return False


async def get_lead_email_sent(lead_id: int) -> bool:
    async with SessionLocal() as session:
        result = await session.execute(select(Lead.email_sent).where(Lead.id == lead_id))
        return result.scalar_one()


def test_contact_success(client: TestClient, contact_payload: dict[str, str | None]) -> None:
    response = client.post("/api/contact", json=contact_payload)

    assert response.status_code == 201
    body = response.json()
    assert body["success"] is True
    assert body["id"] >= 1
    assert body["category"] == "project_request"
    assert body["sentiment"] == "positive"
    assert body["category_label"] == "Project Request"


def test_contact_keeps_lead_when_email_sending_fails(
    client: TestClient,
    contact_payload: dict[str, str | None],
) -> None:
    client.app.dependency_overrides[get_email_service] = FailedEmailService

    try:
        response = client.post("/api/contact", json=contact_payload)
    finally:
        client.app.dependency_overrides.pop(get_email_service, None)

    assert response.status_code == 201
    lead_id = response.json()["id"]
    assert asyncio.run(get_lead_email_sent(lead_id)) is False


def test_contact_validation(client: TestClient, contact_payload: dict[str, str | None]) -> None:
    invalid_payload = {**contact_payload, "email": "not-an-email", "message": "short"}

    response = client.post("/api/contact", json=invalid_payload)

    assert response.status_code == 422
    assert response.json()["error"] == "validation_error"


def test_contact_accepts_phone_without_email(
    client: TestClient,
    contact_payload: dict[str, str | None],
) -> None:
    payload = {**contact_payload, "email": None, "phone": "+995 555 44 55 66"}

    response = client.post("/api/contact", json=payload)

    assert response.status_code == 201
    assert response.json()["success"] is True


def test_contact_accepts_russian_phone_starting_with_8(
    client: TestClient,
    contact_payload: dict[str, str | None],
) -> None:
    payload = {**contact_payload, "email": None, "phone": "8 999 123 45 67"}

    response = client.post("/api/contact", json=payload)

    assert response.status_code == 201
    assert response.json()["success"] is True


def test_contact_rejects_invalid_phone(
    client: TestClient,
    contact_payload: dict[str, str | None],
) -> None:
    payload = {**contact_payload, "email": None, "phone": "123"}

    response = client.post("/api/contact", json=payload)

    assert response.status_code == 422
    assert response.json()["error"] == "validation_error"


def test_contact_requires_email_or_phone(
    client: TestClient,
    contact_payload: dict[str, str | None],
) -> None:
    payload = {**contact_payload, "email": None, "phone": None}

    response = client.post("/api/contact", json=payload)

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
