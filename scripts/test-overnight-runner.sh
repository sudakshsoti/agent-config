#!/usr/bin/env bash
# shellcheck disable=SC2016,SC2034
# Behaviour tests for skills/overnight-run/scripts/overnight.sh, driven from
# outside like the skill does: a temp git repo per case, stub `gh` and `omp` on
# PATH (issues, blocked-by edges and worker behaviour are set per case), the
# usage gate pinned to a fixture. Checks exit codes, commits, stashes, patches,
# handoffs, state and report fields. No network, no quota. Cases run in
# parallel. Exits 77 (skip) when jq, perl or git is unavailable.
set -uo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
runner="$repo_root/skills/overnight-run/scripts/overnight.sh"
fixtures="$repo_root/skills/overnight-run/scripts/fixtures"
for tool in jq perl git; do
  command -v "$tool" >/dev/null 2>&1 || {
    echo "$tool not on PATH"
    exit 77
  }
done

T="$(mktemp -d)"
trap 'rm -rf "$T"' EXIT
MODEL='opencode-go/deepseek-v4.1-flash:high'
DL="$(date -v-1M +%H:%M 2>/dev/null || date -d '1 minute ago' +%H:%M)"

# --- environment shared by every case ---------------------------------------

export HOME="$T/home"
mkdir -p "$HOME/.agents/skills/implement" "$HOME/.agents/skills/code-review" "$T/bin" "$T/bin-claude"
echo stub >"$HOME/.agents/skills/implement/SKILL.md"
echo stub >"$HOME/.agents/skills/code-review/SKILL.md"
cat >"$HOME/.gitconfig" <<'EOF'
[user]
	name = t
	email = t@example.test
[init]
	defaultBranch = main
[commit]
	gpgsign = false
EOF

# One gate reading for every provider: the Anthropic go.json report plus a
# clear Go report (limit ids and shape as captured live).
jq '.reports += [{provider: "opencode-go", fetchedAt: 1790533120264, limits: [
  {id: "rolling-5h", window: {id: "5h", label: "5 Hour", resetsAt: 1790536720264, durationMs: 18000000},
   amount: {used: 4, limit: 100, usedFraction: 0.04, unit: "percent"}, status: "ok"},
  {id: "weekly", window: {id: "7d", label: "Weekly", resetsAt: 1790792320264, durationMs: 604800000},
   amount: {used: 2, limit: 100, usedFraction: 0.02, unit: "percent"}, status: "ok"},
  {id: "monthly", window: {id: "monthly", label: "Monthly", resetsAt: 1790955712000},
   amount: {used: 42, limit: 100, usedFraction: 0.42, unit: "percent"}, status: "ok"}]}]' \
  "$fixtures/go.json" >"$T/gate.json"
export USAGE_GATE_JSON="$T/gate.json" USAGE_GATE_NOW_MS=1790533120264 OVERNIGHT_NOTIFY=0
unset HERDR_WORKSPACE_ID HERDR_ENV CLAUDECODE CLAUDE_CODE_ENTRYPOINT OVERNIGHT_WORKER_MODEL OVERNIGHT_PROTECTED_RE
export PATH="$T/bin:$PATH"

cat >"$T/bin/gh" <<'EOF'
#!/usr/bin/env bash
c="${OT_CASE:?}"
jqf="" field="" prev=""
for a in "$@"; do
  [[ "$prev" == --jq ]] && jqf="$a"
  [[ "$prev" == --json ]] && field="$a"
  prev="$a"
done
case "$1 $2" in
"issue view")
  jq -c "{$field: .$field}" "$c/issues/$3.json" | jq -r "$jqf"
  ;;
"api repos/{owner}/{repo}/issues/"*)
  n="$(sed -E 's#.*/issues/([0-9]+)/.*#\1#' <<<"$2")"
  { cat "$c/edges/$n.json" 2>/dev/null || echo '[]'; } | jq -c "$jqf"
  ;;
"auth status") ;;
"pr create") echo "https://example.test/pull/1" ;;
*) exit 1 ;;
esac
EOF

