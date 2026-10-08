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
Wave 2 (parallel): `PROMPT P5-CI`, `PROMPT R-shared`
Wave 2b (parallel, dispatch now): `PROMPT P0b` (approved), `PROMPT P-1c`, `PROMPT P-1d` (dry-run only)
Wave 3: `PROMPT P3-root`, then `PROMPT P0c` (decision memo, after P0 has landed)
Wave 4 (owner-gated): `PROMPT P3b-meta`, `PROMPT P4-case`, `PROMPT P6-visual`, `PROMPT P7-dist`

**No agent runs `git commit` or `git push`.** The orchestrator commits per
package so parallel agents cannot race on the index; the only force-push in
the whole plan is the history rewrite, and it stays blocked until the owner
authorises it in writing.

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

## PROMPT P0b — Retry parity + README truth-up *(APPROVED by owner 2026-10-09)*

> **Superseded by `PROMPT ALL-IN-ONE` at the end of this file.** Keep this
> block for reference only — dispatch the consolidated prompt instead.

**Wave 2 · write scope:** `n8n/daily-cash-tally/workflow.json`,
`n8n/faq-chatbot/workflow.json`, `n8n/daily-cash-tally/README.md`,
`n8n/faq-chatbot/README.md`

```
TASK: Two parts. Part 1 applies the retry policy that already exists in two
sibling workflows. Part 2 is mandatory: the READMEs currently state the
opposite of what part 1 makes true, and must be updated in the same commit.

PART 1 — retry flags (JSON)
RATIONALE (verified): client-report-generator has retryOnFail:true,
maxTries:3, waitBetweenTries:1500 on 15 of 15 credentialed nodes;
promise-ledger on 18 of 18; daily-cash-tally on 0 of 9; faq-chatbot on 0 of
13. The repo claims "observable and idempotent by default" — that asymmetry
is buyer-visible.

SCOPE BOUNDARY — read carefully:
- RETRY PARITY ON EXISTING NODES ONLY. It is not "add error handling where
  the word error is missing".
- affiliate-intake is OUT OF SCOPE: no external call exists (5 Code, 1 IF,
  1 Merge, 1 Manual Trigger, 5 sticky notes), so there is nothing to retry,
  and adding any alert node would give it its first credential and destroy
  its "Zero credentials required" headline.
- Do NOT add Error Trigger nodes, alert nodes, or any new node. That is a
  separate decision (P0c), still only a memo.
- Set EXACTLY this triple on existing nodes of these types —
  n8n-nodes-base.googleSheets, n8n-nodes-base.gmail,
  n8n-nodes-base.telegram, n8n-nodes-base.openAi,
  @n8n/n8n-nodes-langchain.openAi, n8n-nodes-base.httpRequest:
      "retryOnFail": true, "maxTries": 3, "waitBetweenTries": 1500
  All three fields, to match the sibling convention exactly.
- Change NOTHING else: no new nodes, no new connections, no renames, no
  onError/continueOnFail edits, no position or parameter changes.

PART 2 — README truth-up (mandatory, same commit)
Both target READMEs currently document the retry gap explicitly:
  - n8n/daily-cash-tally/README.md — "No retries, no error workflow — stated
    plainly" (~line 179)
  - n8n/faq-chatbot/README.md — "No retries." and "No error workflow."
    (~lines 248-251)
Rewrite ONLY the retry half to the new truth (9/9 and 13/13, naming
retryOnFail/maxTries:3/waitBetweenTries:1500). KEEP the "no error workflow"
half exactly as-is — it is still true; P0c is a memo, not a change.
Then add one retry-coverage row to each README's evidence table, in the same
shape promise-ledger already uses, e.g.
  | Retry coverage: 13/13 credentialed nodes (`retryOnFail`, `maxTries: 3`) | `workflow.json` |
Do NOT overstate: retries absorb transient failures only; they do not alert
on persistent ones.

VERIFY (paste output):
  python3 - <<'EOF'
  import json
  TYPES={'n8n-nodes-base.googleSheets','n8n-nodes-base.gmail',
   'n8n-nodes-base.telegram','n8n-nodes-base.openAi',
   '@n8n/n8n-nodes-langchain.openAi','n8n-nodes-base.httpRequest'}
  for slug,exp in [('daily-cash-tally',9),('faq-chatbot',13)]:
      d=json.load(open(f'n8n/{slug}/workflow.json'))
      cred=[n for n in d['nodes'] if n['type'] in TYPES]
      r=[n for n in cred if n.get('retryOnFail') is True
         and n.get('maxTries')==3 and n.get('waitBetweenTries')==1500]
      print(slug, f'{len(r)}/{len(cred)} retry-configured (expected {exp})',
            'nodes:',len(d['nodes']))
  EOF
Node counts must stay 20 and 40. Then run `bash scripts/verify-all.sh` — the
mermaid graph must be unchanged (no nodes added) and the demo lane must still
reach 0 credentialed nodes.

DO NOT: touch docs/error-handling-decision.md — it was re-read and is
accurate (it already says the unwired error branch "drops silently" AND
"self-heals transient faults", and it names the 8 continueRegularOutput
nodes correctly). Do not "fix" it.
```

