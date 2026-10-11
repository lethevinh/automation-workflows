"""The triage pipeline: ingest -> route -> draft -> gate -> audit.

The core is deterministic and stdlib-only. Given an inbox folder, the router
configuration and an approval source it produces, for every message: one route,
one draft action, one audit row, and one gate outcome (sent or blocked).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from bo_triage_audit import AuditRow, BlockedRow, SentRow, gate, read_approvals
from bo_triage_config import TriageConfig
from bo_triage_draft import is_sensitive, render_action
from bo_triage_route import classify
from bo_triage_config import RouterConfig


@dataclass(frozen=True)
class RouteRow:
    """The routing decision record: one per message (AC a)."""

    source_file: str
    queue: str
    confidence: str
    classifier: str


@dataclass(frozen=True)
class RunResult:
    """Everything one pipeline run produced."""

    routes: list[RouteRow]
    audit: list[AuditRow]
    sent: list[SentRow]
    blocked: list[BlockedRow]

    @property
    def sensitive(self) -> int:
        return sum(1 for row in self.audit if is_sensitive(row.queue))


def parse_message(text: str) -> tuple[str, str]:
    """Split a message into ``(subject, body)``.

    The format is a header block of ``Key: value`` lines, then a blank line, then
    the body. Only the lines *before* the blank line are headers, so a body line
    that happens to contain a colon is never mistaken for a header. When no
    ``Subject`` header is present, the first body line stands in.
    """

    lines = text.splitlines()
    header_end = len(lines)
    for index, line in enumerate(lines):
        if not line.strip():
            header_end = index
            break

    subject = ""
    for line in lines[:header_end]:
        key, sep, value = line.partition(":")
        if sep and key.strip().lower() == "subject":
            subject = value.strip()
            break

    body_lines = lines[header_end + 1 :] if header_end < len(lines) else []
    body = "\n".join(body_lines).strip()

    if not subject:
        for line in body_lines:
            if line.strip():
                subject = line.strip()
                break

    return subject, body


def _inbox_files(inbox_dir: Path) -> list[Path]:
    if not inbox_dir.is_dir():
        return []
    return sorted(p for p in inbox_dir.iterdir() if p.is_file() and p.suffix == ".txt")


def run_pipeline(
    inbox_dir: Path,
    router: RouterConfig,
    config: TriageConfig,
    approvals_path: Path,
    as_of: str,
) -> RunResult:
    """Run the deterministic pipeline over every message in ``inbox_dir``."""

    approvals = read_approvals(approvals_path)
    routes: list[RouteRow] = []
    audit: list[AuditRow] = []
    sent: list[SentRow] = []
    blocked: list[BlockedRow] = []

    for path in _inbox_files(inbox_dir):
        source_file = path.name
        subject, body = parse_message(path.read_text(encoding="utf-8"))
        route = classify(subject, body, router)
        action = render_action(router, route.queue, subject)

        outcome, approval_id, reason = gate(source_file, approvals)

        routes.append(
            RouteRow(
                source_file=source_file,
                queue=route.queue,
                confidence=f"{route.confidence:.2f}",
                classifier=route.classifier,
            )
        )
        audit.append(
            AuditRow(
                source_file=source_file,
                queue=route.queue,
                action=action,
                needs_approval=config.send_policy.require_approval,
                outcome=outcome,
                approval_id=approval_id,
                routed_as_of=as_of,
            )
        )
        if outcome == "sent":
            sent.append(
                SentRow(
                    source_file=source_file,
                    queue=route.queue,
                    approval_id=approval_id,
                    sent_as_of=as_of,
                )
            )
        else:
            blocked.append(
                BlockedRow(source_file=source_file, queue=route.queue, reason=reason)
            )

    return RunResult(routes=routes, audit=audit, sent=sent, blocked=blocked)
