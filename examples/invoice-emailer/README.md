# invoice-emailer — sample input

`test-data.json` documents the **input contract** for
[`n8n/invoice-emailer`](../../n8n/invoice-emailer/): one JSON object per
invoice, the same shape the workflow's `Intake: load invoices` Code node emits.

## How to run

The one-click demo lane is the primary path: import
`n8n/invoice-emailer/workflow.json` and click **Test workflow** — the bundled
intake node emits this batch, so both branches run immediately. There is
nothing to repoint and nothing to configure; this file exists to document the
row shape and the verdict each invoice produces, e.g. if you wire a real folder
watch or Sheet read later.

## Input shape

| Field | Type | Used by |
|---|---|---|
| `invoice_no` | string | `Lookup customer + dedup` (matches, dedups) and `Compose invoice email` (subject/body) |
| `customer_key` | string | `Lookup customer + dedup` — the key into the customer map |
| `pdf_file` | string | carried through `Lookup …` and read by `Compose invoice email` as the attachment |

All three fields are read by a demo Code node: `Lookup …` reads `invoice_no`
and `customer_key` and spreads the rest (`{ ...d, … }`), so `pdf_file` reaches
`Compose …`, which reads it as the attachment. Any extra fields you carry
through are passed along untouched.

## Samples → expected verdicts

| # | Invoice | `customer_key` | Edge case | Expected verdict |
|---|---|---|---|---|
| 1 | INV-1001 | `acme` | Clean row | **Composed** → `billing@acme.example`, subject `Invoice INV-1001 — Acme Facilities` |
| 2 | INV-1002 | `globex` | Clean row | **Composed** → `ap@globex.example`, subject `Invoice INV-1002 — Globex Corp` |
| 3 | INV-1003 | `unknown_co` | Unknown customer | Alerted → `no customer record for key 'unknown_co'` |
| 4 | INV-1001 | `acme` | Duplicate invoice number (same as #1) | Alerted → `duplicate of INV-1001 — already processed` |

Expected digest — exactly one item from `Merge branches` → `Daily digest to owner`:

> `Run complete: 2 invoice(s) composed, 2 alert(s)`

All customer addresses use `*.example` placeholders and all invoices are
synthetic; no real recipient or billing data.
