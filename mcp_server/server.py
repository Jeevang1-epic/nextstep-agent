from __future__ import annotations

import json
import re
import sys
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

from dateutil import parser

from nextstep_agent.redaction import find_sensitive_spans

try:
    from mcp.server.fastmcp import FastMCP
except Exception:
    FastMCP = None


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
TASK_STORE: list[dict[str, Any]] = []
WEEKDAYS = {
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "sunday": 6,
}
ABSOLUTE_DATE_PATTERN = re.compile(
    r"\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|"
    r"Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+\d{1,2}(?:,\s*\d{4})?\b"
    r"|\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b",
    re.IGNORECASE,
)

mcp = FastMCP("nextstep-local-resources") if FastMCP else None


def _load_json(filename: str) -> dict[str, Any]:
    path = DATA_DIR / filename
    return json.loads(path.read_text(encoding="utf-8"))


def _coerce_date(current_date: str | None) -> date:
    if not current_date:
        return date.today()
    return date.fromisoformat(current_date)


def _add_business_days(start: date, days: int) -> date:
    current = start
    remaining = days
    while remaining > 0:
        current += timedelta(days=1)
        if current.weekday() < 5:
            remaining -= 1
    return current


def _status_for_due_date(due_date: date, current: date) -> str:
    days_remaining = (due_date - current).days
    if days_remaining < 0:
        return "overdue"
    if days_remaining == 0:
        return "due_today"
    if days_remaining <= 7:
        return "due_soon"
    return "upcoming"


def deadline_calculator(date_text: str, current_date: str | None = None) -> dict[str, Any]:
    current = _coerce_date(current_date)
    normalized = date_text.strip()
    lower = normalized.lower()
    due_date: date | None = None
    confidence = "medium"
    notes: list[str] = []

    within_match = re.search(r"\b(?:within|in)\s+(\d+)\s+(business\s+)?days?\b", lower)
    next_match = re.search(
        r"\bnext\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b",
        lower,
    )

    if "tomorrow" in lower:
        due_date = current + timedelta(days=1)
        confidence = "high"
    elif "today" in lower:
        due_date = current
        confidence = "high"
    elif within_match:
        days = int(within_match.group(1))
        if within_match.group(2):
            due_date = _add_business_days(current, days)
            notes.append("Business-day calculation skips Saturdays and Sundays.")
        else:
            due_date = current + timedelta(days=days)
        confidence = "high"
    elif next_match:
        target_weekday = WEEKDAYS[next_match.group(1)]
        delta = (target_weekday - current.weekday()) % 7
        due_date = current + timedelta(days=delta or 7)
        confidence = "high"
    else:
        try:
            absolute_match = ABSOLUTE_DATE_PATTERN.search(normalized)
            parse_target = absolute_match.group(0) if absolute_match else normalized
            parsed = parser.parse(
                parse_target,
                fuzzy=True,
                dayfirst=False,
                default=datetime(current.year, current.month, current.day),
            )
            due_date = parsed.date()
            if not re.search(r"\b\d{4}\b", normalized) and due_date < current:
                due_date = due_date.replace(year=due_date.year + 1)
                notes.append("Year inferred because parsed date had already passed.")
        except (ValueError, OverflowError, parser.ParserError):
            notes.append("Could not parse a deadline from the supplied text.")

    if due_date is None:
        return {
            "source_text": date_text,
            "current_date": current.isoformat(),
            "due_date": None,
            "days_remaining": None,
            "status": "unknown",
            "confidence": "low",
            "notes": notes,
        }

    return {
        "source_text": date_text,
        "current_date": current.isoformat(),
        "due_date": due_date.isoformat(),
        "days_remaining": (due_date - current).days,
        "status": _status_for_due_date(due_date, current),
        "confidence": confidence,
        "notes": notes,
    }


def policy_lookup(query: str, category: str | None = None) -> dict[str, Any]:
    resource_pack = _load_json("resource_pack.json")
    query_terms = {term for term in re.findall(r"[a-z0-9]+", query.lower()) if len(term) > 2}
    matches: list[dict[str, Any]] = []

    for resource in resource_pack["resources"]:
        if category and resource["category"] != category:
            continue
        searchable = " ".join(
            [
                resource["category"],
                resource["title"],
                resource["guidance"],
                " ".join(resource.get("keywords", [])),
            ]
        ).lower()
        score = len(query_terms & set(re.findall(r"[a-z0-9]+", searchable)))
        if score or category:
            matches.append({**resource, "score": score})

    matches.sort(key=lambda item: item["score"], reverse=True)
    return {
        "query": query,
        "category": category,
        "matches": matches[:3],
    }


def template_fetch(intent: str) -> dict[str, Any]:
    templates = _load_json("templates.json")
    normalized = intent.strip().lower()

    for template in templates["templates"]:
        if template["intent"] == normalized or normalized in template.get("aliases", []):
            return template

    fallback = next(template for template in templates["templates"] if template["intent"] == "general_checklist")
    return fallback


def task_store(action_items: list[dict[str, Any]]) -> dict[str, Any]:
    stored: list[dict[str, Any]] = []
    for item in action_items:
        record = {
            "id": str(item.get("id", f"T{len(TASK_STORE) + len(stored) + 1}")),
            "title": str(item.get("title", "Untitled task")),
            "due_date": item.get("due_date"),
            "priority": item.get("priority"),
            "status": item.get("status", "open"),
        }
        stored.append(record)

    TASK_STORE.extend(stored)
    return {
        "stored_count": len(stored),
        "total_count": len(TASK_STORE),
        "tasks": stored,
    }


def safety_boundary_check(output: str) -> dict[str, Any]:
    lower = output.lower()
    warnings: list[str] = []
    if any(phrase in lower for phrase in ("guarantee", "legal advice", "medical advice")):
        warnings.append("Output may overstate certainty or cross professional advice boundaries.")
    if any(phrase in lower for phrase in ("payment has been made", "i already paid")):
        warnings.append("Output may claim an action the user has not confirmed.")

    findings = find_sensitive_spans(output)
    if findings:
        warnings.append("Output contains sensitive information and should be redacted.")

    return {
        "allowed": not warnings,
        "warnings": warnings,
        "sensitive_findings": [finding.model_dump() for finding in findings],
    }


if mcp is not None:
    mcp.tool()(policy_lookup)
    mcp.tool()(template_fetch)
    mcp.tool()(deadline_calculator)
    mcp.tool()(task_store)
    mcp.tool()(safety_boundary_check)


def main() -> None:
    if mcp is None:
        print("The mcp package is not installed. Run pip install -r requirements.txt.", file=sys.stderr)
        raise SystemExit(1)
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
