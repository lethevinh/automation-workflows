"""Extractor unit tests — confidence and the reasons behind it."""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path

from invoice_ledger_extract import extract_record, normalize_date, parse_amount
from invoice_ledger_parse import parse_document

INBOX = Path(__file__).resolve().parent.parent / "fixtures" / "inbox"


def _extract(name: str):
    text = (INBOX / name).read_text(encoding="utf-8")
    return extract_record(parse_document(text, name))


def test_clean_invoice_is_high_confidence() -> None:
    record = _extract("01-invoice-acme.txt")
    assert record.confidence == "high"
    assert record.reasons == ()
    assert record.amount is not None and record.amount == 1250
    assert record.vendor == "ACME Facilities Co"
    assert record.document_kind == "invoice"


def test_missing_number_is_low_confidence_with_reason() -> None:
    record = _extract("05-invoice-no-number.txt")
    assert record.confidence == "low"
    assert "missing invoice number" in record.reasons


def test_unparseable_amount_is_low_confidence() -> None:
    record = _extract("06-receipt-bad-amount.txt")
    assert record.amount is None
    assert "amount not parseable" in record.reasons


def test_unparseable_date_is_low_confidence() -> None:
    record = _extract("07-invoice-bad-date.txt")
    assert record.issue_date == ""
    assert record.due_date == ""
    assert "issue date not parseable" in record.reasons


def test_euro_receipt_parses_with_currency() -> None:
    record = _extract("09-receipt-initech.txt")
    assert record.confidence == "high"
    assert record.amount is not None and record.amount == 120
    assert record.currency == "EUR"


def test_parse_amount_forms() -> None:
    assert parse_amount("$1,250.00") == 1250
    assert parse_amount("€120.00") == 120
    assert parse_amount("USD 86.40") == Decimal("86.40")
    assert parse_amount("about $55") is None
    assert parse_amount("") is None
    assert parse_amount("-12") is None


def test_normalize_date_forms() -> None:
    assert normalize_date("2026-08-01") == "2026-08-01"
    assert normalize_date("2026/08/01") == "2026-08-01"
    assert normalize_date("2026.08.01") == "2026-08-01"
    assert normalize_date("01 Aug 2026") == "2026-08-01"
    assert normalize_date("soon") == ""