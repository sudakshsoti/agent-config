#!/usr/bin/env python3
"""Compare an installed Claude plugin's commit with its claude/plugins.txt pin.

    plugin-pin.py <installed_plugins.json> <plugin_id> <pinned_commit>

Prints one warning line when the installed commit differs from the pin, or
when the registry cannot be read or has an unexpected shape. Prints nothing
when the plugin is at the pin or is not installed. Always exits 0: install.sh
treats drift as advisory.
"""

import json
import sys


def check(path, plugin_id, pin):
    try:
        with open(path, encoding="utf-8") as handle:
            entries = json.load(handle)["plugins"].get(plugin_id, [])
        installed = entries[0]["gitCommitSha"] if entries else ""
        if not isinstance(installed, str):
            raise TypeError("gitCommitSha is not a string")
    except (OSError, ValueError, KeyError, IndexError, TypeError, AttributeError) as error:
        return (
            f"⚠️  cannot read the installed commit of {plugin_id} from {path} "
            f"({type(error).__name__}: {error}); pin drift not checked."
        )
    if installed and installed != pin:
        return f"⚠️  {plugin_id} is at {installed[:8]}, claude/plugins.txt pins {pin[:8]}."
    return ""


def main(argv):
    if len(argv) != 4:
        print(__doc__, file=sys.stderr)
        return 2
    warning = check(*argv[1:])
    if warning:
        print(warning)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
