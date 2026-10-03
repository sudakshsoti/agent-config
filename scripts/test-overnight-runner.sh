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
unset HERDR_WORKSPACE_ID HERDR_ENV CLAUDECODE CLAUDE_CODE_ENTRYPOINT OVERNIGHT_WORKER_MODEL OVERNIGHT_PROTECTED_RE OT_TASK_ROLE OT_MODELS_FAIL
# The stub `omp models` catalogue, and the runner path for stubs that call back in.
echo '{"models":[{"selector":"opencode-go/deepseek-v4.1-flash"},{"selector":"anthropic/claude-sonnet-5-5"},{"selector":"openrouter/~anthropic/claude-opus-latest"}]}' >"$T/models.json"
export OT_MODELS="$T/models.json" OT_RUNNER="$runner"
export PATH="$T/bin:$PATH"

cat >"$T/bin/gh" <<'EOF'
#!/usr/bin/env bash
c="${OT_CASE:?}"
echo "$*" | tr '\n' ' ' >>"$c/gh.calls"
echo >>"$c/gh.calls"
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
"auth status") [[ ! -f "$c/gh-unauth" ]] ;;
"repo view") cat "$c/perm" 2>/dev/null || echo WRITE ;;
"pr create")
  head="" base="" title="" body="" prev=""
  for a in "$@"; do
    case "$prev" in
    --head) head="$a" ;;
    --base) base="$a" ;;
    --title) title="$a" ;;
    --body) body="$a" ;;
    esac
    prev="$a"
  done
  if [[ -f "$c/pr-fail" ]]; then
    echo "GraphQL: simulated failure" >&2
    exit 1
  fi
  # Like GitHub: both the head and the base must exist on the remote.
  for ref in "$head" "$base"; do
    git ls-remote --exit-code --heads origin "$ref" >/dev/null || {
      echo "branch $ref is not on the remote" >&2
      exit 1
    }
  done
  mkdir -p "$c/prs"
  id=$(($(ls "$c/prs" | wc -l) + 1))
  jq -n --arg head "$head" --arg base "$base" --arg title "$title" --arg body "$body" \
    '{head: $head, base: $base, title: $title, body: $body}' >"$c/prs/$id.json"
  echo "https://example.test/pull/$id"
  ;;
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
case "${1:-}" in
usage) exit 1 ;;
models)
  [[ "${OT_MODELS_FAIL:-0}" == 1 ]] && exit 1
  cat "$OT_MODELS"
  exit 0
  ;;
config)
  jq -nc --arg r "${OT_TASK_ROLE-anthropic/claude-sonnet-5-5:medium}" \
    '{key: "modelRoles", value: (if $r == "" then {} else {task: $r} end)}'
  exit 0
  ;;
esac
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
printf '#!/bin/sh\n[ "$1" = --help ] && printf "  --max-turns N\\n  --effort <level>\\n"\nexit 0\n' >"$T/bin-claude/claude"
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

