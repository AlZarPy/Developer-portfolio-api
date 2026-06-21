from datetime import datetime
from enum import StrEnum

from sqlalchemy import Boolean, DateTime, Enum, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class LeadSource(StrEnum):
    WEBSITE = "website"
    GITHUB = "github"
    CV = "cv"
    TELEGRAM = "telegram"
    KWORK = "kwork"
    OTHER = "other"


class LeadCategory(StrEnum):
    JOB_OFFER = "job_offer"
    PROJECT_REQUEST = "project_request"
    PARTNERSHIP = "partnership"
    SUPPORT = "support"
    SPAM = "spam"
    OTHER = "other"


class LeadSentiment(StrEnum):
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"


class Lead(Base):
    __tablename__ = "leads"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(254), nullable=False, index=True)
    phone: Mapped[str | None] = mapped_column(String(40), nullable=True)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    source: Mapped[LeadSource] = mapped_column(Enum(LeadSource), nullable=False)
    category: Mapped[LeadCategory] = mapped_column(Enum(LeadCategory), nullable=False)
    sentiment: Mapped[LeadSentiment] = mapped_column(Enum(LeadSentiment), nullable=False)
    ai_reply: Mapped[str] = mapped_column(Text, nullable=False)
    email_sent: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
