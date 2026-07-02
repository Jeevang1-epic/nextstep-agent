from __future__ import annotations

import os
import tempfile
from datetime import date
from io import BytesIO
from pathlib import Path

import streamlit as st

from nextstep_agent.agent import format_trace, run_pipeline
from nextstep_agent.config import get_settings
from nextstep_agent.document_loader import DocumentLoadError, LoadedDocument


ROOT_DIR = Path(__file__).resolve().parent
EXAMPLES = {
    "School notice": ROOT_DIR / "examples" / "sample_school_notice.txt",
    "Invoice": ROOT_DIR / "examples" / "sample_invoice.txt",
    "Utility bill": ROOT_DIR / "examples" / "sample_utility_bill.txt",
}
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg"}


def _load_streamlit_secrets() -> None:
    try:
        if "GOOGLE_API_KEY" in st.secrets and "GOOGLE_API_KEY" not in os.environ:
            os.environ["GOOGLE_API_KEY"] = str(st.secrets["GOOGLE_API_KEY"])
        if "NEXTSTEP_MODEL" in st.secrets and "NEXTSTEP_MODEL" not in os.environ:
            os.environ["NEXTSTEP_MODEL"] = str(st.secrets["NEXTSTEP_MODEL"])
    except Exception:
        return


def _read_upload(uploaded_file, use_gemini: bool, gemini_available: bool) -> LoadedDocument:
    suffix = "." + uploaded_file.name.rsplit(".", 1)[-1].lower() if "." in uploaded_file.name else ""
    if suffix in {".txt", ".md"}:
        return LoadedDocument(
            text=uploaded_file.getvalue().decode("utf-8"),
            source_path=None,
            mime_type="text/markdown" if suffix == ".md" else "text/plain",
        )
    if suffix == ".pdf":
        try:
            from pypdf import PdfReader
        except Exception as exc:
            raise DocumentLoadError("PDF uploads require pypdf. Install requirements.txt or paste extracted text.") from exc
        reader = PdfReader(BytesIO(uploaded_file.getvalue()))
        pages = [(page.extract_text() or "").strip() for page in reader.pages]
        text = "\n\n".join(page for page in pages if page)
        if not text:
            raise DocumentLoadError("No extractable text was found in this PDF. Use Gemini image input for scans.")
        return LoadedDocument(text=text, source_path=None, mime_type="application/pdf")
    if suffix in IMAGE_SUFFIXES:
        if not use_gemini or not gemini_available:
            raise DocumentLoadError("Image OCR requires Gemini. Enable Gemini and configure GOOGLE_API_KEY.")
        temp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
        temp.write(uploaded_file.getvalue())
        temp.close()
        mime_type = "image/jpeg" if suffix in {".jpg", ".jpeg"} else "image/png"
        return LoadedDocument(
            text=f"Image document: {uploaded_file.name}",
            source_path=Path(temp.name),
            mime_type=mime_type,
            is_image=True,
        )
    raise DocumentLoadError("Upload a .txt, .md, .pdf, .png, .jpg, or .jpeg file.")


def _load_sample(label: str) -> str:
    if label == "None":
        return ""
    return EXAMPLES[label].read_text(encoding="utf-8")


_load_streamlit_secrets()
settings = get_settings()

st.set_page_config(page_title="NextStep Agent", layout="wide")
st.title("NextStep Agent")
st.caption("Turn confusing documents into safe, verified next steps.")
st.warning(
    "NextStep Agent provides organizational help only. It does not provide legal, medical, or financial advice."
)

with st.sidebar:
    st.subheader("Demo Commands")
    st.code("python -m nextstep_agent.agent examples/sample_school_notice.txt --current-date 2026-07-02 --trace")
    st.code("python -m nextstep_agent.agent examples/sample_invoice.txt --current-date 2026-07-02 --json")
    st.code("python evals/run_evals.py")

st.header("Upload Or Paste Document")
left, right = st.columns([2, 1])
with left:
    sample_choice = st.selectbox("Load sample document", ["None", *EXAMPLES.keys()])
    uploaded_file = st.file_uploader("Upload document", type=["txt", "md", "pdf", "png", "jpg", "jpeg"])
    pasted_text = st.text_area("Document text", value=_load_sample(sample_choice), height=260)
with right:
    selected_date = st.date_input("Current date", value=date.today())
    use_gemini = st.toggle("Use Gemini if API key is available", value=False)
    show_trace = st.toggle("Show agent trace", value=True)
    st.write("Gemini available:", "yes" if settings.gemini_available else "no")
    if use_gemini and not settings.gemini_available:
        st.info("GOOGLE_API_KEY is not configured. Text documents will use deterministic extraction.")

run_clicked = st.button("Run NextStep Agent", type="primary")

if run_clicked:
    try:
        document = (
            _read_upload(uploaded_file, use_gemini=use_gemini, gemini_available=settings.gemini_available)
            if uploaded_file
            else LoadedDocument(text=pasted_text)
        )
        if not document.text.strip():
            st.warning("Paste text, choose a sample, or upload a document before running.")
            st.stop()

        result = run_pipeline(
            document_text=document.text,
            current_date=selected_date.isoformat(),
            use_gemini=use_gemini,
            image_path=str(document.source_path) if document.is_image and document.source_path else None,
            image_mime_type=document.mime_type,
        )

        st.header("Agent Trace")
        if show_trace:
            st.text(format_trace(result))
        else:
            st.caption("Trace hidden. Enable the toggle to show stage-by-stage execution.")

        st.header("Extracted Facts")
        st.json(result.facts.model_dump(mode="json"))

        st.header("Risk And Priority")
        st.json(result.risk.model_dump(mode="json"))

        st.header("MCP Tool Calls")
        st.table(result.metadata.get("mcp_calls", []))

        st.header("Next-Step Plan")
        st.table([item.model_dump(mode="json") for item in result.plan.action_items])
        st.write("Resources:", result.plan.resources)

        st.header("Draft And Checklist")
        st.subheader(result.draft.subject)
        st.text(result.draft.body)
        st.write(result.draft.checklist)

        st.header("Verification")
        st.json(result.verification.model_dump(mode="json"))

        st.header("Redacted Final Output")
        st.text(result.redacted_output)

        st.header("Saved Tasks")
        saved = result.metadata.get("saved_tasks", {})
        st.write(f"Session: {result.metadata.get('session_id')}")
        st.write(f"Saved task count: {saved.get('stored_count', 0)}")
        st.write(f"Task store path: {saved.get('task_store_path', 'not available')}")
        st.table(saved.get("tasks", []))
    except DocumentLoadError as exc:
        st.error(str(exc))
    except Exception as exc:
        st.error(f"Run failed: {exc}")