# The stub worker: finds the ticket and result file in the brief, logs
# "<n> <model> <attempt> <tree already dirty>", then runs behave/<n>-<attempt>.sh
# or behave/<n>.sh (sourced; may call `result <status> [notes]`, set EXIT or
# NO_RESULT). The default behaviour writes work-<n>.txt and reports done.
cat >"$T/bin/omp" <<'EOF'
#!/usr/bin/env bash
c="${OT_CASE:?}"
[[ "${1:-}" == usage ]] && exit 1
brief="${!#}"
n="$(grep -o 'ticket #[0-9]*' <<<"$brief" | head -n 1 | tr -dc 0-9)"
rf="$(grep -o '/[^ `]*\.result\.json' <<<"$brief" | head -n 1)"
model="" prev=""
for a in "$@"; do
  [[ "$prev" == --model ]] && model="$a"
  prev="$a"
done
attempt=$(($(cat "$c/count-$n" 2>/dev/null || echo 0) + 1))
echo "$attempt" >"$c/count-$n"
dirty=0
[[ -z "$(git status --porcelain)" ]] || dirty=1
echo "$n $model $attempt $dirty" >>"$c/invocations.log"
printf '%s' "$brief" >"$c/brief-$n-$attempt.md"
EXIT=0 NO_RESULT=0
result() {
  RESULT="$(jq -nc --arg s "$1" --arg n "${2:-}" \
    '{status: $s, files: [], unmet_criteria: ["criterion X"], checks: {}, routes_to_check: [], commit_subject: "do ticket", notes: $n}')"
}
echo "attempt $attempt" >"work-$n.txt"
result done
for f in "$c/behave/$n-$attempt.sh" "$c/behave/$n.sh"; do
  if [[ -f "$f" ]]; then
    # shellcheck disable=SC1090
    source "$f"
    break
  fi
done
if ((!NO_RESULT)); then printf '%s' "$RESULT" >"$rf"; fi
jq -nc --arg t "$([[ $NO_RESULT == 1 ]] && echo 'finished' || echo "$RESULT")" \
  '{type: "agent_end", messages: [{role: "assistant", content: [{type: "text", text: $t}]}]}'
exit "$EXIT"
EOF
printf '#!/bin/sh\n[ "$1" = --help ] && echo "  --max-turns N"\nexit 0\n' >"$T/bin-claude/claude"
chmod +x "$T/bin/gh" "$T/bin/omp" "$T/bin-claude/claude"

# --- per-case helpers --------------------------------------------------------

fails=0
ok() { echo "  ok    $1"; }
bad() {
  echo "  FAIL  $1"
  fails=$((fails + 1))
}
# check <label> <shell expression>; no pipefail, so `grep -q` cannot fail a
# pipeline by closing it early.
check() { if (set +o pipefail; eval "$2"); then ok "$1"; else bad "$1  [$2]"; fi; }

# mk_case <name> — sets C (case dir), R (repo) and the stub-visible OT_CASE.
mk_case() {
  C="$T/$1"
  R="$C/repo"
  export OT_CASE="$C"
  mkdir -p "$R/.github/workflows" "$R/.scratch/overnight" "$C/issues" "$C/edges" "$C/behave"
  (
    cd "$R" || exit 1
    git init -q
    echo 'on: push' >.github/workflows/ci.yml
    echo hi >README.md
    git add -A
    git commit -q -m init
    git switch -q -c overnight/test
  )
  TEST_CMD='' SETUP_CMD=''
}
issue() { jq -n --arg t "$2" --arg b "${3:-}" '{title: $t, body: $b}' >"$C/issues/$1.json"; }
# edge <issue> <blocker> — the blocker is open and in the run.
edge() {
  local f="$C/edges/$1.json"
  [[ -f "$f" ]] || echo '[]' >"$f"
  jq -c --argjson b "$2" '. + [{number: $b, state: "open"}]' "$f" >"$f.tmp" && mv "$f.tmp" "$f"
}
behave() { cat >"$C/behave/$1.sh"; } # behave <n>[-<attempt>] < script
# plan <queue-json> [model] — model defaults to none; TEST_CMD/SETUP_CMD apply.
plan() {
  jq -n --argjson q "$1" --arg m "${2-}" --arg test "$TEST_CMD" --arg setup "$SETUP_CMD" \
    '{branch: "overnight/test", queue: $q, waived: [],
      checks: {typecheck: "", build: "", lint: "", test: $test}, setup: $setup}
     + (if $m == "" then {} else {worker_model: $m} end)' >"$R/.scratch/overnight/plan.json"
}
# run_runner [args...] — sets RC; output in $C/run.out and $C/run.err.
run_runner() {
  RC=0
  (cd "$R" && bash "$runner" --headless --worker omp --deadline "$DL" "$@") >"$C/run.out" 2>"$C/run.err" || RC=$?
}
sq() { jq -r "$1" "$R/.scratch/overnight/state.json"; }
inv() { cut -d' ' -f1 "$C/invocations.log" 2>/dev/null | paste -sd' ' -; }
report() { cat "$R/.scratch/overnight/"[0-9]*.md; }
# stash_files — files held by the newest stash (tracked or index, and untracked).
stash_files() {
  git -C "$R" diff --name-only "stash@{0}^1" "stash@{0}"
  git -C "$R" ls-tree -r --name-only "stash@{0}^3" 2>/dev/null || true
}
logs="\$R/.scratch/overnight/logs"

