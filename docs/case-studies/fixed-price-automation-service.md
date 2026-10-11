# Case study: from a backlog-chasing founder to a scoped, fixed-price build

**Who:** a solo founder running a small automation service on fixed-price,
milestone-based projects.
**What they wanted:** someone reliable for "clearly defined fixed-price projects
with agreed deadlines" — and a way to stop chasing project status and payment by
hand.
**What they got from this repo:** a free, deterministic audit of the process —
a scoped spec, three ordered automation candidates, and a ~12h build estimate —
plus the working reference patterns to build them.

---

## The ask (real, sourced)

The process that anchors this case study is a real ask on the n8n Community
"Jobs" board, thread 315672, posted 2026-09-22:
<https://community.n8n.io/t/looking-for-n8n-make-automation-specialist-for-ongoing-fixed-price-projects/315672>.

The poster's own words:

> "I'm building a small automation service and I'm looking for reliable n8n /
> Make specialists for ongoing project-based work." … "I'm looking for people
> who can work on clearly defined fixed-price projects with agreed deadlines."
> "Payment would be agreed per project or milestone and paid after the
> corresponding client milestone is approved and funds are released."

The operational gap behind those words: nothing tracks which milestone a project
is on, whether the client has signed it off, or whether the handover pack exists
yet — so the owner chases status by hand and payment waits on someone's memory.

## The audit (what the free audit produced)

Paste the process description into
[`skills/automation-audit/`](../../skills/automation-audit/) and the audit lane
returns a scoped spec and an ordered build list — quickest win first, with a
catalog-based effort estimate. For this ask:

1. **Track each project milestone from kickoff to client sign-off** — Milestone
   acceptance tracking · effort S (~3h)
2. **Client-brief intake with required-field checks** — Client-brief intake ·
   effort S (~4h)
3. **Handover-pack generator (flow map + runbook when a project closes)** —
   Handover-pack generation · effort S (~5h)

Rough total: **~12h** across the three candidates (validate with a scoped quote
before committing).

The audit is deterministic — no model, no API key, no network. Same description,
same spec, every run. The worked example is pinned in the pack's fixtures
(`fixtures/processes/03-fixed-price-service.md` → the audit above), so the
numbers above are reproducible in CI, not marketing.

## Mapping to this repo's patterns

The audit scopes the work; the packs in this repo are the reference patterns
each candidate builds on:

| Audit candidate | Repo pattern it maps to |
| :--- | :--- |
| Client-brief intake with required-field checks | [`csv-cleaner`](../../n8n/csv-cleaner/) — validate each field in one pass, route ok vs reason-coded quarantine, exactly one digest per run. A required-field form intake is the same validate/route/quarantine shape. |
| Milestone sign-off gates (never send until approved) | [`lead-router`](../../zapier/lead-router/) and [`backoffice-triage`](../../ai-agents/backoffice-triage/) — review-gated drafts and an approval-row gate: the machine routes and drafts, a human signs off. The "payment after milestone approval" rule is exactly that gate. |
| Handover-pack generator | [`invoice-emailer`](../../n8n/invoice-emailer/) — compose a payload against matched records, dedupe, and alert the owner on every failure; and [`invoice-ledger`](../../python/invoice-ledger/) — deterministic field extraction, low-confidence rows sent to a review file instead of silently dropped. |

## What was deliberately left out

The ask's **billing and payment processing** is out of scope for this audit —
payment release is a money action, and the pattern this repo stands behind is
*humans approve money moves, machines draft them*. The audit's `Scope out` names
it explicitly, and it stays out until a client's setup genuinely calls for a
wired payment flow.

## The result and the honest limit

The concrete result of this repo for this founder: instead of a vague "we should
automate something," they now have a scoped spec, an ordered build list with
effort figures, and reference implementations of every pattern it needs — ready
to brief a specialist with an agreed deadline and a fixed price.

The honest limit: catalog effort figures are estimates, not promises, and the
owner's real numbers — how fast a brief moves to a fixed-price quote, how many
hours the handover pack previously took — are unmeasured until the founder runs
the builds and reports them.

## Owner metrics

Unmeasured until the owner supplies real numbers; every blank below is an
explicit placeholder, not a missing detail:

<!-- owner-metric: time from brief to fixed-price quote (target: one working day) -->
<!-- owner-metric: hours saved per project by the handover-pack generator -->
<!-- owner-metric: % of projects with a sign-off date recorded vs chased by hand -->
<!-- owner-metric: number of fixed-price projects delivered with this model -->

## Start yours

Describe the process that eats your week — in a message, a call, or a paste into
[`skills/automation-audit/`](../../skills/automation-audit/) — and get back a
scoped spec and an ordered build list. Then we agree a fixed price and a
deadline. [Contact me](../../README.md#hire-me).