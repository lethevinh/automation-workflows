# invoice-ledger — sample input

`test-data.json` documents the **input contract** for
[`python/invoice-ledger`](../../python/invoice-ledger/): the nine bundled
`fixtures/inbox/` messages and the verdict the deterministic pipeline produces
for each one. Every message is plain text — an email header block, a blank
line, then a `label: value` body — the exact shape the demo lane reads.

## How to run

The credential-free demo lane is the primary path:

```bash
cd python/invoice-ledger
python3 invoice_ledger_cli.py --demo
# RESULT: PASS - the demo ledger exactly matches fixtures/expected/ledger.csv.
```

It processes exactly these nine fixtures with a fixed `as-of 2026-09-30` and
writes `./demo-out/`. Nothing to install and no network call; this file exists
to document the row shape and the verdict each message produces, e.g. if you
wire a real folder watch or mail-to-folder bridge later.

## Input shape

| Field | Type | Used by |
|---|---|---|
| `invoice_no` / `receipt_no` | string | `extract` (reference, kind) and the ledger dedupe key |
| `issue_date` | string | `extract` — accepted as `YYYY-MM-DD`, `YYYY/MM/DD`, `YYYY.MM.DD`, `DD Mon YYYY` |
| `due_date` | string (optional) | the overdue check that decides chase drafts |
| `amount` | string | `extract` — `1,250.00` / `€120.00` style; unparseable values are reviewed |
| `currency` | string (default `USD`) | the currency guard (USD/EUR/GBP recognised) |

The parser reads `label: value` lines from the body only — an email's own
`From:` / `Date:` headers are never mistaken for document fields. The vendor is
the body line carrying the company name, or a `Vendor:` label.

## Samples → expected verdicts

| # | File | Edge case | Expected verdict |
|---|---|---|---|
| 1 | 01-invoice-acme.txt | Clean invoice, overdue at as-of | **posted** → ledger row + `chase-INV-1001.txt` draft |
| 2 | 02-receipt-globex.txt | Clean receipt | **posted** → ledger row |
| 3 | 03-invoice-acme-duplicate.txt | Same invoice no. as #1 | **skipped** → `duplicate of 'acme facilities co\|INV-1001'` |
| 4 | 04-receipt-globex-duplicate.txt | Same receipt no. as #2 | **skipped** → `duplicate of 'globex corp\|RCT-2001'` |
| 5 | 05-invoice-no-number.txt | Missing invoice number | **reviewed** → `missing invoice number` |
| 6 | 06-receipt-bad-amount.txt | Amount not a clean number | **reviewed** → `amount not parseable` |
| 7 | 07-invoice-bad-date.txt | Date unreadable | **reviewed** → `issue date not parseable` |
| 8 | 08-invoice-umbrella.txt | Clean invoice, not overdue at as-of | **posted** → no draft |
| 9 | 09-receipt-initech.txt | Clean receipt, EUR | **posted** → ledger row |

Expected digest — `posted=4 skipped=2 reviewed=3 drafts=1 ledger_rows=4`, and
re-running the demo in the same folder leaves the ledger row count unchanged
(idempotency). All vendors and amounts are synthetic and every address uses a
`*.example` placeholder; no real billing data.