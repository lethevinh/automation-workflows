# n8n Workflows

Production-ready n8n workflows. Each folder is self-contained:

```
<workflow-slug>/
├── workflow.json        # Export straight from n8n — importable as-is
├── .env.example         # Credential/service checklist + placeholders (no secrets, ever)
├── README.md            # Problem → Solution → Setup → Verification → Reliability → Results
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
| [client-report-generator](client-report-generator/) | Weekly per-client reports from a config sheet — Meta Ads, Google Ads, GA4 → branded HTML via Gmail/Slack | Sheets, Gmail, OpenAI, Slack + Meta Ads / Google Ads / GA4 API tokens (demo: none) | Production-ready |
| [promise-ledger](promise-ledger/) | Track promises made to you in email, chase before they go cold (approval gate) | Gmail, Sheets, OpenAI (demo: none) | Production-ready |
| [faq-chatbot](faq-chatbot/) | FAQ chatbot that learns from misses — with owner approval before it writes back | Sheets, Gmail, OpenAI (demo: none; Chat Trigger needs no key) | Production-ready |
| [daily-cash-tally](daily-cash-tally/) | Till cash-leak monitor — 30-day scoring, repeat-offender escalation, quarantine | Sheets, Gmail, Telegram + optional OpenAI (demo: none) | Production-ready |
| [affiliate-intake](affiliate-intake/) | Screen affiliate applications, draft outreach for qualified applicants | None | Demo |

All five import clean on `n8n:latest` and run their demo lanes with **zero
credentials** — click Test workflow after import.

## How to import a workflow

1. In n8n, go to **Workflows → Import from File** and pick `workflow.json`.
2. Want to see it run first? Press **Test workflow** — every workflow
   ships a demo lane that needs no credentials.
3. To go live, open the folder's `.env.example`. It is a checklist, not an
   env file the workflow reads (no export contains `$env` references):
   create each listed credential in n8n (**Credentials → New**), attach it
   on the named nodes, and replace the listed node-level placeholders
   (sheet IDs, owner email, chat IDs). The file also explains that
   workflow's live/demo switch — `$json.live` gates or `disabled` nodes.
   affiliate-intake skips this step entirely: it has no credentialed nodes.
4. Activate.

All workflows are tested on a self-hosted n8n instance (Docker) and n8n
Cloud. Node-version notes live in each workflow's README.
