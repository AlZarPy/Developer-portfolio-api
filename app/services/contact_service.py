import logging

from app.db.models import LeadCategory
from app.repositories.lead_repository import LeadRepository
from app.schemas.lead import ContactRequest, PublicContactResponse
from app.services.ai_service import AIService
from app.services.email_service import EmailService

logger = logging.getLogger(__name__)


CATEGORY_LABELS: dict[LeadCategory, str] = {
    LeadCategory.JOB_OFFER: "Job Offer",
    LeadCategory.PROJECT_REQUEST: "Project Request",
    LeadCategory.PARTNERSHIP: "Partnership",
    LeadCategory.SUPPORT: "Support",
    LeadCategory.SPAM: "Spam",
    LeadCategory.OTHER: "Other",
}


class ContactService:
    def __init__(
        self,
        repository: LeadRepository,
        ai_service: AIService,
        email_service: EmailService,
    ) -> None:
        self.repository = repository
        self.ai_service = ai_service
        self.email_service = email_service

    async def process(self, contact: ContactRequest) -> PublicContactResponse:
        analysis = await self.ai_service.analyze(contact)
        email_sent = await self.email_service.send_contact_emails(contact, analysis)

        lead = await self.repository.create(
            name=contact.name,
            email=str(contact.email),
            phone=contact.phone,
            message=contact.message,
            source=contact.source,
            category=analysis.category,
            sentiment=analysis.sentiment,
            ai_reply=analysis.reply,
            email_sent=email_sent,
        )
        logger.info("Lead created: id=%s category=%s", lead.id, analysis.category.value)

        return PublicContactResponse(
            success=True,
            id=lead.id,
            category=analysis.category,
            sentiment=analysis.sentiment,
            category_label=CATEGORY_LABELS[analysis.category],
        )
