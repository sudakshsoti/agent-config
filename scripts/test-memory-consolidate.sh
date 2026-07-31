#!/usr/bin/env bash
# test-memory-consolidate.sh — behaviour tests for hooks/memory-consolidate.py
#
# Same reason test-context-size.sh exists: this hook fails SILENTLY by design. A
# broken one and a quiet one are indistinguishable from the outside, and this
# one has side effects (a background process, a lock, a vault commit) rather
# than a visible widget, so "it printed nothing" proves even less than usual.
#
# Nothing here touches the real vault or the real `claude` binary. Both are
# redirected by env var:
#   MEMORY_CONSOLIDATE_VAULT      -> a throwaway git repo under $tmp
#   MEMORY_CONSOLIDATE_CLAUDE_BIN -> a stub that records its argv and exits
#   MEMORY_CONSOLIDATE_STATE_DIR  -> $tmp, so lock/stamp/log never hit /tmp
# So the headless `claude -p` call is NEVER exercised end to end here. What is
# proven is the gating, the spawn, the exclusion and the silence -- not that
# the model does the right thing once spawned.
#
#   ./scripts/test-memory-consolidate.sh
set -uo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
hook="$repo_root/hooks/memory-consolidate.py"
tmp="$(mktemp -d)"
trap 'pkill -f "memory-consolidate.py --run" >/dev/null 2>&1; rm -rf "$tmp"' EXIT

pass=0
fail=0

ok()   { echo "  ok    $1"; pass=$((pass + 1)); }
bad()  { echo "  FAIL  $1"; echo "        $2"; fail=$((fail + 1)); }

# Throwaway vault: the hook refuses to fire unless <vault>/.git exists, and the
# stub never writes to it, but it must look real enough to pass that check.
vault="$tmp/vault"
mkdir -p "$vault"
git -C "$vault" init -q 2>/dev/null

# Stub `claude`: records the fact and the argv it was handed, then lingers a
# few seconds so the "hook returns immediately" and "lock is held for the
# worker's lifetime" assertions have something to observe.
stub="$tmp/claude-stub"
# One line per invocation in the counter file (the prompt is multi-line, so
# counting lines of argv would count newlines in the prompt, not invocations),
# and the argv itself in a separate file.
cat > "$stub" <<EOF
#!/bin/sh
echo invoked >> "$tmp/claude-invocations"
printf '%s\n' "\$*" > "$tmp/claude-argv"
sleep 4
echo NOTHING_DURABLE
EOF
chmod +x "$stub"

export MEMORY_CONSOLIDATE_VAULT="$vault"
export MEMORY_CONSOLIDATE_CLAUDE_BIN="$stub"
export MEMORY_CONSOLIDATE_STATE_DIR="$tmp"

lock="$tmp/claude-memory-consolidate.lock"

reset_state() {
  pkill -f "memory-consolidate.py --run" >/dev/null 2>&1
  rm -f "$lock" "$tmp"/claude-memory-consolidate-*.stamp "$tmp/claude-invocations" "$tmp/claude-argv"
  sleep 0.2
}

invocations() { [[ -f "$tmp/claude-invocations" ]] && wc -l < "$tmp/claude-invocations" | tr -d ' ' || echo 0; }

# --- fixtures --------------------------------------------------------------

# One human turn as the transcript actually stores it: type "user", content a
# plain string. Tool results are also type "user", hence the other shapes below.
human_turn() {
  python3 - "$1" <<'PY'
import json, sys
print(json.dumps({"type": "user", "isSidechain": False,
                  "message": {"role": "user", "content": sys.argv[1]}}))
PY
}

