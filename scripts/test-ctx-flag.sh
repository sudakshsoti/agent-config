#!/usr/bin/env bash
# test-ctx-flag.sh — behaviour tests for scripts/ctx-flag.py
#
# ctx-flag.py is a status line widget, so it fails SILENTLY by design: any
# error path prints nothing and exits 0. That is exactly the failure mode a
# human never notices — a broken script and a below-threshold session look
# identical. Hence tests, in a repo that otherwise has none.
#
#   ./scripts/test-ctx-flag.sh
set -uo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
script="$repo_root/scripts/ctx-flag.py"
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

pass=0
fail=0

check() {  # check <name> <predicate-description> <stdin> <test-fn>
  local name="$1" input="$2" want="$3" out status
  out=$(printf '%s' "$input" | python3 "$script" 2>/dev/null)
  status=$?
  local ok=1
  case "$want" in
    # Errors collapse the widget entirely rather than rendering a traceback.
    empty) [[ -z "$out" ]] || ok=0 ;;
    # Both live states must carry their own ANSI — preserveColors is only
    # worth setting if the script actually emits an escape sequence.
    label) [[ "$out" == *ctx*   && "$out" == *$'\033['* ]] || ok=0 ;;
    alert) [[ "$out" == *CLEAR* && "$out" == *$'\033['* ]] || ok=0 ;;
  esac
  # A widget that exits non-zero renders "[Exit: N]" into the status line,
  # so the exit code is part of the contract, not an afterthought.
  [[ $status -eq 0 ]] || ok=0
  if [[ $ok -eq 1 ]]; then
    echo "  ok    $name"
    pass=$((pass + 1))
  else
    echo "  FAIL  $name (want=$want, exit=$status, output=$(printf '%q' "$out"))"
    fail=$((fail + 1))
  fi
}

expect_empty() { check "$1" "$2" empty; }   # error paths: render nothing
expect_label() { check "$1" "$2" label; }   # under threshold: plain "ctx"
expect_flag()  { check "$1" "$2" alert; }   # over threshold: red "CLEAR"

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

echo "ctx-flag.py"

if [[ ! -f "$script" ]]; then
  echo "  FAIL  script does not exist: $script"
  exit 1
fi

# --- fast path: context_window.current_usage present -----------------------
# 100k + 20k + 10k = 130k, under the 150k line.
expect_label "below threshold via current_usage" \
  "$(payload '{"input_tokens":100000,"output_tokens":9999999,"cache_creation_input_tokens":20000,"cache_read_input_tokens":10000}')"

# The absurd output_tokens above is deliberate: output must NOT count toward
# the threshold, matching used_percentage's input-only formula.

# 100k + 20k + 40k = 160k, over the line.
expect_flag "above threshold via current_usage" \
  "$(payload '{"input_tokens":100000,"output_tokens":0,"cache_creation_input_tokens":20000,"cache_read_input_tokens":40000}')"

# --- fallback: current_usage null (pre-first-call, or just after /compact) --
below="$tmp/below.jsonl"
{ usage_line 5000; usage_line 120000; } > "$below"
expect_label "below threshold via transcript fallback" \
  "$(payload 'null' "$below")"

above="$tmp/above.jsonl"
{ usage_line 5000; usage_line 175000; } > "$above"
expect_flag "above threshold via transcript fallback" \
  "$(payload 'null' "$above")"

# A subagent turn carries its own much smaller context; counting one as the
# latest would silence the flag on a long main thread.
sidechain="$tmp/sidechain.jsonl"
{ usage_line 175000; usage_line 900 true; } > "$sidechain"
expect_flag "sidechain turns do not mask a large main thread" \
  "$(payload 'null' "$sidechain")"

# --- unmeasurable context degrades to the plain label ----------------------
# An unknown context size is not an alarm. Every one of these renders exactly
# what the static custom-text label used to render, so a measurement failure
# leaves the layout untouched instead of crying wolf.
expect_label "no context_window and no transcript" '{}'
expect_label "transcript path does not exist" \
  "$(payload 'null' "$tmp/nope.jsonl")"
expect_label "json that is not an object" '[1,2,3]'

corrupt="$tmp/corrupt.jsonl"
printf '{"message":{"usage":{"input_tokens":\ngarbage\n' > "$corrupt"
expect_label "corrupt transcript lines" "$(payload 'null' "$corrupt")"

# --- unreadable stdin renders nothing at all -------------------------------
# Nothing was understood, so nothing is asserted — not even the label.
expect_empty "malformed json on stdin" 'not json at all'
expect_empty "empty stdin" ''

echo
echo "$pass passed, $fail failed"
[[ $fail -eq 0 ]]
