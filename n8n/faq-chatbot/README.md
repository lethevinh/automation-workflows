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

## Stack & credentials

40 nodes — Chat Trigger, OpenAI ×2, Google Sheets ×8, Gmail ×2, Schedule &
Manual Triggers, Switch, Code.

Production needs Google Sheets + Gmail + OpenAI credentials. The demo lane
needs none. See [SETUP.md](SETUP.md) for the step-by-step guide (~5 min).

## Why it's different

| Typical FAQ template | This workflow |
|---|---|
| Answers from KB, drops misses | Misses are logged, clustered, drafted into new FAQ entries |
| Auto-saves AI answers | Owner-approved write-back — no unprompted self-learning |
| Lead capture as an afterthought | Lead detection is a first-class route |

## Verification

Container pilot on `n8n:latest` (zero credentials): digest exactly 1 item,
6 happy-path items, empty-message / duplicate / bad-AI branches all
verified — PASS.

---

*Need something like this for your business?
[Contact me](../../README.md#hire-me)*
