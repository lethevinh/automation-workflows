# FAQ Chatbot — Step-by-Step Setup

Total effort: **3 credentials + 1 button + 1 paste**. About 5 minutes.

## What you need first

| Credential | Where to get it |
|---|---|
| Google Sheets | n8n → Credentials → New → "Google Sheets OAuth2" (or Service Account) |
| Gmail | n8n → Credentials → New → "Gmail OAuth2" |
| OpenAI | platform.openai.com → API keys → paste into "OpenAI" credential |

## Step 1 — Import

n8n → Workflows → Import from File → pick `workflow.json`.

You will see a **START HERE** sticky top-left — it repeats these steps on the canvas.

## Step 2 — Build your data layer (one click)

Scroll to the bottom of the canvas → **Lane D**.

Hover the orange trigger node **"SETUP — press play on this node once"** → press the **play button** on that node.

It will:

- Create a Google Spreadsheet named `FAQ Bot — Knowledge Base`
- Create four tabs: `FAQ`, `Unanswered`, `Leads`, `FAQ-Pending`
- Write the headers and example rows into each tab
- Print the result in the last node:

```json
{
  "spreadsheet_id": "1AbC...",
  "spreadsheet_url": "https://docs.google.com/spreadsheets/d/1AbC...",
  "next_step": "..."
}
```

Copy the `spreadsheet_id`.

## Step 3 — One paste, one email

Open the **Workflow Config** node (top of Lane A). Edit two values:

```js
sheet_id: '1AbC...',          // ← paste here
owner_email: 'you@you.com',   // ← alerts + weekly digest go here
```

Every Google Sheets and Gmail node in lanes A and B reads these — no other node needs editing.

## Step 4 — Go live

1. Delete Lane D (optional but tidy).
2. Toggle the workflow **Active**.
3. Open **Website visitor chat** → copy the public chat URL → embed it in your site, or share it directly.

## Check before going live (optional, zero credentials)

Press **Test workflow** — the demo lane simulates six visitor turns (answered, unanswered, lead, empty message, repeat, bad AI answer) and prints a run digest. Nothing is written to your sheet.

## What each tab is for

| Tab | Written by | Contains |
|---|---|---|
| `FAQ` | **You** (and approved proposals) | `q`, `a` — the only source the bot answers from |
| `Unanswered` | Workflow | Questions the bot could not answer; repeats update `repeat_count` |
| `Leads` | Workflow | Visitors who left an email |
| `FAQ-Pending` | Weekly lane | AI-drafted FAQ entries awaiting your approval |

## Weekly rhythm

Every Monday 09:00: the bot clusters the `Unanswered` log, drafts FAQ entries for the most-asked gaps, emails you the digest, and parks proposals in `FAQ-Pending`. **You approve by copying a row into `FAQ`** — the bot never publishes an answer you did not sign off.

## Troubleshooting

| Symptom | Fix |
|---|---|
| SETUP node errors on credential | Attach Google Sheets credential first (Step 1) |
| Chat answers "I don't know" to everything | `sheet_id` in Workflow Config is wrong, or the `FAQ` tab is empty |
| No owner email arrives | `owner_email` in Workflow Config; check Gmail credential |
| Bot repeats itself to same visitor | Normal until FAQ grows — check `Unanswered` tab after Monday |
