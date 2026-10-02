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
# Before the static checks run, a dependency bootstrap step restores the
# ignored node_modules/ tree with `npm ci --ignore-scripts --no-audit
# --no-fund` when node_modules/@earendil-works/pi-tui is missing and npm is on
# PATH. A test file whose header carries `// check.sh: requires-npm` is
# skipped with a specific reason instead of failing when that dependency
# cannot be restored (npm missing, or npm ci itself failed, e.g. offline).
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

script_dir="${BASH_SOURCE[0]%/*}"
[[ "$script_dir" == "${BASH_SOURCE[0]}" ]] && script_dir="."
repo_root="$(cd "$script_dir/.." && pwd)"

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

# Dependency bootstrap: restore the ignored node_modules/ tree when it looks
# absent. node_modules/@earendil-works/pi-tui is the marker -- it is the
# deepest peer dependency a test actually imports, so its presence is a
# reasonable proxy for "npm ci already ran". A tree that already has it is not
# touched again, and that "nothing to do" case adds no row at all: it is not
# noteworthy and should not look like a failure or a skip.
pi_tui_marker="$repo_root/node_modules/@earendil-works/pi-tui"
npm_present=false
command -v npm >/dev/null 2>&1 && npm_present=true
npm_ci_failed=false
npm_ci_failure_detail=""
if [[ -d "$pi_tui_marker" ]]; then
  : # Already restored -- nothing to bootstrap, nothing to report.
elif [[ "$npm_present" != true ]]; then
  record skip "npm-ci-bootstrap" "npm not found"
else
  npm_ci_output="$(cd "$repo_root" && npm ci --ignore-scripts --no-audit --no-fund 2>&1)"
  npm_ci_status=$?
  if [[ $npm_ci_status -eq 0 ]]; then
    record ok "npm-ci-bootstrap"
  else
    npm_ci_failed=true
    npm_ci_failure_detail="${npm_ci_output##*$'\n'}"
    record fail "npm-ci-bootstrap" "exit $npm_ci_status: ${npm_ci_failure_detail:-npm ci failed}"
  fi
fi

# CI parity. CI runs with an empty HOME and the runner sets XDG_CONFIG_HOME,
# so a check that reads ~/.pi or ignores XDG_CONFIG_HOME passes here and fails
# on the PR (#69, #70). Run every check under that shape. After the npm
# bootstrap, so npm keeps the real ~/.npm cache.
ci_scratch="$(mktemp -d)"
trap 'rm -rf "$ci_scratch"' EXIT
mkdir -p "$ci_scratch/home" "$ci_scratch/xdg-config"
export HOME="$ci_scratch/home" XDG_CONFIG_HOME="$ci_scratch/xdg-config"
unset PI_CODING_AGENT_DIR

# Static checks first. They are not discovered: they do not follow the
# scripts/test-* naming rule.
run "lint-skills.py" python3 "$repo_root/scripts/lint-skills.py" "$repo_root"
run "check-manifest.py" python3 "$repo_root/scripts/check-manifest.py" "$repo_root"
run "check-model-routing.py" python3 "$repo_root/scripts/check-model-routing.py" "$repo_root"
run "build-dist.py" python3 "$repo_root/scripts/build-dist.py" "$repo_root" --check

npm_dependency_available=false
[[ -d "$pi_tui_marker" ]] && npm_dependency_available=true
node_present=false
command -v node >/dev/null 2>&1 && node_present=true

npm_unavailable_reason() {
  if [[ "$npm_present" != true ]]; then
    echo "npm not found"
  elif [[ "$npm_ci_failed" == true ]]; then
    if [[ -n "$npm_ci_failure_detail" ]]; then
      echo "npm ci failed: $npm_ci_failure_detail"
    else
      echo "npm ci failed"
    fi
  else
    echo "npm ci did not restore it"
  fi
}

requires_npm() {
  # Pure-bash line match (no grep dependency): the discovery loop must keep
  # working on a minimal PATH that has only node, python3, bash and git.
  local file="$1" line
  while IFS= read -r line || [[ -n "$line" ]]; do
    [[ "$line" == '// check.sh: requires-npm' ]] && return 0
  done <"$file"
  return 1
}

# Lexical discovery: every scripts/test-* regular file, by extension.
for test_file in "$repo_root"/scripts/test-*; do
  [[ -f "$test_file" ]] || continue
  label="${test_file##*/}"
  case "$label" in
  *.py) run "$label" python3 "$test_file" ;;
  *.mjs | *.js)
    if [[ "$node_present" != true ]]; then
      record skip "$label" "dependency unavailable: node not found"
    elif [[ "$npm_dependency_available" != true ]] && requires_npm "$test_file"; then
      record skip "$label" "dependency unavailable: $(npm_unavailable_reason)"
    else
      run "$label" node "$test_file"
    fi
    ;;
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
