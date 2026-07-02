from __future__ import annotations

import re

from .schemas import ActionPlan, DraftOutput, VerificationReport
from .redaction import find_sensitive_spans


UNSUPPORTED_PHRASES = (
    "payment has been made",
    "i have already paid",
    "guarantee",
    "legal advice",
    "medical advice",
    "ignore the deadline",
    "share your full account number",
    "send your password",
)


def _tokens(text: str) -> set[str]:
    return {token for token in re.findall(r"[a-z0-9$]+", text.lower()) if len(token) > 2}


def _evidence_supported(source_text: str, evidence: str) -> bool:
    source_tokens = _tokens(source_text)
    evidence_tokens = _tokens(evidence)
    if not evidence_tokens:
        return False
    overlap = evidence_tokens & source_tokens
    return len(overlap) / len(evidence_tokens) >= 0.5


def verify_plan_against_source(
    source_text: str,
    plan: ActionPlan,
    draft: DraftOutput,
) -> VerificationReport:
    issues: list[str] = []
    missing_required_actions: list[str] = []

    for item in plan.action_items:
        if not _evidence_supported(source_text, item.source_evidence):
            missing_required_actions.append(item.id)
            issues.append(f"Action item {item.id} lacks enough source evidence.")

    draft_lower = draft.body.lower()
    unsupported_claims = [phrase for phrase in UNSUPPORTED_PHRASES if phrase in draft_lower]
    if unsupported_claims:
        issues.append("Draft contains unsupported or unsafe wording.")

    sensitive_findings = find_sensitive_spans(draft.body)
    if sensitive_findings:
        issues.append("Draft contains unredacted sensitive information.")

    if not plan.action_items:
        issues.append("No action items were generated.")

    total_checks = max(len(plan.action_items) + 1, 1)
    failed_checks = len(missing_required_actions) + (1 if unsupported_claims else 0) + (1 if sensitive_findings else 0)
    alignment_score = max(0.0, 1.0 - failed_checks / total_checks)

    return VerificationReport(
        passed=not issues,
        issues=issues,
        unsupported_claims=unsupported_claims,
        missing_required_actions=missing_required_actions,
        source_alignment_score=round(alignment_score, 2),
    )
