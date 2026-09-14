#!/usr/bin/env bash
# Build the reviewed agent-config snapshot from committed Git HEAD only.
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
REPO_ROOT="$(cd -- "$SCRIPT_DIR/.." && pwd -P)"
SOURCE_ROOT="$REPO_ROOT/sandbox/bootstrap"
MANIFEST_PATH="sandbox/bootstrap/manifest.txt"
INSTALLER_PATH="sandbox/bootstrap/install.sh"
DEFAULT_OUTPUT="${HOME:-}/.local/share/agent-sandbox/bootstrap"
OUTPUT="${DEFAULT_OUTPUT}"
# Narrow marker written into every bundle. Replacement of an existing output is
# allowed only when this exact file/value is present, so an unrelated directory
# or file is never overwritten.
BUNDLE_MARKER_NAME=".agent-config-sandbox-bundle"
BUNDLE_MARKER_VALUE="agent-config-sandbox-bundle:1"

usage() {
  printf 'usage: %s [--output PATH]\n' "$(basename "$0")"
}

while [ "$#" -gt 0 ]; do
  case "$1" in
  --output)
    [ "$#" -ge 2 ] || {
      usage >&2
      exit 2
    }
    OUTPUT="$2"
    shift 2
    ;;
  --output=*)
    OUTPUT="${1#--output=}"
    shift
    ;;
  --help | -h)
    usage
    exit 0
    ;;
  *)
    usage >&2
    exit 2
    ;;
  esac
done

fail() {
  printf 'sandbox bundle: %s\n' "$1" >&2
  exit 1
}

git -C "$REPO_ROOT" rev-parse --git-dir >/dev/null 2>&1 || fail "not a Git worktree: $REPO_ROOT"
[ -n "${HOME:-}" ] || fail 'HOME is required to choose the default output'
[ -n "$OUTPUT" ] || fail 'output path must not be empty'

# realpath(3) semantics without requiring the destination to exist. Python is
# already a repository test prerequisite and is available on macOS/Linux.
canonical_path() {
  python3 - "$1" <<'PY'
import os
import sys
print(os.path.realpath(os.path.expanduser(sys.argv[1])))
PY
}

OUTPUT="$(canonical_path "$OUTPUT")"
REPO_REAL="$(canonical_path "$REPO_ROOT")"
SOURCE_REAL="$(canonical_path "$SOURCE_ROOT")"
case "$OUTPUT" in
"$REPO_REAL" | "$REPO_REAL"/*) fail 'output must be outside the repository' ;;
"$SOURCE_REAL" | "$SOURCE_REAL"/*) fail 'output must be outside the bootstrap source tree' ;;
/) fail 'output must not be filesystem root' ;;
esac

# The installed bundle is the immutable trust anchor for a sandbox. The broad
# ~/dev workspace stays writable for ordinary development, so no output may sit
# anywhere under it, not only inside this repository's own checkout.
HOME_REAL="$(canonical_path "${HOME}")"
case "$OUTPUT" in
"$HOME_REAL/dev" | "$HOME_REAL/dev"/*) fail "output must be outside \$HOME/dev" ;;
esac

# In a linked worktree REPO_REAL is the worktree, not the checkout the branch is
# shared with (~/dev/agent-config for this repository). Refuse an output that
# would land inside that shared checkout, whose .git directory hosts this tree.
common_dir="$(git -C "$REPO_ROOT" rev-parse --git-common-dir 2>/dev/null || true)"
if [ -n "$common_dir" ]; then
  case "$common_dir" in
  /*) ;;
  *) common_dir="$REPO_ROOT/$common_dir" ;;
  esac
  common_real="$(canonical_path "$common_dir")"
  if [ "$(basename -- "$common_real")" = .git ]; then
    main_real="$(canonical_path "$(dirname -- "$common_real")")"
    case "$OUTPUT" in
    "$main_real" | "$main_real"/*) fail 'output must be outside the source repository' ;;
    esac
  fi
fi

[ -f "$REPO_ROOT/$MANIFEST_PATH" ] || fail "missing manifest: $MANIFEST_PATH"
[ -f "$REPO_ROOT/$INSTALLER_PATH" ] || fail "missing installer: $INSTALLER_PATH"

# Read the manifest from HEAD, never from a dirty checkout. It is intentionally
# a small allowlist of payload paths; vendor/, auth stores and runtime state do
# not appear here and therefore cannot enter the archive.
manifest_text="$(git -C "$REPO_ROOT" show "HEAD:$MANIFEST_PATH")" || fail "manifest is not present in committed HEAD"
manifest_paths=()
while IFS= read -r line || [ -n "$line" ]; do
  [ -n "$line" ] || continue
  [[ "$line" == \#* ]] && continue
  case "$line" in
  /* | *\\* | ../* | */../* | */.. | . | ./* | *[!A-Za-z0-9_./-]*) fail "unsafe manifest path: $line" ;;
  esac
  manifest_paths+=("$line")
done <<<"$manifest_text"
[ "${#manifest_paths[@]}" -gt 0 ] || fail 'manifest is empty'

for required in global-agents.md skills/ pi/settings.json pi/subagents.json pi/prompts/ pi/themes/ pi/extensions/ pi/agents/ omp/config.yml omp/lsp.yml omp/themes/ omp/overlays/; do
  found=0
  for path in "${manifest_paths[@]}"; do [ "$path" = "$required" ] && found=1; done
  [ "$found" -eq 1 ] || fail "manifest is missing required entry: $required"
done

# A build is allowed with unrelated untracked files (for example local docs),
# but every selected path must match HEAD and selected directories may not have
# untracked children. This prevents accidental local source leakage.
for path in "${manifest_paths[@]}" "$INSTALLER_PATH" "$MANIFEST_PATH"; do
  if ! git -C "$REPO_ROOT" diff --quiet HEAD -- "$path" ||
    ! git -C "$REPO_ROOT" diff --cached --quiet HEAD -- "$path"; then
    fail "selected path is dirty: $path"
  fi
  if [ -n "$(git -C "$REPO_ROOT" status --porcelain=v1 --untracked-files=all -- "$path")" ]; then
    fail "selected path has untracked content: $path"
  fi
  if [[ "$path" != */ ]] && ! git -C "$REPO_ROOT" cat-file -e "HEAD:$path" 2>/dev/null; then
    fail "selected path is missing from committed HEAD: $path"
  fi
