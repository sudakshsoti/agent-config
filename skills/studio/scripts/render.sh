#!/usr/bin/env bash
# render.sh — the studio skill's render gate.
#
# Usage: bash render.sh <file.html> [outdir]
#
# Renders a self-contained HTML artifact at three shots: 390 and 1440
# viewport-only, plus one full-page shot at 1440 so what's below the fold is
# actually visible. A viewport-only pair never shows that; a full-page shot
# at 390 is deliberately skipped — on a long artifact it is thousands of
# pixels tall and unreadable once downscaled. Exits 0 only if all three
# files exist and are non-empty.
set -euo pipefail

if ! command -v playwright >/dev/null 2>&1; then
  echo "playwright not on PATH — brew install playwright, or npx playwright" >&2
  exit 1
fi

if [ $# -lt 1 ]; then
  echo "usage: render.sh <file.html> [outdir]" >&2
  exit 1
fi

file="$1"
base="$(basename "${file%.*}")"
outdir="${2:-/tmp/studio-render/$base}"
mkdir -p "$outdir"

shot_390="$outdir/$base-390.png"
shot_1440="$outdir/$base-1440.png"
shot_1440_full="$outdir/$base-1440-full.png"

playwright screenshot --viewport-size=390,844 "$file" "$shot_390"
echo "$shot_390"
playwright screenshot --viewport-size=1440,900 "$file" "$shot_1440"
echo "$shot_1440"
playwright screenshot --viewport-size=1440,900 --full-page "$file" "$shot_1440_full"
echo "$shot_1440_full"

for shot in "$shot_390" "$shot_1440" "$shot_1440_full"; do
  if [ ! -s "$shot" ]; then
    echo "render failed — $shot missing or empty" >&2
    exit 1
  fi
done
