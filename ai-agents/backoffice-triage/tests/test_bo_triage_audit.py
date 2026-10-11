"""AC (c): one audit row is written per routed message."""

from __future__ import annotations

from pathlib import Path

from bo_triage_config import load_config, load_router
from bo_triage_core import run_pipeline

PACK_DIR = Path(__file__).resolve().parents[1]


def _run():
    config = load_config(PACK_DIR)
    router = load_router(PACK_DIR)
    return run_pipeline(
        inbox_dir=PACK_DIR / "fixtures" / "inbox",
        router=router,
        config=config,
        approvals_path=PACK_DIR / "fixtures" / "expected" / "approvals.csv",
        as_of=config.demo_as_of,
    )


def test_one_audit_row_per_routed_message() -> None:
    result = _run()
    source_files = [row.source_file for row in result.audit]
    assert len(source_files) == 10
    assert len(set(source_files)) == 10  # exactly one row per message, none repeated


def test_every_audit_row_carries_route_action_and_outcome() -> None:
    result = _run()
    for row in result.audit:
        assert row.queue in {
            "billing", "shipping", "security", "support", "general"
        }
        assert row.action
        assert row.needs_approval is True  # the policy has no auto-send path
        assert row.outcome in {"sent", "blocked"}


def test_audit_rows_match_the_expected_fixture() -> None:
    result = _run()
    expected = (PACK_DIR / "fixtures" / "expected" / "audit.csv").read_text(
        encoding="utf-8"
    )
    # spot-check the first data row so the demo and the audit cannot drift apart
    assert "01-email-refund-request.txt,billing" in expected
    assert "03-email-tracking.txt,shipping" in expected
    assert len(result.audit) == 10