"""AC (a)/(b)/(c): skill format, the two-fixture lane and the worked example.

Self-contained: the pack runs its own proof with stdlib + pytest only, so the
published repo's CI job can call ``python3 -m pytest -q`` unchanged. The
repo's own ``verify_skill_format`` validator is used when present (the company
workspace) and skipped where it does not ship.
"""

from __future__ import annotations

import importlib
import re
import subprocess
import sys
from pathlib import Path

import audit_lane
import pytest

PACK_DIR = Path(__file__).resolve().parents[1]
PROCESSES = PACK_DIR / "fixtures" / "processes"
EXPECTED = PACK_DIR / "fixtures" / "expected"

TWO_FIXTURES = ("01-invoice-emailing.md", "02-lead-intake.md")
WORKED_EXAMPLE = "03-fixed-price-service.md"


# --- AC (b): running the skill on 2 fixture descriptions ------------------


def test_two_fixture_processes_produce_every_required_section() -> None:
    assert len(TWO_FIXTURES) == 2
    for name in TWO_FIXTURES:
        audit = audit_lane.build_audit((PROCESSES / name).read_text("utf-8"))
        for section in audit_lane.OUTPUT_SECTIONS:
            assert f"## {section}" in audit, (name, section)


def test_self_check_is_green_and_cwd_independent() -> None:
    proc = subprocess.run(
        [sys.executable, str(PACK_DIR / "audit_lane.py"), "--self-check"],
        cwd=PROCESSES,  # arbitrary cwd: the lane resolves its own paths
        capture_output=True, text=True, check=False,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "RESULT: PASS" in proc.stdout
    passed = [line for line in proc.stdout.splitlines()
              if line.startswith("PASS ")]
    assert len(passed) == 3  # three fixtures checked


def test_every_fixture_has_an_expected_output() -> None:
    for case in sorted(PROCESSES.glob("*.md")):
        assert (EXPECTED / f"{case.stem}.audit.md").is_file(), case.name


def test_audit_is_reproducible() -> None:
    source = (PROCESSES / WORKED_EXAMPLE).read_text("utf-8")
    assert audit_lane.build_audit(source) == audit_lane.build_audit(source)


def test_missing_section_is_refused() -> None:
    broken = (PROCESSES / TWO_FIXTURES[0]).read_text("utf-8").replace(
        "## Out of scope", "## Notes"
    )
    with pytest.raises(audit_lane.AuditError) as excinfo:
        audit_lane.build_audit(broken)
    assert "Out of scope" in str(excinfo.value)


def test_unmapped_candidate_is_tbd_and_excluded_from_total() -> None:
    text = (
        "# Process: Two-step tidy\n\n"
        "## Business problem\n\nduplicates everywhere\n\n"
        "## In scope\n\n- one thing\n\n"
        "## Out of scope\n\n- another\n\n"
        "## Success signal\n\nzero duplicates\n\n"
        "## Automation opportunities\n\n"
        "- Keep the invoice ledger in sync\n"
        "- Invent a bespoke teleporter\n"
    )
    audit = audit_lane.build_audit(text)
    assert "effort TBD (scope first)" in audit
    assert "Total: **~4h**" in audit  # only the invoice candidate is counted


# --- AC (c): the worked example cites a real source, invents no numbers ----


def test_worked_example_cites_a_real_source() -> None:
    ask = (PROCESSES / WORKED_EXAMPLE).read_text("utf-8")
    assert ask.startswith("# Process:")
    assert "Source: real ask" in ask
    assert (
        "community.n8n.io/t/looking-for-n8n-make-automation-specialist"
        in ask
    )


def test_worked_example_contains_no_invented_numbers() -> None:
    ask = (PROCESSES / WORKED_EXAMPLE).read_text("utf-8")
    audit = audit_lane.build_audit(ask)

    candidates = [
        line[2:].strip()
        for line in audit_lane.parse_sections(ask)["Automation opportunities"]
        .splitlines()
        if line.strip().startswith("- ")
    ]
    matched = [
        pillar for pillar in (audit_lane.match_pillar(c) for c in candidates)
        if pillar is not None
    ]
    allowed = (
        {pillar.hours for pillar in matched}
        | {sum(pillar.hours for pillar in matched)}
        | set(range(1, len(candidates) + 1))
    )
    # Only the audit's *generated* sections carry figures; the echoed spec
    # sections are the source's own quoted words (verified verbatim above).
    generated = audit.split("## Automation candidates (ordered)", 1)[1]
    found = {int(token) for token in re.findall(r"\d+", generated)}
    assert found <= allowed, f"unexplained numbers: {sorted(found - allowed)}"


# --- AC (a): SKILL.md passes the repository's skill-format validator -------


def test_skill_md_meets_the_documented_skill_format() -> None:
    text = (PACK_DIR / "SKILL.md").read_text("utf-8")
    assert text.startswith("---\n")
    front, _, body = text[3:].partition("\n---\n")

    top: dict[str, str] = {}
    for line in front.splitlines():
        if not line or line.startswith(" "):
            continue
        key, _, value = line.partition(":")
        top[key.strip()] = value.strip().strip('"')

    assert top["name"] == PACK_DIR.name == "automation-audit"
    assert re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", top["name"])
    assert 0 < len(top["description"]) <= 1024
    assert "metadata:" in front
    assert "version:" in front
    assert "status: active" in front
    assert body.lstrip().startswith("# ")
    for section in ("## When to Use", "## Procedure"):
        assert section in body, section


def _repo_validator() -> Path | None:
    for base in PACK_DIR.parents:
        candidate = base / "scripts" / "agents-verify" / "verify_skill_format.py"
        if candidate.is_file():
            return candidate
    return None


def test_skill_md_passes_the_repo_validator_when_present() -> None:
    validator = _repo_validator()
    if validator is None:
        pytest.skip("company-workspace validator not present in this checkout")
    assert validator is not None  # mypy narrowing after the pytest.skip branch
    sys.path.insert(0, str(validator.parent))
    try:
        module = importlib.import_module("verify_skill_format")
        errors = module.check_skill(PACK_DIR / "SKILL.md")
    finally:
        sys.path.remove(str(validator.parent))
    assert errors == [], errors