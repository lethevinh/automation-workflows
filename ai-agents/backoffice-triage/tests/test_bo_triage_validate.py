"""Parsing and configuration validation edge cases."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from bo_triage_config import (
    SUPPORTED_CONFIG_VERSION,
    ConfigError,
    load_config,
    load_router,
)
from bo_triage_core import parse_message
from bo_triage_route import classify

PACK_DIR = Path(__file__).resolve().parents[1]


def test_parse_message_headers_vs_body() -> None:
    text = (
        "From: a@example.com\n"
        "Subject: Hello\n"
        "Date: 2026-09-01\n"
        "\n"
        "This is the body.\n"
        "Note: this colon is body, not a header.\n"
    )
    subject, body = parse_message(text)
    assert subject == "Hello"
    assert "Note: this colon is body" in body
    assert "not a header" in body


def test_parse_message_body_colon_is_not_a_header() -> None:
    text = "Subject: invoice\n\nAmount due: 5.00\n"
    subject, body = parse_message(text)
    assert subject == "invoice"
    assert body == "Amount due: 5.00"


def test_parse_message_subject_falls_back_to_first_body_line() -> None:
    subject, _ = parse_message(
        "From: +1 555 0100\n\nLocked out of my account\nPlease unlock it.\n"
    )
    assert subject == "Locked out of my account"


def test_parse_message_form_fields() -> None:
    subject, body = parse_message(
        "Form: contact-us\nSubject: Cancel order\nField (order_id): 1042\n"
        "\n"
        "Please cancel it.\n"
    )
    assert subject == "Cancel order"
    assert body == "Please cancel it."


def test_config_rejects_auto_send_policy(tmp_path: Path) -> None:
    broken = tmp_path / "pack"
    shutil.copytree(
        PACK_DIR,
        broken,
        ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache", "tests"),
    )
    config_path = broken / "config" / "config.json"
    data = json.loads(config_path.read_text(encoding="utf-8"))
    data["send_policy"]["require_approval"] = False
    config_path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    with pytest.raises(ConfigError, match="require_approval"):
        load_config(broken)


def test_config_rejects_unknown_version(tmp_path: Path) -> None:
    broken = tmp_path / "pack"
    shutil.copytree(
        PACK_DIR,
        broken,
        ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache", "tests"),
    )
    config_path = broken / "config" / "config.json"
    data = json.loads(config_path.read_text(encoding="utf-8"))
    data["version"] = SUPPORTED_CONFIG_VERSION + 1
    config_path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    with pytest.raises(ConfigError, match="version"):
        load_config(broken)


def test_router_config_loads_from_bundled_files() -> None:
    router = load_router(PACK_DIR)
    assert router.version == SUPPORTED_CONFIG_VERSION
    assert set(router.queues) == {"billing", "shipping", "security", "support", "general"}
    assert set(router.action_templates) == set(router.queues)


def test_every_message_is_routable_offline() -> None:
    router = load_router(PACK_DIR)
    inbox = PACK_DIR / "fixtures" / "inbox"
    assert len(list(inbox.glob("*.txt"))) == 10
    for path in inbox.glob("*.txt"):
        subject, body = parse_message(path.read_text(encoding="utf-8"))
        route = classify(subject, body, router)
        assert route.queue in router.queues, path.name