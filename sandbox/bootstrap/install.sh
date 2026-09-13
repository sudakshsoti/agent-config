#!/usr/bin/env bash
# Install the committed, sanitized agent configuration carried by this bundle.
# This deliberately installs configuration only. Binary installation is a
# separate prerequisite until pinned Linux install procedures are verified.
set -euo pipefail

BUNDLE_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
SNAPSHOT="$BUNDLE_DIR/snapshot"
MANIFEST="$BUNDLE_DIR/manifest.txt"
VERSION_FILE="$BUNDLE_DIR/VERSION"
CHECKSUMS="$BUNDLE_DIR/SHA256SUMS"
CONFIG_ONLY=0

usage() {
  printf 'usage: %s [--config-only]\n' "$(basename "$0")"
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --config-only) CONFIG_ONLY=1 ;;
    --help|-h) usage; exit 0 ;;
    *) usage >&2; exit 2 ;;
  esac
  shift
done

fail() { printf 'sandbox bootstrap: %s\n' "$1" >&2; exit 1; }

[ "$(id -u)" -ne 0 ] || fail 'refusing to run as root'
[ -f "$MANIFEST" ] || fail "missing manifest: $MANIFEST"
[ -f "$VERSION_FILE" ] || fail "missing metadata: $VERSION_FILE"
[ -f "$CHECKSUMS" ] || fail "missing checksums: $CHECKSUMS"
[ -d "$SNAPSHOT" ] || fail "missing snapshot: $SNAPSHOT"

