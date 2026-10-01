#!/usr/bin/env bash
# overnight.sh — the only loop of the overnight-run skill.
#
# Strictly serial: gate usage, run one fresh worker per ready-for-agent ticket,
# gate the build, commit or stash, repeat. The invoking agent session only
# writes .scratch/overnight/plan.json and launches this under tmux (or a herdr
# tab) with caffeinate.
#
#   overnight.sh [--dry-run] [--deadline HH:MM] [--max-tickets N]
#                [--worker claude|omp] [--visible|--headless] [--pr-per-ticket] [--resume]
#                [--stop]
#
# --stop           ask the live run in this repo to end after its current ticket
#                  (or during a usage sleep); it writes its report and exits 0.
#                  For an immediate abort, kill -TERM the pid in state.json,
#                  never caffeinate or the tmux pane.
# --visible        default for an omp worker inside herdr (--headless opts out):
#                  each worker runs as the interactive omp TUI in its own herdr
#                  tab, closed when it ends.
# --pr-per-ticket  each ticket runs in its own worktree (<repo>-overnight/<N>)
#                  on ticket/<N>-<slug>, stacked on the previous passed ticket
#                  (the first on origin/main). A pass is committed, pushed and
#                  opened as a draft PR against its base; a fail keeps its
#                  worktree. Nothing is merged. plan.json "setup" (e.g. "npm ci")
#                  runs in each new worktree.
#
# plan.json (written by the preflight):
#   {"branch": "overnight/YYYY-MM-DD", "queue": [12, 14],
#    "waived": [[14, 9]],             # [issue, blocker] edges to ignore
#    "checks": {"typecheck": "...", "build": "...", "lint": "...", "test": "..."},
#    "setup": "npm ci"}                # --pr-per-ticket only; "" or absent = none
# "" means the repo has no such command. The build gate after each worker is
# typecheck + build + lint + test; the tree-health check after a stash skips
# test. worker_model is optional: OVERNIGHT_WORKER_MODEL, then plan worker_model,
# then (on --resume) the state, then omp's modelRoles.task. It must be an
# `omp models` selector, plus an optional :<thinking> suffix. The usage gate
# reads the quota of the model's provider (the prefix before "/"); a claude
# worker takes an anthropic model, its :<level> passed as --effort.
#
# Outputs, all under .scratch/overnight/ (git-ignored via .git/info/exclude):
#   state.json     queue, done, failed, skipped, SHAs, stash refs, usage
#   <date>.md      morning report
#   logs/          worker stdout/stderr, briefs, results, check logs, for a human only
#   sessions/      --visible worker transcripts (omp --resume <file> to replay)
#
# Tracker access is read-only (gh issue view, gh api GET). Without
# --pr-per-ticket nothing is pushed; with it, only ticket branches and draft PRs.
#
# SC2016 off: the single-quoted $names are jq variables, not shell ones.
# shellcheck disable=SC2016
set -euo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=SCRIPTDIR/usage-gate.sh disable=SC1091
source "$here/usage-gate.sh"

# OVERNIGHT_* environment variables override these.
TICKET_TIMEOUT_SECS="${OVERNIGHT_TICKET_TIMEOUT_SECS:-2700}" # 45 min wall clock per worker
CHECK_TIMEOUT_SECS="${OVERNIGHT_CHECK_TIMEOUT_SECS:-1200}"   # per build-gate command
KILL_GRACE_SECS="${OVERNIGHT_KILL_GRACE_SECS:-30}"           # TERM, then KILL
CLAUDE_MAX_TURNS=200 # passed only while `claude --help` lists --max-turns
CLAUDE_PERMISSION_MODE="${OVERNIGHT_CLAUDE_PERMISSION_MODE:-auto}"
WORKER_MODEL="${OVERNIGHT_WORKER_MODEL:-}"                             # overrides plan.json worker_model
RATE_LIMIT_BACKOFF_SECS="${OVERNIGHT_RATE_LIMIT_BACKOFF_SECS:-1800}" # limit the gate cannot see
MAX_REQUEUES=3                                                       # per ticket, then the run stops
MAX_RETRIES=1                                                        # per ticket, temporary failures only
PR_BASE="${OVERNIGHT_PR_BASE:-main}"                                 # --pr-per-ticket stack root
VISIBLE_IDLE_SECS=60 # --visible: quiet time after a terminal turn that counts as finished
LIMIT_RE="You('|’)ve hit your .* limit|Request rejected \(429\)"
MODEL_MISSING_RE='Model "[^"]+" not found|issue with the selected model|unrecognized_model'
# Repo-relative paths a worker may never change: env files, keys, CI workflows,
# git internals. id_*.pub stays allowed.
PROTECTED_RE="${OVERNIGHT_PROTECTED_RE:-(^|/)\.env(\.|\$)|\.pem\$|\.key\$|(^|/)id_(rsa|ed25519|ecdsa|dsa)(\$|[^.]|\.[^p])|(^|/)\.git/|^\.github/workflows/}"

die() {
  echo "overnight: $*" >&2
  exit 1
}
log() { printf '%s  %s\n' "$(date '+%H:%M:%S')" "$*"; }

# notify <title> <msg> — macOS notification; never fails the run.
notify() {
  if [[ "${OVERNIGHT_NOTIFY:-1}" == 0 ]] || ! command -v osascript >/dev/null 2>&1; then return 0; fi
  osascript -e 'on run argv' -e 'display notification (item 2 of argv) with title (item 1 of argv)' \
    -e 'end run' "$1" "$2" >/dev/null 2>&1 || true
}

# --- arguments -------------------------------------------------------------

dry_run=0
resume=0
deadline_hm="07:00"
max_tickets=0
worker=""
visible= # empty = auto: on for an omp worker inside herdr
pr_mode=0
stop_req=0
while (($#)); do
  case "$1" in
  --dry-run) dry_run=1 ;;
  --resume) resume=1 ;;
  --visible) visible=1 ;;
  --headless) visible=0 ;;
  --pr-per-ticket) pr_mode=1 ;;
  --stop) stop_req=1 ;;
  --deadline)
    deadline_hm="${2:?--deadline needs HH:MM}"
    shift
    ;;
  --max-tickets)
    max_tickets="${2:?--max-tickets needs N}"
    shift
    ;;
  --worker)
    worker="${2:?--worker needs claude|omp}"
    shift
    ;;
  -h | --help)
    awk 'NR > 1 && /^# SC2016/ { exit } NR > 1 { sub(/^# ?/, ""); print }' "${BASH_SOURCE[0]}"
    exit 0
    ;;
  *) die "unknown argument: $1" ;;
  esac
  shift
done
[[ "$max_tickets" =~ ^[0-9]+$ ]] || die "--max-tickets must be a number"
[[ "$deadline_hm" =~ ^([01][0-9]|2[0-3]):[0-5][0-9]$ ]] || die "--deadline must be HH:MM"

root="$(git rev-parse --show-toplevel 2>/dev/null)" || die "not inside a git checkout"
cd "$root"
dir="$root/.scratch/overnight"
plan="$dir/plan.json"
state="$dir/state.json"
stop_file="$dir/stop-requested"
if ((stop_req)); then
  live_pid="$(jq -r '.pid // empty' "$state" 2>/dev/null || true)"
  if [[ -z "$live_pid" ]] || ! kill -0 "$live_pid" 2>/dev/null ||
    [[ "$(jq -r '.stop_reason // empty' "$state")" != "" ]]; then
    die "no live run to stop (state.json pid ${live_pid:-unset})"
  fi
  : >"$stop_file"
  live_current="$(jq -r '.current // empty' "$state")"
  echo "overnight: stop requested; run $live_pid ends $([[ -n "$live_current" ]] && echo "after ticket #$live_current" || echo "at its next check")"
  exit 0
