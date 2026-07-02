# Evaluation

NextStep Agent uses deterministic fixture evaluations plus unit tests. The goal is not to claim production accuracy. The goal is to prove the pipeline is structured, source-grounded, safe, and repeatable.

## Run

```powershell
python evals/run_evals.py
```

The runner prints a console table and writes `evals/eval_report.md`.

## Current Fixture Coverage

The suite contains ten scenarios:

1. School notice with a student deadline.
2. Invoice with amount and payment due date.
3. Utility bill with service interruption risk.
4. Appointment slip with preparation actions.
5. NGO intake or beneficiary support form.
6. Rental or maintenance notice.
7. Internship application deadline.
8. Medical appointment reminder without medical advice.
9. Small business order request.
10. Scholarship or college fee circular.

Each case checks:

- Expected document type or category.
- Minimum action item count.
- Expected risk level.
- Required MCP tools called.
- Expected redaction behavior.
- Verification pass.
- No hallucinated payment, legal, or medical claims.

## Current Result

Latest deterministic run:

- Total cases: 10.
- Passed cases: 10.
- Failed cases: 0.
- Score: 80/80.

See `evals/eval_report.md` and `docs/demo_outputs/eval_report.md` for the generated report.

## Unit Tests

```powershell
python -m pytest -q
```

Tests cover:

- Redaction patterns.
- Deadline parsing.
- Text, Markdown, PDF, and image input gatekeeping.
- Pipeline trace and task persistence metadata.
- Persistent JSONL task storage.
- Evaluation fixture behavior.

## Known Limits

- The fixture suite is deterministic and intentionally small.
- Gemini live extraction quality is not scored automatically yet.
- OCR is delegated to Gemini image input rather than local OCR dependencies.
- The current task store is local JSONL, suitable for demos but not a multi-user hosted database.
