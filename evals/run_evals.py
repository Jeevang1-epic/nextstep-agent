from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from nextstep_agent.agent import run_pipeline


def load_cases(path: Path | None = None) -> list[dict[str, Any]]:
    case_path = path or Path(__file__).with_name("cases.json")
    return json.loads(case_path.read_text(encoding="utf-8"))


def _contains_deadline(result: Any, expected_text: str) -> bool:
    haystack = " ".join([*result.facts.deadlines, *result.facts.dates, result.redacted_output])
    return expected_text.lower() in haystack.lower()


def evaluate_case(case: dict[str, Any], current_date: str = "2026-07-02") -> dict[str, Any]:
    expected = case["expected"]
    result = run_pipeline(case["document"], current_date=current_date)
    checks = {
        "document_type": result.facts.document_type == expected["document_type"],
        "deadline": _contains_deadline(result, expected["deadline_contains"]),
        "risk_level": result.risk.level == expected["risk_level"],
        "redaction": ("[REDACTED_" in result.redacted_output or bool(result.facts.sensitive_fields))
        if expected["redaction_expected"]
        else True,
        "action_count": len(result.plan.action_items) >= expected["min_action_items"],
        "verification": result.verification.passed,
    }
    return {
        "id": case["id"],
        "passed": all(checks.values()),
        "checks": checks,
        "notes": {
            "document_type": result.facts.document_type,
            "risk_level": result.risk.level,
            "action_items": len(result.plan.action_items),
            "mcp_trace": result.mcp_trace,
        },
    }


def run_cases(cases: list[dict[str, Any]], current_date: str = "2026-07-02") -> dict[str, Any]:
    results = [evaluate_case(case, current_date=current_date) for case in cases]
    return {
        "total": len(results),
        "passed": sum(1 for result in results if result["passed"]),
        "failed": sum(1 for result in results if not result["passed"]),
        "results": results,
    }


def print_summary(summary: dict[str, Any]) -> None:
    print("# NextStep Agent Evaluation")
    print()
    print(f"Total cases: {summary['total']}")
    print(f"Passed cases: {summary['passed']}")
    print(f"Failed cases: {summary['failed']}")
    print()
    for result in summary["results"]:
        status = "PASS" if result["passed"] else "FAIL"
        print(f"## {result['id']}: {status}")
        for check, passed in result["checks"].items():
            print(f"- {check}: {'pass' if passed else 'fail'}")
        print(f"- notes: {json.dumps(result['notes'], sort_keys=True)}")
        print()


def main() -> None:
    summary = run_cases(load_cases())
    print_summary(summary)
    if summary["failed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
