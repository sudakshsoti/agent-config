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
echo "orient.py build"

# --- splice against the fixture: island must hold the exact payload ---
#
# Reuses the $spool repo-root built above -- its refs already resolve
# against example-payload.json, so this exercises validate-then-splice
# together rather than duplicating the fixture.
build_out=$(python3 "$script" build "$fixture" --repo-root "$spool" 2>&1)
build_status=$?
if [[ $build_status -eq 0 ]]; then
  echo "  ok    build exits 0 on the valid fixture"
  pass=$((pass + 1))
else
  echo "  FAIL  build exits 0 on the valid fixture (exit=$build_status, output=$(printf '%q' "$build_out"))"
  fail=$((fail + 1))
fi

index="$spool/orient/index.html"
payload_out="$spool/orient/payload.json"
if [[ -f "$index" && -f "$payload_out" ]]; then
  echo "  ok    build writes orient/index.html and orient/payload.json"
  pass=$((pass + 1))
else
  echo "  FAIL  build writes orient/index.html and orient/payload.json (index=$([[ -f "$index" ]] && echo present || echo missing), payload=$([[ -f "$payload_out" ]] && echo present || echo missing))"
  fail=$((fail + 1))
fi

if [[ "$build_out" == *"blocks:"* && "$build_out" == *"provenance:"* ]]; then
  echo "  ok    build prints the honest summary (blocks + provenance)"
  pass=$((pass + 1))
else
  echo "  FAIL  build prints the honest summary (blocks + provenance) (output=$(printf '%q' "$build_out"))"
  fail=$((fail + 1))
fi

roundtrip_out=$(python3 - "$index" "$fixture" <<'PY' 2>&1
import json
import re
import sys

html = open(sys.argv[1], encoding="utf-8").read()
m = re.search(r'<script id="orient-data" type="application/json">(.*?)</script>', html, re.DOTALL)
if not m:
    print("ISLAND NOT FOUND")
    sys.exit(1)
try:
    data = json.loads(m.group(1))
except json.JSONDecodeError as e:
    print("ISLAND DID NOT PARSE: %s" % e)
    sys.exit(1)
expected = json.load(open(sys.argv[2], encoding="utf-8"))
if data != expected:
    print("ISLAND CONTENT MISMATCH")
    sys.exit(1)
print("MATCH")
PY
)
roundtrip_status=$?
if [[ $roundtrip_status -eq 0 && "$roundtrip_out" == "MATCH" ]]; then
  echo "  ok    data island round-trips the exact payload"
  pass=$((pass + 1))
else
  echo "  FAIL  data island round-trips the exact payload ($roundtrip_out)"
  fail=$((fail + 1))
fi

# --- a payload containing a literal </script> must not kill the page ---
#
# Without the '</' -> '<\/' escape, this text would terminate the data
# island's script tag early and leave the rest of the document -- including
# the render script -- as broken markup.
script_breakout="$tmp/script-breakout.json"
cat > "$script_breakout" <<'JSON'
{
  "blocks": [
    { "type": "callout", "summary": "Contains a literal </script> tag right in the text, which must not break the page.", "tone": "note" }
  ]
}
JSON

breakout_root="$tmp/breakout-root"
mkdir -p "$breakout_root"

breakout_out=$(python3 "$script" build "$script_breakout" --repo-root "$breakout_root" 2>&1)
breakout_status=$?
if [[ $breakout_status -eq 0 ]]; then
  echo "  ok    build succeeds on a payload containing a literal </script>"
  pass=$((pass + 1))
else
  echo "  FAIL  build succeeds on a payload containing a literal </script> (exit=$breakout_status, output=$(printf '%q' "$breakout_out"))"
  fail=$((fail + 1))
fi

