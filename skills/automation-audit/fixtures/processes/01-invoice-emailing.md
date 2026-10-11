# Process: Invoice emailing into the bookkeeping ledger

Source: synthetic — first of the two fixture process descriptions (TASK-2026-798).

## Business problem

Invoices and receipts arrive by email every day, and someone keys each one
into the bookkeeping spreadsheet by hand. It takes about an hour of the
owner's morning, duplicates slip in when two people are both on the inbox,
and there is no record of which invoice was reviewed and when.

## In scope

- Parse the emailed invoice and receipt attachments
- Append each one to the bookkeeping ledger
- Flag items that do not scan cleanly for a human review

## Out of scope

- Paying the invoices
- Posting entries into accounting software

## Success signal

The ledger is up to date with under half an hour of invoice work per day, and
every entry has a review timestamp.

## Automation opportunities

- Parse emailed invoices & receipts into the ledger
- Auto-save email attachments into the right folder
