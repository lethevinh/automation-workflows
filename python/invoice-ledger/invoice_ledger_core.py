"""Pipeline orchestration: inbox -> parse -> extract -> validate -> ledger.

The production lane and the demo lane are the same code path. A production
run points ``inbox`` at a watched folder; the demo points it at the bundled
``fixtures/inbox/`` and uses a fixed ``as_of`` date so every run is
deterministic. There is no network call anywhere in this module — the live
mailbox and LLM steps are documented owner-side integrations that feed text
into the same folder.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path

from invoice_ledger_extract import ExtractedRecord, extract_record
from invoice_ledger_ledger import (
    Ledger,
    build_row,
    write_chase_draft,
    write_review,
)
from invoice_ledger_parse import parse_document
from invoice_ledger_validate import extra_reasons


@dataclass(frozen=True)
class ItemVerdict:
    """One inbox file and the decision the pipeline made for it."""

    source_file: str
    verdict: str  # "posted" | "skipped" | "reviewed"
    detail: str


@dataclass(frozen=True)
class RunReport:
    """The machine-readable summary of one run."""

    posted: int
    skipped: int
    reviewed: int
    drafts: list[Path]
    ledger_path: Path
    review_path: Path
    ledger_rows: int

    def digest(self) -> str:
        return (
            f"posted={self.posted} skipped={self.skipped} "
            f"reviewed={self.reviewed} drafts={len(self.drafts)} "
            f"ledger_rows={self.ledger_rows}"
        )


def run_pipeline(
    inbox: Path,
    ledger_path: Path,
    review_path: Path,
    drafts_dir: Path,
    as_of: date,
) -> tuple[RunReport, list[ItemVerdict]]:
    """Process every file in ``inbox`` and write ledger, review and drafts."""
    ledger = Ledger(ledger_path)
    review_entries: list[tuple[ExtractedRecord, tuple[str, ...]]] = []
    verdicts: list[ItemVerdict] = []
    drafts: list[Path] = []
    posted = 0
    skipped = 0

    for path in sorted(inbox.iterdir()):
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        record = extract_record(parse_document(text, path.name))
        reasons = record.reasons + extra_reasons(record)
        if reasons:
            review_entries.append((record, reasons))
            verdicts.append(ItemVerdict(path.name, "reviewed", "; ".join(reasons)))
            continue

        row = build_row(record)
        if not ledger.add(row):
            skipped += 1
            verdicts.append(
                ItemVerdict(path.name, "skipped", f"duplicate of '{row.dedupe_key}'")
            )
            continue
        posted += 1
        verdicts.append(ItemVerdict(path.name, "posted", ""))
        if record.document_kind == "invoice" and record.due_date and record.amount is not None:
            if date.fromisoformat(record.due_date) < as_of:
                draft = write_chase_draft(drafts_dir, record, as_of)
                if draft is not None:
                    drafts.append(draft)

    ledger.write()
    write_review(review_path, review_entries)
    report = RunReport(
        posted=posted,
        skipped=skipped,
        reviewed=len(review_entries),
        drafts=drafts,
        ledger_path=ledger_path,
        review_path=review_path,
        ledger_rows=ledger.row_count,
    )
    return report, verdicts