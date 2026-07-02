from evals.run_evals import load_cases, markdown_summary, run_cases


def test_evaluation_cases_pass() -> None:
    summary = run_cases(load_cases())

    assert summary["total"] >= 10
    assert summary["failed"] == 0
    assert summary["score_percent"] == 100.0
    report = markdown_summary(summary)
    assert "Total score:" in report
    assert "| Case | Status | Score | Reason |" in report
