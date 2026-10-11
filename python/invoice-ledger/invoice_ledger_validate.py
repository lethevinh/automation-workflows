"""Business-rule validation that runs after extraction.

Extraction grades completeness; this module grades well-formedness — the
rules that turn a plausible row into a ledger-safe one. Rules are purely
deterministic and time-free (no wall clock, no network), so the demo lane
and a production run decide identically.
"""

from __future__ import annotations

import re

from invoice_ledger_extract import ExtractedRecord

_REFERENCE_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9-]{0,31}")
_MAX_VENDOR_LENGTH = 80


def extra_reasons(record: ExtractedRecord) -> tuple[str, ...]:
    """Return validation failures beyond the extractor's own reasons."""
    reasons: list[str] = []
    if record.reference and not _REFERENCE_RE.fullmatch(record.reference):
        reasons.append("reference contains unsupported characters")
    if len(record.vendor) > _MAX_VENDOR_LENGTH:
        reasons.append("vendor name exceeds 80 characters")
    return tuple(reasons)