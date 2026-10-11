"""The idempotent CSV ledger, the review file, and the chase-draft writer.

Idempotency is the point: the ledger is keyed by a :func:`dedupe_key` derived
from the document itself, so re-running over the same inbox appends nothing and
the row count is unchanged. Low-confidence items never reach the ledger — they
are written to the review file with their reasons instead. Chase drafts are
written to disk and never sent.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from pathlib import Path

from invoice_ledger_extract import ExtractedRecord

LEDGER_COLUMNS = (
    "dedupe_key",
    "document_kind",
    "vendor",
    "reference",
    "issue_date",
    "due_date",
    "amount",
    "currency",
    "status",
    "source_file",
)
REVIEW_COLUMNS = (
    "source_file",
    "document_kind",
    "vendor",
    "reference",
    "issue_date",
    "amount",
    "currency",
    "reasons",
)

POSTED = "posted"


@dataclass(frozen=True)
class LedgerRow:
    """One posted ledger line."""

    dedupe_key: str
    document_kind: str
    vendor: str
    reference: str
    issue_date: str
    due_date: str
    amount: Decimal | None
    currency: str
    status: str
    source_file: str


def format_amount(amount: Decimal | None) -> str:
    """Render an amount for CSV, or ``""`` when unknown."""
    return "" if amount is None else f"{amount:.2f}"


def dedupe_key(record: ExtractedRecord) -> str:
    """Stable identity of a document: vendor + reference, else vendor/date/amount."""
    vendor = record.vendor.strip().lower()
    if record.reference:
        return f"{vendor}|{record.reference}"
    return f"{vendor}|{record.issue_date}|{format_amount(record.amount)}|{record.currency}"


def build_row(record: ExtractedRecord, status: str = POSTED) -> LedgerRow:
    """Build the ledger row for a clean, postable record."""
    return LedgerRow(
        dedupe_key=dedupe_key(record),
        document_kind=record.document_kind,
        vendor=record.vendor,
        reference=record.reference,
        issue_date=record.issue_date,
        due_date=record.due_date,
        amount=record.amount,
        currency=record.currency,
        status=status,
        source_file=record.source_file,
    )


class Ledger:
    """A CSV ledger that appends only unseen dedupe keys."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self._rows: dict[str, LedgerRow] = {}
        self._load()

    def _load(self) -> None:
        if not self.path.exists():
            return
        with self.path.open(newline="", encoding="utf-8") as handle:
            for raw in csv.DictReader(handle):
                amount_text = (raw.get("amount") or "").strip()
                row = LedgerRow(
                    dedupe_key=raw.get("dedupe_key", ""),
                    document_kind=raw.get("document_kind", ""),
                    vendor=raw.get("vendor", ""),
                    reference=raw.get("reference", ""),
                    issue_date=raw.get("issue_date", ""),
                    due_date=raw.get("due_date", ""),
                    amount=Decimal(amount_text) if amount_text else None,
                    currency=raw.get("currency", ""),
                    status=raw.get("status", POSTED),
                    source_file=raw.get("source_file", ""),
                )
                self._rows[row.dedupe_key] = row

    def add(self, row: LedgerRow) -> bool:
        """Store ``row``; return ``False`` when its key is already present."""
        if row.dedupe_key in self._rows:
            return False
        self._rows[row.dedupe_key] = row
        return True

    def write(self) -> None:
        """Write every row, sorted by issue date then key, for a stable file."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        ordered = sorted(self._rows.values(), key=lambda row: (row.issue_date, row.dedupe_key))
        with self.path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(LEDGER_COLUMNS))
            writer.writeheader()
            for row in ordered:
                writer.writerow(
                    {
                        "dedupe_key": row.dedupe_key,
                        "document_kind": row.document_kind,
                        "vendor": row.vendor,
                        "reference": row.reference,
                        "issue_date": row.issue_date,
                        "due_date": row.due_date,
                        "amount": format_amount(row.amount),
                        "currency": row.currency,
                        "status": row.status,
                        "source_file": row.source_file,
                    }
                )

    @property
    def row_count(self) -> int:
        return len(self._rows)


def write_review(path: Path, entries: list[tuple[ExtractedRecord, tuple[str, ...]]]) -> None:
    """Write low-confidence items with their reasons (one row each)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(REVIEW_COLUMNS))
        writer.writeheader()
        for record, reasons in entries:
            writer.writerow(
                {
                    "source_file": record.source_file,
                    "document_kind": record.document_kind,
                    "vendor": record.vendor,
                    "reference": record.reference,
                    "issue_date": record.issue_date,
                    "amount": format_amount(record.amount),
                    "currency": record.currency,
                    "reasons": "; ".join(reasons),
                }
            )


def write_chase_draft(drafts_dir: Path, record: ExtractedRecord, as_of: date) -> Path | None:
    """Write a never-sent payment-chase draft for an overdue invoice."""
    if record.document_kind != "invoice" or not record.reference:
        return None
    drafts_dir.mkdir(parents=True, exist_ok=True)
    path = drafts_dir / f"chase-{record.reference}.txt"
    amount = f"{format_amount(record.amount)} {record.currency}".strip()
    path.write_text(
        f"Subject: Payment reminder — {record.reference}\n"
        "\n"
        f"Hi {record.vendor},\n"
        "\n"
        f"Our records show invoice {record.reference} for {amount}, dated "
        f"{record.issue_date} and due {record.due_date}, was still unpaid as of "
        f"{as_of.isoformat()}.\n"
        "\n"
        "If payment has already been sent, please ignore this note — the ledger "
        "stays current either way.\n"
        "\n"
        "Thanks,\n",
        encoding="utf-8",
    )
    return path