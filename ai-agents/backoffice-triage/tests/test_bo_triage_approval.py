"""AC (b): no message is sent without an approval row; the approval gate blocks
any auto-send."""

from __future__ import annotations

from pathlib import Path

from bo_triage_audit import gate, read_approvals
from bo_triage_config import load_config, load_router
from bo_triage_core import run_pipeline

PACK_DIR = Path(__file__).resolve().parents[1]


def _run(approvals_path: Path):
    config = load_config(PACK_DIR)
    router = load_router(PACK_DIR)
    return run_pipeline(
        inbox_dir=PACK_DIR / "fixtures" / "inbox",
        router=router,
        config=config,
        approvals_path=approvals_path,
        as_of=config.demo_as_of,
    )


def test_gate_sends_only_with_an_approval_row() -> None:
    approvals_path = PACK_DIR / "fixtures" / "expected" / "approvals.csv"
    approvals = read_approvals(approvals_path)
    result = _run(approvals_path)

    sent_files = {row.source_file for row in result.sent}
    assert sent_files == {"03-email-tracking.txt", "04-message-login-locked.txt",
                          "09-email-vendor-confirmation.txt"}
    # every sent message has an approval row, and the blocked ones never do
    assert sent_files <= set(approvals)
    blocked_files = {row.source_file for row in result.blocked}
    assert blocked_files & set(approvals) == set()
    assert len(sent_files) + len(blocked_files) == 10


def test_no_side_effect_before_approval() -> None:
    result = _run(PACK_DIR / "fixtures" / "expected" / "approvals.csv")
    for row in result.audit:
        if row.approval_id == "":
            assert row.outcome == "blocked", row.source_file
        else:
            assert row.outcome == "sent", row.source_file


def test_with_no_approvals_every_message_is_blocked() -> None:
    result = _run(PACK_DIR / "fixtures" / "inbox" / "no-such-approvals.csv")
    assert result.sent == []
    assert len(result.blocked) == 10
    assert all(row.reason == "no approval row" for row in result.blocked)


def test_gate_unit_never_releases_without_an_approval() -> None:
    approvals = {"03-email-tracking.txt": "APR-1001"}
    outcome, approval_id, _ = gate("03-email-tracking.txt", approvals)
    assert (outcome, approval_id) == ("sent", "APR-1001")
    outcome, approval_id, reason = gate("01-email-refund-request.txt", approvals)
    assert outcome == "blocked"
    assert approval_id == ""
    assert reason == "no approval row"