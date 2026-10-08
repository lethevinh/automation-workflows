# Portfolio Upgrade Plan v2 — automation-workflows

**Status:** ready for owner sign-off — not yet executed.
**Supersedes:** v1 (draft). See [§0 What changed in v2](#0-what-changed-in-v2) for the corrections.
**Repo:** https://github.com/lethevinh/automation-workflows (public, MIT)
**Goal:** turn the repo into a job-winning portfolio for n8n / automation
contracts (Upwork, direct clients, agency subcontracting).

**Companion file:** [`docs/agent-prompts.md`](agent-prompts.md) — copy-paste
prompts for the executing agents, one per work package, wave-ordered.

---

## 0. What changed in v2

Every claim below was re-verified against the working tree and git history.
Corrections to v1:

| v1 said | Actually | Action |
|---|---|---|
| "credentials and account IDs removed" (proposed sanitization text) | Credentials **are** clean, but `meta.instanceId`, workflow `id`/`versionId` and 12 `webhookId`s remain — and are **already public on GitHub** | New **P-1** (blocking) + owner decision on history rewrite |
| "`examples/` + `docs/case-studies/` = dead links in root README" | No broken links anywhere; they are thin stubs (6–19 lines) | Reworded; `examples/` gets real content in P1 |
| "No `test-data.json` → visitor can't run anything" | All five workflows run a **zero-credential demo lane on click** | Reframed: P1 preserves the one-click demo and adds an input contract |
| "No error-handling/reliability section" | Mechanisms **are** documented, but scattered across `The solution` / `Why it's different` | P0 standardizes a named section instead of inventing content |
| "No `Results & impact` metrics anywhere" | `## Verification` sections already carry evidence numbers (item counts, branch coverage, PASS) for 4/5 | P0 promotes them into a consistent section; business metrics stay owner-gated |
| "crg has 23 error-path refs, promise-ledger 28" | Not reproducible under any definition (raw `error` = 71/14; retry nodes = 15/18) | Numbers dropped; use the verified figures in [Appendix A](#appendix-a--per-workflow-fact-sheet) |
| P2 "extract credential types / `$env` from workflow.json" | **0 credential blocks, 0 `$env` references** in all five exports | P2 redefined: enumerate services + placeholders |
| P1 "affiliate-intake — webhook payload" | Trigger is `When clicking 'Test workflow'` (manual); no webhook exists | Corrected input contract |
| P1 puts `test-data.json` inside `n8n/<slug>/` | `examples/README.md` promises fixtures live in `examples/` | Moved to `examples/<slug>/` |
| P5 "mermaid parse check" | Real failure mode is README drift, not invalid mermaid | Replaced with a generator drift check (cheaper, currently green) |
| — | Retry policy covers 100% of credentialed nodes in crg + promise-ledger, 0% in the other three | New **P0b** (owner-gated JSON change) |
| — | Repo description says "n8n **templates**", contradicting the §1 positioning | New **P3b** (repo metadata) |
| — | Plan has no distribution step; repo has 0 stars / 0 forks | New **P7** |

---

## 1. Positioning decision (unchanged)

The winning frame is **"production systems, sanitized for public sharing"**,
not "templates I found online". The differentiators buyers screen for:

- human-in-the-loop approvals where money/reputation is at stake
- failure handling: retries, quarantine lanes, error alerts, idempotency
- real numbers, even one per project
- evidence it ran (execution screenshots, demo video)

The five workflows already contain these mechanisms, and — this is the
repo's most under-sold asset — **each one runs a zero-credential demo lane
that a visitor can execute in one click**. The upgrade is mostly
**surfacing what exists**, standardizing it, and adding proof artifacts.

Tagline direction for the root README:

> "I build automation systems, not 'connect App A to App B' zaps —
> human-in-the-loop where it matters, idempotent and observable by default."

---

## 2. Verified current state

### 2.1 Already done — do not redo

| Asset | Evidence |
|---|---|
| 5 workflows, JSON structurally sound | 0 duplicate node names, 0 connections to missing nodes, 0 nodes missing required keys, all parse |
| Credentials genuinely stripped | 0 `credentials` blocks, 0 `$env` refs, 0 hardcoded tokens/headers across all five |
| Zero-credential demo lanes | Flow-aware simulation (honouring `disabled:true` and `$json.live` gates) reaches **0 credentialed nodes** from the demo trigger in all five |
| 5 × archify `diagram.svg` + `diagram.json` | present, all committed |
| 5 × generated mermaid node graph | **in sync** with `scripts/render-mermaid.py` output (regenerated and diffed) |
| 3 × `SETUP.md` | client-report-generator, faq-chatbot, promise-ledger |
| LICENSE (MIT), `.gitignore`, root `.env.example` | present |
| CI: n8n JSON validity, secret scan, ruff | present and passes locally |
| `docs/visual-style.md` + `scripts/` tooling | present |

### 2.2 Real gaps

| Gap | Impact | Where addressed |
|---|---|---|
| `meta.instanceId` + `id`/`versionId`/`webhookId` published | makes any "sanitized" claim false; instance fingerprint | **P-1** |
| No consistently named Reliability section (content is scattered) | production credibility buried mid-README | P0 |
| No business/outcome metrics | #1 buyer question unanswered | P0 (owner-gated) |
| No `examples/<slug>/` fixtures + input contract | edge cases not reproducible by a visitor | P1 |
| No per-workflow `.env.example` **though `n8n/README.md` promises it** | broken promise + setup friction | P2 |
| Root README overclaims ("Sample data so you can run it yourself", "problem, diagram, setup, results") | live false claim to buyers | **P-1b** |
| Root featured table has no Result column | homepage doesn't sell outcomes | P3 |
| Hire-me links still placeholders | dead CTA | P3 (owner) |
| Repo description says "n8n templates" | contradicts positioning; hurts discovery relevance | P3b |
| `examples/`, `docs/case-studies/`, `zapier/`, `python/`, `ai-agents/`, `skills/` are stubs | thin content behind live links | P1/P3/P4 |
| No execution screenshots / demo video | no "it actually ran" proof | P6 (owner) |
| No distribution | 0 stars/0 forks → no inbound | P7 |

---

## 3. Rules of engagement (binding for every executing agent)

1. **No invented facts.** No fabricated client names, testimonials,
   percentages, or dollar figures. If a number is not measurable from the
   repo or supplied by the owner, write it as an explicit placeholder
   (`<!-- owner-metric -->`) — never a plausible guess.
2. **Every claim must be verifiable.** Numbers come from `workflow.json`
   (node counts, gate counts, retry counts) or from the owner. Prefer a CI
   check over a prose assertion.
3. **`workflow.json` edits are forbidden**, with exactly two sanctioned
   exceptions: P-1 (field stripping) and P0b (per-node `retryOnFail`/
   `maxTries`, owner-approved). No node insertions, no fabricated error
   branches, no renames.
4. **Preserve importability.** After any JSON change, the file must still
   parse and keep `nodes` + `connections` intact.
5. **One writer per file.** Never edit a file outside your assigned write
   scope ([§8](#8-execution-waves--write-scopes)).
6. **Style.** English, Paper theme for diagrams, conventional commits, no
   `Generated with` trailers, no bot co-author.

---

## 4. Security item (owner decision required) — P-1 rationale

Inside `meta.instanceId` in four of five exports:

```
REMOVED-INSTANCE-ID
```

- Files: `n8n/{affiliate-intake,daily-cash-tally,faq-chatbot,promise-ledger}/workflow.json`
- Also present: real-looking workflow `id`, `versionId` (4/5), 12 `webhookId`
  values, `createdAt`/`updatedAt` (crg only)
- `client-report-generator` was hand-edited (`id: client-report-generator-0001`),
  so the set is inconsistently sanitized

**Exposure status:** the repo is **public**; the identifier is in commit
`c81a929`, already on `origin/main`. GitHub API at review time: 0 stars,
0 forks, 0 watchers, 3 commits.

**Severity (stated honestly):** an n8n `instanceId` is not a credential and
grants no access. Real risks are (a) fingerprinting/correlation of the
owner's instance if its URL is known elsewhere, and (b) credibility — the
plan's own sanitization sentence would be false.

**Options:**

- **A — Rewrite history (recommended).** `git filter-repo` the five files,
  force-push. Cheap now: 0 forks, 3 commits, no stars. Removes the value
  from published history.
- **B — Strip going forward.** New commit removes the fields; the value
  stays in history and in any fork/clone already made.

Either way: strip the fields, add the CI residue check (P5), and only then
publish the sanitization sentence.

---

## 5. Work plan

Ordered by sales impact. P-1/P-1b are blocking. Waves are defined in
[§8](#8-execution-waves--write-scopes); prompts live in
[`docs/agent-prompts.md`](agent-prompts.md).

### P-1 — Sanitize exports *(blocking, agent)*

**Deliverable:** `scripts/sanitize-export.py` + stripped `workflow.json` ×5.

- Remove: `meta` (or at least `meta.instanceId`), top-level `id`,
  `versionId`, `createdAt`, `updatedAt`, `nodeGroups`, `pinData`,
  per-node `webhookId`. Keep `active: false`, `tags: []`, `settings`,
  node `id`s (needed for stable connections), `name`, `connections`.
- Script is idempotent, prints a per-file report, and is safe to re-run.
- History rewrite: **owner-gated** (see §4), not part of the agent run.

**Acceptance:** `git grep -nE 'instanceId|versionId|webhookId' -- n8n/`
returns nothing; all five files still parse; node + connection counts
unchanged from [Appendix A](#appendix-a--per-workflow-fact-sheet).

### P-1b — Kill the live overclaims *(blocking, agent)*

**Deliverable:** corrected `README.md` (root) + frozen section order in
`docs/workflow-template.md`.

- Root README line 22 claims "Sample data so you can run it yourself" and
  line 76 claims each workflow ships "problem, diagram, setup, results" —
  neither is true yet. Replace with the truth that is currently true:
  one-click zero-credential demo lane, architecture diagram, setup guide.
- Reword "Nothing here is a toy demo" only if it stays defensible.
- Freeze the v2 workflow README section order in the template so the five
  wave-1 writers cannot drift:
  `Problem → Solution → Stack & credentials → Setup → Verification →
  Reliability & error handling → Results & impact → Sanitization → CTA`.
  (Note: current READMEs use `The solution` / `Why it's different` /
  `Customize` inconsistently; v2 folds `Why it's different` into
  `The solution` and keeps `Customize` only where it exists.)

**Acceptance:** no claim in the root README lacks a supporting artifact in
the tree; template section order matches all five v2 READMEs.

### P0 — Workflow README v2 *(agent, one writer per folder)*

Per workflow, produce/standardize:

- **Reliability & error handling** — the real mechanisms, with node names:
  retry policy (`retryOnFail`/`maxTries:3` where present), live/demo gates
  (`$json.live` vs `disabled:true`), quarantine lane, approval queues,
  idempotency keys, error workflow, alert paths, per-source failure
  isolation. **Document only what the JSON does.** Where a mechanism is
  absent, say so or omit the claim — do not pad.
  - **Caveat for `client-report-generator` (verified):** its `On workflow
    error` node is **inert as shipped**. An n8n Error Trigger only fires when
    a workflow selects that workflow as its *Error Workflow*, and
    `settings.errorWorkflow` is **absent in all five exports**. The README
    line "instance-level Error Trigger emails the owner on unhandled
    failures" must be qualified with the required configuration step;
    otherwise it reads as working out of the box. Same rule for any other
    claim that depends on instance-level settings.
- **Results & impact** — two layers, clearly separated:
  1. *Evidence (repo-verifiable):* promote existing `## Verification`
     numbers (e.g. "digest exactly 1 item, 16 happy-path items,
     missing-data/duplicate/failure alerts 3/3 — PASS").
  2. *Business outcome (owner-gated):* leave an explicit
     `<!-- owner-metric: ... -->` placeholder. Never invent.
- **Sanitization notes** — only publishable **after P-1**; then the sentence
  "credentials, instance identifiers and pinned data removed" is true.
- Keep the existing `## Verification` content (it is good and already true).

**Acceptance:** all five READMEs have the v2 section order; every
reliability claim names a node that exists in that workflow's
`workflow.json`; no numeric claim that is not in Appendix A or owner-supplied.

### P0b — Retry policy parity *(owner-gated, agent)*

**Problem:** `retryOnFail: true` + `maxTries: 3` are set on **every**
credentialed node in `client-report-generator` (15/15) and
`promise-ledger` (18/18), and on **none** in `daily-cash-tally` (0/9) and
`faq-chatbot` (0/13). `affiliate-intake` has no credentialed nodes.
An "observable and idempotent by default" tagline is not credible with that
asymmetry.

**Change:** set `retryOnFail: true` + `maxTries: 3` on the existing
credentialed nodes of those two workflows. No nodes added, no logic
changed, no error branches.

**Owner approval required** because it modifies verified exports. If
declined, the Reliability sections must state the gap honestly instead.

**Acceptance:** retry coverage 9/9 and 13/13; files still parse; demo lane
still credential-free; mermaid graph unchanged (no nodes added).

> **Scope boundary (important):** P0b is *retry parity on existing nodes
> only*. It is NOT "add error handling to the workflows that mention
> `error` least". Two facts rule that framing out:
> `affiliate-intake` contains **no external call at all** (5 Code, 1 IF,
> 1 Merge, 1 Manual Trigger, 5 sticky notes) — there is nothing to retry or
> alert on, and adding a Gmail/Slack alert node would give it its **first
> credential**, destroying the "Zero credentials required" headline that
> makes it the one workflow labelled *Demo* in `n8n/README.md`.
> `daily-cash-tally` mentions no "error" string but already implements
> quarantine, escalation, gap detection and disabled live sinks — absence of
> the word is not absence of handling.
> Anything that adds nodes is a separate decision → **P0c**.

### P0c — Error-alert coverage (proposal, owner decision) *(owner-gated)*

**Question:** should the workflows other than `client-report-generator` get
a real error-alert path? Three options, no recommendation to rush:

| Option | What it costs | Verdict |
|---|---|---|
| (a) Mirror `daily-cash-tally`'s pattern: add `Error Trigger` + alert node shipped `disabled: true` | +2–3 nodes per workflow → node counts change (Appendix A, CI), and it is a **build**, not "surfacing existing behaviour"; needs n8n re-verification | Only where the story is genuinely weak (`faq-chatbot`, `promise-ledger`) |
| (b) Use n8n's native Error Workflow (`settings.errorWorkflow`) | stores a workflow id reference → conflicts with P-1 sanitization; unverifiable from the repo | Not recommended |
| (c) Document honestly: errors appear in n8n's execution list; no alert workflow configured | zero risk, weaker story | Safe default for `affiliate-intake` (keep its zero-credential purity) |

**Prerequisite:** P0 must land first — the Reliability sections have to state
what currently exists before deciding what to add.

### P1 — Fixtures + input contract *(agent, per folder)*

`examples/<slug>/test-data.json` + `expected-output.json` (or `.md`), and a
**Run it yourself** subsection in the workflow README.

- Fixtures mirror the demo fixtures already embedded in each workflow's
  `Demo …` code node — they are the *documented input contract*, not a
  replacement for the one-click demo. The demo lane stays the primary path.
- Do **not** ask the reader to repoint a trigger at a file: for
  `affiliate-intake` (manual trigger) and the demo lanes generally there is
  nothing to repoint. Document the shape + expected verdicts instead.
- Correct the input descriptions:
  - `affiliate-intake` — manual trigger, 6 sample applications
    (missing email, implausible metrics, duplicate, below threshold)
  - `faq-chatbot` — chat payloads, hit/miss/duplicate/bad-AI/lead
  - `daily-cash-tally` — till-log rows: clean shift, escalated repeat
    offender, duplicate, missing `counted_cash`, 3-day gap
  - `promise-ledger` — inbound email JSON, commitment/newsletter/fulfilment
  - `client-report-generator` — config row + 3 source adapter payloads
- Update `examples/README.md` index accordingly (wave 2).

**Acceptance:** `test-data.json` parses; keys match what the demo code node
consumes; README subsection links to the file.

### P2 — Per-workflow `.env.example` *(agent, per folder)*

`n8n/README.md` already promises one. There is nothing to extract
(0 credential blocks, 0 `$env`), so **enumerate and comment**:

- the services to connect, derived from node types actually present
  (see Appendix A), with the n8n credential type named in a comment
- the node-level placeholders the reader must replace
  (`your_chat_id` in daily-cash-tally, `owner@example.com`, sheet IDs)
- the live/demo switch explanation (`$json.live` vs `disabled: true`)

**Acceptance:** every placeholder value is empty or obviously fake; no file
resembles a real secret; the file lists exactly the services that appear in
that workflow's JSON.

### P3 — Root README sells outcomes *(agent, wave 3)*

- Featured table gains a **Result** column: evidence numbers from
  Appendix A; business metrics only when owner-supplied.
- One-line sanitization statement (after P-1).
- Skills strip: platforms, APIs, differentiators (HITL, idempotency,
  quarantine, per-source isolation).
- Wire the real CTA (owner-supplied links).

**Acceptance:** no placeholder links remain (or the section is clearly
marked as pending); every table cell traceable to an artifact or owner input.

### P3b — Repo metadata *(owner-gated, agent-assisted)*

Description currently reads "n8n templates…", contradicting §1. Rewrite
description + topics + social preview to match the positioning. `gh` is
authenticated on this machine, so it is scriptable — but it writes to the
public repo, so confirm first.

### P4 — Flagship case study *(owner-gated, agent)*

`docs/case-studies/client-report-generator.md` — deeper than the README:
client context (anonymized), before/after, architecture, failure modes,
numbers. Needs owner input; use placeholders rather than invented numbers.
This is the proposal-attachment asset.

### P5 — CI guards *(agent, wave 2)*

Extend `.github/workflows/validate.yml`:

1. **Folder contract** — every `n8n/*/` has `workflow.json`, `README.md`,
   `assets/diagram.svg`, `.env.example`; every `examples/*/` has `test-data.json`.
2. **Mermaid drift** — run `scripts/render-mermaid.py` then
   `git diff --exit-code` (currently green, so it lands clean).
3. **Sanitization residue** — fail on `instanceId`, top-level `"id":`,
   `versionId`, `webhookId` under `n8n/`.
4. **Placeholder scan** — fail on `[your-`, `your_chat_id`, `TODO`.
5. **Fixture shape** — `test-data.json` parses and matches the documented keys.
6. Keep the existing JSON validity, secret scan, ruff.
7. **Optional / only after local verification:** `docker run n8nio/n8n
   import:workflow` per file, turning "imports clean" into machine proof.
   Docker daemon was unavailable at review time — do not enable blind.

**Acceptance:** CI green on the final tree; each guard demonstrated by a
deliberate local failure.

**Additional guard — demo-lane regression (no n8n required).** Add
`scripts/verify-demo-lane.py`: for each workflow, walk the graph from the
demo triggers honouring `disabled: true` and the `$json.live` gates, and
assert (a) the demo lane still reaches **0 credentialed nodes**, (b) node and
connection counts are unchanged from Appendix A, (c) every `retryOnFail` node
still parses. This is the local substitute for an n8n instance while P-1/P0b
touch the exports — it cannot prove n8n imports the file, but it catches
structural breakage and demo-lane regressions. Dock it into
`scripts/verify-all.sh`.

### P6 — Visual proof *(owner-assisted, agent prepares)*

Shot list per workflow (which node/execution to capture, crop, redaction
rules) + a 2–3 min Loom script for `client-report-generator`. Redact
account IDs, emails, and sheet IDs from every frame.

### P7 — Distribution *(owner-gated, agent prepares copy)*

A polished repo with no traffic wins no jobs. Prepared, owner-approved:
n8n community template gallery submissions, `awesome-n8n` PRs, Reddit
r/n8n, LinkedIn post, Upwork portfolio entry. Include UTM-tagged links so
the owner can see what converts.

---

## 6. Owner input required

| Item | Needed for | Blocks |
|---|---|---|
| Decide: rewrite published history (option A) or strip forward (B)? | P-1 exposure | P-1, P0 sanitization text |
| Real metrics per workflow (even rough) | P0 Results & impact, P4 | P0 final, P4 |
| Contact links (Upwork, LinkedIn, email, site) | Root README CTA | P3 |
| Approve P0b retry change to `workflow.json`? | Reliability parity | P0b |
| P0c: add error-alert paths to the other four workflows, or document the gap? | Reliability story | P0c (after P0) |
| Confirm "Production-ready" (n8n/README.md) and "ran in production" phrasing are accurate — the exports read as demo/practice builds in places | Credibility | P0, P-1b |
| n8n instance access for screenshots | P6 | P6 |
| Client context that may be mentioned (anonymized ok) | P4 | P4 |
| Approve repo metadata rewrite (public write) | P3b | P3b |

---

## 7. Commit plan (conventional, one per group)

1. `chore(n8n): strip instance identifiers from published exports` (P-1)
2. `docs: correct root README claims and freeze v2 README template` (P-1b)
3. `docs(n8n): standardize reliability, results and sanitization sections` (P0)
   — optionally `fix(n8n): apply retry policy to remaining credentialed nodes` (P0b, separate commit)
4. `feat(examples): add per-workflow fixtures and input contracts` (P1)
5. `docs(n8n): add per-workflow env examples` (P2)
6. `docs: add results column, positioning and live CTA to root README` (P3)
7. `ci: validate folder contract, mermaid drift and sanitization` (P5)
8. `docs(case-studies): client report generator deep dive` (P4)
9. `docs(n8n): add execution screenshots` (P6)

Also commit this plan and `docs/agent-prompts.md` (both currently untracked).

No `Generated with` trailers, no bot co-author.

---

## 8. Execution waves & write scopes

| Wave | Package | Owner | Write scope |
|---|---|---|---|
| 0 | P-1 sanitize | agent | `scripts/sanitize-export.py`, `n8n/*/workflow.json` |
| 0 | P-1b claims + template | agent | `README.md`, `docs/workflow-template.md` |
| 1 | P0 + P1 + P2 per workflow | agent ×5 | `n8n/<slug>/README.md`, `n8n/<slug>/.env.example`, `examples/<slug>/**` |
| 2 | P5 CI | agent | `.github/workflows/validate.yml`, `scripts/verify-all.sh`, `scripts/verify-demo-lane.py` |
| 2 | Shared READMEs | agent | `n8n/README.md`, `examples/README.md` |
| 2 | P0b retry | agent | `n8n/{daily-cash-tally,faq-chatbot}/workflow.json` *(after owner approval)* |
| 3 | P3 root README | agent | `README.md` |
| 3+ | P0c error alerts *(only if approved, after P0)* | agent | `n8n/*/workflow.json` + affected READMEs — **re-run P-1 sanitization and update Appendix A afterwards** |
| 4 | P3b, P4, P6, P7 | owner + agent | owner-gated |

Wave 0 must land before wave 1 (writers need the frozen template and the
sanitized exports). Wave 1 folders are disjoint. Wave 2 depends on wave 1.
Wave 3 depends on wave 2.

---

## 9. Acceptance checklist

| # | Item | Verified by |
|---|---|---|
| 1 | No `instanceId`/`versionId`/`webhookId`/`id` residue under `n8n/` | `git grep` + CI guard |
| 2 | All five exports still parse; node/connection counts match Appendix A | CI + script |
| 3 | No unsupported claim in root README | manual read vs tree |
| 4 | Five READMEs share the v2 section order | CI folder contract + diff against template |
| 5 | Every reliability claim names an existing node | manual spot-check per README |
| 6 | Results sections separate evidence from owner-gated metrics | manual read |
| 7 | Sanitization sentence present **and** accurate | after P-1 |
| 8 | `examples/<slug>/test-data.json` ×5 + input contract documented | CI fixture shape |
| 9 | `.env.example` ×5, placeholders only | CI placeholder scan |
| 10 | Root README Result column + live CTA | manual |
| 11 | Repo description/topics match positioning | `gh repo view` |
| 12 | CI: contract + drift + residue + placeholder + fixtures green | Actions run |
| 13 | ≥1 flagship case study | `docs/case-studies/` |
| 14 | ≥1 execution screenshot or demo video | `assets/execution.png` (owner) |
| 15 | Distribution submitted to ≥2 channels | owner confirmation |
| 16 | No secrets committed | existing secret scan |
| 17 | History conventional-commit clean | `git log` |

---

## 10. Out of scope (deliberate)

- No `/projects` restructure — platform folders stay.
- No new workflows built "for show"; depth over breadth.
- No workflow.json edits beyond P-1 and P0b.
- No fake testimonials, client names, or invented metrics.
- No history rewrite without explicit owner approval.

---

## Appendix A — per-workflow fact sheet

Verified against the working tree at review time. Agents must use these
figures instead of estimating.

| | affiliate-intake | daily-cash-tally | faq-chatbot | promise-ledger | client-report-generator |
|---|---|---|---|---|---|
| Nodes | 13 | 20 | 40 | 56 | 87 |
| Triggers | Manual | Manual, Schedule 21:30 | Manual, Chat, Schedule (weekly) | Manual, Schedule (hourly) | Manual, Schedule (Mon 09:00), Error, SETUP manual |
| Credentialed nodes | 0 | 9 | 13 | 18 | 15 |
| Services in JSON | — | Sheets ×4, Gmail ×1, Telegram ×2, OpenAI ×2 | Sheets ×9, Gmail ×2, OpenAI ×2, Chat Trigger | Sheets ×10, Gmail ×6, OpenAI ×2 | Sheets ×6, Gmail ×4, HTTP ×4, OpenAI ×1 |
| `retryOnFail` nodes | 0 (n/a) | **0 / 9** | **0 / 13** | 18 / 18 | 15 / 15 |
| Error workflow node | none | none | none | none | **`On workflow error`** — inert until wired via n8n Error Workflow settings |
| Demo isolation | no live nodes at all | 9 × `disabled: true` | `$json.live` gate | `$json.live` gates ×3 | `$json.live` gates ×10 |
| Demo lane, 0 credentials | ✅ | ✅ | ✅ | ✅ | ✅ |
| SETUP.md | — | — | ✅ | ✅ | ✅ |
| Named differentiators | rule-based scoring, dedupe by email, exactly-one digest | 30-day history scoring, repeat-offender escalation, quarantine lane, gap detection | owner-approved FAQ write-back, lead detection, gap clustering | inbound-promise direction, chase approval queue, fulfillment detection, aging | config-sheet driven, adapter contract, idempotent ledger (`client_id`+ISO week), draft-review seam, per-source failure isolation |
| Existing evidence numbers | 4 edge cases exercised | 5 branch cases | digest 1 item / 6 happy-path / 3 branches PASS | digest 1 / happy path 5 / alerts 3-3 PASS | digest 1 / 16 happy-path / alerts 3-3 PASS |
| Sanitization residue (pre-P-1) | id, versionId, instanceId | id, versionId, instanceId | id, versionId, instanceId | id, versionId, instanceId | hand-edited id, timestamps |

**Repo-reproducible metrics** safe to publish without owner input: node
counts, credentialed-node counts, retry coverage, gate counts, demo-lane
coverage, diagram/README/demo-lane availability.
