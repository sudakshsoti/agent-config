#!/usr/bin/env python3
"""Status line widget: the context group's label, which shouts when it should.

ccstatusline's `context-percentage` widget is pinned to a single colour, and
there is no value-driven colouring anywhere in it — its gradients are
positional, painted across a widget's own characters, not mapped to the value.
So the one reading that ought to raise its voice cannot. This is the gap that
forces a `custom-command` widget with `preserveColors: true`, which is the
only way a script gets to emit its own ANSI.

It renders the group's label rather than adding a separate flag, because line
2 has about 3 spare columns at width 150 and a standalone "▲ CLEAR" costs 8 —
enough to truncate the 7-day reset timer at exactly the moment the line is
worth reading. Swapping a 3-char label for a 5-char one costs 2.

    under threshold ->  ctx     (grey, indistinguishable from the old label)
    over threshold  ->  CLEAR   (red)

Errors print nothing and exit 0; a status line that prints a traceback is
worse than one that prints nothing. That silence is why
`scripts/test-ctx-flag.sh` exists. The visible cost of a failure is a missing
label, which is the failure mode you notice rather than the one you don't.

Reads the Claude Code status payload on stdin (ccstatusline forwards it
verbatim, plus a `terminal_width` it adds itself).
"""

import json
import sys
from pathlib import Path

# The threshold and the measurement both live with the hook that shares them,
# so the status line and the hook can never disagree about when to break.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "hooks"))

LABEL = "ctx"
ALERT = "CLEAR"
GREY = "\033[38;2;130;134;137m"   # hex:828689, the line's muted label colour
RED = "\033[38;2;225;116;107m"    # muted red, same saturation family as line 2
RESET = "\033[39m"


def main():
    from context_size import THRESHOLD, measure

    try:
        payload = json.load(sys.stdin)
    except Exception:
        return

    if measure(payload) >= THRESHOLD:
        sys.stdout.write(f"{RED}{ALERT}{RESET}")
    else:
        sys.stdout.write(f"{GREY}{LABEL}{RESET}")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass   # never let a status line widget surface an error
