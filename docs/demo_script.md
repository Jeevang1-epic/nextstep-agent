# Demo Script

## Goal

Show that NextStep Agent can turn a confusing document into a safe, prioritized next-step plan with visible MCP usage, verification, and redaction.

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Demo 1: School Notice

```powershell
python -m nextstep_agent.agent examples/sample_school_notice.txt --current-date 2026-07-02
```

Expected talking points:

- Document type is detected as `school_notice`.
- Permission slip and payment deadline are detected.
- Risk is medium because the deadline is within seven days and the context involves a student.
- MCP trace shows calls to deadline, policy lookup, template fetch, task store, and safety boundary tools.
- Final output redacts student ID, email, phone number, and labeled names.
- Verification passes only if the draft is grounded in the source.

## Demo 2: Utility Bill

```powershell
python -m nextstep_agent.agent examples/sample_utility_bill.txt --current-date 2026-07-02
```

Expected talking points:

- Disconnect language raises the risk level.
- Payment and contact actions are prioritized.
- Account details are redacted.
- The draft avoids claiming payment was made.

## Demo 3: Invoice

```powershell
python -m nextstep_agent.agent examples/sample_invoice.txt --current-date 2026-07-02
```

Expected talking points:

- Invoice amount and due date are extracted.
- The plan recommends validating the invoice and scheduling payment or contacting the vendor.
- Invoice and email identifiers are redacted.

## Validation

Run:

```powershell
pytest -q
```

The tests cover redaction behavior and deadline parsing.
