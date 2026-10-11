"""Deterministic spine of the automation-audit skill.

Turns one described business process into the three-part audit the skill
promises - a scoped spec, an ordered automation list and a rough effort
estimate - with no model, no key and no network. The live skill (read by an
agent or a human) adds judgement on top; this module is the offline proof that
a process description produces every required section in a fixed,
reproducible shape.

Run it::

    python3 audit_lane.py --audit fixtures/processes/01-invoice-emailing.md
    python3 audit_lane.py --self-check     # compare processes to expected/

Section contract (every process description must carry, in order):

    ## Business problem
    ## In scope
    ## Out of scope
    ## Success signal
    ## Automation opportunities

The audit always emits these six sections:

    ## Business problem
    ## Scope in
    ## Scope out
    ## Success signal
    ## Automation candidates (ordered)
    ## Rough effort estimate

Effort figures are catalog estimates defined in this file - the skill's own
rough buckets - never figures taken from the source description.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

PACK_DIR = Path(__file__).resolve().parent
PROCESSES = PACK_DIR / "fixtures" / "processes"
EXPECTED = PACK_DIR / "fixtures" / "expected"

REQUIRED_SECTIONS = (
    "Business problem",
    "In scope",
    "Out of scope",
    "Success signal",
    "Automation opportunities",
)

OUTPUT_SECTIONS = (
    "Business problem",
    "Scope in",
    "Scope out",
    "Success signal",
    "Automation candidates (ordered)",
    "Rough effort estimate",
)

SECTION_RE = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)


class AuditError(ValueError):
    """A process description that does not carry the required sections."""


@dataclass(frozen=True)
class Pillar:
    keyword: str  # matched (case-insensitively) inside an opportunity line
    label: str  # human label shown in the audit
    bucket: str  # S / M / L
    hours: int  # catalog estimate


# The skill's effort catalog: the rough buckets a scoped quote is checked
# against. Ordered here is the tie-break order for equal-effort candidates.
CATALOG: tuple[Pillar, ...] = (
    Pillar("invoice", "Invoice & receipt capture", "S", 4),
    Pillar("attachment", "Attachment filing", "S", 3),
    Pillar("lead", "Lead intake & follow-up", "M", 8),
    Pillar("order", "Order status & tracking replies", "M", 8),
    Pillar("support", "Support-ticket triage", "M", 9),
    Pillar("feedback", "Feedback & review triage", "S", 4),
    Pillar("report", "Report auto-assembly", "M", 10),
    Pillar("approval", "Approval-gated drafts", "S", 6),
    Pillar("calendar", "Appointment scheduling", "S", 5),
    Pillar("inventory", "Stock-level reorder alerts", "M", 12),
    Pillar("brief", "Client-brief intake", "S", 4),
    Pillar("milestone", "Milestone acceptance tracking", "S", 3),
    Pillar("handover", "Handover-pack generation", "S", 5),
)


def _title(text: str) -> str:
    """The process name from an ``# Process: <name>`` line (any ``# `` line
    stands in if the process prefix is missing)."""
    for line in text.splitlines():
        if line.startswith("# Process:"):
            return line[len("# Process:"):].strip()
        if line.startswith("# "):
            return line[2:].strip()
    return "Untitled process"


def parse_sections(text: str) -> dict[str, str]:
    """Split the body into ``## ``-headed sections keyed by heading name."""
    sections: dict[str, str] = {}
    matches = list(SECTION_RE.finditer(text))
    for index, match in enumerate(matches):
        name = match.group(1).strip()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        sections[name] = text[match.end():end].strip()
    return sections


def missing_sections(sections: dict[str, str]) -> list[str]:
    return [name for name in REQUIRED_SECTIONS
            if not sections.get(name, "").strip()]


def _opportunities(sections: dict[str, str]) -> list[str]:
    block = sections.get("Automation opportunities", "")
    return [line[2:].strip() for line in block.splitlines()
            if line.strip().startswith("- ")]


def match_pillar(line: str) -> Pillar | None:
    """Longest-keyword match against the catalog; ties resolve to catalog
    order, so every input maps deterministically."""
    lowered = line.lower()
    best: Pillar | None = None
    for pillar in CATALOG:
        if pillar.keyword in lowered and (
            best is None or len(pillar.keyword) > len(best.keyword)
        ):
            best = pillar
    return best


