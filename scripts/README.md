# Scripts

## Final QA

Run the release-candidate quality gate:

```powershell
python scripts/final_qa.py
```

The script runs:

- `python -m pytest -q`
- `python -m compileall nextstep_agent mcp_server`
- `python evals/run_evals.py`
- sample school notice CLI trace
- sample invoice JSON CLI output

It does not start Streamlit, so it finishes cleanly on Windows and Linux.
