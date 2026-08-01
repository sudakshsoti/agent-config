#!/usr/bin/env bash
# Statusline wrapper: claude-powerline, with the context token count in "k".
#
# Why this exists: claude-powerline renders the context token count with a bare
# `toLocaleString()` (src/segments/renderer.ts:541), which takes the *system*
# locale. On an en-IN machine 170000 comes out as "1,70,000" — lakh grouping,
# correct for rupees, unreadable as a token budget. There is no config key for
# the format and no locale that yields "170k", so the only lever left is the
# rendered output. Rewrites "◔ 1,70,000 (17%)" to "◔ 170k (17%)".
#
# Fails open, always. A statusline that errors is worse than one that is merely
# formatted oddly, so every failure path falls back to the raw bar, and the
# script exits 0 no matter what.

set -uo pipefail

input=$(cat)
raw=$(printf '%s' "$input" | claude-powerline --style=minimal 2>/dev/null) || {
  printf '%s' "$raw"
  exit 0
}

printf '%s' "$raw" | python3 -c '
import re, sys

def k(m):
    n = int(m.group(1).replace(",", ""))
    # Below 1000 a "k" figure would lose more than it saves.
    return (str(n) if n < 1000 else f"{round(n / 1000)}k") + m.group(2)

src = sys.stdin.read()
# Anchor on the trailing " (NN%)" so this only ever touches the context count
# and never a cost, a message tally or a duration.
sys.stdout.write(re.sub(r"(\d[\d,]*)( \(\d+%\))", k, src))
' 2>/dev/null || printf '%s' "$raw"

exit 0
