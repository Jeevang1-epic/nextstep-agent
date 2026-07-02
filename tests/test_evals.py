from evals.run_evals import load_cases, run_cases


def test_evaluation_cases_pass() -> None:
    summary = run_cases(load_cases())

    assert summary["total"] >= 5
    assert summary["failed"] == 0
