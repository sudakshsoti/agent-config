#!/usr/bin/env python3
"""check-claude-path.py — verify the Pi → Claude path still holds, after an update.

The Pi/Claude route has two independent halves, and either can rot silently:

1. **The prompt trigger.** Pi's `docs` section carries an enumeration that
   Anthropic's classifier reads as third-party traffic
   (`earendil-works/pi#6888`). `pi/extensions/anthropic-prompt-shim/` removes
   it. If upstream rewords the line, the shim stops matching and quietly
   becomes a no-op — the failure looks like a billing change, not a bug.
2. **The billing-header shim.** `@gotgenes/pi-anthropic-auth` supplies the
   header that stops the request being billed as third-party usage. It needs a
   minimum Pi version and an OAuth credential to do anything at all.

Every check below is a fact this repo has already got wrong once:

- Pi 0.85.1 was below the extension's 0.86.0 floor, so the install was inert.
- `auth.json` held only `opencode-go` since 2026-09-16, so the shim had no
  token to shape and every request failed with "No API key found for anthropic".
- The shim's own triggers are upstream strings; a rewording disables it
  without an error.

Run after every `pi update`:

  ./scripts/check-claude-path.py

Stdlib only: this must run on a box with no repo dependencies installed.
Exits 0 with findings, like `audit-local.py`; it reports, it does not gate
`check.sh`, because a missing credential is a normal state on a fresh box and
must not fail everyone else's build.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys

PI_AGENT_DIR = os.path.expanduser(os.environ.get("PI_AGENT_DIR", "~/.pi/agent"))
SETTINGS = os.path.join(PI_AGENT_DIR, "settings.json")
AUTH = os.path.join(PI_AGENT_DIR, "auth.json")

SHIM_PACKAGE = "@gotgenes/pi-anthropic-auth"
# The extension's own peer floor. Raise when its README raises it.
SHIM_MIN_PI = (0, 86, 0)
# The upstream substring the prompt shim removes. Reworded upstream => the shim
# silently stops firing, which is the failure this check exists to catch.
PROMPT_TRIGGER = "When asked about:"

OK, WARN, FAIL = "ok", "warn", "FAIL"


class Finding:
    def __init__(self, level, subject, detail, hint=None):
        self.level = level
        self.subject = subject
        self.detail = detail
        self.hint = hint


def read_json(path):
    try:
        with open(path, encoding="utf-8") as handle:
            return json.load(handle)
    except OSError:
        return None
    except ValueError:
        return "invalid"


def parse_version(text):
    """Leading numeric triple of a version string, or None."""
    match = re.match(r"^\s*(\d+)\.(\d+)\.(\d+)", text or "")
    return tuple(int(part) for part in match.groups()) if match else None


def pi_version():
    """Installed Pi version, or a reason it could not be read."""
    try:
        result = subprocess.run(
            ["pi", "--version"],
            capture_output=True,
            text=True,
            timeout=60,
            stdin=subprocess.DEVNULL,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return None, f"could not run `pi --version`: {exc}"
    if result.returncode != 0:
        return None, f"`pi --version` exited {result.returncode}"
    return parse_version(result.stdout), None


def check_pi_version():
    version, error = pi_version()
    if error:
        return Finding(FAIL, "pi version", error, "install Pi or fix PATH")
    if version < SHIM_MIN_PI:
        floor = ".".join(str(part) for part in SHIM_MIN_PI)
        return Finding(
            FAIL,
            "pi version",
            f"{'.'.join(str(p) for p in version)} is below the {floor} "
            f"floor required by {SHIM_PACKAGE}",
            "run `npm install -g --ignore-scripts @earendil-works/pi-coding-agent@latest`",
        )
    return Finding(OK, "pi version", ".".join(str(part) for part in version))


def check_shim_installed(settings):
    if settings is None:
        return Finding(FAIL, "shim package", f"{SETTINGS} not found or unreadable")
    if settings == "invalid":
        return Finding(FAIL, "shim package", f"{SETTINGS} is not valid JSON")
    packages = settings.get("packages") or []
    names = []
    for entry in packages:
        name = entry[4:] if entry.startswith("npm:") else entry
        if name.startswith("@"):
            head, _, tail = name.rpartition("@")
            name = head if head and tail else name
        else:
            name = name.split("@", 1)[0]
        names.append(name)
    if SHIM_PACKAGE not in names:
        return Finding(
            FAIL,
            "shim package",
            f"{SHIM_PACKAGE} is not in settings packages[]",
            "run `pi install npm:" + SHIM_PACKAGE + "`",
        )
    return Finding(OK, "shim package", "installed")


def check_credential(auth):
    """The shim is inert without an OAuth credential to shape."""
    if auth is None:
        return Finding(
            FAIL,
            "anthropic credential",
            f"{AUTH} not found",
            "run /login anthropic in pi",
        )
    if auth == "invalid":
        return Finding(FAIL, "anthropic credential", f"{AUTH} is not valid JSON")
    if "anthropic" not in auth:
        return Finding(
            FAIL,
            "anthropic credential",
            "no `anthropic` entry, so the shim has nothing to shape and every "
            "request fails with 'No API key found for anthropic'",
            "run /login anthropic in pi (interactive, per box)",
        )
    entry = auth.get("anthropic") or {}
    kind = entry.get("type") if isinstance(entry, dict) else None
    if kind != "oauth":
        return Finding(
            WARN,
            "anthropic credential",
            f"present but type is {kind!r}; the shim activates only on an "
            "sk-ant-oat OAuth token",
            "an API key bills per token and needs no shim",
        )
    return Finding(OK, "anthropic credential", "OAuth present")


def subprocess_which(name):
    for directory in os.environ.get("PATH", "").split(os.pathsep):
        candidate = os.path.join(directory, name)
        if os.access(candidate, os.X_OK):
            return candidate
    return None


def probe_installed_prompt():
    """Render Pi's real system prompt and report whether the trigger is present."""
    pi_path = subprocess_which("pi")
    if not pi_path:
        return Finding(FAIL, "prompt trigger", "`pi` not on PATH")
    # The `pi` shim points at <pkg>/dist/bundle/cli.js, so walking up from its
    # directory starts inside dist/. Search upward for the module rather than
    # assuming a fixed depth, which silently breaks on a layout change.
    start = os.path.dirname(os.path.realpath(pi_path))
    module = None
    probe = start
    for _ in range(4):
        candidate = os.path.join(probe, "core", "system-prompt.js")
        if os.path.exists(candidate):
            module = candidate
            break
        probe = os.path.dirname(probe)
    if module is None:
        return Finding(
            WARN,
            "prompt trigger",
            f"system-prompt.js not found above {start}; cannot verify the trigger",
            "Pi's layout changed — re-read how the prompt is built",
        )
    script = (
        "import {buildSystemPrompt} from "
        + json.dumps(module)
        + ";process.stdout.write(buildSystemPrompt({cwd:process.cwd()}));"
    )
    try:
        result = subprocess.run(
            ["node", "--input-type=module", "-e", script],
            capture_output=True, text=True, timeout=60,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return Finding(WARN, "prompt trigger", f"could not render prompt: {exc}")
    if result.returncode != 0:
        return Finding(
            WARN, "prompt trigger",
            f"rendering failed: {result.stderr.strip()[:200]}",
        )
    prompt = result.stdout
    if PROMPT_TRIGGER in prompt:
        return Finding(
            OK,
            "prompt trigger",
            f"{PROMPT_TRIGGER!r} still present, so the shim is doing work",
        )
    return Finding(
        WARN,
        "prompt trigger",
        f"{PROMPT_TRIGGER!r} is gone from the installed Pi's prompt",
        "the shim is now a no-op — re-check #6888 and the shim's trigger list",
    )


def check_shim_extension(repo):
    path = os.path.join(repo, "pi", "extensions", "anthropic-prompt-shim", "index.ts")
    if not os.path.exists(path):
        return Finding(
            FAIL, "prompt shim", "pi/extensions/anthropic-prompt-shim/index.ts missing"
        )
    with open(path, encoding="utf-8") as handle:
        source = handle.read()
    if PROMPT_TRIGGER not in source:
        return Finding(
            FAIL,
            "prompt shim",
            f"the shim no longer references {PROMPT_TRIGGER!r}; its trigger list "
            "has drifted from this check",
            "keep TRIGGER_LINES and PROMPT_TRIGGER in step",
        )
    return Finding(OK, "prompt shim", "present, trigger in step with this check")


def collect(repo):
    findings = []
    settings = read_json(SETTINGS)
    auth = read_json(AUTH)

    findings.append(check_pi_version())
    findings.append(check_shim_installed(settings))
    findings.append(check_credential(auth))
    findings.append(probe_installed_prompt())
    findings.append(check_shim_extension(repo))

    # Cross-check: a Claude pin is only sound when both halves are live.
    pinned = claude_pins(repo)
    if pinned:
        blocked = [f for f in findings if f.level == FAIL]
        if blocked:
            findings.append(
                Finding(
                    FAIL,
                    "claude pins",
                    f"{len(pinned)} Pi agent(s) pin Claude ({', '.join(pinned)}), "
                    f"but {len(blocked)} prerequisite(s) are unmet",
                    "those agents fail on their first request",
                )
            )
        else:
            findings.append(
                Finding(OK, "claude pins", f"{', '.join(pinned)} pin Claude")
            )
    return findings


def claude_pins(repo):
    """Pi agents whose frontmatter pins an anthropic/* model."""
    directory = os.path.join(repo, "pi", "agents")
    if not os.path.isdir(directory):
        return []
    pinned = []
    for name in sorted(os.listdir(directory)):
        if not name.endswith(".md"):
            continue
        with open(os.path.join(directory, name), encoding="utf-8") as handle:
            text = handle.read()
        if re.search(r"^model:\s*anthropic/", text, re.M):
            pinned.append(name[:-3])
    return pinned


def main(argv):
    repo = argv[1] if len(argv) > 1 else os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    )
    findings = collect(repo)
    width = max(len(f.subject) for f in findings)
    failures = 0
    for finding in findings:
        if finding.level == FAIL:
            failures += 1
        print(f"  {finding.level:<4} {finding.subject:<{width}}  {finding.detail}")
        if finding.hint:
            print(f"       {' ' * width}  -> {finding.hint}")
    print()
    if failures:
        print(f"{failures} blocking problem(s); the Pi -> Claude path is not armed.")
    else:
        print("Pi -> Claude path preconditions hold.")
        print("Note: this does not prove plan billing. Watch for")
        print("`anthropic-ratelimit-unified-overage-in-use` after real use.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
