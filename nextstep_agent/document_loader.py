from __future__ import annotations

import mimetypes
from dataclasses import dataclass
from pathlib import Path


SUPPORTED_TEXT_SUFFIXES = {".txt", ".md"}
SUPPORTED_IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg"}


@dataclass(frozen=True)
class LoadedDocument:
    text: str
    source_path: Path | None = None
    mime_type: str | None = None
    is_image: bool = False


class DocumentLoadError(ValueError):
    pass


def load_document(path: str | Path) -> str:
    return load_document_payload(path).text


def load_document_payload(path: str | Path, allow_image: bool = False) -> LoadedDocument:
    document_path = Path(path)
    if not document_path.exists():
        raise DocumentLoadError(f"Document path does not exist: {document_path}")
    if not document_path.is_file():
        raise DocumentLoadError(f"Document path is not a file: {document_path}")

    suffix = document_path.suffix.lower()
    if suffix in SUPPORTED_TEXT_SUFFIXES:
        return LoadedDocument(
            text=document_path.read_text(encoding="utf-8"),
            source_path=document_path,
            mime_type="text/markdown" if suffix == ".md" else "text/plain",
        )
    if suffix == ".pdf":
        return LoadedDocument(
            text=_load_pdf(document_path),
            source_path=document_path,
            mime_type="application/pdf",
        )
    if suffix in SUPPORTED_IMAGE_SUFFIXES:
        if not allow_image:
            raise DocumentLoadError("Image OCR requires Gemini. Re-run with --use-gemini and configure GOOGLE_API_KEY.")
        return LoadedDocument(
            text=f"Image document: {document_path.name}",
            source_path=document_path,
            mime_type=mimetypes.guess_type(document_path.name)[0] or "image/png",
            is_image=True,
        )
    raise DocumentLoadError(
        "Unsupported document type "
        f"'{suffix}'. Supported file types are .txt, .md, .pdf, .png, .jpg, and .jpeg."
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


def load_document_input_payload(
    path_or_text: str | None = None,
    direct_text: str | None = None,
    allow_image: bool = False,
) -> LoadedDocument:
    if direct_text and direct_text.strip():
        return LoadedDocument(text=direct_text)
    if not path_or_text:
        raise DocumentLoadError("Provide a document path or direct text.")

    candidate = Path(path_or_text)
    if candidate.exists():
        return load_document_payload(candidate, allow_image=allow_image)
    return LoadedDocument(text=path_or_text)


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
