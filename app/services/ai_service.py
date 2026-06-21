import logging

from app.core.config import Settings
from app.providers.base import AIAnalysis, AIProvider
from app.providers.gemini_provider import GeminiProvider
from app.providers.mock_provider import MockProvider
from app.schemas.lead import ContactRequest

logger = logging.getLogger(__name__)


class AIService:
    def __init__(self, settings: Settings, provider: AIProvider | None = None) -> None:
        self.settings = settings
        self.provider = provider or self._build_provider(settings)
        self.fallback_provider = MockProvider()

    async def analyze(self, contact: ContactRequest) -> AIAnalysis:
        try:
            return await self.provider.analyze(contact)
        except Exception:
            logger.exception("AI provider failed; using mock fallback")
            return await self.fallback_provider.analyze(contact)

    @staticmethod
    def _build_provider(settings: Settings) -> AIProvider:
        if settings.ai_provider.lower() == "gemini" and settings.gemini_api_key:
            return GeminiProvider(settings)
        return MockProvider()
