from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from datetime import date
from typing import Any

from mcp_server.server import (
    deadline_calculator,
    policy_lookup,
    safety_boundary_check,
    task_store,
    template_fetch,
)

from .prompts import AGENT_PROMPTS, ROOT_AGENT_INSTRUCTION
from .redaction import find_sensitive_spans, redact_text, redact_value
from .document_loader import load_document_input
from .gemini_client import extract_document_facts_with_gemini, get_last_gemini_metadata
from .schemas import (
    ActionItem,
    ActionPlan,
    DocumentFacts,
    DraftOutput,
    FinalResponse,
    RiskAssessment,
)
from .verifier import verify_plan_against_source

try:
    from google.adk.agents import LlmAgent as GoogleAdkAgent
except Exception:
    try:
        from google.adk import Agent as GoogleAdkAgent
    except Exception:
        GoogleAdkAgent = None


MONTH_PATTERN = (
    r"Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|"
    r"Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?"
)
DATE_PATTERN = re.compile(
    rf"\b(?:{MONTH_PATTERN})\s+\d{{1,2}}(?:,\s*\d{{4}})?\b"
    r"|\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b"
    r"|\b(?:today|tomorrow|next\s+(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday))\b"
    r"|\b(?:within|in)\s+\d+\s+(?:business\s+)?days?\b",
    re.IGNORECASE,
)
AMOUNT_PATTERN = re.compile(r"(?:USD|INR|Rs\.?|\$)\s?\d{1,3}(?:,\d{3})*(?:\.\d{2})?|\b\d+\s?(?:dollars|rupees)\b", re.IGNORECASE)
CONTACT_PATTERN = re.compile(
    r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b|(?<!\w)(?:\+?1[\s.-]?)?(?:\(?\d{3}\)?[\s.-]?)\d{3}[\s.-]?\d{4}(?!\w)",
    re.IGNORECASE,
)
IDENTIFIER_PATTERN = re.compile(
    r"\b(?:account|acct|customer|client|student|patient|invoice|meter|policy)\s*"
    r"(?:number|no\.?|id|#)\s*[:#-]?\s*[A-Z0-9][A-Z0-9-]{2,}(?:[ \t]?[A-Z0-9-]{2,}){0,3}\b",
    re.IGNORECASE,
)
ACTION_KEYWORDS = (
    "must",
    "please",
    "due",
    "submit",
    "pay",
    "return",
    "bring",
    "call",
    "email",
    "attend",
    "schedule",
    "complete",
    "sign",
    "rsvp",
    "disconnect",
)


@dataclass(frozen=True)
class LocalAgentDefinition:
    name: str
    instruction: str


def build_agent_registry() -> list[LocalAgentDefinition]:
    return [LocalAgentDefinition(name=name, instruction=instruction) for name, instruction in AGENT_PROMPTS.items()]


def build_adk_agents(model: str = "gemini-flash-latest") -> list[Any]:
    if GoogleAdkAgent is None:
        return build_agent_registry()

    return [
        GoogleAdkAgent(
            name=re.sub(r"[^a-z0-9_]+", "_", name.lower()).strip("_"),
            model=model,
            instruction=instruction,
        )
        for name, instruction in AGENT_PROMPTS.items()
    ]


def build_root_agent(model: str = "gemini-flash-latest") -> Any:
    if GoogleAdkAgent is None:
        return LocalAgentDefinition(name="NextStep Coordinator", instruction=ROOT_AGENT_INSTRUCTION)
    return GoogleAdkAgent(name="nextstep_coordinator", model=model, instruction=ROOT_AGENT_INSTRUCTION)


root_agent = build_root_agent()


def _clean_lines(document_text: str) -> list[str]:
    return [line.strip() for line in document_text.replace("\r\n", "\n").split("\n") if line.strip()]


def _detect_document_type(text: str) -> str:
    lower = text.lower()
    if any(term in lower for term in ("school", "student", "permission slip", "field trip")):
        return "school_notice"
    if any(term in lower for term in ("utility", "electric", "water bill", "disconnect", "service interruption")):
        return "utility_bill"
    if "invoice" in lower or "amount due" in lower:
        return "invoice"
    if any(term in lower for term in ("appointment", "clinic", "doctor", "visit")):
        return "appointment_slip"
    if any(term in lower for term in ("intake", "case worker", "ngo", "nonprofit")):
        return "ngo_intake"
    return "general_notice"


def _extract_sender(lines: list[str]) -> str | None:
    for line in lines[:8]:
        match = re.search(r"\bfrom\s*:\s*(.+)$", line, re.IGNORECASE)
        if match:
            return redact_text(match.group(1)).text
    return redact_text(lines[0]).text if lines else None


