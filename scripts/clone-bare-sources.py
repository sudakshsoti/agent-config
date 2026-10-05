#!/usr/bin/env python3
"""clone-bare-sources.py — shallow-clone each bare `external` source into vendor/.

lint-skills.py's external-skills.txt drift check only runs where vendor/<slug>
exists, so a checkout without vendor/ never sees upstream add a skill. Run
this, then lint-skills.py, to check a fresh checkout for drift. An existing
clone is left alone. Slugs follow install.sh: <owner>-<repo>.

  ./scripts/clone-bare-sources.py [repo-root]
"""

import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from manifest import parse_plugins_file  # noqa: E402


def main(argv):
    root = argv[1] if len(argv) > 1 else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    entries, errors = parse_plugins_file(os.path.join(root, "plugins.txt"))
    if errors:
        for err in errors:
            sys.stderr.write("plugins.txt:%d: %s\n" % (err.line_no, err.message))
        return 1
    for source in sorted({e.source for e in entries if not e.skills}):
        dest = os.path.join(root, "vendor", source.replace("/", "-", 1))
        if os.path.isdir(dest):
            continue
        print("clone %s -> %s" % (source, os.path.relpath(dest, root)))
        subprocess.run(
            ["git", "clone", "--quiet", "--depth", "1", "https://github.com/%s.git" % source, dest],
            check=True,
        )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
