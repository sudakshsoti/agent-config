#!/usr/bin/env bash
# Fixture tests for skills/overnight-run/scripts/usage-gate.sh: the exit code
# is the whole contract with overnight.sh, and a wrong 0 spends a weekly
# window unattended. Exits 77 (skip) when jq is unavailable.
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
gate="$repo_root/skills/overnight-run/scripts/usage-gate.sh"
fixtures="$repo_root/skills/overnight-run/scripts/fixtures"
command -v jq >/dev/null 2>&1 || {
  echo "jq not on PATH"
  exit 77
}

# Every fixture is generated at this instant; the 5h windows reset 3600 s later.
export USAGE_GATE_NOW_MS=1790533120264
fails=0

# expect <want-exit> <want-stdout> <label> <fixture name|absolute path|-> [gate args...]
# "-" runs the live omp path.
expect() {
  local want="$1" want_out="$2" label="$3" fixture="$4"
  shift 4
  [[ "$fixture" == /* || "$fixture" == - ]] || fixture="$fixtures/$fixture"
  local got=0 out
  if [[ "$fixture" == - ]]; then
    out="$(unset USAGE_GATE_JSON && "$gate" "$@" 2>/dev/null)" || got=$?
  else
    out="$(USAGE_GATE_JSON="$fixture" "$gate" "$@" 2>/dev/null)" || got=$?
  fi
  if [[ "$got" == "$want" && "$out" == "$want_out" ]]; then
    echo "  ok    $label"
  else
    echo "  FAIL  $label: exit $got stdout '$out', want exit $want stdout '$want_out'"
    fails=$((fails + 1))
  fi
}

expect 0 "" "all windows under threshold" go.json
expect 10 3720 "5h over threshold sleeps until reset + 120 s" sleep-5h.json
FIVE_HOUR_SLEEP_PCT=76 expect 0 "" "5h below a raised threshold goes" sleep-5h.json
expect 20 "" "7d over pace stops, even with 5h also over" stop-7d.json
expect 20 "" "model-scoped 7d over pace stops its family" stop-model-7d.json --model anthropic/claude-opus-5-5
expect 0 "" "model-scoped 7d of another family is ignored" stop-model-7d.json --model claude-sonnet-5-5
expect 20 "" "unknown family gates every model-scoped 7d" stop-model-7d.json
expect 0 "" "late-week 7d at 60% with 90% elapsed goes" pace-go-late-7d.json
expect 20 "" "day-1 7d at 40% with 10% elapsed stops" pace-stop-early-7d.json
expect 0 "" "near-start 7d at 10% with 1% elapsed goes (floor)" pace-guard-start-7d.json
expect 20 "" "late-week 7d at 92% stops on the ceiling" pace-hard-cap-late-7d.json
expect 20 "" "scoped 7d over pace stops its family while global is on pace" pace-stop-model-7d.json --model anthropic/claude-opus-5-5
expect 20 "" "unknown family gates an over-pace scoped 7d" pace-stop-model-7d.json
expect 0 "" "weekly window without resetsAt at 70% goes" pace-no-reset-7d.json
expect 20 "" "weekly window without resetsAt at 95% stops" pace-no-reset-hard-7d.json
expect 20 "" "borderline pace stops at the default margin" pace-margin-borderline-7d.json
PACE_MARGIN_PCT=25 expect 0 "" "raised margin lets the borderline case go" pace-margin-borderline-7d.json
expect 30 "" "no anthropic report is unknown" no-anthropic.json
expect 30 "" "missing 5h window is unknown" missing-5h.json

# The stop reason must name the rule that fired.
err="$(USAGE_GATE_JSON="$fixtures/pace-stop-early-7d.json" "$gate" 2>&1 >/dev/null || true)"
case "$err" in
*elapsed*) echo "  ok    pace stop names the elapsed rule" ;;
*)
  echo "  FAIL  pace stop names the elapsed rule: '$err'"
  fails=$((fails + 1))
  ;;
esac
err="$(USAGE_GATE_JSON="$fixtures/pace-hard-cap-late-7d.json" "$gate" 2>&1 >/dev/null || true)"
case "$err" in
*"weekly over 90%"*) echo "  ok    ceiling stop names the 90% rule" ;;
*)
  echo "  FAIL  ceiling stop names the 90% rule: '$err'"
  fails=$((fails + 1))
  ;;
esac

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
printf 'not json\n' >"$tmp/garbage.json"
expect 30 "" "unparseable usage JSON is unknown" "$tmp/garbage.json"
# A PATH holding the tools the gate needs, but no omp.
mkdir "$tmp/bin"
for tool in bash env jq cat date sleep; do ln -s "$(command -v "$tool")" "$tmp/bin/$tool"; done
PATH="$tmp/bin" expect 30 "" "omp missing is unknown" -
((fails == 0)) || exit 1
