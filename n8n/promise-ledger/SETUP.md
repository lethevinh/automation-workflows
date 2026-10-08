# promise-ledger — setup guide

Track what people promise you in email and chase it before the deadline.

## What you need (3 credentials)

| Credential | Where to get it |
|---|---|
| Gmail | n8n → Credentials → Gmail → Google OAuth (n8n connects for you) |
| Google Sheets | n8n → Credentials → Google Sheets → Google OAuth |
| OpenAI | platform.openai.com → API keys → paste the key |

## Step 1 — Import

n8n → Workflows → Import from file → select `promise-ledger.json`.

## Step 2 — Attach credentials

Attach the 3 credentials to the nodes that ask for them
(Gmail / Google Sheets / OpenAI node types show a credential picker).

## Step 3 — Run the setup lane once

Press **play** on the **`Create promise ledger`** node (bottom lane — it
has no incoming edges; run it via its play button). It creates a Google Sheet named
**Promise Ledger — Follow-ups** with two tabs, headers, and example rows:

- `Commitments` — the ledger: `dedupe_key` (person+promise hash),
  `message_id` (Gmail source pointer), person, promise, due_date, status
  (`open / reminded / chased / escalated / done`), confidence,
  chase_count, source_link, created_at, last_nudged_at, closed_at.
- `Chase-Queue` — AI-drafted follow-ups waiting for your approval
  (keyed by `dedupe_key` so a second promise never overwrites a draft).

The final node prints `spreadsheet_id` — copy it.

> **Upgrade note:** a ledger created by a Revision-2-or-earlier setup has
> no `dedupe_key`/`message_id` columns — the upsert/update nodes match on
> `dedupe_key`, so either re-run the setup lane into a fresh sheet, or add
> both columns (and a `dedupe_key` value per existing row) by hand.

## Step 4 — One node, three values

Open the **Workflow Config** node. Set `sheet_id` (from Step 3),
`label_id` (the Gmail label ID below), and `owner_email` to your address.
Every Sheets and Gmail node reads these — this is the only node you edit.

## Step 5 — Activate

Delete the bottom setup lane (optional), press **Test workflow** once to
watch the six-email demo run offline, then set the workflow **Active**.

## Daily rhythm

- **Every hour:** new inbox mail is scanned; promises land in
  `Commitments` (status `open`); processed mail gets the
  `promises-processed` label. Unparseable AI answers and vague promises
  email you an intake alert.
- **At 08:00** (workflow timezone — Settings → Timezone, shipped as GMT):
  the sweep classifies open rows — due-today drafts → `reminded`,
  overdue drafts → `chased` in `Chase-Queue`; 3+ days overdue emails you
  directly and marks the row `escalated` — escalation fires **once**; an
  `escalated` row is not chased again until you set it back or close it.
  The morning digest email summarizes due/overdue/escalated + aging by
  person, and is skipped entirely on quiet mornings.
- **You:** open `Chase-Queue`, approve a draft by sending it (copy to
  Gmail), or delete the row. Nothing sends without you.
- When someone delivers, their reply closes the row automatically.

## Create the Gmail label (one time)

Gmail → Settings → Labels → New label → `promises-processed`.
Then copy its **label ID** (Gmail URL shows it as `…/#label/promises-processed`,
or run an n8n Gmail node → resource `label` → Get All). Paste it into
`label_id` in Workflow Config — Gmail's API needs the ID, not the name.

## Troubleshooting

| Symptom | Fix |
|---|---|
| Sheets nodes say "no document" | `sheet_id` not pasted into Workflow Config (Step 4) |
| Nothing is scanned | Create the `promises-processed` label AND paste its ID into `label_id` |
| Label step errors 400 | `label_id` holds a name, not an ID — copy the label ID |
| Sweep runs at a wrong hour | Workflow Settings → Timezone — set yours |
| AI node 401 | Check the OpenAI credential key |
| Chase drafts missing | `Chase-Queue` tab was renamed — keep the name |
