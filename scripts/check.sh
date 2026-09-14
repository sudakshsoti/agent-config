#!/usr/bin/env bash
# check.sh — the single entrypoint for everything this repo can verify.
#
# Before this existed each check had to be remembered and run by hand, which
# in practice meant neither test script ran between the day it was written and
# the day something broke. One command, run manually and by CI; pre-commit runs
# only the fast subset.
#
#   ./scripts/check.sh
#
# A fixed static-check list runs first, then every scripts/test-* regular file
# is discovered by extension and run with its interpreter (.py -> python3,
# .mjs/.js -> node, .sh -> bash). A test that exits 0 passes, exit 77 skips and
# any other status fails; an extension we cannot run fails rather than quietly
# disappearing from the report. Every check runs even when an earlier one fails
# -- one run should report every problem, not the first one. Hence
# set -uo pipefail and NOT -e.
#
# The working tree must look the same before and after the run, so a check that
# writes into the checkout is reported instead of passing silently. The guard
# is skipped, not failed, when git cannot answer.
set -uo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

pass=0
fail=0
skip=0
declare -a results=()

record() { # record <ok|skip|fail> <label> [detail]
  local state="$1"
  local label="$2"
  local detail="${3:-}"
  case "$state" in
  ok)
    results+=("  ok    $label")
    pass=$((pass + 1))
    ;;
  skip)
    results+=("  SKIP  $label${detail:+ ($detail)}")
    skip=$((skip + 1))
    ;;
  *)
    results+=("  FAIL  $label${detail:+ ($detail)}")
    fail=$((fail + 1))
    ;;
  esac
  echo
}

run() { # run <label> <command...>
  local label="$1"
  shift
  "$@"
  local status=$?
  case "$status" in
  0) record ok "$label" ;;
  77) record skip "$label" "exit 77" ;;
  *) record fail "$label" "exit $status" ;;
  esac
}

tree_status() {
  git -C "$repo_root" status --porcelain 2>/dev/null
}

before_status=""
guard_supported=false
if command -v git >/dev/null 2>&1 &&
  git -C "$repo_root" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  guard_supported=true
  before_status="$(tree_status)"
fi

# Static checks first. They are not discovered: they do not follow the
# scripts/test-* naming rule.
run "lint-skills.py" python3 "$repo_root/scripts/lint-skills.py" "$repo_root"

# Lexical discovery: every scripts/test-* regular file, by extension.
for test_file in "$repo_root"/scripts/test-*; do
  [[ -f "$test_file" ]] || continue
  label="$(basename "$test_file")"
  case "$label" in
  *.py) run "$label" python3 "$test_file" ;;
  *.mjs | *.js) run "$label" node "$test_file" ;;
  *.sh) run "$label" bash "$test_file" ;;
  *) record fail "$label" "unsupported extension" ;;
  esac
done

if [[ "$guard_supported" != true ]]; then
  record skip "git-status-unchanged" "no git work tree"
else
  after_status="$(tree_status)"
  if [[ "$before_status" == "$after_status" ]]; then
    record ok "git-status-unchanged"
  else
    record fail "git-status-unchanged" "working tree changed"
  fi
fi

echo "check.sh"
if [[ ${#results[@]} -gt 0 ]]; then
  printf '%s\n' "${results[@]}"
fi
echo
echo "$pass passed, $fail failed, $skip skipped"
[[ $fail -eq 0 ]]
