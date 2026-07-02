# Deployment

NextStep Agent deploys as a Streamlit app and also runs locally without any API key through deterministic extraction.

## Local Run

```powershell
pip install -r requirements.txt
streamlit run app.py
```

Open the local URL shown by Streamlit, choose the school notice sample, and run the pipeline.

## Manual Streamlit Community Cloud Deployment

1. Push the repository to GitHub.
2. Go to Streamlit Community Cloud.
3. Choose **New app**.
4. Select the public GitHub repository.
5. Select the main branch.
6. Set the main file path to `app.py`.
7. Confirm `requirements.txt` is at the repository root.
8. Open app secrets or advanced settings.
9. Add `GOOGLE_API_KEY` only if Gemini is available.
10. Optionally add `NEXTSTEP_MODEL = "gemini-flash-latest"`.
11. Deploy the app.
12. Test the deployed app with `demo_pack/demo_school_notice.txt` or the built-in sample dropdown.
13. Confirm the page shows extracted facts, risk, MCP calls, next steps, verification, redaction, and saved task metadata.
14. Copy the deployed URL into `README.md` and `SUBMISSION_CHECKLIST.md`.

Placeholder to replace after deployment:

```text
STREAMLIT_PUBLIC_URL_HERE
```

## Streamlit Secrets

Use `.streamlit/secrets.toml.example` as the local template:

```toml
GOOGLE_API_KEY = "your_key_here"
NEXTSTEP_MODEL = "gemini-flash-latest"
```

Do not commit `.streamlit/secrets.toml`. In Streamlit Community Cloud, paste secrets into the app settings, not into the repository.

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
- Public Streamlit app loads.
- School notice sample works in the deployed app.
- Public app URL is added to `README.md` and `SUBMISSION_CHECKLIST.md`.
