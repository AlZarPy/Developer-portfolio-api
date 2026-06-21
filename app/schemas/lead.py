import re

import phonenumbers
from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator

from app.db.models import LeadCategory, LeadSentiment, LeadSource


class ContactRequest(BaseModel):
    name: str = Field(min_length=2, max_length=120, examples=["Aleksandr Zaretsky"])
    email: EmailStr | None = Field(default=None, examples=["client@example.com"])
    phone: str | None = Field(default=None, max_length=40, examples=["+995 555 12 34 56"])
    message: str = Field(min_length=10, max_length=4000)
    source: LeadSource = LeadSource.WEBSITE

    @model_validator(mode="after")
    def validate_contact_method(self) -> "ContactRequest":
        if self.email is None and self.phone is None:
            raise ValueError("Email or phone is required.")
        return self

    @field_validator("name", "message", mode="after")
    @classmethod
    def normalize_required_text(cls, value: str) -> str:
        cleaned = " ".join(value.split())
        if not cleaned:
            raise ValueError("Value must not be blank.")
        return cleaned

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = str(value).strip()
        return cleaned or None

    @field_validator("phone", mode="after")
    @classmethod
    def normalize_phone(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = " ".join(value.split())
        if not cleaned:
            return None

        digits = re.sub(r"\D", "", cleaned)
        if cleaned.startswith("+"):
            candidate = cleaned
        elif len(digits) == 11 and digits.startswith("8"):
            candidate = f"+7{digits[1:]}"
        elif len(digits) >= 10:
            candidate = f"+{digits}"
        else:
            candidate = cleaned

        try:
            phone = phonenumbers.parse(candidate, "GE")
        except phonenumbers.NumberParseException as exc:
            raise ValueError("Enter a valid phone number.") from exc

        if not phonenumbers.is_valid_number(phone):
            raise ValueError("Enter a valid phone number.")

        return phonenumbers.format_number(phone, phonenumbers.PhoneNumberFormat.E164)


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
