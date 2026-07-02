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


def test_redacts_long_account_like_numbers_and_12_digit_ids() -> None:
    text = "Reference 123456789012 and account-like value 9988776655443322."

    result = redact_text(text)

    assert "123456789012" not in result.text
    assert "9988776655443322" not in result.text
    assert any(finding.label in {"ID_12_DIGIT", "LONG_NUMBER"} for finding in result.findings)


def test_redacts_simple_address() -> None:
    text = "Service address: 1400 Lake Road Apt 5"

    result = redact_text(text)

    assert "1400 Lake Road" not in result.text
    assert "[REDACTED_ADDRESS]" in result.text
