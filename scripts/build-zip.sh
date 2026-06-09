#!/usr/bin/env bash
# Package skills into uploadable .zip files for claude.ai / the API.
#
# Skills don't sync between surfaces — Claude Code uses the symlinks from
# install.sh, but claude.ai and the API need a zip upload each. This builds
# those zips. Each archive contains a single top-level <skill>/ folder with
# SKILL.md at its root, which is the structure claude.ai expects.
#
#   ./scripts/build-zip.sh            # zip every skill into dist/
#   ./scripts/build-zip.sh ux-writing # zip just one skill
#
# Output lands in dist/ (git-ignored). Re-run any time after editing a skill.
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
skills_dir="$repo_root/skills"
dist_dir="$repo_root/dist"

mkdir -p "$dist_dir"

zip_one() {
  local name="$1"
  local src="$skills_dir/$name"
  if [[ ! -f "$src/SKILL.md" ]]; then
    echo "skip: $name (no SKILL.md)" >&2
    return
  fi
  local out="$dist_dir/$name.zip"
  rm -f "$out"
  # zip from skills/ so the archive holds a single top-level <name>/ folder.
  ( cd "$skills_dir" && zip -r -q -X "$out" "$name" -x '*.DS_Store' -x '*/.git/*' )
  echo "built: dist/$name.zip"
}

if [[ $# -gt 0 ]]; then
  for name in "$@"; do
    zip_one "$name"
  done
else
  for dir in "$skills_dir"/*/; do
    zip_one "$(basename "$dir")"
  done
fi
