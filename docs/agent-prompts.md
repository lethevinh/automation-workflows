# Agent prompts — portfolio upgrade

Copy-paste prompts for executing the plan in
[`docs/portfolio-upgrade-plan.md`](portfolio-upgrade-plan.md). One agent per
prompt. Respect the wave order in §8 of the plan — wave 0 must land before
wave 1, wave 1 before wave 2, wave 2 before wave 3.

## How to use

1. Paste the **shared preamble** at the top of every agent prompt.
2. Pick the prompt for the package and paste it under the preamble.
3. Give the agent **only** the write scope listed in that prompt.
4. When the agent reports done, check its own verification output, then re-run
   the VERIFY commands from that prompt yourself. After P5-CI lands you can use
   `bash scripts/verify-all.sh` instead.
5. Never run two prompts whose write scopes overlap at the same time.

Wave 0 (parallel, different files): `PROMPT P-1`, `PROMPT P-1b`
Wave 1 (parallel, one workflow each): `PROMPT W` + its data block (`W1`…`W5`) — needs wave 0 done
Wave 2 (parallel): `PROMPT P5-CI`, `PROMPT R-shared`, `PROMPT P0b` (owner-gated)
Wave 3: `PROMPT P3-root`, then `PROMPT P0c` (decision memo, after P0 has landed)
Wave 4 (owner-gated): `PROMPT P3b-meta`, `PROMPT P4-case`, `PROMPT P6-visual`, `PROMPT P7-dist`

**New here? Run the canary first:** dispatch `PROMPT W` + the `W2
data block — daily-cash-tally` (smallest README, 20 nodes) alone, inspect the
result against the frozen template, and only then fan out the other four. One
bad template reading caught early beats five identical reworks.

---

## SHARED PREAMBLE (paste first, always)

```
You are working in the repo /Users/le/Projects/automation-workflows — a public
portfolio of n8n automation workflows used to win freelance contracts.

Before doing anything:
1. Read docs/portfolio-upgrade-plan.md in full, especially §3 "Rules of
   engagement" and §8 "Execution waves & write scopes". Treat them as binding.
2. Read the files in your write scope before editing.

Binding rules:
- NEVER invent facts: no fake client names, testimonials, percentages, dollar
  figures, or "approximately" numbers that were not supplied. If a number is
  needed and not available, leave an explicit `<!-- owner-metric: ... -->`
  placeholder and report it.
- Every claim must be traceable to the repo (workflow.json, scripts, CI) or to
  explicit owner input.
- Do NOT edit any workflow.json unless your prompt explicitly authorizes it.
- Stay strictly inside your write scope. Do not reformat, rename, or "tidy"
  files outside it. Do not touch other agents' files.
- Preserve existing true content (the `## Verification` sections are accurate —
  keep them).
- Language: English. Conventional commits. No "Generated with" trailers, no
  bot co-author.
- When finished, report: files changed, exact verification commands you ran,
  their output, and any placeholder you left for the owner. If something in
  the plan contradicts the repo, report the contradiction instead of guessing.
```

---

## PROMPT P-1 — Sanitize the published n8n exports

**Wave 0 · write scope:** `scripts/sanitize-export.py` (new), `n8n/*/workflow.json`

```
TASK: Remove leaked instance metadata from the five published n8n exports and
provide a reproducible script that keeps them clean.

CONTEXT: The repo is public. Four of five exports embed the owner's n8n
instance identifier, plus real-looking workflow ids, version ids and webhook
ids. See plan §4.

STEPS:
1. Write scripts/sanitize-export.py:
   - takes one or more workflow.json paths (default: n8n/*/workflow.json)
   - removes: top-level "meta" (or "meta"."instanceId" if meta carries other
     keys you judge useful — prefer removing the whole object), top-level
     "id", "versionId", "createdAt", "updatedAt", "nodeGroups", "pinData",
     and per-node "webhookId"
   - preserves everything else exactly: nodes (including per-node "id" — needed
     for stable connections), connections, settings, "active": false, tags,
     names, notes, parameters
   - is idempotent, prints a per-file summary of removed keys, exits non-zero
     on malformed JSON
   - must not reorder or reformat unrelated JSON beyond normal json.dumps with
     indent=2 and a trailing newline (match the existing file formatting)
