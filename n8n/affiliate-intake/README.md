# Affiliate Intake — Application Screening & Outreach Drafting

**Platform:** n8n · **Category:** Marketing / Partner Ops
**Outcome:** Every application screened against your own rules — qualified
applicants get a personalized outreach draft, the rest get a reason-coded
alert, and you get exactly one digest per run.

![Workflow diagram](assets/diagram.svg)

*Architecture diagram — source [`assets/diagram.json`](assets/diagram.json), rendered with [archify](https://github.com/tt-a1i/archify)*

**Node graph** — generated from `workflow.json` (see `scripts/render-mermaid.py`):

<!-- mermaid:start -->
```mermaid
%%{init: {"theme":"base","themeVariables":{"fontFamily":"ui-monospace, SFMono-Regular, Menlo, monospace","fontSize":"13px","background":"#FFFFFF","primaryColor":"#FFFFFF","primaryBorderColor":"#CBD5E1","primaryTextColor":"#0F172A","lineColor":"#94A3B8","tertiaryColor":"#FFFFFF"}}}%%
flowchart TB
    n0(["When clicking 'Test workflow'"])
    n1["Demo intake: sample applications"]
    n2["Validate + dedupe + score"]
    n3{"Qualified?"}
    n4["Draft outreach"]
    n5["Owner alert"]
    n6["Merge branches"]
    n7["Owner digest"]
    n0 --> n1
    n1 --> n2
    n2 --> n3
    n3 -->|"true"| n4
    n3 -->|"false"| n5
    n4 --> n6
    n5 --> n6
    n6 --> n7
    classDef trigger fill:#EFF6FF,stroke:#3B82F6,color:#0F172A
    classDef logic fill:#ECFDF5,stroke:#10B981,color:#0F172A
    classDef decide fill:#FFFBEB,stroke:#F59E0B,color:#0F172A
    classDef store fill:#F5F3FF,stroke:#8B5CF6,color:#0F172A
    classDef ai fill:#FDF2F8,stroke:#EC4899,color:#0F172A
    classDef external fill:#F8FAFC,stroke:#64748B,color:#0F172A
    classDef gate fill:#FEF2F2,stroke:#EF4444,color:#0F172A
    classDef disabled opacity:.55,stroke-dasharray:4 3
    class n0 trigger
    class n1,n2,n4,n5,n6,n7 logic
    class n3 decide
```
<!-- mermaid:end -->

## The problem

Affiliate and ambassador programs attract a steady trickle of applications —
some great, most not. Reading each one by hand doesn't scale, but
auto-accepting everyone dilutes the program.

## The solution

Screens applications end-to-end: dedupes by email, sanity-checks
self-reported metrics, scores fit against an **editable RULES block**
(accepted platforms, minimums, fit threshold), then routes each applicant —
qualified → personalized outreach draft; rejected → owner alert with the
reason. A Merge node guarantees the owner digest ("N qualified, M alerts")
fires exactly once.

## Stack & credentials

13 nodes — Code, IF, Merge, Manual Trigger, Sticky Notes.
**Zero credentials required** — the demo intake emits six sample
applications covering every branch (missing email, implausible metrics,
duplicate, below threshold).

## Setup

~2 minutes. Import `workflow.json`, click **Test workflow** — the demo runs
end-to-end on import.

**To go live:** swap the demo intake for a real form (n8n Form Trigger,
Tally/Typeform webhook) emitting the same item shape; add Gmail/Slack after
the outreach/alert/digest nodes.

## Verification

Verified in a clean n8n container (`n8n:latest`, Docker): imports clean,
all four edge cases exercised, zero credentials attached, demo data uses
placeholder addresses only.

---

*Need something like this for your business?
[Contact me](../../README.md#hire-me)*
