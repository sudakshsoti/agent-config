#!/usr/bin/env python3
"""Warn when session context crosses a threshold.

Long sessions should be broken at a task boundary rather than run to 300K+.
Measured on this machine (519 sessions, 33,935 API calls): a token added
mid-session is re-billed ~33x as cache read, and the 35% of sessions passing
100K carry 78% of all cost. Drop THRESHOLD to 100000 to track the data.

UserPromptSubmit hook. Fails open, never blocks a prompt.
"""

import glob
import hashlib
import json
import os
import sys

THRESHOLD = 150_000   # warn once context passes this
BUCKET = 50_000       # re-warn each time it climbs another BUCKET


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return
    if not isinstance(payload, dict):
        return

    path = payload.get("transcript_path")
    session = payload.get("session_id")

    # Fall back to locating the transcript by session id if the payload omits it.
    if not path and session:
        hits = glob.glob(
            os.path.expanduser(f"~/.claude/projects/**/{session}.jsonl"),
            recursive=True,
        )
        path = hits[0] if hits else None

    if not path or not os.path.isfile(path):
        return

    ctx = 0
    try:
        with open(path, errors="ignore") as fh:
            for line in fh:
                if '"usage"' not in line:
                    continue
                try:
                    entry = json.loads(line)
                except Exception:
                    continue
                # Subagent turns carry their own much smaller context. Counting one
                # would understate the main thread and silence the warning.
                if entry.get("isSidechain"):
                    continue
                msg = entry.get("message") or {}
                usage = msg.get("usage") if isinstance(msg, dict) else None
                if not isinstance(usage, dict):
                    continue
                total = (
                    (usage.get("input_tokens") or 0)
                    + (usage.get("cache_read_input_tokens") or 0)
                    + (usage.get("cache_creation_input_tokens") or 0)
                )
                if total > 0:
                    ctx = total   # last main-chain usage = current context size
    except Exception:
        return

    if ctx < THRESHOLD:
        return

    # Warn once per bucket rather than on every prompt above the line.
    step = (ctx - THRESHOLD) // BUCKET
    key = hashlib.sha1(f"{path}:{step}".encode()).hexdigest()[:16]
    stamp = os.path.join("/tmp", f"claude-ctx-{key}")
    if os.path.exists(stamp):
        return
    try:
        open(stamp, "w").close()
    except Exception:
        pass

    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": (
                f"Context is at ~{ctx // 1000}K tokens, past the "
                f"{THRESHOLD // 1000}K break threshold. Everything already in "
                f"context is re-billed on every remaining call this session "
                f"(~33x on average here). Finish the current item, commit it, "
                f"then tell the user this is a good point to /clear (or "
                f"/handoff then /clear if continuity is needed). Do not start "
                f"new exploratory work in this session; delegate any further "
                f"searching to a subagent."
            ),
        }
    }))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass   # a warning is never worth breaking a prompt over
