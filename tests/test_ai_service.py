import pytest

from app.core.config import Settings
from app.db.models import LeadCategory, LeadSentiment
from app.schemas.lead import ContactRequest
from app.services.ai_service import AIService


class BrokenProvider:
    async def analyze(self, contact: ContactRequest):
        raise RuntimeError("provider unavailable")


@pytest.mark.asyncio
async def test_ai_service_uses_mock_fallback_when_provider_fails() -> None:
    service = AIService(Settings(), provider=BrokenProvider())
    contact = ContactRequest(
        name="Maria Client",
        email="maria@example.com",
        phone=None,
        message="Need a FastAPI backend for a project.",
        source="website",
    )

    analysis = await service.analyze(contact)

    assert analysis.category == LeadCategory.PROJECT_REQUEST
    assert analysis.sentiment == LeadSentiment.POSITIVE
    assert analysis.reply
