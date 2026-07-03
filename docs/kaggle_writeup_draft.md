# NextStep Agent

## Track: Concierge Agents

## Project Links

- Public demo: `PASTE_STREAMLIT_URL_HERE`
- GitHub repository: `https://github.com/Jeevang1-epic/nextstep-agent`
- Track: Concierge Agents

NextStep Agent turns confusing real-world documents into safe, verified next steps. The project focuses on the everyday moment when a person receives a school notice, invoice, utility bill, appointment slip, small-business notice, or intake form and does not immediately know what matters, what is due, what could go wrong, or what can be safely shared. Instead of producing one broad chat answer, NextStep Agent runs a traceable agent workflow: extract facts, detect deadlines, assess risk, call MCP-backed local resources, create prioritized tasks, draft a cautious response or checklist, verify the draft against the source, redact sensitive information, and save redacted tasks locally.

The selected track is Concierge Agents because the system helps a user complete a practical workflow from messy input to a clear plan. It is not legal, medical, or financial advice. It is organizational assistance that helps the user prepare, verify, and act more confidently.

## Problem

Everyday documents often carry hidden consequences. A permission slip may have a return date in the middle of a paragraph. A bill may include a service interruption warning. An invoice may mix vendor details, due dates, amounts, and payment instructions. An appointment reminder may include preparation steps but should not become medical advice. An intake form may request sensitive information that should not be copied into a casual reply.

The user usually needs five answers:

- What kind of document is this?
- What are the key facts?
- What is due and when?
- What should I do first?
- What information should be protected?

A plain chatbot can help, but it can also miss deadlines, overstate risk, invent payment status, or echo sensitive identifiers. For this use case, judgeability and safety matter as much as fluency.

## Why This Needs Agents

The workflow has several jobs with different failure modes. Extraction should be structured. Deadline handling should be deterministic. Risk assessment should consider urgency and consequences. Resource lookup should use grounded local knowledge. Drafting should be careful. Verification should check source support. Redaction should happen after the final answer is assembled.

NextStep Agent separates those jobs into named stages:

- Intake Agent normalizes the document.
- Extraction Agent creates typed `DocumentFacts`.
- Risk & Priority Agent calculates urgency and risk.
- Resource Lookup Agent calls MCP tools.
- Action Planner Agent produces prioritized tasks.
- Drafting Agent creates a response or checklist.
- Verification Agent checks grounding and unsafe claims.
- Redaction Agent sanitizes the final output.

This makes the system inspectable. The CLI trace and Streamlit app show the stages and MCP calls, so a reviewer can see how the answer was produced.

## Solution

The project supports pasted text, `.txt`, `.md`, text-based `.pdf`, and optional Gemini-backed image input. Gemini is optional. Without `GOOGLE_API_KEY`, the deterministic text pipeline still runs, tests pass, and evals are reproducible. With a key, Gemini can provide structured extraction and image understanding. If image extraction is requested without Gemini, the app explains the limitation instead of failing silently.

The final output is a Pydantic `FinalResponse` containing extracted facts, risk assessment, action plan, draft output, verification report, redacted output, MCP trace, and saved task metadata. This keeps the result easy to test and easy to present. The deployed Streamlit demo at `PASTE_STREAMLIT_URL_HERE` exposes the same workflow through a judge-friendly interface.

## Architecture

The architecture is intentionally small enough for a five-day capstone:

1. Document loader reads pasted text, text files, Markdown, text-based PDFs, or Gemini-backed images.
2. Agent pipeline turns the document into typed facts, risk, actions, draft, verification, and redacted output.
3. Local MCP server provides `policy_lookup`, `template_fetch`, `deadline_calculator`, `task_store`, and `safety_boundary_check`.
4. Task storage writes redacted action records to a local JSONL file ignored by git.
5. CLI and Streamlit expose the same workflow for reproducible demos and interactive review.
6. Deterministic evals and unit tests serve as the quality gate.

The project is Google ADK-aligned. It defines ADK-compatible agent objects when the ADK package is available, while retaining a local execution path so judges can run the project without extra cloud configuration.

## MCP Usage

MCP is part of the normal workflow, not a decorative integration. Deadline calculations, local resource guidance, templates, task persistence, and safety checks all flow through tools in `mcp_server/server.py`. The trace records these calls and the eval suite checks expected tool coverage.

Examples:

- `deadline_calculator` normalizes due dates against the current date.
- `policy_lookup` retrieves relevant local guidance from the resource pack.
- `template_fetch` selects a response or checklist template.
- `task_store` persists redacted tasks.
- `safety_boundary_check` flags risky draft language.

## Security And Redaction

Security is visible in the product. The system redacts emails, phone numbers, account-like values, 12 digit ID-like values, simple addresses, labeled identifiers, and labeled names. The verifier rejects unsupported claims such as saying a payment has already been made or giving legal or medical advice. The app tells users that NextStep Agent provides organizational help only.

The local task store is also treated carefully. Saved tasks are redacted and `data/tasks.jsonl` is ignored by git.

## Evaluation

The deterministic evaluation suite contains ten scenarios:

1. School notice.
2. Invoice.
3. Utility bill.
4. Appointment slip.
5. NGO intake form.
6. Rental maintenance notice.
7. Internship deadline.
8. Medical appointment reminder.
9. Small-business order request.
10. Scholarship or college fee circular.

Each case checks document type, minimum action count, expected risk level, MCP tool usage, redaction behavior, verification, and absence of unsafe claims.

Current result:

- 10/10 scenarios passed.
- 0 failed.
- 80/80 deterministic score.

The runner writes `evals/eval_report.md`, and `scripts/final_qa.py` runs the release-candidate gate.

## Demo Plan

The strongest demo is the school notice. It shows a realistic deadline, student context, MCP deadline calculation, policy/template lookup, action plan, draft checklist, verification, redaction, and task storage. The second demo is an invoice shown as JSON, which proves the output is structured. The Streamlit app then provides the judge-friendly interactive view with cards for facts, risk, MCP calls, next steps, verification, redaction, and saved tasks.

The deployed Streamlit demo is available at `PASTE_STREAMLIT_URL_HERE`. The demo can be recorded without an API key because deterministic text extraction remains the reliable baseline. If Gemini is available in Streamlit secrets, a short optional segment can compare deterministic extraction with Gemini structured extraction.

## Limitations

NextStep Agent is a release-candidate capstone, not a production document automation platform. Image extraction requires Gemini. Text-based PDFs work through `pypdf`; scanned PDFs should be treated as images. The deterministic extractor is conservative and may miss unusual phrasing. The JSONL task store is demo-grade and not a hosted multi-user database. Drafts should be reviewed by the user before sending.

These limits are intentional for this phase. The project prioritizes a clear agent workflow, real tool usage, visible safety controls, and repeatable evaluation over a large unfinished feature set.

## Secondary Impact

Although the selected track is Concierge Agents, the project also has secondary relevance to business productivity, good causes, and freestyle agent design. Small businesses could use the same pattern for invoices and customer notices. Community organizations could use it for intake forms. Students and families could use it for school and scholarship deadlines. These are impact areas, but the core submission remains a concierge workflow.

## What I Learned

This project made the course ideas concrete for me. Useful agents are not just larger prompts. They need schemas, tools, state, safety boundaries, evaluation, and a user experience that shows what happened. MCP helped ground the system in local resources. Pydantic models made handoffs testable. The eval suite caught regressions. Redaction and verification worked best as first-class stages, not final afterthoughts.

The result is a scoped, inspectable agent that solves a real everyday problem and stays honest about what it can and cannot do.