def build_audit(text: str) -> str:
    """Render the six-section audit for one process description."""
    sections = parse_sections(text)
    missing = missing_sections(sections)
    if missing:
        raise AuditError(
            "process description is missing required section(s): "
            + ", ".join(missing)
        )

    entries: list[tuple[str, Pillar | None]] = [
        (line, match_pillar(line)) for line in _opportunities(sections)
    ]

    def sort_key(item: tuple[str, Pillar | None]) -> tuple[int, int, int]:
        _line, pillar = item
        if pillar is None:
            return (1, 0, 0)  # unmapped candidates sort last
        return (0, pillar.hours, CATALOG.index(pillar))

    ordered = sorted(entries, key=sort_key)

    lines: list[str] = [f"# Automation audit: {_title(text)}", ""]
    for output_name, input_name in (
        ("Business problem", "Business problem"),
        ("Scope in", "In scope"),
        ("Scope out", "Out of scope"),
        ("Success signal", "Success signal"),
    ):
        lines.append(f"## {output_name}")
        lines.append("")
        lines.append(sections[input_name])
        lines.append("")

    lines.append("## Automation candidates (ordered)")
    lines.append("")
    for index, (line, pillar) in enumerate(ordered, start=1):
        if pillar is None:
            lines.append(
                f"{index}. **{line}** — custom · effort TBD (scope first)"
            )
        else:
            lines.append(
                f"{index}. **{line}** — {pillar.label} · effort {pillar.bucket} "
                f"(~{pillar.hours}h)"
            )
    lines.append("")
    lines.append(
        "_Ordered quickest-first by catalog effort; effort figures are "
        "catalog estimates, not source figures._"
    )
    lines.append("")

    lines.append("## Rough effort estimate")
    lines.append("")
    matched = [pillar for _line, pillar in ordered if pillar is not None]
    total = sum(pillar.hours for pillar in matched)
    lines.append(
        f"Total: **~{total}h** across {len(matched)} catalog-mapped "
        "candidate(s) (validate with a scoped quote before committing)."
    )
    if len(matched) < len(ordered):
        lines.append("")
        lines.append(
            "Unmapped candidate(s) above need a scoped quote before an "
            "estimate is possible."
        )
    lines.append("")
    return "\n".join(lines)


def self_check() -> int:
    """Run every fixture process and fail if any output differs from
    ``fixtures/expected/`` or is not reproducible on a second run."""
    failures = 0
    cases = sorted(PROCESSES.glob("*.md"))
    for case in cases:
        source = case.read_text(encoding="utf-8")
        expected_path = EXPECTED / f"{case.stem}.audit.md"
        try:
            first = build_audit(source)
            second = build_audit(source)
        except AuditError as exc:
            print(f"FAIL {case.name}: {exc}")
            failures += 1
            continue
        expected = expected_path.read_text(encoding="utf-8")
        ok = first == second == expected
        print(
            f"{'PASS' if ok else 'FAIL'} {case.name} -> {expected_path.name} "
            f"(deterministic={first == second}, "
            f"matches-expected={first == expected})"
        )
        if not ok:
            failures += 1
    print(f"RESULT: {'PASS' if failures == 0 else 'FAIL'} "
          f"- {len(cases)} fixture(s) checked")
    return 0 if failures == 0 else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__.splitlines()[0],
    )
    parser.add_argument(
        "--audit", metavar="PATH",
        help="one process description file to audit (printed to stdout)",
    )
    parser.add_argument(
        "--self-check", action="store_true",
        help="compare fixtures/processes/ against fixtures/expected/ "
             "and fail on any diff or non-reproducible run",
    )
    args = parser.parse_args(argv)
    if args.audit:
        try:
            text = Path(args.audit).read_text(encoding="utf-8")
        except OSError as exc:
            print(f"audit error: cannot read {args.audit}: {exc}",
                  file=sys.stderr)
            return 2
        try:
            sys.stdout.write(build_audit(text))
        except AuditError as exc:
            print(f"audit error: {exc}", file=sys.stderr)
            return 2
        return 0
    return self_check()


if __name__ == "__main__":
    raise SystemExit(main())