def _extract_recipient(lines: list[str]) -> str | None:
    for line in lines[:12]:
        match = re.search(r"\b(?:to|student|customer|client|patient|guardian)\s*:\s*(.+)$", line, re.IGNORECASE)
        if match:
            return redact_text(line).text
    return None


def _extract_deadlines(lines: list[str]) -> list[str]:
    deadline_lines: list[str] = []
    for line in lines:
        lower = line.lower()
        if any(term in lower for term in ("due", "deadline", "by ", "before", "within", "disconnect", "appointment")):
            if DATE_PATTERN.search(line):
                deadline_lines.append(redact_text(line).text)
    return deadline_lines


def _extract_actions(lines: list[str]) -> list[str]:
    actions: list[str] = []
    for line in lines:
        lower = line.lower()
        if any(keyword in lower for keyword in ACTION_KEYWORDS):
            actions.append(redact_text(line).text)
    return actions[:8]


def intake_agent(document_text: str) -> str:
    normalized = document_text.replace("\r\n", "\n").strip()
    if not normalized:
        raise ValueError("Document text is empty.")
    return normalized


def extraction_agent(document_text: str) -> DocumentFacts:
    lines = _clean_lines(document_text)
    dates = [match.group(0) for match in DATE_PATTERN.finditer(document_text)]
    amounts = [match.group(0) for match in AMOUNT_PATTERN.finditer(document_text)]
    identifier_matches = list(IDENTIFIER_PATTERN.finditer(document_text))
    identifiers = [redact_text(match.group(0)).text for match in identifier_matches]
    contacts = [
        redact_text(match.group(0)).text
        for match in CONTACT_PATTERN.finditer(document_text)
        if not any(match.start() >= identifier.start() and match.end() <= identifier.end() for identifier in identifier_matches)
    ]
    sensitive_fields = sorted({finding.label for finding in find_sensitive_spans(document_text)})

    return DocumentFacts(
        document_type=_detect_document_type(document_text),
        source_name=redact_text(lines[0]).text if lines else None,
        sender=_extract_sender(lines),
        recipient=_extract_recipient(lines),
        dates=dates,
        deadlines=_extract_deadlines(lines),
        amounts=amounts,
        identifiers=identifiers,
        required_actions=_extract_actions(lines),
        contact_methods=contacts,
        sensitive_fields=sensitive_fields,
    )


def risk_priority_agent(facts: DocumentFacts, current_date: str) -> tuple[RiskAssessment, list[dict[str, Any]], list[str]]:
    flags: list[str] = []
    mcp_trace: list[str] = []
    deadline_results: list[dict[str, Any]] = []

    for deadline_text in facts.deadlines or facts.dates:
        result = deadline_calculator(deadline_text, current_date)
        deadline_results.append(result)
        mcp_trace.append(f"deadline_calculator:{result.get('due_date') or 'unknown'}")
        days_remaining = result.get("days_remaining")
        if isinstance(days_remaining, int):
            if days_remaining < 0:
                flags.append("deadline_overdue")
            elif days_remaining <= 7:
                flags.append("deadline_within_7_days")

    combined = " ".join([facts.document_type, *facts.required_actions, *facts.deadlines]).lower()
    if any(term in combined for term in ("disconnect", "shut off", "service interruption", "collection", "late fee")):
        flags.append("service_or_financial_consequence")
    if facts.document_type == "school_notice":
        flags.append("minor_or_school_context")
    if facts.amounts:
        flags.append("payment_or_amount_detected")

    unique_flags = sorted(set(flags))
    if "deadline_overdue" in unique_flags or "service_or_financial_consequence" in unique_flags:
        level = "high"
    elif "deadline_within_7_days" in unique_flags or "payment_or_amount_detected" in unique_flags:
        level = "medium"
    else:
        level = "low"

    explanation = "Risk is based on deadline timing, consequences, document type, and payment signals."
    return (
        RiskAssessment(
            level=level,
            flags=unique_flags,
            explanation=explanation,
            requires_human_review=level == "high",
        ),
        deadline_results,
        mcp_trace,
    )


def _intent_for_document_type(document_type: str) -> str:
    return {
        "school_notice": "school_response",
        "invoice": "invoice_payment_check",
        "utility_bill": "utility_bill_response",
        "appointment_slip": "appointment_confirmation",
        "ngo_intake": "intake_followup",
    }.get(document_type, "general_checklist")


def resource_lookup_agent(facts: DocumentFacts) -> tuple[dict[str, Any], dict[str, Any], list[str]]:
    category = {
        "school_notice": "school",
        "invoice": "billing",
        "utility_bill": "utility",
        "appointment_slip": "appointment",
        "ngo_intake": "intake",
    }.get(facts.document_type, "general")
    query = " ".join([facts.document_type, *facts.required_actions, *facts.deadlines])
    policy = policy_lookup(query=query, category=category)
    template = template_fetch(_intent_for_document_type(facts.document_type))
    return policy, template, [f"policy_lookup:{category}", f"template_fetch:{template['intent']}"]


