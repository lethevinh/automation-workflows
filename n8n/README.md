# n8n Workflows

Production-ready n8n workflows. Each folder is self-contained:

```
<workflow-slug>/
├── workflow.json        # Export straight from n8n — importable as-is
├── .env.example         # Credentials/config placeholders (no secrets, ever)
├── README.md            # Problem → Diagram → Node graph → Setup → Results
├── SETUP.md             # Step-by-step guide (when the workflow needs one)
└── assets/
    ├── diagram.svg      # Architecture diagram (archify — see below)
    └── diagram.json     # Diagram source — regenerate the SVG from this
```

Each README also embeds a **Mermaid node graph** generated straight from
`workflow.json` by `scripts/render-mermaid.py` (markers
`<!-- mermaid:start/end -->`) — re-run the script after editing a workflow
to keep it in sync.

Every diagram is a typed [archify](https://github.com/tt-a1i/archify)
workflow candidate (`diagram.json`) rendered to a validated, gate-checked
SVG — lanes map to the workflow's logical stages, red lanes are human
approval/exception paths.

## Index

| Workflow | Use case | Credentials needed | Status |
|---|---|---|---|
| [client-report-generator](client-report-generator/) | Weekly per-client reports from a config sheet — Meta Ads, Google Ads, GA4 → branded HTML via Gmail/Slack | Sheets, Gmail, OpenAI + provider tokens | Production-ready |
| [promise-ledger](promise-ledger/) | Track promises made to you in email, chase before they go cold (approval gate) | Gmail, Sheets, OpenAI | Production-ready |
| [faq-chatbot](faq-chatbot/) | FAQ chatbot that learns from misses — with owner approval before it writes back | Sheets, Gmail, OpenAI | Production-ready |
| [daily-cash-tally](daily-cash-tally/) | Till cash-leak monitor — 30-day scoring, repeat-offender escalation, quarantine | Sheets, Gmail, Telegram (demo: none) | Production-ready |
| [affiliate-intake](affiliate-intake/) | Screen affiliate applications, draft outreach for qualified applicants | None | Demo |

All five import clean on `n8n:latest` and run their demo lanes with **zero
credentials** — click Test workflow after import.

## How to import a workflow

1. In n8n, go to **Workflows → Import from File** and pick `workflow.json`.
2. Copy `.env.example` to `.env` (or set the vars in your n8n environment)
   and fill in your credentials.
3. Open each credential node and select your saved credential.
4. Activate.

All workflows are tested on a self-hosted n8n instance (Docker) and n8n
Cloud. Node-version notes live in each workflow's README.
