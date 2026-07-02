# NextStep Agent

NextStep Agent is a Phase 1 foundation for a multimodal document-to-action concierge agent. It turns confusing real-world documents into a safe, prioritized next-step plan with redaction, verification, and local resource lookup.

The project is scoped for the Kaggle AI Agents Intensive Vibe Coding Capstone. Phase 1 is intentionally deterministic so the demo and tests run locally without API keys, while the architecture is ready for Google ADK and MCP-backed tool use in later phases.

## Problem

People often receive notices, bills, invoices, forms, and appointment slips that are hard to interpret quickly. The risk is missing a deadline, paying the wrong amount, exposing sensitive information, or replying with unsupported claims.

## Solution

NextStep Agent extracts key facts, detects deadlines, checks risk, calls a local MCP resource/template server, creates a prioritized action plan, drafts a safe response or checklist, verifies the draft against the source document, and redacts sensitive information before presenting the output.

## Phase 1 Features

- Typed Pydantic schemas for facts, risk, actions, plans, drafts, verification, and final responses.
- ADK-oriented multi-agent structure with named specialist agents.
- Local MCP server exposing real tools for policy lookup, templates, deadline calculation, task storage, and safety checks.
- CLI runner for local demos without live model calls.
- Sample school notice, invoice, and utility bill documents.
- Redaction and deadline parser tests.

## Architecture

The Phase 1 pipeline is organized as these named agents:

1. Intake Agent
2. Extraction Agent
3. Risk & Priority Agent
4. Resource Lookup Agent
5. Action Planner Agent
6. Drafting Agent
7. Verification Agent
8. Redaction Agent

The MCP server in `mcp_server/server.py` exposes:

- `policy_lookup(query, category)`
- `template_fetch(intent)`
- `deadline_calculator(date_text, current_date)`
- `task_store(action_items)`
- `safety_boundary_check(output)`

See `docs/architecture.md` for the full flow.

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

No API key is required for the Phase 1 CLI. `.env.example` shows the optional variables for later ADK/Gemini integration.

## Run The Demo

```powershell
python -m nextstep_agent.agent examples/sample_school_notice.txt --current-date 2026-07-02
```

You can also pass pasted text:

```powershell
python -m nextstep_agent.agent --text "Payment due by July 12, 2026. Account Number: 1234567890." --current-date 2026-07-02
```

## Expected Output Example

The CLI returns JSON. A shortened example for the school notice looks like this:

```json
{
  "facts": {
    "document_type": "school_notice",
    "deadlines": ["Permission slips and payment are due by July 8, 2026."],
    "required_actions": ["Please return the signed permission slip and $18 fee by July 8, 2026."]
  },
  "risk": {
    "level": "medium",
    "flags": ["deadline_within_7_days", "minor_or_school_context"]
  },
  "plan": {
    "action_items": [
      {
        "title": "Return signed permission slip and fee",
        "due_date": "2026-07-08",
        "priority": 2
      }
    ]
  },
  "verification": {
    "passed": true
  },
  "redacted_output": "NextStep summary..."
}
```

Sensitive fields such as email addresses, phone numbers, account numbers, student IDs, invoice IDs, and labeled names are replaced with redaction markers.

## Tests

```powershell
pytest -q
```

There is no lint command configured in Phase 1.

## Limitations

- Extraction is heuristic and designed for stable local demos, not production accuracy.
- OCR, image upload handling, and live LLM reasoning are planned for later phases.
- The MCP server runs locally over stdio when used by an MCP client; the CLI calls the same tool functions directly.
- Deadline parsing supports common absolute and relative phrases but does not cover every locale or business calendar.
- Drafts are informational and should be reviewed by a human before sending.

## Repository Hygiene

This repo intentionally avoids committed secrets, local environments, generated caches, and assistant-specific files.
