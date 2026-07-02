from __future__ import annotations

from datetime import date
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


RiskLevel = Literal["low", "medium", "high"]
ActionStatus = Literal["open", "blocked", "done"]


class BaseSchema(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class DocumentFacts(BaseSchema):
    document_type: str = Field(description="Detected document category.")
    source_name: str | None = Field(default=None, description="Document title or first meaningful line.")
    sender: str | None = None
    recipient: str | None = None
    dates: list[str] = Field(default_factory=list)
    deadlines: list[str] = Field(default_factory=list)
    amounts: list[str] = Field(default_factory=list)
    identifiers: list[str] = Field(default_factory=list)
    required_actions: list[str] = Field(default_factory=list)
    contact_methods: list[str] = Field(default_factory=list)
    sensitive_fields: list[str] = Field(default_factory=list)


class RiskAssessment(BaseSchema):
    level: RiskLevel
    flags: list[str] = Field(default_factory=list)
    explanation: str
    requires_human_review: bool = False


class ActionItem(BaseSchema):
    id: str
    title: str
    details: str
    due_date: date | None = None
    priority: int = Field(ge=1, le=5, description="1 is highest priority.")
    status: ActionStatus = "open"
    owner: str = "user"
    source_evidence: str


class ActionPlan(BaseSchema):
    summary: str
    action_items: list[ActionItem]
    resources: list[str] = Field(default_factory=list)
    risk_assessment: RiskAssessment


class DraftOutput(BaseSchema):
    intent: str
    subject: str
    body: str
    checklist: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    redacted: bool = False


class VerificationReport(BaseSchema):
    passed: bool
    issues: list[str] = Field(default_factory=list)
    unsupported_claims: list[str] = Field(default_factory=list)
    missing_required_actions: list[str] = Field(default_factory=list)
    source_alignment_score: float = Field(ge=0.0, le=1.0)


class FinalResponse(BaseSchema):
    facts: DocumentFacts
    risk: RiskAssessment
    plan: ActionPlan
    draft: DraftOutput
    verification: VerificationReport
    redacted_output: str
    mcp_trace: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