# --- cases -------------------------------------------------------------------

case_retry_success() {
  mk_case retry_success
  issue 1 "First" $'Body\n\n## Acceptance criteria\n\n- [ ] foo works\n- [x] bar works\n\n## Notes\n\n- not a criterion'
  issue 2 "Second" "Just do it."
  plan '[1,2]' "$MODEL"
  behave 1-1 <<'B'
echo half >work-1.txt
result partial "half done"
B
  run_runner
  check "retry: run finishes" '[[ $RC == 0 ]]'
  check "retry: worker ran 1, 1 (retry), 2" '[[ "$(inv)" == "1 1 2" ]]'
  check "retry: model passed to the worker" '[[ "$(sed -n 1p "$C/invocations.log")" == "1 $MODEL 1 0" ]]'
  check "retry: first attempt started on a clean tree, retry on the patch" '[[ "$(sed -n 2p "$C/invocations.log")" == "1 $MODEL 2 1" ]]'
  check "retry: committed with the retry's work" '[[ "$(sq ".done | map(.n) | join(\",\")")" == "1,2" ]] && git -C "$R" log --format=%s | grep -qx "do ticket (#1)"'
  check "retry: retry counted in state" '[[ "$(sq ".retries[\"1\"]")" == 1 ]]'
  check "retry: attempt patch saved" 'grep -q "^+half" '"$logs"'/1-attempt1.patch'
  check "retry: handoff names reason, notes and unmet criteria" 'grep -q "worker reported partial" '"$logs"'/1.handoff.md && grep -q "half done" '"$logs"'/1.handoff.md && grep -q "criterion X" '"$logs"'/1.handoff.md'
  check "retry: handoff records the patch applied" 'grep -q "Previous patch applied" '"$logs"'/1.handoff.md'
  check "retry: attempt-1 work was stashed for the reset" 'git -C "$R" stash list | grep -q "overnight #1 attempt 1"'
  check "retry: brief points at the handoff" 'grep -q "1.handoff.md" "$C/brief-1-2.md" && ! grep -q "1.handoff.md" "$C/brief-1-1.md"'
  check "brief: Done when holds the ticket bullets only" 'grep -q -- "- \[ \] foo works" "$C/brief-1-1.md" && grep -q -- "- \[x\] bar works" "$C/brief-1-1.md" && ! grep -q "not a criterion" "$C/brief-1-1.md"'
  check "brief: no criteria falls back to the ticket wording" 'grep -q "states no separate acceptance criteria" "$C/brief-2-1.md"'
  check "report: attempts column" 'report | grep -E "^\| #1 " | grep -q "| 2 |$" && report | grep -E "^\| #2 " | grep -q "| 1 |$"'
  check "state: provider and model recorded" '[[ "$(sq .provider)" == opencode-go && "$(sq .model)" == "$MODEL" ]]'
  check "report: header shows model and gated provider" 'report | grep -q "gated provider \`opencode-go\`"'
}

