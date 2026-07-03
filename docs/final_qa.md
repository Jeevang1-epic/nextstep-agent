# Final QA

## Public Demo

```text
PASTE_STREAMLIT_URL_HERE
```

## Deployment Checks

- [x] Local app loaded.
- [x] Deployed app loaded.
- [ ] Gemini availability checked in the deployed app.
- [x] School notice sample tested.
- [x] Invoice sample tested.
- [x] Agent trace visible.
- [x] MCP tool calls visible.
- [x] Redaction visible.
- [x] No API key visible.
- [x] No secrets committed.

## Commands Run

```powershell
python -m pytest -q
python evals/run_evals.py
python scripts/final_qa.py
python -m compileall nextstep_agent mcp_server
git diff --check
```

## Expected Results

- Unit tests pass.
- Deterministic evals report 10/10 scenarios and 80/80 score.
- Final QA script passes.
- Package compileall passes.
- Git diff whitespace check passes.

## Notes

`GOOGLE_API_KEY`, if used, must be configured only through Streamlit Community Cloud secrets. The repository must not include `.env`, `.streamlit/secrets.toml`, or `data/tasks.jsonl`.
