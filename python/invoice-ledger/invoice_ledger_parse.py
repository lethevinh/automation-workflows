"""Parse a plain-text invoice/receipt message into stable fields.

The input contract is deliberately small and deterministic (no LLM in this
step): a plain-text email with a header block, a blank line, then a body of
``label: value`` lines. Recognised labels are ``invoice number``, ``receipt
number``, ``invoice date`` / ``date``, ``due date``, ``total due`` /
``amount paid`` / ``total``, ``currency``, and ``vendor`` / ``supplier`` /
``company`` / ``from``. The vendor is otherwise the first body line that is
not a field line.

Everything in this module is pure: the same text always parses to the same
:class:`RawDocument`, which is what lets the demo lane run fully offline.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

#: Email header labels that never carry document fields. The parser splits the
#: message at the first blank line; the header block is skipped entirely, so an
#: email's own ``Date:`` / ``From:`` headers can never be mistaken for document
#: fields.
_HEADER_RE = re.compile(
    r"^(from|to|cc|bcc|subject|reply-to|date|mime-version|content-type|"
    r"content-transfer-encoding|message-id|x-[a-z0-9-]+)\s*:",
    re.I,
)

#: Document field labels, tried in order per body line. First match wins and no
#: line is consumed twice.
_FIELD_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("invoice_no", re.compile(r"^invoice\s*(?:number|no\.?|#)\s*:\s*(.+)$", re.I)),
    ("receipt_no", re.compile(r"^receipt\s*(?:number|no\.?|#)\s*:\s*(.+)$", re.I)),
    (
        "issue_date",
        re.compile(r"^(?:invoice\s*(?:date|issue\s*date)|date)\s*:\s*(.+)$", re.I),
    ),
    ("due_date", re.compile(r"^(?:due\s*date|payment\s*due\s*date)\s*:\s*(.+)$", re.I)),
    (
        "amount",
        re.compile(r"^(?:total\s*(?:due|paid)|amount\s*(?:due|paid)?|total)\s*:\s*(.+)$", re.I),
    ),
    ("currency", re.compile(r"^currency\s*:\s*(.+)$", re.I)),
    ("vendor", re.compile(r"^(?:vendor|supplier|company)\s*:\s*(.+)$", re.I)),
)


@dataclass(frozen=True)
class RawDocument:
    """A message sliced into the raw pieces the extractor consumes."""

    source_file: str
    subject: str
    body_lines: tuple[str, ...]
    kv: dict[str, str]
    kind_hint: str


def _match_field(line: str) -> tuple[str, str] | None:
    for name, pattern in _FIELD_PATTERNS:
        match = pattern.match(line)
        if match:
            return name, match.group(1).strip()
    return None


def parse_document(text: str, source_file: str) -> RawDocument:
    """Parse ``text`` into a :class:`RawDocument` (deterministic, no IO)."""
    lines = [line.strip() for line in text.replace("\r\n", "\n").split("\n")]

    # Split at the first blank line: headers above, document body below. When
    # there is no blank line (a bare pasted text), everything is treated as
    # body and email-looking headers are skipped inside the body loop.
    split_at = 0
    found_blank = False
    for index, line in enumerate(lines):
        if not line:
            split_at = index
            found_blank = True
            break
    headers = lines[:split_at] if found_blank else []
    body = [line for line in lines[split_at:] if line]

    subject = ""
    for line in headers:
        if line.lower().startswith("subject:"):
            subject = line.split(":", 1)[1].strip()
            break

    # Only a bare pasted text (no blank line) can carry email-looking lines in
    # its body; when a header block is present, every body line is content.
    kv: dict[str, str] = {}
    vendor_hint = ""
    for line in body:
        if not found_blank and _HEADER_RE.match(line):
            continue
        field = _match_field(line)
        if field is not None:
            name, value = field
            if name == "vendor" and value:
                kv[name] = value
                continue
            kv.setdefault(name, value)
            continue
        if ":" not in line and not vendor_hint:
            vendor_hint = line

    if "vendor" not in kv and vendor_hint:
        kv["vendor"] = vendor_hint

    kind_hint = _kind_hint(kv, subject, body)
    return RawDocument(
        source_file=source_file,
        subject=subject,
        body_lines=tuple(body),
        kv=kv,
        kind_hint=kind_hint,
    )


def _kind_hint(kv: dict[str, str], subject: str, body: list[str]) -> str:
    if kv.get("invoice_no"):
        return "invoice"
    if kv.get("receipt_no"):
        return "receipt"
    haystack = " ".join([subject, *body]).lower()
    if "invoice" in haystack:
        return "invoice"
    if "receipt" in haystack:
        return "receipt"
    return ""


def field(kv: dict[str, str], name: str) -> str:
    """Read a parsed field, defaulting to ``""``."""
    return kv.get(name, "")