case_retry_exhausted() {
  mk_case retry_exhausted
  for n in 1 2 3; do issue "$n" "T$n" "Body"; done
  edge 2 1
  plan '[1,2,3]' "$MODEL"
  behave 1 <<'B'
echo "try $attempt" >>partial-1.txt
result partial "still broken"
EXIT=3
B
  run_runner
  check "exhausted: run finishes" '[[ $RC == 0 ]]'
  check "exhausted: ticket 1 tried twice, dependent 2 never ran, 3 did" '[[ "$(inv)" == "1 1 3" ]]'
  check "exhausted: 1 failed as temporary, 2 skipped" '[[ "$(sq ".failed[0].n")" == 1 && "$(sq ".failed[0].class")" == temporary && "$(sq ".skipped[0].n")" == 2 ]]'
  check "exhausted: reason recorded" '[[ "$(sq ".failed[0].reason")" == "worker exited 3" ]]'
  check "exhausted: 3 committed" '[[ "$(sq ".done | map(.n) | join(\",\")")" == 3 ]]'
  check "exhausted: final patch holds both attempts' work" 'grep -q "try 1" '"$logs"'/1-attempt2.patch && grep -q "try 2" '"$logs"'/1-attempt2.patch'
  check "exhausted: state points at patch and handoff" '[[ -s "$(sq ".failed[0].patch")" && -s "$(sq ".failed[0].handoff")" ]]'
  check "exhausted: final stash holds the work" 'git -C "$R" stash list | grep -q "overnight #1$" && stash_files | grep -qx partial-1.txt'
  check "exhausted: report shows class and paths" 'report | grep -E "^- #1:" | grep -q "Class: temporary" && report | grep -E "^- #1:" | grep -q "Handoff"'
  check "exhausted: report attempts" 'report | grep -E "^\| #1 " | grep -q "| 2 |$"'
}

case_dependent_order() {
  mk_case dependent_order
  for n in 1 2; do issue "$n" "T$n" "Body"; done
  edge 2 1
  plan '[2,1]' "$MODEL"
  behave 1-1 <<'B'
result partial "retry me"
B
  run_runner
  check "order: retried blocker settles before its dependent" '[[ "$(inv)" == "1 1 2" ]]'
  check "order: both done" '[[ "$(sq ".done | map(.n) | join(\",\")")" == "1,2" ]]'
}

case_blocked() {
  mk_case blocked
  for n in 1 2; do issue "$n" "T$n" "Body"; done
  edge 2 1
  plan '[1,2]' "$MODEL"
  behave 1 <<'B'
result blocked "needs a design decision"
B
  run_runner
  check "blocked: never retried, dependent skipped" '[[ "$(inv)" == 1 && "$(sq ".skipped[0].n")" == 2 ]]'
  check "blocked: permanent" '[[ "$(sq ".failed[0].class")" == permanent && "$(sq ".retries // {} | length")" == 0 ]]'
  check "blocked: handoff written for a permanent failure" 'grep -q "needs a design decision" '"$logs"'/1.handoff.md'
}

case_protected() {
  mk_case protected
  for n in 1 2; do issue "$n" "T$n" "Body"; done
  plan '[1,2]' "$MODEL"
  behave 1 <<'B'
echo "SECRET=hunter2" >.env
mkdir -p keys
echo hunter2 >keys/server.pem
echo "hunter2" >>.github/workflows/ci.yml
echo work >src.txt
result done "all good"
B
  run_runner
  check "protected: permanent failure, never retried" '[[ "$(sq ".failed[0].class")" == permanent && "$(sq ".failed[0].reason")" == "protected paths touched:"* && "$(inv)" == "1 2" ]]'
  check "protected: hits listed in state" '[[ "$(sq ".failed[0].protected | sort | join(\",\")")" == ".env,.github/workflows/ci.yml,keys/server.pem" ]]'
  check "protected: nothing committed for #1" '! git -C "$R" log --format=%s | grep -q "(#1)"'
  check "protected: other work still stashed" 'stash_files | grep -qx src.txt'
  check "protected: files absent from the stash" '! stash_files | grep -Eq "\.env|\.pem|workflows"'
  check "protected: secret in no stash, patch or handoff" '! git -C "$R" grep -q hunter2 "stash@{0}^3" && ! git -C "$R" grep -q hunter2 "stash@{0}" && ! grep -rq hunter2 '"$logs"'/*.patch '"$logs"'/1.handoff.md'
  check "protected: files gone from the tree" '[[ ! -e "$R/.env" && ! -e "$R/keys/server.pem" ]] && ! git -C "$R" status --porcelain | grep -q .'
  check "protected: next ticket still ran" '[[ "$(sq ".done | map(.n) | join(\",\")")" == 2 ]]'
  check "protected: report lists the paths" 'report | grep -E "^- #1:" | grep -q "Protected paths touched:.*\.env"'
}

