"""Measure how much context a session is carrying, and where the line sits.

The `context-budget.py` UserPromptSubmit hook is the sole consumer of this
number (it tells Claude to wrap up). Keeping THRESHOLD here rather than
duplicated in the hook avoids a second copy drifting out of sync.

The formula is input-only — `input_tokens + cache_creation + cache_read`,
never `output_tokens`. That is not a choice: it is what Claude Code's own
`context_window.used_percentage` uses (documented at
code.claude.com/docs/en/statusline). Adding output here would put this number
above every other context reading on screen.

Importable, not runnable. Underscored filename so `import context_size` works;
`context-budget.py` keeps its hyphen because settings.json invokes it by path.
"""

import glob
import json
import os

THRESHOLD = 180_000   # absolute and cost-driven, so it does not scale with a larger context window
BUCKET = 50_000       # the hook re-warns each time it climbs another BUCKET


def _sum_usage(usage):
    """Input-side token total of one `usage`-shaped dict, or 0."""
    if not isinstance(usage, dict):
        return 0
    return (
        (usage.get("input_tokens") or 0)
        + (usage.get("cache_read_input_tokens") or 0)
        + (usage.get("cache_creation_input_tokens") or 0)
    )


def from_payload(payload):
    """Context size straight off the payload, or 0 if it isn't there.

    The status line payload carries `context_window.current_usage` — the same
    four counters as a transcript `message.usage`, from the most recent API
    response. Reading it costs nothing, versus walking a JSONL that can run to
    tens of MB on every render.

    It is `null` before the first API call of a session and again after
    `/compact` until the next call repopulates it, so 0 here means "ask the
    transcript", not "no context". Hook payloads omit `context_window`
    entirely and always land on the fallback.
    """
    if not isinstance(payload, dict):
        return 0
    window = payload.get("context_window")
    if not isinstance(window, dict):
        return 0
    usage = window.get("current_usage")
    # Some versions report current_usage as a bare total rather than a
    # breakdown; that total includes output tokens, but it is the only signal
    # available in that shape.
    if isinstance(usage, (int, float)) and not isinstance(usage, bool):
        return int(usage) if usage > 0 else 0
    return _sum_usage(usage)


def resolve_transcript(payload):
    """Path to the session transcript, or None."""
    if not isinstance(payload, dict):
        return None
    path = payload.get("transcript_path")
    if not path:
        # Some hook payloads give only the session id; the transcript is
        # filed under a project directory keyed by cwd, so glob for it.
        session = payload.get("session_id")
        if not session:
            return None
        hits = glob.glob(
            os.path.expanduser(f"~/.claude/projects/**/{session}.jsonl"),
            recursive=True,
        )
        path = hits[0] if hits else None
    if not path or not os.path.isfile(path):
        return None
    return path


def from_transcript(path):
    """Context size from the last main-chain turn in a transcript, or 0.

    Walks forward and keeps overwriting, so the value left standing is the
    most recent usage in the file — which is the current context size, since
    each turn's input already contains every turn before it.
    """
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
                if not isinstance(entry, dict):
                    continue
                # Subagent turns carry their own much smaller context.
                # Counting one would understate the main thread.
                if entry.get("isSidechain"):
                    continue
                msg = entry.get("message")
                if not isinstance(msg, dict):
                    continue
                total = _sum_usage(msg.get("usage"))
                if total > 0:
                    ctx = total
    except Exception:
        return 0
    return ctx


def measure(payload):
    """Current context size in tokens: payload first, transcript as fallback."""
    ctx = from_payload(payload)
    if ctx > 0:
        return ctx
    path = resolve_transcript(payload)
    return from_transcript(path) if path else 0