def _best_due_date(deadline_results: list[dict[str, Any]]) -> date | None:
    due_dates: list[date] = []
    for result in deadline_results:
        due_date = result.get("due_date")
        if due_date:
            due_dates.append(date.fromisoformat(due_date))
    return min(due_dates) if due_dates else None


def _priority_for_due_date(due_date: date | None, risk: RiskAssessment, current_date: str) -> int:
    if risk.level == "high":
        return 1
    if due_date is None:
        return 3
    days_remaining = (due_date - date.fromisoformat(current_date)).days
    if days_remaining <= 3:
        return 1
    if days_remaining <= 7:
        return 2
    return 3


def _action_title(action: str) -> str:
    cleaned = re.sub(r"\s+", " ", action).strip(" .")
    cleaned = re.sub(r"^(please|you must|must)\s+", "", cleaned, flags=re.IGNORECASE)
    return cleaned[:96] or "Review document"


def action_planner_agent(
    facts: DocumentFacts,
    risk: RiskAssessment,
    policy: dict[str, Any],
    deadline_results: list[dict[str, Any]],
    current_date: str,
) -> ActionPlan:
    due_date = _best_due_date(deadline_results)
    action_sources = facts.required_actions or facts.deadlines or ["Review the document and confirm the next required step."]
    resources = [match["title"] for match in policy.get("matches", [])]

    action_items = [
        ActionItem(
            id=f"A{index}",
            title=_action_title(action),
            details=action,
            due_date=due_date,
            priority=_priority_for_due_date(due_date, risk, current_date),
            source_evidence=action,
        )
        for index, action in enumerate(action_sources[:5], start=1)
    ]

    return ActionPlan(
        summary=f"{facts.document_type.replace('_', ' ').title()} requires {len(action_items)} next step(s).",
        action_items=action_items,
        resources=resources,
        risk_assessment=risk,
    )


def drafting_agent(facts: DocumentFacts, plan: ActionPlan, template: dict[str, Any], current_date: str) -> DraftOutput:
    checklist = [
        f"{item.title}" + (f" by {item.due_date.isoformat()}" if item.due_date else "")
        for item in plan.action_items
    ]
    actions_text = "\n".join(f"- {item.title}" for item in plan.action_items)
    due_date = plan.action_items[0].due_date.isoformat() if plan.action_items and plan.action_items[0].due_date else "the listed deadline"

    body = template["body_template"].format(
        sender=facts.sender or "the sender",
        recipient=facts.recipient or "the recipient",
        due_date=due_date,
        actions=actions_text,
        current_date=current_date,
    )
    body = redact_text(body).text

    return DraftOutput(
        intent=template["intent"],
        subject=template["subject"],
        body=body,
        checklist=checklist,
        assumptions=[
            "The draft is based only on the provided document text.",
            "No payment, submission, or appointment change is performed by this tool.",
        ],
        redacted=True,
    )


def redaction_agent(facts: DocumentFacts, plan: ActionPlan, draft: DraftOutput, verification_passed: bool) -> str:
    lines = [
        "NextStep summary",
        f"Document type: {facts.document_type}",
        f"Risk: {plan.risk_assessment.level}",
        f"Verification passed: {verification_passed}",
        "",
        "Prioritized actions:",
    ]
    for item in plan.action_items:
        due = f" due {item.due_date.isoformat()}" if item.due_date else ""
        lines.append(f"- P{item.priority}: {item.title}{due}")
    lines.extend(["", "Draft:", draft.body])
    return redact_text("\n".join(lines)).text


def _sanitize_model(model: Any, schema: type[Any]) -> Any:
    return schema.model_validate(redact_value(model.model_dump(mode="json")))


def _trace(stage: str, detail: str) -> dict[str, str]:
    return {"stage": stage, "detail": detail}


def _mcp_call(tool: str, why: str, result: Any) -> dict[str, Any]:
    return {"tool": tool, "why": why, "result": result}


