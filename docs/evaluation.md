# Evaluation

Phase 1 uses deterministic tests and source-grounded checks so the project can be evaluated without live model access.

## Current Checks

`tests/test_redaction.py` verifies that common sensitive fields are removed while useful non-sensitive facts remain available.

`tests/test_deadline_parser.py` verifies absolute dates, relative dates, business-day windows, and overdue detection.

`nextstep_agent/verifier.py` performs runtime checks that action items have evidence and that drafts avoid common unsupported or unsafe claims.

## Manual Demo Evaluation

For each sample document, check:

- Were the key facts extracted?
- Were deadlines parsed relative to the supplied current date?
- Did risk level reflect urgency and consequence?
- Did MCP resource and template lookup influence the plan or draft?
- Did the draft avoid unsupported commitments?
- Were sensitive values redacted from the final output?

## Future Evaluation Set

Prompt 1.1 should add a small fixture-based evaluation suite with expected facts and deadlines for each document type:

- School notice
- Invoice
- Utility bill
- Appointment slip
- Small-business notice
- NGO intake form

Each fixture should score extraction, deadline accuracy, action relevance, verification outcome, and redaction completeness.
