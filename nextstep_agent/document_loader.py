from __future__ import annotations

from pathlib import Path


SUPPORTED_TEXT_SUFFIXES = {".txt", ".md"}


class DocumentLoadError(ValueError):
    pass


def load_document(path: str | Path) -> str:
    document_path = Path(path)
    if not document_path.exists():
        raise DocumentLoadError(f"Document path does not exist: {document_path}")
    if not document_path.is_file():
        raise DocumentLoadError(f"Document path is not a file: {document_path}")

    suffix = document_path.suffix.lower()
    if suffix in SUPPORTED_TEXT_SUFFIXES:
        return document_path.read_text(encoding="utf-8")
    if suffix == ".pdf":
        return _load_pdf(document_path)
    raise DocumentLoadError(
        f"Unsupported document type '{suffix}'. Supported file types are .txt, .md, and .pdf with pypdf installed."
    )


def load_document_input(path_or_text: str | None = None, direct_text: str | None = None) -> str:
    if direct_text and direct_text.strip():
        return direct_text
    if not path_or_text:
        raise DocumentLoadError("Provide a document path or direct text.")

    candidate = Path(path_or_text)
    if candidate.exists():
        return load_document(candidate)
    return path_or_text


def _load_pdf(path: Path) -> str:
    try:
        from pypdf import PdfReader
    except Exception as exc:
        raise DocumentLoadError(
            "PDF input requires the optional pypdf dependency. Install requirements.txt or paste extracted text."
        ) from exc

    reader = PdfReader(str(path))
    pages = [(page.extract_text() or "").strip() for page in reader.pages]
    text = "\n\n".join(page for page in pages if page)
    if not text:
        raise DocumentLoadError("No extractable text was found in the PDF. OCR for scanned images is planned later.")
    return text