# mk_case <name> — sets C (case dir), R (repo, with a bare origin that holds
# main) and the stub-visible OT_CASE.
mk_case() {
  C="$T/$1"
  R="$C/repo"
  export OT_CASE="$C"
  mkdir -p "$R/.github/workflows" "$R/.scratch/overnight" "$C/issues" "$C/edges" "$C/behave"
  git init -q --bare "$C/origin.git"
  (
    cd "$R" || exit 1
    git init -q
    echo 'on: push' >.github/workflows/ci.yml
    echo hi >README.md
    git add -A
    git commit -q -m init
    git remote add origin "$C/origin.git"
    git push -q origin main
  )
  TEST_CMD=''
}
issue() { jq -n --arg t "$2" --arg b "${3:-}" '{title: $t, body: $b}' >"$C/issues/$1.json"; }
# edge <issue> <blocker> — the blocker is open and in the run.
edge() {
  local f="$C/edges/$1.json"
  [[ -f "$f" ]] || echo '[]' >"$f"
  jq -c --argjson b "$2" '. + [{number: $b, state: "open"}]' "$f" >"$f.tmp" && mv "$f.tmp" "$f"
}
behave() { cat >"$C/behave/$1.sh"; } # behave <n>[-<attempt>] < script
# plan <queue-json> [model] — model defaults to none; TEST_CMD applies.
plan() {
  jq -n --argjson q "$1" --arg m "${2-}" --arg test "$TEST_CMD" \
    '{prefix: "overnight/test", base: "main", queue: $q, waived: [],
      checks: {typecheck: "", build: "", lint: "", test: $test}}
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
# subjects — every commit subject in the repo, on any branch.
subjects() { git -C "$R" log --all --format=%s; }
# origin_ref <branch> — its sha on the bare origin, empty when absent.
origin_ref() { git --git-dir="$C/origin.git" rev-parse -q --verify "refs/heads/$1" || true; }
# pr_field <head-branch> <field> — a field of the PR the stub gh recorded.
pr_field() { jq -sr --arg h "$1" --arg f "$2" '[.[] | select(.head == $h)][0][$f] // empty' "$C"/prs/*.json 2>/dev/null; }
npr() { find "$C/prs" -type f 2>/dev/null | wc -l | tr -d ' '; }
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
  check "retry: committed with the retry's work" '[[ "$(sq ".done | map(.n) | join(\",\")")" == "1,2" ]] && subjects | grep -qx "do ticket (#1)"'
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
  check "protected: nothing committed for #1" '! subjects | grep -q "(#1)"'
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
  check "protected: id_rsa.pub is allowed by default" '[[ "$(sq ".done | map(.n) | join(\",\")")" == 1 ]] && git -C "$R" ls-tree -r --name-only overnight/test/1 | grep -qx id_rsa.pub'
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
  check "protected: OVERNIGHT_PROTECTED_RE overrides the default" '[[ "$(sq ".done | map(.n) | join(\",\")")" == 1 ]] && git -C "$R" ls-tree -r --name-only overnight/test/1 | grep -qx .env'
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
  check "red tests: nothing committed for #1, #2 committed" '! subjects | grep -q "(#1)" && subjects | grep -q "(#2)"'
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


case_pr_independent() {
  mk_case pr_independent
  issue 1 "T1" "Body"
  issue 2 "T2" "Body"
  plan '[1,2]' "$MODEL"
  local base_sha
  base_sha="$(git -C "$R" rev-parse main)"
  behave 1 <<'B'
result done "worker note for one"
RESULT="$(jq -c '.checks = {typecheck: "pass", lint: "n/a"} | .routes_to_check = ["/settings"]' <<<"$RESULT")"
B
  run_runner
  check "pr: run finishes with both tickets done" '[[ $RC == 0 && "$(sq ".done | map(.n) | join(\",\")")" == "1,2" ]]'
  check "pr: two branches off the base, pushed" '[[ -n "$(origin_ref overnight/test/1)" && -n "$(origin_ref overnight/test/2)" && "$(git -C "$R" merge-base overnight/test/1 main)" == "$base_sha" && "$(git -C "$R" merge-base overnight/test/2 main)" == "$base_sha" ]]'
  check "pr: no commit lands on the base, locally or on origin" '[[ "$(git -C "$R" rev-parse main)" == "$base_sha" && "$(origin_ref main)" == "$base_sha" ]]'
  check "pr: two PRs against the base, titled with the commit subject" '[[ "$(npr)" == 2 && "$(pr_field overnight/test/1 base)" == main && "$(pr_field overnight/test/2 base)" == main && "$(pr_field overnight/test/1 title)" == "do ticket (#1)" && "$(pr_field overnight/test/1 title)" == "$(git -C "$R" log -1 --format=%s overnight/test/1)" ]]'
  check "pr: each body closes its issue" 'pr_field overnight/test/1 body | grep -qx "Closes #1\." && pr_field overnight/test/2 body | grep -qx "Closes #2\."'
  check "pr: body summarises checks, unmet criteria, routes and notes" 'b="$(pr_field overnight/test/1 body)" && grep -q "typecheck: pass" <<<"$b" && grep -q "criterion X" <<<"$b" && grep -q "/settings" <<<"$b" && grep -q "worker note for one" <<<"$b"'
  check "pr: body, title and commits carry no agent attribution" '! { pr_field overnight/test/1 body; pr_field overnight/test/1 title; git -C "$R" log --all --format=%B; } | grep -Eqi "claude|co-authored|generated|agent|omp"'
  check "pr: state and report show branch and PR link" '[[ "$(sq ".done[0].pr")" == https://example.test/pull/1 && "$(sq ".done[0].branch")" == overnight/test/1 ]] && report | grep -E "^\| #1 " | grep -q "overnight/test/1.*example.test/pull/1" && report | grep -q "^1\. #1 .*overnight/test/1.*main.*pull/1"'
  check "pr: no merge command and no auto-merge, ever" '! grep -Eq "^(pr merge|api .*merge)|--auto( |$)" "$C/gh.calls" && grep -q "^pr create" "$C/gh.calls"'
  check "pr: the checkout ends detached on the base, clean" '[[ -z "$(git -C "$R" branch --show-current)" && "$(git -C "$R" rev-parse HEAD)" == "$base_sha" && -z "$(git -C "$R" status --porcelain)" ]]'
}

case_pr_stacked() {
  mk_case pr_stacked
  issue 1 "T1" "Body"
  issue 2 "T2" "Body"
  edge 2 1
  plan '[2,1]' "$MODEL"
  local base_sha
  base_sha="$(git -C "$R" rev-parse main)"
  behave 2 <<'B'
[[ -f work-1.txt ]] && echo yes >"$OT_CASE/saw-1"
B
  run_runner
  check "stacked: both done, A before B" '[[ $RC == 0 && "$(sq ".done | map(.n) | join(\",\")")" == "1,2" ]]'
  check "stacked: A targets the base, B targets A's branch" '[[ "$(pr_field overnight/test/1 base)" == main && "$(pr_field overnight/test/2 base)" == overnight/test/1 ]]'
  check "stacked: B's branch holds A's commit and B saw A's work" 'git -C "$R" merge-base --is-ancestor overnight/test/1 overnight/test/2 && [[ -f "$C/saw-1" ]]'
  check "stacked: B's PR names what it stacks on" 'pr_field overnight/test/2 body | grep -q "Stacked on #1 (https://example.test/pull/1)"'
  check "stacked: the report states the order A -> B" 'report | grep -q "Stacking order: #1 → #2"'
  check "stacked: nothing lands on the base" '[[ "$(git -C "$R" rev-parse main)" == "$base_sha" && "$(origin_ref main)" == "$base_sha" ]]'
}

case_pr_multi() {
  mk_case pr_multi
  for n in 1 2 3; do issue "$n" "T$n" "Body"; done
  edge 3 1
  edge 3 2
  plan '[1,2,3]' "$MODEL"
  local base_sha
  base_sha="$(git -C "$R" rev-parse main)"
  behave 3 <<'B'
[[ -f work-1.txt && -f work-2.txt ]] && echo yes >"$OT_CASE/saw-both"
B
  run_runner
  check "multi: all three done" '[[ $RC == 0 && "$(sq ".done | map(.n) | join(\",\")")" == "1,2,3" ]]'
  check "multi: the PR targets the base and the worker saw both blockers' work" '[[ "$(pr_field overnight/test/3 base)" == main && -f "$C/saw-both" ]]'
  check "multi: the branch contains both blockers' commits" 'git -C "$R" merge-base --is-ancestor overnight/test/1 overnight/test/3 && git -C "$R" merge-base --is-ancestor overnight/test/2 overnight/test/3'
  check "multi: the PR names both blockers' PRs" 'b="$(pr_field overnight/test/3 body)" && grep -q "https://example.test/pull/1" <<<"$b" && grep -q "https://example.test/pull/2" <<<"$b" && grep -q "^Closes #3\.$" <<<"$b"'
  check "multi: nothing lands on the base; the merge was never a PR merge" '[[ "$(origin_ref main)" == "$base_sha" ]] && ! grep -Eq "^pr merge" "$C/gh.calls"'
}

case_pr_conflict() {
  mk_case pr_conflict
  for n in 1 2 3 4; do issue "$n" "T$n" "Body"; done
  edge 3 1
  edge 3 2
  plan '[1,2,3,4]' "$MODEL"
  local base_sha
  base_sha="$(git -C "$R" rev-parse main)"
  behave 1 <<'B'
echo one >shared.txt
B
  behave 2 <<'B'
echo two >shared.txt
B
  run_runner
  check "conflict: the run continues past it" '[[ $RC == 0 && "$(sq ".done | map(.n) | join(\",\")")" == "1,2,4" ]]'
  check "conflict: #3 is retried once, then fails as temporary with the merge conflict as its reason" '[[ "$(sq ".failed[0].n")" == 3 && "$(sq ".failed[0].class")" == temporary && "$(sq ".retries[\"3\"]")" == 1 && "$(sq ".failed[0].reason")" == "setup failed: merge conflict: #"* ]] && report | grep -E "^- #3:" | grep -q "merge conflict" && [[ -s "$R/.scratch/overnight/logs/3.handoff.md" ]]'
  check "conflict: #3's worker never ran, #4 started on a clean tree" '[[ "$(inv)" == "1 2 4" && "$(sed -n 3p "$C/invocations.log")" == "4 $MODEL 1 0" ]]'
  check "conflict: no branch for #3, locally or on origin; no merge left half-done" '[[ -z "$(git -C "$R" branch --list overnight/test/3)" && -z "$(origin_ref overnight/test/3)" && ! -e "$R/.git/MERGE_HEAD" && -z "$(git -C "$R" status --porcelain)" ]]'
  check "conflict: #4 branched from the base" '[[ "$(git -C "$R" merge-base overnight/test/4 main)" == "$base_sha" ]]'
}

# A setup failure that is not a merge: the ticket branch cannot be created.
case_setup_failure() {
  mk_case setup_failure
  for n in 1 2 3; do issue "$n" "T$n" "Body"; done
  edge 2 1
  plan '[1,2,3]' "$MODEL"
  # refs/heads/overnight/test/1/x blocks creating refs/heads/overnight/test/1
  git -C "$R" branch overnight/test/1/x main
  run_runner
  check "setup failure: the run finishes and only #1 fails, as temporary after one retry" '[[ $RC == 0 && "$(sq ".failed | map(.n) | join(\",\")")" == 1 && "$(sq ".failed[0].class")" == temporary && "$(sq ".retries[\"1\"]")" == 1 ]]'
  check "setup failure: #1 never ran a worker, its dependent is skipped, #3 is done" '[[ "$(inv)" == 3 && "$(sq ".skipped | map(.n) | join(\",\")")" == 2 && "$(sq ".done | map(.n) | join(\",\")")" == 3 ]]'
  check "setup failure: the handoff names the failure" 'grep -qi "setup" "$R/.scratch/overnight/logs/1.handoff.md"'
}

case_pr_failed() {
  mk_case pr_failed
  for n in 1 2 3; do issue "$n" "T$n" "Body"; done
  plan '[1,2,3]' "$MODEL"
  local base_sha
  base_sha="$(git -C "$R" rev-parse main)"
  behave 1 <<'B'
result blocked "needs a design decision"
B
  behave 2-1 <<'B'
RESULT="You've hit your usage limit"
B
  behave 2-2 <<'B'
git rev-parse HEAD >"$OT_CASE/head-2-2"
git branch --format='%(refname:short)' --list 'overnight/test/*' >"$OT_CASE/branches-2-2"
B
  OVERNIGHT_RATE_LIMIT_BACKOFF_SECS=0 run_runner
  check "failed: run finishes; #1 failed, #2 requeued then done, #3 done" '[[ $RC == 0 && "$(inv)" == "1 2 2 3" && "$(sq ".failed | map(.n) | join(\",\")")" == 1 && "$(sq ".done | map(.n) | join(\",\")")" == "2,3" && "$(sq ".requeues[\"2\"]")" == 1 ]]'
  check "failed: #1 leaves no branch, locally or on origin" '[[ -z "$(git -C "$R" branch --list overnight/test/1)" && -z "$(origin_ref overnight/test/1)" ]]'
  check "failed: #1's stash is recorded as before" 'git -C "$R" stash list | grep -q "overnight #1$" && stash_files | grep -qx work-1.txt && [[ -n "$(sq ".failed[0].stash")" ]]'
  check "failed: the requeued attempt started on a clean tree at the base, on a fresh branch" '[[ "$(sed -n 3p "$C/invocations.log")" == "2 $MODEL 2 0" && "$(cat "$C/head-2-2")" == "$base_sha" && "$(cat "$C/branches-2-2")" == overnight/test/2 ]]'
  check "failed: the next ticket starts clean from the base" '[[ "$(sed -n 4p "$C/invocations.log")" == "3 $MODEL 1 0" && "$(git -C "$R" merge-base overnight/test/3 main)" == "$base_sha" ]]'
  check "failed: only the passed tickets got PRs" '[[ "$(npr)" == 2 && -z "$(pr_field overnight/test/1 head)" ]]'
}

case_pr_publish_failure() {
  mk_case pr_publish_failure
  issue 1 "T1" "Body"
  issue 2 "T2" "Body"
  edge 2 1
  plan '[1,2]' "$MODEL"
  git -C "$R" remote set-url origin "$C/nowhere.git"
  run_runner
  check "publish failure: green tickets are done with a publish error, no PR" '[[ $RC == 0 && "$(sq ".done | map(.n) | join(\",\")")" == "1,2" && "$(sq ".done[0].pr")" == null && "$(sq ".done[0].publish_error")" == "push of overnight/test/1 failed"* && "$(sq ".failed | length")" == 0 && "$(npr)" == 0 ]]'
  check "publish failure: branches are kept locally; the report shows the error" '[[ -n "$(git -C "$R" branch --list overnight/test/1)" && -n "$(git -C "$R" branch --list overnight/test/2)" ]] && report | grep -E "^\| #1 " | grep -q "no PR: push of overnight/test/1 failed"'
  git -C "$R" remote set-url origin "$C/origin.git"
  run_runner --resume
  check "publish failure: --resume opens the missing PRs without re-running a worker" '[[ $RC == 0 && "$(inv)" == "1 2" && "$(npr)" == 2 && "$(sq ".done[0].pr")" == https://* && "$(sq ".done[1].pr")" == https://* && "$(sq ".done[0].publish_error")" == null ]]'
  check "publish failure: the stacked PR follows its blocker" '[[ "$(pr_field overnight/test/1 base)" == main && "$(pr_field overnight/test/2 base)" == overnight/test/1 ]]'
}

case_pr_create_failure() {
  mk_case pr_create_failure
  issue 1 "T1" "Body"
  plan '[1]' "$MODEL"
  touch "$C/pr-fail"
  run_runner
  check "pr create failure: done with the error, branch pushed" '[[ $RC == 0 && "$(sq ".done[0].n")" == 1 && "$(sq ".done[0].pr")" == null && "$(sq ".done[0].publish_error")" == "PR creation for overnight/test/1 failed: GraphQL: simulated failure" && -n "$(origin_ref overnight/test/1)" ]]'
  rm "$C/pr-fail"
  run_runner --resume
  check "pr create failure: --resume opens it, no worker re-run" '[[ $RC == 0 && "$(inv)" == 1 && "$(npr)" == 1 && "$(sq ".done[0].pr")" == https://* ]]'
}

case_gh_access() {
  mk_case gh_access
  issue 1 "T1" "Body"
  plan '[1]' "$MODEL"
  echo READ >"$C/perm"
  run_runner --dry-run
  check "gh access: a dry run stops without write access" '[[ $RC != 0 ]] && grep -q "write access" "$C/run.err"'
  run_runner
  check "gh access: so does a real run, before any state or worker" '[[ $RC != 0 ]] && grep -q "write access" "$C/run.err" && grep -q "READ" "$C/run.err" && [[ ! -e "$R/.scratch/overnight/state.json" && ! -e "$C/invocations.log" ]]'
  rm "$C/perm"
  touch "$C/gh-unauth"
  run_runner
  check "gh access: an unauthenticated gh stops the run" '[[ $RC != 0 ]] && grep -q "not authenticated" "$C/run.err" && [[ ! -e "$C/invocations.log" ]]'
  rm "$C/gh-unauth"
  run_runner --dry-run
  check "gh access: with write access the dry run reports it" '[[ $RC == 0 ]] && grep -q "gh access   write (WRITE)" "$C/run.out"'
}

case_pr_dry_run() {
  mk_case pr_dry_run
  for n in 1 2 3 4; do issue "$n" "T$n" "Body"; done
  edge 3 1
  edge 3 2
  edge 4 1
  plan '[1,2,3,4]' "$MODEL"
  run_runner --dry-run
  check "dry run: independent ticket shows its branch and the base as PR base" '[[ $RC == 0 ]] && grep -q "branch overnight/test/1, from main, PR base main" "$C/run.out"'
  check "dry run: single blocker stacks, PR base is the blocker's branch" 'grep -q "branch overnight/test/4, stacked on overnight/test/1, PR base overnight/test/1" "$C/run.out"'
  check "dry run: several blockers merge, PR base is the base" 'grep -q "branch overnight/test/3, from main merging overnight/test/1, overnight/test/2, PR base main" "$C/run.out"'
  check "dry run: creates no branch, pushes nothing, opens nothing" '[[ -z "$(git -C "$R" branch --list "overnight/*")" && -z "$(origin_ref overnight/test/1)" && ! -e "$C/prs" ]]'
}

case_no_merge() {
  check "no merge: the runner has no PR-merge or auto-merge call" '! grep -Eq "pr +merge|enableAutoMerge|enable-auto|--auto( |\$)" "$runner"'
  local brief="$repo_root/skills/overnight-run/scripts/worker-brief.md"
  check "no merge: the worker brief still forbids git and GitHub writes" 'grep -q "^- Git: read-only" "$brief" && grep -q "^- GitHub and the tracker: read-only" "$brief" && grep -q "PRs or merges" "$brief"'
}

case_matrix() {
  mk_case matrix
  issue 1 "Has criteria" $'## Done when\n- [ ] it works'
  issue 2 "Vague" "no bullets here"
  local dry="--dry-run"
  plan '[1,2]' "$MODEL"
  run_runner $dry
  check "matrix: DeepSeek gates the Go provider" '[[ $RC == 0 ]] && grep -q "gate provider  opencode-go" "$C/run.out" && grep -q "model       $MODEL" "$C/run.out" && grep -q "in omp models" "$C/run.out" && grep -Eq "^  gate +exit [0-9]+ — .*opencode-go" "$C/run.out"'
  check "matrix: dry run shows Go thresholds" 'grep -q "monthly" "$C/run.out" && grep -q "5h sleep" "$C/run.out"'
  check "matrix: dry run lists tickets without criteria" 'grep -q "no acceptance criteria: #2$" "$C/run.out"'
  check "matrix: dry run says why it is headless" 'grep -q "visible     no (--headless)" "$C/run.out"'
  plan '[1]' ''
  OVERNIGHT_WORKER_MODEL=anthropic/claude-sonnet-5-5 run_runner $dry
  check "matrix: omp + anthropic model gates Anthropic (env beats plan)" '[[ $RC == 0 ]] && grep -q "gate provider  anthropic" "$C/run.out" && grep -q "model       anthropic/claude-sonnet-5-5" "$C/run.out"'
  plan '[1]' "$MODEL"
  OVERNIGHT_WORKER_MODEL=anthropic/claude-sonnet-5-5 run_runner $dry
  check "matrix: env override beats the plan model" 'grep -q "gate provider  anthropic" "$C/run.out"'
  plan '[1]' ''
  run_runner $dry
  check "matrix: omp with no plan model defaults to modelRoles.task" '[[ $RC == 0 ]] && grep -q "model       anthropic/claude-sonnet-5-5:medium" "$C/run.out" && grep -q "omp modelRoles.task" "$C/run.out" && grep -q "gate provider  anthropic" "$C/run.out"'
  OT_TASK_ROLE= run_runner $dry
  check "matrix: no plan model and no task role is refused, naming modelRoles.task" '[[ $RC != 0 ]] && grep -q "modelRoles.task" "$C/run.err"'
  plan '[1]' 'deepseek-v4.1-flash'
  run_runner $dry
  check "matrix: omp model without provider prefix is refused" '[[ $RC != 0 ]] && grep -q "provider/model" "$C/run.err"'
  plan '[1]' "$MODEL"
  PATH="$T/bin-claude:$PATH" run_runner --worker claude $dry
  check "matrix: claude + DeepSeek refused, naming both" '[[ $RC != 0 ]] && grep -q "claude" "$C/run.err" && grep -q "$MODEL" "$C/run.err"'
  plan '[1]' ''
  PATH="$T/bin-claude:$PATH" run_runner --worker claude $dry
  check "matrix: claude defaults to the task role, split into --model and --effort" '[[ $RC == 0 ]] && grep -q -- "--model claude-sonnet-5-5 --effort medium" "$C/run.out" && grep -q "gate provider  anthropic" "$C/run.out"'
  plan '[1]' 'anthropic/claude-sonnet-5-5:minimal'
  PATH="$T/bin-claude:$PATH" run_runner --worker claude $dry
  check "matrix: claude refuses a non-claude effort word" '[[ $RC != 0 ]] && grep -q "effort" "$C/run.err"'
  plan '[1]' 'anthropic/claude-sonnet-5-5'
  PATH="$T/bin-claude:$PATH" run_runner --worker claude $dry
  check "matrix: claude with an anthropic model is allowed" '[[ $RC == 0 ]] && grep -q "gate provider  anthropic" "$C/run.out" && grep -q "visible     no (claude worker is headless)" "$C/run.out"'
  plan '[1]' 'anthropic/claude-opus-latest:high'
  run_runner $dry
  check "matrix: a model missing from omp models is refused with a near match" '[[ $RC != 0 ]] && grep -q "not in omp models" "$C/run.err" && grep -q "openrouter/~anthropic/claude-opus-latest" "$C/run.err"'
  plan '[1]' "$MODEL"
  OT_MODELS_FAIL=1 run_runner $dry
  check "matrix: an unreadable catalogue does not block the run" '[[ $RC == 0 ]] && grep -q "catalogue unreadable" "$C/run.out"'
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
  OT_TASK_ROLE= run_runner --resume
  check "resume: no model anywhere is refused, naming worker_model and modelRoles.task" '[[ $RC != 0 ]] && grep -q "worker_model" "$C/run.err" && grep -q "modelRoles.task" "$C/run.err"'
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

case_model_rejected() {
  mk_case model_rejected
  for n in 1 2; do issue "$n" "T$n" "Body"; done
  edge 2 1
  plan '[1,2]' "$MODEL"
  behave 1 <<'B'
echo 'Model "x" not found. Run "omp models" to see available models.' >&2
EXIT=1 NO_RESULT=1
B
  run_runner
  check "model rejected: the run stops without retrying" '[[ $RC != 0 && "$(inv)" == 1 ]]'
  check "model rejected: stop reason names the model" '[[ "$(sq .stop_reason)" == "worker model"* ]]'
  check "model rejected: #1 is neither failed nor its dependent skipped" '[[ "$(sq ".failed | length")" == 0 && "$(sq ".skipped | length")" == 0 && "$(sq ".queue | map(tostring) | join(\",\")")" == "1,2" && "$(sq .current)" == 1 ]]'
  check "model rejected: the worker's stderr is kept" 'grep -q "not found" '"$logs"'/1-1.err'
}

case_stop() {
  mk_case stop
  for n in 1 2; do issue "$n" "T$n" "Body"; done
  plan '[1,2]' "$MODEL"
  behave 1 <<'B'
bash "$OT_RUNNER" --stop >"$OT_CASE/stop-msg.out"
B
  run_runner
  check "stop: the current ticket finishes, then the run ends cleanly" '[[ $RC == 0 && "$(inv)" == 1 && "$(sq ".done | map(.n) | join(\",\")")" == 1 && "$(sq .stop_reason)" == "stop requested" && "$(sq ".queue | map(tostring) | join(\",\")")" == 2 && ! -e "$R/.scratch/overnight/stop-requested" ]]'
  check "stop: the confirmation names the current ticket once" 'grep -q "ends after ticket #1$" "$C/stop-msg.out"'
  run_runner --resume
  check "stop: --resume picks up the rest and the request does not linger" '[[ $RC == 0 && "$(inv)" == "1 2" && "$(sq .stop_reason)" == "queue empty" ]]'
  local src=0
  (cd "$R" && bash "$runner" --stop) >"$C/stop.out" 2>"$C/stop.err" || src=$?
  check "stop: with no live run it is refused" '[[ $src != 0 ]] && grep -q "no live run" "$C/stop.err"'
}

case_abort() {
  mk_case abort
  for n in 1 2; do issue "$n" "T$n" "Body"; done
  plan '[1,2]' "$MODEL"
  behave 1 <<'B'
sleep 30
B
  (cd "$R" && exec bash "$runner" --headless --worker omp --deadline "$DL") >"$C/run.out" 2>"$C/run.err" &
  local pid=$! i
  for i in $(seq 100); do
    [[ -f "$C/invocations.log" ]] && break
    sleep 0.1
  done
  kill -TERM "$pid"
  RC=0
  wait "$pid" || RC=$?
  check "abort: SIGTERM ends the run at once, with #1 still current and #2 never started" '[[ $RC == 143 && "$(inv)" == 1 && "$(sq .current)" == 1 && "$(sq .stop_reason)" == aborted* ]] && ! grep -q "#2 start" "$C/run.out"'
  behave 1 <<'B'
true
B
  run_runner --resume
  check "abort: --resume finishes both tickets" '[[ $RC == 0 && "$(sq ".done | map(.n) | join(\",\")")" == "1,2" ]]'
}

case_caffeinate() {
  mk_case caffeinate
  issue 1 "T1" "Body"
  plan '[1]' "$MODEL"
  mkdir -p "$C/bin"
  # A stub that behaves like `caffeinate -i -w <pid>`: logs its argv, lives
  # until that pid is gone, then logs the exit.
  cat >"$C/bin/caffeinate" <<'S'
#!/usr/bin/env bash
echo "$*" >"$OT_CASE/caff.args"
w=""
[[ "$1 $2" == "-i -w" ]] && w="$3"
while [[ -n "$w" ]] && kill -0 "$w" 2>/dev/null; do sleep 0.1; done
echo gone >"$OT_CASE/caff.gone"
S
  chmod +x "$C/bin/caffeinate"
  behave 1 <<'B'
cp "$OT_CASE/caff.args" "$OT_CASE/caff.during" 2>/dev/null
B
  PATH="$C/bin:$PATH" run_runner --dry-run
  check "caffeinate: a dry run takes no assertion" '[[ $RC == 0 && ! -e "$C/caff.args" ]]'
  PATH="$C/bin:$PATH" run_runner
  local i
  for i in $(seq 50); do [[ -e "$C/caff.gone" ]] && break; sleep 0.1; done
  check "caffeinate: held while the worker runs, tied to the runner pid" '[[ $RC == 0 && "$(cat "$C/caff.during")" == "-i -w $(sq .pid)" ]]'
  check "caffeinate: released once the runner exits" '[[ -e "$C/caff.gone" ]]'
  check "caffeinate: no warning noise" '! grep -qi "caffeinate\|sleep" "$C/run.err"'
  # a caffeinate that fails must not fail or noise up the run
  printf '#!/bin/sh\necho "caffeinate: broken" >&2\nexit 1\n' >"$C/bin/caffeinate"
  rm -f "$C/caff.gone" "$R/.scratch/overnight/state.json"
  git -C "$R" reset -q --hard main
  PATH="$C/bin:$PATH" run_runner
  check "caffeinate: a failing caffeinate is silent and harmless" '[[ $RC == 0 ]] && ! grep -qi "caffeinate: broken" "$C/run.err" "$C/run.out"'
  # abort: SIGTERM mid-ticket still releases the assertion
  rm -f "$C/caff.gone" "$C/invocations.log" "$R/.scratch/overnight/state.json"
  git -C "$R" reset -q --hard main
  cat >"$C/bin/caffeinate" <<'S'
#!/usr/bin/env bash
w="$3"
while kill -0 "$w" 2>/dev/null; do sleep 0.1; done
echo gone >"$OT_CASE/caff.gone"
S
  behave 1 <<'B'
sleep 30
B
  (cd "$R" && PATH="$C/bin:$PATH" exec bash "$runner" --headless --worker omp --deadline "$DL") >"$C/run.out" 2>"$C/run.err" &
  local pid=$!
  for i in $(seq 100); do [[ -f "$C/invocations.log" ]] && break; sleep 0.1; done
  check "caffeinate: still held mid-ticket" '[[ ! -e "$C/caff.gone" ]]'
  kill -TERM "$pid"
  wait "$pid" || true
  for i in $(seq 50); do [[ -e "$C/caff.gone" ]] && break; sleep 0.1; done
  check "caffeinate: released on abort" '[[ -e "$C/caff.gone" ]]'
}

# --- run ----------------------------------------------------------------------

cases=(retry_success retry_exhausted dependent_order blocked protected protected_allowed
  protected_override red_tests commit_refused pr_independent pr_stacked pr_multi
  pr_conflict setup_failure pr_failed pr_publish_failure pr_create_failure gh_access pr_dry_run no_merge matrix resume_old_state
  resume_no_model resume_interrupted notify model_rejected stop abort caffeinate)
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
