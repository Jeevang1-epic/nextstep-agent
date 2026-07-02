from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from nextstep_agent.agent import run_pipeline


UNSAFE_CLAIMS = (
    "payment has been made",
    "i have already paid",
    "legal advice",
    "medical advice",
    "diagnose",
    "guarantee",
)


def load_cases(path: Path | None = None) -> list[dict[str, Any]]:
    case_path = path or Path(__file__).with_name("cases.json")
    return json.loads(case_path.read_text(encoding="utf-8"))


def _contains_deadline(result: Any, expected_text: str) -> bool:
    haystack = " ".join([*result.facts.deadlines, *result.facts.dates, result.redacted_output])
    return expected_text.lower() in haystack.lower()


def _called_tools(result: Any) -> set[str]:
    calls = {call.get("tool", "") for call in result.metadata.get("mcp_calls", [])}
    calls.update(entry.split(":", 1)[0] for entry in result.mcp_trace)
    return calls


def _no_unsafe_claims(result: Any) -> bool:
    text = f"{result.draft.body}\n{result.redacted_output}".lower()
    return not any(claim in text for claim in UNSAFE_CLAIMS) and not result.verification.unsupported_claims


def _display_path(path_value: str | None) -> str | None:
    if not path_value:
        return None
    path = Path(path_value)
    if not path.is_absolute():
        return str(path).replace("\\", "/")
    try:
        return str(path.relative_to(ROOT_DIR)).replace("\\", "/")
    except ValueError:
        return path.name


def evaluate_case(case: dict[str, Any], current_date: str = "2026-07-02") -> dict[str, Any]:
    expected = case["expected"]
    result = run_pipeline(case["document"], current_date=current_date)
    called_tools = _called_tools(result)
    checks = {
        "document_type": result.facts.document_type == expected["document_type"],
        "deadline": _contains_deadline(result, expected["deadline_contains"]),
        "risk_level": result.risk.level == expected["risk_level"],
        "mcp_tools": set(expected["mcp_tools"]).issubset(called_tools),
        "redaction": ("[REDACTED_" in result.redacted_output or bool(result.facts.sensitive_fields))
        if expected["redaction_expected"]
        else True,
        "action_count": len(result.plan.action_items) >= expected["min_action_items"],
        "verification": result.verification.passed,
        "no_unsafe_claims": _no_unsafe_claims(result),
    }
    failed_reasons = [name for name, passed in checks.items() if not passed]
    return {
        "id": case["id"],
        "passed": all(checks.values()),
        "score": sum(1 for passed in checks.values() if passed),
        "max_score": len(checks),
        "checks": checks,
        "reason": "pass" if all(checks.values()) else ", ".join(failed_reasons),
        "notes": {
            "document_type": result.facts.document_type,
            "risk_level": result.risk.level,
            "action_items": len(result.plan.action_items),
            "mcp_tools": sorted(called_tools),
            "task_store_path": _display_path(result.metadata.get("saved_tasks", {}).get("task_store_path")),
        },
    }


def run_cases(cases: list[dict[str, Any]], current_date: str = "2026-07-02") -> dict[str, Any]:
    results = [evaluate_case(case, current_date=current_date) for case in cases]
    total_score = sum(result["score"] for result in results)
    max_score = sum(result["max_score"] for result in results)
    return {
        "total": len(results),
        "passed": sum(1 for result in results if result["passed"]),
        "failed": sum(1 for result in results if not result["passed"]),
        "score": total_score,
        "max_score": max_score,
        "score_percent": round((total_score / max_score) * 100, 1) if max_score else 0.0,
        "results": results,
    }


def markdown_summary(summary: dict[str, Any]) -> str:
    lines = [
        "# NextStep Agent Evaluation Report",
        "",
        f"Total cases: {summary['total']}",
        f"Passed cases: {summary['passed']}",
        f"Failed cases: {summary['failed']}",
        f"Total score: {summary['score']}/{summary['max_score']} ({summary['score_percent']}%)",
        "",
        "| Case | Status | Score | Reason |",
        "| --- | --- | ---: | --- |",
    ]
    for result in summary["results"]:
        status = "PASS" if result["passed"] else "FAIL"
        lines.append(f"| {result['id']} | {status} | {result['score']}/{result['max_score']} | {result['reason']} |")

    lines.extend(["", "## Per-Case Notes", ""])
    for result in summary["results"]:
        lines.append(f"### {result['id']}")
        lines.append(f"- Status: {'PASS' if result['passed'] else 'FAIL'}")
        lines.append(f"- Reason: {result['reason']}")
        lines.append(f"- Notes: `{json.dumps(result['notes'], sort_keys=True)}`")
        lines.append("")
    return "\n".join(lines)


def print_summary(summary: dict[str, Any]) -> None:
    print("NextStep Agent Evaluation")
    print(f"Total: {summary['total']} | Passed: {summary['passed']} | Failed: {summary['failed']}")
    print(f"Score: {summary['score']}/{summary['max_score']} ({summary['score_percent']}%)")
    print()
    print(f"{'Case':36} {'Status':8} {'Score':8} Reason")
    print("-" * 80)
    for result in summary["results"]:
        status = "PASS" if result["passed"] else "FAIL"
        print(f"{result['id'][:36]:36} {status:8} {result['score']}/{result['max_score']:<5} {result['reason']}")


def write_report(summary: dict[str, Any], path: Path | None = None) -> Path:
    report_path = path or Path(__file__).with_name("eval_report.md")
    report_path.write_text(markdown_summary(summary), encoding="utf-8")
    return report_path


def main() -> None:
    summary = run_cases(load_cases())
    print_summary(summary)
    report_path = write_report(summary)
    print()
    print(f"Markdown report: {report_path}")
    if summary["failed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
