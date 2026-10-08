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
optional OpenAI.

**Zero credentials for the demo**: the Sheets/Gmail/Telegram nodes ship
disabled and pass demo data through untouched — the workflow runs
end-to-end before you connect anything.

## Setup

1. Import `workflow.json`, click **Test workflow** — demo covers every
   branch: clean shift, escalated repeat offender, duplicate, missing
   `counted_cash`, three-day submission gap.
2. To go live: a Google Sheet as the till log (tabs: `today`, `history`,
   `results`, `quarantine`), Gmail for first-offense alerts, Telegram for
   escalations/digest. Enable the greyed-out nodes and attach credentials.
3. Optional: attach an OpenAI credential and enable the two AI phrasing
   nodes.

## Customize

Edit the `RULES` block in Reconcile — `tolerance_abs`, `tolerance_pct`,
`escalate_after`, `history_days`, `currency`. Swap Gmail/Telegram for SMS
(Twilio) or Slack; point quarantine at a ticketing tool.

## Verification

Verified in a clean n8n container (`n8n:latest`): imports clean, all edge
cases exercised, zero credentials attached, identifiers are placeholders.

---

*Need something like this for your business?
[Contact me](../../README.md#hire-me)*
