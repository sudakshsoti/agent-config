#!/usr/bin/env bash
# test-context-size.sh — behaviour tests for hooks/context-budget.py
#
# context-budget.py is a UserPromptSubmit hook, so it fails SILENTLY by
# design: any error path prints nothing and exits 0. That is exactly the
# failure mode a human never notices — a broken hook and a below-threshold
# session look identical. Hence tests, in a repo that otherwise has none.
#
#   ./scripts/test-context-size.sh
set -uo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
script="$repo_root/hooks/context-budget.py"
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"; rm -f /tmp/claude-ctx-*' EXIT

pass=0
fail=0

check() {  # check <name> <stdin> <want> [runner...] (runner defaults to `python3 "$script"`)
  local name="$1" input="$2" want="$3"
  shift 3
  local -a runner=("$@")
  [[ ${#runner[@]} -eq 0 ]] && runner=(python3 "$script")
  local out status
  out=$(printf '%s' "$input" | "${runner[@]}" 2>/dev/null)
  status=$?
  local ok=1
  case "$want" in
    # Under threshold and every error path render nothing at all -- the hook
    # only ever speaks up when it actually has something to say.
    silent) [[ -z "$out" ]] || ok=0 ;;
    # Over threshold: stdout must parse as JSON carrying the hookSpecificOutput
    # blob Claude Code actually reads, not just a string that happens to
    # contain familiar words.
    alert) printf '%s' "$out" | jq -e '.hookSpecificOutput.additionalContext' >/dev/null 2>&1 || ok=0 ;;
  esac
  # A hook that exits non-zero is a real failure mode: it's supposed to fail
  # open (silent, exit 0), never fail loud.
  [[ $status -eq 0 ]] || ok=0
  if [[ $ok -eq 1 ]]; then
    echo "  ok    $name"
    pass=$((pass + 1))
  else
    echo "  FAIL  $name (want=$want, exit=$status, output=$(printf '%q' "$out"))"
    fail=$((fail + 1))
  fi
}

expect_silent() { check "$1" "$2" silent; }   # under threshold, or any error path: render nothing
expect_flag()   { check "$1" "$2" alert; }    # over threshold: hookSpecificOutput JSON

# A transcript line shaped like a real one: the fields the walk sums live
# under .message.usage, and sidechain (subagent) turns must be ignored.
usage_line() {
  local input="$1" sidechain="${2:-false}"
  printf '{"isSidechain":%s,"message":{"usage":{"input_tokens":%s,"output_tokens":500,"cache_creation_input_tokens":0,"cache_read_input_tokens":0}}}\n' \
    "$sidechain" "$input"
}

payload() {  # payload <current_usage-json> [transcript_path]
  local usage="$1" transcript="${2:-}"
  jq -nc --argjson usage "$usage" --arg transcript "$transcript" \
    '{context_window: {context_window_size: 200000, current_usage: $usage}}
     | if $transcript == "" then . else .transcript_path = $transcript end'
}

# THRESHOLD lives in one place (hooks/context_size.py) precisely so nothing
# downstream has to know its value. Read it back here too, rather than
# hardcoding fixtures against it -- that's what let these tests go stale the
# last time the number moved, and it'll happen again otherwise.
threshold=$(cd "$repo_root/hooks" && python3 -c 'import context_size; print(context_size.THRESHOLD)')
threshold_status=$?
# A failure here (python3 missing, the import broken) must not become a
# silent 0 that arithmetic below happily accepts -- name the cause instead
# of leaving the rest of the suite to fail confusingly downstream.
if [[ $threshold_status -ne 0 || ! "$threshold" =~ ^[0-9]+$ ]]; then
  echo "FATAL: could not read THRESHOLD from hooks/context_size.py" >&2
  echo "  python3 exited $threshold_status, printed: '$threshold'" >&2
  exit 1
fi
under=$((threshold - 30000))   # comfortably under the line
over=$((threshold + 10000))    # comfortably over it

# The current_usage cases split their total across all three input-side
# fields, with input_tokens absorbing the remainder -- see below. Built into
# variables up front (rather than inline) because a `"..."` containing
# escaped quotes does not survive being nested inside another `$(...)"..."`.
input_below=$((under - 30000))
input_above=$((over - 60000))
usage_below="{\"input_tokens\":$input_below,\"output_tokens\":9999999,\"cache_creation_input_tokens\":20000,\"cache_read_input_tokens\":10000}"
usage_above="{\"input_tokens\":$input_above,\"output_tokens\":0,\"cache_creation_input_tokens\":20000,\"cache_read_input_tokens\":40000}"

echo "context-budget.py"

if [[ ! -f "$script" ]]; then
  echo "  FAIL  script does not exist: $script"
  exit 1
fi

# --- fast path: context_window.current_usage present -----------------------
# input_tokens absorbs the remainder, so the three fields still sum to
# $under -- 30k under the line -- rather than landing it all in one field.
expect_silent "below threshold via current_usage" "$(payload "$usage_below")"

# The absurd output_tokens above is deliberate: output must NOT count toward
# the threshold, matching used_percentage's input-only formula.
#
# The dedupe stamp is keyed on transcript_path (falling back to session_id,
# falling back to ""), so every over-threshold case below needs its own
# distinct key -- otherwise two cases sharing "" would collide, and the
# second would render silent not because it's correct but because it got
# deduped, which is a false green. current_usage short-circuits before the
# transcript is ever resolved, so this string never has to point at a real
# file, only to be unique.
expect_flag "above threshold via current_usage" \
  "$(payload "$usage_above" "current-usage-above")"

# --- fallback: current_usage null (pre-first-call, or just after /compact) --
below="$tmp/below.jsonl"
{ usage_line 5000; usage_line "$under"; } > "$below"
expect_silent "below threshold via transcript fallback" \
  "$(payload 'null' "$below")"

above="$tmp/above.jsonl"
{ usage_line 5000; usage_line "$over"; } > "$above"
expect_flag "above threshold via transcript fallback" \
  "$(payload 'null' "$above")"

# A subagent turn carries its own much smaller context; counting one as the
# latest would silence the flag on a long main thread.
sidechain="$tmp/sidechain.jsonl"
{ usage_line "$over"; usage_line 900 true; } > "$sidechain"
expect_flag "sidechain turns do not mask a large main thread" \
  "$(payload 'null' "$sidechain")"

# --- unmeasurable context degrades to silence, not an alarm -----------------
# An unknown context size is not an alarm. Every one of these must render
# nothing, same as a genuinely below-threshold session, so a measurement
# failure never cries wolf.
expect_silent "no context_window and no transcript" '{}'
expect_silent "transcript path does not exist" \
  "$(payload 'null' "$tmp/nope.jsonl")"
expect_silent "json that is not an object" '[1,2,3]'

corrupt="$tmp/corrupt.jsonl"
printf '{"message":{"usage":{"input_tokens":\ngarbage\n' > "$corrupt"
expect_silent "corrupt transcript lines" "$(payload 'null' "$corrupt")"

# --- unreadable stdin renders nothing at all -------------------------------
# Nothing was understood, so nothing is asserted.
expect_silent "malformed json on stdin" 'not json at all'
expect_silent "empty stdin" ''

# --- dedupe: same bucket, same key, only warns once -------------------------
# Real behaviour worth locking in on its own: the hook stamps
# /tmp/claude-ctx-* per (transcript-or-session, threshold-step), so a session
# sitting above the line doesn't get the warning re-injected into every
# single prompt. Needs its own transcript, distinct from every case above --
# reusing one of those would make the "first call" assertion below meet an
# already-written stamp and go silent for the wrong reason.
dedupe="$tmp/dedupe.jsonl"
{ usage_line 5000; usage_line "$over"; } > "$dedupe"
expect_flag   "dedupe: first call over threshold warns" \
  "$(payload 'null' "$dedupe")"
expect_silent "dedupe: second call in same bucket stays silent" \
  "$(payload 'null' "$dedupe")"

echo
echo "$pass passed, $fail failed"
[[ $fail -eq 0 ]]
