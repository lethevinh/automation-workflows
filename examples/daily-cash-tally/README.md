# daily-cash-tally — input contract & fixtures

`test-data.json` mirrors, row for row, what the `Demo till log
(entries + history)` code node inside
[`n8n/daily-cash-tally/workflow.json`](../../n8n/daily-cash-tally/workflow.json)
emits when you click **Test workflow**. It is the *documented input
contract* — the shape your own till log must match — not a replacement for
the one-click demo, which stays the primary way to run the workflow (there
is nothing to repoint: the demo intake is a Code node).

## Input shape

One element = one till-log row = one item's `json` payload. The
`Reconcile, score history, escalate repeats` node consumes exactly:

| Field | Type | Required |
|---|---|---|
| `date` | string, `YYYY-MM-DD` | yes — missing/empty → quarantine |
| `shift` | string | yes — part of the dedupe key (`date\|shift`) |
| `staff` | string | yes — the unit repeat-offender scoring counts |
| `expected_sales` | number | yes — non-number → quarantine |
| `counted_cash` | number | yes — non-number/absent → quarantine |

There is no "today" flag: the reconciler treats the **max `date` among
complete rows as today**; every earlier complete row is 30-day history.
In production the same rows come from the `today` and `history` Sheet tabs.

## The batch

The fixture is a realistic dirty batch: four history rows (two prior
over-band nights for the same staff member seed the escalation), then
today's submissions — with nothing at all logged for 2026-09-28 → 09-30.

| Row(s) | Edge case | Expected verdict |
|---|---|---|
| `2026-09-25/27` — Linh | history, inside tolerance | no verdict; feeds scoring only |
| `2026-09-26/27` — Nga | history, over band (−120.00, −150.00) | 2 prior over-band shifts → seeds escalation |
| *(absent)* | three-day submission gap, `09-28 → 09-30` | route `alert` → `Email owner alert` |
| `2026-10-01` — Linh, day | clean shift (−1.60 within ±10.25 band) | route `clean` → `Append verdict to till log` |
| `2026-10-01` — Nga, night (1420.00) | escalated repeat offender — over-band shift #3 in 30 days | route `escalation` → `Escalation ping` |
| `2026-10-01` — Nga, night (1421.00) | duplicate — same `date\|shift` as the previous row | route `quarantine` → `Park row in quarantine` (first submission kept) |
| `2026-10-01` — Bo, day | malformed — `counted_cash` missing | route `quarantine` → `Park row in quarantine`, flagged `missing counted_cash` |

Every run also emits **exactly one digest** regardless of branch outcomes,
routed to `Send daily digest`. For this batch it reports 1 clean shift,
4 alerts, `leak_30d_total` −450.00, and `repeat_watch` = Nga (2 prior
over-band shifts).

All routing is deterministic — tolerance band
(`max(tolerance_abs: 5.00, expected_sales × 0.5%)`), `escalate_after: 2`
priors, `history_days: 30` — so the same fixture always produces the same
verdicts. The disabled OpenAI nodes only rephrase output.
