#!/usr/bin/env bash
# overnight.sh — the only loop of the overnight-run skill.
#
# Strictly serial: gate usage, run one fresh worker per ready-for-agent ticket,
# gate the build, commit or stash, repeat. The invoking agent session only
# writes .scratch/overnight/plan.json and launches this under tmux (or a herdr
# tab) with caffeinate.
#
#   overnight.sh [--dry-run] [--deadline HH:MM] [--max-tickets N]
#                [--worker claude|omp] [--visible] [--pr-per-ticket] [--resume]
#
# --visible        omp worker only, inside herdr: each worker runs as the
#                  interactive omp TUI in its own herdr tab, closed when it ends.
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
# "" means the repo has no such command. test goes to the worker only; the
# build gate is typecheck + build + lint.
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
WORKER_MODEL="${OVERNIGHT_WORKER_MODEL:-}"                             # empty = the harness default
RATE_LIMIT_BACKOFF_SECS="${OVERNIGHT_RATE_LIMIT_BACKOFF_SECS:-1800}" # limit the gate cannot see
MAX_REQUEUES=3                                                       # per ticket, then the run stops
PR_BASE="${OVERNIGHT_PR_BASE:-main}"                                 # --pr-per-ticket stack root
VISIBLE_IDLE_SECS=60 # --visible: quiet time after a terminal turn that counts as finished
LIMIT_RE="You('|’)ve hit your .* limit|Request rejected \(429\)"

die() {
  echo "overnight: $*" >&2
  exit 1
}
log() { printf '%s  %s\n' "$(date '+%H:%M:%S')" "$*"; }

# --- arguments -------------------------------------------------------------

dry_run=0
resume=0
deadline_hm="07:00"
max_tickets=0
worker=""
visible=0
pr_mode=0
while (($#)); do
  case "$1" in
  --dry-run) dry_run=1 ;;
  --resume) resume=1 ;;
  --visible) visible=1 ;;
  --pr-per-ticket) pr_mode=1 ;;
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

resolve_model() {
  if [[ -n "$WORKER_MODEL" ]]; then
    echo "$WORKER_MODEL"
  elif [[ "$worker" == claude ]]; then
    jq -r '.model // empty' "$HOME/.claude/settings.json" 2>/dev/null || true
  else
    omp config get modelRoles --json 2>/dev/null | jq -r '.value.default // empty' 2>/dev/null || true
  fi
}

