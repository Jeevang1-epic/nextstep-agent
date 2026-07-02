# Demo Script

## Story

NextStep Agent helps a user turn a confusing document into safe, verified next steps. The demo should show the agent stages, MCP tool calls, redaction, and evaluation evidence.

## CLI Trace Demo

```powershell
python -m nextstep_agent.agent examples/sample_school_notice.txt --current-date 2026-07-02 --trace
```

Show:

- Intake, extraction, risk, MCP lookup, planning, drafting, verification, and redaction stages.
- `deadline_calculator`, `policy_lookup`, `template_fetch`, `task_store`, and `safety_boundary_check` MCP calls.
- Redacted student, email, phone, and identifier values.

## JSON Demo

```powershell
python -m nextstep_agent.agent examples/sample_invoice.txt --current-date 2026-07-02 --json
```

Show:

- Valid `FinalResponse` JSON.
- `metadata.extraction.mode`.
- `metadata.mcp_calls`.

## Streamlit Demo

```powershell
streamlit run app.py
```

Show:

- Pasted text area.
- File upload for `.txt`, `.md`, or text-based `.pdf`.
- Current date input.
- Gemini toggle.
- Agent trace toggle.
- Tabs for extracted facts, risk, next steps, draft, verification, redacted output, and MCP calls.

## Gemini Demo

With `GOOGLE_API_KEY` configured:

```powershell
python -m nextstep_agent.agent examples/sample_school_notice.txt --current-date 2026-07-02 --use-gemini --trace
```

If the key is absent, show the graceful heuristic fallback in `metadata.extraction`.

## Evaluation Demo

```powershell
python evals/run_evals.py
```

Show total cases, passed cases, failed cases, and per-case notes.

## Antigravity Demo Readiness

Use Antigravity or any local demo recorder to show the CLI trace, Streamlit app, tests, and eval runner. Antigravity is not required for the app to run.
