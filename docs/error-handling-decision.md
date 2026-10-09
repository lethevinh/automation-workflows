# Decision memo — error-alert coverage (P0c)

**Status:** proposal — needs an owner decision before any `workflow.json` is
touched. This memo changes no code.

**Question:** should the four workflows without an error path —
`affiliate-intake`, `daily-cash-tally`, `faq-chatbot`, `promise-ledger` —
get a real error-alert path, or should the gap stay documented?

**Prerequisite already met:** P0 has landed, so the Reliability sections
already state what exists and what doesn't. Option (c) below is therefore
partially the *status quo* — the honest sentences are already written.

---

## Verified baseline (from the exports, not from memory)

- `settings.errorWorkflow` is **absent in all five exports** — the only
  `settings` keys present are `executionOrder`/`binaryMode`
  (`client-report-generator` adds `saveExecutionProgress` + `timezone`).
- `client-report-generator` is the only workflow with an error lane:
  `On workflow error` (Error Trigger) → `Operator email` →
  `Format error alert` → `Email owner: workflow error` (Gmail,
  `retryOnFail` ×3). It is **inert as shipped**: an n8n Error Trigger only
  fires when some workflow selects this workflow as its Error Workflow in
  Settings. The shipped setup guide already documents the arming step
  ("Settings → Error workflow → pick this same workflow",
  `n8n/client-report-generator/README.md` setup step 6).