case "${HOME:-}" in
  /*) ;;
  *) fail 'HOME must be an absolute path' ;;
esac
[ "$HOME" != / ] || fail 'HOME must not be filesystem root'
[ -d "$HOME" ] || fail 'HOME must be an existing directory'
[ ! -L "$HOME" ] || fail 'HOME must not be a symlink'
HOME_REAL="$(cd -- "$HOME" && pwd -P)"
[ "$HOME_REAL" != / ] || fail 'HOME must not resolve to filesystem root'

checksum() {
  if command -v sha256sum >/dev/null 2>&1; then
    sha256sum -- "$1" | awk '{print $1}'
  elif command -v shasum >/dev/null 2>&1; then
    shasum -a 256 -- "$1" | awk '{print $1}'
  else
    fail 'sha256sum or shasum is required'
  fi
}

# The checksum list is the trust boundary for a bundle copied into a sandbox.
# SHA256SUMS cannot checksum itself, but every executable, metadata and payload
# file is covered.
while IFS= read -r line || [ -n "$line" ]; do
  [ -n "$line" ] || continue
  expected="${line%%  *}"
  relative="${line#*  }"
  [ "$expected" != "$line" ] || fail "malformed checksum entry"
  [[ "$expected" =~ ^[0-9a-fA-F]{64}$ ]] || fail "malformed checksum for $relative"
  case "$relative" in
    /*|../*|*/../*|*/..|''|SHA256SUMS) fail "unsafe checksum path: $relative" ;;
  esac
  case "$relative" in
    ./*) fail "unsafe checksum path: $relative" ;;
  esac
  file="$BUNDLE_DIR/$relative"
  [ -f "$file" ] || fail "checksum target is missing: $relative"
  actual="$(checksum "$file")"
  [ "$actual" = "$expected" ] || fail "checksum mismatch: $relative"
done < "$CHECKSUMS"

manifest_has() {
  local wanted="$1" line
  while IFS= read -r line || [ -n "$line" ]; do
    [ -z "$line" ] && continue
    [[ "$line" == \#* ]] && continue
    [ "$line" = "$wanted" ] && return 0
  done < "$MANIFEST"
  return 1
}

# Only relative, lexical paths are accepted from the manifest. Also reject a
# symlink anywhere in the path: copying one could read outside this bundle.
manifest_entries=()
while IFS= read -r line || [ -n "$line" ]; do
  [ -z "$line" ] && continue
  [[ "$line" == \#* ]] && continue
  case "$line" in
    /*|*\\*|../*|*/../*|*/..|.|./*|*[!A-Za-z0-9_./-]*)
      fail "unsafe manifest path: $line" ;;
  esac
  manifest_entries+=("$line")
  relative="${line%/}"
  [ -n "$relative" ] || fail "empty manifest path"
  cursor="$SNAPSHOT"
  IFS='/' read -r -a components <<< "$relative"
  for component in "${components[@]}"; do
    cursor="$cursor/$component"
    [ ! -L "$cursor" ] || fail "symlink escapes bundle: $line"
  done
  [ -e "$SNAPSHOT/$relative" ] || fail "manifest path is missing: $line"
done < "$MANIFEST"
[ "${#manifest_entries[@]}" -gt 0 ] || fail 'manifest is empty'
for required in global-agents.md skills/ pi/settings.json pi/subagents.json pi/prompts/ pi/themes/ pi/extensions/ pi/agents/ omp/config.yml omp/lsp.yml omp/themes/ omp/overlays/; do
  manifest_has "$required" || fail "manifest is missing required entry: $required"
done

# Validate the complete extracted tree, including files not directly named in a
# directory entry. A malicious symlink must never be followed by cp/find.
while IFS= read -r -d '' link; do
  fail "symlink in snapshot: ${link#"$SNAPSHOT"/}"
done < <(find "$SNAPSHOT" -type l -print0)

if [ "$CONFIG_ONLY" -eq 0 ]; then
  pi_version='0.85.1'
  omp_version='18.1.19'
  grep -Eq "(^|[^0-9])${pi_version//./\\.}([^0-9]|$)" <(pi --version 2>&1) \
    || fail "pi $pi_version is required; install the pinned binary before bootstrapping (or use --config-only)"
  grep -Eq "(^|[^0-9])${omp_version//./\\.}([^0-9]|$)" <(omp --version 2>&1) \
    || fail "omp $omp_version is required; install the pinned binary before bootstrapping (or use --config-only)"
fi

# Resolve symlinks in the existing ancestors of an absolute path without
# requiring the path itself to exist. macOS exposes /var and /tmp through
# /private symlinks, so a lexical comparison against a caller-supplied HOME
# would wrongly reject a legitimate mktemp path. Existing ancestors are
# canonicalized first; the resolved path is what containment is judged on.
canonical_dir() {
  local path="$1" suffix="" parent base
  case "$path" in
    /*) ;;
    *) fail "path must be absolute: $path" ;;
  esac
  while [ ! -e "$path" ] && [ ! -L "$path" ]; do
    base="$(basename -- "$path")"
    [ -n "$base" ] || fail "cannot resolve path: $1"
    suffix="/$base$suffix"
    parent="$(dirname -- "$path")"
    [ "$parent" != "$path" ] || fail "cannot resolve path: $1"
    path="$parent"
  done
  [ -d "$path" ] || fail "path is not a directory: $path"
  path="$(cd -- "$path" && pwd -P)"
  printf '%s%s\n' "$path" "$suffix"
}

within_home() {
  case "$1" in
    "$HOME_REAL"|"$HOME_REAL"/*) return 0 ;;
  esac
  return 1
}

ensure_dir() {
  local dir="$1" canonical
  [ -n "$dir" ] || fail 'destination path must not be empty'
  [ "$dir" != / ] || fail "refusing filesystem root: $dir"
  within_home "$dir" || fail "destination escapes HOME: $dir"
  if [ -L "$dir" ] && [ ! -e "$dir" ]; then
    fail "destination is a dangling symlink: $dir"
  fi
  if [ -e "$dir" ] && [ ! -d "$dir" ]; then fail "destination is not a directory: $dir"; fi
  # A symlink inside HOME is allowed only when it still resolves inside HOME;
  # anything that redirects the write elsewhere is refused.
  canonical="$(canonical_dir "$dir")"
  within_home "$canonical" || fail "destination escapes HOME: $dir"
  mkdir -p -- "$dir"
}

managed_marker() { printf '%s.agent-config-sandbox-managed' "$1"; }

install_file() {
  local source="$1" destination="$2" parent name stage marker
  [ -f "$source" ] || fail "source file is missing: $source"
  parent="$(dirname -- "$destination")"
  ensure_dir "$parent"
  marker="$(managed_marker "$destination")"
  if [ -e "$destination" ] || [ -L "$destination" ]; then
    [ ! -L "$destination" ] || fail "managed destination is a symlink: $destination"
    [ -f "$marker" ] || fail "refusing to replace unmanaged file: $destination"
  fi
  stage="$(mktemp -d "$parent/.sandbox-bootstrap.XXXXXX")"
  name="$(basename -- "$destination")"
  cp -- "$source" "$stage/$name"
  chmod -- "$(stat -c '%a' "$source" 2>/dev/null || stat -f '%Lp' "$source")" "$stage/$name" 2>/dev/null || true
  mv -f -- "$stage/$name" "$destination"
  printf 'agent-config sandbox bootstrap\n' > "$stage/marker"
  mv -f -- "$stage/marker" "$marker"
  rmdir -- "$stage"
}

copy_tree() {
  local source_root="$1" destination_root="$2" source file relative destination
  [ -d "$source_root" ] || fail "source directory is missing: $source_root"
  ensure_dir "$destination_root"
  while IFS= read -r -d '' source; do
    relative="${source#"$source_root"/}"
    destination="$destination_root/$relative"
    install_file "$source" "$destination"
  done < <(find "$source_root" -type f -print0)
}

install_skill() {
  local source="$1" destination="$2" parent stage marker name
  [ -d "$source" ] || fail "skill directory is missing: $source"
  [ -f "$source/SKILL.md" ] || fail "skill has no SKILL.md: $source"
  while IFS= read -r -d '' link; do fail "skill contains symlink: $link"; done < <(find "$source" -type l -print0)
  parent="$(dirname -- "$destination")"
  ensure_dir "$parent"
  if [ -L "$destination" ]; then fail "skill destination is a symlink: $destination"; fi
  if [ -e "$destination" ]; then
    marker="$destination/.agent-config-sandbox-managed"
    [ -f "$marker" ] || fail "refusing to replace unmanaged skill: $destination"
    rm -rf -- "$destination"
  fi
  stage="$(mktemp -d "$parent/.sandbox-skill.XXXXXX")"
  name="$(basename -- "$destination")"
  cp -R -- "$source" "$stage/$name"
  printf 'agent-config sandbox bootstrap\n' > "$stage/$name/.agent-config-sandbox-managed"
  mv -- "$stage/$name" "$destination"
  rmdir -- "$stage"
}

# Install under the canonical HOME so destination paths never traverse the
# symlinked ancestors (for example /var on macOS) that HOME itself may have.
PI_HOME="$HOME_REAL/.pi/agent"
OMP_HOME="$HOME_REAL/.omp/agent"
AGENTS_HOME="$HOME_REAL/.agents/skills"
OMP_CONFIG="$HOME_REAL/.config/omp"

install_file "$SNAPSHOT/global-agents.md" "$PI_HOME/AGENTS.md"
install_file "$SNAPSHOT/global-agents.md" "$OMP_HOME/AGENTS.md"

ensure_dir "$AGENTS_HOME"
while IFS= read -r -d '' skill; do
  install_skill "$skill" "$AGENTS_HOME/$(basename -- "$skill")"
done < <(find "$SNAPSHOT/skills" -mindepth 1 -maxdepth 1 -type d -print0)

install_file "$SNAPSHOT/pi/settings.json" "$PI_HOME/settings.json"
install_file "$SNAPSHOT/pi/subagents.json" "$PI_HOME/subagents.json"
copy_tree "$SNAPSHOT/pi/prompts" "$PI_HOME/prompts"
copy_tree "$SNAPSHOT/pi/themes" "$PI_HOME/themes"
copy_tree "$SNAPSHOT/pi/extensions" "$PI_HOME/extensions"
copy_tree "$SNAPSHOT/pi/agents" "$PI_HOME/agents"

install_file "$SNAPSHOT/omp/config.yml" "$OMP_HOME/config.yml"
install_file "$SNAPSHOT/omp/lsp.yml" "$OMP_HOME/lsp.yml"
copy_tree "$SNAPSHOT/omp/themes" "$OMP_HOME/themes"
copy_tree "$SNAPSHOT/omp/overlays" "$OMP_CONFIG"

if [ "$CONFIG_ONLY" -eq 1 ]; then
  printf 'sandbox bootstrap: installed configuration only (--config-only); pinned pi 0.85.1 and omp 18.1.19 binaries remain a prerequisite.\n'
else
  printf 'sandbox bootstrap: installed configuration and verified pi 0.85.1 / omp 18.1.19.\n'
fi
