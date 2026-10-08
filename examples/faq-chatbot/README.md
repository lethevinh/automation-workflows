# faq-chatbot — input contract & test data

These files document the **input contract** of the faq-chatbot demo lane —
they mirror the fixtures already embedded in the `Demo visitor turns` Code
node of [`n8n/faq-chatbot/workflow.json`](../../n8n/faq-chatbot/workflow.json).

**The primary way to run the workflow is still the one-click demo lane:**
import `workflow.json`, press **Test workflow**, and the embedded six turns
below execute against the real `Route verdict` switch and `Live write?`
gate — zero credentials needed. There is nothing to repoint: the demo
trigger is a Manual Trigger, so this file is documentation of the shape,
not a file the workflow reads. To add cases, edit the `turns` array inside
`Demo visitor turns`.

## Input shape

Each visitor turn is one item consumed by
`Demo verdict (mirrors AI contract)`:

```json
{
  "question": "What the visitor typed",
  "visitor_email": "known address, or empty string",
  "session_id": "chat session identifier",
  "sim": "demo-lane hint: answerable | gap | lead | empty | repeat | bad_ai"
}
```

`sim` exists **only** in the demo lane — it lets the deterministic Code
node reproduce every route without an OpenAI key. In production the Chat
Trigger supplies `chatInput`/`sessionId`, `Build FAQ prompt` normalizes
them into `question`/`visitor_email`/`session_id`, and
`Answer from FAQ only` + `Parse AI verdict` produce the same routed
`status`/`verdict` contract.

## What `test-data.json` covers

Order matters: `Demo verdict` tracks a per-run `seen` set, so the
duplicate case only fires after the same normalized question has appeared.

| # | Edge case | `sim` | Expected verdict |
|---|---|---|---|
| 1 | FAQ hit — "support hours" matches a seeded entry | `answerable` | `status: answered`, `verdict: answered` → `Visitor reply` |
| 2 | Miss — no FAQ entry covers it | `gap` | `status: logged`, `verdict: gap` → would append to `Unanswered` + owner email |
| 3 | Lead — visitor leaves an email in the message | `lead` | `status: logged`, `verdict: lead` → would append to `Leads` + owner email |
| 4 | Empty message — whitespace only | `empty` | `status: alerted`, `kind: missing-data` → graceful fallback reply |
| 5 | Duplicate — same question already seen this run | `repeat` | `status: alerted`, `kind: duplicate` → graceful fallback reply |
| 6 | Unparseable AI verdict — `__force_bad_ai__` simulates a broken model answer | `bad_ai` | `status: alerted`, `kind: failure` → graceful fallback reply |

Because every demo item carries `live: false`, gap/lead turns stop at
`Demo: record gap or lead` (which annotates what the write *would* do)
instead of `Log question or lead` → `Notify owner` — no sheet rows are
written and no emails are sent. `Owner digest` prints exactly one summary
per run: 3 processed turns (answered/gap/lead) and 3 alerts
(missing-data/duplicate/failure).
