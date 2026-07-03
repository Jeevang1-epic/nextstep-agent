# Deployment

NextStep Agent deploys as a Streamlit app and also runs locally without any API key through deterministic extraction.

Deployment status: complete.

Public Streamlit demo:

```text
PASTE_STREAMLIT_URL_HERE
```

## Local Run

```powershell
pip install -r requirements.txt
streamlit run app.py
```

Open the local URL shown by Streamlit, choose the school notice sample, and run the pipeline.

## Streamlit Community Cloud Deployment

Completed deployment path:

1. Repository pushed to GitHub.
2. Streamlit Community Cloud app created from the public repository.
3. Main file path set to `app.py`.
4. `requirements.txt` used from the repository root.
5. Deployed app tested with the school notice and invoice demo flows.
6. Public URL added to README, submission checklist, release notes, and writeup.

## Streamlit Secrets

Use `.streamlit/secrets.toml.example` as the local template only. For the deployed app, configure `GOOGLE_API_KEY` only through Streamlit Community Cloud secrets.

```toml
GOOGLE_API_KEY = "your_key_here"
NEXTSTEP_MODEL = "gemini-flash-latest"
```

Do not commit `.env`, `.streamlit/secrets.toml`, or any API key. The repository contains no committed secrets.

## Fallback Demo Without Gemini API Key

If no `GOOGLE_API_KEY` is configured, the demo still works:

- Pasted text, `.txt`, `.md`, and text-based `.pdf` inputs use deterministic extraction.
- The school notice, invoice, utility bill, and internship demo pack files run normally.
- Tests and deterministic evals remain reproducible.
- Gemini toggles show fallback metadata for text inputs.
- Image inputs show a clear message that Gemini is required for image OCR.

What to say during a demo without a key:

```text
Gemini is optional in this release candidate. The deterministic text pipeline is the reproducible baseline for judges, and image extraction is gracefully gated behind Gemini when an API key is available.
```

## Final Deployment Checklist

- `python scripts/final_qa.py` passes locally.
- `python -m pytest -q` passes.
- `python evals/run_evals.py` reports 10/10 and 80/80.
- `streamlit run app.py` starts locally.
- `.env` is not committed.
- `.streamlit/secrets.toml` is not committed.
- `data/tasks.jsonl` is not committed.
- Public Streamlit app loads at `PASTE_STREAMLIT_URL_HERE`.
- School notice sample works in the deployed app.
- Invoice sample works in the deployed app.
- Agent trace, MCP calls, verification, and redaction are visible.
- Public app URL is added to `README.md`, `SUBMISSION_CHECKLIST.md`, release notes, and writeup.
