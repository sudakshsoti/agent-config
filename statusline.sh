#!/usr/bin/env bash
# Claude Code status line — minimal editorial style
# Reads JSON from stdin, outputs a single status line

input=$(cat)

used=$(echo "$input" | jq -r '.context_window.used_percentage // 0')
model_name=$(echo "$input" | jq -r '.model.display_name // "—"')
cwd=$(echo "$input" | jq -r '.cwd // ""')

# Shorten cwd: replace $HOME with ~
home="$HOME"
short_cwd="${cwd/#$home/\~}"

# Build the progress bar (10 blocks wide) — always rendered, defaults to 0%
filled=$(echo "$used" | awk '{printf "%d", int($1 / 10 + 0.5)}')
bar=""
for i in $(seq 1 10); do
  if [ "$i" -le "$filled" ]; then
    bar="${bar}█"
  else
    bar="${bar}░"
  fi
done
pct=$(printf "%.0f" "$used")

# Color the bar based on fill level
if [ "$pct" -ge 80 ]; then
  # Warm amber — mirrors --accent in the theme
  color="\033[38;5;179m"
elif [ "$pct" -ge 50 ]; then
  color="\033[38;5;145m"
else
  # Muted neutral — matches --fg-secondary
  color="\033[38;5;102m"
fi
reset="\033[0m"
dim="\033[2m"

printf "${dim}${short_cwd}${reset}  ${color}${bar}${reset}  ${dim}${pct}%%  ${model_name}${reset}"
