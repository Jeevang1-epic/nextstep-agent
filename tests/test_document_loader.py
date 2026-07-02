from pathlib import Path

import pytest

from nextstep_agent.document_loader import DocumentLoadError, load_document, load_document_input


def test_loads_txt_file(tmp_path: Path) -> None:
    document = tmp_path / "notice.txt"
    document.write_text("Payment due by July 12, 2026.", encoding="utf-8")

    assert load_document(document) == "Payment due by July 12, 2026."


def test_loads_md_file(tmp_path: Path) -> None:
    document = tmp_path / "notice.md"
    document.write_text("# Notice\nBring form tomorrow.", encoding="utf-8")

    assert "Bring form" in load_document(document)


def test_direct_text_wins_over_path(tmp_path: Path) -> None:
    document = tmp_path / "notice.txt"
    document.write_text("file text", encoding="utf-8")

    assert load_document_input(str(document), direct_text="pasted text") == "pasted text"


def test_unsupported_file_extension(tmp_path: Path) -> None:
    document = tmp_path / "notice.docx"
    document.write_text("legacy document", encoding="utf-8")

    with pytest.raises(DocumentLoadError):
        load_document(document)
