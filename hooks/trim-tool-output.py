#!/usr/bin/env python3
"""Cap oversized tool output before it enters context.

Measured on this machine (4 Aug 2026) across 21,004 tool results: 886 of them
(4.2%) account for 64% of every byte of tool output entering context, and the
largest single result was 675,714 characters. Everything in context is
re-billed on every later API call (29.1x median amplification here), so one
unbounded `find` or SQL dump gets re-read dozens of times for the rest of the
session.

This hook trims any Bash/MCP tool result over CAP chars down to a head and a
tail, and spills the full output to /tmp so the model can grep/head it
instead of re-running the command that produced it.

PostToolUse hook. Fails open, never touches a well-behaved result: anything
at or under CAP passes through completely untouched (no stdout at all), and
any error here prints nothing, which leaves the ORIGINAL tool output intact.
"""

import json
import os
import sys
import time

CAP = 20_000    # chars; at or below this, pass through untouched
HEAD = 8_000
TAIL = 4_000

SPILL_ROOT = "/tmp/claude-tool-output"
SPILL_MAX_AGE_SECS = 7 * 24 * 60 * 60   # 7 days


def _prune_old_spill_files():
    # Best-effort housekeeping. A failure here must never affect trimming.
    try:
        cutoff = time.time() - SPILL_MAX_AGE_SECS
        if not os.path.isdir(SPILL_ROOT):
            return
        for session_dir in os.listdir(SPILL_ROOT):
            session_path = os.path.join(SPILL_ROOT, session_dir)
            if not os.path.isdir(session_path):
                continue
            for fname in os.listdir(session_path):
                fpath = os.path.join(session_path, fname)
                try:
                    if os.path.getmtime(fpath) < cutoff:
                        os.remove(fpath)
                except OSError:
                    pass
            try:
                if not os.listdir(session_path):
                    os.rmdir(session_path)
            except OSError:
                pass
    except Exception:
        pass


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return
    if not isinstance(payload, dict):
        return

    tool_output = payload.get("tool_output")
    if tool_output is None:
        return

    # MCP tools return structured content; string tools return a string.
    if isinstance(tool_output, str):
        output = tool_output
    else:
        output = json.dumps(tool_output)

    total = len(output)
    if total <= CAP:
        return

    session_id = payload.get("session_id", "unknown-session")
    tool_use_id = payload.get("tool_use_id", "unknown-tool-use")

    session_dir = os.path.join(SPILL_ROOT, str(session_id))
    spill_path = os.path.join(session_dir, f"{tool_use_id}.txt")

    os.makedirs(session_dir, exist_ok=True)
    with open(spill_path, "w") as f:
        f.write(output)

    _prune_old_spill_files()

    dropped = total - HEAD - TAIL
    marker = (
        f"\n\n... [trimmed {dropped:,} of {total:,} chars to protect context.\n"
        f"     Full output: {spill_path}\n"
        f"     grep/head that file rather than re-running the command.] ...\n\n"
    )
    trimmed = output[:HEAD] + marker + output[-TAIL:]

    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            "updatedToolOutput": trimmed,
        }
    }))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass   # fail open: never corrupt or block a tool result
