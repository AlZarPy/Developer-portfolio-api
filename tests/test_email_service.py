import pytest

from app.core.config import Settings
from app.db.models import LeadCategory, LeadSentiment
from app.providers.base import AIAnalysis
from app.schemas.lead import ContactRequest
from app.services.email_service import EmailService


class CapturingEmailService(EmailService):
    def __init__(self, settings: Settings) -> None:
        super().__init__(settings)
        self.messages: list[dict[str, str]] = []

    async def _send(self, *, to: str, subject: str, text: str) -> bool:
        self.messages.append({"to": to, "subject": subject, "text": text})
        return True


@pytest.mark.asyncio
async def test_user_email_replaces_ai_placeholder_signature() -> None:
    service = CapturingEmailService(
        Settings(
            email_enabled=True,
            resend_api_key="test-key",
            owner_email="owner@example.com",
        )
    )
    contact = ContactRequest(
        name="Tatyana",
        email="tatyana@example.com",
        phone=None,
        message="Предлагаю обсудить backend проект.",
        source="website",
    )
    analysis = AIAnalysis(
        category=LeadCategory.PROJECT_REQUEST,
        sentiment=LeadSentiment.POSITIVE,
        reply=(
            "Здравствуйте, Татьяна!\n\n"
            "Спасибо за ваше предложение.\n\n"
            "С уважением,\n"
            "[Ваше Имя]"
        ),
    )

    sent = await service.send_contact_emails(contact, analysis)

    assert sent is True
    user_message = service.messages[1]
    assert "[Ваше Имя]" not in user_message["text"]
    assert user_message["text"].endswith("С уважением,\nАлександр Зарецкий")
    assert user_message["text"].count("С уважением") == 1
