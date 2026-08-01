#!/usr/bin/env python3
"""check-zips.py — is every dist/<skill>.zip still in sync with its source?

dist/*.zip is a committed upload artifact (claude.ai and the API install a
skill from a zip, not a symlink), so it drifts the moment somebody edits a
SKILL.md and forgets ./scripts/build-zip.sh. Until now the only guard was a
paragraph of prose in CLAUDE.md.

Byte comparison is not an option: `zip` writes each entry's mtime into its
local header and `-X` does not strip it, so rebuilding byte-identical content
on another checkout produces a different file. What IS stable is the per-entry
CRC32 the archive already stores — compare that against zlib.crc32() of the
source file and the answer depends only on content.

Stdlib only (zipfile + zlib); no rebuild, no temp files, nothing written.

  ./scripts/check-zips.py [repo-root]

Exit 1 if any zip is stale, missing, or orphaned.
"""

import os
import sys
import zipfile
import zlib

# build-zip.sh excludes these; so must we, or a stray macOS turd reads as drift.
EXCLUDED_NAMES = {".DS_Store"}
EXCLUDED_DIRS = {".git", "__pycache__"}


def source_files(skill_dir):
    """Relative paths of every file build-zip.sh would put in the archive."""
    found = {}
    for root, dirs, files in os.walk(skill_dir):
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]
        for name in files:
            if name in EXCLUDED_NAMES:
                continue
            full = os.path.join(root, name)
            found[os.path.relpath(full, os.path.dirname(skill_dir))] = full
    return found


def crc32(path):
    crc = 0
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            crc = zlib.crc32(chunk, crc)
    return crc & 0xFFFFFFFF


def compare(zip_path, skill_dir):
    """Return a list of human-readable differences; empty means fresh."""
    sources = source_files(skill_dir)
    try:
        with zipfile.ZipFile(zip_path) as zf:
            entries = {
                info.filename: info.CRC
                for info in zf.infolist()
                if not info.is_dir()
                and os.path.basename(info.filename) not in EXCLUDED_NAMES
            }
    except (zipfile.BadZipFile, OSError) as exc:
        return ["unreadable zip: %s" % exc]

    diffs = []
    for rel in sorted(set(sources) - set(entries)):
        diffs.append("%s is not in the zip" % rel)
    for rel in sorted(set(entries) - set(sources)):
        diffs.append("%s is in the zip but not in the source" % rel)
    for rel in sorted(set(sources) & set(entries)):
        if crc32(sources[rel]) != entries[rel]:
            diffs.append("%s differs" % rel)
    return diffs


def main(argv):
    if len(argv) > 2:
        sys.stderr.write("usage: check-zips.py [repo-root]\n")
        return 2
    repo_root = argv[1] if len(argv) > 1 else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    skills_dir = os.path.join(repo_root, "skills")
    dist_dir = os.path.join(repo_root, "dist")
    if not os.path.isdir(skills_dir):
        sys.stderr.write("FATAL: no skills/ directory under %s\n" % repo_root)
        return 2

    active = sorted(
        d
        for d in os.listdir(skills_dir)
        if not d.startswith("_")
        and not d.startswith(".")
        and os.path.isfile(os.path.join(skills_dir, d, "SKILL.md"))
    )
    zipped = set()
    if os.path.isdir(dist_dir):
        zipped = {f[: -len(".zip")] for f in os.listdir(dist_dir) if f.endswith(".zip")}

    stale = missing = orphan = 0
    print("dist zips")
    for name in active:
        zip_path = os.path.join(dist_dir, name + ".zip")
        if not os.path.isfile(zip_path):
            print("  FAIL  %s (no dist/%s.zip — run ./scripts/build-zip.sh %s)" % (name, name, name))
            missing += 1
            continue
        diffs = compare(zip_path, os.path.join(skills_dir, name))
        if diffs:
            print(
                "  FAIL  %s (stale: %s — run ./scripts/build-zip.sh %s)"
                % (name, "; ".join(diffs[:3]), name)
            )
            stale += 1
        else:
            print("  ok    %s" % name)

    for name in sorted(zipped - set(active)):
        print("  FAIL  %s (orphan: dist/%s.zip has no active skill — rm it)" % (name, name))
        orphan += 1

    print()
    print(
        "%d active, %d stale, %d missing, %d orphan"
        % (len(active), stale, missing, orphan)
    )
    return 1 if (stale or missing or orphan) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
