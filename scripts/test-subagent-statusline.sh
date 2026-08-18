#!/usr/bin/env bash
# test-subagent-statusline.sh — behaviour tests for scripts/subagent-statusline.sh
#
# subagent-statusline.sh implements Claude Code's `subagentStatusLine` command:
# stdin is one JSON object (columns, tasks[]), stdout is JSON-lines overriding
# a subset of rows. It fails open by design — any error path must still exit
# 0, and a row it declines to touch must simply be omitted, never break the
# panel. That "never break the panel" property is exactly the kind of thing
# a human never notices going wrong, hence tests.
#
#   ./scripts/test-subagent-statusline.sh
set -uo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
script="$repo_root/scripts/subagent-statusline.sh"

pass=0
fail=0

ok()   { echo "  ok    $1"; pass=$((pass + 1)); }
bad()  { echo "  FAIL  $1"; fail=$((fail + 1)); }

# Strip ANSI escape sequences so visible width can be measured.
strip_ansi() {
  python3 -c 'import re, sys; sys.stdout.write(re.sub(r"\x1b\[[0-9;]*m", "", sys.stdin.read()))'
}

visible_width() {
  # Character (codepoint) count, not byte count -- awk's `length` counts
  # bytes for multi-byte UTF-8 (e.g. the "…" truncation marker is 3 bytes,
  # 1 codepoint), which would over-count and false-fail this check. jq's own
  # `length`, which the script budgets columns against, counts codepoints,
  # so this must match that, not raw bytes.
  strip_ansi | python3 -c 'import sys; print(len(sys.stdin.readline().rstrip("\n")))'
}

if [[ ! -x "$script" ]]; then
  echo "FATAL: script missing or not executable: $script" >&2
  exit 1
fi

echo "subagent-statusline.sh"

# --- case 1: full task (model + effort + counts) ---------------------------
input='{"columns":80,"tasks":[{"id":"t1","name":"Task One","type":"general-purpose","status":"running","description":"Doing something useful","model":"claude-sonnet-5[1m]","effort":"high","contextWindowSize":200000,"tokenCount":50000}]}'
out=$(printf '%s' "$input" | "$script" 2>/dev/null)
status=$?
name="full task -> one line, correct id, human-readable model"
if [[ $status -ne 0 ]]; then
  bad "$name (exit=$status)"
elif [[ "$(printf '%s\n' "$out" | wc -l | tr -d ' ')" != "1" ]]; then
  bad "$name (want exactly one line, got: $(printf '%q' "$out"))"
elif ! printf '%s' "$out" | jq -e '.id == "t1"' >/dev/null 2>&1; then
  bad "$name (id mismatch: $(printf '%q' "$out"))"
else
  content=$(printf '%s' "$out" | jq -r '.content')
  if printf '%s' "$content" | grep -q 'Sonnet 5'; then
    ok "$name"
  else
    bad "$name (model not rendered as 'Sonnet 5': $(printf '%q' "$content"))"
  fi
fi

# --- case 2: model absent -> no line emitted for that id --------------------
input='{"columns":80,"tasks":[{"id":"t2","name":"NoModel","type":"general-purpose","status":"running","description":"desc"}]}'
out=$(printf '%s' "$input" | "$script" 2>/dev/null)
status=$?
name="model absent -> row omitted (default rendering preserved)"
if [[ $status -ne 0 ]]; then
  bad "$name (exit=$status)"
elif [[ -z "$out" ]]; then
  ok "$name"
else
  bad "$name (expected no output, got: $(printf '%q' "$out"))"
fi

# --- case 3: effort absent -> row renders, no stray middot ------------------
input='{"columns":80,"tasks":[{"id":"t3","name":"NoEffort","type":"general-purpose","status":"running","description":"desc","model":"claude-opus-4"}]}'
out=$(printf '%s' "$input" | "$script" 2>/dev/null)
status=$?
name="effort absent -> renders without stray middot"
if [[ $status -ne 0 ]]; then
  bad "$name (exit=$status)"
elif ! printf '%s' "$out" | jq -e '.id == "t3"' >/dev/null 2>&1; then
  bad "$name (row missing or malformed: $(printf '%q' "$out"))"
