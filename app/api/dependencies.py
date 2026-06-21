from collections.abc import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.db.database import get_session
from app.repositories.lead_repository import LeadRepository
from app.services.ai_service import AIService
from app.services.contact_service import ContactService
from app.services.email_service import EmailService
from app.services.metrics_service import MetricsService


def get_app_settings() -> Settings:
    return get_settings()


async def get_lead_repository(
    session: AsyncSession = Depends(get_session),
) -> AsyncGenerator[LeadRepository, None]:
    yield LeadRepository(session)


def get_ai_service(settings: Settings = Depends(get_app_settings)) -> AIService:
    return AIService(settings)


def get_email_service(settings: Settings = Depends(get_app_settings)) -> EmailService:
    return EmailService(settings)


async def get_contact_service(
    repository: LeadRepository = Depends(get_lead_repository),
    ai_service: AIService = Depends(get_ai_service),
    email_service: EmailService = Depends(get_email_service),
) -> AsyncGenerator[ContactService, None]:
    yield ContactService(repository, ai_service, email_service)


async def get_metrics_service(
    repository: LeadRepository = Depends(get_lead_repository),
) -> AsyncGenerator[MetricsService, None]:
    yield MetricsService(repository)