case_protected_allowed() {
  mk_case protected_allowed
  issue 1 "T1" "Body"
  plan '[1]' "$MODEL"
  behave 1 <<'B'
echo pub >id_rsa.pub
echo notes >notes.txt
result done
B
  run_runner
  check "protected: id_rsa.pub is allowed by default" '[[ "$(sq ".done | map(.n) | join(\",\")")" == 1 ]] && git -C "$R" ls-tree -r --name-only HEAD | grep -qx id_rsa.pub'
}

case_protected_override() {
  mk_case protected_override
  issue 1 "T1" "Body"
  plan '[1]' "$MODEL"
  behave 1 <<'B'
echo FOO=1 >.env
result done
B
  OVERNIGHT_PROTECTED_RE='^nothing-matches$' run_runner
  check "protected: OVERNIGHT_PROTECTED_RE overrides the default" '[[ "$(sq ".done | map(.n) | join(\",\")")" == 1 ]] && git -C "$R" ls-tree -r --name-only HEAD | grep -qx .env'
}

case_red_tests() {
  mk_case red_tests
  for n in 1 2; do issue "$n" "T$n" "Body"; done
  TEST_CMD='test ! -f red.marker'
  plan '[1,2]' "$MODEL"
  behave 1 <<'B'
touch red.marker
result done "tests are fine, trust me"
B
  run_runner
  check "red tests: run continues past the red ticket" '[[ $RC == 0 && "$(inv)" == "1 1 2" && "$(sq .stop_reason)" == "queue empty" ]]'
  check "red tests: ticket fails naming the check" '[[ "$(sq ".failed[0].reason")" == "checks red: test" && "$(sq ".failed[0].red_checks | join(\",\")")" == test ]]'
  check "red tests: report says which check went red" 'report | grep -E "^- #1:" | grep -q "Red checks: test"'
  check "red tests: handoff carries the red check log" 'grep -q "Red check: test" '"$logs"'/1.handoff.md'
  check "red tests: nothing committed for #1, #2 committed" '! git -C "$R" log --format=%s | grep -q "(#1)" && git -C "$R" log --format=%s | grep -q "(#2)"'
  check "red tests: gate ran the tests, the after-stash health check did not" '[[ -f '"$logs"'/2-test.log && ! -e '"$logs"'/1-after-stash-test.log ]]'
}

case_commit_refused() {
  mk_case commit_refused
  issue 1 "T1" "Body"
  plan '[1]' "$MODEL"
  printf '#!/bin/sh\necho refused >&2\nexit 1\n' >"$R/.git/hooks/pre-commit"
  chmod +x "$R/.git/hooks/pre-commit"
  run_runner
  check "commit hook refusal: permanent, no retry" '[[ "$(inv)" == 1 && "$(sq ".failed[0].class")" == permanent && "$(sq ".failed[0].reason")" == "git commit failed"* ]]'
}