---

## PROMPT P-1c — Commit the redaction + close the secret-scan hole *(dispatch now)*

> **Superseded by `PROMPT ALL-IN-ONE` at the end of this file.**

**Wave 2 · write scope:** `docs/portfolio-upgrade-plan.md`,
`.github/workflows/validate.yml`, `scripts/verify-all.sh`

```
TASK: Three small hygiene items left over from P-1.

1. The plan doc was leaking the identifier it warns about.
   docs/portfolio-upgrade-plan.md §4 previously quoted the FULL n8n instanceId
   verbatim. That has already been redacted in the working tree to
   `<redacted>` plus a "do not paste the full value" note. VERIFY this
   (do not re-derive the value, do not type it):
     grep -rnE '[0-9a-f]{8}.{1,2}[0-9a-f]{6}' --include='*.md' .    # must print nothing
   If it prints anything, redact it the same way.

2. Close the secret-scan hole. .github/workflows/validate.yml runs the secret
   scan with `--exclude='.env.example'`, and wave 1 added 5 more
   .env.example files. A real key pasted into one of them would sail through.
   Removing the exclusion has already been tested as SAFE on the current tree
   (the placeholder values `sk-...`, `xoxb-...`, `your-n8n-instance…` do not
   match the regex, which needs 20+ real characters). Remove the exclusion in
   BOTH .github/workflows/validate.yml and scripts/verify-all.sh.
   Keep the regex itself unchanged.

3. Update the plan's stale status. docs/portfolio-upgrade-plan.md still says
   "Status: ready for owner sign-off — not yet executed", which is now false:
   waves 0-3 have landed. Set an accurate status line and append a short
   "## 11. Decision log" section recording, factually:
     - P-1, P-1b, W1-W5, P5-CI, R-shared, P3, P0c memo: DONE (local commits,
       not pushed)
     - P0b: APPROVED by owner 2026-10-09 — retry flags on existing nodes only
     - history rewrite: option A chosen; force-push NOT yet authorised
     - owner-metric placeholders (12) and hire-me CTA links: still pending
       owner input
   Do not restate any identifier value anywhere.

VERIFY (paste output):
  grep -rnE '[0-9a-f]{8}.{1,2}[0-9a-f]{6}' --include='*.md' . || echo "redaction: clean"
  bash scripts/verify-all.sh 2>&1 | tail -5      # must stay all-pass
  grep -n 'exclude=.env.example' .github/workflows/validate.yml scripts/verify-all.sh || echo "scan scope: .env.example now included"

DO NOT: run `git commit`, `git push`, or any history rewrite — the
orchestrator commits per package. Do not edit the P0c memo (it is accurate)
or any file outside the write scope.
```

---

## PROMPT P-1d — History rewrite runbook *(dry-run only; force-push is HARD-GATED)*

> **Superseded by `PROMPT ALL-IN-ONE` at the end of this file.**