else
  content=$(printf '%s' "$out" | jq -r '.content')
  if printf '%s' "$content" | grep -qF '·'; then
    bad "$name (stray middot present: $(printf '%q' "$content"))"
  else
    ok "$name"
  fi
fi

# --- case 4: unrecognised model id passes through verbatim ------------------
input='{"columns":80,"tasks":[{"id":"t4","name":"Weird","type":"general-purpose","status":"running","description":"desc","model":"claude-mystery-omega"}]}'
out=$(printf '%s' "$input" | "$script" 2>/dev/null)
status=$?
name="unrecognised model id -> passed through raw, not mis-mapped"
if [[ $status -ne 0 ]]; then
  bad "$name (exit=$status)"
elif ! printf '%s' "$out" | jq -e '.id == "t4"' >/dev/null 2>&1; then
  bad "$name (row missing or malformed: $(printf '%q' "$out"))"
else
  content=$(printf '%s' "$out" | jq -r '.content')
  if printf '%s' "$content" | grep -qF 'claude-mystery-omega'; then
    ok "$name"
  else
    bad "$name (raw id not found verbatim: $(printf '%q' "$content"))"
  fi
fi

# --- case 5: columns:40 -> every emitted line fits within 40 visible cols ---
input='{"columns":40,"tasks":[
  {"id":"t5","name":"Narrow","type":"general-purpose","status":"running","description":"A very long description that should be truncated to fit the narrow panel width without blowing the column budget","model":"claude-sonnet-5","effort":"medium","contextWindowSize":200000,"tokenCount":190000},
  {"id":"t6","name":"Narrow2","type":"code-reviewer","status":"running","description":"short","model":"claude-haiku-4","contextWindowSize":100000,"tokenCount":1000}
]}'
out=$(printf '%s' "$input" | "$script" 2>/dev/null)
status=$?
name="columns:40 -> visible width of every line <= 40"
if [[ $status -ne 0 ]]; then
  bad "$name (exit=$status)"
elif [[ -z "$out" ]]; then
  bad "$name (expected output, got none)"
else
  width_ok=1
  while IFS= read -r line; do
    [[ -z "$line" ]] && continue
    content=$(printf '%s' "$line" | jq -r '.content' 2>/dev/null) || { width_ok=0; break; }
    w=$(printf '%s' "$content" | visible_width)
    [[ -z "$w" ]] && w=0
    if [[ "$w" -gt 40 ]]; then
      width_ok=0
      echo "        line width $w > 40: $(printf '%q' "$content")"
    fi
  done <<< "$out"
  if [[ $width_ok -eq 1 ]]; then
    ok "$name"
  else
    bad "$name"
  fi
fi

# --- case 6: malformed / empty stdin, missing config -> fail open -----------
check_fails_open() {  # check_fails_open <name> <stdin> [extra env assignment...]
  local name="$1" input="$2"
  shift 2
  local out status
  out=$(printf '%s' "$input" | env "$@" "$script" 2>/dev/null)
  status=$?
  if [[ $status -ne 0 ]]; then
    bad "$name (exit=$status)"
    return
  fi
  if [[ -z "$out" ]]; then
    ok "$name"
    return
  fi
  local all_valid=1
  while IFS= read -r line; do
    [[ -z "$line" ]] && continue
    printf '%s' "$line" | jq -e . >/dev/null 2>&1 || all_valid=0
  done <<< "$out"
  if [[ $all_valid -eq 1 ]]; then
    ok "$name"
  else
    bad "$name (emitted output is not valid JSON: $(printf '%q' "$out"))"
  fi
}

check_fails_open "malformed stdin" 'not json at all'
check_fails_open "empty stdin" ''
check_fails_open "missing ~/.claude/claude-powerline.json" \
  '{"columns":80,"tasks":[{"id":"t7","name":"X","type":"general-purpose","status":"running","description":"d","model":"claude-sonnet-5","effort":"low"}]}' \
  "HOME=/tmp/nonexistent-$$"

echo
echo "$pass passed, $fail failed"
[[ $fail -eq 0 ]]
