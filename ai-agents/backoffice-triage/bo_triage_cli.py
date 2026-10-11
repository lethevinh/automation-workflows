"""``bo-triage`` — route back-office messages, draft actions, gate every send.

The credential-free entry point is ``--mock-llm``: it runs the whole pipeline
offline over the bundled fixtures and self-verifies the four output files
against ``fixtures/expected/`` (exit 0 = PASS, exit 1 = a real difference).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from bo_triage_audit import (
    AuditRow,
    BlockedRow,
    SentRow,
    read_csv_rows,
    write_csv,
)
from bo_triage_config import ConfigError, load_config, load_router
from bo_triage_core import RouteRow, RunResult, run_pipeline

ROUTE_FIELDS = ["source_file", "queue", "confidence", "classifier"]
AUDIT_FIELDS = [
    "source_file",
    "queue",
    "action",
    "needs_approval",
    "outcome",
    "approval_id",
    "routed_as_of",
]
SENT_FIELDS = ["source_file", "queue", "approval_id", "sent_as_of"]
BLOCKED_FIELDS = ["source_file", "queue", "reason"]

PACK_DIR = Path(__file__).resolve().parent


def _route_rows(rows: list[RouteRow]) -> list[dict[str, str]]:
    return [
        {
            "source_file": row.source_file,
            "queue": row.queue,
            "confidence": row.confidence,
            "classifier": row.classifier,
        }
        for row in rows
    ]


def _audit_rows(rows: list[AuditRow]) -> list[dict[str, str]]:
    return [
        {
            "source_file": row.source_file,
            "queue": row.queue,
            "action": row.action,
            "needs_approval": str(row.needs_approval).lower(),
            "outcome": row.outcome,
            "approval_id": row.approval_id,
            "routed_as_of": row.routed_as_of,
        }
        for row in rows
    ]


def _sent_rows(rows: list[SentRow]) -> list[dict[str, str]]:
    return [
        {
            "source_file": row.source_file,
            "queue": row.queue,
            "approval_id": row.approval_id,
            "sent_as_of": row.sent_as_of,
        }
        for row in rows
    ]


def _blocked_rows(rows: list[BlockedRow]) -> list[dict[str, str]]:
    return [
        {"source_file": row.source_file, "queue": row.queue, "reason": row.reason}
        for row in rows
    ]


def _write_outputs(result: RunResult, out_dir: Path) -> dict[str, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    files = {
        "routes.csv": (ROUTE_FIELDS, _route_rows(result.routes)),
        "audit.csv": (AUDIT_FIELDS, _audit_rows(result.audit)),
        "sent.csv": (SENT_FIELDS, _sent_rows(result.sent)),
        "blocked.csv": (BLOCKED_FIELDS, _blocked_rows(result.blocked)),
    }
    written: dict[str, Path] = {}
    for name, (fields, rows) in files.items():
        path = out_dir / name
        write_csv(path, fields, rows)
        written[name] = path
    return written


def _verify(written: dict[str, Path], expected_dir: Path) -> list[str]:
    mismatches: list[str] = []
    for name, path in written.items():
        expected = read_csv_rows(expected_dir / name)
        actual = read_csv_rows(path)
        if actual != expected:
            mismatches.append(name)
    return mismatches


def _print_result(result: RunResult, out_dir: Path) -> None:
    print(f"back-office triage — mock LLM (deterministic), out {out_dir}")
    print(f"{'source_file':34} {'queue':9} {'conf':5} classifier")
    for route in result.routes:
        print(
            f"  {route.source_file:32} {route.queue:9} {route.confidence:5} {route.classifier}"
        )
    print()
    print(f"sent ({len(result.sent)}):")
    for sent_row in result.sent:
        print(f"  {sent_row.source_file:32} {sent_row.queue:9} approval {sent_row.approval_id}")
    print(f"blocked ({len(result.blocked)}):")
    for blocked_row in result.blocked:
        print(f"  {blocked_row.source_file:32} {blocked_row.queue:9} {blocked_row.reason}")
    print()
    print(
        "digest: "
        f"routed={len(result.routes)} "
        f"sent={len(result.sent)} "
        f"blocked={len(result.blocked)} "
        f"audit_rows={len(result.audit)} "
        f"sensitive={result.sensitive}"
    )


def run_lane(
    pack_dir: Path,
    inbox: Path,
    out_dir: Path,
    approvals: Path,
    verify: bool,
) -> int:
    """Run the pipeline over ``inbox``; self-verify only in the demo lane.

    ``verify`` is true only for ``--mock-llm``, where the outputs are asserted
    against ``fixtures/expected/``. Route mode (a real inbox) has no bundled
    expected file and never claims one.
    """

    config = load_config(pack_dir)
    router = load_router(pack_dir)
    result = run_pipeline(
        inbox_dir=inbox,
        router=router,
        config=config,
        approvals_path=approvals,
        as_of=config.demo_as_of,
    )
    written = _write_outputs(result, out_dir)
    _print_result(result, out_dir)

    if not verify:
        print()
        print("route mode: outputs written, no self-verify (that is the demo lane's job).")
        return 0

    expected_dir = pack_dir / "fixtures" / "expected"
    mismatches = _verify(written, expected_dir)
    if mismatches:
        print()
        print(f"RESULT: FAIL - differs from fixtures/expected/ in: {', '.join(mismatches)}")
        return 1
    print()
    print("RESULT: PASS - every output matches fixtures/expected/.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="bo-triage",
        description="Route back-office messages, draft actions, gate every send.",
    )
    parser.add_argument(
        "--mock-llm",
        action="store_true",
        help="run the whole pipeline offline over the bundled fixtures and self-verify",
    )
    parser.add_argument(
        "--route",
        action="store_true",
        help="run the pipeline over a real inbox (no self-verify; the demo lane owns that)",
    )
    parser.add_argument(
        "--pack-dir",
        type=Path,
        default=PACK_DIR,
        help="pack root holding config/, fixtures/ and prompts/ (default: this file's dir)",
    )
    parser.add_argument(
        "--inbox",
        type=Path,
        default=None,
        help="inbox folder to route (default: the pack's bundled fixtures/inbox)",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=None,
        help="output directory (default: ./mock-out in mock mode, ./out in route mode)",
    )
    parser.add_argument(
        "--approvals",
        type=Path,
        default=None,
        help=(
            "approval CSV (default: fixtures/expected/approvals.csv in mock mode, "
            "./approvals.csv in route mode); with no file, all sends are blocked"
        ),
    )
    parser.add_argument("--version", action="version", version="backoffice-triage 0.1.0")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.mock_llm and not args.route:
        parser.print_help()
        return 2

    pack_dir: Path = args.pack_dir
    route_mode: bool = args.route and not args.mock_llm

    if route_mode:
        out_dir: Path = args.out if args.out is not None else Path.cwd() / "out"
        approvals: Path = (
            args.approvals if args.approvals is not None else Path.cwd() / "approvals.csv"
        )
    else:
        out_dir = args.out if args.out is not None else Path.cwd() / "mock-out"
        approvals = (
            args.approvals
            if args.approvals is not None
            else pack_dir / "fixtures" / "expected" / "approvals.csv"
        )

    try:
        config = load_config(pack_dir)
        inbox: Path = args.inbox if args.inbox is not None else pack_dir / config.inbox
        return run_lane(
            pack_dir, inbox, out_dir, approvals, verify=not route_mode
        )
    except ConfigError as exc:
        print(f"config error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
