# Promise Ledger — Track Promises Made to You, Chase Before They Go Cold

**Platform:** n8n · **Category:** Founder Ops / Follow-up
**Outcome:** "I'll send it Friday" stops disappearing. Every promise lands
in a ledger, drafts its own chase email, and closes itself when the person
delivers.

![Workflow diagram](assets/diagram.svg)

*Architecture diagram — source [`assets/diagram.json`](assets/diagram.json), rendered with [archify](https://github.com/tt-a1i/archify)*

**Node graph** — generated from `workflow.json` (see `scripts/render-mermaid.py`):

<!-- mermaid:start -->
```mermaid
%%{init: {"theme":"base","themeVariables":{"fontFamily":"ui-monospace, SFMono-Regular, Menlo, monospace","fontSize":"13px","background":"#FFFFFF","primaryColor":"#FFFFFF","primaryBorderColor":"#CBD5E1","primaryTextColor":"#0F172A","lineColor":"#94A3B8","tertiaryColor":"#FFFFFF"}}}%%
flowchart TB
    n0(["When clicking 'Test workflow'"])
    n1["Demo inbox emails"]
    n2["Demo extract (mirrors AI contract)"]
    n3["Run digest"]
    n4(["Hourly tick (sweep at 08:00)"])
    n5["Workflow Config"]
    n6{"Lane entry"}
    n7["Fetch new inbox emails"]
    n8["Build extraction prompt"]
    n9["Extract promises (AI)"]
    n10["Parse commitment verdict"]
    n11{"Route intake"}
    n12["Merge write streams"]
    n13{"Live write?"}
    n14{"Write kind?"}
    n15[("Write ledger row")]
    n16[("Find open row")]
    n17["Pick open row"]
    n18{"Row matched?"}
    n19[("Mark done in ledger")]
    n20["Label email processed"]
    n21["Demo: record ledger write"]
    n22{"Skip is live?"}
    n23["Compose alert"]
    n24{"Alert is live?"}
    n25["Email owner: intake alert"]
    n26[("Read ledger rows")]
    n27["Classify aging"]
    n28["Sweep digest"]
    n29{"Digest worth sending?"}
    n30["Email owner: daily digest"]
    n31{"Route sweep"}
    n32["Merge chase streams"]
    n33["Build chase prompt"]
    n34["Draft chase email (AI)"]
    n35["Parse chase draft"]
    n36[("Queue chase for approval")]
    n37["Notify owner of queue"]
    n38[("Mark chased in ledger")]
    n39["Escalate to owner"]
    n40[("Mark escalated in ledger")]
    n41[("Create promise ledger")]
    n42["Seed headers and examples"]
    n43{"Route by tab"}
    n44["Columns for Commitments"]
    n45["Columns for Chase-Queue"]
    n46[("Write Commitments tab")]
    n47[("Write Chase-Queue tab")]
    n48["Print sheet id + next step"]
    n49(["On workflow error"])
    n50["Format error alert"]
    n51["Email owner: promise-ledger error"]
    n0 --> n1
    n1 --> n2
    n2 --> n11
    n2 --> n3
    n4 --> n5
    n5 --> n6
    n6 -->|"0"| n26
    n6 -->|"1"| n7
    n7 --> n8
    n8 --> n9
    n9 --> n10
    n10 --> n11
    n11 -->|"0"| n12
    n11 -->|"1"| n12
    n11 -->|"2"| n22
    n11 -->|"3"| n23
    n12 --> n13
    n13 -->|"true"| n14
    n13 -->|"false"| n21
    n14 -->|"0"| n16
    n14 -->|"1"| n15
    n16 --> n17
    n17 --> n18
    n18 -->|"true"| n19
    n18 -->|"false"| n20
    n15 --> n20
    n19 --> n20
    n23 --> n24
    n24 --> n20
    n24 --> n25
    n22 --> n20
    n26 --> n27
    n27 --> n31
    n27 --> n28
    n28 --> n29
    n29 --> n30
    n31 -->|"0"| n32
    n31 -->|"1"| n32
    n31 -->|"2"| n39
    n32 --> n33
    n33 --> n34
    n34 --> n35
    n35 --> n36
    n36 --> n37
    n37 --> n38
    n39 --> n40
    n41 --> n42
    n42 --> n43
    n43 -->|"0"| n44
    n43 -->|"1"| n45
    n44 --> n46
    n45 --> n47
    n46 --> n48
    n47 --> n48
    n49 --> n50
    n50 --> n51
    classDef trigger fill:#EFF6FF,stroke:#3B82F6,color:#0F172A
    classDef logic fill:#ECFDF5,stroke:#10B981,color:#0F172A
    classDef decide fill:#FFFBEB,stroke:#F59E0B,color:#0F172A
    classDef store fill:#F5F3FF,stroke:#8B5CF6,color:#0F172A
    classDef ai fill:#FDF2F8,stroke:#EC4899,color:#0F172A
    classDef external fill:#F8FAFC,stroke:#64748B,color:#0F172A
    classDef gate fill:#FEF2F2,stroke:#EF4444,color:#0F172A
    classDef disabled opacity:.55,stroke-dasharray:4 3
    class n0,n4,n49 trigger
    class n1,n2,n3,n5,n8,n10,n12,n17,n21,n23,n27,n28,n32,n33,n35,n42,n44,n45,n48,n50 logic
    class n6,n11,n13,n14,n18,n22,n24,n29,n31,n43 decide
    class n15,n16,n19,n26,n36,n38,n40,n41,n46,n47 store
    class n9,n34 ai
    class n7,n20,n25,n30,n37,n39,n51 external
```
<!-- mermaid:end -->

## The problem

People promise you things over email — documents, payments, intros — and
then go quiet. Tracking them means digging through your inbox; chasing them
means remembering who owes what, and for how long.

## The solution

- **Hourly intake** reads your inbox and extracts every concrete promise
  (who, what, due when — relative dates like "by Thursday" resolve
  correctly) into a Google Sheets `Commitments` ledger with live status:
  `open → reminded → chased → escalated → done`.
- **08:00 daily sweep** classifies open promises: due today → gentle
  reminder draft; overdue → firmer follow-up; 3+ days overdue → escalates
  straight to you.
- **Approval gate** — drafts land in a `Chase-Queue` tab; you approve
  before anything sends, so the automation can never embarrass you with a
  wrong chase.
- **Fulfillment detection** — when the person finally delivers, their
  reply closes the ledger row automatically.
- **Per-person aging digest** — see at a glance who habitually leaves
  commitments hanging.
- **One-click setup lane** provisions the spreadsheet itself.

Most "commitment tracker" templates scan your *sent* mail to track promises
*you* made. This one works the inbound direction — promises made *to* you —
and adds the missing half: outbound chasing with an approval gate,
fulfillment detection, and per-person aging.

## Stack & credentials

56 nodes — Google Sheets (×10), Gmail (×6), OpenAI (×2, `gpt-4o-mini`),
Switch, Merge, Schedule Trigger, Code.

Production needs Gmail + Google Sheets + OpenAI credentials — service and
credential types are enumerated in [.env.example](.env.example). The demo
lane needs none. See [SETUP.md](SETUP.md) (~5 min).

## Setup

1. Import `workflow.json`, attach the three credentials (Gmail OAuth2,
   Google Sheets OAuth2, OpenAI API key).
2. Press play once on `Create promise ledger` — the setup lane builds a
   **Promise Ledger — Follow-ups** spreadsheet with `Commitments` and
   `Chase-Queue` tabs, headers and example rows, and
   `Print sheet id + next step` outputs the `spreadsheet_id`.
3. Open `Workflow Config` (the only node you edit) and paste `sheet_id`,
   `label_id` — the ID of a Gmail label named `promises-processed` — and
   `owner_email`. Every Sheets and Gmail node reads from this node.
4. Delete the setup lane, press **Test workflow** once to watch the demo
   run offline, then set the workflow **Active**. Intake runs every hour;
   `Lane entry` routes the 08:00 tick (workflow timezone) to the chase
   sweep.

Full walkthrough: [SETUP.md](SETUP.md).

### Run it yourself (zero credentials)

Press **Test workflow** after import — `Demo inbox emails` fires six
sample emails and `Demo extract (mirrors AI contract)` emits the same
verdicts the live AI contract returns, so every intake route runs with no
credentials: a clear commitment, a newsletter that gets skipped, a vague
promise with no due date, a duplicate, an unparseable AI answer, and a
fulfillment reply.

The documented input contract — the fields each sample carries and the
verdict it should produce — lives in
[`examples/promise-ledger/`](../../examples/promise-ledger/)
([test-data.json](../../examples/promise-ledger/test-data.json)). The
one-click demo lane is the primary way to run it; the fixture documents
the shape — there is no trigger to repoint at a file.

## Verification

Container pilot on `n8n:latest` (zero credentials): digest 1 item, happy
path 5 items, missing-data/duplicate/failure alerts 3/3 — PASS. Live OpenAI
extraction verified against a real key: relative due dates resolved,
newsletters skipped, fulfillment replies close the right ledger row.

## Reliability & error handling

- **Retries on every external call:** all 19 credentialed nodes — every
  Google Sheets (×10), Gmail (×6) and OpenAI (×2) node — ship with
  `retryOnFail: true`, `maxTries: 3`, `waitBetweenTries: 1500`.
- **Live vs demo isolation:** three `$json.live` IF gates — `Live write?`,
  `Skip is live?`, `Alert is live?` — keep demo items away from every
  external write; the demo code nodes set `live: false`, so the demo lane
  reaches zero credentialed nodes.
- **Idempotent ledger writes:** `Write ledger row` and
  `Queue chase for approval` use `appendOrUpdate` matched on `dedupe_key`
  (a person+promise hash) — a repeated promise updates its row instead of
  duplicating it, and a re-chase updates the queue draft rather than
  stacking a second one.
- **Write-before-label idempotency:** `Label email processed` applies the
  `promises-processed` label only *after* a successful ledger write, and
  `Fetch new inbox emails` excludes labelled mail. `Write ledger row` and
  `Mark done in ledger` run with `onError: continueErrorOutput` — a failed
  write never reaches the label, so the unlabelled email is re-scanned on
  the next hourly tick instead of being lost.
- **Deterministic AI fallback:** `Parse commitment verdict` strict-parses
  the model's JSON — an unparseable verdict or a missing `has_promise`
  flag becomes an `alerted`/`failure` item, and a promise with no due
  date or `confidence < 0.6` becomes `alerted`/`missing-data`. Both route
  through `Compose alert` → `Alert is live?` → `Email owner: intake alert`
  instead of writing a bad row. Same contract on the chase side:
  `Parse chase draft` keeps an unparseable draft `pending-approval` and
  flags it for the owner.
- **Human approval gate:** `Queue chase for approval` writes AI drafts to
  the `Chase-Queue` tab as `pending-approval` and `Notify owner of queue`
  emails you. Nothing sends itself.
- **Fulfillment closes the right row:** `Find open row` → `Pick open row`
  → `Row matched?` → `Mark done in ledger` closes the *oldest* open row
  for the sender; an unmatched fulfillment is still labelled processed so
  it isn't re-scanned every hour.
- **Escalate once, not daily:** `Mark escalated in ledger` moves a 3+
  day-overdue row out of the active set after `Escalate to owner` fires —
  the alert cannot repeat.
- **One digest per run, suppressed when quiet:** `Run digest` and
  `Sweep digest` each aggregate a single summary per run, and
  `Digest worth sending?` skips the morning email entirely when nothing
  is due, overdue, escalated or flagged.
- **Error-alert lane included — wire once.** The export ships an
  `On workflow error` → `Format error alert` → `Email owner:
  promise-ledger error` lane that formats every unhandled failure into an
  owner email. It is **inert until wired**: the lane only fires when this
  workflow is selected as the Error Workflow in n8n's Workflow Settings —
  `settings.errorWorkflow` is not carried by the export. Until then,
  unhandled failures surface in n8n's execution list.

## Results & impact

### Evidence (verifiable from this repo)

| Result | Source |
|---|---|
| Zero-credential container pilot: digest exactly 1 item, happy path 5 items | `## Verification` |
| Missing-data / duplicate / failure alerts: 3/3 PASS | `## Verification` |
| Live OpenAI extraction verified against a real key — relative due dates resolved, newsletters skipped, fulfillment replies close the right row | `## Verification` |
| Retry coverage: 19/19 credentialed nodes (`retryOnFail`, `maxTries: 3`) | `workflow.json` |
| Error lane: `On workflow error` → `Format error alert` → `Email owner: promise-ledger error` (needs Error Workflow wiring) | `workflow.json` |
| Live/demo isolation: 3 `$json.live` gates; demo lane reaches 0 credentialed nodes | `workflow.json` |

### Business outcome

- Promises chased to done per month: <!-- owner-metric: count of ledger rows moving open → done per month -->
- Time recovered vs manual inbox tracking: <!-- owner-metric: hours per week previously spent digging for and chasing follow-ups -->

## Sanitization notes

Sanitized for public sharing: credential blocks, instance identifiers
(`meta.instanceId`, workflow `id`/`versionId`), timestamps and pinned data
were removed from `workflow.json`. Remaining placeholders are inert —
`PASTE_SPREADSHEET_ID_HERE`, `PASTE_LABEL_ID_HERE` and `owner@example.com`
inside `Workflow Config`; all demo-fixture addresses are `example.com`.

---

*Need something like this for your business?
[Contact me](../../README.md#hire-me)*
