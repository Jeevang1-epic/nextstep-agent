from __future__ import annotations

import json
import logging
import re
from typing import Any

from pydantic import ValidationError

from .config import get_settings
from .schemas import DocumentFacts


logger = logging.getLogger(__name__)

LAST_GEMINI_METADATA: dict[str, Any] = {
    "mode": "not_called",
    "used": False,
    "fallback_reason": None,
}


def get_last_gemini_metadata() -> dict[str, Any]:
    return dict(LAST_GEMINI_METADATA)


def _set_metadata(**values: Any) -> None:
    LAST_GEMINI_METADATA.clear()
    LAST_GEMINI_METADATA.update(values)


def _fallback(document_text: str, reason: str) -> DocumentFacts:
    from .agent import extraction_agent

    logger.info("Gemini extraction fallback: %s", reason)
    _set_metadata(mode="heuristic_fallback", used=False, fallback_reason=reason)
    return extraction_agent(document_text)


def _build_prompt(document_text: str, current_date: str) -> str:
    schema = json.dumps(DocumentFacts.model_json_schema(), indent=2)
    return (
        "Extract structured facts from the document for the NextStep Agent workflow.\n"
        "Return only valid JSON matching this Pydantic schema. Do not include markdown fences.\n"
        "Redact sensitive personal identifiers in extracted contact, identifier, sender, and recipient fields.\n"
        f"Current date: {current_date}\n\n"
        f"Schema:\n{schema}\n\n"
        f"Document:\n{document_text}"
    )


def _response_text(response: Any) -> str:
    parsed = getattr(response, "parsed", None)
    if parsed is not None:
        if isinstance(parsed, DocumentFacts):
            return parsed.model_dump_json()
        if isinstance(parsed, dict):
            return json.dumps(parsed)
    text = getattr(response, "text", None)
    if text:
        return text
    candidates = getattr(response, "candidates", None) or []
    for candidate in candidates:
        content = getattr(candidate, "content", None)
        parts = getattr(content, "parts", None) if content else None
        if parts:
            joined = "".join(getattr(part, "text", "") for part in parts)
            if joined:
                return joined
    return ""


def _strip_json(text: str) -> str:
    stripped = text.strip()
    fenced = re.search(r"```(?:json)?\s*(.*?)```", stripped, re.DOTALL | re.IGNORECASE)
    return fenced.group(1).strip() if fenced else stripped


def _validate_response(text: str) -> DocumentFacts:
    payload = json.loads(_strip_json(text))
    return DocumentFacts.model_validate(payload)


def extract_document_facts_with_gemini(document_text: str, current_date: str) -> DocumentFacts:
    settings = get_settings()
    if not settings.google_api_key:
        return _fallback(document_text, "GOOGLE_API_KEY is not configured")

    try:
        from google import genai
        from google.genai import types
    except Exception as exc:
        return _fallback(document_text, f"google-genai import failed: {exc}")

    prompt = _build_prompt(document_text, current_date)

    try:
        client = genai.Client(api_key=settings.google_api_key)
        try:
            config = types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=DocumentFacts,
                temperature=0,
            )
            response = client.models.generate_content(
                model=settings.gemini_model,
                contents=prompt,
                config=config,
            )
        except TypeError:
            config = types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0,
            )
            response = client.models.generate_content(
                model=settings.gemini_model,
                contents=prompt,
                config=config,
            )

        facts = _validate_response(_response_text(response))
        _set_metadata(
            mode="gemini",
            used=True,
            fallback_reason=None,
            model=settings.gemini_model,
        )
        return facts
    except (json.JSONDecodeError, ValidationError) as exc:
        return _fallback(document_text, f"Gemini returned malformed structured output: {exc}")
    except Exception as exc:
        return _fallback(document_text, f"Gemini request failed: {exc}")
