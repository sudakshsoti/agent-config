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

echo "ctx-flag.py"

if [[ ! -f "$script" ]]; then
  echo "  FAIL  script does not exist: $script"
  exit 1
fi

# --- fast path: context_window.current_usage present -----------------------
# input_tokens absorbs the remainder, so the three fields still sum to
# $under -- 30k under the line -- rather than landing it all in one field.
expect_label "below threshold via current_usage" "$(payload "$usage_below")"

# The absurd output_tokens above is deliberate: output must NOT count toward
# the threshold, matching used_percentage's input-only formula.

# Same split, only the total moves: $over -- 10k over the line.
expect_flag "above threshold via current_usage" "$(payload "$usage_above")"

# --- fallback: current_usage null (pre-first-call, or just after /compact) --
below="$tmp/below.jsonl"
{ usage_line 5000; usage_line "$under"; } > "$below"
expect_label "below threshold via transcript fallback" \
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
echo "layout command (ccstatusline-settings.json, widget 11)"

# Everything above calls ctx-flag.py directly; nothing tests the *string
# ccstatusline actually runs*. ccstatusline types a widget's `type` as a bare
# string rather than an enum, so a wrong value renders nothing at all, and a
# failing custom-command renders "[Exit: N]" straight into the status line --
# a config-level mistake here would slip past every test above it. Pull the
# real commandPath for widget "11" out of the layout and run it verbatim
# under /bin/sh -c, since that's what ccstatusline's execSync uses, and it's
# what makes the `||` fallback in the string meaningful.
#
# commandPath is an absolute path baked to this checkout. If this checkout is
# ever moved, only one of the three tests below is guaranteed to fail: the
# fallback renders identically to success (same grey "ctx"), so the
# below-threshold case and the missing-script case both pass vacuously --
# they observe the fallback firing and mistake it for the real script running.
# Only the above-threshold case is safe, because the fallback can never
# produce red "CLEAR". The guard just below turns that silent, misleading
# 2-pass-1-fail into a named failure instead of relying on someone noticing
# the group didn't go fully red.
cmd=$(jq -r '.lines[1][] | select(.id=="11") | .commandPath' "$repo_root/ccstatusline-settings.json")
fail_before_layout=$fail

# Precondition for the missing-script case below: it works by substituting
# $missing for $script inside $cmd, which only rewrites anything if $script
# actually appears in $cmd. A moved checkout means commandPath no longer
# contains $script, so the sed match-and-replace becomes a no-op, broken_cmd
# equals cmd, and that case silently re-runs the already-broken real command
# instead of testing the substitution it claims to. Name that condition
# directly rather than letting it masquerade as a pass.
if [[ "$cmd" != *"$script"* ]]; then
  echo "  FAIL  layout commandPath does not point at $script"
  echo "        commandPath: $cmd"
  echo "        Did this checkout move? The live status line is broken too;"
  echo "        run ./install.sh --force-statusline after fixing the path."
  fail=$((fail+1))
fi

check "layout command: below threshold renders ctx" "$(payload "$usage_below")" label /bin/sh -c "$cmd"

check "layout command: above threshold renders CLEAR" "$(payload "$usage_above")" alert /bin/sh -c "$cmd"

# Regression test for the `|| printf` fallback Task 1 added to commandPath:
# rewrite the .py path to a file that doesn't exist, so python3 fails to
# execute it and the fallback fires. Substitute into a path under $tmp --
# never touch the real script, since a crashed test run must not leave the
# live status line pointed at a missing file. '#' as the sed delimiter since
# the paths themselves contain '/'.
missing="$tmp/no-such-ctx-flag.py"
broken_cmd=$(printf '%s' "$cmd" | sed "s#$script#$missing#")
check "layout command: missing script falls back to ctx" "$(payload "$usage_below")" label /bin/sh -c "$broken_cmd"

if [[ $fail -gt $fail_before_layout ]]; then
  echo "  NOTE  commandPath is an absolute path baked to this checkout ($repo_root)."
  echo "        If this checkout was moved or renamed, that's the likely cause of the"
  echo "        failure(s) above -- and it means the live status line is broken too."
fi

echo
echo "$pass passed, $fail failed"
[[ $fail -eq 0 ]]
