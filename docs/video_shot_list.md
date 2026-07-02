# Video Shot List

Target runtime: 4-5 minutes.

## Recording Order

| Shot | What to show | Purpose | Approx. time |
| --- | --- | --- | --- |
| 1 | GitHub README top section | Establish project, tagline, and judge positioning | 0:00-0:25 |
| 2 | Competition alignment table | Show capstone proof points quickly | 0:25-0:55 |
| 3 | Streamlit app landing view | Show interactive demo readiness | 0:55-1:25 |
| 4 | School notice CLI trace | Show the full agent pipeline | 1:25-2:10 |
| 5 | MCP tool calls in trace or app | Prove MCP tools are used in the workflow | 2:10-2:45 |
| 6 | Invoice JSON output or Streamlit cards | Show structured `FinalResponse` output | 2:45-3:15 |
| 7 | Redaction and verification sections | Show safety and source-grounding controls | 3:15-3:45 |
| 8 | Eval report | Show 10/10 scenarios and 80/80 deterministic score | 3:45-4:15 |
| 9 | Architecture diagram | Explain why this is an agent system | 4:15-4:40 |
| 10 | README tagline or closing slide | End with impact and scope | 4:40-5:00 |

## Pre-Recording Checks

- Run `python scripts/final_qa.py`.
- Confirm the repo has no uncommitted secrets.
- Keep terminal output zoomed for readability.
- Close unrelated browser tabs and file explorer windows.
- Use the fictional files in `demo_pack/`.
- Avoid showing `.env`, Streamlit secrets, or personal directories.

## Demo Commands

```powershell
python -m nextstep_agent.agent demo_pack/demo_school_notice.txt --current-date 2026-07-02 --trace
python -m nextstep_agent.agent demo_pack/demo_invoice.txt --current-date 2026-07-02 --json
python evals/run_evals.py
streamlit run app.py
```

## Optional Gemini Shot

Only include this if `GOOGLE_API_KEY` is available and the output is clean:

```powershell
python -m nextstep_agent.agent demo_pack/demo_school_notice.txt --current-date 2026-07-02 --use-gemini --trace
```

Show `metadata.extraction.mode` and explain that deterministic fallback remains the reliable baseline.
