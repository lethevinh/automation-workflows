#!/usr/bin/env python3
"""Offline replay of the lead-router's deterministic steps.

Runs the credential-free lane the README promises: it replays the normalize ->
dedupe -> score -> route steps of ``spec.json`` over the bundled 8-lead
fixture, prints the verdict per lead and exactly one digest, and asserts the
result against the fixture's own ``expected`` block. A one-step-ahead mistake
in the blueprint therefore fails the replay, not just a reader's eye.

No Zapier account, no credential and no network call: the scoring rule table
and bands are read straight out of ``spec.json``.

Usage:
    python3 replay.py [spec.json] [fixture.json]
Exit code 0 = the replay matched every expected verdict; 1 = a mismatch.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_SPEC = HERE / "spec.json"
DEFAULT_FIXTURE = HERE / "fixtures" / "leads-8.json"

SPECIAL = {"duplicate_skipped", "missing_data_alert"}


def normalize_email(value: str) -> str:
    return (value or "").strip().lower()


def derived(lead: dict) -> dict:
    fields = dict(lead)
    fields["message_length"] = len(lead.get("message") or "")
    fields["phone"] = bool((lead.get("phone") or "").strip())
    return fields


def rule_matches(rule: dict, fields: dict) -> bool:
    value = fields.get(rule["field"])
    op, target = rule["op"], rule.get("value")
    if op == ">=":
        return value is not None and value >= target
    if op == ">":
        return value is not None and value > target
    if op == "<=":
        return value is not None and value <= target
    if op == "<":
        return value is not None and value < target
    if op == "==":
        return value == target
    if op == "in":
        return isinstance(target, (list, tuple)) and value in target
    if op == "present":
        return value is True if target is True else value is not None
    raise ValueError(f"unsupported op {op!r}")


def score_lead(scoring: dict, lead: dict) -> int:
    fields = derived(lead)
    return sum(r["points"] for r in scoring["rules"] if rule_matches(r, fields))


def band_for(scoring: dict, score: int) -> dict:
    ordered = sorted(scoring["bands"], key=lambda b: b["min"], reverse=True)
    for band in ordered:
        if score >= band["min"]:
            return band
    return ordered[-1]


def replay(spec: dict, fixture: dict) -> tuple[list[dict], dict]:
    scoring = spec["scoring"]
    seen: set[str] = set()
    results: list[dict] = []
    for lead in fixture["leads"]:
        email = normalize_email(lead.get("email", ""))
        row = {"lead_id": lead["lead_id"], "score": None, "band": None}
        if not email:
            row["verdict"] = "missing_data_alert"
            results.append(row)
            continue
        if email in seen:
            row["verdict"] = "duplicate_skipped"
            results.append(row)
            continue
        seen.add(email)
        score = score_lead(scoring, lead)
        band = band_for(scoring, score)
        row.update({"verdict": band["route"], "score": score, "band": band["name"]})
        results.append(row)

    verdicts = [r["verdict"] for r in results]
    digest = {
        "received": len(results),
        "upserted": sum(v in ("crm_upsert_and_draft", "crm_upsert") for v in verdicts),
        "drafted": verdicts.count("crm_upsert_and_draft"),
        "duplicates": verdicts.count("duplicate_skipped"),
        "missing_data": verdicts.count("missing_data_alert"),
        "cold_logged": verdicts.count("log_only"),
    }
    return results, digest


def main(argv: list[str]) -> int:
    spec_path = Path(argv[1]) if len(argv) > 1 else DEFAULT_SPEC
    fixture_path = Path(argv[2]) if len(argv) > 2 else DEFAULT_FIXTURE
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    fixture = json.loads(fixture_path.read_text(encoding="utf-8"))

    results, digest = replay(spec, fixture)

    print(f"replay: {spec['slug']} over {fixture_path.name} ({len(fixture['leads'])} leads)")
    print(f"{'lead':<8} {'score':>5} {'band':<8} verdict")
    for r in results:
        score = "-" if r["score"] is None else str(r["score"])
        band = r["band"] or "-"
        print(f"{r['lead_id']:<8} {score:>5} {band:<8} {r['verdict']}")
    print(f"digest (exactly 1): {json.dumps(digest, sort_keys=True)}")

    problems: list[str] = []
    for result in results:
        expected = fixture["expected"].get(result["lead_id"])
        if expected is None:
            problems.append(f"{result['lead_id']}: no expected verdict in the fixture")
        elif (result["verdict"], result["score"], result["band"]) != (
            expected["verdict"],
            expected["score"],
            expected["band"],
        ):
            problems.append(f"{result['lead_id']}: got {result}, expected {expected}")
    if digest != fixture["expected_digest"]:
        problems.append(f"digest mismatch: got {digest}, expected {fixture['expected_digest']}")

    if problems:
        print(f"RESULT: FAIL - {len(problems)} replay problem(s):")
        for problem in problems:
            print(f"  - {problem}")
        return 1
    print("RESULT: PASS - every verdict matches the fixture and exactly 1 digest was emitted.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
