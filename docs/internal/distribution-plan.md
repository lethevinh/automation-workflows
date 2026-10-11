# Distribution plan — get the portfolio in front of buyers

Draft copy for every channel. **Post nothing without owner review** — this
is copy to approve and send, not to auto-publish. No fake engagement
claims, no "as seen in" statements.

Base URL for all links: `https://github.com/lethevinh/automation-workflows`
Append `?utm_source=<channel>&utm_medium=<type>&utm_campaign=portfolio-launch`
so the owner can see what converts.

## Pre-post redaction checklist (run before EVERY post)

- [ ] No n8n instance identifier (64-hex) in text, screenshots, or video
- [ ] No client names, real emails, spreadsheet IDs, account IDs
- [ ] No instance URL visible in captures
- [ ] Claims match the repo: "verified in a clean container", repo-verifiable
      metrics, `<!-- owner-metric -->` numbers only if owner supplied them
- [ ] The repo commit being linked is actually pushed

---

## Channels

### 1. n8n community template gallery — creators.n8n.io

Submit each workflow individually (they review per-workflow).

**Draft submission (per workflow):**

> **<Workflow name>** — <one-line outcome>. Zero-credential demo lane:
> import, press Test workflow, watch every branch run on built-in sample
> data. Includes an architecture diagram, a documented reliability section
> (retries, live/demo isolation, approval gates), and a fixtures folder
> with the input contract. Sanitized production export — credentials and
> instance identifiers stripped.

**Owner action:** submit at https://creators.n8n.io (account needed);
attach `assets/diagram.svg` as the cover image. Note: gallery submissions
require the workflow description to be self-contained — copy the workflow
README's Problem + Solution sections.

### 2. awesome-n8n / awesome-automation lists — GitHub PR

**Draft PR body:**

> Adds `lethevinh/automation-workflows` — a small portfolio of documented
> n8n workflows (not raw dumps): each ships a sanitized `workflow.json`, an
> architecture diagram, a generated node graph, a `.env.example` checklist,
> and run-it-yourself fixtures with the input contract documented. CI
> guards keep the exports sanitized and the diagrams in sync.

**Owner action:** open the PR from their account; link target
`https://github.com/lethevinh/automation-workflows?utm_source=github&utm_medium=pr&utm_campaign=portfolio-launch`.

### 3. Reddit r/n8n — showcase post

**Draft:**

> **Title:** I open-sourced my n8n portfolio — 5 workflows with diagrams,
> test fixtures, and honest reliability docs
>
> Every workflow runs a demo lane with zero credentials (import → press
> Test → watch it route). Each README documents what's actually in the
> JSON: retry coverage, live/demo isolation, approval gates — including
> what's *not* there. Feedback welcome.
>
> Repo: <UTM link>

**Owner action:** post from their Reddit account; pick the showcase/self-promo flair; answer comments within the first day.

### 4. LinkedIn — portfolio post

**Draft:**

> I published the workflows I use to win automation contracts.
>
> Five n8n systems — client report generation, a promise-tracking ledger,
> a self-improving FAQ bot, a till-reconciliation monitor, and an affiliate
> intake screener — each with an architecture diagram, a zero-credential
> demo you can run in one click, and documented reliability (retries,
> approval gates, quarantine lanes).
>
> I build automation that fails loudly, never silently. Repo: <UTM link>

**Owner action:** post with the flagship `client-report-generator`
`diagram.svg` as the image; follow with a comment linking the case study
once P4 lands.

### 5. Upwork portfolio entry

**Draft:**

> **Automation systems portfolio** — five production n8n workflows with
> full documentation: architecture diagrams, test fixtures, sanitization
> notes, and reliability sections covering retry policy, human-in-the-loop
> approvals and idempotency. Includes an 87-node multi-source reporting
> pipeline (Meta Ads + Google Ads + GA4 → branded HTML → Gmail/Slack) with
> an idempotent ledger and a human review seam.

**Owner action:** add to Upwork profile portfolio; attach diagram.svg +
one execution screenshot (once P6 assets exist).

### 6. Short blog post — dev.to / personal site

**Draft outline** (800–1,000 words):

1. The problem with workflow portfolios: screenshots of canvases prove
   nothing.
2. What buyers actually check: can it fail silently? can I run it? does
   the README match the JSON?
3. The pattern: zero-credential demo lanes + documented reliability +
   repo-verifiable evidence.
4. Walk one workflow end to end (client-report-generator).
5. CTA: repo link + "open for automation projects".

**Owner action:** publish on their dev.to/site with canonical link back
to the repo.

---

## Two-week schedule (one action per day)

| Day | Action |
|---|---|
| 1 | Push the finished repo; confirm all links resolve on GitHub |
| 2 | P3b: update repo description/topics (needs owner approval) |
| 3 | P6: capture execution screenshots for client-report-generator |
| 4 | P6: screenshots for promise-ledger + faq-chatbot |
| 5 | P4: publish the flagship case study |
| 6 | Submit client-report-generator to the n8n template gallery |
| 7 | Submit promise-ledger + faq-chatbot to the gallery |
| 8 | Submit daily-cash-tally + affiliate-intake to the gallery |
| 9 | Post the LinkedIn announcement |
| 10 | Add the Upwork portfolio entry |
| 11 | Open the awesome-n8n PR |
| 12 | Post to r/n8n |
| 13 | Publish the blog post |
| 14 | Review UTM traffic in GitHub Insights → decide where to double down |

Buffer days are intentional — gallery review queues and PR merges are not
same-day.

---

*Everything above is draft copy for owner review. Nothing is posted by an
agent.*
