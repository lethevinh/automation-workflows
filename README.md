# Automation Workflows — n8n, Zapier, Python & AI Agents

> Automation systems, not "connect App A to App B" zaps — human-in-the-loop
> approvals where money or reputation is at stake, deterministic core logic,
> and failure handling designed in rather than bolted on.
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

- A problem statement and the outcome it targets
- An architecture diagram and a documented setup path
- A zero-credential demo lane — import, click **Test workflow**, watch it
  route every branch
- The same structure I deliver on paid projects

## Featured workflows

| Workflow | Platform | Use case | Highlights | Result (repo-verified) |
|---|---|---|---|---|
| [Client Report Generator](n8n/client-report-generator/) | n8n | Weekly per-client marketing reports | Meta Ads + Google Ads + GA4, config-sheet driven, branded HTML, draft-review mode | Pilot run: 16 report items, exactly 1 digest, alerts 3/3 — PASS · `retryOnFail` on 15/15 credentialed nodes |
| [Promise Ledger](n8n/promise-ledger/) | n8n | Track promises made to you in email | AI extraction, chase drafts with approval gate, fulfillment detection | Pilot run: 5-item happy path, alerts 3/3 — PASS · `retryOnFail` on 19/19 credentialed nodes |
| [FAQ Chatbot](n8n/faq-chatbot/) | n8n | Support chatbot that grows its own FAQ | Learns from misses — only with owner approval; lead capture | Pilot run: 6 visitor turns routed, digest exactly 1, 3/3 edge branches — PASS |
| [Daily Cash Tally](n8n/daily-cash-tally/) | n8n | End-of-day till reconciliation | 30-day history scoring, repeat-offender escalation, quarantine lane | Demo run exercises all 5 branch routes — quarantine, escalation and gap alert included |
| [Affiliate Intake](n8n/affiliate-intake/) | n8n | Screen affiliate applications | Editable rules, outreach drafts, zero-credential demo | Demo run: 6 applications → 2 qualified drafts + 4 reason-coded alerts, exactly 1 digest |

Every n8n workflow runs its demo lane with **zero credentials** — import,
click Test, watch it route every branch. All five exports are **sanitized
for public sharing**: credential blocks, instance identifiers and pinned
data stripped, with a CI check keeping them that way.

<!-- owner-metric: business results per workflow (hours saved, spend
     replaced, volume handled) — to be supplied by the owner for the
     Result column -->

**Platforms & APIs on display:** `n8n` (cloud & self-hosted) ·
`Google Sheets` · `Gmail` · `Telegram` · `OpenAI` · `Meta Ads` /
`Google Ads` / `GA4` / `Slack` over HTTP (Header & Custom Auth)

**Differentiators on display:** human-in-the-loop approval gates ·
idempotent writes (dedupe keys, `appendOrUpdate`) · quarantine lanes ·
per-source failure isolation · retry/backoff policies (`retryOnFail`,
`maxTries: 3`) · one-click zero-credential demo lanes

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
| [`n8n/`](n8n/) | Five n8n workflows — `workflow.json` + archify diagrams + setup docs |
| [`examples/`](examples/) | Per-workflow input contracts — `test-data.json` fixtures + expected verdicts for all five workflows |
| [`zapier/`](zapier/) | Zapier automations — step-by-step docs + configs — *coming soon* |
| [`python/`](python/) | Standalone scripts & pipelines — *coming soon* |
| [`ai-agents/`](ai-agents/) | Agent setups — prompts, configs, orchestration — *coming soon* |
| [`skills/`](skills/) | Reusable agent skills (SKILL.md format) — *coming soon* |
| [`docs/`](docs/) | Repo docs — workflow README template, visual style guide, upgrade plan |
| [`docs/case-studies/`](docs/case-studies/) | Deep-dives: problem → build → measured results — *first one in progress* |
| [`scripts/`](scripts/) | Repo tooling — mermaid node-graph generator, archify extractor, export sanitizer, local CI runner |
| [`.github/`](.github/) | CI — JSON validity, secret scan, sanitization residue, mermaid drift, placeholder & demo-lane checks |
| [`.archify/`](.archify/) | archify project sources behind the committed `diagram.svg` files |

Every workflow ships an
[archify](https://github.com/tt-a1i/archify)-rendered architecture diagram
(`assets/diagram.svg`, source `assets/diagram.json`) and a README in the
[standard template](docs/workflow-template.md) order: problem → solution →
stack & credentials → setup → verification → reliability & error handling →
results & impact → sanitization notes.

## Tech stack

`n8n` · `Zapier` · `Make` · `Python` · `TypeScript` · `OpenAI / Anthropic`
`PostgreSQL` · `Docker` · `Google Workspace` · `Airtable` · `Slack` · `Notion`

## Hire me

I'm **Le The Vinh** — I design and build automation systems for small
businesses and solo founders who are drowning in manual work.

<!-- owner-input: replace the four placeholder links below with the real
     Upwork / LinkedIn / email / website URLs — the only remaining blocker
     before publishing (CI allowlists exactly these four tokens). -->

- Upwork: [your-upwork-profile]
- LinkedIn: [your-linkedin]
- Email: [your-email]
- Website: [your-site]

*Direct links are being wired up — in the meantime you can reach me via
[GitHub](https://github.com/lethevinh).*

The fastest way to start: send me 2–3 sentences about the process that's
eating your time. I'll reply with what I'd automate and roughly how.

## License

Code under [MIT](LICENSE). Workflow definitions and documentation may be
used as reference; please don't resell the packaged templates as-is.
