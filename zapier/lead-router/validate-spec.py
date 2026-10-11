#!/usr/bin/env python3
"""Schema guard for a Zapier blueprint spec.json.

Validates spec.json against schema.json, then asserts the one rule the task
names beyond the schema: every blueprint step carries a non-empty app name
(trigger, each step and the failure branch).

Runs with no third-party dependency. If the ``jsonschema`` package is
importable it is used as the engine; otherwise a small built-in validator
covers the keyword subset this schema uses (type, required, properties,
additionalProperties, items, minItems, minLength, pattern, const, enum,
minimum). Both engines accept the same document.

Usage:
    python3 validate-spec.py [spec.json] [schema.json]
Exit code 0 = pass; 1 = the spec or schema is invalid.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
DEFAULT_SPEC = HERE / "spec.json"
DEFAULT_SCHEMA = HERE / "schema.json"

_TYPES: dict[str, Any] = {
    "object": dict,
    "array": list,
    "string": str,
    "integer": int,
    "number": (int, float),
    "boolean": bool,
    "null": type(None),
}


def _type_ok(value: object, name: str) -> bool:
    if name in ("integer", "number") and isinstance(value, bool):
        return False
    return isinstance(value, _TYPES[name])


def _validate(node: object, schema: dict, path: str, errors: list[str]) -> None:
    """Minimal JSON Schema subset validator (fallback engine)."""
    if "const" in schema and node != schema["const"]:
        errors.append(f"{path}: expected const {schema['const']!r}, got {node!r}")
    if "enum" in schema and node not in schema["enum"]:
        errors.append(f"{path}: {node!r} not in enum {schema['enum']!r}")
    if "type" in schema:
        names = schema["type"] if isinstance(schema["type"], list) else [schema["type"]]
        if not any(_type_ok(node, n) for n in names):
            errors.append(f"{path}: expected type {names}, got {type(node).__name__}")
            return
    if isinstance(node, str):
        if "minLength" in schema and len(node) < schema["minLength"]:
            errors.append(f"{path}: shorter than minLength {schema['minLength']}")
        if "pattern" in schema and not re.search(schema["pattern"], node):
            errors.append(f"{path}: {node!r} does not match {schema['pattern']!r}")
    if isinstance(node, (int, float)) and not isinstance(node, bool):
        if "minimum" in schema and node < schema["minimum"]:
            errors.append(f"{path}: below minimum {schema['minimum']}")
    if isinstance(node, list):
        if "minItems" in schema and len(node) < schema["minItems"]:
            errors.append(f"{path}: fewer than minItems {schema['minItems']}")
        if "items" in schema:
            for i, item in enumerate(node):
                _validate(item, schema["items"], f"{path}[{i}]", errors)
    if isinstance(node, dict):
        for key in schema.get("required", []):
            if key not in node:
                errors.append(f"{path}: missing required key {key!r}")
        props = schema.get("properties", {})
        for key, val in node.items():
            if key in props:
                _validate(val, props[key], f"{path}.{key}", errors)
            elif schema.get("additionalProperties") is False:
                errors.append(f"{path}: unexpected key {key!r}")


def validate(spec: object, schema: dict) -> tuple[str, list[str]]:
    """Return (engine, errors)."""
    try:
        import jsonschema  # type: ignore
    except ImportError:
        errors: list[str] = []
        _validate(spec, schema, "$", errors)
        return "builtin", errors
    validator = jsonschema.Draft7Validator(schema)
    errors = [
        f"$: {'/'.join(str(p) for p in err.absolute_path) or '(root)'}: {err.message}"
        for err in sorted(validator.iter_errors(spec), key=lambda e: list(e.absolute_path))
    ]
    return "jsonschema", errors


def app_coverage(spec: dict) -> list[str]:
    """Assert every blueprint step names its app."""
    errors: list[str] = []
    trigger = spec.get("trigger", {})
    if not str(trigger.get("app", "")).strip():
        errors.append("trigger: names no app")
    steps = spec.get("steps", [])
    if not isinstance(steps, list) or not steps:
        errors.append("steps: none declared")
    else:
        for i, step in enumerate(steps):
            if not str(step.get("app", "")).strip():
                errors.append(f"steps[{i}] ({step.get('id', '?')}): names no app")
    branch = spec.get("failure_branch", {})
    if not str(branch.get("app", "")).strip():
        errors.append("failure_branch: names no app")
    return errors


def main(argv: list[str]) -> int:
    spec_path = Path(argv[1]) if len(argv) > 1 else DEFAULT_SPEC
    schema_path = Path(argv[2]) if len(argv) > 2 else DEFAULT_SCHEMA
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    schema = json.loads(schema_path.read_text(encoding="utf-8"))

    engine, schema_errors = validate(spec, schema)
    app_errors = app_coverage(spec) if isinstance(spec, dict) else ["spec is not an object"]

    is_dict = isinstance(spec, dict)
    steps = spec.get("steps", []) if is_dict else []
    slug = spec.get("slug", "?") if is_dict else "?"
    platform = spec.get("platform", "?") if is_dict else "?"
    print(f"spec:    {spec_path.name} -> slug {slug!r}, platform {platform!r}")
    print(f"schema:  {schema_path.name} (engine: {engine})")
    print(f"steps:   {len(steps)} declared")

    problems = schema_errors + app_errors
    if problems:
        print(f"RESULT: FAIL - {len(problems)} schema-guard problem(s):")
        for err in problems:
            print(f"  - {err}")
        return 1

    apps = [spec["trigger"]["app"]] + [s["app"] for s in steps] + [spec["failure_branch"]["app"]]
    print(f"apps:    every step names its app ({len(apps)} app slots: {', '.join(apps)})")
    print("RESULT: PASS - spec.json satisfies schema.json and the app-coverage rule.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
