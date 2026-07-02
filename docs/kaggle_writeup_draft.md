# NextStep Agent

## Subtitle

A multimodal document-to-action concierge agent that turns confusing real-world documents into safe, verified next steps.

## Track Selection: Concierge Agents

NextStep Agent fits the Concierge Agents track because it helps a user complete a practical everyday workflow: understanding a document, identifying obligations, and deciding what to do next. The project is not trying to replace a professional advisor. It acts as a careful assistant that reads messy documents, extracts facts, checks deadlines and risk, uses tools, drafts cautious responses, verifies itself, and redacts sensitive information before showing the final answer.

## Problem

Many important documents are written for institutions, not for the person who needs to act on them. A school notice may hide a form deadline in the middle of a paragraph. A utility bill may include service interruption risk. An invoice may have a due date, a vendor, and payment instructions spread across multiple lines. A clinic reminder may include preparation steps but should not become medical advice. An NGO intake form may ask for sensitive documents that should not be emailed casually.

The user often has five immediate questions. What is this document? What are the key facts? What is due and when? What should I do first? What information is sensitive? A normal chat response can answer some of these questions, but the risk is inconsistency. It may miss a deadline, invent a payment status, include personal identifiers in a draft, or fail to show how it reached the answer.

## Why This Needs Agents, Not Just Chat

The workflow has multiple responsibilities that should not be collapsed into one prompt. Extraction, risk assessment, resource lookup, planning, drafting, verification, and redaction are different jobs with different failure modes. NextStep Agent separates them into named agents with typed handoffs. This makes the system easier to inspect and easier to test.

The Intake Agent normalizes the input. The Extraction Agent turns the document into a `DocumentFacts` schema. The Risk & Priority Agent computes urgency and consequence. The Resource Lookup Agent calls MCP tools for local guidance and templates. The Action Planner Agent produces prioritized tasks. The Drafting Agent writes a cautious response. The Verification Agent checks grounding and unsafe claims. The Redaction Agent sanitizes the final output.

This architecture is useful because each stage can be demonstrated. The CLI trace shows which stage ran and which MCP tool was called. The Streamlit app exposes the same sections for judges and users.

## Solution Overview

NextStep Agent accepts pasted text, `.txt`, `.md`, text-based `.pdf`, and Gemini-backed image inputs. It supports deterministic extraction for reliable local demos and optional Gemini structured extraction when `GOOGLE_API_KEY` is configured. If a key is missing, the system falls back gracefully for text. For images, it shows a clear message that OCR requires Gemini rather than adding heavy local OCR dependencies.

The output is a `FinalResponse` Pydantic object. It includes extracted facts, risk assessment, action plan, draft response, verification report, redacted output, MCP trace, saved task metadata, and stage-by-stage trace. This gives a portfolio-quality demo without hiding the reasoning flow inside a single black-box response.

One important design choice was to keep the first useful version deterministic. That means the project can be tested, recorded, and evaluated even when no model key is available. Gemini is then added as an enhancement, not as a single point of failure. This matters for a judged capstone because the reviewer should be able to clone the repository, run tests, run the evals, and see the full workflow immediately. The live model path is still meaningful because it uses structured output and multimodal image input, but the project does not depend on a fragile live call to prove the architecture.

## Architecture

The architecture is intentionally small enough for a five-day capstone but complete enough to be judged. The local package contains the agent pipeline, schemas, document loader, Gemini client, verifier, redaction layer, and task store. The MCP server exposes tools for policy lookup, template fetch, deadline calculation, task storage, and safety boundary checks. The Streamlit app provides an upload-ready interface and the CLI provides reproducible demo commands.

The project is ADK-oriented. `nextstep_agent/agent.py` builds ADK-compatible agent definitions when Google ADK is installed, while still providing local deterministic execution. This avoids making the demo fail because of external configuration while preserving the architecture expected for agent development.

The repository also separates runtime surfaces. The CLI is best for reproducible traces and video snapshots. Streamlit is best for an interactive judge demo. The MCP server is available over stdio for agent tool integration. The evaluation runner is separate so it can be used as a quality gate. This split keeps the implementation realistic without turning the capstone into an oversized platform.

## Agent Workflow

The workflow begins with document intake. Text inputs are read directly. PDFs are parsed with `pypdf` when possible. Image inputs are routed to Gemini multimodal extraction if the user enables Gemini and a key is available. The Intake Agent normalizes the input and records a trace event.

The Extraction Agent creates `DocumentFacts`. This includes document type, sender, recipient, dates, deadlines, amounts, identifiers, required actions, contact methods, and sensitive field categories. The deterministic path uses conservative regex and keyword rules. The Gemini path asks for structured JSON output and validates it with Pydantic. Malformed JSON triggers a safe fallback for text inputs.

The Risk & Priority Agent calculates deadlines by calling the MCP `deadline_calculator` tool. It marks deadlines as overdue, due soon, or upcoming and sets risk using urgency, service interruption language, payment signals, student context, and appointment context.

