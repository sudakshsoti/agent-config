#!/usr/bin/env bash
# Subagent statusline: one aligned, Kohra-tinted row body per running subagent.
#
# Why this exists: Claude Code's default subagent rows say what an agent is
# called but not what it costs — which model it resolved to, what effort it was
# given, or how close it is to filling its context. On a panel of five parallel
# agents that is exactly the information needed to decide which one to stop, so
# this rewrites each row body to carry it.
#
# Colours are read at runtime from ~/.claude/claude-powerline.json (a symlink
# into this repo) rather than pasted in, so the main bar and this panel stay the
# same palette from one edit. If that read fails the rows still render, plain.
#
# Model names degrade rather than guess: the ID is transformed generically, and
# anything the rule does not recognise is printed as its raw ID. A model shipped
# after this script was written must show up honestly, not under a wrong label.
#
# Fails open, always. Emitting nothing leaves every row at Claude Code's default
# rendering, which is strictly better than a broken panel, so every failure path
# falls through and the script exits 0 no matter what.

set -uo pipefail

CONFIG="$HOME/.claude/claude-powerline.json"

# Hex -> a 24-bit ANSI foreground prefix. Empty on anything unexpected, which
# makes the corresponding cell render uncoloured instead of garbled.
ansi_fg() {
  local hex="${1:-}"
  [[ "$hex" =~ ^#[0-9a-fA-F]{6}$ ]] || { printf ''; return 0; }
  printf '\033[38;2;%d;%d;%dm' "0x${hex:1:2}" "0x${hex:3:2}" "0x${hex:5:2}"
}

c_model='' c_effort='' c_type='' c_ctx='' c_warn='' c_crit=''
if [[ -r "$CONFIG" ]]; then
  # One read, six values, tab-separated: a missing key comes back empty and its
  # cell simply loses colour.
  IFS=$'\t' read -r h_model h_effort h_type h_ctx h_warn h_crit < <(
    jq -r '[.colors.custom.model.fg, .colors.custom.thinking.fg,
            .colors.custom.agent.fg, .colors.custom.context.fg,
            .colors.custom.contextWarning.fg, .colors.custom.contextCritical.fg]
           | map(. // "") | @tsv' "$CONFIG" 2>/dev/null
  ) || true
  c_model=$(ansi_fg "${h_model:-}")
  c_effort=$(ansi_fg "${h_effort:-}")
  c_type=$(ansi_fg "${h_type:-}")
  c_ctx=$(ansi_fg "${h_ctx:-}")
  c_warn=$(ansi_fg "${h_warn:-}")
  c_crit=$(ansi_fg "${h_crit:-}")
fi

jq -c -r \
  --arg cModel "$c_model" \
  --arg cEffort "$c_effort" \
  --arg cType "$c_type" \
  --arg cCtx "$c_ctx" \
  --arg cWarn "$c_warn" \
  --arg cCrit "$c_crit" '
def col($pre): if ($pre == "") then . else $pre + . + "\u001b[0m" end;
def rpad($n): if ($n > length) then . + (" " * ($n - length)) else . end;
def lpad($n): if ($n > length) then (" " * ($n - length)) + . else . end;

# Generic, deliberately conservative. Strip the vendor prefix, a trailing build
# date and a context-size suffix; only "family-N[-N...]" is rewritten. Anything
# else falls through to the raw ID rather than to a guess.
def pretty($id):
  ($id | sub("^claude-"; "") | sub("\\[1m\\]$"; "") | sub("-[0-9]{8}$"; "")) as $s
  | if ($s | test("^[a-z]+(-[0-9]+)+$"))
    then ($s | split("-")) as $p
      | (($p[0][0:1] | ascii_upcase) + $p[0][1:]) + " " + ($p[1:] | join("."))
    else $id
    end;

(if (.columns | type) == "number" and .columns > 0 then (.columns | floor) else 80 end) as $cols
| [ .tasks[]?
    # model absent means the task has not resolved one yet; those rows keep
    # their default rendering, so they are dropped before anything is measured.
    | select(.model != null and (.model | type) == "string")
    | {
        id: .id,
        model: pretty(.model),
        effort: (if .effort == null then "" else "·" + (.effort | tostring) end),
        type: (.type // ""),
        desc: (if ((.description // "") | length) > 0 then .description else (.name // "") end),
        pct: (
          if ((.contextWindowSize | type) == "number") and (.contextWindowSize > 0)
          then ((((.tokenCount // 0) * 100) / .contextWindowSize) | floor)
          else null end
        )
      }
  ] as $rows
| ($rows | map(.model | length) | max // 0) as $wModel
| ($rows | map(.effort | length) | max // 0) as $wEffort
| ($rows | map(.type | length) | max // 0) as $wType
| $rows[]
| (if .pct == null then "" else (.pct | tostring) + "%" end) as $pctText
# Bound here rather than at the call site: a jq function argument is a closure
# evaluated against the input at the point of call, which by then is a string.
| (if .pct == null then ""
   elif .pct >= 90 then $cCrit
   elif .pct >= 70 then $cWarn
   else $cCtx end) as $cPct
| ((.model | rpad($wModel))
   + (if $wEffort > 0 then " " + (.effort | rpad($wEffort)) else "" end)) as $head
| ($head + "  " + (.type | rpad($wType)) + "  ") as $prefix
| ($prefix | length) as $wPrefix
| ($pctText | lpad(4)) as $pctCell
| ($cols - $wPrefix - 2 - 4) as $avail
| (if $avail <= 0 then ""
   elif (.desc | length) <= $avail then .desc
   else (.desc[0:($avail - 1)] + "…") end) as $desc
| (($desc | rpad(if $avail > 0 then $avail else 0 end))) as $descCell
| ($prefix + $descCell + "  " + $pctCell) as $plain
| (if ($plain | length) > $cols
   # Last resort for a panel too narrow to hold even the fixed columns: hard
   # truncate, uncoloured. Never emit a row wider than the width given.
   then { id: .id, content: (if $cols > 0 then ($plain[0:($cols - 1)] + "…") else "" end) }
   else { id: .id,
          content: (
            (.model | rpad($wModel) | col($cModel))
            + (if $wEffort > 0 then " " + (.effort | rpad($wEffort) | col($cEffort)) else "" end)
            + "  " + (.type | rpad($wType) | col($cType))
            + "  " + $descCell
            + "  " + ($pctCell | col($cPct))
          ) }
   end)
' 2>/dev/null

exit 0
