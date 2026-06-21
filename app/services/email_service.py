import logging

import httpx

from app.core.config import Settings
from app.providers.base import AIAnalysis
from app.schemas.lead import ContactRequest

logger = logging.getLogger(__name__)


class EmailService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def send_contact_emails(self, contact: ContactRequest, analysis: AIAnalysis) -> bool:
        if not self._is_configured:
            logger.info("Email sending skipped: Resend is not configured")
            return False

        owner_sent = await self._send(
            to=self.settings.owner_email or "",
            subject=f"New portfolio lead: {analysis.category.value}",
            text=(
                f"Name: {contact.name}\n"
                f"Email: {contact.email or '-'}\n"
                f"Phone: {contact.phone or '-'}\n"
                f"Source: {contact.source.value}\n"
                f"Category: {analysis.category.value}\n"
                f"Sentiment: {analysis.sentiment.value}\n\n"
                f"{contact.message}"
            ),
        )

        user_sent = True
        if contact.email:
            user_sent = await self._send(
                to=str(contact.email),
                subject="Спасибо за обращение",
                text=analysis.reply,
            )

        return owner_sent and user_sent

    async def _send(self, *, to: str, subject: str, text: str) -> bool:
        payload = {
            "from": self.settings.email_from,
            "to": [to],
            "subject": subject,
            "text": text,
        }
        headers = {"Authorization": f"Bearer {self.settings.resend_api_key}"}

        try:
            async with httpx.AsyncClient(timeout=self.settings.email_timeout_seconds) as client:
                response = await client.post(
                    "https://api.resend.com/emails",
                    headers=headers,
                    json=payload,
                )
                response.raise_for_status()
        except Exception:
            logger.exception("Email sending failed")
            return False

        return True

    @property
    def _is_configured(self) -> bool:
        return bool(
            self.settings.email_enabled
            and self.settings.resend_api_key
            and self.settings.owner_email
        )