transcript() {  # transcript <path> <turn-count> [extra-text]
  local path="$1" n="$2" extra="${3:-}"
  : > "$path"
  local i
  for ((i = 0; i < n; i++)); do
    human_turn "Turn $i. $(printf 'x%.0s' {1..200}) ${extra}" >> "$path"
    # A tool result and a sidechain turn, which must NOT count as human turns.
    printf '{"type":"user","isSidechain":false,"message":{"content":[{"type":"tool_result","tool_use_id":"t","content":"out"}]}}\n' >> "$path"
    printf '{"type":"user","isSidechain":true,"message":{"content":"subagent chatter"}}\n' >> "$path"
    printf '{"type":"assistant","message":{"usage":{"input_tokens":100}}}\n' >> "$path"
  done
}

payload() {  # payload <transcript> [reason]
  jq -nc --arg t "$1" --arg r "${2:-other}" \
    '{session_id:"test-session", hook_event_name:"SessionEnd", cwd:"/tmp/somewhere",
      transcript_path:$t, reason:$r}'
}

# run_hook <stdin> -> sets $out, $err, $status, $elapsed_ms
run_hook() {
  local start end
  start=$(python3 -c 'import time;print(int(time.time()*1000))')
  out=$(printf '%s' "$1" | python3 "$hook" 2>"$tmp/stderr")
  status=$?
  end=$(python3 -c 'import time;print(int(time.time()*1000))')
  elapsed_ms=$((end - start))
  err=$(cat "$tmp/stderr")
}

# silent_and_quiet <name> <stdin> -- exits 0, says nothing, spawns nothing
silent_and_quiet() {
  reset_state
  run_hook "$2"
  local why=""
  [[ $status -eq 0 ]] || why="exit=$status"
  [[ -z "$out" ]] || why="$why stdout=$(printf '%q' "$out")"
  [[ -z "$err" ]] || why="$why stderr=$(printf '%q' "$err")"
  sleep 0.5
  [[ ! -f "$lock" ]] || why="$why lock was created"
  [[ "$(invocations)" == "0" ]] || why="$why claude was invoked"
  if [[ -z "$why" ]]; then ok "$1"; else bad "$1" "$why"; fi
}

echo "memory-consolidate.py"

if [[ ! -f "$hook" ]]; then
  echo "  FAIL  hook does not exist: $hook"
  exit 1
fi

# --- the silent-failure contract -------------------------------------------
# Every one of these is a malformed or unusable input. The contract is exit 0,
# no output on either stream, and no side effect at all.

silent_and_quiet "garbage on stdin"            'not json at all{{{'
silent_and_quiet "empty stdin"                 ''
silent_and_quiet "json that is not an object"  '[1,2,3]'
silent_and_quiet "empty object, no transcript" '{}'
silent_and_quiet "transcript path missing"     "$(payload "$tmp/does-not-exist.jsonl")"
silent_and_quiet "transcript_path is null"     '{"hook_event_name":"SessionEnd","transcript_path":null,"reason":"other"}'
silent_and_quiet "reason is a nonsense type"   '{"transcript_path":"/etc/hosts","reason":{"weird":true}}'

# A transcript that is not JSONL at all, and one that is binary noise. The
# per-line parse swallows both, so the gate simply counts zero human turns.
printf 'this is not jsonl\nneither is this\n' > "$tmp/notjsonl.jsonl"
silent_and_quiet "transcript is not JSONL" "$(payload "$tmp/notjsonl.jsonl")"
head -c 5000 /dev/urandom > "$tmp/binary.jsonl"
silent_and_quiet "transcript is binary noise" "$(payload "$tmp/binary.jsonl")"

# A deliberately broken hook must still exit 0 and block nothing. Simulated by
# breaking the import it depends on: a copy of the hook in a directory with no
# context_size.py next to it, which is what a half-installed checkout looks
# like. This is the closest thing to "the hook is broken" that can be staged
# without editing the real file.
mkdir -p "$tmp/broken"
cp "$hook" "$tmp/broken/memory-consolidate.py"
big="$tmp/passing.jsonl"
transcript "$big" 8
brk_out=$(printf '%s' "$(payload "$big")" | python3 "$tmp/broken/memory-consolidate.py" 2>"$tmp/brk_err")
brk_status=$?
brk_err=$(cat "$tmp/brk_err")
if [[ $brk_status -eq 0 && -z "$brk_out" && -z "$brk_err" ]]; then
  ok "deliberately broken hook (missing context_size) still exits 0, silently"
