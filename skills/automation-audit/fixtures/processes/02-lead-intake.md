# Process: Lead intake from the website form to the CRM

Source: synthetic — second of the two fixture process descriptions (TASK-2026-798).

## Business problem

Web-form leads land in the shared inbox, then someone re-keys each one into
the CRM and writes a first reply by hand. On busy weeks a lead sits for a
day, and replies go out with typos or to the wrong person.

## In scope

- Route each web-form lead into the CRM as a row
- Draft the first follow-up reply
- Collapse repeat submissions so one person is one row

## Out of scope

- Lead qualification scoring
- Outbound campaigns

## Success signal

A new lead is in the CRM with a drafted first reply within ten minutes of the
form submit, and repeat submissions collapse to a single row.

## Automation opportunities

- Route web-form leads into the CRM with a follow-up reply
- Approval-gated reply drafts (a human approves before anything sends)
