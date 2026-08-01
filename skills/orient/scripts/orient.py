#!/usr/bin/env python3
"""orient.py — build and check the /orient payload.

`validate` is the mechanical gate that stops a confident wrong answer
reaching the rendered page: the model can write a `goal` or `decision` with
any confidence word it likes, and it can cite a `ref` that doesn't actually
say what it claims -- `validate` is what catches that before shell.html ever
sees it. `build` runs that gate, then splices the payload into the fixed
shell and writes the finished page. `status` reads an already-built
orient/payload.json back and reports how stale it is against the current
working tree -- age, commits behind, and which of its `sources[]` paths have
since changed -- so a preflight phase can decide whether the existing doc is
still worth trusting. See skills/orient/references/BLOCKS.md for the schema
this enforces.

  python3 orient.py validate <payload.json> [--repo-root ROOT]
  python3 orient.py build <payload.json> [--repo-root ROOT]
  python3 orient.py status [--repo-root ROOT]

Stdlib only, matching scripts/lint-skills.py.
"""

import argparse
import datetime
import json
import os
import re
import subprocess
import sys
from html.parser import HTMLParser

BLOCK_TYPES = {
    "section",
    "prose",
    "goal",
    "decision",
    "flow",
    "map",
    "table",
    "flag",
    "callout",
    "question",
}

# goal and decision are the only types gated by the confidence ladder --
# BLOCKS.md is explicit that "stated" / "evidenced" are the only legal
# values and there is no third value for a guess (that lives in a
# question block's `guess` field instead).
CONFIDENCE_TYPES = {"goal", "decision"}
VALID_CONFIDENCE = {"stated", "evidenced"}


def _refs_in_block(block):
    """Every `ref` object a block carries, in the shapes BLOCKS.md defines.

    Most block types keep them in `refs[]`. `question` is the one exception:
    its optional `guess.refs[]` is still a ref list and still gets opened,
    even though `guess` itself is explicitly not a stated/evidenced claim.
    """
    refs = []
    block_refs = block.get("refs")
    if isinstance(block_refs, list):
        refs.extend(block_refs)
    if block.get("type") == "question":
        guess = block.get("guess")
        if isinstance(guess, dict):
            guess_refs = guess.get("refs")
            if isinstance(guess_refs, list):
                refs.extend(guess_refs)
    return refs


