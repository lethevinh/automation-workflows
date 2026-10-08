# History rewrite runbook — remove the leaked n8n instanceId

**Purpose:** erase the 64-hex n8n `instanceId` (referred to below as
`<leaked-instance-id>`) from the public git history of this repository —
plan §4 option A.

**Status:** prepared, dry-run verified. The rewrite and the force-push are
**owner-authorised actions** — do not run them unattended.

**Where the value lives (verified 2026-10-09):**

- `c81a929` — pushed to `origin/main`: `meta.instanceId` inside
  `n8n/{affiliate-intake,daily-cash-tally,faq-chatbot,promise-ledger}/workflow.json`
- `e916120` — **local only** (unpushed): quoted verbatim in
  `docs/portfolio-upgrade-plan.md` (the working-tree file has since been
  redacted; the committed version still embeds it)
- 12 per-node `webhookId`s were also stripped in the same pass — they are
  rotated on re-export and are not part of this rewrite target. Add them to
  the replacements file too if you want them scrubbed (see step 4).

**Never write the value into a tracked file.** That is how it was
re-published once already — extract it from git into `/tmp` at runtime.

---

## 1. Preconditions

```bash
cd /Users/le/Projects/automation-workflows
git status --short            # must be empty — everything committed
git fetch origin
gh api repos/lethevinh/automation-workflows \
  --jq '{stars:.stargazers_count,forks:.forks_count,watchers:.subscribers_count}'
# expect {"stars":0,"forks":0,"watchers":0} — safe window for a force-push
```

Stop if the tree is dirty, or if forks/stars have appeared — re-evaluate
option A vs B in that case.

## 2. Backup first

```bash
git clone --mirror . ~/backups/automation-workflows-$(date +%Y-%m-%d).git
```

Restore path if anything goes wrong: delete the corrupted checkout, then
`git clone ~/backups/automation-workflows-<date>.git automation-workflows`.
The mirror preserves every branch, tag and commit exactly.

## 3. Install git-filter-repo

```bash
brew install git-filter-repo
git filter-repo --version    # sanity check
```

## 4. Extract the value at runtime → /tmp only

```bash
git grep -h '"instanceId"' c81a929 -- 'n8n/*/workflow.json' \
  | sed -E 's/.*"instanceId": *"([0-9a-f]{64})".*/\1==>REMOVED-INSTANCE-ID/' \
  | sort -u > /tmp/replacements.txt
wc -l /tmp/replacements.txt   # expect exactly 1 line
grep -c '==>' /tmp/replacements.txt   # expect 1
```

The `--replace-text` format is `literal==>replacement`. Verify the file
contains the pattern, not the prose label.

## 5. Rewrite

```bash
git filter-repo --replace-text /tmp/replacements.txt --force
```

This rewrites every commit. `--force` is required because the repo has a
remote and existing refs — it is safe here precisely because we are about
to force-push anyway.

## 6. Re-add the remote (gotcha)

`git filter-repo` **deletes the `origin` remote** as a safety measure.
Re-add it or the push fails confusingly:

```bash
git remote add origin https://github.com/lethevinh/automation-workflows.git
git remote -v   # confirm
```

## 7. Post-rewrite verification

```bash
# the value must be gone from every reachable commit
LEAK=$(sed -E 's/==>.*//' /tmp/replacements.txt)
git log --all -S "$LEAK" --oneline           # expect: no output
git grep -c "$LEAK" HEAD -- . ; echo "grep exit $? (1 = clean)"
bash scripts/verify-all.sh                   # expect: RESULT: all checks passed
```

**`c81a929` no longer exists after the rewrite** — replacing text changes the
blob, so that commit (and every descendant) gets a new hash. Do not try to
reference the old SHAs from the rewritten repo. Compare against the step-2
mirror instead:

```bash
# pull the pre-rewrite tip in from the backup mirror, then diff old vs new
git fetch ~/backups/automation-workflows-<date>.git main:refs/backup/pre-rewrite
git diff --stat refs/backup/pre-rewrite HEAD
```

Expected: only the files listed as targets in step 4 (the four `workflow.json`
carrying `meta.instanceId`, plus `docs/portfolio-upgrade-plan.md` from
`e916120`). Anything else in that diff means the rewrite was too broad — stop
and restore from the mirror before pushing. The commit map filter-repo writes
is also useful evidence:

```bash
wc -l .git/filter-repo/commit-map    # old_sha new_sha per rewritten commit
```

Then drop the rewritten-away objects from the local repo, so the value does not
linger in reflogs or dangling objects on this machine (the repo is on a shared
working directory used by agents):

```bash
git reflog expire --expire=now --all && git gc --prune=now --aggressive
git fsck --no-progress 2>/dev/null | head    # expect: no dangling objects carrying the value
```

## 8. HARD GATE — do not push from this runbook

The final step is, verbatim:

```bash
git push --force-with-lease origin main
```

**Print it. Do not run it.** The owner must authorise the force-push in
writing — it rewrites public history.

## 9. Honest post-push caveats

- Earlier clones/forks keep the value — there is no recall.
- GitHub may retain the old commits as dangling objects and in cached
  views; open a GitHub Support request to purge them if the exposure
  matters.
- Treat the value as compromised regardless: it was public in
  `c81a929`. If n8n ever uses `instanceId` for telemetry/licensing
  correlation, rotate or regenerate the instance identity.

## 10. Cleanup

```bash
shred -u /tmp/replacements.txt 2>/dev/null || rm -P /tmp/replacements.txt
```