**Wave 2 · write scope:** `docs/history-rewrite-runbook.md` (new)

```
TASK: Write docs/history-rewrite-runbook.md: an executable, owner-reviewable
runbook for removing the leaked n8n instanceId from public git history
(option A). You may run the DRY-RUN verification steps. You must NOT execute
the rewrite or the force-push.

CRITICAL RULE: the runbook document must NOT contain the leaked value. Refer
to it as `<leaked-instance-id>`, and extract it at runtime from history into a
path OUTSIDE the repo. Never write it into a tracked file — that is exactly
how it got re-published once already.

VERIFIED FACTS to build on:
- `git filter-repo` is NOT installed on this machine (git reports
  'filter-repo' is not a git command; the Python module is absent);
  Homebrew is available at /opt/homebrew/bin/brew.
- The value exists in history at commits c81a929 (added to 4 workflow.json),
  e70fb04 era strip commit, and e916120 (adding it to the plan doc).
- origin/main is 11+ commits behind HEAD; nothing local is pushed yet.
- Repo has 0 stars / 0 forks (verify again with `gh api`), so a force-push
  breaks no one.

RUNBOOK MUST COVER, in order:
1. Preconditions: working tree clean, all packages committed, `gh api
   repos/lethevinh/automation-workflows` showing forks_count == 0.
2. Backup: `git clone --mirror` to a dated path outside the repo
   (~/backups/automation-workflows-YYYY-MM-DD.git) and state how to restore.
3. Install: `brew install git-filter-repo`.
4. Extract the value at runtime into /tmp (never into the repo), e.g. via
   `git grep -h '"instanceId"' c81a929 -- n8n/ | sed ...` into
   /tmp/replacements.txt, in filter-repo `--replace-text` format.
5. The rewrite command itself, including `--replace-text /tmp/replacements.txt
   --force`.
6. GOTCHA: git-filter-repo REMOVES the `origin` remote — re-add it before any
   push, or the push fails confusingly.
7. Post-rewrite verification: `git log --all -S '<value>'` returns nothing;
   `bash scripts/verify-all.sh` still all-pass; `git show HEAD --stat` shows
   file contents otherwise unchanged.
8. HARD GATE: stop here. Print the exact push command
   (`git push --force-with-lease origin main`) but do not run it. The runbook
   must state that the owner has to authorise the force-push explicitly and in
   writing.
9. Post-push caveats, stated honestly: earlier clones/forks keep the value;
   GitHub may retain dangling objects and cached views, so open a GitHub
   Support request to purge them; assume the value is compromised either way.

VERIFY (paste output): the dry-run checks you actually ran, and a grep proving
the new runbook contains no 64-hex identifier:
  grep -nE '[0-9a-f]{32,}' docs/history-rewrite-runbook.md || echo "runbook: no identifier leaked"

DO NOT: run git-filter-repo, git filter-branch, git push, or any command that
rewrites history. Do not commit.
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

---

# PROMPT ALL-IN-ONE — toàn bộ việc còn lại, chạy tuần tự trong 1 agent

> Paste the **SHARED PREAMBLE** above first, then this whole block.
> Supersedes `PROMPT P0b`, `PROMPT P-1c`, `PROMPT P-1d`.
> One agent, sequential. Do not parallelise inside this prompt.

```
MISSION
Finish every remaining executable item of docs/portfolio-upgrade-plan.md in one
sequential run: the approved retry change, the leftover P-1 hygiene, the
history-rewrite runbook (dry-run only), and the Wave-4 draft documents.
Owner-only inputs (real metrics, contact links, force-push authorisation) are
NOT yours to invent — leave placeholders and report them.

BINDING RULES
1. Never invent facts: no client names, testimonials, percentages, dollar
   figures, or "roughly" numbers. Missing data becomes an explicit
   `<!-- owner-metric: ... -->` or `<!-- owner-input: ... -->` placeholder.
