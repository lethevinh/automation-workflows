# Zapier test-mode walkthrough

This is the step-by-step a builder follows in their own Zapier account to see
the lead router run in **test mode**. It is the live companion to the offline
replay ([`../replay.py`](../replay.py)) — the replay proves the logic with no
account, this proves the wiring in a real editor.

> **Screenshots are owner-supplied at publish.** Capturing them needs a live
> Zapier account, which is out of scope for the agent build. The steps below
> are the shot list.

## Build order

1. **Trigger — Webhooks by Zapier → Catch Hook.** Copy the webhook URL Zapier
   mints. Send it one JSON body shaped like a fixture lead (see
   [`../fixtures/leads-8.json`](../fixtures/leads-8.json)): `lead_id`, `email`,
   `name`, `company`, `company_size`, `country`, `source`, `phone`, `message`.
   *Shot:* the trigger with the sample payload filled in.
2. **Action — Formatter by Zapier → Text → Lowercase**, then **Trim**, on
   `email`. *Shot:* the two Formatter steps with the `email` field mapped.
3. **Action — Close → Find Contact**, searching by the formatted email.
   *Shot:* the search step with `email` as the lookup field.
4. **Action — Paths by Zapier.** Branch A fires when the search returns a
   result (duplicate → log only). Branch B is the new-lead lane. *Shot:* both
   path rules.
5. **Action — Formatter by Zapier → Numbers → Spreadsheet-Style Formula**, one
   term per `scoring.rules` entry in [`../spec.json`](../spec.json). *Shot:* the
   five-term formula.
6. **Action — Paths by Zapier** on the score: hot at 55, nurture at 30, cold
   below. *Shot:* the three thresholds.
7. **Hot lane — Close → Create/Update Contact**, then **Gmail → Create Draft**.
   *Shot:* the upsert mapped to the contact fields, and the draft body.
8. **Log lane — Google Sheets → Create Spreadsheet Row**, then **Slack → Send
   Channel Message** for the digest. *Shot:* the log row mapping and the digest
   message.
9. **Error handling.** Add an error handler to the Close, Gmail, Sheets and
   Slack steps; point it at the ops channel. *Shot:* the handler configured on
   one step.

## What to expect in the test pane

- The trigger shows the sample payload's fields by name.
- The Formatter steps show the normalized email and the numeric score.
- Hot, nurture and cold leads light up different path branches; the duplicate
  branch lights up when you re-play L-1001 then L-1004.
- The digest message is emitted once for the run.

## Why this is not a one-click public demo

A public Zap template cannot contain Formatter, Paths or Webhooks steps, and it
never runs for a visitor without their own connected account. The offline
replay is therefore the credential-free substitute — see the README's
**The honest limit** section.