- The other four have no Error Trigger node and their READMEs already say
  so: `affiliate-intake` ("Any runtime error surfaces in n8n's execution
  list"), `daily-cash-tally` ("not retried or paged"), `faq-chatbot`
  ("no alert path for workflow-level failures"), `promise-ledger`
  ("unhandled failures surface in n8n's execution list").
- Retry coverage is a **separate** decision (P0b, still owner-gated):
  `promise-ledger` 18/18, `client-report-generator` 15/15,
  `daily-cash-tally` 0/9, `faq-chatbot` 0/13, `affiliate-intake` n/a.
  Retries absorb transient failures; they never alert on persistent ones,
  so P0b approval does not settle this memo's question.

## The three options

**(a) Ship a disabled error lane** — add an `Error Trigger` node plus an
alert node (optionally a Code "format" node, mirroring the
`client-report-generator` lane), shipped `disabled: true` so the
zero-credential demo lanes stay clean. Cost per workflow: **+2 nodes**
(+3 to mirror crg's format step exactly). Because the added nodes hang
off an Error Trigger — unreachable from the demo triggers — and are
disabled, the demo lane still reaches 0 credentialed nodes. But:

- It is a **build**, not surfacing existing behaviour. The export must be
  edited, re-verified in n8n, and re-run through the P-1 sanitization
  script.
- Node/connection counts change → `docs/portfolio-upgrade-plan.md`
  Appendix A, `scripts/verify-demo-lane.py` `EXPECTED` table, and the
  mermaid graphs all need regenerating.
- The lane is **still inert until armed** — same caveat as crg. The owner
  must select the workflow as its own Error Workflow in n8n Settings;
  that setting is an instance-level choice the export cannot carry (see
  option b), so the README gains a documented activation step, not a
  working-out-of-the-box alert.
- For `affiliate-intake` specifically: any alert transport (Gmail,
  Telegram, Slack, HTTP webhook) is a credentialed node — its **first**
  credential — which breaks the "Credentials needed: **None** / Demo"
  positioning in `n8n/README.md` and the README's "0 of 13 credentialed
  nodes" evidence row.

**(b) n8n native Error Workflow via `settings.errorWorkflow`** — set the
key in the export pointing at an alert workflow. **Not recommended.** The
value is a workflow-id reference — exactly the identifier class P-1 just
stripped, so publishing it contradicts the sanitization sentence; a
foreign or stale id is useless to an importer anyway. It is also
unverifiable from the repo: nothing in `workflow.json` can prove the
referenced workflow exists or is an error handler. The owner is free to
wire error workflows instance-side at any time — that needs no export
change and several READMEs already explain how.

**(c) Document the gap honestly** — state that unhandled failures surface
in n8n's execution list and no alert is configured. Zero cost, zero risk,
weaker story. Already partially in place post-P0 (baseline above); this
option means *keep it and close the question*.

## Per-workflow analysis

### affiliate-intake — recommend **(c)**

Real failure surface: there are **no external calls at all** — the 13
nodes are 5 Code (`Demo intake: sample applications`, `Validate + dedupe
+ score`, `Draft outreach`, `Owner alert`, `Owner digest`), 1 IF, 1
Merge, 1 Manual Trigger, 5 sticky notes. What can fail at runtime is a
JavaScript exception in a Code node on an input shape the fixture doesn't
cover; every *designed* failure (missing email, implausible metrics,
duplicate, below threshold) is already a reason-coded `Owner alert` item,
not an exception. And the only trigger is `When clicking 'Test workflow'`
— failures happen while someone is watching the canvas. Option (a) buys a
lane that guards interactive runs at the price of the workflow's single
most distinctive claim — "Credentials needed: None" — since any alert
node is its first credential. That trade loses. **Keep (c): the README's
honest sentence already exists (lines 131–134) and is the right shape
for a workflow whose entire failure surface is deterministic in-run
logic.**

### daily-cash-tally — recommend **(c)**, the cheapest (a) if any are approved

Real failure surface: nine credentialed nodes — Google Sheets ×4 (`Read
today's till entries`, `Read prior-30d till log`, `Append verdict to till
log`, `Park row in quarantine`), Gmail ×1 (`Email owner alert`),
Telegram ×2 (`Escalation ping`, `Send daily digest`), OpenAI ×2 — all
shipped `disabled: true`, so none can fail in the demo lane. Once
enabled, expired OAuth, a renamed/deleted sheet, quota limits, a stale
Telegram `chatId`, or an OpenAI outage each kill the run — and the workflow
runs on `Nightly 21:30`, unattended. Sharpest wrinkle: the alert
transports *are* failure surfaces — a failure inside `Email owner alert`
or `Escalation ping` produces no signal at all. The quarantine lane and
gap detection handle **data** problems, not **execution** crashes.
Still, this workflow's reliability story is already the strongest of the
four (30-day scoring, first-offense-vs-repeat-offender routing,
quarantine, gap detection), so an error lane adds the least narrative
value here. Note for the decision: if any (a) builds are approved, this
is the lowest-cost site — `disabled: true` on live nodes is already its
isolation convention, and Gmail/Telegram credentials the owner needs for
the lane already exist in its live setup. **(c) is sufficient; hold (a)
as an optional add-on, not a gap.**

### faq-chatbot — recommend **(a)**

Real failure surface: 13 credentialed nodes (Sheets ×9, Gmail ×2,
OpenAI ×2) plus the public-facing `Website visitor chat` Chat Trigger
(not credentialed). The exposure is twofold: **visitor-facing** — if
`Load FAQ answers` or `Answer from FAQ only` throws, the visitor gets
silence and the owner learns about it from a complaint, not an alert —
and **unattended** — the `Weekly gap review` schedule and the setup lane
(`Create FAQ spreadsheet` + four tab writes) can fail mid-write with no
watcher. The existing `Parse AI verdict` → `Compose alert` path is
excellent but covers *model output* failures (unparseable JSON), not
*execution* failures (OpenAI down, Sheets auth expired). Combined with
0/13 retry coverage (P0b pending), this is the weakest runtime story of
the four. Option (a) costs +2 nodes (`Error Trigger` + a Gmail alert
node — reusing the Gmail credential type the workflow already needs);
the lane sits off the Error Trigger, unreachable from the demo trigger,
and ships `disabled: true`. **Recommend (a): the only workflow where a
failure can silently strand an end user in real time.**

### promise-ledger — recommend **(a)**

Real failure surface: 18 credentialed nodes (Sheets ×10, Gmail ×6,
OpenAI ×2) on an hourly `Hourly tick (sweep at 08:00)` schedule —
unattended by design, and the workflow guards money/reputation
(commitments made to the owner). Retries are 18/18, but the subtle gap
is in the `onError` settings the README already documents as a feature:
`Write ledger row` and `Mark done in ledger` run
`onError: continueErrorOutput` with the error branch **connected to
nothing** — a failed write drops silently; the email stays unlabelled and
is re-scanned next hour, which self-heals transient faults but means a
*persistent* Sheets failure (bad credential, deleted sheet) produces no
failed execution and no alert, forever — the owner notices only when rows
are missing. Eight more nodes (`Label email processed`, both owner
emails, `Queue chase for approval`, `Notify owner of queue`,
`Mark chased in ledger`, `Escalate to owner`, `Mark escalated in ledger`)
use `continueRegularOutput`, so e.g. a failed escalation email doesn't
even fail the run. Retries cover transients; nothing covers persistence.
Option (a) costs +2–3 nodes (`Error Trigger` + Gmail alert [+ Code
formatter to mirror crg]); Gmail is already a required credential.
**Recommend (a): the highest-stakes workflow and the one whose existing
error routing is explicitly designed to continue past failures — it is
the strongest argument for a last-resort alarm.**

## Decision table

| Workflow | Option | Cost | Recommendation |
|---|---|---|---|
| affiliate-intake | (a) disabled error lane | +2 nodes; **first credential** → breaks "None / Demo" positioning; still inert until armed in Settings | ✗ |
| affiliate-intake | (b) `settings.errorWorkflow` | workflow-id reference conflicts with P-1; unverifiable from repo | ✗ |
| affiliate-intake | (c) document the gap | 0 — sentence already shipped | **✓ recommended** |
| daily-cash-tally | (a) disabled error lane | +2 nodes; cheapest (a) site — disabled-node convention + existing Gmail/Telegram creds; still inert until armed | optional add-on |
| daily-cash-tally | (b) `settings.errorWorkflow` | as above — conflicts with P-1, unverifiable | ✗ |
| daily-cash-tally | (c) document the gap | 0 — strongest existing failure story of the four | **✓ recommended** |
| faq-chatbot | (a) disabled error lane | +2 nodes (Error Trigger + Gmail alert); visitor-facing + unattended lanes get a last-resort alarm | **✓ recommended** |
| faq-chatbot | (b) `settings.errorWorkflow` | as above | ✗ |
| faq-chatbot | (c) document the gap | 0 — but leaves silent public-facing downtime | fallback if (a) declined |
| promise-ledger | (a) disabled error lane | +2–3 nodes (Error Trigger + Gmail alert [+ formatter]); covers persistent-failure silence that `onError`/`retryOnFail` deliberately route around | **✓ recommended** |
| promise-ledger | (b) `settings.errorWorkflow` | as above | ✗ |
| promise-ledger | (c) document the gap | 0 — but persistent write failures stay invisible | fallback if (a) declined |
| client-report-generator | — (lane already exists) | none — inert until armed; activation step already documented in setup step 6 | no action |

## If any (a) lanes are approved — knock-on work

1. Edit the affected `workflow.json` (new nodes + connections only; the
   lane hangs off an Error Trigger and the alert node ships
   `disabled: true`).
2. Re-verify in n8n that the lane fires when armed and the demo lane is
   unchanged (the new nodes are unreachable from demo triggers).
3. Re-run `scripts/sanitize-export.py` on the edited exports.
4. Update Appendix A node/connection counts, the `EXPECTED` table in
   `scripts/verify-demo-lane.py`, and regenerate mermaid graphs
   (`scripts/render-mermaid.py`).
5. Update each affected README's Reliability section with the same caveat
   crg carries: the lane exists but is inert until Settings → Error
   Workflow selects this workflow.

## Questions the owner must answer

1. **faq-chatbot** — approve a +2-node disabled error lane (Error Trigger
   → Gmail alert reusing the existing Gmail credential)? If yes, which
   owner address receives it?
2. **promise-ledger** — approve the same +2–3-node lane? Gmail alert to
   which address — and should it also mirror crg's Code "format" step so
   all error lanes look identical?
3. **daily-cash-tally** — documented gap only (recommended), or add the
   same disabled lane anyway since it is the cheapest site (disabled
   nodes are already the convention; Gmail or Telegram transport — which)?
4. **affiliate-intake** — confirm (c): preserve zero-credential purity
   and keep the honest-gap sentence, or accept a first credential for an
   alert lane guarding only interactive runs?
5. **For every approved lane** — the owner accepts the arming step is a
   manual n8n Settings action (Error Workflow → this workflow) that the
   export cannot carry, so the README documents it rather than the repo
   proving it. OK to document it that way?
6. **Knock-on approvals** — if lanes are added: approve Appendix A /
   `verify-demo-lane.py` / mermaid updates and the extra P-1 re-run.
7. **Separate pending gate** — P0b retry parity for `daily-cash-tally`
   (0/9) and `faq-chatbot` (0/13) is still awaiting approval. Confirm
   this memo's recommendations independent of that decision (retries mute
   transient noise; they never alert on persistent failure).

---

## Decision (owner, 2026-10-09)

Option (a) **implemented** for `faq-chatbot` and `promise-ledger`: each
export now carries a `On workflow error` → `Format error alert` →
`Email owner: <slug> error` lane (mirroring client-report-generator),
inert until the workflow is selected as an Error Workflow in n8n Settings.
`daily-cash-tally` stays option (c) — its existing quarantine/escalation
story is strong enough. `affiliate-intake` is unchanged — any alert node
would be its first credential and break the zero-credential positioning.
