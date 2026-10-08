#!/usr/bin/env bash
# Local reproduction of the checks in .github/workflows/validate.yml.
# KEEP THE TWO IN SYNC — the CI job runs the same commands step by step.
#
# Usage: bash scripts/verify-all.sh
# Exit code is non-zero if any check failed (all checks still run, so the
# summary shows the full damage instead of stopping at the first failure).

set -uo pipefail
cd "$(dirname "$0")/.."

FAILED=()

check() {
    local name="$1"; shift
    echo "=== $name"
    if "$@"; then
        echo "PASS: $name"
    else
        echo "FAIL: $name"
        FAILED+=("$name")
    fi
    echo
}

# --- existing checks (unchanged from validate.yml) -------------------------

workflow_json_validity() {
    local found=0 f
    while IFS= read -r -d '' f; do
        found=1
        echo "Checking $f"
        jq empty "$f" || return 1
        # n8n exports must have a nodes array
        jq -e '.nodes | type == "array"' "$f" > /dev/null || return 1
    done < <(find n8n -name 'workflow.json' -print0)
    [ "$found" -eq 0 ] && echo "No n8n workflows yet — skipping."
    return 0
}

secret_scan() {
    if grep -rInE '(xoxb-[0-9A-Za-z-]{20,}|sk-[A-Za-z0-9_-]{20,}|AKIA[0-9A-Z]{16}|-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----)' \
        --exclude-dir=.git --exclude='.env.example' .; then
        echo "Possible secret committed to the repo"
        return 1
    fi
    echo "No secrets found."
}

ruff_lint() {
    if find python -name '*.py' | grep -q .; then
        if command -v ruff >/dev/null 2>&1; then
            ruff check python/
        elif command -v pipx >/dev/null 2>&1; then
            pipx run ruff check python/
        else
            echo "SKIP: ruff not installed locally (CI uses 'pipx run ruff')"
        fi
    else
        echo "No Python sources yet — skipping."
    fi
}

# --- portfolio guardrails (P5) ----------------------------------------------

folder_contract() {
    local rc=0 d f
    for d in n8n/*/; do
        for f in workflow.json README.md assets/diagram.svg \
                 assets/diagram.json .env.example; do
            if [ ! -f "$d$f" ]; then
                echo "MISSING: $d$f"
                rc=1
            fi
        done
    done
    for d in examples/*/; do
        if [ ! -f "${d}test-data.json" ]; then
            echo "MISSING: ${d}test-data.json"
            rc=1
        fi
    done
    [ "$rc" -eq 0 ] && echo "Folder contract: all required files present."
    return "$rc"
}

mermaid_drift() {
    if [ -n "$(git status --porcelain -- n8n)" ]; then
        echo "note: uncommitted changes already exist under n8n/ —"
        echo "      the diff below may include them, not just render output:"
        git status --porcelain -- n8n
    fi
    python3 scripts/render-mermaid.py n8n/*/ || return 1
    git diff --exit-code -- n8n/
}

sanitization_residue() {
    local rc=0
    # Spec'd pattern: quoted JSON keys anywhere under n8n/. README prose
    # mentions these names in backticks, which this pattern does not match.
    if git grep -nE '"instanceId"|"versionId"|"webhookId"' -- n8n/; then
        echo "leaked-identifier keys found under n8n/"
        rc=1
    fi
    # Stronger bareword scan on the exports only: catches the tokens inside
    # parameter strings too (JSON keys are always quoted either way).
    if git grep -nE 'instanceId|versionId|webhookId' -- 'n8n/*/workflow.json'; then
        echo "identifier residue in a workflow export"
        rc=1
    fi
    # Top-level export keys that P-1 removed must not come back.
    python3 - <<'EOF' || rc=1
import glob
import json
import sys

bad = []
for f in sorted(glob.glob("n8n/*/workflow.json")):
    d = json.load(open(f))
    for key in ("id", "versionId", "createdAt", "updatedAt",
                "pinData", "nodeGroups"):
        if key in d:
            bad.append(f"{f}: top-level {key!r} present")
    if isinstance(d.get("meta"), dict) and "instanceId" in d["meta"]:
        bad.append(f"{f}: meta.instanceId present")
if bad:
    print("\n".join(bad))
    sys.exit(1)
print("Top-level identifiers: clean.")
EOF
    return "$rc"
}

placeholder_scan() {
    python3 - <<'EOF'
import re
import subprocess
import sys

# These two planning docs legitimately discuss placeholders and identifiers.
EXCLUDE = {"docs/portfolio-upgrade-plan.md", "docs/agent-prompts.md"}

# Owner-pending hire-me CTAs in the root README, to be replaced by P3 once
# the owner supplies links (plan section 6). Allowlisted so the scan lands
# green in wave 2; any NEW placeholder, or these tokens anywhere else,
# still fails.
ALLOWED_TOKENS = {
    "README.md": {
        "[your-upwork-profile]",
        "[your-linkedin]",
        "[your-email]",
        "[your-site]",
    },
}

files = subprocess.check_output(
    ["git", "ls-files", "*.md"], text=True
).split()

bad = []
for path in files:
    if path in EXCLUDE:
        continue
    with open(path, encoding="utf-8") as fh:
        for i, line in enumerate(fh, 1):
            for pat in ("your_chat_id", "TODO"):
                if pat in line:
                    bad.append(f"{path}:{i}: contains {pat!r}")
            tokens = re.findall(r"\[your-[^\s\]]*\]", line)
            if line.count("[your-") != len(tokens):
                bad.append(f"{path}:{i}: unterminated '[your-' placeholder")
            for tok in tokens:
                if tok not in ALLOWED_TOKENS.get(path, set()):
                    bad.append(f"{path}:{i}: placeholder {tok!r}")
if bad:
    print("\n".join(bad))
    sys.exit(1)
print("Placeholder scan: clean.")
EOF
}

fixtures_parse() {
    local rc=0 f found=0
    for f in examples/*/test-data.json; do
        [ -e "$f" ] || continue
        found=1
        if jq empty "$f"; then
            echo "ok $f"
        else
            rc=1
        fi
    done
    [ "$found" -eq 0 ] && { echo "No test-data.json fixtures found."; rc=1; }
    return "$rc"
}

demo_lane() {
    python3 scripts/verify-demo-lane.py
}

check "workflow.json validity"        workflow_json_validity
check "secret scan"                   secret_scan
check "ruff lint"                     ruff_lint
check "folder contract"               folder_contract
check "mermaid drift"                 mermaid_drift
check "sanitization residue"          sanitization_residue
check "placeholder scan"              placeholder_scan
check "fixture test-data.json parse"  fixtures_parse
check "demo lane (zero credentials)"  demo_lane

echo "=============================================="
if [ "${#FAILED[@]}" -gt 0 ]; then
    echo "RESULT: FAIL — ${#FAILED[@]} check(s) failed:"
    printf '  - %s\n' "${FAILED[@]}"
    exit 1
fi
echo "RESULT: all checks passed."