2. Never write the leaked n8n instance identifier anywhere. Do not type it, do
   not paste it from history into any tracked file. Detect it only by pattern:
       grep -rnE '\b[0-9a-f]{64}\b' docs/ *.md 2>/dev/null
   If you need the value (only for the runbook's runtime extraction step),
   pipe it from git straight into /tmp — never into the repo.
3. Do NOT run `git commit`, `git push`, `git filter-repo`, `git filter-branch`,
   or `gh repo edit`. The orchestrator commits per package; the force-push is
   a separate owner-authorised action.
4. Stay strictly inside the WRITE SCOPE below. Do not reformat or "tidy"
   anything else. `docs/error-handling-decision.md` is accurate — do not edit
   it.
5. English, conventional commits wording in your report, no bot co-author.

WRITE SCOPE (nothing outside this list)
  n8n/daily-cash-tally/workflow.json
  n8n/daily-cash-tally/README.md
  n8n/faq-chatbot/workflow.json
  n8n/faq-chatbot/README.md
  docs/portfolio-upgrade-plan.md
  .github/workflows/validate.yml
  scripts/verify-all.sh
  docs/history-rewrite-runbook.md            (new)
  docs/visual-proof-guide.md                 (new)
  docs/distribution-plan.md                  (new)
  docs/case-studies/client-report-generator.md (new)

═══════════════════════════════════════════════════════════════════
PART A — P0b: retry parity + README truth-up  (APPROVED by owner 2026-10-09)
═══════════════════════════════════════════════════════════════════
A1. JSON flags. Set EXACTLY this triple on the existing nodes of these types
    in n8n/daily-cash-tally/workflow.json and n8n/faq-chatbot/workflow.json:
        "retryOnFail": true, "maxTries": 3, "waitBetweenTries": 1500
    Node types in scope: n8n-nodes-base.googleSheets, n8n-nodes-base.gmail,
    n8n-nodes-base.telegram, n8n-nodes-base.openAi,
    @n8n/n8n-nodes-langchain.openAi, n8n-nodes-base.httpRequest.
    Expected: daily-cash-tally 9/9, faq-chatbot 13/13.
    RATIONALE: the two sibling workflows already do this — client-report-generator
    15/15, promise-ledger 18/18 — so today the repo's "observable and idempotent
    by default" claim is asymmetric.
A2. Change NOTHING else in those files: no new nodes, no new connections, no
    renames, no onError/continueOnFail edits, no position/parameter changes.
    Node counts must stay 20 and 40.
A3. SCOPE BOUNDARY: affiliate-intake is OUT OF SCOPE. It has no external call
    at all (5 Code, 1 IF, 1 Merge, 1 Manual Trigger, 5 sticky notes), nothing
    to retry, and adding an alert node would give it its first credential and
    destroy its "Zero credentials required" headline. Do NOT add Error Trigger
    nodes or alert nodes anywhere — that is P0c, still only a memo.
A4. README truth-up — MANDATORY in the same run, because Part A makes both
    READMEs false. Locate by text, not by line number:
      - daily-cash-tally/README.md: "No retries, no error workflow — stated
        plainly" (~line 179)
      - faq-chatbot/README.md: "No retries." and "No error workflow."
        (~lines 248-251)
    Rewrite ONLY the retry half to the new truth (9/9 and 13/13, naming
    retryOnFail / maxTries:3 / waitBetweenTries:1500). KEEP the "no error
    workflow" half exactly as it is — still true. Do not overstate: retries
    absorb transient failures only; they never alert on persistent ones.
A5. Add one retry-coverage row to each README's evidence table, in the shape
    promise-ledger already uses:
      | Retry coverage: 13/13 credentialed nodes (`retryOnFail`, `maxTries: 3`) | `workflow.json` |
A6. VERIFY and paste output:
      python3 - <<'EOF'
      import json
      TYPES={'n8n-nodes-base.googleSheets','n8n-nodes-base.gmail',
       'n8n-nodes-base.telegram','n8n-nodes-base.openAi',
       '@n8n/n8n-nodes-langchain.openAi','n8n-nodes-base.httpRequest'}
      for slug,exp in [('daily-cash-tally',9),('faq-chatbot',13)]:
          d=json.load(open(f'n8n/{slug}/workflow.json'))
          cred=[n for n in d['nodes'] if n['type'] in TYPES]
          r=[n for n in cred if n.get('retryOnFail') is True
             and n.get('maxTries')==3 and n.get('waitBetweenTries')==1500]
          print(slug, f'{len(r)}/{len(cred)} (expected {exp})','nodes:',len(d['nodes']))
      EOF

═══════════════════════════════════════════════════════════════════
PART B — verify the leaked identifier is gone from the working tree
═══════════════════════════════════════════════════════════════════
B1. §4 of docs/portfolio-upgrade-plan.md used to quote the full 64-hex n8n
    instanceId. It has already been redacted to `<redacted>` plus a
    "do not paste the full value" note. VERIFY:
        grep -rnE '\b[0-9a-f]{64}\b' docs/ *.md 2>/dev/null || echo "clean"
    Must print nothing (or "clean"). If any 64-hex identifier appears in a
    tracked doc, redact it the same way. Do not re-derive the value.

═══════════════════════════════════════════════════════════════════
PART C — close the secret-scan hole
═══════════════════════════════════════════════════════════════════
C1. .github/workflows/validate.yml runs the secret scan with
    `--exclude='.env.example'`, and wave 1 added 5 more .env.example files, so
    a real key pasted into one would pass undetected. Removing that exclusion
    has ALREADY BEEN TESTED SAFE on the current tree: the placeholder values
    (`sk-...`, `xoxb-...`, `your-n8n-instance…`) do not match the regex, which
    requires 20+ real characters. Remove the exclusion in BOTH
    .github/workflows/validate.yml and scripts/verify-all.sh. Leave the regex
    itself unchanged.
C2. VERIFY: grep for the exclusion string in both files; expect no match.

═══════════════════════════════════════════════════════════════════
PART D — plan status + decision log
═══════════════════════════════════════════════════════════════════
D1. docs/portfolio-upgrade-plan.md still says "Status: ready for owner
    sign-off — not yet executed", now false (waves 0-3 landed). Replace with an
    accurate status line, and append a "## 11. Decision log" section recording
    factually:
      - DONE, committed locally: P-1, P-1b, W1-W5, P5-CI, R-shared, P3,
        P0c memo; not pushed
      - P0b: APPROVED by owner 2026-10-09 — retry flags on existing nodes only
      - history rewrite: option A chosen; force-push NOT yet authorised
      - pending owner input: 12 owner-metric placeholders, 4 hire-me CTA links
D2. Do not restate any identifier value anywhere. Keep the existing §0
    corrections table intact.

═══════════════════════════════════════════════════════════════════
PART E — history-rewrite runbook (DRY RUN ONLY)
═══════════════════════════════════════════════════════════════════
E1. Write docs/history-rewrite-runbook.md: an executable, owner-reviewable
    runbook for removing the leaked identifier from public git history
    (option A). You may run the read-only verification steps. You must NOT run
    the rewrite or the push.
E2. CRITICAL: the runbook itself must not contain the value. Refer to it as
    `<leaked-instance-id>` and extract it at runtime from git history straight
    into /tmp (e.g. `git grep -h '"instanceId"' c81a929 -- n8n/ | sed ...` into
    /tmp/replacements.txt). Never write it into a tracked file — that is how it
    got re-published once already.
E3. VERIFIED FACTS to build on:
      - `git filter-repo` is NOT installed (git reports 'filter-repo' is not a
        git command; the Python module is absent). Homebrew is at
        /opt/homebrew/bin/brew.
      - The value exists in history at c81a929 (4 workflow.json), the strip
        commit that removed it, and e916120 (the plan doc).
      - origin/main is ~11 commits behind HEAD; nothing local is pushed.
      - The repo has 0 stars / 0 forks — re-verify with
        `gh api repos/lethevinh/automation-workflows` before asserting it.
E4. Runbook must cover, in order:
      1. Preconditions: clean tree, all packages committed, forks_count == 0.
      2. Backup: `git clone --mirror` to a dated path OUTSIDE the repo
         (~/backups/automation-workflows-YYYY-MM-DD.git) + restore steps.
      3. `brew install git-filter-repo`.
      4. Runtime extraction of the value into /tmp/replacements.txt in
         filter-repo `--replace-text` format.
      5. The rewrite command, including `--replace-text /tmp/replacements.txt
         --force`.
      6. GOTCHA: git-filter-repo REMOVES the `origin` remote — re-add it before
         any push or the push fails confusingly.
      7. Post-rewrite verification: `git log --all -S '<value>'` empty;
         `bash scripts/verify-all.sh` still all-pass; `git show HEAD --stat`
         shows nothing else changed.
      8. HARD GATE: print `git push --force-with-lease origin main` but do not
         run it; state that the owner must authorise the force-push in writing.
      9. Honest post-push caveats: earlier clones keep the value; GitHub may
         retain dangling objects/cached views (open a Support request to purge);
         assume the value is compromised regardless.
E5. VERIFY and paste:
      grep -nE '[0-9a-f]{32,}' docs/history-rewrite-runbook.md || echo "runbook: no identifier leaked"

═══════════════════════════════════════════════════════════════════
PART F — Wave-4 draft documents (drafts only; publish nothing)
═══════════════════════════════════════════════════════════════════
F1. docs/visual-proof-guide.md — per workflow: which n8n screen to capture
    (a Test run showing every branch, the quarantine tab, the approval queue),
    what to annotate, exact redaction rules (no account IDs, client emails,
    spreadsheet IDs, instance URLs), target filename
    n8n/<slug>/assets/execution.png, and a note that the owner adds the assets.
    Plus a 2-3 minute Loom script for client-report-generator: import → test
    run → config sheet → draft-review seam → error path. Numbered steps, no
    jargon.
F2. docs/distribution-plan.md — channels with exact draft copy, target URL,
    asset to attach, and the owner action for each: n8n community template
    gallery, awesome-n8n PR, Reddit r/n8n, LinkedIn, Upwork portfolio entry,
    one short blog post. UTM-tagged links back to the repo. A 2-week schedule,
    one action per day. A pre-post redaction checklist. No fake engagement
    claims; post nothing.
F3. docs/case-studies/client-report-generator.md — skeleton following
    docs/case-studies/README.md (Context → Problem → What I built → Results →
    What I'd do differently). Fill only what the repo supports: 87 nodes, three
    source adapters behind one contract, idempotent ledger keyed on
    client_id + ISO week, delivery_mode=draft review seam, per-source failure
    isolation, the Error Trigger lane (note it is inert until selected as the
    Error Workflow in n8n settings). Leave `<!-- owner-input: ... -->` for
    client domain/size, before-state cost, pilot scope and business result.
    Invent nothing.

═══════════════════════════════════════════════════════════════════
PART G — repo metadata proposal (propose only, do not execute)
═══════════════════════════════════════════════════════════════════
G1. The GitHub description currently says "n8n templates…", which contradicts
    the chosen positioning (production systems, not template dumps). In your
    REPORT (not in a file), propose a replacement description, a topic list,
    and the exact `gh repo edit` command. Do not run it — it writes to a public
    repo and needs explicit approval.

═══════════════════════════════════════════════════════════════════
PART H — final verification
═══════════════════════════════════════════════════════════════════
H1. Run `bash scripts/verify-all.sh` and paste the full tail. It must end
    "RESULT: all checks passed", with demo lanes still reaching 0 credentialed
    nodes and node counts 13/87/20/40/56.
H2. Report, in this order:
      - per part A-H: status, files touched, the verify command and its output
      - anything you had to leave as a placeholder, and why
      - any contradiction you found between the plan and the repo
      - the Part G proposal
      - an explicit statement that you did not commit, push, or rewrite history

HARD GATES — stop and report instead of proceeding if:
  - a Part A change would require adding or removing a node
  - a file in the write scope has diverged from what this prompt describes
  - you cannot complete a part without inventing a fact
  - any instruction would require git commit/push/filter-repo/gh repo edit
```

---

# PROMPT PUSH — backup, scrub, force-push, verify  ⚠️ IRREVERSIBLE

> **This prompt INCLUDES the force-push.** If the owner wants to stop at the
> gate, delete Step 6 and end after Step 5. Everything before Step 6 is
> reversible; Step 6 rewrites public GitHub history.
>
> Paste the **SHARED PREAMBLE** first, then this block.

```
MISSION
Publish the rewritten history: replace the public `main` with the clean chain
that no longer contains the leaked n8n instanceId. Nothing is pushed yet —
everything is local, so this is the only irreversible step in the project.

CONTEXT (verified by the Lead, 2026-10-09)
- refs/heads/main = 17 commits, rewritten by git filter-repo (SHAs differ from
  the public ones). Scan of every commit on this branch for
  `"instanceId": "<64-hex>"` returns NOTHING. This is the branch to publish.
- refs/backup/main = 2e0d130 = the pre-rewrite tip. It deliberately keeps the
  old chain (including the leaked value). Local only — never push it.
- Mirror: ~/backups/automation-workflows-2026-10-09.git (pre-rewrite, 17 commits).
- `origin` is re-added, but there is NO refs/remotes/origin/main, so
  `--force-with-lease` FAILS right now with `! [rejected] (stale info)`.
  This is expected and safe; Step 4 fixes it.
- /tmp/replacements.txt holds the raw value in plaintext and must not survive.
- 5 lines in tracked docs still carry a FRAGMENT of the identifier and would be
  published by this push (Step 1 removes them).

HARD RULES
- Only `--force-with-lease`. NEVER bare `--force`, and never `--mirror`,
  `--all` or `--tags`.
- Push `main` and nothing else. Never push refs/backup/* or backup/pre-push-*.
- Never delete, move or rewrite any backup in this run.
- Never write the identifier — or any fragment of it — into any file, including
  the SHA record file and your report.
- Do not run `gh repo edit` unless the dispatch message explicitly approves it.

═══════════════════ STEP 0 — BACKUPS FIRST (do this before anything) ═══════════
cd /Users/le/Projects/automation-workflows
DATE=$(date +%Y-%m-%d)

# 0a. record every SHA you may need, in a file OUTSIDE the repo, with no secrets
mkdir -p ~/backups
{
  echo "local main (rewritten, to push): $(git rev-parse refs/heads/main)"
  echo "refs/backup/main (pre-rewrite tip): $(git rev-parse refs/backup/main)"
  echo "public tip (before push): $(git rev-parse refs/remotes/origin/main 2>/dev/null || echo '<run git fetch first>')"
  echo "mirror pre-rewrite: ~/backups/automation-workflows-2026-10-09.git"
} > ~/backups/automation-workflows-shas-$DATE.txt
cat ~/backups/automation-workflows-shas-$DATE.txt

# 0b. prove the pre-rewrite mirror is intact — this is the real rollback
git --git-dir=$HOME/backups/automation-workflows-2026-10-09.git log --oneline | wc -l
# expect: 17

# 0c. a SECOND independent copy of the pre-rewrite state
git clone --quiet --mirror ~/backups/automation-workflows-2026-10-09.git \
  ~/backups/automation-workflows-prerewrite-copy-$DATE.git && echo "0c ok"

# 0d. mirror the CURRENT (rewritten) state, so both sides exist on disk
git clone --quiet --mirror . ~/backups/automation-workflows-postrewrite-$DATE.git && echo "0d ok"

# 0e. a local branch pointing at exactly what you are about to push
git branch backup/pre-push-$DATE refs/heads/main
git branch --list 'backup/*'
git for-each-ref --format='%(refname) %(objectname:short)' | grep -E 'backup|heads/main'

STOP if any of 0b–0e fails. Do not continue without backups.

═══════════════════ STEP 1 — scrub identifier fragments from published docs ═══
The fragment is 8 hex + a connector + 6 hex. Locate it WITHOUT typing it:
    grep -rnE '[0-9a-f]{8}.{1,2}[0-9a-f]{6}' --include='*.md' .
Expect exactly 5 lines in 2 files: docs/portfolio-upgrade-plan.md (1 line) and
docs/agent-prompts.md (4 lines).
Replace every occurrence with `<redacted>`. For the two lines that are grep
COMMANDS inside the superseded P-1c prompt, rewrite the command to use the
pattern above instead of a literal.
Re-run the locator: it must return 0 lines.

═══════════════════ STEP 2 — commit ═══════════════════════════════════════════
docs/history-rewrite-runbook.md also carries uncommitted Lead fixes.
    git add -A docs/
    git commit -m "docs: correct post-rewrite verification steps; redact identifier fragments"
    git status --short          # expect: empty

═══════════════════ STEP 3 — verify the branch you are about to publish ════════
    bash scripts/verify-all.sh                       # expect: all checks passed
    git rev-list refs/heads/main | while read c; do
      git grep -l -E '"instanceId": *"[0-9a-f]{64}"' "$c" -- 2>/dev/null
    done | sort -u                                   # expect: nothing
    git rev-list --count refs/heads/main

═══════════════════ STEP 4 — fetch and establish the lease ═══════════════════
    git fetch origin
    git rev-parse refs/remotes/origin/main           # record it in the SHA file
    git merge-base --is-ancestor refs/remotes/origin/main refs/backup/main \
      && echo "remote is at the known pre-rewrite history"
If the ancestry check fails, the remote has moved since the rewrite — STOP and
report; do not force anything.

═══════════════════ STEP 5 — dry run (reversible) ═════════════════════════════
    git push --force-with-lease --dry-run origin main
Must report a forced update of main with NO rejection. If you see
`stale info` or `[rejected]`, STOP and report the exact output.

═══════════════════ STEP 6 — PUSH  ⚠️ THE IRREVERSIBLE STEP ═══════════════════
    git push --force-with-lease origin main
Capture the full output. Expected shape: `+ <old>...<new> main -> main (forced update)`.

═══════════════════ STEP 7 — verify what the world actually sees ══════════════
    git ls-remote origin main
    # must equal: git rev-parse refs/heads/main

    rm -rf /tmp/verify-public
    git clone --quiet https://github.com/lethevinh/automation-workflows.git /tmp/verify-public
    cd /tmp/verify-public
    git log --oneline | head -3
    git rev-list --all | while read c; do
      git grep -l -E '"instanceId": *"[0-9a-f]{64}"' "$c" -- 2>/dev/null
    done | sort -u                                   # expect: nothing
    grep -rnE '[0-9a-f]{8}.{1,2}[0-9a-f]{6}' --include='*.md' . \
      || echo "published docs: no fragment"
    bash scripts/verify-all.sh                       # expect: all checks passed
Every line must be clean. If any check fails, go to Step 8, do not "fix forward".

═══════════════════ STEP 8 — rollback reference (run only if Step 7 fails) ═════
    # restore the previous public state — WARNING: this re-publishes the leak
    git push --force origin <OLD_PUBLIC_SHA>:refs/heads/main
    # restore the local repo to the pre-rewrite tip
    git reset --hard refs/backup/main
    # total local restore from the mirror
    git clone ~/backups/automation-workflows-2026-10-09.git automation-workflows-restored

═══════════════════ STEP 9 — cleanup and report ══════════════════════════════
    shred -u /tmp/replacements.txt 2>/dev/null || rm -f /tmp/replacements.txt

KEEP, do not delete: refs/backup/main, backup/pre-push-<DATE>, both mirrors in
~/backups/, and the SHA record file. The owner explicitly wants these retained.

REPORT
  - SHAs: local main before/after, remote main before/after
  - full push output (Step 6)
  - Step 7 results verbatim, including the fresh-clone scan
  - every backup location created in Step 0
  - open items: the local mirrors still hold the value by design; GitHub may
    retain dangling objects and cached views (Support request to purge);
    recommend rotating the n8n instance identity
  - an explicit statement of whether Step 6 ran
```
