#!/usr/bin/env python3
"""orient.py — build and check the /orient payload.

Only the `validate` subcommand exists so far; `build` and `status` are later
items in plans/2026-08-02-orient-skill.md. This is the mechanical gate that
stops a confident wrong answer reaching the rendered page: the model can
write a `goal` or `decision` with any confidence word it likes, and it can
cite a `ref` that doesn't actually say what it claims -- `validate` is what
catches that before shell.html ever sees it. See
skills/orient/references/BLOCKS.md for the schema this enforces.

  python3 orient.py validate <payload.json> [--repo-root ROOT]

Stdlib only, matching scripts/lint-skills.py.
"""

import argparse
import json
import os
import sys

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

    args = parser.parse_args(argv[1:])
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
