# Video script — Promise Ledger demo (~3.5 min)

Target: one watchable pass, no editing tricks. Voiceover EN; captions on
(Loom auto-generates). All claims below are repo-verifiable — say only
what the workflow actually does.

**Setup before recording:**
- Clean n8n canvas, browser at 1080p, zoom so ~10 nodes are legible.
- Open `examples/promise-ledger/test-data.json` in a side tab.
- Have a Google Sheet + Gmail ready to show live artifacts, or keep the
  whole run inside the demo lane (zero credentials).
- Notifications off, only the n8n tab visible.

---

## [0:00–0:25] Hook — the pain

**VO:** "Someone emails you a promise — 'I'll send the contract Friday',
'payment goes out Monday'. Three weeks later it's buried in your inbox
and it's awkward to chase. I built a system that never forgets for me."

**Visual:** n8n canvas, full workflow visible at low zoom. Cursor rests
on the workflow name.

## [0:25–0:55] What it is

**VO:** "This is Promise Ledger — a 60-node n8n workflow. It reads
incoming email, extracts commitments with an AI step, writes them to a
ledger, and drafts a polite chase when a promise ages past its date. The
key design decision: the AI drafts — it never sends. Every chase waits
for my approval."

**Visual:** slow pan across the canvas — intake lane, ledger writes,
sweep/digest lane, error lane at the bottom. Don't narrate nodes yet.

## [0:55–2:00] One email's journey (the demo lane)

**VO:** "Let me run it. This workflow ships a demo lane — zero
credentials, just press Test."

- Click **Test workflow** (`When clicking 'Test workflow'` trigger).
- Zoom to `Demo inbox emails` — "fixture emails, three realistic cases."
- Zoom to `Demo extract (mirrors AI contract)` — "the AI call is stubbed
  in demo mode; in production this is an OpenAI extraction node."
- Follow the flow: `Lane entry` → `Parse commitment verdict` →
  `Route intake` → ledger write. **VO:** "Each promise lands in a Google
  Sheet — who, what, when, extracted verbatim plus a deadline."
- Show the ledger rows (demo records or the real Sheet).
- Sweep side: `Classify aging` → `Sweep digest` → `Email owner: daily
  digest`. **VO:** "Every morning it re-scores the ledger and sends me
  one digest — not forty pings."

## [2:00–2:45] The gate — brand moment

**VO:** "Here's the part I care about most. When a promise goes cold,
the AI drafts the follow-up email — and then it *stops*."

- Zoom: `Draft chase email (AI)` → `Queue chase for approval` →
  `Notify owner of queue`.
- Show the Chase-Queue tab: draft sitting in `pending`.
- **VO:** "Nothing leaves my inbox until I flip this row to approved.
  Reputation is at stake, so a human stays in the loop — that's the
  design, not a limitation."

## [2:45–3:15] Failure handling

- Zoom bottom lane: `On workflow error` → `Format error alert` →
  `Email owner: promise-ledger error`.
- **VO:** "Every credentialed node retries — 19 of 19 in this workflow.
  And if the whole run fails, this error lane emails me — it arms once
  the workflow is set as the Error Workflow in settings. Documented,
  not implied."
- Optionally point at a `retryOnFail` parameter on a Gmail node.

## [3:15–3:45] Close + CTA

**VO:** "Everything you saw is in the repo — importable, documented,
runs with zero credentials. If a manual process is eating your week,
send me two sentences about it — I'll reply with what I'd automate
first. Link below."

**Visual:** return to full canvas → cut to repo README.

---

## Shot checklist

| # | Shot | Node focus |
|---|---|---|
| 1 | Full canvas overview | whole graph |
| 2 | Test run start | `When clicking 'Test workflow'` |
| 3 | Fixture data | `Demo inbox emails` |
| 4 | Extraction | `Demo extract (mirrors AI contract)` |
| 5 | Routing | `Parse commitment verdict` → `Route intake` |
| 6 | Ledger write | `Write ledger row` / ledger tab |
| 7 | Digest | `Email owner: daily digest` |
| 8 | Approval gate | `Queue chase for approval`, Chase-Queue tab |
| 9 | Error lane | `On workflow error` → Gmail alert |
| 10 | Outro | canvas → repo |

## Don'ts

- No invented numbers ("saved X hours") — pilot metrics go in once real.
- No panning over all 60 nodes — viewers lose the thread.
- No music bed; voice + screen only.
- If a live AI call is shown, keep the API key field off-screen.