case_setup_failure() {
  mk_case setup_failure
  for n in 1 2; do issue "$n" "T$n" "Body"; done
  git init -q --bare "$C/origin.git"
  git -C "$R" remote add origin "$C/origin.git"
  git -C "$R" push -q origin main
  SETUP_CMD='[ "$(basename "$PWD")" != 1 ]'
  plan '[1,2]' "$MODEL"
  run_runner --pr-per-ticket
  check "setup failure: run continues, only #2's worker ran" '[[ $RC == 0 && "$(inv)" == 2 ]]'
  check "setup failure: #1 failed as temporary after its retry" '[[ "$(sq ".failed[0].n")" == 1 && "$(sq ".failed[0].class")" == temporary && "$(sq ".failed[0].reason")" == "setup failed: see"* && "$(sq ".retries[\"1\"]")" == 1 ]]'
  check "setup failure: #2 committed with a draft PR" '[[ "$(sq ".done[0].n")" == 2 && "$(sq ".done[0].pr")" == https://* ]]'
  check "setup failure: run not stopped by it" '[[ "$(sq .stop_reason)" == "queue empty" ]]'
}

case_matrix() {
  mk_case matrix
  issue 1 "Has criteria" $'## Done when\n- [ ] it works'
  issue 2 "Vague" "no bullets here"
  local dry="--dry-run"
  plan '[1,2]' "$MODEL"
  run_runner $dry
  check "matrix: DeepSeek gates the Go provider" '[[ $RC == 0 ]] && grep -q "gate provider  opencode-go" "$C/run.out" && grep -q "model       $MODEL" "$C/run.out" && grep -Eq "^  gate +exit [0-9]+ — .*opencode-go" "$C/run.out"'
  check "matrix: dry run shows Go thresholds" 'grep -q "monthly" "$C/run.out" && grep -q "5h sleep" "$C/run.out"'
  check "matrix: dry run lists tickets without criteria" 'grep -q "no acceptance criteria: #2$" "$C/run.out"'
  plan '[1]' ''
  OVERNIGHT_WORKER_MODEL=anthropic/claude-sonnet-5-5 run_runner $dry
  check "matrix: omp + anthropic model gates Anthropic (env beats plan)" '[[ $RC == 0 ]] && grep -q "gate provider  anthropic" "$C/run.out" && grep -q "model       anthropic/claude-sonnet-5-5" "$C/run.out"'
  plan '[1]' "$MODEL"
  OVERNIGHT_WORKER_MODEL=anthropic/claude-sonnet-5-5 run_runner $dry
  check "matrix: env override beats the plan model" 'grep -q "gate provider  anthropic" "$C/run.out"'
  plan '[1]' ''
  run_runner $dry
  check "matrix: omp with no model is refused" '[[ $RC != 0 ]] && grep -q "worker_model" "$C/run.err"'
  plan '[1]' 'deepseek-v4.1-flash'
  run_runner $dry
  check "matrix: omp model without provider prefix is refused" '[[ $RC != 0 ]] && grep -q "provider/model" "$C/run.err"'
  plan '[1]' "$MODEL"
  PATH="$T/bin-claude:$PATH" run_runner --worker claude $dry
  check "matrix: claude + DeepSeek refused, naming both" '[[ $RC != 0 ]] && grep -q "claude" "$C/run.err" && grep -q "$MODEL" "$C/run.err"'
  plan '[1]' ''
  PATH="$T/bin-claude:$PATH" run_runner --worker claude $dry
  check "matrix: claude with no model gates Anthropic and passes no --model" '[[ $RC == 0 ]] && grep -q "gate provider  anthropic" "$C/run.out" && ! grep -q -- "--model" "$C/run.out"'
  plan '[1]' 'anthropic/claude-sonnet-5-5'
  PATH="$T/bin-claude:$PATH" run_runner --worker claude $dry
  check "matrix: claude with an anthropic model is allowed" '[[ $RC == 0 ]] && grep -q "gate provider  anthropic" "$C/run.out"'
}

