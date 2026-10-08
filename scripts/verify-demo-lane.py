#!/usr/bin/env python3
"""Demo-lane regression guard for the published n8n exports.

Every workflow in n8n/ ships a zero-credential demo lane: clicking
"Test workflow" must never execute a node that needs credentials. This
script is the local substitute for an n8n instance while exports are being
edited (plan P5) — it cannot prove n8n imports the file, but it catches
structural breakage and demo-lane regressions.

Per workflow.json it asserts:
  a. the file parses and has a list "nodes" and an object "connections"
  b. node names are unique and every connection endpoint resolves
  c. node and main-connection counts match EXPECTED below
  d. the demo lane reaches 0 credentialed nodes

Demo-lane semantics (verified against the five exports):
  * entry points are `manualTrigger` nodes — the "Test workflow" button.
    SETUP lanes ("SETUP — ..." manual triggers, a documented one-time lane)
    and live triggers (schedule / chat / error) are NOT part of the demo
    lane.
  * `disabled: true` nodes are dead ends: n8n does not execute them and
    nothing flows through them (daily-cash-tally isolates its live lane
    this way).
  * an IF whose conditions reference `$json.live` is a live gate; demo
    fixtures set `live: false`, so only the false output (slot 1) is taken.
    The same rule applies per-rule to Switch outputs.
  * every other branch output is followed — the demo fixtures exercise
    several routes, so non-live gates stay reachable.

EXPECTED is pinned from the sanitized tree; node counts are plan
Appendix A, connection counts measured on the same tree with the P-1
verify formula (main-connection targets only). Update the table only as
part of an owner-approved export change (P0b/P0c) — see
docs/portfolio-upgrade-plan.md.

Usage:
    python3 scripts/verify-demo-lane.py [n8n/<slug>/workflow.json ...]
Exit code is non-zero if any check fails.
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Node types that need a credential to execute (services in plan
# Appendix A). Extend if a future workflow adds a new service.
CREDENTIALED_TYPES = {
    "n8n-nodes-base.googleSheets",
    "n8n-nodes-base.gmail",
    "n8n-nodes-base.telegram",
    "n8n-nodes-base.openAi",
    "@n8n/n8n-nodes-langchain.openAi",
    "n8n-nodes-base.httpRequest",
}

EXPECTED = {
    "affiliate-intake":        {"nodes": 13, "connections": 24},
    "daily-cash-tally":        {"nodes": 20, "connections": 45},
    "faq-chatbot":             {"nodes": 40, "connections": 117},
    "promise-ledger":          {"nodes": 56, "connections": 162},
    "client-report-generator": {"nodes": 87, "connections": 312},
}


def is_demo_trigger(node):
    return (
        node.get("type") == "n8n-nodes-base.manualTrigger"
        and not node.get("disabled")
        and not node.get("name", "").strip().upper().startswith("SETUP")
    )


def is_credentialed(node):
    return (
        node.get("type") in CREDENTIALED_TYPES
        or bool(node.get("credentials"))
    )


def live_only_slot(node, slot_idx):
    """True if output slot `slot_idx` only carries items when live=True."""
    params = node.get("parameters", {})
    ntype = node.get("type", "")
    if ntype == "n8n-nodes-base.if":
        # IF slot 0 is the "true" output. A condition on $json.live makes the
        # whole condition false in demo mode (demo fixtures set live: false).
        conds = params.get("conditions", {}).get("conditions", [])
        return slot_idx == 0 and any(
            "$json.live" in json.dumps(c) for c in conds
        )
    if ntype == "n8n-nodes-base.switch":
        rules = params.get("rules", {}).get("values", [])
        return slot_idx < len(rules) and "$json.live" in json.dumps(
            rules[slot_idx]
        )
    return False


def demo_lane(workflow):
    """Node names reachable from the demo triggers under demo semantics."""
    nodes = {n["name"]: n for n in workflow["nodes"]}
    starts = [n["name"] for n in workflow["nodes"] if is_demo_trigger(n)]
    seen, stack = set(starts), list(starts)
    while stack:
        name = stack.pop()
        node = nodes[name]
        main = workflow.get("connections", {}).get(name, {}).get("main", [])
        for slot_idx, targets in enumerate(main or []):
            if live_only_slot(node, slot_idx):
                continue
            for target in targets or []:
                dst = nodes.get(target.get("node"))
                if dst is None or dst.get("disabled"):
                    continue
                if dst["name"] not in seen:
                    seen.add(dst["name"])
                    stack.append(dst["name"])
    return seen, starts


def main_connection_count(workflow):
    """Same formula as the P-1 verify snippet in docs/agent-prompts.md."""
    return sum(
        len(targets or [])
        for conn in workflow["connections"].values()
        for slots in conn.get("main", [])
        for targets in slots
    )


def check_file(path):
    """Return (errors, report-dict-or-None) for one workflow.json."""
    slug = path.parent.name
    try:
        wf = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        return [f"{slug}: workflow.json does not parse: {exc}"], None

    errors = []
    nodes = wf.get("nodes")
    conns = wf.get("connections")
    if not isinstance(nodes, list):
        return [f"{slug}: 'nodes' is not a list"], None
    if not isinstance(conns, dict):
        errors.append(f"{slug}: 'connections' is not an object")
        conns = {}

    by_name = {}
    for n in nodes:
        name = n.get("name")
        if name in by_name:
            errors.append(f"{slug}: duplicate node name {name!r}")
        by_name[name] = n

    # every connection endpoint must resolve to a real node
    for src, conn in conns.items():
        if src not in by_name:
            errors.append(f"{slug}: connection from unknown node {src!r}")
        for slots in conn.values():
            for targets in slots or []:
                for t in targets or []:
                    if t.get("node") not in by_name:
                        errors.append(
                            f"{slug}: connection to unknown node "
                            f"{t.get('node')!r} (from {src!r})"
                        )

    n_nodes = len(nodes)
    n_conns = main_connection_count(wf)
    exp = EXPECTED.get(slug)
    if exp is None:
        errors.append(
            f"{slug}: no entry in EXPECTED — new workflow? update the table"
        )
    else:
        if n_nodes != exp["nodes"]:
            errors.append(
                f"{slug}: node count {n_nodes} != expected {exp['nodes']}"
            )
        if n_conns != exp["connections"]:
            errors.append(
                f"{slug}: connection count {n_conns} != expected "
                f"{exp['connections']}"
            )

    lane, starts = demo_lane({"nodes": nodes, "connections": conns})
    if not starts:
        errors.append(f"{slug}: no demo trigger (manualTrigger) found")
    cred_hit = sorted(
        name for name in lane if is_credentialed(by_name[name])
    )
    if cred_hit:
        errors.append(
            f"{slug}: demo lane reaches credentialed node(s): {cred_hit}"
        )

    report = {
        "slug": slug,
        "nodes": n_nodes,
        "exp_nodes": exp["nodes"] if exp else "?",
        "conns": n_conns,
        "exp_conns": exp["connections"] if exp else "?",
        "triggers": len(starts),
        "lane": len(lane),
        "cred": len(cred_hit),
    }
    return errors, report


def main():
    if len(sys.argv) > 1:
        paths = [Path(a) for a in sys.argv[1:]]
    else:
        paths = sorted(ROOT.glob("n8n/*/workflow.json"))
    if not paths:
        print("verify-demo-lane: no workflow.json files found", file=sys.stderr)
        return 1

    all_errors = []
    seen_slugs = set()
    for p in paths:
        errors, report = check_file(p)
        seen_slugs.add(p.parent.name)
        if report:
            print(
                f"{report['slug']:<25} nodes {report['nodes']:>3}/"
                f"{report['exp_nodes']:<3} conns {report['conns']:>3}/"
                f"{report['exp_conns']:<3} demo-triggers {report['triggers']} "
                f"lane-nodes {report['lane']:>3} credentialed-reached "
                f"{report['cred']}"
            )
        all_errors.extend(errors)

    for slug in EXPECTED:
        if slug not in seen_slugs:
            all_errors.append(
                f"{slug}: expected workflow n8n/{slug}/workflow.json missing"
            )

    if all_errors:
        print("FAIL", file=sys.stderr)
        for e in all_errors:
            print(f"  {e}", file=sys.stderr)
        return 1
    print(f"verify-demo-lane: {len(paths)}/{len(paths)} workflows PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
