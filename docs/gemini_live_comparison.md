# Gemini Live Comparison

Gemini is optional in NextStep Agent. The deterministic path is the default reliability baseline, while Gemini adds structured extraction and image understanding when `GOOGLE_API_KEY` is available.

## Deterministic Fallback Behavior

Without `GOOGLE_API_KEY`:

- Text, Markdown, and text-based PDF inputs still run.
- The extraction metadata shows heuristic mode or Gemini fallback mode.
- Evals remain deterministic and fast.
- Image inputs show a clear message that image OCR requires Gemini.

Demo command:

```powershell
python -m nextstep_agent.agent demo_pack/demo_school_notice.txt --current-date 2026-07-02 --trace
```

## Gemini-Enhanced Behavior

With `GOOGLE_API_KEY` configured:

- `--use-gemini` asks Gemini for structured JSON matching `DocumentFacts`.
- The output is validated through Pydantic before the rest of the agent pipeline runs.
- If malformed JSON is returned for text, the system falls back safely.

Demo command:

```powershell
python -m nextstep_agent.agent demo_pack/demo_school_notice.txt --current-date 2026-07-02 --use-gemini --trace
```

## Image Input Behavior

Image files require Gemini:

```powershell
python -m nextstep_agent.agent path/to/document.png --current-date 2026-07-02 --use-gemini --trace
```

If the API key is unavailable, say in the video:

```text
Image extraction is intentionally gated behind Gemini. The rest of the project is fully demoable without an API key using deterministic text extraction.
```

## What To Show In The Video

If an API key is available:

1. Run the same sample once without Gemini.
2. Run it again with `--use-gemini`.
3. Point to `metadata.extraction.mode`.
4. Show that the downstream MCP, planning, verification, redaction, and task storage stages remain the same.

If an API key is not available:

1. Show deterministic extraction.
2. Show the fallback metadata.
3. Explain that this keeps the project reproducible for judges.