case_resume_old_state() {
  mk_case resume_old_state
  for n in 1 2; do issue "$n" "T$n" "Body"; done
  plan '[1,2]' "$MODEL"
  run_runner --max-tickets 1
  check "resume: first run stops at the cap" '[[ "$(sq .stop_reason)" == "max tickets (1)" && "$(sq ".done | length")" == 1 ]]'
  # A state file from before this change: no retries, no provider, no model_arg;
  # the plan no longer names a model, so the state's model carries on.
  local s="$R/.scratch/overnight/state.json"
  jq 'del(.retries, .provider, .model_arg)' "$s" >"$s.tmp" && mv "$s.tmp" "$s"
  plan '[1,2]' ''
  behave 2-1 <<'B'
result partial "flaky"
B
  run_runner --resume
  check "resume: state without retries continues and retries" '[[ $RC == 0 && "$(inv)" == "1 2 2" && "$(sq ".done | map(.n) | join(\",\")")" == "1,2" && "$(sq ".retries[\"2\"]")" == 1 ]]'
  check "resume: model remembered from state" '[[ "$(sed -n 3p "$C/invocations.log")" == "2 $MODEL 2 1" && "$(sq .provider)" == opencode-go ]]'
}

case_resume_no_model() {
  mk_case resume_no_model
  issue 1 "T1" "Body"
  issue 2 "T2" "Body"
  plan '[1,2]' "$MODEL"
  run_runner --max-tickets 1
  local s="$R/.scratch/overnight/state.json"
  jq 'del(.model, .model_arg)' "$s" >"$s.tmp" && mv "$s.tmp" "$s"
  plan '[1,2]' ''
  run_runner --resume
  check "resume: no model anywhere is refused, naming worker_model" '[[ $RC != 0 ]] && grep -q "worker_model" "$C/run.err"'
}

case_resume_interrupted() {
  mk_case resume_interrupted
  for n in 1 2; do issue "$n" "T$n" "Body"; done
  plan '[1,2]' "$MODEL"
  run_runner --max-tickets 1
  # An interrupted #2 left work behind, including a protected file.
  local s="$R/.scratch/overnight/state.json"
  jq '.current = 2' "$s" >"$s.tmp" && mv "$s.tmp" "$s"
  echo half >"$R/half.txt"
  echo SECRET=1 >"$R/.env"
  run_runner --resume
  check "resume: interrupted work is stashed without protected files" \
    '[[ $RC == 0 ]] && git -C "$R" stash list | grep -q "overnight #2 interrupted" && idx="$(git -C "$R" stash list | grep -n "overnight #2 interrupted" | cut -d: -f1)" && files="$(git -C "$R" ls-tree -r --name-only "stash@{$((idx - 1))}^3")" && grep -qx half.txt <<<"$files" && ! grep -qx .env <<<"$files"'
}

case_notify() {
  mk_case notify
  issue 1 "T1" "Body"
  plan '[1]' "$MODEL"
  mkdir -p "$C/bin"
  printf '#!/bin/sh\necho "$@" >>"%s/notify.log"\nexit 1\n' "$C" >"$C/bin/osascript"
  chmod +x "$C/bin/osascript"
  PATH="$C/bin:$PATH" OVERNIGHT_NOTIFY=1 run_runner
  check "notify: fires on stop; a failing osascript never fails the run" '[[ $RC == 0 ]] && grep -q "queue empty" "$C/notify.log"'
  rm -f "$C/notify.log" "$R/.scratch/overnight/state.json"
  git -C "$R" reset -q --hard main
  PATH="$C/bin:$PATH" OVERNIGHT_NOTIFY=0 run_runner
  check "notify: OVERNIGHT_NOTIFY=0 silences it" '[[ $RC == 0 && ! -e "$C/notify.log" ]]'
}

# --- run ----------------------------------------------------------------------

cases=(retry_success retry_exhausted dependent_order blocked protected protected_allowed
  protected_override red_tests commit_refused setup_failure matrix resume_old_state
  resume_no_model resume_interrupted notify)
for c in "${cases[@]}"; do
  (
    "case_$c"
    exit $((fails > 0))
  ) >"$T/out-$c" 2>&1 &
done
wait
total_fail=0
for c in "${cases[@]}"; do
  echo "$c"
  cat "$T/out-$c"
  grep -q '^  FAIL' "$T/out-$c" && total_fail=$((total_fail + 1))
done
if ((total_fail)); then
  echo "$total_fail case(s) failed"
  for c in "${cases[@]}"; do
    if grep -q '^  FAIL' "$T/out-$c"; then
      echo "--- $c: run.err (tail)"
      tail -n 15 "$T/$c/run.err" 2>/dev/null
    fi
  done
  exit 1
fi
