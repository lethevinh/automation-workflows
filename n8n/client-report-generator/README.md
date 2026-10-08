# Client Report Generator — Weekly Per-Client Reports from One Config Sheet

**Platform:** n8n · **Category:** Marketing / Agency Reporting
**Outcome:** Meta Ads + Google Ads + GA4 → week-over-week deltas →
AI-written branded report, delivered per client through Gmail and/or
Slack — driven entirely by spreadsheet cells, not workflow edits.

![Workflow diagram](assets/diagram.svg)

*Architecture diagram — source [`assets/diagram.json`](assets/diagram.json), rendered with [archify](https://github.com/tt-a1i/archify)*

**Node graph** — generated from `workflow.json` (see `scripts/render-mermaid.py`):

<!-- mermaid:start -->
```mermaid
%%{init: {"theme":"base","themeVariables":{"fontFamily":"ui-monospace, SFMono-Regular, Menlo, monospace","fontSize":"13px","background":"#FFFFFF","primaryColor":"#FFFFFF","primaryBorderColor":"#CBD5E1","primaryTextColor":"#0F172A","lineColor":"#94A3B8","tertiaryColor":"#FFFFFF"}}}%%
flowchart TB
    n0(["When clicking 'Test workflow'"])
    n1["Demo config (fixture)"]
    n2(["On workflow error"])
    n3["Operator email"]
    n4["Format error alert"]
    n5["Email owner: workflow error"]
    n6(["Weekly tick — Monday 09:00"])
    n7["Workflow Config"]
    n8[("Read config tab")]
    n9[("Read reports ledger")]
    n10["Collect sent keys"]
    n11["Validate clients"]
    n12["Expand enabled sources"]
    n13{"Has source?"}
    n14{"Source route"}
    n15{"Meta Ads live?"}
    n16["Fetch Meta Ads insights"]
    n17["Normalize Meta Ads"]
    n18["Demo Meta Ads fetch"]
    n19{"Google Ads live?"}
    n20["Fetch Google Ads metrics"]
    n21["Normalize Google Ads"]
    n22["Demo Google Ads fetch"]
    n23{"GA4 live?"}
    n24["Fetch GA4 report"]
    n25["Normalize GA4"]
    n26["Demo GA4 fetch"]
    n27["Extension dock"]
    n28["Compose source alert"]
    n29["Merge sources"]
    n30["Compute WoW deltas"]
    n31["Group report table"]
    n32{"Ready to report?"}
    n33["Dedupe check"]
    n34{"Already sent?"}
    n35["Compose duplicate alert"]
    n36["Build report prompt"]
    n37{"Prose live?"}
    n38["Write report narrative (AI)"]
    n39["Parse narrative"]
    n40["Demo narrative"]
    n41["Render report"]
    n42["Fan out sinks"]
    n43{"Sink route"}
    n44{"Gmail live?"}
    n45{"Delivery mode: draft?"}
    n46{"Demo delivery: draft?"}
    n47["Send report email"]
    n48["Create report draft"]
    n49["Mark email sent"]
    n50["Mark draft created"]
    n51["Demo email sink"]
    n52["Demo draft sink"]
    n53{"Slack live?"}
    n54["Post report to Slack"]
    n55{"Slack delivered?"}
    n56["Mark slack sent"]
    n57["Demo Slack sink"]
    n58["Sink extension dock"]
    n59["Compose sink alert"]
    n60["Merge sends"]
    n61["Collapse sends"]
    n62{"Record report?"}
    n63[("Record report")]
    n64["Demo: record or skip"]
    n65["Merge run"]
    n66["Run digest"]
    n67{"Digest is live?"}
    n68["Format digest email"]
    n69["Email operator: run digest"]
    n70(["SETUP — press play on this node once"])
    n71[("Create report workbook")]
    n72["Seed tabs"]
    n73{"Route by tab"}
    n74["Shape config row"]
    n75["Shape reports row"]
    n76[("Write config tab")]
    n77[("Write reports tab")]
    n78["Merge setup writes"]
    n79["Print sheet id + next step"]
    n0 --> n1
    n1 --> n11
    n2 --> n3
    n3 --> n4
    n3 --> n68
    n4 --> n5
    n6 --> n7
    n7 --> n8
    n7 --> n9
    n9 --> n10
    n8 --> n11
    n11 --> n12
    n12 --> n13
    n13 -->|"true"| n14
    n13 -->|"false"| n65
    n14 -->|"0"| n15
    n14 -->|"1"| n19
    n14 -->|"2"| n23
    n14 -->|"3"| n27
    n15 -->|"true"| n16
    n15 -->|"false"| n18
    n16 -->|"out 0"| n17
    n16 -->|"out 1"| n28
    n17 --> n29
    n18 --> n29
    n19 -->|"true"| n20
    n19 -->|"false"| n22
    n20 -->|"out 0"| n21
    n20 -->|"out 1"| n28
    n21 --> n29
    n22 --> n29
    n23 -->|"true"| n24
    n23 -->|"false"| n26
    n24 -->|"out 0"| n25
    n24 -->|"out 1"| n28
    n25 --> n29
    n26 --> n29
    n27 --> n29
    n28 --> n65
    n29 --> n30
    n30 --> n31
    n31 --> n32
    n32 -->|"true"| n33
    n32 -->|"false"| n65
    n33 --> n34
    n34 -->|"true"| n35
    n34 -->|"false"| n36
    n35 --> n65
    n36 --> n37
    n37 -->|"true"| n38
    n37 -->|"false"| n40
    n38 --> n39
    n39 --> n41
    n40 --> n41
    n41 --> n42
    n42 --> n43
    n43 -->|"0"| n44
    n43 -->|"1"| n53
    n43 -->|"2"| n58
    n44 -->|"true"| n45
    n44 -->|"false"| n46
    n45 -->|"true"| n48
    n45 -->|"false"| n47
    n46 -->|"true"| n52
    n46 -->|"false"| n51
    n47 -->|"out 0"| n49
    n47 -->|"out 1"| n59
    n48 -->|"out 0"| n50
    n48 -->|"out 1"| n59
    n50 --> n60
    n49 --> n60
    n52 --> n60
    n51 --> n60
    n53 -->|"true"| n54
    n53 -->|"false"| n57
    n54 -->|"out 0"| n55
    n54 -->|"out 1"| n59
    n55 -->|"true"| n56
    n55 -->|"false"| n59
    n56 --> n60
    n57 --> n60
    n58 --> n60
    n59 --> n65
    n60 --> n61
    n61 --> n62
    n62 -->|"true"| n63
    n62 -->|"false"| n64
    n63 -->|"out 0"| n65
    n63 -->|"out 1"| n59
    n64 --> n65
    n65 --> n66
    n66 --> n67
    n67 --> n3
    n68 --> n69
    n70 --> n71
    n71 --> n72
    n72 --> n73
    n73 -->|"0"| n74
    n73 -->|"1"| n75
    n74 --> n76
    n76 --> n78
    n75 --> n77
    n77 --> n78
    n78 --> n79
    classDef trigger fill:#EFF6FF,stroke:#3B82F6,color:#0F172A
    classDef logic fill:#ECFDF5,stroke:#10B981,color:#0F172A
    classDef decide fill:#FFFBEB,stroke:#F59E0B,color:#0F172A
    classDef store fill:#F5F3FF,stroke:#8B5CF6,color:#0F172A
    classDef ai fill:#FDF2F8,stroke:#EC4899,color:#0F172A
    classDef external fill:#F8FAFC,stroke:#64748B,color:#0F172A
    classDef gate fill:#FEF2F2,stroke:#EF4444,color:#0F172A
    classDef disabled opacity:.55,stroke-dasharray:4 3
    class n0,n2,n6,n70 trigger
    class n1,n3,n4,n7,n10,n11,n12,n17,n18,n21,n22,n25,n26,n27,n28,n29,n30,n31,n33,n35,n36,n39,n40,n41,n42,n49,n50,n51,n52,n56,n57,n58,n59,n60,n61,n64,n65,n66,n68,n72,n74,n75,n78,n79 logic
    class n13,n14,n15,n19,n23,n32,n34,n37,n43,n44,n45,n46,n53,n55,n62,n67,n73 decide
    class n8,n9,n63,n71,n76,n77 store
    class n38 ai
    class n5,n16,n20,n24,n47,n48,n54,n69 external
```
<!-- mermaid:end -->

## The problem

Agencies and freelancers write the same per-client marketing report every
week: pull metrics from three ad platforms, compute deltas, write the
summary, format it, send it. Existing tools charge $20–700/month per seat;
typical templates hardcode one client per workflow.

## The solution

Every Monday it reads a `config` Google Sheet — **one row per client, one
yes/no cell per source and per delivery channel** — then:

- Fetches **Meta Ads, Google Ads and GA4** behind one adapter contract
  (a named extension dock takes new sources without touching the engine)
- Computes WoW deltas **deterministically in a Code node** — the AI only
  writes prose around finished numbers, never invents them
- Renders a **per-client branded HTML report** (`brand_name`/`brand_color`/
  `brand_logo_url` cells)
- **`delivery_mode=draft`** files a Gmail draft for owner sign-off — a
  human review seam no incumbent template offers
- **`alert_threshold_pct`** flags metrics crossing each client's band in
  the report body and counts them in the run digest
- **Idempotent `reports` ledger** keyed on `client_id + ISO week` —
  re-runs in the same week are skipped as duplicates, never double-sent
- **Per-source failure isolation** — one bad fetch alerts without blocking
  other clients; instance-level Error Trigger emails the owner on
  unhandled failures
- One-click SETUP lane provisions the workbook and prints the ID

## Stack & credentials

87 nodes — Google Sheets, Gmail, Slack, OpenAI, HTTP Request (Meta/GA4/
Slack via Header Auth, Google Ads via Custom Auth for its two-header
requirement). Works on n8n Cloud — no env vars needed.

Credentials for production: Gmail, Google Sheets, OpenAI, plus provider
tokens on the HTTP nodes. **Test workflow runs a four-client demo with
zero credentials.** See [SETUP.md](SETUP.md).

## Why it's different

| Typical report template | This workflow |
|---|---|
| Hardcoded params per client | One `config` sheet row per client — cells toggle everything |
| One ad provider | Three sources behind one adapter contract + extension dock |
| LLM summarizes raw payload | Code computes deltas; AI writes prose only |
| Append-only or no ledger | Idempotent upsert — re-runs never double-send |
| One bad fetch kills the run | Per-source alerts; other clients still report |
| Send-only | `delivery_mode=draft` review seam |
| Fixed layout | Per-client branded HTML from config cells |

## Verification

- Container pilot on `n8n:latest` (zero credentials): digest exactly 1
  item, 16 happy-path items, missing-data/duplicate/failure alerts 3/3 —
  PASS
- Fixture-driven: three config variants replay the same workflow with
  different config cells — pinned deltas verified (per-client sources,
  pause/skip, draft routing, anomaly flags)
- Slack delivery gated on the API `ok` flag — the ledger never records an
  undelivered report

---

*Need something like this for your business?
[Contact me](../../README.md#hire-me)*
