# affiliate-intake — sample input

`test-data.json` documents the **input contract** for
[`n8n/affiliate-intake`](../../n8n/affiliate-intake/): one JSON object per
application, the same shape the workflow's `Demo intake: sample
applications` Code node emits.

## How to run

The one-click demo lane is the primary path: import
`n8n/affiliate-intake/workflow.json` and click **Test workflow** — the
bundled intake node emits this batch (plus one extra qualified applicant),
so every branch runs immediately. There is nothing to repoint and nothing
to configure; this file exists to document the input shape and the verdict
each row produces, e.g. if you build a real form intake later.

## Input shape

| Field | Type | Rule applied by `Validate + dedupe + score` |
|---|---|---|
| `name` | string | Required — missing → rejected |
| `email` | string | Required; lower-cased + trimmed; second occurrence in a run → rejected as duplicate |
| `platform` | string | Required; scores only if in `RULES.accepted_platforms` (instagram / tiktok / youtube) |
| `handle` | string | Cosmetic — used in the outreach draft |
| `followers` | number | ≥ 0; with fewer than `min_posts_for_claimed_reach` (10) posts, a claimed audience is implausible → rejected |
| `engagement_rate` | number | Percent, must be 0–100 |
| `posts` | number | ≥ 0 |
| `niche` | string | Cosmetic — used in the outreach draft |

Defaults from the editable `RULES` block: `min_followers` 5000,
`min_engagement_rate` 2.0, `min_posts_for_claimed_reach` 10,
`min_fit_score` 60.

## Samples → expected verdicts

| # | Applicant | Edge case | Expected verdict |
|---|---|---|---|
| 1 | Ari Lopez | Clean qualified applicant | **Qualified** — fit score 92/100 → `Draft outreach` produces a personalized draft |
| 2 | Nate Null | Missing `email` | Rejected → `Owner alert`: `missing required field: email` |
| 3 | Mia Moon | Implausible metrics (2,000,000 followers, 0 posts) | Rejected → `Owner alert`: `implausible metrics: 2000000 followers but only 0 posts` |
| 4 | Ari Again | Duplicate application (same email as #1) | Rejected → `Owner alert`: `duplicate of ari@example.com — already seen this run` |
| 5 | Sam Small | Below threshold (unaccepted platform, low followers/engagement) | Rejected → `Owner alert`: `fit score 8 below threshold 60` |

Expected digest — exactly one item from `Merge branches` → `Owner digest`:

> `Run complete: 1 applicant(s) qualified, 4 alert(s)`

All emails are `example.com` placeholders; no real applicant data.