def _check_ref(ref, ctx, repo_root, errors):
    if not isinstance(ref, dict):
        errors.append("%s: ref is not an object" % ctx)
        return

    path = ref.get("path")
    if not path or not isinstance(path, str):
        errors.append("%s: ref missing a 'path'" % ctx)
        return

    full_path = os.path.join(repo_root, path)
    try:
        with open(full_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except OSError as e:
        errors.append("%s: ref path does not exist: %s (%s)" % (ctx, path, e.strerror or e))
        return

    line = ref.get("line")
    quote = ref.get("quote")

    if line is None:
        if quote is not None:
            errors.append(
                "%s: ref has a 'quote' but no 'line' to verify it against: %s" % (ctx, path)
            )
        return

    if not isinstance(line, int) or line < 1 or line > len(lines):
        errors.append(
            "%s: ref line %r is past EOF in %s (%d lines)" % (ctx, line, path, len(lines))
        )
        return

    if quote is not None:
        actual = lines[line - 1].rstrip("\n")
        if quote not in actual:
            errors.append(
                "%s: ref quote is not verbatim at %s:%d\n"
                "      wanted: %r\n"
                "      found:  %r" % (ctx, path, line, quote, actual)
            )


def _walk_blocks(blocks, prefix, repo_root, errors):
    if not isinstance(blocks, list):
        errors.append("%s: must be a list of blocks" % prefix)
        return

    for i, block in enumerate(blocks):
        ctx = "%s[%d]" % (prefix, i)

        if not isinstance(block, dict):
            errors.append("%s: block is not an object" % ctx)
            continue

        btype = block.get("type")
        if btype not in BLOCK_TYPES:
            errors.append("%s: unknown block type %r" % (ctx, btype))
            continue

        if btype in CONFIDENCE_TYPES:
            confidence = block.get("confidence")
            if confidence not in VALID_CONFIDENCE:
                errors.append(
                    "%s: %s block has confidence %r, must be 'stated' or 'evidenced'"
                    % (ctx, btype, confidence)
                )

        for ref in _refs_in_block(block):
            _check_ref(ref, ctx, repo_root, errors)

        if btype == "section":
            _walk_blocks(block.get("blocks", []), ctx + ".blocks", repo_root, errors)


def validate_payload(payload, repo_root):
    """Return a list of human-readable error strings; empty means valid."""
    errors = []

    if not isinstance(payload, dict):
        errors.append("payload must be a JSON object")
        return errors

    if "blocks" not in payload:
        errors.append("payload missing top-level 'blocks'")
        return errors

    _walk_blocks(payload["blocks"], "blocks", repo_root, errors)
    return errors


def _walk_all_blocks(blocks):
    """Yield every block, recursing into section.blocks -- the same shape
    _walk_blocks validates against, but flattened for the build summary
    rather than collecting errors."""
    for block in blocks or []:
        if not isinstance(block, dict):
            continue
        yield block
        if block.get("type") == "section":
            for sub in _walk_all_blocks(block.get("blocks", [])):
                yield sub


def _summarize(payload):
    """The honest-summary numbers `cmd_build` prints: how many blocks, how
    many refs were verified, the provenance split, and the tools ledger.

    `refs_dropped` is always empty under the current contract: `build` runs
    `validate_payload` first and bails on any error, so by the time this
    runs, every ref that reached here already resolved. The field stays in
    the summary shape anyway -- printing an empty list is the honest answer,
    not an omission, and keeps the summary format stable if a future,
    looser build mode ever does drop blocks instead of refusing outright.
    """
    blocks = list(_walk_all_blocks(payload.get("blocks", [])))
    total_refs = 0
    for block in blocks:
        total_refs += len(_refs_in_block(block))

    stated = sum(
        1 for b in blocks if b.get("type") in CONFIDENCE_TYPES and b.get("confidence") == "stated"
    )
    evidenced = sum(
        1
        for b in blocks
        if b.get("type") in CONFIDENCE_TYPES and b.get("confidence") == "evidenced"
    )
    questions = sum(1 for b in blocks if b.get("type") == "question")

    tools = payload.get("tools") or {}
    return {
        "blocks": len(blocks),
        "refs_total": total_refs,
        "refs_verified": total_refs,
        "refs_dropped": [],
        "stated": stated,
        "evidenced": evidenced,
        "questions": questions,
        "tools_used": list(tools.get("used") or []),
        "tools_absent": list(tools.get("absent") or []),
    }


def _shell_html_path():
    """Locate assets/shell.html relative to this script's own real location,
    never cwd -- at runtime cwd is the *target* repo being documented, not
    the skill.

    Resolved through os.path.realpath deliberately: this script is reached
    in production through a symlinked directory
    (~/.claude/skills/orient -> this checkout's skills/orient), and may in
    principle be reached through a symlinked file too. realpath collapses
    either kind of symlink down to the real path on disk before we go
    looking for ../assets/shell.html, so the lookup is correct regardless of
    which link shape is in play at the call site.
    """
    here = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(here, "..", "assets", "shell.html")


_ISLAND_RE = re.compile(
    r'(<script id="orient-data" type="application/json">)(.*?)(</script>)', re.DOTALL
)


def _escape_data_island(json_text):
    """Escape '</' as '<\\/' so a payload quoting a literal '</script>'
    cannot terminate the data island's script tag early and kill the rest of
    the page. JSON parsers treat '\\/' as an escaped '/', so this round-trips
    losslessly through JSON.parse -- it changes the bytes on disk, not the
    value the page reads back.
    """
    return json_text.replace("</", "<\\/")


def splice_payload(shell_html, payload):
    """Return shell_html with the (validated) payload spliced into the
    `orient-data` island, `</` escaped so the splice can't break the page.
    """
    json_text = _escape_data_island(json.dumps(payload, indent=2, ensure_ascii=False))
    matches = list(_ISLAND_RE.finditer(shell_html))
    if len(matches) != 1:
        raise ValueError(
            "expected exactly one orient-data script island in shell.html, found %d"
            % len(matches)
        )
    start, end = matches[0].start(2), matches[0].end(2)
    return shell_html[:start] + json_text + shell_html[end:]


class _SelfContainmentChecker(HTMLParser):
    """Walks actual markup nodes only. HTMLParser treats <script> and
    <style> contents as opaque CDATA-like text (handle_data, never
    handle_starttag) until their closing tag, so a URL quoted inside the
    JSON data island -- which lives as the *text* of a <script> element --
    is never seen as a tag attribute here. That is the property the
    self-containment false-positive test in test-orient.sh pins down: this
    must not degrade into a whole-file grep for https?://.
    """

    _EXTERNAL = re.compile(r"^https?://", re.IGNORECASE)

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.violations = []

    def _external(self, url):
        return bool(url) and self._EXTERNAL.match(url) is not None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "script" and self._external(attrs.get("src")):
            self.violations.append("<script src=%r>" % attrs.get("src"))
        elif tag == "link" and self._external(attrs.get("href")):
            self.violations.append("<link href=%r>" % attrs.get("href"))
        elif tag == "img" and self._external(attrs.get("src")):
            self.violations.append("<img src=%r>" % attrs.get("src"))


def check_self_contained(html_text):
    """Return a list of external markup-node violations, empty if none.
    <a href> is deliberately not checked -- BLOCKS.md is explicit that
    external links there are fine; only script/link/img loads reach out."""
    parser = _SelfContainmentChecker()
    parser.feed(html_text)
    return parser.violations


def _output_is_dirty(repo_root, rel_path):
    """True if <repo_root>/<rel_path> has uncommitted state relative to git
    -- modified, staged, or untracked all count, since any of them means a
    blind overwrite could clobber something not yet in history.

    A target that isn't a git repo, or has no git on PATH, can't be
    protected this way: that degrades to "not dirty" so build can still run
    somewhere with no version control, rather than refusing to ever build
    there.
    """
    try:
        proc = subprocess.run(
            ["git", "status", "--porcelain", "--", rel_path],
            cwd=repo_root,
            capture_output=True,
            text=True,
        )
    except OSError:
        return False
    if proc.returncode != 0:
        return False
    return bool(proc.stdout.strip())


def _run_git(args, repo_root):
    """Run `git <args>` in repo_root. Returns (ok, stdout_text_or_reason).

    ok is False on a missing git binary, a directory with no git on PATH,
    a directory that isn't a git repo at all, or any nonzero exit (e.g.
    `rev-list`/`diff` against a sha that predates a shallow clone's
    history, which git reports as a bad revision) -- `status` treats every
    one of those as the same "can't tell" degrade path, not a crash.
    """
    try:
        proc = subprocess.run(
            ["git"] + args, cwd=repo_root, capture_output=True, text=True
        )
    except OSError as e:
        return False, str(e)
    if proc.returncode != 0:
        return False, (proc.stderr.strip() or "git command failed")
    return True, proc.stdout


def _is_git_repo(repo_root):
    ok, out = _run_git(["rev-parse", "--is-inside-work-tree"], repo_root)
    return ok and out.strip() == "true"


def _parse_iso8601(text):
    """Parse repo.builtAt into an aware datetime, or None if it's missing
    or malformed. Handles the trailing 'Z' that datetime.fromisoformat only
    started accepting directly in 3.11 -- rewriting it to '+00:00' keeps
    this working on older stdlib.
    """
    if not isinstance(text, str) or not text:
        return None
    candidate = text[:-1] + "+00:00" if text.endswith("Z") else text
    try:
        dt = datetime.datetime.fromisoformat(candidate)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=datetime.timezone.utc)
    return dt


