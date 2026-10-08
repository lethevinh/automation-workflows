# client-report-generator — sample input

The one-click demo lane in
[`n8n/client-report-generator`](../../n8n/client-report-generator/) already
replays this exact data: import `workflow.json`, press **Test workflow**,
done. Nothing needs repointing — the fixture embedded in the
`Demo config (fixture)` node *is* the demo input.

[`test-data.json`](test-data.json) documents the **input contract** — the
shape the workflow consumes, so you can build your own `config` tab rows
and, if you extend it, dock new source adapters.

## What's inside

1. **`config_row_shape`** — one fully populated example row: every column
   a `config` tab can carry, including the optional `delivery_mode`,
   `brand_*` and `alert_threshold_pct` cells the demo fixture leaves out
   (they default to `send`, no branding, no flagging). Two fixture-only
   fields are flagged as such: `sim_error_source` fakes a source outage,
   `already_sent` pre-seeds the dedupe check.
2. **`demo_config_rows`** — the four rows embedded verbatim in
   `Demo config (fixture)` (the code node adds `live: false` to each).
3. **`edge_cases`** — which edge case each row exercises and its verdict.
4. **`source_adapter_payloads`** — one payload per source adapter
   (Meta Ads, Google Ads, GA4): the raw API response shape the fetch node
   receives and `Normalize *` consumes, plus the adapter contract rows
   emitted downstream. Any adapter you dock at `Extension dock` must emit
   the same contract row — `Compute WoW deltas` then adds `delta_pct`
   deterministically.

## Edge cases exercised by the demo run

| client_id | What it exercises | Expected verdict |
|---|---|---|
| `acme` | all three sources + both sinks; `sim_error_source: meta_ads` fakes a Meta outage | one `failure` alert via `Compose source alert`; Google Ads + GA4 still report; delivered via Gmail + Slack |
| `boutique` | `already_sent: yes` pre-seeds the dedupe key | `Dedupe check` flags `is_duplicate` → `Already sent?` → `Compose duplicate alert`; nothing re-sent |
| `coachlee` | `sink_gmail: yes` but `recipients_email` empty | `Validate clients` → `missing-data` alert (no usable sink); row never reaches the engine |
| `pausedco` | `enabled: no` | `skipped` in `Validate clients`; one skipped line in the digest |

After the run, `Run digest` emits exactly one item — delivered, skipped,
alerts and anomaly flags. See the workflow README's Verification section
for the pilot numbers (digest 1 item, 16 happy-path items,
missing-data/duplicate/failure alerts 3/3 — PASS).

## The ledger input

Live runs also read a `reports` tab — the sent-report ledger that makes
re-runs idempotent. Rows are keyed on `dedupe_key` =
`client_id` + `__` + ISO week (e.g. `acme__2026-W42`), plus `client_id`,
`report_week`, `sinks_sent`, `sent_at`. An empty ledger is valid input —
`Dedupe check` treats it as "nothing sent yet", never as an error. To
permit a re-send, delete that client's row for the week.