# The gate reads omp's Anthropic login. A claude worker must be on the same
# org, or the reading describes somebody else's quota.
account_check() {
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
  gate_secs="$(bash "$here/usage-gate.sh" ${model:+--model "$model"} 2>"$errf")" || gate_code=$?
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
  local launcher="${result%.result.json}.worker.sh"
  printf 'export PATH=%q\nexec %s\n' "$PATH" "$(printf '%q ' "${worker_argv[@]}")" >"$launcher"
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

# build_gate <label> — runs typecheck, build, lint; sets gate_failures.
build_gate() {
  local label="$1" key cmd timed_out=0
  gate_failures=""
  for key in typecheck build lint; do
    cmd="$(jq -r --arg k "$key" '.checks[$k] // ""' "$plan")"
    [[ -n "$cmd" ]] || continue
    if ! run_with_timeout "$CHECK_TIMEOUT_SECS" "$dir/logs/$label-$key.log" "$dir/logs/$label-$key.log" \
      bash -c "$cmd"; then
      gate_failures="${gate_failures:+$gate_failures, }$key"
    elif ((timed_out)); then
      gate_failures="${gate_failures:+$gate_failures, }$key (timeout)"
    fi
  done
  [[ -z "$gate_failures" ]]
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

render_brief() {
  local n="$1" title="$2"
  OB_N="$n" OB_TITLE="$title" OB_RESULT_FILE="$3" OB_IMPLEMENT_SKILL="$implement_skill" \
    OB_CODE_REVIEW_SKILL="$code_review_skill" \
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
  if [[ -n "$WORKER_MODEL" ]]; then worker_argv+=(--model "$WORKER_MODEL"); fi
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
      "- \(if .pr_mode then "Draft PR per ticket, stacked from `\(.pr_base)`" else "Branch `\(.branch)`" end), worker `\(.worker)`\(if .visible then " (visible)" else "" end), model \(.model // "" | if . == "" then "harness default" else "`\(.)`" end)",
      "- Started \(.started_at | hm), ended \(.ended_at // now | floor | hm), deadline \(.deadline | hm)",
      "- Stop reason: **\(.stop_reason // "still running")**",
      "- Account check: \(.account)", "",
      "## Queue", "",
      "- Planned: \(.planned | map("#\(.)") | join(", "))",
      "- Actual: \(.order | map("#\(.)") | join(", "))", "",
      "## Tickets", "",
      "| # | Title | Status | SHA / PR | Duration | Unmet criteria |", "| --- | --- | --- | --- | --- | --- |",
      (.planned[] as $n
        | ([$s.done[] | select(.n == $n)] | first) as $d
        | ([$s.failed[] | select(.n == $n)] | first) as $f
        | ([$s.skipped[] | select(.n == $n)] | first) as $k
        | "| #\($n) | \($s | title($n) | cell) | "
          + (if $d then "done | `\($d.sha)`\(if $d.pr then " [PR](\($d.pr))" elif $d.branch then " `\($d.branch)` (no PR)" else "" end) | \($d.secs | dur) | \($d.unmet | map(tostring) | join("; ") | cell)"
             elif $f then "failed | — | \($f.secs | dur) | \($f.unmet | map(tostring) | join("; ") | cell)"
             elif $k then "skipped-blocked | — | — | —"
             else "not run | — | — | —" end) + " |"),
      "", "## Failures", "",
      (if (.failed | length) == 0 then "None." else
        (.failed[] | "- #\(.n): \(.reason). " + (if .worktree then "Worktree `\(.worktree)` on `\(.branch)`" else "Stash `\(.stash_name)`\(if .stash then " at `\(.stash)`" else " (nothing to stash)" end)" end) + "\(if .notes != "" then ". Worker: \(.notes | cell)" else "" end)") end),
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
  st_apply '.stop_reason = $r | .ended_at = (now | floor) | .current = null' --arg r "$1"
  write_report
  finished=1
  log "stopped: $1 — report $dir/$(sget .date).md"
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
    nap "$RATE_LIMIT_BACKOFF_SECS"
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
      git -C "$wt" stash push -u -q -m "overnight #$n $label"
      log "stashed #$n $label work as 'overnight #$n $label'"
    fi
    git worktree remove --force "$wt"
  fi
  git worktree prune
  if git show-ref -q --verify "refs/heads/$tbranch"; then git branch -q -D "$tbranch"; fi
}

# open_worktree <n> <title> — PR mode: a fresh worktree for ticket n on the
# stack base, set up and entered; sets tbranch, tbase and wt.
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
    stop "setup failed in $wt: see $dir/logs/$n-setup.log" 1
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

run_ticket() {
  local n="$1" title attempt out err brief start secs rc=0 text result status unmet reason
  local sessions resultf head_before pr_url=""
  title="$(sget ".titles[\"$n\"] // \"\"")"
  attempt=$(($(sget ".requeues[\"$n\"] // 0") + 1))
  st_apply '.current = $n | .tickets_run += 1' --argjson n "$n"
  out="$dir/logs/$(sget .tickets_run)-$n.out" # one set per worker start, resumes included
  err="${out%.out}.err"
  brief="${out%.out}.brief.md"
  resultf="${out%.out}.result.json"
  sessions="$dir/sessions/$(sget .tickets_run)-$n"
  if ((pr_mode)); then open_worktree "$n" "$title"; else tbranch="$branch"; fi
  render_brief "$n" "$title" "$resultf" >"$brief"
  worker_cmd "$brief" "$sessions"
  head_before="$(git rev-parse HEAD)"
  if ((pr_mode)); then
    log "#$n start (attempt $attempt): $title — $tbranch on $tbase in $wt"
  else
    log "#$n start (attempt $attempt): $title"
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

  if ((timed_out)); then
    reason="timed out after $((secs / 60))m$((secs % 60))s"
  elif ((rc != 0)); then
    reason="worker exited $rc"
  elif [[ -z "$result" ]]; then
    reason="no final JSON from worker"
  elif [[ "$status" != "done" ]]; then
    reason="worker reported $status"
  elif [[ -z "$(git status --porcelain)" ]]; then
    reason="worker reported done but changed nothing"
  elif ! build_gate "$n"; then
    reason="build gate red: $gate_failures"
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
  fi

  if ((pr_mode)); then
    st_apply '.failed += [{n: $n, reason: $reason, worktree: $wt, branch: $tb, secs: $secs,
        unmet: $unmet, notes: ($r.notes // "")}]
      | .order += [$n] | .queue -= [$n] | .current = null' \
      --argjson n "$n" --arg reason "$reason" --arg wt "$wt" --arg tb "$tbranch" \
      --argjson secs "$secs" --argjson unmet "$unmet" --argjson r "$robj"
    log "#$n failed: $reason (worktree $wt kept)"
    return
  fi
  local stash=""
  if [[ -n "$(git status --porcelain)" ]]; then
    git stash push -u -q -m "overnight #$n"
    stash="$(git rev-parse --short refs/stash)"
  fi
  st_apply '.failed += [{n: $n, reason: $reason, stash_name: "overnight #\($n)",
      stash: (if $stash == "" then null else $stash end), secs: $secs, unmet: $unmet,
      notes: ($r.notes // "")}]
    | .order += [$n] | .queue -= [$n] | .current = null' \
    --argjson n "$n" --arg reason "$reason" --arg stash "$stash" --argjson secs "$secs" \
    --argjson unmet "$unmet" --argjson r "$robj"
  log "#$n failed: $reason${stash:+ (stash $stash)}"
  build_gate "$n-after-stash" || stop "red build after stashing #$n: $gate_failures" 1
}

# --- setup -----------------------------------------------------------------

branch="$(git branch --show-current)"
if ((resume)); then
  [[ -f "$state" ]] || die "--resume needs $state"
  [[ "$(sget .branch)" == "$branch" ]] || die "state.json is for $(sget .branch); $branch is checked out"
  [[ -n "$worker" ]] || worker="$(sget .worker)"
  ((visible)) || visible="$(sget '.visible // false | if . then 1 else 0 end')"
  ((pr_mode)) || pr_mode="$(sget '.pr_mode // false | if . then 1 else 0 end')"
fi
if [[ -z "$worker" ]]; then
  if [[ -n "${CLAUDECODE:-}" ]]; then worker=claude; else worker=omp; fi
fi
[[ "$worker" == claude || "$worker" == omp ]] || die "--worker must be claude or omp"
command -v "$worker" >/dev/null 2>&1 || die "$worker not on PATH"
if ((visible)); then
  [[ "$worker" == omp ]] || die "--visible needs --worker omp"
  if [[ -z "${HERDR_WORKSPACE_ID:-}" ]] || ! command -v herdr >/dev/null 2>&1; then
    die "--visible needs to run inside a herdr pane"
  fi
fi
setup_cmd="$(jq -r '.setup // ""' "$plan")"
worktrees="$root-overnight"
if ((pr_mode)); then
  git remote get-url origin >/dev/null 2>&1 || die "--pr-per-ticket needs an origin remote"
  gh auth status >/dev/null 2>&1 || die "--pr-per-ticket needs gh to be logged in"
fi
implement_skill="$(skill_path implement)" || die "implement skill not installed"
code_review_skill="$(skill_path code-review)" || die "code-review skill not installed"
claude_lists_max_turns=0
if [[ "$worker" == claude ]] && claude --help 2>/dev/null | grep -q -- '--max-turns'; then
  claude_lists_max_turns=1
fi
model="$(resolve_model)"
deadline="$(deadline_epoch)"
account="$(account_check)"
mkdir -p "$dir/logs"

new_state() {
  jq -n --argjson plan "$(cat "$plan")" --arg branch "$branch" --arg worker "$worker" \
    --arg model "$model" --argjson deadline "$deadline" --arg account "$account" \
    --arg date "$(date +%Y-%m-%d)" --argjson visible "$visible" --argjson pr_mode "$pr_mode" \
    --arg pr_base "$PR_BASE" '
    {date: $date, branch: $branch, worker: $worker, model: $model, account: $account,
     visible: ($visible == 1), pr_mode: ($pr_mode == 1), pr_base: $pr_base, stack_base: null,
     started_at: (now | floor), ended_at: null, deadline: $deadline,
     planned: $plan.queue, queue: $plan.queue, waived: ($plan.waived // []),
     titles: {}, edges: {}, done: [], failed: [], skipped: [], order: [], usage: [],
     tickets_run: 0, requeues: {}, current: null, stop_reason: null}'
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
  echo "  model       ${model:-harness default (gate checks every model-scoped 7d window)}"
  if ((visible)); then echo "  visible     one herdr tab per worker (omp TUI), idle after ${VISIBLE_IDLE_SECS}s"; fi
  if ((pr_mode)); then
    echo "  PRs         worktrees in $worktrees; ticket/<N>-<slug> stacked from origin/$PR_BASE; draft PR per pass"
    echo "  setup       ${setup_cmd:-none}"
  fi
  echo "  skills      $implement_skill · $code_review_skill"
  echo "  build gate  $(jq -r '[.checks | to_entries[] | select(.key != "test") | "\(.key): \(if .value == "" then "n/a" else .value end)"] | join(" · ")' "$plan")"
  echo "  limits      deadline $(date -r "$deadline" '+%a %H:%M' 2>/dev/null || date -d "@$deadline" '+%a %H:%M'), $((TICKET_TIMEOUT_SECS / 60))m per ticket, max tickets $([[ "$max_tickets" == 0 ]] && echo unlimited || echo "$max_tickets")"
  echo "  thresholds  5h sleep ≥${FIVE_HOUR_SLEEP_PCT}% · 7d stop ≥${SEVEN_DAY_STOP_PCT}% · unknown-gate cap ${FALLBACK_MAX_TICKETS} tickets"
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
  exit 0
fi

[[ "$branch" == "$(jq -r '.branch // ""' "$plan")" ]] || die "checked-out branch $branch is not the plan's branch"
ensure_ignored
if ((resume)); then
  if [[ -n "$(git status --porcelain)" ]]; then
    current="$(sget '.current // empty')"
    [[ -n "$current" ]] || die "dirty tree and no interrupted ticket in state.json; clean it by hand"
    git stash push -u -q -m "overnight #$current interrupted"
    log "stashed interrupted #$current work as 'overnight #$current interrupted'"
  fi
  st_apply '.current = null | .stop_reason = null | .ended_at = null | .deadline = $d | .worker = $w
      | .visible = ($v == 1) | .pr_mode = ($p == 1) | .pr_base = (.pr_base // $b)' \
    --argjson d "$deadline" --arg w "$worker" --argjson v "$visible" --argjson p "$pr_mode" --arg b "$PR_BASE"
else
  [[ ! -f "$state" ]] || die "$state exists; pass --resume or move it aside"
  [[ -z "$(git status --porcelain)" ]] || die "working tree is not clean"
  new_state >"$state"
fi
trap on_exit EXIT
trap 'exit 129' HUP
trap 'exit 130' INT
trap 'exit 143' TERM
fetch_tracker
gate
record_usage "start"
log "overnight run on $branch with $worker; gate: $gate_reading"

# --- the loop --------------------------------------------------------------

while :; do
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
    nap "$gate_secs"
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
