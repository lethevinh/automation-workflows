# csv-cleaner — sample input

`test-data.json` documents the **input contract** for
[`n8n/csv-cleaner`](../../n8n/csv-cleaner/): one JSON object per row, the same
shape the workflow's `Intake: demo data` Code node emits.

## How to run

The one-click demo lane is the primary path: import
`n8n/csv-cleaner/workflow.json` and click **Test workflow** — the bundled
intake node emits this batch, so every branch runs immediately. There is
nothing to repoint and nothing to configure; this file exists to document the
row shape and the verdict each row produces, e.g. if you wire a real CSV or
Sheet read later.

## Input shape

| Field | Type | Rule applied by `Process` |
|---|---|---|
| `name` | string | Required — empty or missing → quarantined as `missing name` |
| `email` | string | Required; must match the email regex or it is quarantined as `invalid email`; the second occurrence of an address in a run → quarantined as `duplicate email` |

Only `name` and `email` are consumed. Any extra columns you carry through are
passed along untouched — `Process` spreads the incoming object
(`{ ...d, ok, reason }`), so downstream nodes still see them.

## Samples → expected verdicts

| # | Row | Edge case | Expected verdict |
|---|---|---|---|
| 1 | Ana `ana@acme.example` | Clean row | **Clean** — routed to `Clean row` |
| 2 | Bo `not-an-email` | Malformed email | Quarantined → `not-an-email: invalid email` |
| 3 | Cid `cid@x.example` | Clean row | **Clean** — routed to `Clean row` |
| 4 | Ana2 `ana@acme.example` | Duplicate address (same as #1) | Quarantined → `ana@acme.example: duplicate email` |
| 5 | `""` `no@name.example` | Missing `name` | Quarantined → `no@name.example: missing name` |
| 6 | Dee `dee@y.example` | Clean row | **Clean** — routed to `Clean row` |

Expected digest — exactly one item from `Merge branches` → `Digest to owner`:

> `Run complete: 3 item(s) cleaned, 3 alert(s)`

All addresses use `*.example` placeholders; no real recipient data.
