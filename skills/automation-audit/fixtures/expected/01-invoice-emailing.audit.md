# Automation audit: Invoice emailing into the bookkeeping ledger

## Business problem

Invoices and receipts arrive by email every day, and someone keys each one
into the bookkeeping spreadsheet by hand. It takes about an hour of the
owner's morning, duplicates slip in when two people are both on the inbox,
and there is no record of which invoice was reviewed and when.

## Scope in

- Parse the emailed invoice and receipt attachments
- Append each one to the bookkeeping ledger
- Flag items that do not scan cleanly for a human review

## Scope out

- Paying the invoices
- Posting entries into accounting software

## Success signal

The ledger is up to date with under half an hour of invoice work per day, and
every entry has a review timestamp.

## Automation candidates (ordered)

1. **Auto-save email attachments into the right folder** — Attachment filing · effort S (~3h)
2. **Parse emailed invoices & receipts into the ledger** — Invoice & receipt capture · effort S (~4h)

_Ordered quickest-first by catalog effort; effort figures are catalog estimates, not source figures._

## Rough effort estimate

Total: **~7h** across 2 catalog-mapped candidate(s) (validate with a scoped quote before committing).
