# promise-ledger — input contract & sample data

`test-data.json` documents the shape of one inbound email as consumed by
the workflow's demo lane — the `Demo inbox emails` code node in
[`n8n/promise-ledger/workflow.json`](../../n8n/promise-ledger/workflow.json)
ships this same fixture embedded, so **the primary way to run it is to
import the workflow and press "Test workflow"** — six emails, zero
credentials, every intake route exercised. There is no trigger to repoint
at this file; it is the documented contract, not a data source.

## Input shape

Each sample is one inbox email with four fields:

| Field | Type | Meaning |
|---|---|---|
| `subject` | string | Email subject line |
| `from` | string | Sender address — becomes `person`, feeds `dedupe_key` |
| `body` | string | Email body sent to the extractor |
| `sim` | string | Demo-router key the `Demo extract (mirrors AI contract)` node maps to a verdict — stands in for the live AI output |

The demo node adds `message_id` (`demo-<sim>`), `origin: "demo"` and
`live: false` per item — `live: false` is what the three `$json.live`
gates (`Live write?`, `Skip is live?`, `Alert is live?`) check before any
external write.

On the live lane the same items come from `Fetch new inbox emails`
(unread, unlabelled inbox mail), `Build extraction prompt` sets
`live: true`, and `Extract promises (AI)` + `Parse commitment verdict`
produce the verdicts the `sim` field mirrors.

## Samples and expected verdicts

| # | `sim` | Edge case | Expected verdict |
|---|---|---|---|
| 1 | `clear_promise` | Concrete promise with a deadline | `commitment` → ledger row `open` (demo: `Demo: record ledger write`; live: `Write ledger row` appendOrUpdate on `dedupe_key`, then labelled) |
| 2 | `no_promise` | Newsletter / non-promise | `skipped` (`no-promise`) → `Skip is live?`; live runs label it so it is never re-scanned |
| 3 | `vague_promise` | Promise with no due date (missing data) | `alerted` (`missing-data`) → owner intake alert on live lane |
| 4 | `repeat` | Same promise from the same sender again | `alerted` (`duplicate`) — on live lane the `dedupe_key` upsert updates the existing row instead of duplicating it |
| 5 | `bad_ai` | Unparseable AI verdict — `__force_bad_ai__` in the body simulates it without an API key | `alerted` (`failure`) → `Email owner: intake alert`; nothing is written |
| 6 | `fulfillment` | Reply delivering on an earlier promise | `fulfillment` → live lane closes the oldest open row for that sender (`Find open row` → `Pick open row` → `Row matched?` → `Mark done in ledger`) |

## Expected demo output

One `Run digest` item per run — for the six samples: 6 messages scanned,
3 alerts (samples 3–5), 1 commitment, 1 fulfillment, 1 skipped. Container
pilot result: digest exactly 1 item, happy path 5 items, alerts 3/3 — PASS
(see the workflow README's Verification section).
