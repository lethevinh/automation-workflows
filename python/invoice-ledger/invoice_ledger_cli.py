#!/usr/bin/env python3
"""invoice-ledger — parse invoices & receipts into an idempotent CSV ledger.

The production lane watches a folder of plain-text messages::

    invoice-ledger --inbox ./inbox --ledger ./ledger.csv

The credential-free demo lane runs the same pipeline on the bundled fixtures
with a fixed ``as_of`` date, writes its output to ``./demo-out/`` and asserts
the ledger matches ``fixtures/expected/ledger.csv``::

    invoice-ledger --demo

The demo makes no network call and needs no credentials; exit code 0 means
the emitted ledger exactly matched the expected one.
"""

from __future__ import annotations

import argparse
import csv
from datetime import date, datetime
from pathlib import Path

from invoice_ledger_core import run_pipeline

HERE = Path(__file__).resolve().parent
DEMO_AS_OF = date(2026, 9, 30)
DEMO_OUT_DIR = "demo-out"
_VERSION = "invoice-ledger 0.1.0"


def _parse_as_of(value: str) -> date:
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError as error:
        raise argparse.ArgumentTypeError(f"expected YYYY-MM-DD, got {value!r}") from error


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="invoice-ledger",
        description=(
            "Parse invoices and receipts into an idempotent CSV ledger; "
            "low-confidence items go to a review file, overdue invoices get a "
            "draft chase."
        ),
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="run the credential-free demo on the bundled fixtures",
    )
    parser.add_argument("--inbox", type=Path, help="folder of plain-text invoice/receipt messages")
    parser.add_argument("--ledger", type=Path, default=Path("ledger.csv"), help="ledger CSV path")
    parser.add_argument("--review", type=Path, default=Path("review.csv"), help="review CSV path")
    parser.add_argument(
        "--drafts", type=Path, default=Path("drafts"), help="chase-draft output dir"
    )
    parser.add_argument(
        "--as-of",
        type=_parse_as_of,
        default=date.today(),
        help="date to judge overdue against (YYYY-MM-DD)",
    )
    parser.add_argument("--version", action="version", version=_VERSION)
    return parser


def _print_ledger(path: Path) -> None:
    if not path.exists():
        print("  (no ledger written)")
        return
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            print(
                f"  {row.get('issue_date', ''):<10} {row.get('document_kind', ''):<8} "
                f"{row.get('vendor', ''):<24} {row.get('reference', ''):<10} "
                f"{row.get('amount', ''):>10} {row.get('currency', ''):<4} "
                f"{row.get('source_file', '')}"
            )


def _print_review(path: Path) -> None:
    if not path.exists():
        print("  (no review file)")
        return
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            print(
                f"  {row.get('source_file', ''):<32} {row.get('reference', ''):<10} "
                f"{row.get('reasons', '')}"
            )


def _ledgers_match(actual: Path, expected: Path) -> bool:
    def rows(path: Path) -> list[list[str]]:
        with path.open(newline="", encoding="utf-8") as handle:
            return sorted(row for row in csv.reader(handle) if row)

    return rows(actual) == rows(expected)


def _run_demo() -> int:
    out = Path.cwd() / DEMO_OUT_DIR
    inbox = HERE / "fixtures" / "inbox"
    expected = HERE / "fixtures" / "expected" / "ledger.csv"
    report, verdicts = run_pipeline(
        inbox,
        out / "ledger.csv",
        out / "review.csv",
        out / "drafts",
        DEMO_AS_OF,
    )

    print(f"invoice-ledger demo — inbox fixtures/inbox, as-of {DEMO_AS_OF.isoformat()}")
    print(f"{'file':<34} {'verdict':<9} detail")
    for verdict in verdicts:
        print(f"  {verdict.source_file:<32} {verdict.verdict:<9} {verdict.detail}")

    print("\nledger:")
    _print_ledger(out / "ledger.csv")
    print("\nreview (low-confidence, with reasons):")
    _print_review(out / "review.csv")
    print(f"\ndigest: {report.digest()}")

    if _ledgers_match(out / "ledger.csv", expected):
        print("RESULT: PASS - the demo ledger exactly matches fixtures/expected/ledger.csv.")
        return 0
    print("RESULT: FAIL - the demo ledger differs from fixtures/expected/ledger.csv.")
    return 1


def _run_production(args: argparse.Namespace) -> int:
    report, _ = run_pipeline(args.inbox, args.ledger, args.review, args.drafts, args.as_of)
    print(f"invoice-ledger — inbox {args.inbox}, as-of {args.as_of.isoformat()}")
    print(f"ledger: {report.ledger_path} ({report.ledger_rows} rows)")
    print(f"review: {report.review_path}")
    print(f"digest: {report.digest()}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.demo:
        return _run_demo()
    if args.inbox is None:
        parser.error("either --demo or --inbox DIR is required")
    return _run_production(args)


if __name__ == "__main__":
    raise SystemExit(main())