The Resource Lookup Agent calls MCP `policy_lookup` and `template_fetch`. This makes MCP usage real: local guidance and templates affect the resources and draft type selected for the final plan.

The Action Planner Agent creates action items with id, title, details, due date, priority, status, owner, and source evidence. The Drafting Agent writes a safe response or checklist. The Verification Agent checks whether action evidence overlaps with the source document and whether unsafe claims appear. The Redaction Agent sanitizes final display.

## MCP Tools

The MCP server is more than a wrapper. It exposes five tools used in the normal pipeline:

`policy_lookup` searches the local resource pack for category guidance. `template_fetch` retrieves response templates by intent. `deadline_calculator` normalizes absolute and relative dates against the current date. `task_store` persists redacted action records with a session id into a local JSONL store. `safety_boundary_check` checks draft output for unsafe certainty, unsupported payment claims, and sensitive information.

These tool calls are visible in both CLI and Streamlit output. The eval suite also checks that the expected MCP tools were called for each case.

## Gemini Structured Extraction

Gemini is optional but integrated. `nextstep_agent/gemini_client.py` loads `GOOGLE_API_KEY` from environment variables or `.env`, requests JSON structured output, validates the result through `DocumentFacts`, and records metadata about whether Gemini or fallback extraction was used. Image files use Gemini multimodal extraction because scanned or photographed documents need visual understanding.

This design keeps the demo reliable. A judge can run everything without a key, then enable Gemini to show live structured extraction.

## Security And Redaction

Security is visible, not decorative. The project redacts email addresses, phone numbers, labeled identifiers, account-like long numbers, 12 digit ID-like sequences, simple addresses, and labeled names. The verifier checks drafts for unsupported payment, legal, or medical claims. The Streamlit app includes a clear warning that the tool provides organizational help only.

Task persistence also passes through redaction. Saved tasks do not store obvious raw account identifiers from source evidence.

The security model is intentionally humble. NextStep Agent does not claim to make a document safe in every jurisdiction or context. Instead, it visibly reduces common risks: exposing contact details, repeating account numbers, inventing completed payments, or drifting into professional advice. The draft language is conservative. It says what the user can verify or ask, not what has already happened. This is especially important for bills, medical reminders, and financial documents.

## Evaluation Results

The deterministic eval suite has ten cases: school notice, invoice, utility bill, appointment slip, NGO intake, rental maintenance notice, internship application deadline, medical appointment reminder, small business order request, and scholarship or college fee circular. Each case checks document type, action count, risk level, MCP tool coverage, redaction behavior, verification, and absence of unsafe claims.

The current result is 10 passed, 0 failed, with a score of 80/80. The runner prints a console table and writes `evals/eval_report.md`.

The evaluation cases are deliberately varied. Some are time-sensitive, like utility interruption and school permission slips. Some are administrative, like internship applications and scholarship circulars. Some are sensitive, like NGO intake and medical reminders. This mix forces the system to demonstrate more than one happy path. The evals also check MCP tool usage, so a passing score requires the pipeline to use tools rather than simply generating a plausible answer.

## Demo Scenarios

The main demo begins with a school notice. The trace shows all eight agents, the MCP calls, the deadline calculation, the medium risk assessment, the permission slip action, saved tasks, verification, and redaction. The second demo uses an invoice and shows valid JSON output. The Streamlit demo shows the same workflow through an upload-ready interface with tabs for facts, risk, MCP calls, next steps, draft, verification, final output, and saved tasks.

For the final video, the strongest story is to show the same source document moving through multiple representations. First, show the raw confusing school notice. Second, show the agent trace. Third, show the structured facts and deadline. Fourth, show MCP calls. Fifth, show redaction. Sixth, run evals. This makes the demo concrete: the judge can see the problem, the agent architecture, tool use, safety, and evaluation discipline in less than five minutes.

## Limitations

The project is not a production OCR system. Image extraction requires Gemini. Text-based PDFs work through `pypdf`, but scanned PDFs should be treated as image inputs. The local JSONL task store is demo-grade and not a multi-user database. The deterministic extractor is conservative and may miss unusual phrasing. The draft should be reviewed by a human before sending.

Another limitation is that current image support depends on Gemini. That is the right tradeoff for this phase because adding local OCR would increase dependency weight and distract from the agent architecture. In a production setting, the system should include OCR confidence scores, image quality warnings, multilingual support, and a user review step before any downstream action is saved or sent.

## Future Work

Next steps include richer OCR and multilingual fixtures, hosted task storage, a deployed public demo URL, stronger Gemini-vs-heuristic evaluation, and deeper ADK runner integration. The system could also add calendar export and email draft export after more safety review.

## What I Learned From The Course

The course emphasized that useful agents are not just bigger prompts. They need tools, state, safety boundaries, evaluation, and clear user experience. NextStep Agent made that concrete. MCP gives the agent grounded local capabilities. Structured schemas make handoffs inspectable. Evaluation fixtures catch regressions. Redaction and verification need to be first-class stages. The result is a small but complete agentic system that solves a real everyday problem while staying honest about its limits.
