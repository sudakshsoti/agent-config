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
# What runs:
#   - a fixed list of static checks (below);
#   - every scripts/test-* file, discovered in lexical order and run by
#     extension (.py -> python3, .mjs/.js -> node, .sh -> bash). A test-* file
#     with any other extension is reported as FAIL, never silently ignored, so
#     adding a test can't leave it unrun.
#
# Result states: ok (exit 0), SKIP (exit 77, the automake convention for "this
# test cannot run here", e.g. a missing dependency), FAIL (anything else).
#
# The run must not change the working tree: `git status --porcelain` is
# compared before and after, and any difference is a FAIL.
#
# Every check runs even when an earlier one fails -- one run should report
# every problem, not the first one. Hence set -uo pipefail and NOT -e.
set -uo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

pass=0
fail=0
skip=0
declare -a results=()

record() { # record <state> <label> [detail]
  local line
  case "$1" in
    ok)   line="  ok    $2"; pass=$((pass + 1)) ;;
    SKIP) line="  SKIP  $2"; skip=$((skip + 1)) ;;
    *)    line="  FAIL  $2"; fail=$((fail + 1)) ;;
  esac
  [[ -n "${3:-}" ]] && line="$line ($3)"
  results+=("$line")
}

run() { # run <label> <command...>
  local label="$1"
  shift
  echo "== $label"
  "$@"
  local status=$?
  case $status in
    0)  record ok "$label" ;;
    77) record SKIP "$label" "exit 77" ;;
    *)  record FAIL "$label" "exit $status" ;;
  esac
  echo
}

git_status() {
  git -C "$repo_root" status --porcelain 2>/dev/null
}

in_git=0
if git -C "$repo_root" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  in_git=1
  status_before="$(git_status)"
fi

# Static checks: fixed list, run before the discovered tests.
run "lint-skills.py" python3 "$repo_root/scripts/lint-skills.py" "$repo_root"
run "check-zips.py" python3 "$repo_root/scripts/check-zips.py" "$repo_root"

# Tests: every scripts/test-*, lexical order (glob expansion is sorted).
for test_path in "$repo_root"/scripts/test-*; do
  [[ -f "$test_path" ]] || continue
  name="$(basename "$test_path")"
  case "$name" in
    *.py)       run "$name" python3 "$test_path" ;;
    *.mjs|*.js) run "$name" node "$test_path" ;;
    *.sh)       run "$name" bash "$test_path" ;;
    *)          record FAIL "$name" "no runner for this extension" ;;
  esac
done

# Working-tree guard: a hermetic check must leave git status untouched.
if [[ $in_git -eq 1 ]]; then
  status_after="$(git_status)"
  if [[ "$status_before" == "$status_after" ]]; then
    record ok "git-status-unchanged"
  else
    echo "== git-status-unchanged"
    echo "git status --porcelain changed during the run:"
    diff <(printf '%s\n' "$status_before") <(printf '%s\n' "$status_after")
    echo
    record FAIL "git-status-unchanged" "working tree changed"
  fi
else
  record SKIP "git-status-unchanged" "not a git work tree"
fi

echo "check.sh"
printf '%s\n' ${results[@]+"${results[@]}"}
echo
echo "$pass passed, $fail failed, $skip skipped"
[[ $fail -eq 0 ]]
