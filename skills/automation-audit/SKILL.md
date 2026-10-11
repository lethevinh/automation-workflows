---
name: automation-audit
description: "Turn a described business process into a scoped spec, an ordered automation list and a rough effort estimate. Use when someone describes a manual process — invoices by email, leads re-keyed into a CRM, reports assembled by hand — and asks what is worth automating first, what the scope is, or roughly what it takes. The free-audit lead magnet: a described process in, a scoped spec plus a ranked build list and an effort estimate out."
license: MIT
metadata:
  version: "1.0.0"
  status: active
---

# Automation Audit

A described business process goes in; a three-part audit comes out — the
**scoped spec** (what the process is, what is in and out of scope, and the
success signal), an **ordered automation list** (each candidate matched to an
effort bucket, quickest win first) and a **rough effort estimate**. This is the
free-audit lead magnet: the same structure an agency hands back after a paid
discovery call, produced from a written description.

## When to Use

Load this skill when any of these is true:

- Someone describes a manual, repetitive process and asks *what can be
  automated here*, *what would you scope first*, or *how long would this
  take*.
- A free-audit request arrives — a founder or ops lead pastes their process
  (invoices by email, leads re-keyed into a CRM, appointments by phone,
  reports assembled from spreadsheets, supplier checks, feedback triage) and
  wants a scoping answer before any build commitment.
- You are preparing a fixed-price quote or a proposal and need the process
  broken into a scoped spec plus an ordered candidate list with rough effort.
- A process description must be checked for *completeness* before it can be
  scoped — the five required sections below are the minimum a good brief
  carries.

Do **not** load it to design the automation implementation itself, to write the
workflow code, or to give a firm delivery quote — the audit produces a
*rough* estimate that a scoped quote still has to confirm.

## Procedure

### 1. Read the description for the five required sections

Every auditable process description carries exactly these sections:

```
## Business problem
## In scope
## Out of scope
## Success signal
## Automation opportunities
```

If one is missing or empty, stop and ask for it — an audit built on a missing
section silently guesses, which is the one thing the audit must never do. The
`## Business problem` paragraph is the owner's own words; keep them. `##
Success signal` is the measurable before/after that says the automation
worked.

### 2. Produce the scoped spec

Emit the first four output sections, echoing the owner's own words:

- **Business problem** — what happens today and what it costs in time or
  errors.
- **Scope in** — the steps this audit covers.
- **Scope out** — what it deliberately does not cover (name it, so a later
  quote cannot quietly expand).
- **Success signal** — the measurable outcome.

### 3. Build the ordered automation list

Take each `## Automation opportunities` bullet — one candidate per bullet —
and match it to the **effort catalog** below by its keyword, then order
quickest-first (smallest catalog effort first). Candidates that match no
catalog entry are marked `effort TBD (scope first)` and are not estimated.
The ordering rule is deterministic so two auditors reach the same list from
the same description.

### 4. Emit the rough effort estimate

Sum the matched catalog efforts into a total, and label every figure as a
**catalog estimate** — an internal planning number, never a quote and never a
figure lifted from the description. Unmapped candidates are excluded from the
total and flagged for a scoped quote.

Every audit therefore always contains these six sections:

```
## Business problem
## Scope in
## Scope out
## Success signal
## Automation candidates (ordered)
## Rough effort estimate
```

### 5. Verify with the credential-free lane

The deterministic spine of this skill is `audit_lane.py` — no model, no key,
no network. Run it to prove the structure holds:

```bash
python3 audit_lane.py --audit fixtures/processes/01-invoice-emailing.md
python3 audit_lane.py --self-check      # both fixtures + the worked example
```

`--self-check` processes every `fixtures/processes/*.md`, prints PASS/FAIL
against `fixtures/expected/`, and fails if any output differs or is not
reproducible on a second run. Running the skill *live* (by an agent or a
person) is steps 1–4 with judgement on top; the lane is the offline proof that
steps 1–4 produce every required section.

### Effort catalog

The rough buckets each candidate is matched against. The keyword is matched
case-insensitively inside the candidate line; the longest keyword wins, ties
resolve to catalog order.

| Keyword | Pillar | Bucket | Catalog estimate |
| :--- | :--- | :--- | :--- |
| invoice | Invoice & receipt capture | S | ~4h |
| attachment | Attachment filing | S | ~3h |
| lead | Lead intake & follow-up | M | ~8h |
| order | Order status & tracking replies | M | ~8h |
| support | Support-ticket triage | M | ~9h |
| feedback | Feedback & review triage | S | ~4h |
| report | Report auto-assembly | M | ~10h |
| approval | Approval-gated drafts | S | ~6h |
| calendar | Appointment scheduling | S | ~5h |
| inventory | Stock-level reorder alerts | M | ~12h |
| brief | Client-brief intake | S | ~4h |
| milestone | Milestone acceptance tracking | S | ~3h |
| handover | Handover-pack generation | S | ~5h |

The catalog is the skill's own buckets, not a market rate — it is what a
scoped quote is checked *against*, and it changes in one place
(`audit_lane.CATALOG`).

### Worked example

`fixtures/processes/03-fixed-price-service.md` is a **real** ask — the n8n
Community "Jobs" thread *Looking for n8n / Make automation specialist for
ongoing fixed-price projects* (posted 2026-09-22) — turned into an auditable
process. The description quotes the poster's own words and cites the thread
URL; the audit it produces
(`fixtures/expected/03-fixed-price-service.audit.md`) contains only catalog
effort figures, so no number in the worked example is invented. The README's
"Worked example" section carries the source line and the numbers provenance.

## Output contract

| Section | Source |
| :--- | :--- |
| Business problem | echoed from the description |
| Scope in | echoed from the description |
| Scope out | echoed from the description |
| Success signal | echoed from the description |
| Automation candidates (ordered) | matched to the catalog, quickest-first |
| Rough effort estimate | sum of matched catalog efforts (estimates) |

The lane is deterministic and offline: same description in, byte-for-byte
same audit out. The published repo's CI job only has to run
`python3 -m pytest -q` in this folder.
