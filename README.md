# Automation Workflows — n8n, Zapier, Python & AI Agents

> A living portfolio of production-ready automations: n8n workflows, Zapier
> integrations, Python utilities, and AI agents — each one documented,
> tested, and built the way I build for clients.
>
> **Open for automation projects → [Get in touch](#hire-me)**

---

## Why this repo exists

Every business has repetitive work that silently eats hours: copying leads
between tools, triaging inboxes, syncing spreadsheets, chasing invoices.
This repo is where I publish the automations I design and run — real
workflows, documented end to end, so you can see exactly how I work before
you hire me.

**Nothing here is a toy demo.** Each workflow ships with:

- A problem statement and measurable outcome
- An architecture diagram and full setup guide
- Sample data so you can run it yourself
- The same structure I deliver on paid projects

## Featured workflows

| Workflow | Platform | Use case | Highlights |
|---|---|---|---|
| [Client Report Generator](n8n/client-report-generator/) | n8n | Weekly per-client marketing reports | Meta Ads + Google Ads + GA4, config-sheet driven, branded HTML, draft-review mode |
| [Promise Ledger](n8n/promise-ledger/) | n8n | Track promises made to you in email | AI extraction, chase drafts with approval gate, fulfillment detection |
| [FAQ Chatbot](n8n/faq-chatbot/) | n8n | Support chatbot that grows its own FAQ | Learns from misses — only with owner approval; lead capture |
| [Daily Cash Tally](n8n/daily-cash-tally/) | n8n | End-of-day till reconciliation | 30-day history scoring, repeat-offender escalation, quarantine lane |
| [Affiliate Intake](n8n/affiliate-intake/) | n8n | Screen affiliate applications | Editable rules, outreach drafts, zero-credential demo |

Every n8n workflow runs its demo lane with **zero credentials** — import,
click Test, watch it route every branch.

*New workflows are added regularly — watch the repo to follow along.*

## Services I offer

| Service | What you get |
|---|---|
| **n8n workflow setup** | Design, build, and deploy your workflow — cloud or self-hosted |
| **n8n self-hosting** | Docker/VPS deployment, queue mode, backups, monitoring |
| **Workflow audit & rescue** | Fix brittle/broken workflows, add error handling and retries |
| **Custom integrations** | Connect APIs that have no native nodes (Python/JS custom nodes) |
| **AI agent pipelines** | LLM-powered classification, drafting, enrichment inside your stack |
| **Ongoing maintenance** | Monitoring, alerting, versioned updates |

## How I work

1. **Discovery** — map your process, find the automation boundary
2. **Spec** — you approve a written spec before I build anything
3. **Build** — workflow + error handling + docs, in a shared workspace
4. **Verify** — tested against sample data, then a real pilot run
5. **Handoff** — you own everything: workflows, docs, credentials

No black boxes. No lock-in. You can maintain it yourself, or keep me on
retainer — your choice.

## Repository structure

| Folder | Contents |
|---|---|
| [`n8n/`](n8n/) | Production n8n workflows — `workflow.json` + archify diagrams + docs |
| [`zapier/`](zapier/) | Zapier automations — step-by-step docs + configs |
| [`python/`](python/) | Standalone scripts & pipelines — tested, packaged |
| [`ai-agents/`](ai-agents/) | Agent setups — prompts, configs, orchestration |
| [`skills/`](skills/) | Reusable agent skills (SKILL.md format) |
| [`docs/case-studies/`](docs/case-studies/) | Deep-dives: problem → build → measured results |
| [`examples/`](examples/) | Sample data & fixtures so you can run workflows yourself |
| [`scripts/`](scripts/) | Repo tooling — mermaid node-graph generator, archify SVG extractor |

Every workflow follows the [standard template](docs/workflow-template.md):
problem, diagram, setup, results — and ships an
[archify](https://github.com/tt-a1i/archify)-rendered architecture diagram
(`assets/diagram.svg`, source `assets/diagram.json`).

## Tech stack

`n8n` · `Zapier` · `Make` · `Python` · `TypeScript` · `OpenAI / Anthropic`
`PostgreSQL` · `Docker` · `Google Workspace` · `Airtable` · `Slack` · `Notion`

## Hire me

I'm **Le The Vinh** — I design and build automation systems for small
businesses and solo founders who are drowning in manual work.

- Upwork: [your-upwork-profile]
- LinkedIn: [your-linkedin]
- Email: [your-email]
- Website: [your-site]

The fastest way to start: email me 2–3 sentences about the process that's
eating your time. I'll reply with what I'd automate and roughly how.

## License

Code under [MIT](LICENSE). Workflow definitions and documentation may be
used as reference; please don't resell the packaged templates as-is.
