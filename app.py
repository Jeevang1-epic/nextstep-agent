from __future__ import annotations

from datetime import date
from io import BytesIO

import streamlit as st

from nextstep_agent.agent import format_trace, run_pipeline
from nextstep_agent.config import get_settings
from nextstep_agent.document_loader import DocumentLoadError


def _read_upload(uploaded_file) -> str:
    suffix = "." + uploaded_file.name.rsplit(".", 1)[-1].lower() if "." in uploaded_file.name else ""
    if suffix in {".txt", ".md"}:
        return uploaded_file.getvalue().decode("utf-8")
    if suffix == ".pdf":
        try:
            from pypdf import PdfReader
        except Exception as exc:
            raise DocumentLoadError(
                "PDF uploads require pypdf. Install requirements.txt or paste extracted text."
            ) from exc
        reader = PdfReader(BytesIO(uploaded_file.getvalue()))
        pages = [(page.extract_text() or "").strip() for page in reader.pages]
        text = "\n\n".join(page for page in pages if page)
        if not text:
            raise DocumentLoadError("No extractable text was found in this PDF. OCR is planned for a later phase.")
        return text
    raise DocumentLoadError("Upload a .txt, .md, or text-based .pdf file.")


st.set_page_config(page_title="NextStep Agent", layout="wide")
st.title("NextStep Agent")
st.caption("Turn confusing documents into safe, verified next steps.")

settings = get_settings()

with st.sidebar:
    st.subheader("Run Settings")
    selected_date = st.date_input("Current date", value=date.today())
    use_gemini = st.toggle("Use Gemini if API key is available", value=False)
    show_trace = st.toggle("Show agent trace", value=True)
    if use_gemini and not settings.gemini_available:
        st.info("GOOGLE_API_KEY is not configured. The app will use deterministic extraction.")

uploaded_file = st.file_uploader("Upload a document", type=["txt", "md", "pdf"])
pasted_text = st.text_area("Or paste document text", height=220)
run_clicked = st.button("Run NextStep Agent", type="primary")

if run_clicked:
    try:
        document_text = _read_upload(uploaded_file) if uploaded_file else pasted_text
        if not document_text.strip():
            st.warning("Paste text or upload a document before running.")
            st.stop()

        result = run_pipeline(
            document_text=document_text,
            current_date=selected_date.isoformat(),
            use_gemini=use_gemini,
        )

        facts_tab, risk_tab, plan_tab, draft_tab, verify_tab, final_tab, trace_tab = st.tabs(
            [
                "Extracted facts",
                "Risk assessment",
                "Next steps",
                "Draft",
                "Verification",
                "Redacted output",
                "MCP calls",
            ]
        )

        with facts_tab:
            st.json(result.facts.model_dump(mode="json"))
        with risk_tab:
            st.json(result.risk.model_dump(mode="json"))
        with plan_tab:
            st.table([item.model_dump(mode="json") for item in result.plan.action_items])
            st.write("Resources:", result.plan.resources)
        with draft_tab:
            st.subheader(result.draft.subject)
            st.text(result.draft.body)
            st.write("Checklist")
            st.write(result.draft.checklist)
        with verify_tab:
            st.json(result.verification.model_dump(mode="json"))
        with final_tab:
            st.text(result.redacted_output)
        with trace_tab:
            st.write(result.metadata.get("mcp_calls", []))
            if show_trace:
                st.text(format_trace(result))
    except DocumentLoadError as exc:
        st.error(str(exc))
    except Exception as exc:
        st.error(f"Run failed: {exc}")
