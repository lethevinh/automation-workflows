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
LEAK=$(sed -E 's/==>.*//' /tmp/replacements.txt)

# Scope matters: verify the branch that will actually be pushed.
git log -S "$LEAK" --oneline refs/heads/main   # expect: no output
git grep -c "$LEAK" HEAD -- . ; echo "grep exit $? (1 = clean)"

# Whole-object scan, without ever printing the value:
git rev-list refs/heads/main | while read c; do
  git grep -l -E '"instanceId": *"[0-9a-f]{64}"' "$c" -- 2>/dev/null
done | sort -u                                  # expect: nothing

bash scripts/verify-all.sh                      # expect: RESULT: all checks passed
```

**Do not use `--all` for this check.** If you created a rollback ref from the
step-2 mirror (e.g. `refs/backup/main`), that ref deliberately keeps the
pre-rewrite chain — including the leaked value — reachable in this clone.
`git log --all -S "$LEAK"` will therefore still find it and is not a valid
cleanliness test. Only `refs/heads/main` is what gets published.

**`c81a929` no longer exists after the rewrite** — replacing text changes the
blob, so that commit (and every descendant) gets a new hash. Do not try to
reference the old SHAs from the rewritten repo. Compare against the step-2
mirror instead:

```bash
# pull the pre-rewrite tip in from the backup mirror, then diff old vs new
git fetch ~/backups/automation-workflows-<date>.git main:refs/backup/pre-rewrite
git diff --stat refs/backup/pre-rewrite HEAD
```

Expected: **empty** — the pre-rewrite tip's working tree was already clean
(redaction and P-1 landed before the rewrite), so only historical blobs
changed. Anything listed here means the rewrite touched content it should not
have — stop and restore from the mirror before pushing. The commit map
filter-repo writes is the mapping evidence:

```bash
wc -l .git/filter-repo/commit-map    # header + one line per rewritten commit
```

## 8. HARD GATE — do not push from this runbook

**First, fetch — the lease needs a remote-tracking ref.** `git filter-repo`
deleted `origin`; re-adding it does not recreate `refs/remotes/origin/main`.
Running `--force-with-lease` without it fails, and fails *safely*:

```
! [rejected]  main -> main (stale info)
```

Verify that for yourself, then re-establish the lease:

```bash
git fetch origin                                  # recreates refs/remotes/origin/main
git rev-parse refs/remotes/origin/main            # must equal the CURRENT public tip
git push --force-with-lease --dry-run origin main # expect: no rejection
```

The final step, only after the dry run is clean, is verbatim:

```bash
git push --force-with-lease origin main
```

**Print it. Do not run it.** The owner must authorise the force-push in
writing — it rewrites public history. `--force-with-lease` (never bare
`--force`) is what makes it safe: if anyone pushed to the repo since the fetch,
the push is rejected instead of clobbering their work.

## 8b. After the push is verified

- **Purge the local rollback copies.** The mirror in `~/backups/` and any
  `refs/backup/*` ref keep the value on this machine. Once the public repo is
  confirmed clean, delete the ref and decide whether to keep the mirror
  offline: `git update-ref -d refs/backup/main`.
- **Re-run `bash scripts/verify-all.sh`** on a fresh clone of the public repo —
  that is the only check that proves what the world sees.
- GitHub may retain the old commits as dangling objects and in cached views;
  open a Support request to purge them if the exposure matters.

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
