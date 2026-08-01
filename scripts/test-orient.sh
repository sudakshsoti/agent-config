#!/usr/bin/env bash
# test-orient.sh — behaviour tests for skills/orient/scripts/orient.py validate
#
# validate is the gate that stops a confident wrong answer reaching the page:
# an unknown block type, a confidence value outside stated|evidenced on a
# goal/decision, or a ref whose path/line/quote doesn't actually check out
# must all be rejected loudly (non-zero exit, readable message) rather than
# spliced into shell.html. This is the only place that contract is enforced,
# so it needs tests before it needs an implementation.
#
#   ./scripts/test-orient.sh
set -uo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
script="$repo_root/skills/orient/scripts/orient.py"
fixture="$repo_root/skills/orient/assets/example-payload.json"
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

pass=0
fail=0

# check <name> <want> <payload-file> <repo-root>
# want: ok (exit 0) or a substring that must appear in combined output on a
# non-zero exit (e.g. the offending block index or field name).
check() {
  local name="$1" want="$2" payload="$3" root="$4"
  local out status
  out=$(python3 "$script" validate "$payload" --repo-root "$root" 2>&1)
  status=$?
  local ok=1
  if [[ "$want" == "ok" ]]; then
    [[ $status -eq 0 ]] || ok=0
  else
    [[ $status -ne 0 ]] || ok=0
    [[ "$out" == *"$want"* ]] || ok=0
  fi
  if [[ $ok -eq 1 ]]; then
    echo "  ok    $name"
    pass=$((pass + 1))
  else
    echo "  FAIL  $name (want=$want, exit=$status, output=$(printf '%q' "$out"))"
    fail=$((fail + 1))
  fi
}

echo "orient.py validate"

if [[ ! -f "$script" ]]; then
  echo "  FAIL  script does not exist: $script"
  echo
  echo "0 passed, 1 failed"
  exit 1
fi

if [[ ! -f "$fixture" ]]; then
  echo "  FAIL  fixture does not exist: $fixture"
  echo
  echo "0 passed, 1 failed"
  exit 1
fi

# --- the valid fixture, against a constructed repo its refs actually resolve against ---
#
# example-payload.json describes a fictional repo ("spool") that does not
# exist on disk. Its refs are only meaningful against a repo-root that
# actually has these files with this exact content at these exact lines, so
# build one rather than pointing validate at agent-config itself.
spool="$tmp/spool"
mkdir -p "$spool/spool" "$spool/docs"

# README.md: line 3 and line 9 must carry the two quoted goal/decision refs
# verbatim. Padding lines keep the numbering honest rather than magic.
{
  echo "# spool"
  echo
  echo "spool exists so I never have to open Lightroom just to dedupe a phone dump."
  echo
  echo "## Sync"
  echo
  echo "Why rsync, not Synology's cloud client:"
  echo
  echo "we use rsync over SSH because Synology's cloud sync silently drops files over 2 GB"
} > "$spool/README.md"

# spool/transcode.py: referenced at line 12, no quote to match, just needs
# to exist with at least 12 lines.
for i in $(seq 1 15); do echo "# line $i"; done > "$spool/spool/transcode.py"

# docs/setup.md: line 22 carries the doc-drift quote verbatim.
{
  for i in $(seq 1 21); do echo "line $i"; done
  echo "run with --dry-run to preview without writing to the NAS"
} > "$spool/docs/setup.md"

# Referenced by path only (no line/quote) -- just need to exist.
echo "# dead code" > "$spool/spool/legacy_uploader.py"
echo "# cli entrypoint" > "$spool/spool/cli.py"
echo "# raspberry pi notes" > "$spool/docs/raspberry-pi-notes.md"

check "valid fixture passes" ok "$fixture" "$spool"

# --- negative cases: small purpose-built payloads, one failure mode each ---

neg="$tmp/neg"
mkdir -p "$neg"

unknown_type="$tmp/unknown-type.json"
cat > "$unknown_type" <<'JSON'
{
  "blocks": [
    { "type": "prose", "summary": "fine" },
    { "type": "bogus", "summary": "not a real block type" }
  ]
}
JSON
check "unknown block type rejected, names the index" "blocks[1]" "$unknown_type" "$neg"

bad_confidence_goal="$tmp/bad-confidence-goal.json"
cat > "$bad_confidence_goal" <<'JSON'
{
  "blocks": [
    { "type": "goal", "summary": "x", "confidence": "guess" }
  ]
}
JSON
check "bad confidence on goal rejected, names the index" "blocks[0]" "$bad_confidence_goal" "$neg"

bad_confidence_decision="$tmp/bad-confidence-decision.json"
cat > "$bad_confidence_decision" <<'JSON'
{
  "blocks": [
    { "type": "prose", "summary": "padding" },
    { "type": "decision", "summary": "x", "confidence": "maybe" }
  ]
}
JSON
check "bad confidence on decision rejected, names the index" "blocks[1]" "$bad_confidence_decision" "$neg"

# ref checks share one small repo: a two-line file to test past-EOF, and a
# one-line file with known content to test verbatim matching.
refroot="$tmp/refroot"
mkdir -p "$refroot"
printf 'line one\nline two\n' > "$refroot/short.txt"
printf 'hello world\n' > "$refroot/quote.txt"

missing_path="$tmp/missing-path.json"
cat > "$missing_path" <<'JSON'
{
  "blocks": [
    { "type": "prose", "summary": "x", "refs": [{ "path": "does/not/exist.md", "line": 1 }] }
  ]
}
JSON
check "ref path that does not exist fails" "does/not/exist.md" "$missing_path" "$refroot"

line_past_eof="$tmp/line-past-eof.json"
cat > "$line_past_eof" <<'JSON'
{
  "blocks": [
    { "type": "prose", "summary": "x", "refs": [{ "path": "short.txt", "line": 50 }] }
  ]
}
JSON
check "ref line past EOF fails" "short.txt" "$line_past_eof" "$refroot"

quote_mismatch="$tmp/quote-mismatch.json"
cat > "$quote_mismatch" <<'JSON'
{
  "blocks": [
    { "type": "prose", "summary": "x", "refs": [{ "path": "quote.txt", "line": 1, "quote": "goodbye world" }] }
  ]
}
JSON
check "ref quote not verbatim fails" "quote.txt" "$quote_mismatch" "$refroot"

echo
echo "$pass passed, $fail failed"
[[ $fail -eq 0 ]]