else
  bad "deliberately broken hook (missing context_size) still exits 0, silently" \
      "exit=$brk_status stdout=$(printf '%q' "$brk_out") stderr=$(printf '%q' "$brk_err")"
fi

echo
echo "the gate"

# --- below the gate: no spawn ----------------------------------------------
short="$tmp/short.jsonl"
transcript "$short" 2                      # under MIN_HUMAN_TURNS
silent_and_quiet "too few human turns does not fire" "$(payload "$short")"

terse="$tmp/terse.jsonl"
: > "$terse"
for i in 1 2 3 4 5 6; do human_turn "ok" >> "$terse"; done
silent_and_quiet "enough turns but too little said does not fire" "$(payload "$terse")"

# Only tool results and sidechain turns: a session where the human said
# nothing. These are type "user" too, which is exactly the trap.
noise="$tmp/noise.jsonl"
: > "$noise"
for i in $(seq 1 40); do
  printf '{"type":"user","isSidechain":false,"message":{"content":[{"type":"tool_result","tool_use_id":"t","content":"lots and lots of output text here"}]}}\n' >> "$noise"
  printf '{"type":"user","isSidechain":true,"message":{"content":"a very long subagent message that should not count toward the human total at all"}}\n' >> "$noise"
done
silent_and_quiet "tool results and sidechain turns are not human turns" "$(payload "$noise")"

# Slash-command envelopes arrive as pseudo-user messages; they are not a human
# typing either.
cmds="$tmp/cmds.jsonl"
: > "$cmds"
for i in 1 2 3 4 5 6 7 8; do
  human_turn "<command-name>/status</command-name> $(printf 'y%.0s' {1..200})" >> "$cmds"
done
silent_and_quiet "slash-command envelopes are not human turns" "$(payload "$cmds")"

# --- reasons we must not act on --------------------------------------------
silent_and_quiet "reason=prompt_input_exit (a finished headless run) does not fire" \
  "$(payload "$big" prompt_input_exit)"
silent_and_quiet "reason=resume (a suspend, not an end) does not fire" \
  "$(payload "$big" resume)"
silent_and_quiet "reason=logout does not fire" "$(payload "$big" logout)"

# --- the recursion guard ---------------------------------------------------
reset_state
CLAUDE_MEMORY_CONSOLIDATE=1 python3 "$hook" <<< "$(payload "$big")" >"$tmp/g_out" 2>"$tmp/g_err"
g_status=$?
sleep 0.5
if [[ $g_status -eq 0 && ! -s "$tmp/g_out" && ! -s "$tmp/g_err" && ! -f "$lock" ]]; then
  ok "CLAUDE_MEMORY_CONSOLIDATE=1 stands the hook down (recursion guard)"
else
  bad "CLAUDE_MEMORY_CONSOLIDATE=1 stands the hook down (recursion guard)" \
      "exit=$g_status lock=$([[ -f "$lock" ]] && echo yes || echo no)"
fi

# --- an explicit /remember suppresses the automatic write ------------------
did_remember="$tmp/remembered.jsonl"
transcript "$did_remember" 8 "/remember this bit"
silent_and_quiet "a session that already ran /remember does not double-write" \
  "$(payload "$did_remember")"

echo
echo "the spawn"

# --- above the gate: spawns, and returns without waiting -------------------
reset_state
run_hook "$(payload "$big")"
why=""
[[ $status -eq 0 ]] || why="exit=$status"
[[ -z "$out" ]] || why="$why stdout=$(printf '%q' "$out")"
[[ -z "$err" ]] || why="$why stderr=$(printf '%q' "$err")"
# The stub sleeps 4s. Anything near that means the hook waited on the worker.
[[ $elapsed_ms -lt 2000 ]] || why="$why hook took ${elapsed_ms}ms (stub sleeps 4000ms)"
[[ -f "$lock" ]] || why="$why no lock file"
if [[ -z "$why" ]]; then
  ok "above the gate: spawns, stays silent, returns in ${elapsed_ms}ms without waiting"
