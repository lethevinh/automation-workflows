# FAQ Chatbot — Answers Visitors and Grows Its Own FAQ (With Approval)

**Platform:** n8n · **Category:** AI / Customer Support
**Outcome:** A public chatbot that answers only from your FAQ — and turns
every unanswered question into next week's better FAQ, but only after you
approve it.

![Workflow diagram](assets/diagram.svg)

*Architecture diagram — source [`assets/diagram.json`](assets/diagram.json), rendered with [archify](https://github.com/tt-a1i/archify)*

**Node graph** — generated from `workflow.json` (see `scripts/render-mermaid.py`):

<!-- mermaid:start -->
```mermaid
%%{init: {"theme":"base","themeVariables":{"fontFamily":"ui-monospace, SFMono-Regular, Menlo, monospace","fontSize":"13px","background":"#FFFFFF","primaryColor":"#FFFFFF","primaryBorderColor":"#CBD5E1","primaryTextColor":"#0F172A","lineColor":"#94A3B8","tertiaryColor":"#FFFFFF"}}}%%
flowchart TB
    n0(["When clicking 'Test workflow'"])
    n1["Demo visitor turns"]
    n2["Demo verdict (mirrors AI contract)"]
    n3["Owner digest"]
    n4["Workflow Config"]
    n5(["Website visitor chat"])
    n6[("Load FAQ answers")]
    n7["Merge question + FAQ"]
    n8["Build FAQ prompt"]
    n9["Answer from FAQ only"]
    n10["Parse AI verdict"]
    n11{"Route verdict"}
    n12["Visitor reply"]
    n13{"Live write?"}
    n14[("Log question or lead")]
    n15["Notify owner"]
    n16["Demo: record gap or lead"]
    n17["Compose alert"]
    n18["Reply to visitor"]
    n19(["Weekly gap review"])
    n20[("Read unanswered log")]
    n21["Cluster gaps"]
    n22["Draft FAQ entries"]
    n23["Owner weekly digest"]
    n24[("Append FAQ proposals")]
    n25[("Create FAQ spreadsheet")]
    n26["Seed headers and examples"]
    n27{"Route by tab"}
    n28[("Write FAQ tab")]
    n29[("Write Unanswered tab")]
    n30[("Write Leads tab")]
    n31[("Write FAQ-Pending tab")]
    n32["Print sheet id + next step"]
    n0 --> n1
    n1 --> n2
    n2 --> n11
    n2 --> n3
    n5 --> n7
    n5 --> n4
    n4 --> n6
    n4 --> n20
    n6 --> n7
    n7 --> n8
    n8 --> n9
    n9 --> n10
    n10 --> n11
    n11 -->|"0"| n12
    n11 -->|"1"| n13
    n11 -->|"2"| n13
    n11 -->|"3"| n17
    n13 -->|"true"| n14
    n13 -->|"false"| n16
    n14 --> n15
    n15 --> n18
    n16 --> n18
    n12 --> n18
    n17 --> n18
    n19 --> n4
    n20 --> n21
    n21 --> n22
    n22 --> n23
    n23 --> n24
    n25 --> n26
    n26 --> n27
    n27 -->|"0"| n28
    n27 -->|"1"| n29
    n27 -->|"2"| n30
    n27 -->|"3"| n31
    n28 --> n32
    n29 --> n32
    n30 --> n32
    n31 --> n32
    classDef trigger fill:#EFF6FF,stroke:#3B82F6,color:#0F172A
    classDef logic fill:#ECFDF5,stroke:#10B981,color:#0F172A
    classDef decide fill:#FFFBEB,stroke:#F59E0B,color:#0F172A
    classDef store fill:#F5F3FF,stroke:#8B5CF6,color:#0F172A
    classDef ai fill:#FDF2F8,stroke:#EC4899,color:#0F172A
    classDef external fill:#F8FAFC,stroke:#64748B,color:#0F172A
    classDef gate fill:#FEF2F2,stroke:#EF4444,color:#0F172A
    classDef disabled opacity:.55,stroke-dasharray:4 3
    class n0,n5,n19 trigger
    class n1,n2,n3,n4,n7,n8,n10,n12,n16,n17,n18,n21,n26,n32 logic
    class n11,n13,n27 decide
    class n6,n14,n20,n24,n25,n28,n29,n30,n31 store
    class n9,n22 ai
    class n15,n23 external
```
<!-- mermaid:end -->

## The problem

Most FAQ bots answer what they know and silently drop the rest. The gaps
never get fixed, and "self-learning" bots that auto-publish AI answers are
a brand risk.

## The solution

Two interlocking lanes plus a human gate:

- **Lane A — live chat:** a hosted Chat Trigger webchat; the model answers
  strictly from your Google Sheet FAQ (strict-JSON verdict, never
  improvising). Each turn routes: answered → instant reply; unanswered →
  logged to `Unanswered` and emailed to you; visitor leaves an email →
  captured to `Leads`; AI parse failure → alert path that still replies
  gracefully.
- **Lane B — weekly learning loop:** every Monday, clusters the unanswered
  log by frequency, has AI draft candidate FAQ entries, emails you the
  proposals, and appends them to `FAQ-Pending`. **You copy approved rows
  into `FAQ` — the bot only learns what you sign off.**
- **Lane C — demo:** Test workflow runs six visitor turns covering every
  route with zero credentials.
- **Lane D — one-click setup:** provisions the whole Google Sheet (4 tabs,
  headers, example rows) and prints the `spreadsheet_id` to paste once.

Why it's different from a typical FAQ template:

| Typical FAQ template | This workflow |
|---|---|
| Answers from KB, drops misses | Misses are logged, clustered, drafted into new FAQ entries |
| Auto-saves AI answers | Owner-approved write-back — no unprompted self-learning |
| Lead capture as an afterthought | Lead detection is a first-class route |

## Stack & credentials

40 nodes — Chat Trigger, OpenAI ×2, Google Sheets ×9, Gmail ×2, Schedule &
Manual Triggers, Switch, IF, Merge, Code.

Production needs three credentials (see [`.env.example`](.env.example) for
the full checklist):

| Service | n8n credential type | Nodes |
|---|---|---|
| Google Sheets | Google Sheets OAuth2 (or Service Account) | 9 |
| Gmail | Gmail OAuth2 | 2 |
| OpenAI | OpenAI API key | 2 |

The hosted webchat (`Website visitor chat`, a Chat Trigger) needs no
credential — activate the workflow and n8n gives you a public chat URL.
The demo lane needs none of the above.

## Setup

Full guide: [SETUP.md](SETUP.md) (~5 min). Short version:

1. **Import** `workflow.json` (n8n → Workflows → Import from File).
2. **Attach** the Google Sheets, Gmail and OpenAI credentials.
3. **Provision the data layer once** — in Lane D, press the play button on
   `Create FAQ spreadsheet`. It creates `FAQ Bot — Knowledge Base` with
   four tabs (`FAQ`, `Unanswered`, `Leads`, `FAQ-Pending`), headers and
   example rows, and `Print sheet id + next step` outputs the
   `spreadsheet_id`.
4. **Configure in one place** — open `Workflow Config` and replace
   `PASTE_SPREADSHEET_ID_HERE` and `owner@example.com`. Every Sheets and
   Gmail node in lanes A and B reads from there.
5. **Go live** — delete the demo and setup lanes (optional but tidy),
   activate the workflow, and embed the `Website visitor chat` public URL
   in your site.

## Customize *(optional)*

- `Workflow Config` is the single edit point — sheet id and owner email.
- The `FAQ` tab is the knowledge base — the bot answers strictly from its
  `q`/`a` rows; you grow it by copying approved rows out of `FAQ-Pending`.
- `Website visitor chat` exposes the widget title, subtitle and input
  placeholder as plain node options.
- `Cluster gaps` ranks misses by `repeat_count`; `Draft FAQ entries`
  prompts the model for the top 5 proposals — adjust the prompt text to
  change the drafting style.

## Verification

Container pilot on `n8n:latest` (zero credentials): digest exactly 1 item,
6 happy-path items, empty-message / duplicate / bad-AI branches all
verified — PASS.

### Run it yourself

The primary way to try this workflow is the **one-click demo lane** —
import `workflow.json`, press **Test workflow**, and `Demo visitor turns`
emits six chat turns that exercise every route with zero credentials.
`Demo verdict (mirrors AI contract)` decides deterministically, the items
flow through the real `Route verdict` switch and `Live write?` gate, and
`Owner digest` prints exactly one summary per run.

The input contract — the shape `Demo visitor turns` produces and
`Demo verdict` consumes — is documented in
[`examples/faq-chatbot/`](../../examples/faq-chatbot/), with
[`test-data.json`](../../examples/faq-chatbot/test-data.json) covering all
six edge cases: an FAQ hit, a miss (gap), a duplicate, an empty message, an
unparseable AI verdict (`__force_bad_ai__`), and lead capture. Production
turns carry the same routed shape minus the `sim` hint — the Chat Trigger
supplies `chatInput`/`sessionId` and `Build FAQ prompt` normalizes them.

## Reliability & error handling

Mechanisms that exist in `workflow.json`, by node name:

- **Live/demo isolation — one gate.** `Live write?` (IF) checks
  `$json.live` on every logged item. Demo turns from `Demo visitor turns`
  carry `live: false` and route to `Demo: record gap or lead` (Code) —
  the Sheets and Gmail writes never run. Production items get `live: true`
  in `Build FAQ prompt`. Only Lane C is credential-free: the weekly lane
  and the setup lane are production-only and always hit their credentials.
- **Owner-approved write-back.** `Draft FAQ entries` produces proposals
  only; `Append FAQ proposals` writes them to `FAQ-Pending`, never `FAQ`.
  The bot cannot publish an answer the owner did not copy over — no
  unprompted self-learning.
- **Miss logging with dedupe.** `Log question or lead` appends-or-updates
  the `Unanswered`/`Leads` tab keyed on `question` — a repeat ask raises
  `repeat_count` instead of writing a duplicate row.
- **Weekly gap clustering.** `Weekly gap review` (Monday 09:00) →
  `Read unanswered log` → `Cluster gaps` ranks by frequency →
  `Draft FAQ entries` → `Owner weekly digest` — one owner email per week.
- **Lead detection as a first-class route.** `Parse AI verdict` extracts
  the `contact` field from the model's strict-JSON verdict; `Route verdict`
  output 2 sends leads to `Log question or lead` → `Leads` tab and
  `Notify owner`.
- **Bad-AI path.** If the model's reply is not parseable JSON with a
  boolean `answered`, `Parse AI verdict` emits `status: 'alerted',
  kind: 'failure'`; `Compose alert` → `Reply to visitor` still returns a
  graceful fallback to the visitor — the chat never crashes. In the demo
  lane the alert is counted in `Owner digest`.
- **Graceful empty input.** A blank visitor message becomes
  `kind: 'missing-data'` on the same alert path — nothing is answered or
  logged.
- **Deterministic demo verdict.** `Demo verdict (mirrors AI contract)`
  returns the same `status`/`verdict` contract the live parser produces,
  so every route is testable without an OpenAI key.

Stated plainly — what is **not** here:

- **Retries on every live call.** All 13 credentialed nodes ship with
  `retryOnFail: true`, `maxTries: 3`, `waitBetweenTries: 1500` — a transient
  Sheets/Gmail/OpenAI failure is retried automatically. Retries absorb
  transient failures only; a persistent failure still fails the item.
- **No error workflow.** There is no Error Trigger and no alert path for
  workflow-level failures (`settings.errorWorkflow` is not wired); runtime
  failures are visible in n8n's execution list.

## Results & impact

**Evidence (repo-verifiable)** — container pilot on `n8n:latest`, zero
credentials:

| Check | Result |
|---|---|
| Owner digest per demo run | exactly 1 item — PASS |
| Visitor turns processed | 6 happy-path items across every route — PASS |
| Edge branches | empty-message, duplicate and bad-AI branches verified — PASS |
| Retry coverage | 13/13 credentialed nodes (`retryOnFail`, `maxTries: 3`) — `workflow.json` |

**Business outcomes** — to be supplied by the owner:

- <!-- owner-metric: questions answered per week / deflection rate vs. manual replies -->
- <!-- owner-metric: FAQ entries promoted from FAQ-Pending per month -->
- <!-- owner-metric: support hours saved per week -->

## Sanitization notes

This export ships with **no credential blocks** and no real configuration
values — `Workflow Config` carries only the placeholders
`PASTE_SPREADSHEET_ID_HERE` and `owner@example.com`. Instance identifiers
were stripped before publishing: `meta.instanceId`, the top-level workflow
`id`/`versionId`, 3 per-node `webhookId` values and `pinData` were removed.

---

*Need something like this for your business?
[Contact me](../../README.md#hire-me)*