2. Run it on n8n/*/workflow.json.
3. Verify each file still parses and that node and connection counts are
   unchanged versus the numbers below.

EXPECTED COUNTS (must not change):
  affiliate-intake 13 nodes | daily-cash-tally 20 | faq-chatbot 40
  promise-ledger 56 | client-report-generator 87
If any count changes, you broke the file — revert and investigate

VERIFY (paste output in your report):
  python3 -c "import json,glob;[json.load(open(f)) for f in glob.glob('n8n/*/workflow.json')];print('parse ok')"
  git grep -nE '"instanceId"|"versionId"|"webhookId"|"(createdAt|updatedAt)"' -- n8n/ || echo "residue: none"
  python3 - <<'EOF'
  import json,glob
  for f in sorted(glob.glob('n8n/*/workflow.json')):
      d=json.load(open(f))
      print(f, len(d['nodes']), sum(len(o or []) for v in d['connections'].values() for s in v.get('main',[]) for o in s))
  EOF

DO NOT: rewrite workflow logic, rename nodes, add nodes, strip per-node "id",
or rewrite git history (history rewrite is a separate owner decision).
```

---

## PROMPT P-1b — Kill the live overclaims and freeze the README template

**Wave 0 · write scope:** `README.md`, `docs/workflow-template.md`

```
TASK: The root README currently promises artifacts that do not exist, and the
workflow README template does not match the structure we are standardizing.
Fix both.

STEPS:
1. README.md (root):
   - The "Every workflow ships with" list claims "Sample data so you can run it
     yourself" — no test data files exist yet (they land in P1). Replace with
     what IS true today: a zero-credential demo lane you can run in one click
     after import, an architecture diagram, a setup path.
   - Line ~76 claims each workflow ships "problem, diagram, setup, results" —
     Results do not exist yet. Reword to the v2 order without claiming Results
     is already there, or mark it as the target format.
   - Keep "Nothing here is a toy demo" only if every following bullet stays
     defensible after your edit.
   - Do not touch the Services, How I work, or Hire me sections — the CTA
     placeholders are fixed in P3 after the owner supplies links.
2. docs/workflow-template.md:
   - Freeze this section order and make the template show it in that order:
     Problem → Solution → Stack & credentials → Setup → Verification →
     Reliability & error handling → Results & impact → Sanitization notes →
     CTA.
   - Move "Why it's different" out of the order (it gets folded into
     "The solution"); keep "Customize" documented as optional.
   - For Reliability, Results and Sanitization, include one line of guidance:
     document only what workflow.json actually does; separate repo-verifiable
     evidence from owner-supplied business metrics; publish the sanitization
     sentence only after the exports are clean.
   - Do not restructure the folder contract block (workflow.json,
     .env.example, README.md, SETUP.md, assets/) — that contract is correct
     and other packages depend on it.

VERIFY: read your edited README top-to-bottom and list every claim you kept
that is not yet backed by a file in the tree. Report that list — do not
silently delete true content.