else
  bad "above the gate: spawns, stays silent, returns without waiting" "$why"
fi

# The spawned worker really does reach the (stubbed) headless call.
spawned=0
for i in $(seq 1 40); do
  [[ "$(invocations)" != "0" ]] && { spawned=1; break; }
  sleep 0.25
done
if [[ $spawned -eq 1 ]]; then
  ok "the detached worker actually invokes the claude binary"
else
  bad "the detached worker actually invokes the claude binary" \
      "no invocation recorded after 10s; log: $(cat "$tmp/claude-memory-consolidate.log" 2>/dev/null)"
fi

# ...and hands it a headless, bounded, vault-scoped command line.
argv=" $(cat "$tmp/claude-argv" 2>/dev/null) "
argv_why=""
[[ "$argv" == *" -p "* ]]              || argv_why="$argv_why no -p;"
[[ "$argv" == *"--max-turns"* ]]       || argv_why="$argv_why no --max-turns;"
[[ "$argv" == *"$vault"* ]]            || argv_why="$argv_why vault not referenced;"
[[ "$argv" == *"NOTHING_DURABLE"* ]]   || argv_why="$argv_why prompt lacks the no-op escape hatch;"
[[ "$argv" != *"--dangerously-skip-permissions"* ]] || argv_why="$argv_why skips permissions;"
if [[ -z "$argv_why" ]]; then
  ok "the headless command line is bounded and scoped to the vault"
else
  bad "the headless command line is bounded and scoped to the vault" "$argv_why"
fi

echo
echo "mutual exclusion"

# --- a second session ending while the first is consolidating --------------
# The first spawn above is still running (stub sleeps 4s) and still holds the
# lock. A second, different session must not start a second worker.
second="$tmp/second.jsonl"
transcript "$second" 9
run_hook "$(payload "$second")"
sleep 1
if [[ $status -eq 0 && -z "$out" && "$(invocations)" == "1" ]]; then
  ok "a second session ending mid-consolidation does not double-write"
else
  bad "a second session ending mid-consolidation does not double-write" \
      "exit=$status invocations=$(invocations) (want 1)"
fi

# --- the same session, consolidated twice ----------------------------------
# SessionEnd fires again on quit after a /clear, on the same transcript. The
# stamp means only NEW material can trigger a second run.
reset_state
run_hook "$(payload "$big")"
sleep 1
first_inv=$(invocations)
pkill -f "memory-consolidate.py --run" >/dev/null 2>&1   # let the lock go stale
rm -f "$lock"
run_hook "$(payload "$big")"
sleep 1
if [[ "$first_inv" == "1" && "$(invocations)" == "1" ]]; then
  ok "the same transcript is not consolidated twice (stamp)"
else
  bad "the same transcript is not consolidated twice (stamp)" \
      "invocations after first=$first_inv, after second=$(invocations) (want 1 and 1)"
fi

# ...but growth past the stamp is new material and does fire again.
transcript "$tmp/grown.jsonl" 8
cat "$tmp/grown.jsonl" >> "$big"     # +8 human turns on the same transcript
rm -f "$lock"
pkill -f "memory-consolidate.py --run" >/dev/null 2>&1
run_hook "$(payload "$big")"
sleep 1
if [[ "$(invocations)" == "2" ]]; then
  ok "new turns past the stamp do trigger a fresh consolidation"
else
  bad "new turns past the stamp do trigger a fresh consolidation" \
      "invocations=$(invocations) (want 2)"
fi

# --- a lock left behind by a crashed worker --------------------------------
# The failure mode a naive lock has: one crash and the hook never fires again.
reset_state
python3 - "$lock" <<'PY'
import json, sys, time
# PID 999999 is not a running process; the lock names a corpse.
json.dump({"pid": 999999, "at": time.time()}, open(sys.argv[1], "w"))
PY
fresh="$tmp/fresh.jsonl"
transcript "$fresh" 8
run_hook "$(payload "$fresh")"
sleep 1
if [[ "$(invocations)" == "1" ]]; then
  ok "a stale lock from a dead worker is stolen, not obeyed forever"
