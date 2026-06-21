import pytest

from app.db.models import LeadCategory, LeadSentiment
from app.providers.gemini_provider import GeminiProvider


def build_gemini_payload(text: str) -> dict:
    return {"candidates": [{"content": {"parts": [{"text": text}]}}]}


def test_gemini_parse_response_uses_defaults_for_unknown_enums() -> None:
    analysis = GeminiProvider._parse_response(
        build_gemini_payload(
            '{"category": "unexpected", "sentiment": "unknown", "reply": "Спасибо"}'
        )
    )

    assert analysis.category == LeadCategory.OTHER
    assert analysis.sentiment == LeadSentiment.NEUTRAL
    assert analysis.reply == "Спасибо"


def test_gemini_parse_response_rejects_invalid_json() -> None:
    with pytest.raises(ValueError, match="invalid JSON"):
        GeminiProvider._parse_response(build_gemini_payload("not json"))


def test_gemini_parse_response_rejects_missing_text() -> None:
    with pytest.raises(ValueError, match="does not contain candidates"):
        GeminiProvider._parse_response({"candidates": []})
