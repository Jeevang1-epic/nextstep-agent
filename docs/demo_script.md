# Demo Script

## 0:00-0:25 Problem Hook

Every week people receive confusing notices: a school slip, a bill, an invoice, a clinic reminder, or an intake form. The problem is not just reading the document. The problem is knowing what to do next, by when, what could go wrong, and what information should not be exposed in a reply.

NextStep Agent is built for that moment.

## 0:25-0:55 Solution Overview

NextStep Agent turns a document into a safe action plan. A user can paste text or upload a text, PDF, or Gemini-backed image document. The system extracts key facts, calculates deadlines, checks risk, looks up local resources through MCP tools, creates prioritized next steps, drafts a response or checklist, verifies it against the source, redacts sensitive information, and stores the tasks locally.

It works without an API key using deterministic extraction, and it can use Gemini structured extraction when `GOOGLE_API_KEY` is configured.

## 0:55-1:35 Architecture And Agents

The workflow is intentionally multi-agent:

- Intake Agent normalizes the document.
- Extraction Agent creates typed facts, using Gemini when available.
- Risk & Priority Agent calculates urgency.
- Resource Lookup Agent calls MCP tools.
- Action Planner Agent creates source-backed tasks.
- Drafting Agent writes a cautious response.
- Verification Agent checks for unsupported claims.
- Redaction Agent removes sensitive fields before final output.

The schema handoffs are Pydantic models, so the output is structured and testable.

## 1:35-2:45 Live Demo: School Notice And Invoice

First run:

```powershell
python -m nextstep_agent.agent examples/sample_school_notice.txt --current-date 2026-07-02 --trace
```

Show the trace. Point out the MCP calls: `deadline_calculator`, `policy_lookup`, `template_fetch`, `task_store`, and `safety_boundary_check`. The school notice becomes a medium-risk plan because the deadline is within seven days and it involves a student. The output redacts the student name, student ID, email, and phone number.

Next run:

```powershell
python -m nextstep_agent.agent examples/sample_invoice.txt --current-date 2026-07-02 --json
```

Show that the output is valid JSON matching `FinalResponse`. Highlight the invoice amount, due date, prioritized actions, verification pass, and saved task metadata.

Then open the app:

```powershell
streamlit run app.py
```

Use the sample dropdown, run the school notice, and show each section in the UI.

If showing document uploads, use a small text-based PDF generated from one of the examples. The app and CLI use `pypdf` for text-based PDFs and show an install message if the dependency is missing. For a screenshot or phone photo, use:

```powershell
python -m nextstep_agent.agent path/to/sample_notice.png --use-gemini --trace
```

If `GOOGLE_API_KEY` is missing, the CLI and app show that image OCR requires Gemini.

## 2:45-3:30 MCP, Security, Redaction, Verification

The MCP server is not decorative. The action plan depends on MCP-backed tools for deadlines, local policy guidance, templates, task storage, and safety checks.

Security is visible. Redaction covers email, phone, account-like numbers, 12 digit ID-like sequences, simple addresses, and labeled names. The verifier blocks unsupported claims such as saying a payment has already been made, giving legal advice, or giving medical advice. The draft stays organizational and source-grounded.

## 3:30-4:15 Evals And Deployability

Run:

```powershell
python evals/run_evals.py
```

The evaluation suite includes ten scenarios: school, invoice, utility, appointment, NGO intake, rental maintenance, internship, medical appointment, small business order, and scholarship or college fee circular. It checks document type, risk, action count, MCP tools, redaction behavior, and unsafe claims. The report is saved to `evals/eval_report.md`.

Deployment is ready through Streamlit Community Cloud. The app runs without an API key, and Gemini is enabled by adding `GOOGLE_API_KEY` in Streamlit secrets.

## 4:15-4:45 Impact, Limitations, Closing

NextStep Agent is not a legal, medical, or financial advisor. It is a document-to-action concierge: it helps people organize confusing documents safely, avoid missed deadlines, and protect sensitive information.

Future work includes OCR benchmarks, richer multilingual support, durable hosted storage, and live ADK runner orchestration. The current project is intentionally scoped, testable, and demo-ready for the capstone.
