"""End-to-end demo tests — acceptance criteria (a), (b) and (c)."""

from __future__ import annotations

import csv
import subprocess
import sys
from pathlib import Path

PACK_ROOT = Path(__file__).resolve().parent.parent
CLI = PACK_ROOT / "invoice_ledger_cli.py"
EXPECTED_LEDGER = PACK_ROOT / "fixtures" / "expected" / "ledger.csv"


def _run_demo(cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CLI), "--demo"],
        cwd=cwd,
        capture_output=True,
        text=True,
    )


def _csv_rows(path: Path) -> list[list[str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return [row for row in csv.reader(handle) if row]


def test_demo_emits_exact_expected_ledger(tmp_path: Path) -> None:
    result = _run_demo(tmp_path)
    assert result.returncode == 0, result.stdout + result.stderr
    actual = _csv_rows(tmp_path / "demo-out" / "ledger.csv")
    expected = _csv_rows(EXPECTED_LEDGER)
    assert actual == expected
    assert len(actual) == 5  # header + 4 posted rows


def test_demo_rerun_is_idempotent(tmp_path: Path) -> None:
    first = _run_demo(tmp_path)
    assert first.returncode == 0, first.stdout + first.stderr
    second = _run_demo(tmp_path)
    assert second.returncode == 0, second.stdout + second.stderr
    first_rows = _csv_rows(tmp_path / "demo-out" / "ledger.csv")
    second_rows = _csv_rows(tmp_path / "demo-out" / "ledger.csv")
    assert len(first_rows) == len(second_rows) == 5
    assert first_rows == second_rows


def test_demo_review_file_carries_each_reason(tmp_path: Path) -> None:
    result = _run_demo(tmp_path)
    assert result.returncode == 0, result.stdout + result.stderr
    review = tmp_path / "demo-out" / "review.csv"
    assert review.exists()
    rows = _csv_rows(review)
    assert len(rows) == 4  # header + 3 reviewed items
    for row in rows[1:]:
        assert row[-1], f"row has no reason: {row}"
    reasons = [row[-1] for row in rows[1:]]
    assert "missing invoice number" in reasons
    assert "amount not parseable" in reasons
    assert "issue date not parseable" in reasons


def test_demo_writes_exactly_one_chase_draft(tmp_path: Path) -> None:
    result = _run_demo(tmp_path)
    assert result.returncode == 0, result.stdout + result.stderr
    drafts = sorted((tmp_path / "demo-out" / "drafts").glob("chase-*.txt"))
    assert [d.name for d in drafts] == ["chase-INV-1001.txt"]
    text = drafts[0].read_text(encoding="utf-8")
    assert "Payment reminder" in text
    assert "INV-1001" in text
    assert "1250.00 USD" in text


def test_demo_stdout_passes_against_expected(tmp_path: Path) -> None:
    result = _run_demo(tmp_path)
    assert "RESULT: PASS" in result.stdout
    assert "posted=4 skipped=2 reviewed=3 drafts=1" in result.stdout