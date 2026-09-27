#!/usr/bin/env bash
# usage-gate.sh — may the overnight loop start another ticket?
#
# Source: `omp usage invalidate --provider anthropic` then
# `omp usage --provider anthropic --json`. The Claude Code statusline is not a
# source: headless runs never see it (docs/research/
# claude-code-overnight-primitives-2026-09.md §4, §9).
#
#   usage-gate.sh [--model <worker model id>]
#
# Gated windows: anthropic:5h, anthropic:7d, and every model-scoped 7d window
# (id anthropic:7d:<tier>) whose tier occurs in --model. With no --model, every
# model-scoped 7d window is gated, because the worker's family is unknown.
#
# Exit codes (stdout carries a value only on 10; stderr carries the reading):
#   0   go
#   10  sleep — stdout: seconds until the 5h resetsAt + RESET_GRACE_SECS
#   20  stop — a weekly window is over pace (used − elapsed > PACE_MARGIN_PCT
#       once PACE_MIN_ELAPSED_PCT% of the window has elapsed) or at/over
#       SEVEN_DAY_STOP_PCT
#   30  unknown — omp missing, a command failed, no anthropic report, or a
#       required window absent; the loop may continue only while
#       tickets-this-run < FALLBACK_MAX_TICKETS
#
# `omp usage invalidate` empties the cache and the refetch lands asynchronously:
# for ~15-20 s afterwards `--json` lists the account under accountsWithoutUsage
# with no report (observed on omp 18.3.5). The gate polls for up to
# USAGE_FETCH_WAIT_SECS before calling the report absent.
#
# Test hooks: USAGE_GATE_JSON=<file> replaces both omp calls;
# USAGE_GATE_NOW_MS pins the clock.
#
# Sourcing this file defines the thresholds without running the gate.
set -euo pipefail

FIVE_HOUR_SLEEP_PCT="${FIVE_HOUR_SLEEP_PCT:-70}"
SEVEN_DAY_STOP_PCT="${SEVEN_DAY_STOP_PCT:-90}"
PACE_MARGIN_PCT="${PACE_MARGIN_PCT:-15}"
PACE_MIN_ELAPSED_PCT="${PACE_MIN_ELAPSED_PCT:-5}"
FALLBACK_MAX_TICKETS="${FALLBACK_MAX_TICKETS:-4}"
RESET_GRACE_SECS=120
USAGE_FETCH_WAIT_SECS="${USAGE_FETCH_WAIT_SECS:-90}"

gate_unknown() {
  echo "unknown: $1" >&2
  exit 30
}