def cmd_build(args):
    try:
        with open(args.payload, "r", encoding="utf-8") as f:
            raw = f.read()
    except OSError as e:
        sys.stderr.write("orient build: FAIL  cannot read %s: %s\n" % (args.payload, e))
        return 1

    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as e:
        sys.stderr.write("orient build: FAIL  %s is not valid JSON: %s\n" % (args.payload, e))
        return 1

    repo_root = args.repo_root or os.getcwd()
    errors = validate_payload(payload, repo_root)
    if errors:
        sys.stderr.write(
            "orient build: FAIL  %d problem(s) in %s\n" % (len(errors), args.payload)
        )
        for e in errors:
            sys.stderr.write("  - %s\n" % e)
        return 1

    out_dir = os.path.join(repo_root, "orient")
    index_path = os.path.join(out_dir, "index.html")
    index_rel = os.path.join("orient", "index.html")
    if os.path.exists(index_path) and _output_is_dirty(repo_root, index_rel):
        sys.stderr.write(
            "orient build: FAIL  %s has uncommitted local edits; "
            "commit or discard them before rebuilding: %s\n" % (index_rel, index_path)
        )
        return 1

    shell_path = _shell_html_path()
    try:
        with open(shell_path, "r", encoding="utf-8") as f:
            shell_html = f.read()
    except OSError as e:
        sys.stderr.write("orient build: FAIL  cannot read shell.html at %s: %s\n" % (shell_path, e))
        return 1

    try:
        spliced = splice_payload(shell_html, payload)
    except ValueError as e:
        sys.stderr.write("orient build: FAIL  %s\n" % e)
        return 1

    # Checked on the in-memory string, before anything is written, so a
    # violation never leaves a half-built orient/ directory behind.
    violations = check_self_contained(spliced)
    if violations:
        sys.stderr.write(
            "orient build: FAIL  %d self-containment violation(s) -- an external "
            "resource was found in markup:\n" % len(violations)
        )
        for v in violations:
            sys.stderr.write("  - %s\n" % v)
        return 1

    os.makedirs(out_dir, exist_ok=True)
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(spliced)
    with open(os.path.join(out_dir, "payload.json"), "w", encoding="utf-8") as f:
        f.write(json.dumps(payload, indent=2, ensure_ascii=False))
        f.write("\n")

    summary = _summarize(payload)
    print("orient build: ok  %s" % index_path)
    print("  blocks:        %d" % summary["blocks"])
    print(
        "  refs verified: %d/%d (%d dropped)"
        % (summary["refs_verified"], summary["refs_total"], len(summary["refs_dropped"]))
    )
    for dropped in summary["refs_dropped"]:
        print("    - %s" % dropped)
    print(
        "  provenance:    %d stated, %d evidenced, %d question(s)"
        % (summary["stated"], summary["evidenced"], summary["questions"])
    )
    print("  tools used:    %s" % (", ".join(summary["tools_used"]) or "(none)"))
    print("  tools absent:  %s" % (", ".join(summary["tools_absent"]) or "(none)"))
    return 0


