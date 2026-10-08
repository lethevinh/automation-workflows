# Daily Cash Tally — Till Cash-Leak Monitor with Escalation

**Platform:** n8n · **Category:** Operations / Finance
**Outcome:** Not just "was today short" — it catches the drawer that comes
up short *every week*, and escalates it to a different channel.

![Workflow diagram](assets/diagram.svg)

*Architecture diagram — source [`assets/diagram.json`](assets/diagram.json), rendered with [archify](https://github.com/tt-a1i/archify)*

**Node graph** — generated from `workflow.json` (see `scripts/render-mermaid.py`):

<!-- mermaid:start -->
```mermaid
%%{init: {"theme":"base","themeVariables":{"fontFamily":"ui-monospace, SFMono-Regular, Menlo, monospace","fontSize":"13px","background":"#FFFFFF","primaryColor":"#FFFFFF","primaryBorderColor":"#CBD5E1","primaryTextColor":"#0F172A","lineColor":"#94A3B8","tertiaryColor":"#FFFFFF"}}}%%
flowchart TB
    n0(["When clicking 'Test workflow'"])
    n1(["Nightly 21:30"])
    n2["Demo till log (entries + history)"]
    n3[("Read today's till entries")]
    n4[("Read prior-30d till log")]
    n5["Merge intake: entries + history"]
    n6["Reconcile, score history, escalate repeats"]
    n7{"Route outcome"}
    n8[("Append verdict to till log")]
    n9["Email owner alert"]
    n10["Escalation ping"]
    n11[("Park row in quarantine")]
    n12["Send daily digest"]
    n13["Optional AI: phrase owner alert"]
    n14["Optional AI: narrate daily digest"]
    n0 --> n2
    n1 --> n3
    n1 --> n4
    n2 --> n6
    n3 --> n5
    n4 --> n5
    n5 --> n6
    n6 --> n7
    n7 -->|"0"| n8
    n7 -->|"1"| n13
    n7 -->|"2"| n10
    n7 -->|"3"| n11
    n7 -->|"4"| n14
    n13 --> n9
    n14 --> n12
    classDef trigger fill:#EFF6FF,stroke:#3B82F6,color:#0F172A
    classDef logic fill:#ECFDF5,stroke:#10B981,color:#0F172A
    classDef decide fill:#FFFBEB,stroke:#F59E0B,color:#0F172A
    classDef store fill:#F5F3FF,stroke:#8B5CF6,color:#0F172A
    classDef ai fill:#FDF2F8,stroke:#EC4899,color:#0F172A
    classDef external fill:#F8FAFC,stroke:#64748B,color:#0F172A
    classDef gate fill:#FEF2F2,stroke:#EF4444,color:#0F172A
    classDef disabled opacity:.55,stroke-dasharray:4 3
    class n0,n1 trigger
    class n2,n5,n6 logic
    class n7 decide
    class n3,n4,n8,n9,n10,n11,n12,n13,n14 disabled
```
<!-- mermaid:end -->

> An earlier zero-credential version exists in git history — this is the
> production-shaped rebuild with real service nodes and cross-run state.

## The problem

A single over-tolerance night is a blip. The real leak is a pattern: same
staff, same shift, same small shortfall — invisible if every alert looks
identical. Meanwhile malformed entries silently drop, and nobody notices
the days that were never submitted at all.

## The solution

A production-shaped reconciliation pipeline with five routed outcomes:

- **30-day history scoring** — each discrepancy is scored against the prior
  month's log, so repeat offenses escalate instead of arriving as yet
  another routine alert
- **First offense** → email the owner; **repeat offender** → Telegram
  escalation
- **Quarantine lane** — malformed or duplicate rows park in a quarantine
  sheet for reprocessing instead of dropping silently
- **Gap detection** — infers unsubmitted days from sequence gaps
- **One digest per run** carrying the cumulative 30-day leak total
- **Optional AI phrasing** — two disabled OpenAI nodes write the alert
  wording and narrate the digest; the deterministic logic stays in charge
  of every verdict

## Stack & credentials

20 nodes — Google Sheets, Gmail, Telegram, Switch, Merge, Schedule Trigger,
optional OpenAI. Nine nodes call external services:

| Nodes | Service | n8n credential type |
|---|---|---|
| `Read today's till entries`, `Read prior-30d till log`, `Append verdict to till log`, `Park row in quarantine` | Google Sheets | Google Sheets OAuth2 |
| `Email owner alert` | Gmail | Gmail OAuth2 |
| `Escalation ping`, `Send daily digest` | Telegram | Telegram bot token |
| `Optional AI: phrase owner alert`, `Optional AI: narrate daily digest` | OpenAI | OpenAI API key |

See [`.env.example`](.env.example) for the per-node checklist (credential to
attach, placeholder to replace) before going live.

**Zero credentials for the demo**: all nine service nodes ship
`disabled: true` and pass demo data through untouched — the workflow runs
end-to-end before you connect anything.

## Setup

1. Import `workflow.json`, click **Test workflow** — the demo lane covers
   every branch: clean shift, escalated repeat offender, duplicate, missing
   `counted_cash`, three-day submission gap.
2. To go live: a Google Sheet as the till log (tabs: `today`, `history`,
   `results`, `quarantine`), Gmail for first-offense alerts, Telegram for
   escalations/digest. Enable the greyed-out nodes and attach credentials —
   then set the `chatId` placeholder on `Escalation ping` and
   `Send daily digest`, point `Email owner alert` at the owner's address,
   and remove the `Demo till log (entries + history)` node so the two
   Sheet reads feed `Merge intake: entries + history` instead.
3. Optional: attach an OpenAI credential and enable the two AI phrasing
   nodes. Verdicts stay deterministic either way — enabling only changes
   the wording (remap the downstream message fields per the node notes).

### Run it yourself

The one-click demo lane stays the primary way to run this: import, press
**Test workflow**, and `Demo till log (entries + history)` replays a dirty
batch through the real routing — no credentials, nothing to repoint.

The row shape each intake item carries (the same fields the `today` and
`history` Sheet tabs must provide in production) plus the expected verdict
per sample is documented in
[`examples/daily-cash-tally/`](../../examples/daily-cash-tally/).

## Customize

Edit the `RULES` block in Reconcile — `tolerance_abs`, `tolerance_pct`,
`escalate_after`, `history_days`, `currency`. Swap Gmail/Telegram for SMS
(Twilio) or Slack; point quarantine at a ticketing tool.

## Verification

Verified in a clean n8n container (`n8n:latest`): imports clean, all edge
cases exercised, zero credentials attached, identifiers are placeholders.

## Reliability & error handling

Every mechanism below is in `workflow.json`; where something is absent,
it is stated as absent.

- **Live/demo isolation is `disabled: true`, not a feature flag.** There
  are no `$json.live` gates in this workflow — all nine credentialed nodes
  ship disabled, and that *is* the isolation mechanism. Disabled nodes pass
  items through, so the manual demo lane never touches a live service.
  Going live is a deliberate act: enable the greyed-out nodes, attach
  credentials, remove the demo intake node.
- **Deterministic verdicts.** Every route decision — tolerance band,
  dedupe, gap detection, escalation scoring — is computed in
  `Reconcile, score history, escalate repeats`. The two OpenAI nodes
  (`Optional AI: phrase owner alert`, `Optional AI: narrate daily digest`)
  only rephrase output; they never decide anything.
- **30-day history scoring.** The Reconcile node counts each staff
  member's prior over-band shifts within `history_days: 30`. A first
  offense routes to `Email owner alert` (Gmail); once priors reach
  `escalate_after: 2`, `Route outcome` sends it to `Escalation ping`
  (Telegram) — a pattern reaches the urgent channel, a blip does not.
- **Quarantine lane.** Malformed rows (e.g. missing `counted_cash`) and
  duplicate date+shift submissions route to `Park row in quarantine` —
  parked for reprocessing, never dropped. On duplicates the first
  submission is kept; since production intake re-reads the log each sweep,
  a fixed row reprocesses automatically.
- **Gap detection.** Days with no submission at all are inferred from the
  sequence between the last history row and today, and surface as a
  `missing-data` alert via `Email owner alert`.
- **Exactly one digest per run.** The digest item is emitted by the
  Reconcile node *after* every verdict and routed to
  `Send daily digest` — an empty branch can never starve it. It carries
  the cumulative 30-day leak total and the repeat-offender watch list.
- **No retries, no error workflow — stated plainly.** None of the nine
  credentialed nodes sets `retryOnFail`, and this workflow has no error
  trigger node. A failed Sheets/Gmail/Telegram/OpenAI call surfaces as a
  failed execution in n8n's execution list; it is not retried or paged. To
  change that, set a retry policy on the live nodes or select an Error
  Workflow in the workflow's settings.

## Results & impact

**Evidence (verifiable from this repo):** the demo batch exercises all five
branches in a single zero-credential run —

| Demo case | Route | Destination node |
|---|---|---|
| Clean shift — variance inside the tolerance band | `clean` | `Append verdict to till log` |
| Escalated repeat offender — 3rd over-band shift by the same staff member in 30 days | `escalation` | `Escalation ping` |
| Duplicate submission — same date + shift | `quarantine` | `Park row in quarantine` |
| Malformed row — missing `counted_cash` | `quarantine` | `Park row in quarantine` |
| Three-day submission gap — no entries at all | `alert` | `Email owner alert` |
| Run summary | `digest` | `Send daily digest` — exactly one per run |

Verified in a clean n8n container (`n8n:latest`): imports clean, all edge
cases exercised, zero credentials attached.

**Business outcome:**
<!-- owner-metric: hours per week saved on manual till reconciliation -->
<!-- owner-metric: cash-leak amount or repeat-offender pattern caught in production -->

## Sanitization notes

This export was sanitized for public sharing: no `credentials` blocks, no
`$env` references, and the instance identifiers (`meta.instanceId`,
workflow `id`/`versionId`, per-node `webhookId`s, timestamps) have been
removed. The remaining contact fields are placeholders — `owner@example.com`
on `Email owner alert` and a placeholder `chatId` on both Telegram nodes.

---

*Need something like this for your business?
[Contact me](../../README.md#hire-me)*
