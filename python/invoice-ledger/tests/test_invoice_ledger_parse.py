"""Parser unit tests — the input contract of the demo fixtures."""

from __future__ import annotations

from pathlib import Path

from invoice_ledger_parse import parse_document

INBOX = Path(__file__).resolve().parent.parent / "fixtures" / "inbox"


def _parse(name: str):
    return parse_document((INBOX / name).read_text(encoding="utf-8"), name)


def test_kind_inferred_from_document_number() -> None:
    assert _parse("01-invoice-acme.txt").kind_hint == "invoice"
    assert _parse("02-receipt-globex.txt").kind_hint == "receipt"


def test_kind_inferred_from_text_when_no_number() -> None:
    raw = _parse("05-invoice-no-number.txt")
    assert raw.kind_hint == "invoice"
    assert "invoice_no" not in raw.kv


def test_fields_extracted_from_body() -> None:
    raw = _parse("01-invoice-acme.txt")
    assert raw.kv["invoice_no"] == "INV-1001"
    assert raw.kv["issue_date"] == "2026-08-01"
    assert raw.kv["due_date"] == "2026-08-31"
    assert raw.kv["amount"] == "$1,250.00"


def test_email_headers_are_never_document_fields() -> None:
    raw = _parse("02-receipt-globex.txt")
    assert "from" not in raw.kv
    assert raw.kv["receipt_no"] == "RCT-2001"


def test_currency_label_is_captured() -> None:
    raw = _parse("09-receipt-initech.txt")
    assert raw.kv["currency"] == "EUR"