DO NOT: add Result columns or metrics (that is P3), invent metrics, or edit
anything under n8n/.
```

---

## PROMPT W — Workflow README v2 + `.env.example` + fixtures

**Wave 1 · one agent per workflow.** Copy the template below and paste the
matching data block. Write scope for each: `n8n/<slug>/README.md`,
`n8n/<slug>/.env.example` (new), `examples/<slug>/**` (new).

```
TASK: Bring n8n/<SLUG>/ up to the v2 documentation standard and add the
missing .env.example and run-it-yourself fixture.

READ FIRST: docs/workflow-template.md (frozen order), n8n/README.md (index and
folder contract), your n8n/<SLUG>/workflow.json and existing README.md.

STEPS:
1. README.md — reorganize into the frozen section order, preserving all true
   existing content:
   - "Reliability & error handling": describe ONLY mechanisms that exist in
     this workflow's JSON, naming the actual nodes. Cover what applies from:
     retry policy (retryOnFail / maxTries), live-vs-demo isolation
     ($json.live gates or disabled:true nodes), quarantine lane, approval
     queue, idempotency key, error workflow node, alert paths, per-source
     failure isolation. If a mechanism is absent, omit it — do not pad and do
     not claim it.
   - "Results & impact": two clearly separated layers.
     (a) Evidence — promote the existing Verification numbers for this
         workflow into a small table (item counts, branch coverage, PASS).
     (b) Business outcome — leave `<!-- owner-metric: <what is needed> -->`
         placeholders. NEVER invent numbers.
   - "Sanitization notes": only publish the sentence if the exports are already
     sanitized (P-1 must have landed). State truthfully what was removed.
   - Keep the existing `## Verification` content intact.
2. .env.example (new) — there are no credential blocks or $env references in
   the export, so ENUMERATE, don't extract:
   - list exactly the services that appear in this workflow's node types
   - name the n8n credential type in a comment (e.g. Google Sheets OAuth2,
     Gmail OAuth2, Telegram bot token, OpenAI API key, Header Auth / Custom
     Auth for HTTP nodes)
   - list the node-level placeholders a reader must replace (e.g.
     "your_chat_id", owner email, spreadsheet id)
   - explain the live/demo switch for this workflow
   - every value empty or obviously fake; no real-looking secrets
3. examples/<SLUG>/test-data.json (new) + examples/<SLUG>/README.md — the
   documented INPUT CONTRACT, mirroring the demo fixtures already embedded in
   this workflow's Demo code node:
   - test-data.json: realistic sample input matching the fields the demo code
     node consumes, covering the edge cases listed in your data block
   - README.md: the input shape, which edge case each sample triggers, and the
     expected verdict per sample
   - IMPORTANT: the one-click demo lane stays the primary way to run it. Do not
     tell the reader to repoint a trigger at the file — for manual-trigger demo
     lanes there is nothing to repoint. Document the shape and expected output.
4. Add a "Run it yourself" subsection in the workflow README linking to
   examples/<SLUG>/.

VERIFY (paste output):
  python3 -c "import json;d=json.load(open('examples/<SLUG>/test-data.json'));print('fixture ok',type(d))"
  grep -n '^## ' n8n/<SLUG>/README.md          # must match frozen order
  python3 - <<'EOF'
  import json,re
  d=json.load(open('n8n/<SLUG>/workflow.json'))
  names={n['name'] for n in d['nodes']}
  txt=open('n8n/<SLUG>/README.md').read()
  print('unmatched node references:', [m for m in re.findall(r'`([^`]+)`',txt) if m in names]==[] or 'n/a')
  print('nodes:',len(names))
  EOF

DATA BLOCK FOR: <SLUG>
```

### W1 data block — affiliate-intake
```
slug: affiliate-intake | 13 nodes | trigger: Manual only ("When clicking
'Test workflow'") | credentialed nodes: 0 — this workflow needs NO
credentials; .env.example must say so explicitly and list nothing
retry: none, and none is needed (no external calls)
isolation: no live nodes exist at all; the demo intake is a Code node
error workflow node: none
mechanisms to document: editable RULES scoring, dedupe by email,
sanity-check of self-reported metrics, reason-coded rejection, Merge node
guaranteeing exactly one owner digest per run
existing evidence: 4 edge cases exercised (missing email, implausible
metrics, duplicate, below threshold)
demo fixture edge cases for examples/affiliate-intake/test-data.json:
missing email, implausible metrics, duplicate application, below threshold,
one clean qualified applicant
note: the README claims "~2 minutes" setup; keep it
```

### W2 data block — daily-cash-tally
```
slug: daily-cash-tally | 20 nodes | triggers: Manual + Schedule 21:30
credentialed nodes: 9 — Google Sheets x4, Gmail x1, Telegram x2, OpenAI x2
  (all 9 ship with "disabled": true — the demo lane passes data through)
retry: 0 of 9 credentialed nodes have retryOnFail. Say so plainly or omit the
  claim; do NOT promise retries here (P0b may add them later)
isolation: disabled: true on all 9 live nodes — there are NO $json.live gates
  in this workflow. Document this as the mechanism, incl. that the reader must
  enable the greyed-out nodes and attach credentials to go live
error workflow node: none
placeholders to document: your_chat_id (Telegram chatId on "Escalation ping"
  and "Send daily digest")
mechanisms to document: 30-day history scoring, first-offense email vs
  repeat-offender Telegram escalation, quarantine lane ("Park row in
  quarantine"), gap detection, one digest per run, deterministic verdicts with
  optional AI phrasing only
existing evidence: 5 branch cases (clean shift, escalated repeat offender,
  duplicate, missing counted_cash, three-day submission gap)
demo fixture edge cases: the same 5 cases
note: README states an earlier zero-credential version exists in git history —
  keep that sentence
```

### W3 data block — faq-chatbot
```
slug: faq-chatbot | 40 nodes | triggers: Manual + Chat Trigger + weekly Schedule
credentialed nodes: 13 — Google Sheets x9, Gmail x2, OpenAI x2
  (plus 1 Chat Trigger, not credentialed)
retry: 0 of 13 credentialed nodes have retryOnFail — do not claim retries
isolation: single "Live write?" IF gate on $json.live; demo code nodes set
  live: false
error workflow node: none
mechanisms to document: owner-approved write-back (proposals land in the
  FAQ-Pending tab, never auto-published), miss logging, weekly gap clustering,
  duplicate detection, deterministic demo verdict mirroring the AI contract,
  lead detection as a first-class route
existing evidence: container pilot — digest exactly 1 item, 6 happy-path
  items, empty-message / duplicate / bad-AI branches verified, PASS
demo fixture edge cases: hit (answered), miss (gap), duplicate, empty message,
  unparseable AI verdict (__force_bad_ai__), lead capture
```

### W4 data block — promise-ledger
```
slug: promise-ledger | 56 nodes | triggers: Manual + hourly Schedule (sweeps 08:00)
credentialed nodes: 18 — Google Sheets x10, Gmail x6, OpenAI x2
retry: 18 of 18 credentialed nodes have retryOnFail: true with maxTries: 3 —
  document this, it is a genuine strength
isolation: three $json.live gates — "Live write?", "Skip is live?",
  "Alert is live?"; demo code sets live: false
error workflow node: none
mechanisms to document: inbound-promise direction (promises made TO you),
  AI extraction with deterministic parse fallback, dedupe/message_id handling,
  approval gate ("Queue chase for approval" → Chase-Queue tab), fulfillment
  detection ("Find open row" / "Row matched?" / "Mark done in ledger"),
  per-person aging classification, digest suppression ("Digest worth sending?")
existing evidence: digest 1 item, happy path 5 items, missing-data/duplicate/
  failure alerts 3/3 PASS; live OpenAI extraction verified against a real key
demo fixture edge cases: clear commitment, newsletter (skip), missing data,
  duplicate, unparseable AI verdict (__force_bad_ai__), fulfilment reply
```

### W5 data block — client-report-generator
```
slug: client-report-generator | 87 nodes (the flagship; SETUP.md exists)
triggers: Manual ("Test workflow"), weekly Schedule (Mon 09:00), Error Trigger
  ("On workflow error"), SETUP manual ("SETUP — press play on this node once")
credentialed nodes: 15 — Google Sheets x6, Gmail x4, HTTP Request x4, OpenAI x1
retry: 15 of 15 credentialed nodes have retryOnFail: true with maxTries: 3
isolation: ten gating IFs on $json.live plus draft-mode routing; the demo
  config fixture returns live: false for four demo clients
error workflow: THIS IS THE ONLY WORKFLOW WITH ONE — "On workflow error" →
  "Operator email" → "Format error alert" → "Email owner: workflow error".
  IMPORTANT CAVEAT (verified): it is INERT as shipped. An n8n Error Trigger
  only fires when a workflow selects that workflow as its Error Workflow, and
  settings.errorWorkflow is ABSENT in all five exports. Document it as a real
  capability BUT state the required configuration step; do not imply it fires
  out of the box.
HTTP auth types to name in .env.example: Meta Ads + GA4 + Slack use Header
  Auth (genericCredentialType/httpHeaderAuth); Google Ads uses Custom Auth
  (genericCredentialType/httpCustomAuth, two headers required)
mechanisms to document: config-sheet-driven per-client toggles; three sources
  behind one adapter contract with an "Extension dock"; deterministic WoW
  deltas in Code with AI writing prose only; idempotent reports ledger keyed
  on client_id + ISO week ("Collect sent keys" / "Dedupe check" /
  "Already sent?"); delivery_mode=draft human review seam; per-source failure
  isolation ("Compose source alert" / "Extension dock"); sink-level alerts
  (Slack delivery gated on the API ok flag); one-click SETUP lane
existing evidence: container pilot with zero credentials — digest exactly 1
  item, 16 happy-path items, missing-data/duplicate/failure alerts 3/3 PASS;
  three config variants replayed with pinned deltas verified
demo fixture edge cases for examples/client-report-generator/test-data.json:
the config row shape (one row per client: src_*/sink_* flags, delivery_mode,
brand_* cells) plus one payload per source adapter (Meta Ads, Google Ads, GA4)
note: README says "Works on n8n Cloud — no env vars needed"; keep it and make
  .env.example consistent with that (credentials, not env vars)
