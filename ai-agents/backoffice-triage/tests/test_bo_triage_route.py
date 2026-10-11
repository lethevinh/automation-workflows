"""AC (a): ``--mock-llm`` routes the bundled 10-message fixture to the expected
queues, producing the expected route per message."""

from __future__ import annotations

from pathlib import Path

from bo_triage_config import RouterConfig, load_config, load_router
from bo_triage_core import parse_message, run_pipeline
from bo_triage_route import classify

PACK_DIR = Path(__file__).resolve().parents[1]

EXPECTED_ROUTES = {
    "01-email-refund-request.txt": ("billing", "0.95", "rules"),
    "02-form-cancel-order.txt": ("shipping", "0.90", "rules"),
    "03-email-tracking.txt": ("shipping", "0.90", "rules"),
    "04-message-login-locked.txt": ("security", "0.95", "rules"),
    "05-email-invoice-question.txt": ("billing", "0.90", "rules"),
    "06-form-feedback.txt": ("support", "0.80", "rules"),
    "07-email-ambiguous.txt": ("support", "0.90", "llm-mock"),
    "08-message-password-reset.txt": ("security", "0.95", "rules"),
    "09-email-vendor-confirmation.txt": ("shipping", "0.90", "rules"),
    "10-form-complaint.txt": ("support", "0.85", "rules"),
}


def _router() -> RouterConfig:
    return load_router(PACK_DIR)


def test_every_fixture_routes_to_its_expected_queue() -> None:
    router = _router()
    inbox = PACK_DIR / "fixtures" / "inbox"
    for path in sorted(inbox.glob("*.txt")):
        subject, body = parse_message(path.read_text(encoding="utf-8"))
        route = classify(subject, body, router)
        expected_queue, expected_conf, expected_classifier = EXPECTED_ROUTES[path.name]
        assert route.queue == expected_queue, path.name
        assert f"{route.confidence:.2f}" == expected_conf, path.name
        assert route.classifier == expected_classifier, path.name


def test_expected_route_table_in_pipeline_output() -> None:
    config = load_config(PACK_DIR)
    router = _router()
    result = run_pipeline(
        inbox_dir=PACK_DIR / "fixtures" / "inbox",
        router=router,
        config=config,
        approvals_path=PACK_DIR / "fixtures" / "expected" / "approvals.csv",
        as_of=config.demo_as_of,
    )
    by_file = {row.source_file: row for row in result.routes}
    assert len(by_file) == 10
    for source_file, (queue, conf, classifier) in EXPECTED_ROUTES.items():
        row = by_file[source_file]
        assert (row.queue, row.confidence, row.classifier) == (queue, conf, classifier)


def test_classification_is_deterministic() -> None:
    router = _router()
    sample = (
        "Question about invoice INV-3031",
        "Could you explain the software line item on invoice INV-3031?",
    )
    first = classify(*sample, router)
    for _ in range(5):
        assert classify(*sample, router) == first


def test_nomatch_defaults_to_general() -> None:
    router = _router()
    route = classify("Team offsite next week", "Please put a carafe on the table.", router)
    assert route.queue == router.default_queue == "general"
    assert route.classifier == "rules"