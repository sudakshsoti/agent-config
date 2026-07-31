#!/usr/bin/env python3
"""Warn when session context crosses a threshold.

Long sessions should be broken at a task boundary rather than run to 300K+.
Measured on this machine (519 sessions, 33,935 API calls): a token added
mid-session is re-billed ~33x as cache read, and the 35% of sessions passing
100K carry 78% of all cost. Drop THRESHOLD to 100000 to track the data.

THRESHOLD and the measurement itself live in context_size.py.

UserPromptSubmit hook. Fails open, never blocks a prompt.
"""

import hashlib
import json
import os
import sys

# realpath, not abspath: this file is invoked through its ~/.claude/hooks
# symlink, and resolving it lands in the repo checkout next to context_size.py
# whether or not install.sh has linked that module out yet.
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))

from context_size import BUCKET, THRESHOLD, measure


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return
    if not isinstance(payload, dict):
        return

    ctx = measure(payload)
    if ctx < THRESHOLD:
        return

    # Warn once per bucket rather than on every prompt above the line. Keyed
    # on the transcript so two concurrent sessions don't silence each other.
    key_source = payload.get("transcript_path") or payload.get("session_id") or ""
    step = (ctx - THRESHOLD) // BUCKET
    key = hashlib.sha1(f"{key_source}:{step}".encode()).hexdigest()[:16]
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
