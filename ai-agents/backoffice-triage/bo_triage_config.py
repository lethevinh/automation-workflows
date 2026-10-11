"""Typed loaders for the versioned triage configuration.

Two files under ``config/`` are read together:

* ``config.json`` — model/tool settings and the send policy.
* ``router.json`` — the routing rule table and the per-queue action templates.

Both carry a ``version`` integer; the loader refuses an unknown version so a
future schema bump cannot be silently misread by an old CLI.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

SUPPORTED_CONFIG_VERSION = 1
SUPPORTED_ROUTER_VERSION = 1


class ConfigError(Exception):
    """Raised when a config file is missing, unreadable or malformed."""


@dataclass(frozen=True)
class SendPolicy:
    """How outbound actions are gated."""

    require_approval: bool
    approval_source: str


@dataclass(frozen=True)
class TriageConfig:
    """The top-level pack configuration."""

    version: int
    demo_as_of: str
    classifier: str
    send_policy: SendPolicy
    inbox: str
    output: str


@dataclass(frozen=True)
class RouteRule:
    """One routing rule: a regex, its queue, its strength and its reason."""

    pattern: str
    queue: str
    strength: float
    reason: str


@dataclass(frozen=True)
class RouterConfig:
    """The routing rule table and action templates."""

    version: int
    queues: tuple[str, ...]
    default_queue: str
    classifier_threshold: float
    rules: tuple[RouteRule, ...]
    action_templates: dict[str, str]


def _read_json(path: Path) -> dict[str, object]:
    if not path.is_file():
        raise ConfigError(f"config file not found: {path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:  # pragma: no cover - defensive
        raise ConfigError(f"invalid JSON in {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ConfigError(f"config root must be an object: {path}")
    return data


def _require(data: dict[str, object], key: str, path: Path) -> object:
    if key not in data:
        raise ConfigError(f"missing key '{key}' in {path}")
    return data[key]


def load_config(pack_dir: Path) -> TriageConfig:
    """Load and validate ``config/config.json``."""

    path = pack_dir / "config" / "config.json"
    data = _read_json(path)

    version = _require(data, "version", path)
    if version != SUPPORTED_CONFIG_VERSION:
        raise ConfigError(
            f"unsupported config version {version!r} (expected {SUPPORTED_CONFIG_VERSION})"
        )

    policy_raw = _require(data, "send_policy", path)
    if not isinstance(policy_raw, dict):
        raise ConfigError(f"'send_policy' must be an object in {path}")
    require_approval = policy_raw.get("require_approval")
    if require_approval is not True:
        raise ConfigError(
            "send_policy.require_approval must be true — there is no auto-send path"
        )
    approval_source = policy_raw.get("approval_source")
    if not isinstance(approval_source, str) or not approval_source:
        raise ConfigError("send_policy.approval_source must be a non-empty string")

    model_raw = _require(data, "model", path)
    if not isinstance(model_raw, dict):
        raise ConfigError(f"'model' must be an object in {path}")
    classifier = model_raw.get("classifier")
    if not isinstance(classifier, str) or not classifier:
        raise ConfigError("model.classifier must be a non-empty string")

    paths_raw = _require(data, "paths", path)
    if not isinstance(paths_raw, dict):
        raise ConfigError(f"'paths' must be an object in {path}")
    inbox = paths_raw.get("inbox")
    output = paths_raw.get("output")
    if not isinstance(inbox, str) or not isinstance(output, str):
        raise ConfigError("paths.inbox and paths.output must be strings")

    demo_as_of = _require(data, "demo_as_of", path)
    if not isinstance(demo_as_of, str):
        raise ConfigError("demo_as_of must be a string")

    return TriageConfig(
        version=version,
        demo_as_of=demo_as_of,
        classifier=classifier,
        send_policy=SendPolicy(
            require_approval=True, approval_source=approval_source
        ),
        inbox=inbox,
        output=output,
    )


def load_router(pack_dir: Path) -> RouterConfig:
    """Load and validate ``config/router.json``."""

    path = pack_dir / "config" / "router.json"
    data = _read_json(path)

    version = _require(data, "version", path)
    if version != SUPPORTED_ROUTER_VERSION:
        raise ConfigError(
            f"unsupported router version {version!r} (expected {SUPPORTED_ROUTER_VERSION})"
        )

    queues_raw = _require(data, "queues", path)
    if not isinstance(queues_raw, list) or not all(
        isinstance(q, str) for q in queues_raw
    ):
        raise ConfigError("'queues' must be a list of strings")

    default_queue = _require(data, "default_queue", path)
    if not isinstance(default_queue, str) or default_queue not in queues_raw:
        raise ConfigError("'default_queue' must name one of 'queues'")

    threshold = _require(data, "classifier_threshold", path)
    if not isinstance(threshold, (int, float)):
        raise ConfigError("'classifier_threshold' must be a number")

    rules_raw = _require(data, "rules", path)
    if not isinstance(rules_raw, list) or not rules_raw:
        raise ConfigError("'rules' must be a non-empty list")

    rules: list[RouteRule] = []
    for entry in rules_raw:
        if not isinstance(entry, dict):
            raise ConfigError("each rule must be an object")
        pattern = entry.get("pattern")
        queue = entry.get("queue")
        strength = entry.get("strength")
        reason = entry.get("reason")
        if not isinstance(pattern, str) or not isinstance(queue, str):
            raise ConfigError("each rule needs a string 'pattern' and 'queue'")
        if queue not in queues_raw:
            raise ConfigError(f"rule queue {queue!r} is not one of 'queues'")
        if not isinstance(strength, (int, float)):
            raise ConfigError("each rule needs a numeric 'strength'")
        if not isinstance(reason, str):
            raise ConfigError("each rule needs a string 'reason'")
        rules.append(
            RouteRule(
                pattern=pattern,
                queue=queue,
                strength=float(strength),
                reason=reason,
            )
        )

    templates_raw = _require(data, "action_templates", path)
    if not isinstance(templates_raw, dict):
        raise ConfigError("'action_templates' must be an object")
    templates: dict[str, str] = {}
    for queue in queues_raw:
        template = templates_raw.get(queue)
        if not isinstance(template, str) or not template:
            raise ConfigError(f"action_templates is missing a template for {queue!r}")
        templates[queue] = template

    return RouterConfig(
        version=version,
        queues=tuple(queues_raw),
        default_queue=default_queue,
        classifier_threshold=float(threshold),
        rules=tuple(rules),
        action_templates=templates,
    )
