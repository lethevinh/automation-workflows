# Case study — Client Report Generator

*Weekly per-client marketing reports, automated end to end: three ad/data
sources behind one adapter contract, deterministic deltas, a human review
seam, and an idempotent send ledger.*

**Workflow:** [`n8n/client-report-generator/`](../../n8n/client-report-generator/)
(87 nodes · [diagram](../../n8n/client-report-generator/assets/diagram.svg)
· [setup guide](../../n8n/client-report-generator/SETUP.md))

## Context

<!-- owner-input: client domain and size — e.g. "a 3-person marketing
agency running weekly reporting for retainer clients" -->

Before this workflow, producing the weekly report meant
<!-- owner-input: the manual process — which tools, which steps, how long
per client per week -->.

## The problem

<!-- owner-input: the cost of the manual process — hours/week, error rate,
what went wrong when it slipped -->

The structural difficulties, independent of the client context:

- three data sources with different APIs, auth schemes and metric shapes
- numbers must be **computed, not generated** — an LLM inventing a delta
  is worse than no report
- every client has different sources, channels and thresholds — a
  per-client hardcode would not survive the second engagement
- a report sent twice, or sent to the wrong channel, is worse than a late
  one

## What I built

An 87-node n8n pipeline driven by a config sheet — adding a client is one
spreadsheet row, not a code change.

- **Config-driven execution.** One row per client carries the whole
  contract: `src_*`/`sink_*` toggles, `delivery_mode`, brand cells,
  thresholds. A one-click SETUP lane provisions the workbook.
- **Adapter contract.** Meta Ads, Google Ads and GA4 each sit behind a
  fetch → normalize pair emitting the same row shape; a fourth source is
  an "Extension dock", not a rewrite.
- **Deterministic core, AI at the edge.** WoW deltas are computed in Code
  nodes; the AI writes prose around an already-finished table — it can
  never invent a number.
- **Human-in-the-loop by default.** `delivery_mode=draft` files a Gmail
  draft instead of sending — a review seam that flips to full-send per
  client, per sink.
- **Idempotent delivery.** A reports ledger keyed on `client_id` + ISO
  week (`Collect sent keys` → `Dedupe check` → `Already sent?`) makes
  re-runs safe: same week, same client, no double-send.
- **Failure isolation.** Per-source failures route to a composed alert
  instead of killing the batch; sink-level sends are gated on the API's
  `ok` flag; all 15 credentialed nodes carry `retryOnFail` with
  `maxTries: 3`.
- **Error lane, honestly labelled.** The export includes an
  `On workflow error` → operator-email lane; it arms only once an n8n
  workflow selects it as its Error Workflow in settings — documented,
  not implied.

## Results

**Repo-verifiable evidence:** container pilot on `n8n:latest` with zero
credentials — digest exactly 1 item, 16 happy-path items, missing-data /
duplicate / failure-alert branches 3/3 PASS; three config variants
replayed with pinned deltas verified. Retry coverage 15/15 credentialed
nodes.

**Business outcome:**

<!-- owner-input: pilot scope — how many clients, for how long -->
<!-- owner-input: before/after numbers — report-writing time per week,
tooling spend replaced, error rate -->

## What I'd do differently

- <!-- owner-input: honest retrospective — what was tricky, what would
      you change in a v2 -->
- Candidate improvements already visible from the architecture: arm the
  error lane at deploy time rather than leaving it to settings, and grow
  the source library through the extension dock.

---

*Need reporting like this for your clients?
[Contact me](../../README.md#hire-me)*
