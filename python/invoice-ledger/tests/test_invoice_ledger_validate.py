"""Validation, dedupe-key and ledger-row unit tests."""

from __future__ import annotations

from decimal import Decimal

from invoice_ledger_extract import ExtractedRecord
from invoice_ledger_ledger import build_row, dedupe_key
from invoice_ledger_validate import extra_reasons


def _record(**overrides) -> ExtractedRecord:
    base: dict = dict(
        source_file="x.txt",
        document_kind="invoice",
        vendor="Acme",
        reference="INV-1",
        issue_date="2026-08-01",
        due_date="2026-08-31",
        amount=Decimal("10.00"),
        currency="USD",
        confidence="high",
        reasons=(),
    )
    base.update(overrides)
    return ExtractedRecord(**base)


def test_clean_record_passes_validation() -> None:
    assert extra_reasons(_record()) == ()


def test_reference_with_spaces_fails_validation() -> None:
    assert "reference contains unsupported characters" in extra_reasons(_record(reference="INV 1"))


def test_overlong_vendor_fails_validation() -> None:
    assert "vendor name exceeds 80 characters" in extra_reasons(_record(vendor="A" * 81))


def test_dedupe_key_uses_reference_when_present() -> None:
    record = _record(vendor="Acme Co", reference="INV-1001")
    assert dedupe_key(record) == "acme co|INV-1001"


def test_dedupe_key_falls_back_to_amount_without_reference() -> None:
    record = _record(vendor="Acme Co", reference="")
    assert dedupe_key(record) == "acme co|2026-08-01|10.00|USD"


def test_build_row_is_posted_with_stable_key() -> None:
    row = build_row(_record())
    assert row.status == "posted"
    assert row.dedupe_key == "acme|INV-1"
    assert row.source_file == "x.txt"