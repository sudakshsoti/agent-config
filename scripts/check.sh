#!/usr/bin/env bash
# check.sh — the single entrypoint for everything this repo can verify.
#
# Before this existed each check had to be remembered and run by hand, which
# in practice meant neither test script ran between the day it was written and
# the day something broke. One command, run by the pre-commit hook (the two
# fast checks only) and by CI (all four).
#
#   ./scripts/check.sh
#
# Every check runs even when an earlier one fails -- one run should report
# every problem, not the first one. Hence set -uo pipefail and NOT -e, same as
# the two test scripts it wraps.
set -uo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

pass=0
fail=0
declare -a results=()

run() {  # run <label> <command...>
  local label="$1"
  shift
  "$@"
  local status=$?
  if [[ $status -eq 0 ]]; then
    results+=("  ok    $label")
    pass=$((pass + 1))
  else
    results+=("  FAIL  $label (exit $status)")
    fail=$((fail + 1))
  fi
  echo
}

# Fast checks first: they are the ones the pre-commit hook runs, so a failure
# a human is about to hit shows up at the top rather than after a minute of
# sleeps in the memory-consolidate suite.
run "lint-skills.py"              python3 "$repo_root/scripts/lint-skills.py" "$repo_root"
run "check-zips.py"               python3 "$repo_root/scripts/check-zips.py" "$repo_root"
run "test-context-size.sh"        "$repo_root/scripts/test-context-size.sh"
run "test-memory-consolidate.sh"  "$repo_root/scripts/test-memory-consolidate.sh"
run "test-orient.sh"              "$repo_root/scripts/test-orient.sh"
run "test-apply-codex-config.py" python3 "$repo_root/scripts/test-apply-codex-config.py"
run "test-agent-instructions.py" python3 "$repo_root/scripts/test-agent-instructions.py"

# CI has only this checkout, not the sibling repositories in ~/dev. The
# fixture suite above always runs; the live cohort audit is a local check.
if [[ "${CI:-}" != "true" || "${RUN_LIVE_COHORT_CHECK:-}" == "1" ]]; then
  run "managed repository instructions" \
    python3 "$repo_root/scripts/check-agent-instructions.py" \
      --manifest "$repo_root/config/repository-instructions.json" \
      --cohort-root "${AGENT_COHORT_ROOT:-$(dirname "$repo_root")}" \
      --skip-deferred
fi

echo "check.sh"
printf '%s\n' "${results[@]}"
echo
echo "$pass passed, $fail failed"
[[ $fail -eq 0 ]]
