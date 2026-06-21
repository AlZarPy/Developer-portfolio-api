from app.db.models import LeadCategory, LeadSentiment
from app.providers.base import AIAnalysis
from app.schemas.lead import ContactRequest


class MockProvider:
    async def analyze(self, contact: ContactRequest) -> AIAnalysis:
        text = f"{contact.name} {contact.message}".lower()

        if any(word in text for word in ("работ", "job", "vacancy", "hiring", "offer")):
            category = LeadCategory.JOB_OFFER
        elif any(word in text for word in ("проект", "project", "сайт", "api", "backend")):
            category = LeadCategory.PROJECT_REQUEST
        elif any(word in text for word in ("partner", "партнер", "collaboration")):
            category = LeadCategory.PARTNERSHIP
        elif any(word in text for word in ("help", "support", "ошибка", "problem")):
            category = LeadCategory.SUPPORT
        elif any(word in text for word in ("casino", "crypto", "viagra", "spam")):
            category = LeadCategory.SPAM
        else:
            category = LeadCategory.OTHER

        sentiment = LeadSentiment.POSITIVE
        if any(word in text for word in ("bad", "angry", "ужас", "плохо", "проблем")):
            sentiment = LeadSentiment.NEGATIVE
        elif category in {LeadCategory.SPAM, LeadCategory.OTHER}:
            sentiment = LeadSentiment.NEUTRAL

        return AIAnalysis(
            category=category,
            sentiment=sentiment,
            reply=(
                "Спасибо за обращение. Я получил сообщение и вернусь с ответом после "
                "изучения деталей."
            ),
        )