done

commit="$(git -C "$REPO_ROOT" rev-parse HEAD)"
parent="$(dirname -- "$OUTPUT")"
[ ! -L "$OUTPUT" ] || fail 'output must not be a symlink'

# Replacement is allowed only when the destination is a bundle this builder
# produced. An unmarked file or directory is left untouched and the caller must
# remove it deliberately before a bundle may take its place.
if [ -e "$OUTPUT" ]; then
  [ -d "$OUTPUT" ] || fail "refusing to replace existing non-directory output: $OUTPUT"
  marker_file="$OUTPUT/$BUNDLE_MARKER_NAME"
  [ -f "$marker_file" ] || fail "refusing to replace unmarked output directory: $OUTPUT"
  [ "$(cat -- "$marker_file")" = "$BUNDLE_MARKER_VALUE" ] ||
    fail "refusing to replace output with unrecognized bundle marker: $OUTPUT"
fi

mkdir -p -- "$parent"
stage="$(mktemp -d "$parent/.bootstrap-build.XXXXXX")"
cleanup() { rm -rf -- "$stage"; }
trap cleanup EXIT
mkdir -p -- "$stage/snapshot"

# git archive reads the tree named by HEAD, not the index or working tree.
# Prefixing the payload keeps the installer from ever reading source checkout
# paths at install time.
git -C "$REPO_ROOT" archive --format=tar --prefix=snapshot/ HEAD \
  -- "$MANIFEST_PATH" "$INSTALLER_PATH" "${manifest_paths[@]}" |
  tar -xf - -C "$stage"

[ -f "$stage/snapshot/$INSTALLER_PATH" ] || fail 'installer was not exported from HEAD'
[ -f "$stage/snapshot/$MANIFEST_PATH" ] || fail 'manifest was not exported from HEAD'
mv -- "$stage/snapshot/$INSTALLER_PATH" "$stage/install.sh"
mv -- "$stage/snapshot/$MANIFEST_PATH" "$stage/manifest.txt"
rmdir -- "$stage/snapshot/sandbox/bootstrap" 2>/dev/null || true
rmdir -- "$stage/snapshot/sandbox" 2>/dev/null || true
chmod 755 "$stage/install.sh"

# The archive must contain only regular files/directories. Reject symlinks
# before writing the installed output, since the guest installer refuses them.
if find "$stage" -type l -print -quit | grep -q .; then
  fail 'archive contains a symlink'
fi

cat >"$stage/VERSION" <<EOF
bundle_format=1
commit=$commit
pi_target_version=0.85.1
omp_target_version=18.1.19
sbx_tested_version=0.42.1
EOF

# Written before SHA256SUMS is generated so the marker is covered by the
# bundle's own checksum list.
printf '%s\n' "$BUNDLE_MARKER_VALUE" >"$stage/$BUNDLE_MARKER_NAME"

checksum() {
  if command -v sha256sum >/dev/null 2>&1; then
    sha256sum -- "$1" | awk '{print $1}'
  elif command -v shasum >/dev/null 2>&1; then
    shasum -a 256 -- "$1" | awk '{print $1}'
  else
    fail 'sha256sum or shasum is required'
  fi
}
(
  cd -- "$stage"
  find . -type f ! -name SHA256SUMS -print | LC_ALL=C sort | while IFS= read -r file; do
    relative="${file#./}"
    printf '%s  %s\n' "$(checksum "$file")" "$relative"
  done
) >"$stage/SHA256SUMS"

# Swap the completed directory into place. Keep the old directory until the
# new rename succeeds so a failed build leaves the previous bundle restorable.
backup=""
if [ -e "$OUTPUT" ]; then
  backup="${OUTPUT}.old.$$"
  [ ! -e "$backup" ] || fail "temporary backup already exists: $backup"
  mv -- "$OUTPUT" "$backup"
fi
if mv -- "$stage" "$OUTPUT"; then
  trap - EXIT
  [ -z "$backup" ] || rm -rf -- "$backup"
else
  if [ -n "$backup" ] && [ ! -e "$OUTPUT" ]; then mv -- "$backup" "$OUTPUT"; fi
  fail 'could not install output bundle'
fi
printf 'built immutable sandbox bundle at %s (HEAD %s)\n' "$OUTPUT" "$commit"
