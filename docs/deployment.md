# Deployment

NextStep Agent is deployable as a Streamlit app. It also runs locally without any API key by using deterministic extraction.

## Local Run

```powershell
pip install -r requirements.txt
streamlit run app.py
```

## Streamlit Community Cloud

1. Push the repository to GitHub.
2. In Streamlit Community Cloud, choose the GitHub repository and set the main file path to `app.py`.
3. Confirm that `requirements.txt` is present at the repository root.
4. Open Advanced settings and paste secret values in TOML format.
5. Deploy the app.

Streamlit's deployment docs describe the Community Cloud flow as creating an app from the workspace and filling in app information before deploying. Their secrets docs recommend storing sensitive values outside git and pasting local `secrets.toml` contents into Advanced settings.

## Secrets

Use `.streamlit/secrets.toml.example` as the template:

```toml
GOOGLE_API_KEY = "your_key_here"
NEXTSTEP_MODEL = "gemini-flash-latest"
```

Do not commit `.streamlit/secrets.toml`.

## Fallback Mode

If `GOOGLE_API_KEY` is missing:

- Text, Markdown, and text-based PDF inputs still run with deterministic extraction.
- Gemini extraction toggles show fallback metadata.
- Image inputs show a clear message that Gemini is required for OCR.

## Deployment Checklist

- `streamlit run app.py` starts locally.
- `python -m pytest -q` passes.
- `python evals/run_evals.py` reports 100 percent on deterministic fixtures.
- `.env` and `.streamlit/secrets.toml` are not committed.
- `GOOGLE_API_KEY` is configured only in local env or Streamlit Cloud secrets.
- The README demo commands match the deployed app behavior.
