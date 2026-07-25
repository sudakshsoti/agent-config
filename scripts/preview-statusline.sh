#!/usr/bin/env bash
# preview-statusline.sh — render ccstatusline-settings.json against a fixture
#
# Before this script, the only way to check a layout edit was to deploy it
# live (or trust "looks right"). This pipes the REPO copy of the layout and a
# committed sample payload through the real `ccstatusline` binary, so every
# later layout change (dropping separators, adding widgets, right-aligning
# groups, ...) has a rendered line to diff against instead of a guess.
#
#   ./scripts/preview-statusline.sh                     # width 150, repo layout
#   ./scripts/preview-statusline.sh 100                 # width 100
#   ./scripts/preview-statusline.sh 100 /tmp/other.json # width 100, other config
#
# Width: ccstatusline reads the CCSTATUSLINE_WIDTH env var, NOT `COLUMNS`
# (confirmed against dist/ccstatusline.js's probeTerminalWidth(), which never
# touches process.env.COLUMNS — it checks CCSTATUSLINE_WIDTH, then the
# controlling TTY via ps/stty, then `tput cols`). This repo's CLAUDE.md
# currently documents `COLUMNS=150 ccstatusline ...`, which does not work;
# fixing that doc is a separate task, but this script uses the real knob.
#
# The sample payload's field names come straight off ccstatusline's
# StatusJSONSchema (dist/ccstatusline.js, zod `looseObject` around line
# 80221) — not invented. transcript_path points at a tiny committed JSONL
# fixture whose last line carries a message.usage with input_tokens,
# cache_read_input_tokens and cache_creation_input_tokens, for later items
# (context-threshold widgets) to reuse.
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
width="${1:-150}"
config="${2:-$repo_root/ccstatusline-settings.json}"
transcript="$repo_root/scripts/statusline-sample-transcript.jsonl"
sample="$repo_root/scripts/statusline-sample.json"

if [[ ! -f "$config" ]]; then
  echo "config file not found: $config" >&2
  exit 1
fi
if [[ ! -f "$sample" ]] || [[ ! -f "$transcript" ]]; then
  echo "missing fixture: expected $sample and $transcript" >&2
  exit 1
fi

# Prefer the PATH-installed binary (works through nvm/volta shims); fall back
# to resolving the global package directly, since a fresh shell on this
# machine might not have the shim on PATH yet.
if command -v ccstatusline >/dev/null 2>&1; then
  cmd=(ccstatusline)
else
  npm_root="$(npm root -g 2>/dev/null || true)"
  bin="$npm_root/ccstatusline/dist/ccstatusline.js"
  if [[ -n "$npm_root" ]] && [[ -f "$bin" ]]; then
    cmd=(node "$bin")
  else
    echo "ccstatusline not found on PATH or under \$(npm root -g)/ccstatusline/dist" >&2
    echo "install it with: npm i -g ccstatusline" >&2
    exit 1
  fi
fi

# Bake this machine's absolute paths into the committed template (a checked
# in absolute path would break on every other checkout), and stamp the
# rate-limit reset timestamps relative to "now" so the reset-timer widgets
# show a live countdown instead of a stale committed epoch.
five_hour_reset=$(( $(date +%s) + 3 * 3600 ))
seven_day_reset=$(( $(date +%s) + 5 * 86400 ))

payload=$(jq \
  --arg transcript "$transcript" \
  --arg root "$repo_root" \
  --argjson five_hour_reset "$five_hour_reset" \
  --argjson seven_day_reset "$seven_day_reset" \
  '.transcript_path = $transcript
   | .cwd = $root
   | .workspace.current_dir = $root
   | .workspace.project_dir = $root
   | .rate_limits.five_hour.resets_at = $five_hour_reset
   | .rate_limits.seven_day.resets_at = $seven_day_reset' \
  "$sample")

echo "# ccstatusline --config $config (width=$width)" >&2

# --config renders straight to stdout as long as stdin is NOT a TTY (a TTY
# would launch the interactive TUI instead) — always pipe the payload in.
CCSTATUSLINE_WIDTH="$width" "${cmd[@]}" --config "$config" <<< "$payload"