```

---

## PROMPT P5-CI — Guardrails

**Wave 2 · write scope:** `.github/workflows/validate.yml`, `scripts/verify-all.sh` (optional new)

```
TASK: Add machine checks that keep every claim in this portfolio honest. Land
only checks that pass on the current tree.

STEPS: extend .github/workflows/validate.yml with jobs that fail on:
1. Folder contract: every n8n/*/ has workflow.json, README.md,
   assets/diagram.svg, assets/diagram.json, .env.example; every examples/*/
   has test-data.json. (Uses shell/python — do not add third-party actions
   beyond actions/checkout.)
2. Mermaid drift: run `python3 scripts/render-mermaid.py n8n/<each>` and then
   `git diff --exit-code` — fail if the committed graph is stale. This is
   currently green; confirm it stays green.
3. Sanitization residue: fail if `git grep -nE '"instanceId"|"versionId"|
   "webhookId"'` finds matches under n8n/, or if a workflow.json has a
   top-level "id" key.
4. Placeholder scan: fail on `[your-`, "your_chat_id", "TODO" anywhere in
   *.md outside docs/portfolio-upgrade-plan.md and docs/agent-prompts.md.
5. Fixture shape: every examples/*/test-data.json parses as JSON.
6. Keep the existing n8n JSON validity, secret scan and ruff steps unchanged.
7. New scripts/verify-demo-lane.py — the local substitute for an n8n instance
   while P-1/P0b touch the exports. For each workflow: walk the graph from the
   demo triggers honouring `disabled: true` and the `$json.live` gates, then
   assert (a) the demo lane reaches 0 credentialed nodes, (b) node and
   connection counts match the expected table below, (c) every workflow.json
   still parses. Expected counts: affiliate-intake 13, daily-cash-tally 20,
   faq-chatbot 40, promise-ledger 56, client-report-generator 87 nodes.
   Exit non-zero with a clear per-workflow report on failure.

Also add scripts/verify-all.sh that runs the same checks locally, so the owner
can reproduce CI in one command. Include verify-demo-lane.py in it.

VERIFY: run bash scripts/verify-all.sh; paste full output. Then prove at least
the residue and placeholder checks actually fail when violated — temporarily
introduce a violation, show the failure, revert it.

DO NOT: enable a docker-based n8n import check. The Docker daemon was
unavailable at review time; propose it in your report as a follow-up with the
exact command you would use, but do not add it.
```

---

## PROMPT R-shared — Shared READMEs consistency pass

**Wave 2 · after all W1–W5 · write scope:** `n8n/README.md`, `examples/README.md`

```
TASK: Make the shared index docs match what the per-workflow agents actually
produced. Run this only after all five workflow packages have landed.

STEPS:
1. n8n/README.md
   - Update the index table so it reflects reality per workflow: credentials
     needed, status. Keep "All five ... run their demo lanes with zero
     credentials" ONLY if still true after P0b.
   - Add the new per-folder files to the folder contract if the contract block
     is now incomplete (it already lists .env.example — verify it exists
     everywhere now).
   - Keep the import instructions; adjust step 2 if .env.example files turned
     out to be credential/service lists rather than env-var files.
2. examples/README.md
   - Replace the "Each workflow's README points at the files here it consumes"
     promise with an index of the five examples/<slug>/ folders and what each
     covers.
3. Consistency check: every relative link in both files must resolve.

VERIFY:
  python3 - <<'EOF'
  import re,os
  for doc in ['n8n/README.md','examples/README.md']:
      base=os.path.dirname(doc)
      for m in re.finditer(r'\]\(([^)#][^)]*)\)', open(doc).read()):
          t=m.group(1)
          if t.startswith('http'): continue
          p=os.path.normpath(os.path.join(base,t))
          print(('OK  ' if os.path.exists(p) else 'BROKEN'), doc, '->', t)
  EOF
Report any BROKEN line and fix it.

DO NOT: edit per-workflow READMEs or the root README.
```

---

## PROMPT P0b — Retry policy parity *(OWNER APPROVAL REQUIRED FIRST)*

**Wave 2 · write scope:** `n8n/daily-cash-tally/workflow.json`, `n8n/faq-chatbot/workflow.json`

```
TASK: Apply the retry policy that already exists in two sibling workflows to
the credentialed nodes of daily-cash-tally and faq-chatbot.

RATIONALE (verified): client-report-generator has retryOnFail:true +
maxTries:3 on 15 of 15 credentialed nodes; promise-ledger on 18 of 18;
daily-cash-tally on 0 of 9; faq-chatbot on 0 of 13. The repo's positioning
claims "observable and idempotent by default" — that asymmetry is
buyer-visible.

CONSTRAINT: this is one of only two sanctioned edits to workflow.json.
SCOPE BOUNDARY — read carefully:
- This task is RETRY PARITY ON EXISTING NODES ONLY. It is not "add error
  handling where the word error is missing".
- affiliate-intake is OUT OF SCOPE: it has no external call at all (5 Code,
  1 IF, 1 Merge, 1 Manual Trigger, 5 sticky notes), so there is nothing to
  retry, and adding any alert node would give it its first credential and
  destroy its "Zero credentials required" headline.
- Do NOT add Error Trigger nodes, alert nodes, or any new node. That is a
  separate decision (P0c) requiring explicit owner approval.
- Set "retryOnFail": true and "maxTries": 3 on existing nodes that use these
  types: n8n-nodes-base.googleSheets, n8n-nodes-base.gmail,
  n8n-nodes-base.telegram, n8n-nodes-base.openAi,
  @n8n/n8n-nodes-langchain.openAi, n8n-nodes-base.httpRequest.
- Change NOTHING else: no new nodes, no new connections, no renames, no
  onError/continueOnFail, no position or parameter changes.

VERIFY (paste output):
  python3 - <<'EOF'
  import json
  for slug,exp in [('daily-cash-tally',9),('faq-chatbot',13)]:
      d=json.load(open(f'n8n/{slug}/workflow.json'))
      cred=[n for n in d['nodes'] if n['type'] in {
        'n8n-nodes-base.googleSheets','n8n-nodes-base.gmail',
        'n8n-nodes-base.telegram','n8n-nodes-base.openAi',
        '@n8n/n8n-nodes-langchain.openAi','n8n-nodes-base.httpRequest'}]
      r=[n for n in cred if n.get('retryOnFail') and n.get('maxTries')==3]
      print(slug, f'{len(r)}/{len(cred)} retry-configured', 'expected', exp)
      print('  nodes:',len(d['nodes']))
  EOF
Node counts must stay 20 and 40. Then re-run the mermaid drift check — the
graph must be unchanged (no nodes added).

DO NOT: proceed if the owner has not approved this change. If approval was not
given, stop and report that the Reliability sections must instead state the
retry gap honestly.
```

---

## PROMPT P0c — Error-alert coverage decision memo *(OWNER DECISION, run after P0)*

```
TASK: Write docs/error-handling-decision.md — a short decision memo, not code.
Do NOT modify any workflow.json.

CONTEXT: only client-report-generator contains an Error Trigger node, and it
is inert until the owner selects a workflow as its Error Workflow in n8n
settings (settings.errorWorkflow is absent in all five exports).
affiliate-intake, daily-cash-tally, faq-chatbot and promise-ledger have no
error-alert path. Retry coverage is separate and handled by P0b.

FOR EACH of the four workflows without an error path, lay out:
1. What can actually fail at runtime (list the real failure surfaces from the
   JSON: which nodes make external calls, which can throw on bad input).
2. Option (a): follow daily-cash-tally's existing pattern — add Error Trigger
   + alert node shipped `disabled: true`, so the zero-credential demo lane is
   preserved. State the exact node cost and that it is a build requiring n8n
   re-verification.
3. Option (b): n8n native Error Workflow via settings.errorWorkflow — state
   why it conflicts with P-1 sanitization (stores a workflow id reference) and
   cannot be verified from the repo.
4. Option (c): document the gap honestly (errors visible in n8n's execution
   list; no alert configured).
5. A recommendation per workflow with the reasoning. For affiliate-intake,
   weigh that adding any alert node introduces its first credential and breaks
   its "Zero credentials required" positioning.

OUTPUT: a table (workflow × option × cost × recommendation) plus one
paragraph per workflow. End with the exact questions the owner must answer.
```

---

## PROMPT P3-root — Root README sells outcomes

**Wave 3 · after wave 2 · write scope:** `README.md`

```
TASK: Turn the root README into an outcomes-first landing page.

STEPS:
1. Featured table: add a "Result" column. Fill it ONLY with
   (a) repo-verifiable evidence from the workflow READMEs / plan Appendix A
   (item counts, branch coverage, PASS results, gate/retry coverage), or
   (b) owner-supplied business metrics if the owner has provided them by now.
   Anything unavailable gets `<!-- owner-metric -->`, not a guess.
2. Add a one-line sanitization statement (only true once P-1 has landed).
3. Add a skills/differentiators strip: platforms, APIs, and the differentiators
   (human-in-the-loop, idempotency, quarantine lanes, per-source failure
   isolation, zero-credential demo lanes).
4. Replace the four `[your-...]` CTA placeholders with the owner's real links
   if supplied; if not supplied, leave them and report them clearly as the
   only blocker to publishing.
5. Keep Services / How I work / Repository structure consistent with what now
   exists (no folder listed that is empty without a "coming soon" note, and no
   folder missing from the table).

VERIFY: list every placeholder still present in the file, and list every
numeric claim with its source file.

DO NOT: invent metrics, edit per-workflow READMEs, or publish a sanitization
sentence before P-1 is merged.
```

---

## PROMPT P3b-meta — GitHub repo metadata *(owner-gated: writes to the public repo)*

```
TASK: Align the GitHub repo metadata with the positioning.

CURRENT: description says "Production-ready automation workflows: n8n
templates, Zapier zaps, ..." — the word "templates" contradicts the chosen
positioning (production systems, not template dumps).

PROPOSE (do not execute until the owner confirms):
- a new description (one sentence, outcome-oriented, no "templates")
- topics: keep n8n, n8n-workflows, automation, portfolio; consider adding
  error-handling / self-hosted / integration; drop terms that suggest a
  template marketplace if any
- a social preview image built from docs/visual-style.md

PRESENT the exact `gh repo edit` command you would run and wait for approval.
Note: the `gh` CLI is authenticated as lethevinh on this machine, and this
writes to a PUBLIC repo.
```

---

## PROMPT P4-case — Flagship case study *(owner-gated: needs client context)*

```
TASK: Draft docs/case-studies/client-report-generator.md — the
proposal-attachment asset — using docs/case-studies/README.md as the template
(Context → Problem → What I built → Results → What I'd do differently).

Use only: the workflow README, SETUP.md, workflow.json, and any client context
the owner supplies. Every number must be either repo-verifiable evidence or
explicitly quoted from the owner.

Leave `<!-- owner-input: ... -->` placeholders for: client domain and size,
the process before automation (time/cost), pilot scope, and any business
result. Do not invent an anecdote, a client name, or a percentage.
```

---

## PROMPT P6-visual — Screenshot shot list + Loom script *(owner-assisted)*

```
TASK: Produce docs/visual-proof-guide.md containing, per workflow:
1. A shot list: which n8n screen to capture (e.g. a successful Test workflow
   run showing every branch, the quarantine tab, the approval queue), what to
   annotate, and the exact redaction rules — no account IDs, no client emails,
   no spreadsheet IDs, no instance URLs.
2. A 2–3 minute Loom script for client-report-generator: what to say while
   showing import → test run → config sheet → draft-review seam → error path.
3. The target filenames (n8n/<slug>/assets/execution.png) and the note that
   assets are added by the owner, not generated.

Keep it executable by a non-technical owner: numbered steps, no jargon.
```

---

## PROMPT P7-dist — Distribution plan *(owner-gated: publishes publicly)*

```
TASK: Produce docs/distribution-plan.md — a ready-to-execute launch plan so
the polished repo actually reaches buyers.

Required sections:
1. Channels, each with exact copy and links: n8n community template gallery
   submission (per workflow), awesome-n8n / awesome-automation PR entries,
   Reddit r/n8n, LinkedIn, Upwork portfolio entry, dev.to or a short blog post.
2. For each channel: the draft text, the target URL, the asset to attach
   (diagram.svg / screenshot), and the owner action needed.
3. UTM-tagged links back to the repo so the owner can see what converts.
4. A 2-week schedule with one action per day.
5. A redaction checklist to run before any public post: no instance IDs, no
   client names, no real emails, no sheet IDs.

Rules: no fake engagement claims, no "as seen in" statements, do not post
anything — this is copy the owner reviews and sends.
```