fi
[[ -f "$plan" ]] || die "no $plan — run the overnight-run preflight first"
jq -e '(.queue | type) == "array" and (.checks | type) == "object"' "$plan" >/dev/null ||
  die "$plan needs a queue array and a checks object"
for tool in git jq gh perl; do
  command -v "$tool" >/dev/null 2>&1 || die "$tool not on PATH"
done

# --- helpers ---------------------------------------------------------------

# st_apply <filter> [jq args...] — rewrite state.json through a jq filter.
st_apply() {
  local filter="$1"
  shift
  jq "$@" "$filter" "$state" >"$state.tmp" && mv "$state.tmp" "$state"
}
sget() { jq -r "$1" "$state"; }

skill_path() {
  local base
  for base in "$HOME/.claude/skills" "$HOME/.agents/skills"; do
    if [[ -f "$base/$1/SKILL.md" ]]; then
      echo "$base/$1/SKILL.md"
      return 0
    fi
  done
  return 1
}

deadline_epoch() {
  local today t
  today="$(date +%Y-%m-%d)"
  t="$(date -j -f '%Y-%m-%d %H:%M:%S' "$today $deadline_hm:00" +%s 2>/dev/null ||
    date -d "$today $deadline_hm" +%s)"
  ((t > $(date +%s))) || t=$((t + 86400))
  echo "$t"
}

