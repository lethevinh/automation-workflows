"""Extract structured fields from a parsed document and score confidence.

The extractor is rule-based and deterministic: the same raw block always
yields the same fields, the same confidence and the same reasons, so the
demo lane needs no LLM and no network. An item is ``high`` confidence only
when every required field is present and well-formed; anything else is
``low`` with an explicit, ordered list of reasons — the things a human
should look at before posting it to the ledger.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, InvalidOperation

from invoice_ledger_parse import RawDocument

#: Currencies the extractor understands. Anything else is flagged, because a
#: silently-misread currency corrupts the ledger.
KNOWN_CURRENCIES = frozenset({"USD", "EUR", "GBP"})

_DATE_FORMATS = ("%Y-%m-%d", "%Y/%m/%d", "%Y.%m.%d", "%d %b %Y", "%d %B %Y")

_CURRENCY_TOKEN_RE = re.compile(r"[$€£]|[A-Z]{3}", re.I)
_AMOUNT_BODY_RE = re.compile(r"[+-]?\d+(?:\.\d+)?")

#: A sane upper bound. Larger values are almost always a unit error and
#: deserve a human look rather than a silent ledger row.
MAX_AMOUNT = Decimal("1000000")


@dataclass(frozen=True)
class ExtractedRecord:
    """A document reduced to the fields the ledger actually needs."""

    source_file: str
    document_kind: str
    vendor: str
    reference: str
    issue_date: str
    due_date: str
    amount: Decimal | None
    currency: str
    confidence: str
    reasons: tuple[str, ...]


def normalize_date(value: str) -> str:
    """Return ``value`` as an ISO ``YYYY-MM-DD`` string, or ``""`` if unreadable."""
    text = value.strip()
    if not text:
        return ""
    for fmt in _DATE_FORMATS:
        try:
            return datetime.strptime(text, fmt).date().isoformat()
        except ValueError:
            continue
    return ""


def parse_amount(value: str) -> Decimal | None:
    """Parse a monetary amount, or ``None`` when it is not a clean number."""
    cleaned = _CURRENCY_TOKEN_RE.sub("", value).replace(",", "").strip()
    if not _AMOUNT_BODY_RE.fullmatch(cleaned):
        return None
    try:
        amount = Decimal(cleaned)
    except InvalidOperation:
        return None
    return amount if amount > 0 else None


def extract_record(raw: RawDocument) -> ExtractedRecord:
    """Extract fields from ``raw`` and grade confidence with explicit reasons."""
    vendor = (raw.kv.get("vendor") or "").strip()
    document_kind = raw.kind_hint
    reference = (raw.kv.get("invoice_no") or raw.kv.get("receipt_no") or "").strip()
    issue_date = normalize_date(raw.kv.get("issue_date", ""))
    due_date = normalize_date(raw.kv.get("due_date", ""))
    amount = parse_amount(raw.kv.get("amount", ""))
    currency = (raw.kv.get("currency") or "USD").strip().upper()

    reasons: list[str] = []
    if not vendor:
        reasons.append("missing vendor")
    if document_kind == "receipt" and not reference:
        reasons.append("missing receipt number")
    elif document_kind == "invoice" and not reference:
        reasons.append("missing invoice number")
    if not issue_date:
        reasons.append("issue date not parseable")
    if amount is None:
        reasons.append("amount not parseable")
    elif amount > MAX_AMOUNT:
        reasons.append("amount exceeds the 1,000,000 cap")
    if currency not in KNOWN_CURRENCIES:
        reasons.append("currency not recognized")

    confidence = "high" if not reasons else "low"
    return ExtractedRecord(
        source_file=raw.source_file,
        document_kind=document_kind,
        vendor=vendor,
        reference=reference,
        issue_date=issue_date,
        due_date=due_date,
        amount=amount,
        currency=currency if currency else "USD",
        confidence=confidence,
        reasons=tuple(reasons),
    )