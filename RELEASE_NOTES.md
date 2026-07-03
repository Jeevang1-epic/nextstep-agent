# Release Notes

## v0.1.0 Release Candidate

NextStep Agent is ready as a Kaggle AI Agents Intensive capstone release candidate.

Public Streamlit demo:

```text
PASTE_STREAMLIT_URL_HERE
```

## Features Completed

- Multi-agent document-to-action pipeline.
- Google ADK-aligned agent definitions with deterministic local execution.
- Optional Gemini structured extraction with fallback mode.
- Optional Gemini image extraction gate for `.png`, `.jpg`, and `.jpeg`.
- MCP-backed local tools for policy lookup, templates, deadlines, task storage, and safety checks.
- Traceable CLI and Streamlit demo surfaces.
- Redaction for common sensitive fields.
- Verification against unsupported payment, legal, or medical claims.
- Persistent local JSONL task storage.
- Ten deterministic evaluation scenarios with 80/80 score.
- Streamlit deployment verified on Community Cloud.
- Streamlit secrets path documented; no API keys are committed.
- Kaggle writeup draft, demo script, media prompts, and golden demo snapshots.

## Known Limitations

- Gemini image extraction requires `GOOGLE_API_KEY`.
- Scanned PDFs should be treated as image inputs.
- Local JSONL task storage is suitable for demo use, not hosted multi-user production.
- Deterministic extraction is conservative and may miss unusual wording.
- The project gives organizational help only, not legal, medical, or financial advice.

## Validation Results

- `python -m pytest -q` -> 19 passed.
- `python -m compileall nextstep_agent mcp_server` -> passed.
- `python evals/run_evals.py` -> 10 passed, 0 failed, 80/80.
- `python -m nextstep_agent.agent demo_pack/demo_school_notice.txt --current-date 2026-07-02 --trace` -> passed.
- `python -m nextstep_agent.agent demo_pack/demo_invoice.txt --current-date 2026-07-02 --json` -> passed.
- `python scripts/final_qa.py` -> passed.
- Streamlit local start verified.
- Streamlit Community Cloud deployment verified at `PASTE_STREAMLIT_URL_HERE`.

## Submission Readiness

Ready for final manual steps:

- Record and upload demo video.
- Submit Kaggle writeup.
- Add final links to `SUBMISSION_CHECKLIST.md`.
