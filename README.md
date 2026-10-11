# Automation Workflows — n8n, Zapier, Python & AI Agents

Automation systems — human-in-the-loop approvals where money or reputation is at
stake, deterministic core logic, and failure handling designed in rather than
bolted on. The repo runs on n8n with custom code where a native node is not
enough — Make, Zapier or another stack when a client's setup genuinely calls for
it, including the jobs that really are one simple "connect App A to App B" zap.

Every pack ships a **zero-credential demo lane** — import and run, or
`python3 <lane> --demo` — so you can see exactly what it does before a credential
is involved anywhere.

## What's in here

Six artifacts, each solving one concrete, verifiable problem. They are grouped
below by the buyer problem they fix; every card also carries its platform so you
can filter by stack.

### Your data and money ops eat your day

| Pack | Platform | The problem it fixes | Outcome |
| :--- | :--- | :--- | :--- |
| [CSV Cleaner](n8n/csv-cleaner/) | n8n | Messy CSV imports from forms, suppliers and scrapers: blank names, bad emails, duplicate addresses — and spreadsheet formulas that silently drop the bad rows. | Every row is checked, clean rows flow forward, the rest land in a reason-coded quarantine, and you get exactly one summary per run. Nothing drops silently. |
| [Invoice Emailer](n8n/invoice-emailer/) | n8n | Invoices matched to the wrong customer, or sent twice — and failed sends nobody notices until the customer does. | Every invoice is matched and deduped, send-ready payloads are composed, and every failure lands in a reason-coded owner alert with exactly one digest per run. |
| [Invoice Ledger](python/invoice-ledger/) | Python CLI | Invoices and receipts arrive by email and get keyed into a sheet by hand — slow, error-prone, and overdue invoices only get chased when someone remembers. | Every file in the watched folder is parsed, validated and appended once to a bookkeeping-ready CSV ledger; low-confidence items go to a review file with a reason; overdue invoices get a chase draft that is never sent on its own. |

### Leads and messages slip through the cracks

| Pack | Platform | The problem it fixes | Outcome |
| :--- | :--- | :--- | :--- |
| [Lead Router](zapier/lead-router/) | Zapier | Website form and inbox leads leak between the form, the inbox and the CRM — written twice, or lost entirely. | Every lead is normalized, deduped and scored by a declared rule table; hot leads get a CRM upsert and a review-gated draft, the rest are logged with the reason, and the run ends with exactly one digest. |
| [Back-Office Triage](ai-agents/backoffice-triage/) | AI agent setup | Inbound email, form and chat messages pile up overnight, and the morning is spent routing them instead of working them. | Every message is routed to one queue with a drafted next action, and **nothing is ever sent until a human approves it** — with one audit row per message so the whole day is reconstructable. |

### You don't know what to automate first

| Pack | Platform | The problem it fixes | Outcome |
| :--- | :--- | :--- | :--- |
| [Automation Audit](skills/automation-audit/) | Skills | "We should automate something" — but which process, in what scope, and at roughly what cost? A paid discovery call you haven't booked yet. | Paste a described business process and get back a scoped spec, an ordered automation list (quickest win first) and a rough effort estimate — deterministic, no model, no key, no network. |

## The design rules behind every pack

- **Human-in-the-loop where it counts.** Sends, approvals and anything with
  money or reputation attached are gated; the machine drafts, the human decides.
- **Deterministic core logic.** Same input, same verdict, every run — verifiable
  in CI, not a black box.
- **The failure path is a first-class output.** Quarantines, review files,
  reason-coded alerts and owner digests exist as explicit branches, not silent
  drops.
- **Zero credentials to try.** Every pack has a demo lane that runs end-to-end
  with nothing to configure.

## Run them yourself

Each pack README carries its own demo lane; the n8n and python packs also ship a
per-pack input contract under [`examples/`](examples/), while `zapier/`,
`ai-agents/` and `skills/` carry their fixtures inside the pack:

```bash
# n8n packs: import workflow.json, click "Test workflow"
# zapier/lead-router
cd zapier/lead-router && python3 replay.py
# python/invoice-ledger
cd python/invoice-ledger && python3 invoice_ledger_cli.py --demo
# ai-agents/backoffice-triage (offline, mock LLM)
cd ai-agents/backoffice-triage && python3 bo_triage_cli.py --mock-llm
# skills/automation-audit
cd skills/automation-audit && python3 audit_lane.py --self-check
```

All four deterministic lanes print `RESULT: PASS` against their bundled fixtures.

---

## Hire me

I'm **Vinh Le** — I design and build automation systems for small businesses and
solo founders who are drowning in manual work. Fixed-price, milestone-based
projects: a defined brief, an agreed deadline, and a handover pack when the
milestone is approved.

- Email: [lethevinh.qng@gmail.com](mailto:lethevinh.qng@gmail.com)
- LinkedIn: [linkedin.com/in/lethevinh](https://www.linkedin.com/in/lethevinh)
- Support & feedback: [GitHub Issues](https://github.com/lethevinh/automation-workflows/issues)

Tell me the process that eats your week and I'll come back with a scoped,
fixed-price quote — see the [case study](docs/case-studies/fixed-price-automation-service.md)
for what that looks like.

<!-- owner-metric: years of experience · projects shipped · hours saved per client -->