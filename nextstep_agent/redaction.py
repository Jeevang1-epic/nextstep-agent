from __future__ import annotations

import re
from typing import Any

from pydantic import BaseModel, ConfigDict


class RedactionFinding(BaseModel):
    model_config = ConfigDict(extra="forbid")

    label: str
    value: str
    start: int
    end: int


class RedactionResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    text: str
    findings: list[RedactionFinding]


PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    (
        "SSN",
        re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    ),
    (
        "EMAIL",
        re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE),
    ),
    (
        "PHONE",
        re.compile(r"(?<!\w)(?:\+?\d{1,3}[\s.-]?)?(?:\(?\d{3}\)?[\s.-]?)\d{3}[\s.-]?\d{4}(?!\w)"),
    ),
    (
        "ID_12_DIGIT",
        re.compile(r"\b\d{4}[ -]?\d{4}[ -]?\d{4}\b"),
    ),
    (
        "LONG_NUMBER",
        re.compile(r"\b(?:\d[ -]?){11,18}\d?\b"),
    ),
    (
        "IDENTIFIER",
        re.compile(
            r"\b(?:account|acct|customer|client|student|patient|invoice|meter|policy)\s*"
            r"(?:number|no\.?|id|#)\s*[:#-]?\s*[A-Z0-9][A-Z0-9-]{2,}(?:[ \t]?[A-Z0-9-]{2,}){0,3}\b",
            re.IGNORECASE,
        ),
    ),
    (
        "ADDRESS",
        re.compile(
            r"\b\d{1,5}\s+[A-Za-z0-9 .'-]+"
            r"(?:Street|St\.|Road|Rd\.|Avenue|Ave\.|Lane|Ln\.|Drive|Dr\.|Boulevard|Blvd\.|Court|Ct\.|Circle|Cir\.)"
            r"(?:\s+(?:Apt|Unit|Suite|Ste)\.?\s*[A-Za-z0-9-]+)?\b",
            re.IGNORECASE,
        ),
    ),
    (
        "NAME",
        re.compile(
            r"\b(?:student|customer|patient|parent|guardian|client|name)\s*:\s*"
            r"[A-Z][A-Za-z.'-]+(?:[ \t]+[A-Z][A-Za-z.'-]+){0,3}",
            re.IGNORECASE,
        ),
    ),
)


def find_sensitive_spans(text: str) -> list[RedactionFinding]:
    matches: list[RedactionFinding] = []
    for label, pattern in PATTERNS:
        for match in pattern.finditer(text):
            matches.append(
                RedactionFinding(
                    label=label,
                    value=match.group(0),
                    start=match.start(),
                    end=match.end(),
                )
            )

    matches.sort(key=lambda item: (item.start, -(item.end - item.start)))
    selected: list[RedactionFinding] = []
    occupied_end = -1
    for match in matches:
        if match.start >= occupied_end:
            selected.append(match)
            occupied_end = match.end
    return selected


def redact_text(text: str) -> RedactionResult:
    findings = find_sensitive_spans(text)
    if not findings:
        return RedactionResult(text=text, findings=[])

    chunks: list[str] = []
    cursor = 0
    for finding in findings:
        chunks.append(text[cursor : finding.start])
        chunks.append(f"[REDACTED_{finding.label}]")
        cursor = finding.end
    chunks.append(text[cursor:])
    return RedactionResult(text="".join(chunks), findings=findings)


def redact_value(value: Any) -> Any:
    if isinstance(value, str):
        return redact_text(value).text
    if isinstance(value, list):
        return [redact_value(item) for item in value]
    if isinstance(value, tuple):
        return tuple(redact_value(item) for item in value)
    if isinstance(value, dict):
        return {key: redact_value(item) for key, item in value.items()}
    return value
