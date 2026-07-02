from nextstep_agent.redaction import redact_text


def test_redacts_common_sensitive_fields() -> None:
    text = (
        "Student: Maya Patel\n"
        "Student ID: STU-81245\n"
        "Email trips@greenfield.example or call 555-214-8890.\n"
        "Account Number: 7788-2219-004"
    )

    result = redact_text(text)

    assert "Maya Patel" not in result.text
    assert "STU-81245" not in result.text
    assert "trips@greenfield.example" not in result.text
    assert "555-214-8890" not in result.text
    assert "7788-2219-004" not in result.text
    assert "[REDACTED_NAME]" in result.text
    assert "[REDACTED_IDENTIFIER]" in result.text
    assert "[REDACTED_EMAIL]" in result.text
    assert "[REDACTED_PHONE]" in result.text


def test_redaction_preserves_amounts() -> None:
    text = "Amount due: $342.50 by July 12, 2026."

    result = redact_text(text)

    assert "$342.50" in result.text
    assert "July 12, 2026" in result.text
    assert result.findings == []
