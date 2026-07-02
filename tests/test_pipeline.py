import json

from nextstep_agent.agent import format_trace, run_pipeline


def test_pipeline_returns_final_response_with_trace_metadata() -> None:
    result = run_pipeline(
        "Invoice No: INV-12345\nAmount due: $42.00\nPayment due by July 12, 2026.",
        current_date="2026-07-02",
    )

    payload = result.model_dump(mode="json")

    assert payload["facts"]["document_type"] == "invoice"
    assert payload["verification"]["passed"] is True
    assert payload["metadata"]["extraction"]["mode"] == "heuristic"
    assert result.metadata["mcp_calls"]
    assert result.metadata["saved_tasks"]["stored_count"] >= 1
    assert "Task store:" in result.redacted_output
    assert "Resource Lookup Agent" in format_trace(result)
    json.dumps(payload)


def test_gemini_flag_falls_back_without_key(monkeypatch) -> None:
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)

    result = run_pipeline(
        "School notice. Please return the signed form by July 8, 2026. Student ID: STU-111.",
        current_date="2026-07-02",
        use_gemini=True,
    )

    assert result.facts.document_type == "school_notice"
    assert result.metadata["extraction"]["mode"] == "heuristic_fallback"
    assert "GOOGLE_API_KEY" in result.metadata["extraction"]["fallback_reason"]


def test_labeled_account_number_is_not_contact_phone() -> None:
    result = run_pipeline(
        "Payment due by July 12, 2026. Account Number: 1234567890.",
        current_date="2026-07-02",
    )

    assert result.facts.identifiers == ["[REDACTED_IDENTIFIER]"]
    assert result.facts.contact_methods == []


def test_image_pipeline_requires_gemini_key(monkeypatch, tmp_path) -> None:
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    image_path = tmp_path / "notice.png"
    image_path.write_bytes(b"tiny image placeholder")

    try:
        run_pipeline(
            "Image document: notice.png",
            current_date="2026-07-02",
            use_gemini=True,
            image_path=str(image_path),
            image_mime_type="image/png",
        )
    except RuntimeError as exc:
        assert "Image OCR requires Gemini" in str(exc)
    else:
        raise AssertionError("Expected image pipeline to require Gemini without an API key.")
