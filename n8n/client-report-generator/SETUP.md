# client-report-generator — setup guide

Generate a week-over-week performance report per client from one config
sheet — Meta Ads, Google Ads and GA4 in, an AI-written summary out through
Gmail and/or Slack.

## What you need

| Requirement | Where to get it |
|---|---|
| Gmail credential | n8n → Credentials → Gmail → Google OAuth |
| Google Sheets credential | n8n → Credentials → Google Sheets → Google OAuth |
| OpenAI credential | platform.openai.com → API keys |
| Meta access token | Meta for Developers → your app → Marketing API token |
| Google Ads tokens | Google Ads API → access token + developer token |
| GA4 access token | Google Analytics Data API → OAuth token |
| Slack bot token | api.slack.com/apps → Bot token (chat:write) |

Provider tokens attach to the HTTP nodes as **n8n credentials** (see
Step 2) — nothing secret lives in the template and no instance
environment variables are needed, so the workflow also runs on n8n Cloud.

## Step 1 — Import

n8n → Workflows → Import from file → select `workflow.json`.

## Step 2 — Attach credentials

Attach Gmail, Google Sheets and OpenAI credentials to the nodes that ask
for them (credential picker on each node).

Each HTTP node then needs one generic credential — create it once in
n8n → Credentials and pick it on the node:

| Node | Credential type | What to enter |
|---|---|---|
| Fetch Meta Ads insights | **Header Auth** | name `Authorization`, value `Bearer <Meta access token>` |
| Fetch Google Ads metrics | **Custom Auth** | JSON `{"headers": {"Authorization": "Bearer <access token>", "developer-token": "<developer token>"}}` — both headers ride in one credential |
| Fetch GA4 report | **Header Auth** | name `Authorization`, value `Bearer <GA4 access token>` |
| Post report to Slack | **Header Auth** | name `Authorization`, value `Bearer <Slack bot token>` |

## Step 3 — Run the setup lane once

Press **play** on the orange **`SETUP — press play on this node once`**
trigger (bottom lane). It creates a Google Sheet named
**Weekly Client Reports** with two tabs and seed rows:

- `config` — one row per client: `client_id`, `client_name`, `enabled`,
  `src_meta_ads`, `src_google_ads`, `src_ga4`, `sink_gmail`, `sink_slack`,
  `recipients_email`, `slack_channel`, `meta_ad_account_id`,
  `google_ads_customer_id`, `ga4_property_id`, `delivery_mode`,
  `brand_name`, `brand_color`, `brand_logo_url`, `alert_threshold_pct`.
- `reports` — the sent-report ledger: `dedupe_key`
  (`client_id__kkkk-Wxx` — client id + ISO week), `client_id`,
  `report_week`, `sinks_sent`, `sent_at`. It powers idempotent re-runs.

The last node prints `spreadsheet_id` — copy it.

## Step 4 — One node, one value (plus one email)

Open the **Workflow Config** node and set `sheet_id` (from Step 3) — every
Sheets node resolves its document from here.

Then open the **Operator email** node (bottom lane, next to
`On workflow error`) and set `to` to your operator address. It lives in
its own node on purpose: Workflow Config never runs inside an
error-triggered execution, so the failure-alert address cannot come from
there. The same address also receives the weekly run digest — one node,
one value.

## Step 5 — Fill the config tab

One row per client. Set each `src_*`/`sink_*` cell to `yes` or `no` —
that cell alone decides whether a source is fetched or a sink is used for
that client. Fill the matching account-id columns for enabled sources and
the recipient columns for enabled sinks.

Optional per-client cells (all safe to leave empty):

- `delivery_mode` — `send` (default) mails the report; `draft` files it
  into the client's Gmail drafts for your review instead of sending.
- `brand_name` / `brand_color` / `brand_logo_url` — render a branded HTML
  header on the email report (defaults: client name, neutral color, no
  logo).
- `alert_threshold_pct` — a number like `15`: any metric whose WoW change
  is at or beyond that percent is marked **FLAGGED** in the report body
  and counted in the run digest. Empty means no flagging.

## Step 6 — Activate

Delete the bottom setup lane (optional), press **Test workflow** once to
watch the four-client demo run with zero credentials, then set the
workflow **Active**. It runs every Monday 09:00 (workflow timezone —
Settings → Timezone, shipped GMT).

Optional but recommended: Settings → **Error workflow** → pick this same
workflow — its `On workflow error` lane emails you if anything unhandled
ever fails.

## Weekly rhythm

- **Monday 09:00:** each enabled client's enabled sources are fetched,
  week-over-week deltas are computed (Code node — the AI writes prose
  around finished numbers only), the report is sent through the enabled
  sinks, and `reports` is upserted on `client_id + ISO week` so a re-run
  in the same week is skipped as a duplicate.
- **Digest:** every run ends with one digest — reports delivered, skipped,
  anomaly flags (`anomaly_flags` + `flagged_metrics`), and alerts (a
  source outage, a missing recipient, a duplicate). On live runs it is
  emailed to the **Operator email** address; demo runs produce the digest
  item but the `Digest is live?` gate keeps it off Gmail.

## API versions

Pinned against the providers' sunset schedules on 2026-10-07 (see
`spec.md` for sources): Meta Marketing API **v26.0** (v21.0 retires
2027-01-21), Google Ads API **v25** (v18 sunset; v22 sunsets October
2026), GA4 Data API **v1beta** (current). When a provider sunsets the
pinned version, update the version segment in the fetch node's URL.

## Troubleshooting

| Symptom | Fix |
|---|---|
| Sheets nodes say "no document" | `sheet_id` not pasted into Workflow Config (Step 4) |
| A source never runs | Its `src_*` cell is not `yes` in the client's row |
| Digest shows a `failure` alert | The named source fetch failed — check the credential attached to that node (Step 2); other clients were unaffected |
| Digest shows `duplicate` | That report already exists in `reports` — delete the ledger row to allow a re-send |
| Slack posted but digest shows a `failure` alert | Slack returned `ok:false` — the named API error (e.g. `channel_not_found`) tells you what to fix; the report was NOT marked sent |
| Error alerts or digest mails go to the wrong address | Edit `to` in the **Operator email** node — Workflow Config cannot supply it (it does not run inside error executions) |
| No digest email arrived | Digest mail is live-gated — demo/manual demo runs never send it; check the `Digest is live?` output shows `live: true` |
| Client got a draft, not an email | `delivery_mode` is `draft` — set it to `send` (or empty) to mail directly; drafts also count as delivered for the ledger |
| Email header shows wrong brand | Fix `brand_name`/`brand_color`/`brand_logo_url` cells; an invalid color falls back to the neutral default |
| Run at a wrong hour | Workflow Settings → Timezone — set yours |
| AI node 401 | Check the OpenAI credential |
| Slack silent | No Header Auth credential attached to the node, or `slack_channel` empty for the row |
