#!/bin/sh
# PreCompact hook: snapshot the session to a handoff note before Claude Code
# compacts the conversation into a summary.
#
# Why: auto-compact is lossy. It replaces the transcript with a summary, so exact
# file paths, commands run and the user's own wording are flattened. This runs
# while the full transcript still exists on disk and writes the durable parts out.
#
# Deliberately deterministic: it parses the transcript JSONL with jq and reads git
# state. It never calls a model, never hits the network, and always exits 0 so a
# failure here can never block or delay compaction.
#
# Destination: <git repo root>/handoff/, per the global rule that handoff notes are
# tracked project history. Falls back to ~/.claude/handoff/ outside a repo.

set -u

# Whatever happens below, emit valid hook output and let compaction proceed.
trap 'printf "{}\n"; exit 0' EXIT INT TERM

payload=$(cat 2>/dev/null) || payload=''

command -v jq >/dev/null 2>&1 || exit 0

# Handoff notes land in a tracked git directory, so anything echoed from the
# transcript has to be scrubbed first. Masks known token shapes and any
# key/token/secret/password assignment. Better a mangled command than a leaked key.
redact() {
  sed -E \
    -e 's/([Bb]earer)[[:space:]]+[A-Za-z0-9._~+/-]{12,}=*/\1 ***REDACTED***/g' \
    -e 's/(sk-ant-|sk-|ghp_|gho_|ghu_|ghs_|ghr_|github_pat_|xoxb-|xoxp-|xoxa-|xapp-|glpat-|AIza|AKIA|ASIA|hf_|npm_|dop_v1_)[A-Za-z0-9_-]{8,}/\1***REDACTED***/g' \
    -e 's/([Aa][Uu][Tt][Hh][^[:space:]]*|[Aa][Pp][Ii][_-]?[Kk][Ee][Yy]|[Aa][Cc][Cc][Ee][Ss][Ss][_-]?[Kk][Ee][Yy]|[Tt][Oo][Kk][Ee][Nn]|[Ss][Ee][Cc][Rr][Ee][Tt]|[Pp][Aa][Ss][Ss][Ww][Oo][Rr][Dd]|[Pp][Aa][Ss][Ss][Ww][Dd])([[:space:]]*[=:][[:space:]]*)("|'"'"')?[^[:space:]"'"'"']{6,}/\1\2***REDACTED***/g' \
    -e 's/eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]+/***REDACTED-JWT***/g' \
    -e 's#(postgres|postgresql|mysql|mongodb\+srv|mongodb|redis|amqp|ftp)://[^:/[:space:]]+:[^@[:space:]]+@#\1://***REDACTED***@#g' \
    -e 's/-----BEGIN [A-Z ]*PRIVATE KEY-----.*/***REDACTED-PRIVATE-KEY***/g'
}

field() {
  printf '%s' "$payload" | jq -r "$1 // empty" 2>/dev/null
}

transcript=$(field '.transcript_path')
session=$(field '.session_id')
trigger=$(field '.trigger')
cwd=$(field '.cwd')

[ -n "$cwd" ] || cwd=$PWD
[ -n "$trigger" ] || trigger=unknown
[ -n "$session" ] || session=unknown
[ -n "$transcript" ] && [ -r "$transcript" ] || exit 0

root=$(git -C "$cwd" rev-parse --show-toplevel 2>/dev/null) || root=''
if [ -n "$root" ]; then
  dest="$root/handoff"
else
  dest="$HOME/.claude/handoff"
fi
mkdir -p "$dest" 2>/dev/null || exit 0

short=$(printf '%s' "$session" | cut -c1-8)
file="$dest/$(date +%Y-%m-%d)-session-$short.md"

# A file per session, an entry per compaction, so repeated compactions accumulate
# rather than overwrite each other.
if [ ! -f "$file" ]; then
  {
    printf '# Session handoff %s\n\n' "$short"
    printf 'Written by the PreCompact hook. One entry per compaction, oldest first.\n'
  } > "$file"
fi

{
  printf '\n---\n\n'
  printf '## Compaction at %s (%s)\n\n' "$(date '+%Y-%m-%d %H:%M:%S %Z')" "$trigger"
  printf -- '- Session: `%s`\n' "$session"
  printf -- '- Transcript: `%s`\n' "$transcript"
  printf -- '- Directory: `%s`\n' "$cwd"

  if [ -n "$root" ]; then
    branch=$(git -C "$root" rev-parse --abbrev-ref HEAD 2>/dev/null) || branch='?'
    head=$(git -C "$root" log -1 --format='%h %s' 2>/dev/null) || head='?'
    printf -- '- Branch: `%s`\n' "$branch"
    printf -- '- HEAD: %s\n' "$head"
    dirty=$(git -C "$root" status --porcelain 2>/dev/null | head -25)
    if [ -n "$dirty" ]; then
      printf '\n### Uncommitted at compaction\n\n```\n%s\n```\n' "$dirty"
    else
      printf -- '- Working tree: clean\n'
    fi
  fi

  prompts=$(jq -r '
    select(.type == "user" and (.message.content | type) == "string")
    | .message.content
    | select(startswith("<local-command") | not)
    | select(startswith("<command-") | not)
    | select(startswith("Caveat:") | not)
    | gsub("\\s+"; " ")
    | .[0:400]
  ' "$transcript" 2>/dev/null | redact | grep -v '^ *$' | tail -8)
  if [ -n "$prompts" ]; then
    printf '\n### What was asked (last 8 prompts, oldest first)\n\n'
    printf '%s\n' "$prompts" | sed 's/^/- /'
  fi

  files=$(jq -r '
    select(.type == "assistant")
    | .message.content[]?
    | select(.type == "tool_use")
    | (.input.file_path? // .input.notebook_path? // empty)
  ' "$transcript" 2>/dev/null | redact | grep -v '^ *$' | sort -u | head -40)
  if [ -n "$files" ]; then
    printf '\n### Files touched\n\n'
    printf '%s\n' "$files" | sed 's/^/- `/; s/$/`/'
  fi

  cmds=$(jq -r '
    select(.type == "assistant")
    | .message.content[]?
    | select(.type == "tool_use" and .name == "Bash")
    | .input.command
    | gsub("\\s+"; " ")
    | .[0:200]
  ' "$transcript" 2>/dev/null | redact | grep -v '^ *$' | tail -12)
  if [ -n "$cmds" ]; then
    printf '\n### Recent shell commands\n\n```\n%s\n```\n' "$cmds"
  fi

  printf '\n### Still open\n\n_TODO: fill in before relying on this note._\n'
} >> "$file" 2>/dev/null

exit 0