else
  bad "a stale lock from a dead worker is stolen, not obeyed forever" \
      "invocations=$(invocations) (want 1)"
fi

# A lock held by a LIVE process is obeyed, even without our own worker running.
reset_state
sleep 30 &
live_pid=$!
disown "$live_pid" 2>/dev/null   # otherwise bash prints "Terminated" when we kill it
python3 - "$lock" "$live_pid" <<'PY'
import json, sys, time
json.dump({"pid": int(sys.argv[2]), "at": time.time()}, open(sys.argv[1], "w"))
PY
another="$tmp/another.jsonl"
transcript "$another" 8
run_hook "$(payload "$another")"
sleep 1
live_ok=$([[ "$(invocations)" == "0" ]] && echo 1 || echo 0)
kill "$live_pid" 2>/dev/null
if [[ "$live_ok" == "1" ]]; then
  ok "a lock held by a live process is obeyed"
else
  bad "a lock held by a live process is obeyed" "invocations=$(invocations) (want 0)"
fi

echo
echo "settings.json wiring"

# The hook can be perfect and still never run. settings.json invokes it by an
# absolute path baked to this checkout, so a moved repo silently disables it --
# invisibly, since a disabled hook and a quiet one look identical.
cmd=$(jq -r '.hooks.SessionEnd[]?.hooks[]? | select(.command | test("memory-consolidate")) | .command' \
      "$repo_root/settings.json" 2>/dev/null)
if [[ -n "$cmd" ]]; then
  ok "settings.json SessionEnd wires the hook"
else
  bad "settings.json SessionEnd wires the hook" "no SessionEnd entry mentions memory-consolidate"
fi

# The command is a shell string with "$HOME" unexpanded, so resolve it the way
# the shell would. -f follows symlinks, so a dangling ~/.claude/hooks link --
# what a moved checkout leaves behind -- fails here rather than silently
# disabling the hook.
wired=$(python3 -c 'import os,shlex,sys; p=shlex.split(sys.argv[1]); print(os.path.expandvars(p[-1]) if p else "")' "$cmd" 2>/dev/null)
if [[ -n "$wired" && -f "$wired" ]]; then
  ok "the wired path resolves to a real file: $wired"
else
  bad "the wired path resolves to a real file" \
      "settings.json points at '$wired', which is not a file. Did this checkout move? Re-run ./install.sh"
fi

# The other SessionEnd entries are managed by other tooling. Losing one is a
# silent breakage of somebody else's integration, so assert they survived.
others=$(jq '[.hooks.SessionEnd[]?.hooks[]? | select(.command | test("SUPERSET_HOME_DIR") or test("supacode-managed-hook"))] | length' \
         "$repo_root/settings.json" 2>/dev/null)
if [[ "$others" == "2" ]]; then
  ok "the pre-existing SessionEnd hooks (superset, supacode) are intact"
else
  bad "the pre-existing SessionEnd hooks (superset, supacode) are intact" \
      "found $others of 2"
fi

# And the live copy must match, since settings.json here is a copy, not a symlink.
live="$HOME/.claude/settings.json"
live_cmd=$(jq -r '.hooks.SessionEnd[]?.hooks[]? | select(.command | test("memory-consolidate")) | .command' \
           "$live" 2>/dev/null)
if [[ "$live_cmd" == "$cmd" && -n "$live_cmd" ]]; then
  ok "~/.claude/settings.json carries the same wiring"
else
  bad "~/.claude/settings.json carries the same wiring" \
      "live='$live_cmd' repo='$cmd' — settings.json is a copy; update both (see sync.sh)"
fi

echo
echo "$pass passed, $fail failed"
[[ $fail -eq 0 ]]
