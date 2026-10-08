# Examples & Sample Data

Input-contract fixtures for the five n8n workflows — no real credentials
or customer data needed.

The one-click demo lane stays the primary way to run a workflow (import
`n8n/<slug>/workflow.json`, press **Test workflow**); nothing repoints a
trigger at these files. Each folder holds a `test-data.json` plus a
`README.md` that documents the input shape the workflow consumes, which
edge case each sample exercises, and the expected verdict — the contract
to match when you wire your own data source.

| Folder | Workflow | What the fixture covers |
|---|---|---|
| [affiliate-intake/](affiliate-intake/) | Affiliate application screening | 5 sample applications — clean qualified applicant, missing email, implausible metrics (2M followers / 0 posts), duplicate application, below-threshold — with the `RULES` scoring fields, expected verdict per row, and the single run digest |
| [client-report-generator/](client-report-generator/) | Weekly per-client reports | The full `config` tab row shape (every `src_*` / `sink_*` / `brand_*` column), the 4 demo client rows (faked source outage, already-sent dedupe, missing sink, disabled client), one raw payload per source adapter (Meta Ads, Google Ads, GA4), and the `client_id` + ISO-week ledger keying |
| [daily-cash-tally/](daily-cash-tally/) | Till cash-leak monitoring | A dirty till-log batch — history rows seeding repeat-offender scoring, a clean shift, an escalated repeat offender, a duplicate `date\|shift` row, a missing `counted_cash` row, a three-day submission gap — with deterministic verdicts and the single run digest |
| [faq-chatbot/](faq-chatbot/) | FAQ chatbot with owner-approved write-back | 6 visitor chat turns — FAQ hit, miss → gap log, lead capture, empty message, duplicate, unparseable AI verdict — plus the `sim` field that lets the demo lane mirror the AI contract without an OpenAI key |
| [promise-ledger/](promise-ledger/) | Promise tracking & chasing | 6 inbound emails — clear commitment, newsletter skip, vague/missing-data promise, duplicate, unparseable AI verdict, fulfilment reply — plus the `live` flag the three `$json.live` gates check |

Each workflow's README points at the folder it documents under
**Run it yourself**.
