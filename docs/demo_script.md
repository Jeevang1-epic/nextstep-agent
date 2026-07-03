# Demo Script

Target length: 4-5 minutes.

## Screen Recording Checklist

- Browser tab open to the GitHub README.
- Browser tab open to the public app: `PASTE_STREAMLIT_URL_HERE`.
- Terminal open at the repository root.
- Streamlit app ready or easy to start with `streamlit run app.py`.
- Demo files available in `demo_pack/`.
- Terminal font large enough to read in video.
- No `.env`, secrets, local API keys, or personal files visible.
- If using Gemini, verify `GOOGLE_API_KEY` is configured before recording.
- If not using Gemini, mention deterministic fallback clearly.
- Run `python evals/run_evals.py` once before recording so the report is fresh.

## Exact Narration

### 0:00-0:25 - GitHub README And Problem

Show: GitHub README top section.

Narration:

```text
This is NextStep Agent, a document-to-action concierge for the Kaggle AI Agents Intensive capstone. The one-line goal is simple: turn confusing real-world documents into safe, verified next steps.

The problem is that everyday documents often hide important actions. A school notice, invoice, utility bill, appointment slip, or intake form may include deadlines, risk, payment details, or sensitive identifiers. The user does not just need a summary. They need to know what to do next, by when, and what information should be protected.
```

### 0:25-0:55 - Solution Overview

Show: README competition alignment table.

Narration:

```text
NextStep Agent handles that workflow with a traceable multi-agent pipeline. It extracts key facts, detects deadlines, checks risk, calls local MCP tools, builds a prioritized action plan, drafts a cautious response or checklist, verifies the draft against the source document, redacts sensitive information, and stores redacted tasks locally.

This is organizational assistance only. It is not legal, medical, or financial advice.
```

### 0:55-1:25 - Public App Demo

Show: deployed Streamlit app at `PASTE_STREAMLIT_URL_HERE`.

Narration:

```text
The public Streamlit demo is deployed at PASTE_STREAMLIT_URL_HERE. The app is the judge-friendly review surface. It supports pasted text, sample documents, text files, Markdown, text-based PDFs, and optional Gemini-backed image extraction.

Gemini is optional and configured only through Streamlit Community Cloud secrets when available. If no API key is configured, deterministic text extraction still works and the evaluation suite remains fully reproducible.
```

### 1:25-2:10 - School Notice Trace

Show: public app school notice sample, then terminal trace command if desired.

```powershell
python -m nextstep_agent.agent demo_pack/demo_school_notice.txt --current-date 2026-07-02 --trace
```

Narration:

```text
Here is the school notice demo. The trace shows the named stages: Intake, Extraction, Risk and Priority, Resource Lookup, Action Planner, Drafting, Verification, and Redaction.

The notice is transformed into typed facts, a deadline, risk assessment, and next steps. Because the permission form is due soon and involves a student, the risk is elevated. The final response includes a checklist and a safe draft while redacting the student name, student ID, and contact information.
```

### 2:10-2:45 - Agent Trace And MCP Tool Calls

Show: MCP calls in CLI trace or Streamlit MCP section.

Narration:

```text
MCP usage is real in this project. The pipeline calls a local MCP-style server for deadline calculation, policy lookup, template selection, task storage, and safety boundary checks.

Those tool calls affect the output. The deadline tool normalizes dates, the resource tools supply local guidance and templates, the task tool stores redacted actions, and the safety check helps catch risky draft language.
```

### 2:45-3:15 - Invoice Demo

Show: invoice sample in Streamlit cards or terminal JSON output.

```powershell
python -m nextstep_agent.agent demo_pack/demo_invoice.txt --current-date 2026-07-02 --json
```

Narration:

```text
The invoice demo shows the same pipeline as structured JSON. The output follows the FinalResponse schema, including extracted facts, risk, actions, draft, verification, redacted output, MCP metadata, and saved task information.

This matters because the system is testable. It is not only a fluent answer in a chat window.
```

### 3:15-3:45 - Security And Redaction

Show: Streamlit redaction and verification sections.

Narration:

```text
Security is visible, not hidden. The redaction stage removes emails, phone numbers, account-like values, labeled identifiers, simple addresses, and labeled names. The verifier checks that the draft is grounded in the source and avoids unsupported legal, medical, financial, or payment-status claims.

The saved task store is also redacted, and runtime task data is ignored by git.
```

### 3:45-4:15 - Evaluation Report

Show terminal command and result:

```powershell
python evals/run_evals.py
```

Narration:

```text
The deterministic evaluation suite covers ten scenarios: school notice, invoice, utility bill, appointment slip, NGO intake, rental maintenance, internship deadline, medical appointment reminder, small-business order request, and scholarship or college fee circular.

The current release candidate passes 10 out of 10 scenarios with an 80 out of 80 deterministic score.
```

### 4:15-4:40 - Deployability Proof

Show: deployed app URL, `docs/deployment.md`, and README deployment section.

Narration:

```text
The project is deployed on Streamlit Community Cloud and remains reproducible locally. Secrets are configured only through Streamlit settings, not committed to GitHub. The architecture is intentionally scoped for a five-day capstone: document loader, typed schemas, named agents, local MCP tools, verification, redaction, task storage, CLI, Streamlit UI, and deterministic evals.
```

### 4:40-5:00 - Closing Impact

Show: README tagline or closing slide.

Narration:

```text
NextStep Agent is built for a common, practical problem: turning confusing documents into clear next steps while protecting sensitive information. It is small enough to inspect, reliable enough to demo, and structured enough to extend after the capstone.
```

## Required Shots

1. GitHub README top section.
2. Public Streamlit app landing view at `PASTE_STREAMLIT_URL_HERE`.
3. School notice run with trace.
4. Invoice run with JSON output or Streamlit cards.
5. MCP tool calls section.
6. Redaction and security section.
7. Eval report showing 10/10 and 80/80.
8. Deployability proof and architecture diagram.
9. Closing impact slide or README tagline.

## Commands To Capture

```powershell
python -m nextstep_agent.agent demo_pack/demo_school_notice.txt --current-date 2026-07-02 --trace
python -m nextstep_agent.agent demo_pack/demo_invoice.txt --current-date 2026-07-02 --json
python evals/run_evals.py
streamlit run app.py
```

## If Gemini Is Available

Optional short add-on:

```powershell
python -m nextstep_agent.agent demo_pack/demo_school_notice.txt --current-date 2026-07-02 --use-gemini --trace
```

Say:

```text
Gemini is optional. With an API key, it can provide structured extraction and image understanding. Without a key, the deterministic text pipeline still works for local and judged demos.
```
