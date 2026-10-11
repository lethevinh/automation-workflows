# Automation audit: Lead intake from the website form to the CRM

## Business problem

Web-form leads land in the shared inbox, then someone re-keys each one into
the CRM and writes a first reply by hand. On busy weeks a lead sits for a
day, and replies go out with typos or to the wrong person.

## Scope in

- Route each web-form lead into the CRM as a row
- Draft the first follow-up reply
- Collapse repeat submissions so one person is one row

## Scope out

- Lead qualification scoring
- Outbound campaigns

## Success signal

A new lead is in the CRM with a drafted first reply within ten minutes of the
form submit, and repeat submissions collapse to a single row.

## Automation candidates (ordered)

1. **Approval-gated reply drafts (a human approves before anything sends)** — Approval-gated drafts · effort S (~6h)
2. **Route web-form leads into the CRM with a follow-up reply** — Lead intake & follow-up · effort M (~8h)

_Ordered quickest-first by catalog effort; effort figures are catalog estimates, not source figures._

## Rough effort estimate

Total: **~14h** across 2 catalog-mapped candidate(s) (validate with a scoped quote before committing).