# resolve_model — sets model (what the gate filters on), model_arg (what the
# worker is passed), model_source (where it came from), provider (whose quota
# the gate reads) and, for a claude worker, claude_model and claude_effort.
# Precedence: OVERNIGHT_WORKER_MODEL, plan worker_model, on --resume the state,
# then omp's modelRoles.task.
resolve_model() {
  model_arg="$WORKER_MODEL"
  model_source="OVERNIGHT_WORKER_MODEL"
  if [[ -z "$model_arg" ]]; then
    model_arg="$(jq -r '.worker_model // ""' "$plan")"
    model_source="plan.json worker_model"
  fi
  if [[ -z "$model_arg" ]] && ((resume)); then
    model_arg="$(sget '.model_arg // (if .worker == "omp" then .model else "" end) // ""')"
    model_source="state.json (resumed run)"
  fi
  if [[ -z "$model_arg" ]]; then
    model_arg="$(omp config get modelRoles --json 2>/dev/null | jq -r '.value.task // empty' 2>/dev/null || true)"
    model_source="omp modelRoles.task"
  fi
  [[ -n "$model_arg" ]] ||
    die "no worker model: set worker_model in plan.json, OVERNIGHT_WORKER_MODEL, or modelRoles.task in omp config"
  claude_model="" claude_effort=""
  if [[ "$worker" == omp ]]; then
    [[ "$model_arg" =~ ^[^/]+/. ]] ||
      die "omp worker model '$model_arg' needs provider/model form (e.g. anthropic/claude-sonnet-5-5:medium)"
    model="$model_arg"
    provider="${model_arg%%/*}"
  else
    if [[ "$model_arg" == */* && "${model_arg%%/*}" != anthropic ]]; then
      die "worker claude cannot run model '$model_arg' (provider ${model_arg%%/*}): use --worker omp, or an anthropic model"
    fi
    provider=anthropic
    model="$model_arg"
    claude_model="${model_arg#anthropic/}"
    if [[ "$claude_model" =~ ^(.+):(low|medium|high|xhigh|max)$ ]]; then
      claude_model="${BASH_REMATCH[1]}"
      claude_effort="${BASH_REMATCH[2]}"
    elif [[ "$claude_model" == *:* ]]; then
      die "worker claude takes an effort of low|medium|high|xhigh|max, not '${claude_model##*:}'"
    fi
    if [[ -n "$claude_effort" ]] && ((!claude_lists_effort)); then
      die "claude has no --effort; drop the :$claude_effort suffix from the model"
    fi
  fi
}

# check_model — sets model_check; dies when model_arg is not an exact selector
# in `omp models`. Only a trailing thinking/effort word is stripped, so ids that
# contain a colon themselves (…:batch) are looked up whole.
check_model() {
  local base catalog near
  if [[ "$model_arg" != */* ]]; then
    model_check="not checked (bare claude model name)"
    return 0
  fi
  base="$model_arg"
  if [[ "$base" =~ ^(.+):(off|minimal|low|medium|high|xhigh|max|auto)$ ]]; then base="${BASH_REMATCH[1]}"; fi
  if ! catalog="$(omp models --json 2>/dev/null)" || ! jq -e '.models | type == "array"' <<<"$catalog" >/dev/null 2>&1; then
    model_check="catalogue unreadable (omp models --json failed); not checked"
    return 0
  fi
  if jq -e --arg s "$base" 'any(.models[]?; .selector == $s)' <<<"$catalog" >/dev/null; then
    model_check="in omp models"
    return 0
  fi
  near="$(jq -r --arg n "${base#*/}" '[.models[]?.selector | select(contains($n))][:3] | join(", ")' <<<"$catalog")"
  die "model '$model_arg' is not in omp models (no selector '$base')${near:+; did you mean: $near}"
}

# The Anthropic gate reads omp's Anthropic login. A claude worker must be on the
# same org, or the reading describes somebody else's quota.
account_check() {
  if [[ "$provider" != anthropic ]]; then
    # The org-mismatch downgrade does not apply: omp authenticates this provider
    # itself, and a claude worker cannot use it (refused at startup).
    echo "match: omp reads its own $provider login"
    return
  fi
  if [[ "$worker" == omp ]]; then
    echo "match: omp worker uses omp's own Anthropic login"
    return
  fi
  local claude_org omp_orgs
  claude_org="$(claude auth status 2>/dev/null | jq -r '.orgId // empty' 2>/dev/null || true)"
  omp_orgs="$(omp usage --provider anthropic --json 2>/dev/null | jq -r '
    [(.reports[]? | select(.provider == "anthropic") | .metadata.orgId),
     (.accountsWithoutUsage[]? | select(.provider == "anthropic") | .orgId)]
    | map(select(. != null)) | unique | .[]' 2>/dev/null || true)"
  if [[ -z "$claude_org" || -z "$omp_orgs" ]]; then
    echo "unknown: claude org '${claude_org:-?}', omp orgs '${omp_orgs//$'\n'/,}'"
  elif grep -qxF "$claude_org" <<<"$omp_orgs"; then
    echo "match: claude and omp share org $claude_org"
  else
    echo "mismatch: claude org $claude_org, omp orgs ${omp_orgs//$'\n'/,}"
  fi
}

# gate — sets gate_code, gate_secs and gate_reading.
gate() {
  local errf
  errf="$(mktemp)"
  gate_code=0
  gate_secs="$(bash "$here/usage-gate.sh" --provider "$provider" ${model:+--model "$model"} 2>"$errf")" || gate_code=$?
  gate_reading="$(tail -n 1 "$errf")"
  rm -f "$errf"
  if [[ "$account" == mismatch* && "$gate_code" != 30 ]]; then
    gate_code=30
    gate_reading="unknown: account mismatch, reading not the worker's · $gate_reading"
  fi
}

record_usage() {
  st_apply '.usage += [{at: now | floor, label: $l, code: ($c | tonumber), reading: $r}]' \
    --arg l "$1" --arg c "$gate_code" --arg r "$gate_reading"
}

# nap <secs> — a sleep that signal traps can interrupt (bash defers traps
# until a foreground child exits).
nap() {
  sleep "$1" &
  wait $! || true
}

# idle <secs> — nap in chunks of at most 10s, returning early once --stop has
# been requested, so a long usage sleep or backoff does not outlast it.
idle() {
  local left="$1" step
  while ((left > 0)) && [[ ! -f "$stop_file" ]]; do
    step=$((left < 10 ? left : 10))
    nap "$step"
    left=$((left - step))
  done
}

# mtime <file> — modification time in epoch seconds (BSD or GNU stat).
mtime() { stat -f %m "$1" 2>/dev/null || stat -c %Y "$1"; }

# session_tail <session-dir> — the last assistant turn of a --visible worker
# as "<stopReason>\t<text and errorMessage, newlines flattened>".
session_tail() {
  cat "$1"/*.jsonl 2>/dev/null | jq -rs '
    [.[] | select(.type == "message" and .message.role == "assistant") | .message]
    | last // empty
    | "\(.stopReason // "")\t" + (([.content[]? | select(.type == "text") | .text] | join(""))
      + " " + (.errorMessage // "") | gsub("\n"; " "))' 2>/dev/null || true
}

# run_visible <secs> <n> <session-dir> <result-file> — runs worker_argv as the
# omp TUI in a new herdr tab in the current directory. Finished means the result
# file exists, or the last assistant turn is terminal and the transcript has
# been quiet for VISIBLE_IDLE_SECS. Sets timed_out; returns 1 when the tab
# closed first (omp exited or a human closed it), else 0.
active_tab=""
run_visible() {
  local secs="$1" n="$2" sessions="$3" result="$4" started created pane rc=0 f
  local quiet_since
  timed_out=0
  started="$(date +%s)"
  created="$(herdr tab create --workspace "$HERDR_WORKSPACE_ID" --cwd "$PWD" \
    --label "overnight #$n" --no-focus)" || stop "herdr tab create failed" 1
  active_tab="$(jq -r '.result.tab.tab_id' <<<"$created")"
  pane="$(jq -r '.result.root_pane.pane_id' <<<"$created")"
  # The pane types whatever it is sent, so send a short line: a launcher that
  # carries the runner's PATH (the pane's login shell has its own) and the
  # worker command. `exit` closes the tab when omp quits, which the loop reads
  # as "worker exited".
  local launcher="${result%.result.json}.worker.sh" err="${result%.result.json}.err"
  # stderr still reaches the pane, and is kept in the ticket's .err for the checks.
  printf 'export PATH=%q\nexec %s 2> >(tee -a %q >&2)\n' "$PATH" "$(printf '%q ' "${worker_argv[@]}")" "$err" >"$launcher"
  herdr pane run "$pane" "bash $(printf '%q' "$launcher"); exit" >/dev/null
  while :; do
    if [[ -s "$result" ]]; then
      nap 5 # let the final message land in the transcript
      break
    fi
    if ! herdr pane get "$pane" >/dev/null 2>&1; then
      rc=1
      break
    fi
    if (($(date +%s) - started >= secs)); then
      timed_out=1
      break
    fi
    quiet_since=0
    for f in "$sessions"/*.jsonl; do
      if [[ -f "$f" ]] && (($(mtime "$f") > quiet_since)); then quiet_since="$(mtime "$f")"; fi
    done
    if ((quiet_since > 0 && $(date +%s) - quiet_since >= VISIBLE_IDLE_SECS)) &&
      [[ "$(session_tail "$sessions" | cut -f 1)" =~ ^(stop|error|aborted)$ ]]; then
      break
    fi
    nap 5
  done
  herdr tab close "$active_tab" >/dev/null 2>&1 || true
  active_tab=""
  return "$rc"
}

# run_with_timeout <secs> <out> <err> <cmd...> — sets timed_out; returns the
# command's status. Job control gives the command its own process group, so a
# timeout (or the runner's own exit) kills the worker's children too.
active_pid=""
run_with_timeout() {
  local secs="$1" out="$2" err="$3"
  shift 3
  local pid rc=0 started
  timed_out=0
  started="$(date +%s)"
  set -m
  if [[ "$err" == "$out" ]]; then
    "$@" >"$out" 2>&1 </dev/null &
  else
    "$@" >"$out" 2>"$err" </dev/null &
  fi
  pid=$!
  set +m
  active_pid="$pid"
  while kill -0 "$pid" 2>/dev/null; do
    if (($(date +%s) - started >= secs)); then
      timed_out=1
      kill -TERM -- "-$pid" 2>/dev/null || true
      nap "$KILL_GRACE_SECS"
      kill -KILL -- "-$pid" 2>/dev/null || true
      break
    fi
    nap 1
  done
  wait "$pid" 2>/dev/null || rc=$?
  active_pid=""
  return "$rc"
}

# build_gate <label> <full|static> — typecheck, build, lint, plus test in full
# mode (when checks.test is set). Sets gate_failures (display text), gate_red_keys
# (names of the red checks) and gate_red_log (log of the first red one).
build_gate() {
  local label="$1" mode="$2" key cmd log rc timed_out=0
  local keys=(typecheck build lint)
  if [[ "$mode" == full ]]; then keys+=(test); fi
  gate_failures="" gate_red_keys="" gate_red_log=""
  for key in "${keys[@]}"; do
    cmd="$(jq -r --arg k "$key" '.checks[$k] // ""' "$plan")"
    [[ -n "$cmd" ]] || continue
    log="$dir/logs/$label-$key.log"
    rc=0
    run_with_timeout "$CHECK_TIMEOUT_SECS" "$log" "$log" bash -c "$cmd" || rc=$?
    if ((timed_out || rc != 0)); then
      gate_failures="${gate_failures:+$gate_failures, }$key$( ((timed_out)) && echo ' (timeout)' || true)"
      gate_red_keys="${gate_red_keys:+$gate_red_keys }$key"
      [[ -n "$gate_red_log" ]] || gate_red_log="$log"
    fi
  done
  [[ -z "$gate_failures" ]]
}

# changed_paths — every changed path, tracked and untracked, one per line; a
# rename or copy lists both its paths.
changed_paths() {
  local entry
  while IFS= read -r -d '' entry; do
    printf '%s\n' "${entry:3}"
    if [[ "${entry:0:2}" == *[RC]* ]]; then
      IFS= read -r -d '' entry && printf '%s\n' "$entry"
    fi
  done < <(git status --porcelain -z --untracked-files=all)
}

# protected_hits — the changed paths that match PROTECTED_RE.
protected_hits() { changed_paths | grep -E -e "$PROTECTED_RE" || true; }

# purge_protected <paths, one per line> — restore tracked ones from HEAD (index
# and tree) and delete the rest, so they never reach a patch, stash or commit.
purge_protected() {
  local p
  while IFS= read -r p; do
    [[ -n "$p" ]] || continue
    if git cat-file -e "HEAD:$p" 2>/dev/null; then
      git checkout -q HEAD -- "$p"
    else
      git rm -q --cached -f --ignore-unmatch -- "$p" >/dev/null 2>&1 || true
      rm -rf -- "$p"
    fi
  done <<<"$1"
}

# acceptance_criteria — stdin: an issue body. Prints the bullet, numbered and
# checklist lines under the first heading (or bold-only line) that matches
# "acceptance criteria" or "done when", up to the next heading.
acceptance_criteria() {
  awk '
    { sub(/\r$/, "") }
    /^[ ]*#+[ \t]/ || /^[ ]*(\*\*|__)[^*_]+(\*\*|__):?[ \t]*$/ {
      if (on) exit
      if (tolower($0) ~ /acceptance criteria|done when/) on = 1
      next
    }
    on && /^[ \t]*([-*+]|[0-9]+[.)])[ \t]+/ { print }
  '
}

ensure_ignored() {
  git check-ignore -q "$dir/state.json" && return 0
  local exclude
  exclude="$(git rev-parse --git-path info/exclude)"
  mkdir -p "$(dirname "$exclude")"
  printf '/.scratch/overnight/\n' >>"$exclude"
  log "added /.scratch/overnight/ to $exclude"
}

fetch_tracker() {
  local n title edges
  for n in $(sget '.planned[]'); do
    title="$(gh issue view "$n" --json title --jq .title)" || die "gh issue view $n failed"
    edges="$(gh api "repos/{owner}/{repo}/issues/$n/dependencies/blocked_by" \
      --jq '[.[] | {number, state}]')" || die "reading blocked-by edges for #$n failed"
    st_apply '.titles[$n] = $t | .edges[$n] = $e' --arg n "$n" --arg t "$title" --argjson e "$edges"
  done
}

# Frontier: move tickets whose blocker failed, was skipped or is open outside
# the run into skipped (repeat until stable); then the first queued ticket
# whose blockers are all done, closed or waived is next.
FRONTIER_DEFS='
def live_edges($n): (.waived // []) as $w | (.edges[$n | tostring] // [])
  | map(select(.number as $b | ($w | any(.[]; . == [$n, $b])) | not));
def settle:
  . as $s
  | [$s.done[].n] as $done | [$s.failed[].n] as $failed | [$s.skipped[].n] as $skipped
  | [$s.queue[] as $n
      | ($s | live_edges($n)) as $e
      | first($e[]
          | .number as $b
          | if ($failed | any(.[]; . == $b)) then {n: $n, blocker: $b, why: "blocker #\($b) failed"}
            elif ($skipped | any(.[]; . == $b)) then {n: $n, blocker: $b, why: "blocker #\($b) skipped"}
            elif (($s.planned | any(.[]; . == $b)) | not) and .state != "closed"
              then {n: $n, blocker: $b, why: "blocker #\($b) is open and not in this run"}
            else empty end)] as $new
  | if ($new | length) == 0 then .
    else .queue -= [$new[].n] | .skipped += $new | settle end;
def pick:
  . as $s | [$s.done[].n] as $done
  | first($s.queue[] as $n
      | select(all(($s | live_edges($n))[];
          .number as $b | ($done | any(.[]; . == $b))
          or ((($s.planned | any(.[]; . == $b)) | not) and .state == "closed")))
      | $n) // empty;
def run_order:
  ([pick] | first) as $n
  | if $n == null then [] else [$n] + (.queue -= [$n] | .done += [{n: $n}] | run_order) end;
'
settle_and_pick() {
  st_apply "$FRONTIER_DEFS settle"
  next="$(sget "$FRONTIER_DEFS pick")"
  if [[ -z "$next" && "$(sget '.queue | length')" != 0 ]]; then
    st_apply '.skipped += [.queue[] | {n: ., blocker: null, why: "blocker cycle inside the queue"}] | .queue = []'
  fi
}

# render_brief <n> <title> <result-file> <handoff-path|none>
render_brief() {
  local n="$1" title="$2" done_when
  done_when="$(gh issue view "$n" --json body --jq .body 2>/dev/null | acceptance_criteria || true)"
  [[ -n "$done_when" ]] ||
    done_when="The ticket states no separate acceptance criteria; treat the ticket's own wording as the criteria."
  OB_N="$n" OB_TITLE="$title" OB_RESULT_FILE="$3" OB_HANDOFF="$4" OB_DONE_WHEN="$done_when" \
    OB_IMPLEMENT_SKILL="$implement_skill" OB_CODE_REVIEW_SKILL="$code_review_skill" \
    OB_TYPECHECK="$(jq -r '.checks.typecheck // "" | if . == "" then "n/a" else . end' "$plan")" \
    OB_BUILD="$(jq -r '.checks.build // "" | if . == "" then "n/a" else . end' "$plan")" \
    OB_LINT="$(jq -r '.checks.lint // "" | if . == "" then "n/a" else . end' "$plan")" \
    OB_TEST="$(jq -r '.checks.test // "" | if . == "" then "n/a" else . end' "$plan")" \
    perl -pe 's/\{\{(\w+)\}\}/exists $ENV{"OB_$1"} ? $ENV{"OB_$1"} : $&/ge' "$here/worker-brief.md"
}

# worker_cmd <brief-file> [session-dir] — fills the worker_argv array.
worker_cmd() {
  if [[ "$worker" == claude ]]; then
    worker_argv=(env -u CLAUDECODE -u CLAUDE_CODE_ENTRYPOINT claude -p
      --output-format json --permission-mode "$CLAUDE_PERMISSION_MODE"
      --permission-prompts none --no-session-persistence)
    if ((claude_lists_max_turns)); then worker_argv+=(--max-turns "$CLAUDE_MAX_TURNS"); fi
  elif ((visible)); then
    worker_argv=(omp --auto-approve --max-time "$((TICKET_TIMEOUT_SECS / 60))m" --session-dir "$2")
  else
    worker_argv=(omp -p --mode json --auto-approve --max-time "$((TICKET_TIMEOUT_SECS / 60))m" --no-session)
  fi
  if [[ "$worker" == omp ]]; then
    worker_argv+=(--model "$model_arg")
  else
    worker_argv+=(--model "$claude_model")
    if [[ -n "$claude_effort" ]]; then worker_argv+=(--effort "$claude_effort"); fi
  fi
  if ((visible)); then worker_argv+=("@$1"); else worker_argv+=("$(cat "$1")"); fi
}

# final_text <out> — the worker's last assistant text plus any error text.
final_text() {
  if [[ "$worker" == claude ]]; then
    jq -r '[.result?, .errors[]?] | map(strings) | join("\n")' "$1" 2>/dev/null || true
  else
    jq -Rrn '[inputs | fromjson? | select(.type == "agent_end" and .isTerminal != false)]
      | last | (.messages // []) | map(select(.role == "assistant")) | last // {}
      | ([.content[]? | select(.type == "text") | .text] | join("")) + "\n" + (.errorMessage // "")' \
      "$1" 2>/dev/null || true
  fi
}

# final_json <text> — the first status-bearing JSON object in the text, compact.
final_json() {
  jq -Rsc '
    def obj: . as $t
      | (try ($t | fromjson) catch null)
        // (try ($t | sub("^\\s*```(json)?\\s*"; "") | sub("\\s*```\\s*$"; "") | fromjson) catch null)
        // (try ($t | .[index("{"):(rindex("}") + 1)] | fromjson) catch null);
    . as $all | [($all | obj), ($all | split("\n\n") | .[] | obj)]
    | map(select(type == "object" and has("status"))) | first // empty' \
    <<<"$1" 2>/dev/null || true
}

write_report() {
  local date
  date="$(sget .date)"
  jq -r '
    def hm: strflocaltime("%H:%M");
    def dur: "\(. / 60 | floor)m\(. % 60)s";
    def title($n): .titles[$n | tostring] // "";
    def cell: tostring | gsub("\\|"; "/") | gsub("\n"; " ");
    . as $s
    | "# Overnight run \(.date)", "",
      "- \(if .pr_mode then "Draft PR per ticket, stacked from `\(.pr_base)`" else "Branch `\(.branch)`" end), worker `\(.worker)`\(if .visible then " (visible)" else "" end), model `\(.model)`, gated provider `\(.provider // "anthropic")`",
      "- Started \(.started_at | hm), ended \(.ended_at // now | floor | hm), deadline \(.deadline | hm)",
      "- Stop reason: **\(.stop_reason // "still running")**",
      "- Account check: \(.account)", "",
      "## Queue", "",
      "- Planned: \(.planned | map("#\(.)") | join(", "))",
      "- Actual: \(.order | map("#\(.)") | join(", "))", "",
      "## Tickets", "",
      "| # | Title | Status | SHA / PR | Duration | Unmet criteria | Attempts |", "| --- | --- | --- | --- | --- | --- | --- |",
      (.planned[] as $n
        | ([$s.done[] | select(.n == $n)] | first) as $d
        | ([$s.failed[] | select(.n == $n)] | first) as $f
        | ([$s.skipped[] | select(.n == $n)] | first) as $k
        | (((.retries // {})[$n | tostring] // 0) + 1) as $att
        | "| #\($n) | \($s | title($n) | cell) | "
          + (if $d then "done | `\($d.sha)`\(if $d.pr then " [PR](\($d.pr))" elif $d.branch then " `\($d.branch)` (no PR)" else "" end) | \($d.secs | dur) | \($d.unmet | map(tostring) | join("; ") | cell) | \($att)"
             elif $f then "failed | — | \($f.secs | dur) | \($f.unmet | map(tostring) | join("; ") | cell) | \($att)"
             elif $k then "skipped-blocked | — | — | — | —"
             else "not run | — | — | — | —" end) + " |"),
      "", "## Failures", "",
      (if (.failed | length) == 0 then "None." else
        (.failed[] | "- #\(.n): \(.reason). "
          + (if .class then "Class: \(.class). " else "" end)
          + ((.red_checks // []) | if length > 0 then "Red checks: \(join(", ")). " else "" end)
          + ((.protected // []) | if length > 0 then "Protected paths touched: \(map("`\(.)`") | join(", ")). " else "" end)
          + (if .worktree then "Worktree `\(.worktree)` on `\(.branch)`" else "Stash `\(.stash_name)`\(if .stash then " at `\(.stash)`" else " (nothing to stash)" end)" end)
          + (if .patch then ". Patch `\(.patch)`" else "" end)
          + (if .handoff then ". Handoff `\(.handoff)`" else "" end)
          + "\(if .notes != "" then ". Worker: \(.notes | cell)" else "" end)") end),
      "", "## Skipped (blocked)", "",
      (if (.skipped | length) == 0 then "None." else (.skipped[] | "- #\(.n): \(.why)") end),
      "", "## Usage readings", "",
      (.usage[] | "- \(.at | hm) \(.label): \(.reading)"),
      "", "## Visual checks", "",
      ([.done[] as $d | ($d.routes // [])[] | "- \(.) → #\($d.n)"] | if length == 0 then "None." else .[] end)
  ' "$state" >"$dir/$date.md"
}

finished=0
stop() {
  gate
  record_usage "end"
  st_apply '.stop_reason = $r | .ended_at = (now | floor)' --arg r "$1"
  write_report
  finished=1
  log "stopped: $1 — report $dir/$(sget .date).md"
  notify "overnight run stopped" "$1"
  exit "${2:-0}"
}

on_exit() {
  local rc=$?
  if [[ -n "$active_pid" ]]; then
    kill -TERM -- "-$active_pid" 2>/dev/null || true
  fi
  if [[ -n "$active_tab" ]]; then
    herdr tab close "$active_tab" >/dev/null 2>&1 || true
  fi
  if ((!finished)) && [[ -f "$state" ]]; then
    st_apply '.stop_reason = (.stop_reason // $r) | .ended_at = (now | floor)' \
      --arg r "aborted (exit $rc); continue with --resume"
    write_report || true
    notify "overnight run aborted" "exit $rc; continue with --resume"
  fi
}

# --- one ticket ------------------------------------------------------------

requeue() {
  local n="$1" why="$2"
  if ((pr_mode)); then
    drop_worktree "$n" ""
  else
    git reset -q --hard
    git clean -fdq
  fi
  st_apply '.queue = [$n] + (.queue - [$n]) | .requeues[$n | tostring] += 1 | .current = null' --argjson n "$n"
  gate
  record_usage "requeued #$n: $why"
  log "#$n requeued ($why); gate: $gate_reading"
  if (($(sget ".requeues[\"$n\"]") > MAX_REQUEUES)); then
    stop "rate limit persists on #$n after $MAX_REQUEUES requeues"
  fi
  if [[ "$gate_code" == 0 ]]; then
    (($(date +%s) + RATE_LIMIT_BACKOFF_SECS + TICKET_TIMEOUT_SECS <= deadline)) || stop "deadline"
    log "gate sees no limit; backing off ${RATE_LIMIT_BACKOFF_SECS}s"
    idle "$RATE_LIMIT_BACKOFF_SECS"
  fi
}

# ticket_slug <title> — lower-case and hyphenated, at most 40 characters.
ticket_slug() {
  tr '[:upper:]' '[:lower:]' <<<"$1" | tr -cs 'a-z0-9' '-' | cut -c 1-40 | sed -E 's/^-+//; s/-+$//'
}

# drop_worktree <n> <label> — PR mode: remove ticket n's worktree and branch
# (tbranch, wt), stashing uncommitted work as "overnight #n <label>" when label
# is non-empty. Leaves the shell in $root.
drop_worktree() {
  local n="$1" label="$2"
  cd "$root"
  if [[ -d "$wt" ]]; then
    if [[ -n "$label" && -n "$(git -C "$wt" status --porcelain 2>/dev/null)" ]]; then
      (cd "$wt" && purge_protected "$(protected_hits)")
      git -C "$wt" stash push -u -q -m "overnight #$n $label"
      log "stashed #$n $label work as 'overnight #$n $label'"
    fi
    git worktree remove --force "$wt"
  fi
  git worktree prune
  if git show-ref -q --verify "refs/heads/$tbranch"; then git branch -q -D "$tbranch"; fi
}

# open_worktree <n> <title> — PR mode: a fresh worktree for ticket n on the
# stack base, set up and entered; sets tbranch, tbase and wt. Returns 1 when
# setup fails (the worktree stays entered and in place).
open_worktree() {
  local n="$1" baseref
  tbranch="ticket/$n-$(ticket_slug "$2")"
  tbase="$(sget ".stack_base // \"$PR_BASE\"")"
  wt="$worktrees/$n"
  drop_worktree "$n" "interrupted" # leftovers from an interrupted attempt
  git fetch -q origin "$PR_BASE"
  if [[ "$tbase" == "$PR_BASE" ]]; then baseref="origin/$PR_BASE"; else baseref="$tbase"; fi
  mkdir -p "$worktrees"
  git worktree add -q -b "$tbranch" "$wt" "$baseref"
  cd "$wt"
  if [[ -n "$setup_cmd" ]] && ! run_with_timeout "$CHECK_TIMEOUT_SECS" "$dir/logs/$n-setup.log" \
    "$dir/logs/$n-setup.log" bash -c "$setup_cmd"; then
    return 1
  fi
}

# publish <n> <subject> <result> — PR mode: push tbranch and open a draft PR
# against tbase; sets pr_url, "" when either step failed.
publish() {
  local n="$1" subject="$2" result="$3" body publog
  publog="$dir/logs/$n-publish.log"
  pr_url=""
  if ! git push -q -u origin "$tbranch" >>"$publog" 2>&1; then
    log "#$n push failed; see $publog"
    return
  fi
  body="$(jq -r --arg n "$n" --arg base "$tbase" --arg root_base "$PR_BASE" --arg date "$(sget .date)" '
    def list: if type == "array" then . else [.] end | map(tostring)
      | if length == 0 then "None." else map("- " + .) | join("\n") end;
    "Closes #\($n).", "",
    (if $base != $root_base
      then "Stacked on `\($base)`: merge that PR first, with a merge commit or rebase rather than a squash.\n"
      else empty end),
    "Draft opened by the overnight run on \($date); not yet reviewed by a human.", "",
    "## Worker notes", "", (.notes // "" | if . == "" then "None." else . end), "",
    "## Unmet criteria", "", (.unmet_criteria // [] | list), "",
    "## Routes to check", "", (.routes_to_check // [] | list)' <<<"$result")"
  if ! pr_url="$(gh pr create --draft --base "$tbase" --head "$tbranch" \
    --title "$subject (#$n)" --body "$body" 2>>"$publog")"; then
    pr_url=""
    log "#$n draft PR failed; see $publog"
  fi
}

# write_handoff <n> <k> <reason> <class> <retry> <patch> <result-obj> <file> —
# one Markdown note per ticket, overwritten by each retry and final failure.
write_handoff() {
  local n="$1" k="$2" reason="$3" class="$4" retry="$5" patch="$6" robj="$7" file="$8"
  {
    echo "# Handoff: #$n attempt $k"
    echo
    echo "- Reason: $reason"
    echo "- Class: $class$( ((retry)) && echo ' (retrying once)' || echo ' (final)')"
    echo "- Patch: ${patch:-none}"
    echo
    echo "## Diff stat"
    echo
    echo '```'
    git diff --cached --stat HEAD 2>/dev/null || true
    echo '```'
    if [[ -n "$gate_red_log" && -f "$gate_red_log" ]]; then
      echo
      echo "## Red check: ${gate_red_keys%% *} (last 40 lines of $gate_red_log)"
      echo
      echo '```'
      tail -n 40 "$gate_red_log"
      echo '```'
    fi
    echo
    echo "## Worker notes"
    echo
    jq -r '.notes // "" | if . == "" then "None." else . end' <<<"$robj"
    echo
    echo "## Unmet criteria"
    echo
    jq -r '.unmet_criteria // [] | if type == "array" then . else [.] end
      | if length == 0 then "None." else map("- \(.)") | join("\n") end' <<<"$robj"
  } >"$file"
}

# fail_ticket <n> <reason> <temporary|permanent> <result-obj> <secs> <unmet-json> <keep-patch 0|1>
# — the tail of a failed attempt, after the protected-paths check: save the
# attempt as a patch, write the handoff note, then reset for one retry
# (temporary, retry left, room for a whole attempt) or record the final failure.
fail_ticket() {
  local n="$1" reason="$2" class="$3" robj="$4" secs="$5" unmet="$6" keep_patch="$7"
  local retries k patch="" hand="$dir/logs/$n.handoff.md" retry=0 stash=""
  retries="$(sget "(.retries // {})[\"$n\"] // 0")"
  k=$((retries + 1))
  if [[ "$class" == temporary ]] && ((retries < MAX_RETRIES)) &&
    (($(date +%s) + TICKET_TIMEOUT_SECS <= deadline)); then
    retry=1
  fi
  if ((keep_patch)); then
    patch="$dir/logs/$n-attempt$k.patch"
    git add -A
    git diff --cached --binary HEAD >"$patch"
  fi
  write_handoff "$n" "$k" "$reason" "$class" "$retry" "$patch" "$robj" "$hand"

  if ((retry)); then
    if ((pr_mode)); then
      drop_worktree "$n" ""
    elif [[ -n "$(git status --porcelain)" ]]; then
      git stash push -u -q -m "overnight #$n attempt $k"
    fi
    st_apply '.retries = (.retries // {}) | .retries[$n | tostring] += 1 | .current = null' --argjson n "$n"
    log "#$n failed ($reason); temporary, will retry once${patch:+ from $patch}"
    if ((!pr_mode)); then
      build_gate "$n-after-stash" static || stop "red build after stashing #$n attempt $k: $gate_failures" 1
    fi
    return
  fi

  local extra=(--arg class "$class" --arg red "$gate_red_keys" --arg prot "$protected_hit"
    --arg patch "$patch" --arg hand "$hand")
  local fields='class: $class, red_checks: ($red | split(" ") | map(select(. != ""))),
    protected: ($prot | split("\n") | map(select(. != ""))),
    patch: (if $patch == "" then null else $patch end), handoff: $hand'
  if ((pr_mode)); then
    st_apply ".failed += [{n: \$n, reason: \$reason, worktree: \$wt, branch: \$tb, secs: \$secs,
        unmet: \$unmet, notes: (\$r.notes // \"\"), $fields}]
      | .order += [\$n] | .queue -= [\$n] | .current = null" \
      --argjson n "$n" --arg reason "$reason" --arg wt "$wt" --arg tb "$tbranch" \
      --argjson secs "$secs" --argjson unmet "$unmet" --argjson r "$robj" "${extra[@]}"
    log "#$n failed ($class): $reason (worktree $wt kept)"
    return
  fi
  if [[ -n "$(git status --porcelain)" ]]; then
    git stash push -u -q -m "overnight #$n"
    stash="$(git rev-parse --short refs/stash)"
  fi
  st_apply ".failed += [{n: \$n, reason: \$reason, stash_name: \"overnight #\(\$n)\",
      stash: (if \$stash == \"\" then null else \$stash end), secs: \$secs, unmet: \$unmet,
      notes: (\$r.notes // \"\"), $fields}]
    | .order += [\$n] | .queue -= [\$n] | .current = null" \
    --argjson n "$n" --arg reason "$reason" --arg stash "$stash" --argjson secs "$secs" \
    --argjson unmet "$unmet" --argjson r "$robj" "${extra[@]}"
  log "#$n failed ($class): $reason${stash:+ (stash $stash)}"
  build_gate "$n-after-stash" static || stop "red build after stashing #$n: $gate_failures" 1
}

run_ticket() {
  local n="$1" title k retries out err brief start secs rc=0 text result status unmet reason class
  local sessions resultf head_before pr_url="" handoff handoff_ref=none patch_prev
  title="$(sget ".titles[\"$n\"] // \"\"")"
  retries="$(sget "(.retries // {})[\"$n\"] // 0")"
  k=$((retries + 1))
  handoff="$dir/logs/$n.handoff.md"
  patch_prev="$dir/logs/$n-attempt$retries.patch"
  # A first attempt owns its files: leftovers belong to an earlier run.
  if ((retries == 0)); then rm -f "$handoff" "$dir/logs/$n-attempt"*.patch; fi
  gate_failures="" gate_red_keys="" gate_red_log="" protected_hit=""
  st_apply '.current = $n | .tickets_run += 1' --argjson n "$n"
  out="$dir/logs/$(sget .tickets_run)-$n.out" # one set per worker start, resumes included
  err="${out%.out}.err"
  brief="${out%.out}.brief.md"
  resultf="${out%.out}.result.json"
  sessions="$dir/sessions/$(sget .tickets_run)-$n"
  if ((pr_mode)); then
    if ! open_worktree "$n" "$title"; then
      log "#$n setup failed; see $dir/logs/$n-setup.log"
      fail_ticket "$n" "setup failed: see $dir/logs/$n-setup.log" temporary '{}' 0 '[]' 0
      return
    fi
  else
    tbranch="$branch"
  fi
  if ((retries > 0)); then
    if [[ -s "$patch_prev" ]]; then
      if git apply --index --binary "$patch_prev" 2>>"$dir/logs/$n-apply.log"; then
        printf '\n## Retry\n\nPrevious patch applied: the working tree holds attempt %s.\n' "$retries" >>"$handoff"
      else
        if ((!pr_mode)); then
          git reset -q --hard
          git clean -fdq
        fi
        printf '\n## Retry\n\nprevious patch did not apply; started clean\n' >>"$handoff"
        log "#$n previous patch did not apply; started clean"
      fi
    else
      printf '\n## Retry\n\nNo previous patch; started clean.\n' >>"$handoff"
    fi
    if [[ -f "$handoff" ]]; then handoff_ref="$handoff"; fi
  fi
  render_brief "$n" "$title" "$resultf" "$handoff_ref" >"$brief"
  worker_cmd "$brief" "$sessions"
  head_before="$(git rev-parse HEAD)"
  if ((pr_mode)); then
    log "#$n start (attempt $k): $title — $tbranch on $tbase in $wt"
  else
    log "#$n start (attempt $k): $title"
  fi
  start="$(date +%s)"
  local timeout_secs="$TICKET_TIMEOUT_SECS"
  [[ "$worker" == omp ]] && timeout_secs=$((TICKET_TIMEOUT_SECS + 120)) # omp --max-time fires first
  if ((visible)); then
    mkdir -p "$sessions"
    : >"$err"
    run_visible "$timeout_secs" "$n" "$sessions" "$resultf" || rc=$?
  else
    run_with_timeout "$timeout_secs" "$out" "$err" "${worker_argv[@]}" || rc=$?
  fi
  secs=$(($(date +%s) - start))

  # The brief forbids branch and commit changes; repair or halt if one happened.
  [[ "$(git branch --show-current)" == "$tbranch" ]] || stop "worker on #$n left branch $tbranch" 1
  if [[ "$(git rev-parse HEAD)" != "$head_before" ]]; then
    git reset -q --soft "$head_before"
    log "#$n worker committed; folded its commits back into the working tree"
  fi

  if [[ -s "$resultf" ]]; then
    text="$(cat "$resultf")"
  elif ((visible)); then
    text="$(session_tail "$sessions" | cut -f 2-)"
  else
    text="$(final_text "$out")"
  fi
  result="$(final_json "$text")"

  # A rejected model fails every ticket the same way: stop before any retry,
  # patch, stash or gate call, leaving .current so --resume stashes the tree.
  if ((rc != 0)) && { grep -Eq "$MODEL_MISSING_RE" "$err" || grep -Eq "$MODEL_MISSING_RE" <<<"$text"; }; then
    stop "worker model '$model_arg' rejected on #$n; fix the model and --resume" 1
  fi
  local robj="${result:-}"
  [[ -n "$robj" ]] || robj='{}'
  status="$(jq -r '.status // ""' <<<"$robj")"
  unmet="$(jq -c '.unmet_criteria // [] | if type == "array" then . else [.] end' <<<"$robj")"

  local limit_hit=0
  if grep -Eq "$LIMIT_RE" <<<"$text" || grep -Eq "$LIMIT_RE" "$err" ||
    { ((visible)) && grep -Eq "$LIMIT_RE" <<<"$(session_tail "$sessions")"; }; then
    limit_hit=1
  fi
  if ((limit_hit)); then
    requeue "$n" "rate-limit text in worker output"
    return
  fi
  if ((rc != 0 || timed_out)) || [[ "$status" != "done" ]]; then
    gate
    if [[ "$gate_code" == 10 || "$gate_code" == 20 ]]; then
      requeue "$n" "worker failed while the gate reads $gate_code"
      return
    fi
  fi

  # Protected paths: once per attempt, before any patch, stash or commit. The
  # files are removed first, so they reach none of them.
  protected_hit="$(protected_hits)"
  if [[ -n "$protected_hit" ]]; then
    purge_protected "$protected_hit"
    reason="protected paths touched: $(paste -sd ' ' - <<<"$protected_hit")"
    class=permanent
  elif ((timed_out)); then
    reason="timed out after $((secs / 60))m$((secs % 60))s"
    class=temporary
  elif ((rc != 0)); then
    reason="worker exited $rc"
    class=temporary
  elif [[ -z "$result" ]]; then
    reason="no final JSON from worker"
    class=temporary
  elif [[ "$status" == blocked ]]; then
    reason="worker reported blocked"
    class=permanent
  elif [[ "$status" != "done" ]]; then
    reason="worker reported $status"
    class=temporary
  elif [[ -z "$(git status --porcelain)" ]]; then
    reason="worker reported done but changed nothing"
    class=permanent
  elif ! build_gate "$n" full; then
    reason="checks red: $gate_failures"
    class=temporary
  else
    local subject stat sha
    subject="$(jq -r '.commit_subject // ""' <<<"$result" | head -n 1 | sed -E 's/[[:space:]]*\(#[0-9]+\)[[:space:]]*$//')"
    [[ -n "$subject" ]] || subject="$title"
    git add -A
    stat="$(git diff --cached --shortstat)"
    if git commit -q -m "$subject (#$n)"; then
      sha="$(git rev-parse --short HEAD)"
      if ((pr_mode)); then
        publish "$n" "$subject" "$result"
        st_apply '.stack_base = $b' --arg b "$tbranch" # dependants need this code, PR or not
        cd "$root"
        git worktree remove --force "$wt" || log "#$n worktree $wt left in place"
      fi
      st_apply '.done += [{n: $n, sha: $sha, secs: $secs, unmet: $unmet, stat: $stat,
          branch: (if $pm == 1 then $tb else null end), pr: (if $pr == "" then null else $pr end),
          routes: ($r.routes_to_check // []), checks: ($r.checks // {}), notes: ($r.notes // "")}]
        | .order += [$n] | .queue -= [$n] | .current = null' \
        --argjson n "$n" --arg sha "$sha" --argjson secs "$secs" --argjson unmet "$unmet" \
        --arg stat "$stat" --argjson r "$result" --argjson pm "$pr_mode" \
        --arg tb "$tbranch" --arg pr "$pr_url"
      log "#$n done: $sha $stat${pr_url:+ · $pr_url}"
      return
    fi
    git reset -q
    reason="git commit failed (hook?)"
    class=permanent
  fi
  fail_ticket "$n" "$reason" "$class" "$robj" "$secs" "$unmet" 1
}

# --- setup -----------------------------------------------------------------

branch="$(git branch --show-current)"
visible_req="$visible" # what the command line asked for; empty = auto
if ((resume)); then
  [[ -f "$state" ]] || die "--resume needs $state"
  [[ "$(sget .branch)" == "$branch" ]] || die "state.json is for $(sget .branch); $branch is checked out"
  [[ -n "$worker" ]] || worker="$(sget .worker)"
  [[ -n "$visible" ]] || visible="$(sget '.visible // false | if . then 1 else 0 end')"
  ((pr_mode)) || pr_mode="$(sget '.pr_mode // false | if . then 1 else 0 end')"
fi
if [[ -z "$worker" ]]; then
  if [[ -n "${CLAUDECODE:-}" ]]; then worker=claude; else worker=omp; fi
fi
[[ "$worker" == claude || "$worker" == omp ]] || die "--worker must be claude or omp"
in_herdr=0
if [[ -n "${HERDR_WORKSPACE_ID:-}" ]] && command -v herdr >/dev/null 2>&1; then in_herdr=1; fi
if [[ -z "$visible" ]]; then
  if [[ "$worker" == omp ]] && ((in_herdr)); then visible=1; else visible=0; fi
fi
command -v "$worker" >/dev/null 2>&1 || die "$worker not on PATH"
if ((visible)); then
  [[ "$worker" == omp ]] || die "--visible needs --worker omp"
  if ((!in_herdr)); then
    die "--visible needs to run inside a herdr pane"
  fi
fi
if ((visible)); then
  visible_line="yes — one herdr tab per worker (omp TUI), idle after ${VISIBLE_IDLE_SECS}s"
elif [[ "$worker" == claude ]]; then
  visible_line="no (claude worker is headless)"
elif [[ "$visible_req" == 0 ]]; then
  visible_line="no (--headless)"
elif ((!in_herdr)); then
  visible_line="no (not inside herdr)"
else
  visible_line="no (resumed run was headless)"
fi
setup_cmd="$(jq -r '.setup // ""' "$plan")"
worktrees="$root-overnight"
if ((pr_mode)); then
  git remote get-url origin >/dev/null 2>&1 || die "--pr-per-ticket needs an origin remote"
  gh auth status >/dev/null 2>&1 || die "--pr-per-ticket needs gh to be logged in"
fi
implement_skill="$(skill_path implement)" || die "implement skill not installed"
code_review_skill="$(skill_path code-review)" || die "code-review skill not installed"
claude_help=""
if [[ "$worker" == claude ]]; then claude_help="$(claude --help 2>/dev/null || true)"; fi
claude_lists_max_turns=0 claude_lists_effort=0
if grep -q -- '--max-turns' <<<"$claude_help"; then claude_lists_max_turns=1; fi
if grep -q -- '--effort' <<<"$claude_help"; then claude_lists_effort=1; fi
resolve_model
check_model
deadline="$(deadline_epoch)"
account="$(account_check)"
mkdir -p "$dir/logs"

new_state() {
  jq -n --argjson plan "$(cat "$plan")" --arg branch "$branch" --arg worker "$worker" \
    --arg model "$model" --arg model_arg "$model_arg" --arg provider "$provider" \
    --argjson deadline "$deadline" --arg account "$account" --argjson pid "$$" \
    --arg date "$(date +%Y-%m-%d)" --argjson visible "$visible" --argjson pr_mode "$pr_mode" \
    --arg pr_base "$PR_BASE" '
    {date: $date, branch: $branch, worker: $worker, model: $model, model_arg: $model_arg, pid: $pid,
     provider: $provider, account: $account,
     visible: ($visible == 1), pr_mode: ($pr_mode == 1), pr_base: $pr_base, stack_base: null,
     started_at: (now | floor), ended_at: null, deadline: $deadline,
     planned: $plan.queue, queue: $plan.queue, waived: ($plan.waived // []),
     titles: {}, edges: {}, done: [], failed: [], skipped: [], order: [], usage: [],
     tickets_run: 0, requeues: {}, retries: {}, current: null, stop_reason: null}'
}

if ((dry_run)); then
  state="$(mktemp)"
  trap 'rm -f "$state" "$state.tmp"' EXIT
  new_state >"$state"
  fetch_tracker
  st_apply "$FRONTIER_DEFS settle"
  worker_cmd /dev/null "$dir/sessions/<run>-<N>"
  gate
  echo "overnight dry run — nothing will run"
  echo "  repo        $root"
  echo "  branch      $branch (plan: $(jq -r '.branch // "unset"' "$plan"))"
  printf '  worker     '
  printf ' %q' "${worker_argv[@]:0:${#worker_argv[@]}-1}"
  printf ' "<worker-brief.md for #N>"'
  echo
  if [[ "$worker" == claude ]] && ((!claude_lists_max_turns)); then
    echo "              (--max-turns omitted: not listed in claude --help; bounded by the timeout)"
  fi
  echo "  model       $model_arg — from $model_source; $model_check"
  echo "  gate provider  $provider"
  echo "  visible     $visible_line"
  if ((pr_mode)); then
    echo "  PRs         worktrees in $worktrees; ticket/<N>-<slug> stacked from origin/$PR_BASE; draft PR per pass"
    echo "  setup       ${setup_cmd:-none}"
  fi
  echo "  skills      $implement_skill · $code_review_skill"
  echo "  build gate  $(jq -r '[.checks | to_entries[] | "\(.key): \(if .value == "" then "n/a" else .value end)"] | join(" · ")' "$plan") (test skipped in the after-stash health check)"
  echo "  protected   $PROTECTED_RE"
  echo "  limits      deadline $(date -r "$deadline" '+%a %H:%M' 2>/dev/null || date -d "@$deadline" '+%a %H:%M'), $((TICKET_TIMEOUT_SECS / 60))m per ticket, max tickets $([[ "$max_tickets" == 0 ]] && echo unlimited || echo "$max_tickets")"
  echo "  thresholds  5h sleep ≥${FIVE_HOUR_SLEEP_PCT}% · 7d pace +${PACE_MARGIN_PCT}% over elapsed (past ${PACE_MIN_ELAPSED_PCT}%) or ≥${SEVEN_DAY_STOP_PCT}%$([[ "$provider" == anthropic ]] || echo " · monthly (no window length) hard stop ≥${SEVEN_DAY_STOP_PCT}%") · unknown-gate cap ${FALLBACK_MAX_TICKETS} tickets"
  echo "  account     $account"
  echo "  gate        exit $gate_code — $gate_reading${gate_secs:+ (sleep ${gate_secs}s)}"
  git check-ignore -q "$dir/state.json" || echo "  note        $dir/ is not git-ignored yet; a real run adds it to .git/info/exclude"
  echo "  run order if every ticket succeeds:"
  [[ "$(sget '.queue | length')" == 0 ]] && echo "    (empty)"
  sget "$FRONTIER_DEFS"'
    . as $s | (run_order) as $order
    | ($order[] as $n | "    #\($n) \($s.titles[$n | tostring])" + (
        [($s.edges[$n | tostring] // [])[] | select(.state != "closed")
         | .number as $b
         | "#\($b) " + (if ($s.waived | any(.[]; . == [$n, $b])) then "open, waived" else "in run" end)]
        | if length == 0 then "" else " — after " + join(", ") end)),
      ($s.queue - $order | .[] | "    #\(.) blocker cycle inside the queue — would be skipped")'
  if [[ "$(sget '.skipped | length')" != 0 ]]; then
    echo "  skipped-blocked:"
    sget '.skipped[] | "    #\(.n) \(.why)"'
  fi
  no_criteria=""
  for n in $(sget '.queue[]'); do
    body="$(gh issue view "$n" --json body --jq .body)" || die "gh issue view $n failed"
    [[ -n "$(acceptance_criteria <<<"$body")" ]] || no_criteria="${no_criteria:+$no_criteria, }#$n"
  done
  echo "  no acceptance criteria: ${no_criteria:-none}"
  exit 0
fi

[[ "$branch" == "$(jq -r '.branch // ""' "$plan")" ]] || die "checked-out branch $branch is not the plan's branch"
ensure_ignored
if ((resume)); then
  if [[ -n "$(git status --porcelain)" ]]; then
    current="$(sget '.current // empty')"
    [[ -n "$current" ]] || die "dirty tree and no interrupted ticket in state.json; clean it by hand"
    purge_protected "$(protected_hits)" # protected files never reach a stash
    git stash push -u -q -m "overnight #$current interrupted"
    log "stashed interrupted #$current work as 'overnight #$current interrupted'"
  fi
  st_apply '.current = null | .stop_reason = null | .ended_at = null | .deadline = $d | .worker = $w
      | .visible = ($v == 1) | .pr_mode = ($p == 1) | .pr_base = (.pr_base // $b)
      | .model = $m | .model_arg = $ma | .provider = $pv | .retries = (.retries // {}) | .pid = $pid' \
    --argjson d "$deadline" --arg w "$worker" --argjson v "$visible" --argjson p "$pr_mode" --arg b "$PR_BASE" \
    --arg m "$model" --arg ma "$model_arg" --arg pv "$provider" --argjson pid "$$"
else
  [[ ! -f "$state" ]] || die "$state exists; pass --resume or move it aside"
  [[ -z "$(git status --porcelain)" ]] || die "working tree is not clean"
  new_state >"$state"
fi
trap on_exit EXIT
trap 'exit 129' HUP
trap 'exit 130' INT
trap 'exit 143' TERM
rm -f "$stop_file" # a stale request never stops a new run
fetch_tracker
gate
record_usage "start"
log "overnight run on $branch with $worker, model $model_arg, visible: $visible_line; gate: $gate_reading"

# --- the loop --------------------------------------------------------------

while :; do
  if [[ -f "$stop_file" ]]; then
    rm -f "$stop_file"
    stop "stop requested"
  fi
  settle_and_pick
  [[ -n "$next" ]] || stop "queue empty"
  if ((max_tickets > 0 && $(sget .tickets_run) >= max_tickets)); then stop "max tickets ($max_tickets)"; fi
  gate
  case "$gate_code" in
  0) ;;
  10)
    (($(date +%s) + gate_secs + TICKET_TIMEOUT_SECS <= deadline)) || stop "deadline (5h window resets too late)"
    record_usage "sleep ${gate_secs}s"
    log "5h window over ${FIVE_HOUR_SLEEP_PCT}%; sleeping ${gate_secs}s"
    idle "$gate_secs"
    continue
    ;;
  20) stop "weekly limit" ;;
  *)
    if (($(sget .tickets_run) >= FALLBACK_MAX_TICKETS)); then stop "fallback cap ($FALLBACK_MAX_TICKETS tickets on an unknown gate)"; fi
    record_usage "unknown gate, ticket $(($(sget .tickets_run) + 1)) of $FALLBACK_MAX_TICKETS"
    ;;
  esac
  (($(date +%s) + TICKET_TIMEOUT_SECS <= deadline)) || stop "deadline"
  run_ticket "$next"
  cd "$root"
done
