from dataclasses import dataclass
from typing import Protocol

from app.db.models import LeadCategory, LeadSentiment
from app.schemas.lead import ContactRequest


@dataclass(frozen=True)
class AIAnalysis:
    category: LeadCategory
    sentiment: LeadSentiment
    reply: str


class AIProvider(Protocol):
    async def analyze(self, contact: ContactRequest) -> AIAnalysis:
        """Analyze a contact request and return normalized metadata."""
