"""NextStep Agent package."""

from typing import Any

from .schemas import (
    ActionItem,
    ActionPlan,
    DocumentFacts,
    DraftOutput,
    FinalResponse,
    RiskAssessment,
    VerificationReport,
)


def run_pipeline(*args: Any, **kwargs: Any) -> FinalResponse:
    from .agent import run_pipeline as _run_pipeline

    return _run_pipeline(*args, **kwargs)


__all__ = [
    "ActionItem",
    "ActionPlan",
    "DocumentFacts",
    "DraftOutput",
    "FinalResponse",
    "RiskAssessment",
    "VerificationReport",
    "run_pipeline",
]
