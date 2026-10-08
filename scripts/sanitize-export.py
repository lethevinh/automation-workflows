#!/usr/bin/env python3
"""Strip leaked instance metadata from published n8n workflow exports.

Removes the fields that tie an export back to the owner's n8n instance while
preserving everything a reader needs to import and run the workflow:

  top-level:  meta, id, versionId, createdAt, updatedAt, nodeGroups, pinData
  per-node:   webhookId

Kept untouched: nodes (including per-node "id" — connections reference them),
connections, settings, "active", tags, name, notes, parameters.

Usage:
    python3 scripts/sanitize-export.py [workflow.json ...]

With no arguments, processes n8n/*/workflow.json under the repo root.
Idempotent: re-running on a clean file changes nothing. Exits non-zero if any
file is unreadable or contains malformed JSON.
"""

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

TOP_LEVEL_KEYS = (
    "meta",
    "id",
    "versionId",
    "createdAt",
    "updatedAt",
    "nodeGroups",
    "pinData",
)
NODE_KEYS = ("webhookId",)


def sanitize(path: Path) -> bool:
    """Sanitize one file in place. Returns True on success, False on error."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"{path}: ERROR — {exc}", file=sys.stderr)
        return False
    if not isinstance(data, dict):
        print(f"{path}: ERROR — top level is not a JSON object", file=sys.stderr)
        return False

    removed = []
    for key in TOP_LEVEL_KEYS:
        if key in data:
            del data[key]
            removed.append(key)

    node_stripped = 0
    for node in data.get("nodes", []):
        if not isinstance(node, dict):
            continue
        for key in NODE_KEYS:
            if key in node:
                del node[key]
                node_stripped += 1
    if node_stripped:
        removed.append(f"nodes[].webhookId x{node_stripped}")

    if removed:
        path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(f"{path}: removed {', '.join(removed)}")
    else:
        print(f"{path}: already clean")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "paths",
        nargs="*",
        type=Path,
        help="workflow.json files (default: n8n/*/workflow.json)",
    )
    args = parser.parse_args()

    paths = args.paths or sorted(REPO_ROOT.glob("n8n/*/workflow.json"))
    if not paths:
        print("no workflow.json files found", file=sys.stderr)
        return 1

    ok = True
    for path in paths:
        if not sanitize(path):
            ok = False
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
