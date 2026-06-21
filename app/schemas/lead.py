from pydantic import BaseModel, EmailStr, Field, field_validator

from app.db.models import LeadCategory, LeadSentiment, LeadSource


class ContactRequest(BaseModel):
    name: str = Field(min_length=2, max_length=120, examples=["Aleksandr Zaretsky"])
    email: EmailStr = Field(examples=["client@example.com"])
    phone: str | None = Field(default=None, max_length=40, examples=["+995 555 12 34 56"])
    message: str = Field(min_length=10, max_length=4000)
    source: LeadSource = LeadSource.WEBSITE

    @field_validator("name", "message", mode="after")
    @classmethod
    def normalize_required_text(cls, value: str) -> str:
        cleaned = " ".join(value.split())
        if not cleaned:
            raise ValueError("Value must not be blank.")
        return cleaned

    @field_validator("phone", mode="after")
    @classmethod
    def normalize_phone(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = " ".join(value.split())
        return cleaned or None


class ContactResponse(BaseModel):
    success: bool
    id: int
    category: LeadCategory
    sentiment: LeadSentiment


class PublicContactResponse(BaseModel):
    success: bool
    id: int
    category: LeadCategory
    sentiment: LeadSentiment
    category_label: str


class MetricsResponse(BaseModel):
    total: int
    by_category: dict[str, int]
    by_source: dict[str, int]