def run_pipeline(document_text: str, current_date: str | None = None, use_gemini: bool = False) -> FinalResponse:
    run_date = current_date or date.today().isoformat()
    trace_events: list[dict[str, str]] = []
    mcp_calls: list[dict[str, Any]] = []

    source_text = intake_agent(document_text)
    trace_events.append(_trace("Intake Agent", "Normalized document text and confirmed non-empty input."))

    if use_gemini:
        facts = extract_document_facts_with_gemini(source_text, run_date)
        extraction_metadata = get_last_gemini_metadata()
    else:
        facts = extraction_agent(source_text)
        extraction_metadata = {"mode": "heuristic", "used": False, "fallback_reason": None}
    trace_events.append(
        _trace(
            "Extraction Agent",
            f"Extracted facts using {extraction_metadata.get('mode', 'unknown')} mode.",
        )
    )

    risk, deadline_results, risk_trace = risk_priority_agent(facts, run_date)
    for deadline_text, result in zip(facts.deadlines or facts.dates, deadline_results):
        mcp_calls.append(
            _mcp_call(
                "deadline_calculator",
                "Normalize deadline text and compute urgency against the current date.",
                {"input": deadline_text, **result},
            )
        )
    trace_events.append(_trace("Risk & Priority Agent", f"Assigned {risk.level} risk with flags: {', '.join(risk.flags) or 'none'}."))

    policy, template, lookup_trace = resource_lookup_agent(facts)
    mcp_calls.append(
        _mcp_call(
            "policy_lookup",
            "Find local guidance relevant to the document category and extracted actions.",
            {"matches": [match["title"] for match in policy.get("matches", [])]},
        )
    )
    mcp_calls.append(
        _mcp_call(
            "template_fetch",
            "Fetch a safe response template for the detected user intent.",
            {"intent": template["intent"], "subject": template["subject"]},
        )
    )
    trace_events.append(_trace("Resource Lookup Agent", "Called MCP policy and template tools for grounded local context."))

    plan = action_planner_agent(facts, risk, policy, deadline_results, run_date)
    trace_events.append(_trace("Action Planner Agent", f"Created {len(plan.action_items)} prioritized action item(s)."))

    draft = drafting_agent(facts, plan, template, run_date)
    trace_events.append(_trace("Drafting Agent", f"Drafted a {draft.intent} response and checklist."))

    verification = verify_plan_against_source(source_text, plan, draft)
    trace_events.append(_trace("Verification Agent", f"Verification {'passed' if verification.passed else 'failed'} with score {verification.source_alignment_score}."))

    task_result = task_store([item.model_dump(mode="json") for item in plan.action_items])
    safety_result = safety_boundary_check(draft.body)
    mcp_calls.append(
        _mcp_call(
            "task_store",
            "Store the planned actions in the local task sink for demo continuity.",
            task_result,
        )
    )
    mcp_calls.append(
        _mcp_call(
            "safety_boundary_check",
            "Check the draft for unsafe claims or unredacted sensitive information.",
            safety_result,
        )
    )

    safe_facts = _sanitize_model(facts, DocumentFacts)
    safe_plan = _sanitize_model(plan, ActionPlan)
    safe_draft = _sanitize_model(draft, DraftOutput)
    redacted_output = redaction_agent(safe_facts, safe_plan, safe_draft, verification.passed)
    trace_events.append(_trace("Redaction Agent", "Sanitized sensitive fields before final presentation."))

    mcp_trace = [
        *risk_trace,
        *lookup_trace,
        f"task_store:{task_result['stored_count']}",
        f"safety_boundary_check:{'allowed' if safety_result['allowed'] else 'warnings'}",
    ]

    return FinalResponse(
        facts=safe_facts,
        risk=risk,
        plan=safe_plan,
        draft=safe_draft,
        verification=verification,
        redacted_output=redacted_output,
        mcp_trace=mcp_trace,
        metadata={
            "current_date": run_date,
            "extraction": extraction_metadata,
            "trace": trace_events,
            "mcp_calls": mcp_calls,
            "agent_count": len(AGENT_PROMPTS),
        },
    )


def _load_document_from_args(args: argparse.Namespace) -> str:
    return load_document_input(args.path, args.text)


def format_trace(result: FinalResponse) -> str:
    lines = ["Agent trace:"]
    for event in result.metadata.get("trace", []):
        lines.append(f"- {event.get('stage')}: {event.get('detail')}")
    lines.append("")
    lines.append("MCP tool calls:")
    for call in result.metadata.get("mcp_calls", []):
        lines.append(f"- {call.get('tool')}: {call.get('why')}")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the NextStep Agent pipeline.")
    parser.add_argument("path", nargs="?", help="Path to a text document.")
    parser.add_argument("--text", help="Document text to process.")
    parser.add_argument("--current-date", help="ISO date used for deadline calculations.")
    parser.add_argument("--use-gemini", action="store_true", help="Use Gemini extraction when GOOGLE_API_KEY is available.")
    parser.add_argument("--compact", action="store_true", help="Print compact JSON.")
    parser.add_argument("--json", action="store_true", help="Emit valid JSON output.")
    parser.add_argument("--trace", action="store_true", help="Print a stage-by-stage agent and MCP trace.")
    args = parser.parse_args()

    document_text = _load_document_from_args(args)
    result = run_pipeline(document_text, current_date=args.current_date, use_gemini=args.use_gemini)
    indent = None if args.compact else 2

    if args.trace and not args.json and not args.compact:
        print(format_trace(result))
        print()
    print(json.dumps(result.model_dump(mode="json"), indent=indent))


if __name__ == "__main__":
    main()
