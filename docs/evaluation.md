# Evaluation

Prompt 1.1 adds fixture-based evaluation in `evals/cases.json` and `evals/run_evals.py`.

## Run

```powershell
python evals/run_evals.py
```

## Coverage

The current fixture set covers:

- School notice with deadline and student redaction.
- Invoice with payment due date and amount.
- Utility bill with service interruption risk.
- Appointment slip with preparation actions.
- NGO intake form with sensitive support documents.

Each case checks:

- Expected `document_type`.
- At least one deadline or expected deadline phrase.
- Expected risk level.
- Whether redaction is expected.
- Minimum action item count.
- Verification pass/fail.

## Unit Tests

```powershell
python -m pytest -q
```

Tests cover:

- Redaction patterns.
- Deadline parsing.
- Document loading.
- Pipeline JSON/trace metadata.
- Evaluation fixture pass/fail behavior.

## Current Limitations

- Eval fixtures are deterministic text cases, not a broad benchmark.
- Gemini output quality is not scored separately yet.
- OCR and scanned document cases are intentionally deferred.

## Prompt 1.2 Evaluation Ideas

- Add golden JSON snapshots for every case.
- Add Gemini-vs-heuristic comparison metrics.
- Add OCR fixtures once image input is implemented.
- Add rubric scoring for action usefulness and draft quality.