breakout_check=$(python3 - "$breakout_root/orient/index.html" "$script_breakout" <<'PY' 2>&1
import json
import re
import sys
from html.parser import HTMLParser

html = open(sys.argv[1], encoding="utf-8").read()


class Counter(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.script_tags = 0

    def handle_starttag(self, tag, attrs):
        if tag == "script":
            self.script_tags += 1


counter = Counter()
counter.feed(html)

m = re.search(r'<script id="orient-data" type="application/json">(.*?)</script>', html, re.DOTALL)
if not m:
    print("ISLAND NOT FOUND")
    sys.exit(1)
try:
    data = json.loads(m.group(1))
except json.JSONDecodeError as e:
    print("ISLAND DID NOT PARSE: %s" % e)
    sys.exit(1)
expected = json.load(open(sys.argv[2], encoding="utf-8"))
if data != expected:
    print("ISLAND MISMATCH")
    sys.exit(1)
if counter.script_tags != 2:
    print("SCRIPT TAG COUNT %d (want 2: data island + render script)" % counter.script_tags)
    sys.exit(1)
print("OK")
PY
)
breakout_check_status=$?
if [[ $breakout_check_status -eq 0 && "$breakout_check" == "OK" ]]; then
  echo "  ok    literal </script> in the payload still yields a parsing island and an intact page"
  pass=$((pass + 1))
else
  echo "  FAIL  literal </script> in the payload still yields a parsing island and an intact page ($breakout_check)"
  fail=$((fail + 1))
fi

# --- self-containment false positive: a README full of URLs must still build ---
#
# The check must walk markup nodes only (script/link/img with an external
# src/href), never grep the raw file for https?://, or this quoted text
# would be mistaken for an external resource load.
url_heavy="$tmp/url-heavy.json"
cat > "$url_heavy" <<'JSON'
{
  "blocks": [
    {
      "type": "prose",
      "summary": "The README documents installs at https://example.com/install, mirrors at https://mirror.example.org/readme-heavy, docs at https://docs.example.com/readme-heavy/start, a badge linking https://github.com/example/readme-heavy-repo, and a PyPI page at https://pypi.org/project/readme-heavy -- none of these are markup nodes, just quoted text."
    }
  ]
}
JSON

url_root="$tmp/url-root"
mkdir -p "$url_root"

url_out=$(python3 "$script" build "$url_heavy" --repo-root "$url_root" 2>&1)
url_status=$?
if [[ $url_status -eq 0 ]]; then
  echo "  ok    self-containment check does not false-positive on URLs quoted in payload text"
  pass=$((pass + 1))
else
  echo "  FAIL  self-containment check does not false-positive on URLs quoted in payload text (exit=$url_status, output=$(printf '%q' "$url_out"))"
  fail=$((fail + 1))
fi

# --- refuse to overwrite an orient/index.html with uncommitted local edits ---
dirty_root="$tmp/dirty-repo"
mkdir -p "$dirty_root"
git -C "$dirty_root" init -q
git -C "$dirty_root" config user.email "orient-test@example.com"
git -C "$dirty_root" config user.name "orient test"

minimal_payload="$tmp/minimal.json"
cat > "$minimal_payload" <<'JSON'
{
  "blocks": [
    { "type": "callout", "summary": "Minimal payload for the dirty-output-file refusal test.", "tone": "note" }
  ]
}
JSON

first_out=$(python3 "$script" build "$minimal_payload" --repo-root "$dirty_root" 2>&1)
first_status=$?
git -C "$dirty_root" add orient/index.html orient/payload.json
git -C "$dirty_root" commit -q -m "orient: initial build"

# rebuilding a clean, committed output must still be allowed
clean_rebuild_out=$(python3 "$script" build "$minimal_payload" --repo-root "$dirty_root" 2>&1)
clean_rebuild_status=$?

# hand-edit the committed output without committing again
printf '\n<!-- hand edit -->\n' >> "$dirty_root/orient/index.html"

dirty_out=$(python3 "$script" build "$minimal_payload" --repo-root "$dirty_root" 2>&1)
dirty_status=$?

ok=1
[[ $first_status -eq 0 ]] || ok=0
[[ $clean_rebuild_status -eq 0 ]] || ok=0
[[ $dirty_status -ne 0 ]] || ok=0
[[ "$dirty_out" == *"uncommitted"* ]] || ok=0
[[ "$dirty_out" == *"orient/index.html"* ]] || ok=0
if [[ $ok -eq 1 ]]; then
  echo "  ok    build refuses to overwrite orient/index.html with uncommitted local edits"
  pass=$((pass + 1))
else
  echo "  FAIL  build refuses to overwrite orient/index.html with uncommitted local edits (first_status=$first_status clean_rebuild_status=$clean_rebuild_status dirty_status=$dirty_status output=$(printf '%q' "$dirty_out"))"
  fail=$((fail + 1))
fi

if grep -q "hand edit" "$dirty_root/orient/index.html"; then
  echo "  ok    a refused build leaves the dirty file untouched"
  pass=$((pass + 1))
else
  echo "  FAIL  a refused build leaves the dirty file untouched"
  fail=$((fail + 1))
fi

echo
echo "orient.py status"

# --- shared fixture writer -------------------------------------------------
#
# status reads orient/payload.json directly, so these tests hand-write it
# rather than going through `build` (which would additionally require every
# ref to resolve against real files -- irrelevant to what status checks).
# sha="" omits repo.sha entirely, covering the "absent" half of "null or
# absent" from a single writer.
write_status_payload() {  # write_status_payload <root> <sha-or-empty> <builtAt> <sources-json-array>
  local root="$1" sha="$2" built="$3" sources="$4"
  mkdir -p "$root/orient"
  python3 - "$root/orient/payload.json" "$sha" "$built" "$sources" <<'PY'
import json
import sys

out_path, sha, built, sources_json = sys.argv[1:5]
sources = json.loads(sources_json)
repo = {
    "builtAt": built,
    "branch": "main",
    "commitCount": None,
    "remoteUrl": None,
    "vcs": "git",
}
if sha:
    repo["sha"] = sha
payload = {
    "repo": repo,
    "axis": "test axis",
    "sources": sources,
    "tools": {"used": [], "absent": []},
    "blocks": [{"type": "callout", "summary": "test payload", "tone": "note"}],
}
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(payload, f)
PY
}

now_iso() { date -u +%Y-%m-%dT%H:%M:%SZ; }

# --- missing orient/payload.json: informational, not an error --------------
status_missing="$tmp/status-missing"
mkdir -p "$status_missing"
git -C "$status_missing" init -q
git -C "$status_missing" config user.email "orient-test@example.com"
git -C "$status_missing" config user.name "orient test"

status_missing_out=$(python3 "$script" status --repo-root "$status_missing" 2>&1)
status_missing_status=$?
ok=1
[[ $status_missing_status -eq 0 ]] || ok=0
[[ "$status_missing_out" == *"no orient doc yet"* ]] || ok=0
if [[ $ok -eq 1 ]]; then
  echo "  ok    status degrades cleanly when orient/payload.json does not exist"
  pass=$((pass + 1))
else
  echo "  FAIL  status degrades cleanly when orient/payload.json does not exist (exit=$status_missing_status output=$(printf '%q' "$status_missing_out"))"
  fail=$((fail + 1))
fi

# --- non-git directory: age still reported, git-derived fields degrade -----
status_nongit="$tmp/status-nongit"
mkdir -p "$status_nongit"
write_status_payload "$status_nongit" "deadbeefcafe0102030405060708090a0b0c0d0e" "$(now_iso)" '["a.txt","b.txt"]'

status_nongit_out=$(python3 "$script" status --repo-root "$status_nongit" 2>&1)
status_nongit_status=$?
ok=1
[[ $status_nongit_status -eq 0 ]] || ok=0
[[ "$status_nongit_out" == *"not a git repository"* ]] || ok=0
[[ "$status_nongit_out" == *"days ago"* ]] || ok=0
if [[ $ok -eq 1 ]]; then
  echo "  ok    status degrades cleanly on a non-git directory"
  pass=$((pass + 1))
else
  echo "  FAIL  status degrades cleanly on a non-git directory (exit=$status_nongit_status output=$(printf '%q' "$status_nongit_out"))"
  fail=$((fail + 1))
fi

# --- sha absent from history: the shallow-clone analogue --------------------
# A real shallow clone just makes `rev-list`/`diff` against a pre-truncation
# sha fail the same way as an outright bogus sha does -- both are "git ran,
# couldn't resolve the revision," so a made-up sha exercises the same path
# without needing an actual --depth=1 clone.
status_shallow="$tmp/status-shallow"
mkdir -p "$status_shallow"
git -C "$status_shallow" init -q
git -C "$status_shallow" config user.email "orient-test@example.com"
git -C "$status_shallow" config user.name "orient test"
echo "hello" > "$status_shallow/a.txt"
git -C "$status_shallow" add a.txt
git -C "$status_shallow" commit -q -m "initial"

write_status_payload "$status_shallow" "0000000000000000000000000000000000dead" "$(now_iso)" '["a.txt"]'

status_shallow_out=$(python3 "$script" status --repo-root "$status_shallow" 2>&1)
status_shallow_status=$?
ok=1
[[ $status_shallow_status -eq 0 ]] || ok=0
[[ "$status_shallow_out" == *"not found in this repo's history"* ]] || ok=0
if [[ $ok -eq 1 ]]; then
  echo "  ok    status degrades cleanly when the baked sha is absent from history (shallow clone)"
  pass=$((pass + 1))
else
  echo "  FAIL  status degrades cleanly when the baked sha is absent from history (shallow clone) (exit=$status_shallow_status output=$(printf '%q' "$status_shallow_out"))"
  fail=$((fail + 1))
fi

# --- repo.sha null/absent: skip commits-behind and changed-sources ---------
status_nosha="$tmp/status-nosha"
mkdir -p "$status_nosha"
git -C "$status_nosha" init -q
git -C "$status_nosha" config user.email "orient-test@example.com"
git -C "$status_nosha" config user.name "orient test"
write_status_payload "$status_nosha" "" "$(now_iso)" '["a.txt"]'

status_nosha_out=$(python3 "$script" status --repo-root "$status_nosha" 2>&1)
status_nosha_status=$?
ok=1
[[ $status_nosha_status -eq 0 ]] || ok=0
[[ "$status_nosha_out" == *"none recorded in payload.repo.sha"* ]] || ok=0
# The "cannot compute commits behind" gloss on the sha line itself contains
# the phrase "commits behind" -- assert on the absent *metric line*
# ("  commits behind:  ...") specifically, not the substring, or this would
# false-fail against its own explanatory message.
[[ "$status_nosha_out" != *$'\n  commits behind:'* ]] || ok=0
if [[ $ok -eq 1 ]]; then
  echo "  ok    status degrades cleanly when repo.sha is absent from the payload"
  pass=$((pass + 1))
else
  echo "  FAIL  status degrades cleanly when repo.sha is absent from the payload (exit=$status_nosha_status output=$(printf '%q' "$status_nosha_out"))"
  fail=$((fail + 1))
fi

# --- happy path: commits behind and changed sources, untouched source excluded ---
status_happy="$tmp/status-happy"
mkdir -p "$status_happy"
git -C "$status_happy" init -q
git -C "$status_happy" config user.email "orient-test@example.com"
git -C "$status_happy" config user.name "orient test"
echo "a" > "$status_happy/a.txt"
echo "b" > "$status_happy/b.txt"
echo "c" > "$status_happy/c.txt"
git -C "$status_happy" add a.txt b.txt c.txt
git -C "$status_happy" commit -q -m "initial"
happy_sha=$(git -C "$status_happy" rev-parse HEAD)

write_status_payload "$status_happy" "$happy_sha" "$(now_iso)" '["a.txt","b.txt"]'

# Two commits land after the payload's sha: one touches a source (a.txt),
# one touches a file that is not in sources[] (c.txt). b.txt, also a
# source, is never touched and must not be listed as changed.
echo "a2" >> "$status_happy/a.txt"
git -C "$status_happy" add a.txt
git -C "$status_happy" commit -q -m "touch a"
echo "c2" >> "$status_happy/c.txt"
git -C "$status_happy" add c.txt
git -C "$status_happy" commit -q -m "touch c"

status_happy_out=$(python3 "$script" status --repo-root "$status_happy" 2>&1)
status_happy_status=$?
ok=1
[[ $status_happy_status -eq 0 ]] || ok=0
[[ "$status_happy_out" == *"commits behind:  2"* ]] || ok=0
[[ "$status_happy_out" == *"changed sources: 1/2"* ]] || ok=0
[[ "$status_happy_out" == *"- a.txt"* ]] || ok=0
[[ "$status_happy_out" != *"c.txt"* ]] || ok=0
[[ "$status_happy_out" != *"- b.txt"* ]] || ok=0
if [[ $ok -eq 1 ]]; then
  echo "  ok    status reports commits behind and changed sources, excluding an untouched source"
  pass=$((pass + 1))
else
  echo "  FAIL  status reports commits behind and changed sources, excluding an untouched source (exit=$status_happy_status output=$(printf '%q' "$status_happy_out"))"
  fail=$((fail + 1))
fi

# --- more than a few changed sources: named ones capped, remainder counted ---
status_cap="$tmp/status-cap"
mkdir -p "$status_cap"
git -C "$status_cap" init -q
git -C "$status_cap" config user.email "orient-test@example.com"
git -C "$status_cap" config user.name "orient test"
sources_json='['
for i in 1 2 3 4 5 6 7; do
  echo "v0" > "$status_cap/f$i.txt"
  sources_json+="\"f$i.txt\","
done
sources_json="${sources_json%,}]"
git -C "$status_cap" add -A
git -C "$status_cap" commit -q -m "initial"
cap_sha=$(git -C "$status_cap" rev-parse HEAD)

write_status_payload "$status_cap" "$cap_sha" "$(now_iso)" "$sources_json"

for i in 1 2 3 4 5 6 7; do
  echo "v1" >> "$status_cap/f$i.txt"
done
git -C "$status_cap" add -A
git -C "$status_cap" commit -q -m "touch all seven"

status_cap_out=$(python3 "$script" status --repo-root "$status_cap" 2>&1)
status_cap_status=$?
ok=1
[[ $status_cap_status -eq 0 ]] || ok=0
[[ "$status_cap_out" == *"changed sources: 7/7"* ]] || ok=0
[[ "$status_cap_out" == *"(+2 more)"* ]] || ok=0
listed=$(grep -c "^    - f" <<< "$status_cap_out")
[[ "$listed" == "5" ]] || ok=0
if [[ $ok -eq 1 ]]; then
  echo "  ok    status names only the first few changed sources, then a remainder count"
  pass=$((pass + 1))
else
  echo "  FAIL  status names only the first few changed sources, then a remainder count (exit=$status_cap_status output=$(printf '%q' "$status_cap_out"))"
  fail=$((fail + 1))
fi

echo
echo "$pass passed, $fail failed"
[[ $fail -eq 0 ]]
