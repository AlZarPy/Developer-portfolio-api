import json
import logging
from enum import StrEnum

import httpx

from app.core.config import Settings
from app.db.models import LeadCategory, LeadSentiment
from app.providers.base import AIAnalysis
from app.schemas.lead import ContactRequest

logger = logging.getLogger(__name__)


class GeminiProvider:
    def __init__(self, settings: Settings) -> None:
        if not settings.gemini_api_key:
            raise ValueError("Gemini API key is required for GeminiProvider.")

        self.api_key = settings.gemini_api_key
        self.model = settings.gemini_model
        self.timeout = settings.ai_timeout_seconds

    async def analyze(self, contact: ContactRequest) -> AIAnalysis:
        prompt = self._build_prompt(contact)
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"
        )
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.2, "responseMimeType": "application/json"},
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(url, params={"key": self.api_key}, json=payload)
            response.raise_for_status()

        return self._parse_response(response.json())

    @staticmethod
    def _build_prompt(contact: ContactRequest) -> str:
        categories = ", ".join(category.value for category in LeadCategory)
        sentiments = ", ".join(sentiment.value for sentiment in LeadSentiment)
        return (
            "You classify contact form submissions for a developer portfolio website. "
            "Return strict JSON with keys category, sentiment, reply. "
            f"Allowed category values: {categories}. "
            f"Allowed sentiment values: {sentiments}. "
            "The reply must be a short polite Russian email reply, no markdown.\n\n"
            f"Name: {contact.name}\n"
            f"Email: {contact.email}\n"
            f"Phone: {contact.phone or '-'}\n"
            f"Source: {contact.source.value}\n"
            f"Message: {contact.message}"
        )

    @staticmethod
    def _parse_response(payload: dict) -> AIAnalysis:
        text = GeminiProvider._extract_response_text(payload)
        try:
            data = json.loads(text)
        except json.JSONDecodeError as exc:
            raise ValueError("Gemini returned invalid JSON") from exc

        return AIAnalysis(
            category=GeminiProvider._parse_enum(
                LeadCategory,
                data.get("category"),
                LeadCategory.OTHER,
            ),
            sentiment=GeminiProvider._parse_enum(
                LeadSentiment,
                data.get("sentiment"),
                LeadSentiment.NEUTRAL,
            ),
            reply=str(data.get("reply") or "Спасибо за обращение."),
        )

    @staticmethod
    def _extract_response_text(payload: dict) -> str:
        candidates = payload.get("candidates")
        if not candidates:
            raise ValueError("Gemini response does not contain candidates")

        parts = candidates[0].get("content", {}).get("parts")
        if not parts or not parts[0].get("text"):
            raise ValueError("Gemini response does not contain text")

        return str(parts[0]["text"])

    @staticmethod
    def _parse_enum[T: StrEnum](enum_type: type[T], value: object, default: T) -> T:
        try:
            return enum_type(str(value))
        except ValueError:
            return default