gate_main() {
  local model=""
  while (($#)); do
    case "$1" in
    --model)
      model="${2:-}"
      shift 2
      ;;
    *)
      echo "usage: usage-gate.sh [--model <id>]" >&2
      exit 2
      ;;
    esac
  done

  local json
  if [[ -n "${USAGE_GATE_JSON:-}" ]]; then
    json="$(cat "$USAGE_GATE_JSON")" || gate_unknown "cannot read $USAGE_GATE_JSON"
  else
    command -v omp >/dev/null 2>&1 || gate_unknown "omp not on PATH"
    omp usage invalidate --provider anthropic >/dev/null 2>&1 ||
      gate_unknown "omp usage invalidate failed"
    local waited=0
    while :; do
      json="$(omp usage --provider anthropic --json 2>/dev/null)" ||
        gate_unknown "omp usage --json failed"
      jq -e 'any(.reports[]?; .provider == "anthropic")' >/dev/null 2>&1 <<<"$json" && break
      ((waited < USAGE_FETCH_WAIT_SECS)) || break
      sleep 3
      waited=$((waited + 3))
    done
  fi

  local now_ms="${USAGE_GATE_NOW_MS:-$(($(date +%s) * 1000))}"
  local verdict
  verdict="$(printf '%s' "$json" | jq -c \
    --arg model "$model" \
    --argjson sleep "$FIVE_HOUR_SLEEP_PCT" \
    --argjson stop "$SEVEN_DAY_STOP_PCT" \
    --argjson margin "$PACE_MARGIN_PCT" \
    --argjson min_elapsed "$PACE_MIN_ELAPSED_PCT" \
    --argjson now "$now_ms" \
    --argjson grace "$RESET_GRACE_SECS" '
    # Several anthropic accounts: judge each window by its busiest account.
    [.reports[]? | select(.provider == "anthropic") | .limits[]?] as $limits
    | def lim($id): [$limits[] | select(.id == $id and (.amount.used | type) == "number")]
        | if length == 0 then null else max_by(.amount.used) end;
      def pct: .amount.used * 10 | round / 10 | tostring + "%";
      def at: if (.window.resetsAt | type) == "number"
        then " (resets " + (.window.resetsAt / 1000 | floor | strflocaltime("%a %H:%M")) + ")"
        else "" end;
      def tier: .scope.tier // (.id | split(":") | .[2]);
      # Weekly window length: durationMs is authoritative; a 7d window
      # without one is a full week in ms.
      def week_len: (.window.durationMs
        // (if .window.id == "7d" then 604800000 else null end));
      # Percent of the window elapsed at $now, clamped to [0, 100];
      # null when resetsAt (or a usable length) is missing.
      def elapsed($now): (.window.resetsAt | type) as $rt | week_len as $l
        | if $rt != "number" or ($l | type) != "number" or $l <= 0 then null
          else (((($now - (.window.resetsAt - $l)) / $l | [., 0] | max) | [., 1] | min) * 100)
          end;
      def fmt1: .*10 | round / 10 | tostring;
      def pace_over($now; $margin; $min): elapsed($now) as $e
        | if ($e | type) != "number" or $e < $min then false
          else (.amount.used - $e > $margin) end;
      def weekly_reading($now): elapsed($now) as $e
        | .id + " " + pct
          + (if ($e | type) == "number" then " (elapsed " + ($e | fmt1) + "%)" else "" end)
          + at;
      def pace_reason($margin): .elapsed as $e | (.used - $e) as $d
        | "\(.id) \(.used)% vs \($e | fmt1)% elapsed (\(if $d >= 0 then "+" else "" end)\($d | fmt1) > \($margin))";
      ([.reports[]? | select(.provider == "anthropic")] | length) as $reports
    | lim("anthropic:5h") as $five
    | lim("anthropic:7d") as $seven
    | ([$limits[]
        | select((.id | split(":") | length) > 2 and .window.id == "7d"
                 and (.amount.used | type) == "number")
        | (tier | ascii_downcase) as $tier
        | select($model == "" or ($model | ascii_downcase | contains($tier)))]
       | group_by(.id) | map(max_by(.amount.used))) as $scoped
    | if $reports == 0 then {code: 30, why: "no anthropic report"}
      elif $five == null then {code: 30, why: "anthropic:5h window absent"}
      elif $seven == null then {code: 30, why: "anthropic:7d window absent"}
      else
        ([$five | .id + " " + pct + at]
          + ([$seven] + $scoped | map(weekly_reading($now))) | join(" · ")) as $reading
        | ([$seven] + $scoped | map(. as $w | ($w | elapsed($now)) as $e
            | {id: $w.id, used: $w.amount.used, elapsed: $e,
               hard: ($w.amount.used >= $stop),
               pace: ($w | pace_over($now; $margin; $min_elapsed))})) as $weekly
        | ([ $weekly[] | select(.hard) | .id ]) as $hard_ids
        | ([ $weekly[] | select(.pace and (.hard | not)) | pace_reason($margin) ]) as $pace_hits
        | if ($hard_ids | length) > 0 and ($pace_hits | length) > 0 then
            {code: 20,
             why: ("weekly over " + ($stop | tostring) + "%: " + ($hard_ids | join(", "))
                   + "; over pace: " + ($pace_hits | join("; "))), reading: $reading}
          elif ($hard_ids | length) > 0 then
            {code: 20, why: ("weekly over " + ($stop | tostring) + "%: " + ($hard_ids | join(", "))), reading: $reading}
          elif ($pace_hits | length) > 0 then
            {code: 20, why: ("over pace: " + ($pace_hits | join("; "))), reading: $reading}
          elif $five.amount.used >= $sleep then
            if ($five.window.resetsAt | type) != "number" then
              {code: 30, why: "anthropic:5h has no resetsAt", reading: $reading}
            else
              {code: 10, reading: $reading,
               seconds: (([(($five.window.resetsAt - $now) / 1000 | ceil), 0] | max) + $grace)}
            end
          else {code: 0, reading: $reading}
          end
      end')" || gate_unknown "usage JSON did not parse"

  local code reading why
  code="$(jq -r '.code' <<<"$verdict")"
  reading="$(jq -r '.reading // ""' <<<"$verdict")"
  why="$(jq -r '.why // ""' <<<"$verdict")"
  case "$code" in
  0) echo "go: $reading" >&2 ;;
  10)
    echo "sleep: $reading" >&2
    jq -r '.seconds' <<<"$verdict"
    ;;
  20) echo "stop: $why · $reading" >&2 ;;
  *) gate_unknown "$why${reading:+ · $reading}" ;;
  esac
  exit "$code"
}

if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
  gate_main "$@"
fi
