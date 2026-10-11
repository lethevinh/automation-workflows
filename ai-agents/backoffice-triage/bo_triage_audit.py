"""The audit trail and the approval gate.

Two responsibilities live here:

* **One audit row per routed message** — written by the pipeline for every
  message it routes, sent or blocked.
* **The approval gate** — an outbound action is joined to the approval source by
  the message's ``source_file``. A message with a matching approval row is sent;
  a message without one is blocked. There is no auto-send path: the gate is
  structural, not a flag.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AuditRow:
    """One audit row per routed message."""

    source_file: str
    queue: str
    action: str
    needs_approval: bool
    outcome: str
    approval_id: str
    routed_as_of: str


@dataclass(frozen=True)
class SentRow:
    """A sent action (its approval row exists)."""

    source_file: str
    queue: str
    approval_id: str
    sent_as_of: str


@dataclass(frozen=True)
class BlockedRow:
    """A blocked action (no approval row)."""

    source_file: str
    queue: str
    reason: str


def read_approvals(path: Path) -> dict[str, str]:
    """Read the approval source into a ``source_file -> approval_id`` map.

    A missing file is an empty map, not an error: with no approvals, every
    message is blocked — which is exactly the safe default.
    """

    if not path.is_file():
        return {}
    approvals: dict[str, str] = {}
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            source_file = (row.get("source_file") or "").strip()
            approval_id = (row.get("approval_id") or "").strip()
            if source_file and approval_id:
                approvals[source_file] = approval_id
    return approvals


def gate(source_file: str, approvals: dict[str, str]) -> tuple[str, str, str]:
    """Decide the outcome of one action.

    Returns ``(outcome, approval_id, reason)``. A message is **sent** only when
    its ``source_file`` names a row in ``approvals``; otherwise it is
    **blocked** with a reason. This is the single place an action may be
    released, so no code path can send without an approval row.
    """

    approval_id = approvals.get(source_file, "")
    if approval_id:
        return "sent", approval_id, ""
    return "blocked", "", "no approval row"


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    """Write ``rows`` to ``path`` with a stable header and row order."""

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def read_csv_rows(path: Path) -> list[list[str]]:
    """Read a CSV into a list of raw rows, for exact comparison."""

    if not path.is_file():
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return [row for row in csv.reader(handle)]