def cmd_validate(args):
    try:
        with open(args.payload, "r", encoding="utf-8") as f:
            raw = f.read()
    except OSError as e:
        sys.stderr.write("orient validate: FAIL  cannot read %s: %s\n" % (args.payload, e))
        return 1

    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as e:
        sys.stderr.write("orient validate: FAIL  %s is not valid JSON: %s\n" % (args.payload, e))
        return 1

    repo_root = args.repo_root or os.getcwd()
    errors = validate_payload(payload, repo_root)

    if errors:
        sys.stderr.write(
            "orient validate: FAIL  %d problem(s) in %s\n" % (len(errors), args.payload)
        )
        for e in errors:
            sys.stderr.write("  - %s\n" % e)
        return 1

    print("orient validate: ok  %s" % args.payload)
    return 0


# The first few changed sources named on their own lines before falling
# back to a "(+N more)" count -- the plan asks for "listing the first few
# by name", not a dump of every path, since this output is read by a model
# during preflight and needs to stay skimmable.
_STATUS_SOURCES_SHOWN = 5


def cmd_status(args):
    repo_root = args.repo_root or os.getcwd()
    payload_path = os.path.join(repo_root, "orient", "payload.json")

    try:
        with open(payload_path, "r", encoding="utf-8") as f:
            raw = f.read()
    except OSError:
        print(
            "orient status: no orient doc yet -- %s does not exist. "
            "Run `orient.py build` first." % payload_path
        )
        return 0

    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as e:
        sys.stderr.write(
            "orient status: FAIL  %s is not valid JSON: %s\n" % (payload_path, e)
        )
        return 1

    if not isinstance(payload, dict):
        sys.stderr.write("orient status: FAIL  %s is not a JSON object\n" % payload_path)
        return 1

    repo = payload.get("repo")
    if not isinstance(repo, dict):
        repo = {}
    sources = payload.get("sources")
    if not isinstance(sources, list):
        sources = []

    print("orient status: %s" % payload_path)

    dt = _parse_iso8601(repo.get("builtAt"))
    if dt is not None:
        age_days = (datetime.datetime.now(datetime.timezone.utc) - dt).days
        print(
            "  built:           %s (%d day%s ago)"
            % (repo.get("builtAt"), age_days, "" if age_days == 1 else "s")
        )
    else:
        print("  built:           unknown -- repo.builtAt is missing or unparseable")

    sha = repo.get("sha")
    if not sha or not isinstance(sha, str):
        print(
            "  sha:             none recorded in payload.repo.sha -- "
            "cannot compute commits behind or changed sources"
        )
        return 0
    print("  sha:             %s" % sha)

    if not _is_git_repo(repo_root):
        print("  commits behind:  unknown -- %s is not a git repository" % repo_root)
        print("  changed sources: unknown -- %s is not a git repository" % repo_root)
        return 0

    behind_ok, behind_out = _run_git(["rev-list", "--count", "%s..HEAD" % sha], repo_root)
    if behind_ok:
        print("  commits behind:  %s" % behind_out.strip())
    else:
        print(
            "  commits behind:  unknown -- %s not found in this repo's history "
            "(shallow clone?)" % sha
        )

    diff_ok, diff_out = _run_git(["diff", "--name-only", "%s..HEAD" % sha], repo_root)
    if not diff_ok:
        print(
            "  changed sources: unknown -- %s not found in this repo's history "
            "(shallow clone?)" % sha
        )
        return 0

    changed_paths = {line for line in diff_out.splitlines() if line.strip()}
    changed_sources = sorted(p for p in sources if p in changed_paths)
    print(
        "  changed sources: %d/%d since build" % (len(changed_sources), len(sources))
    )
    for path in changed_sources[:_STATUS_SOURCES_SHOWN]:
        print("    - %s" % path)
    remaining = len(changed_sources) - _STATUS_SOURCES_SHOWN
    if remaining > 0:
        print("    (+%d more)" % remaining)

    return 0


def main(argv):
    parser = argparse.ArgumentParser(prog="orient.py")
    sub = parser.add_subparsers(dest="command", required=True)

    p_validate = sub.add_parser("validate", help="validate a payload against the block contract")
    p_validate.add_argument("payload", help="path to the payload JSON file")
    p_validate.add_argument(
        "--repo-root",
        default=None,
        help="repo root ref paths are resolved against (default: cwd)",
    )
    p_validate.set_defaults(func=cmd_validate)

    p_build = sub.add_parser(
        "build", help="validate a payload, splice it into shell.html, and write orient/"
    )
    p_build.add_argument("payload", help="path to the payload JSON file")
    p_build.add_argument(
        "--repo-root",
        default=None,
        help="repo root ref paths are resolved against and orient/ is written under (default: cwd)",
    )
    p_build.set_defaults(func=cmd_build)

    p_status = sub.add_parser(
        "status",
        help="report staleness of an existing orient/payload.json against the working tree",
    )
    p_status.add_argument(
        "--repo-root",
        default=None,
        help="repo root to read orient/payload.json from and run git against (default: cwd)",
    )
    p_status.set_defaults(func=cmd_status)

    args = parser.parse_args(argv[1:])
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
