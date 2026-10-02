#!/usr/bin/env python3
"""check-model-routing.py — catch silent model-routing drift in OMP and Pi config.

Every failure below has already happened in this repo at least once, and none
of them errors at runtime; they just quietly route work to the wrong model:

1. **Agent frontmatter vs override drift.** `omp/config.yml`'s
   `task.agentModelOverrides` beats `omp/agents/<name>.md` frontmatter, so a
   stale `model:` in frontmatter is invisible — until a session that omits that
   agent from its overrides lands it on whatever the frontmatter alias
   resolves to. `builder` sat on `"@default"` (Opus 5) for a whole re-base
   while its override said Sonnet 5.
2. **Dead override keys.** `librarian` stayed pinned long after the agent
   stopped existing. A key naming no agent is never reported.
3. **Selector pinned to a provider the same file disables.** That request
   fails at runtime, but only for whichever role happens to fire first.
4. **A Claude pin in Pi.** Pi reaches `anthropic/*` only while the
   `@gotgenes/pi-anthropic-auth` extension is installed *and* an OAuth
   credential exists; `openrouter/*` has a dead key. Those pins fail on first
   request otherwise, per
   `docs/research/harness-provider-access-2026-09.md`.

  ./scripts/check-model-routing.py [repo-root]

Stdlib only, like `lint-skills.py` (whose frontmatter parser it shares via
`frontmatter.py`): PyYAML is not a dependency of this repo and
must not become one for a check. The parser below handles exactly the flat
mappings, scalar lists and inline empty containers these config files use, and
reports anything it cannot parse rather than guessing.
"""

import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from frontmatter import parse_frontmatter  # noqa: E402

EFFORTS = ("minimal", "low", "medium", "high", "xhigh", "max")
SELECTOR_RE = re.compile(
    r"^(?P<provider>[a-z0-9][a-z0-9-]*)/(?P<model>[A-Za-z0-9][A-Za-z0-9._-]*)"
    r"(?::(?P<effort>" + "|".join(EFFORTS) + r"))?$"
)
ALIAS_RE = re.compile(r"^@([a-z][a-z0-9-]*)$")

# Agents OMP ships itself: they have no file in omp/agents/, so an override key
# naming one of these is legitimate.
BUNDLED_AGENTS = frozenset({"task", "scout", "sonic", "reviewer", "security-reviewer"})

# Providers Pi has no working credential path to. Keep in sync with
# docs/research/harness-provider-access-2026-09.md.
PI_UNREACHABLE = frozenset({"openrouter"})

# The extension that makes `anthropic/*` reachable from Pi, and the
# `packages[]` entry that must be present for that to be true.
PI_ANTHROPIC_SHIM = "@gotgenes/pi-anthropic-auth"


def _installed_pi_packages():
    """Return the `packages[]` entries Pi currently has installed.

    Read from the live settings file so the check reflects the machine, not a
    hardcoded expectation. A missing or unreadable file means "not installed",
    which keeps the conservative behaviour if Pi is not set up here.
    """
    path = os.path.expanduser(os.environ.get("PI_SETTINGS", "~/.pi/agent/settings.json"))
    try:
        with open(path, encoding="utf-8") as handle:
            data = json.load(handle) or {}
    except (OSError, ValueError):
        return frozenset()
    return frozenset(
        _package_name(entry) for entry in (data.get("packages") or [])
    )


def _package_name(entry):
    """Reduce a `packages[]` entry to its bare package name.

    `npm:@scope/name@1.2.3` -> `@scope/name`, `npm:name` -> `name`. The version
    separator is the LAST `@`, never the first: a scoped name carries its own.
    """
    if not entry.startswith("npm:"):
        return entry
    name = entry[4:]
    if name.startswith("@"):
        head, _, tail = name.rpartition("@")
        return head if head and tail else name
    return name.split("@", 1)[0]


# `anthropic/*` is reachable from Pi only with the shim installed. Route it
# deliberately (an explicit pin), never as a default or fallback: Anthropic
# bills the subscription against an extra-usage balance without the shim, and
# the shim impersonates Claude Code, which Anthropic's legal page prohibits and
# actively detects. See docs/research/pi-claude-subscription-2026-10.md.
PI_CLAUDE_ALLOWED = PI_ANTHROPIC_SHIM in _installed_pi_packages()


def parse_config(text, path):
    """Parse the indentation-only YAML subset these config files use."""
    root = {}
    stack = [(-1, root)]
    failures = []
    for lineno, raw in enumerate(text.splitlines(), 1):
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        line = raw.strip()
        while stack and indent <= stack[-1][0]:
            stack.pop()
        if not stack:
            failures.append(f"{path}:{lineno}: cannot parse indentation")
            return root, failures
        parent = stack[-1][1]
        if line.startswith("- "):
            if not isinstance(parent, (list, _Pending)):
                failures.append(f"{path}:{lineno}: list item outside a list")
                return root, failures
            parent.append(_scalar(line[2:].strip()))
            continue
        if line in ("[]", "{}"):
            continue
        key, sep, value = line.partition(":")
        if not sep:
            failures.append(f"{path}:{lineno}: not a mapping entry: {line}")
            return root, failures
        key = key.strip()
        value = value.strip()
        if isinstance(parent, list):
            failures.append(f"{path}:{lineno}: mapping entry inside a list")
            return root, failures
        if value in ("", "[]", "{}"):
            # `[]`/`{}` inline, or a nested block opening on the next line.
            # A list is only distinguishable once its first `- ` item arrives,
            # so start with a dict and promote on demand.
            child = [] if value == "[]" else {}
            parent[key] = child
            stack.append((indent, _Pending(parent, key) if value == "" else child))
        else:
            parent[key] = _scalar(value)
    return root, failures


class _Pending(dict):
    """A block whose kind (mapping or list) is not known until its first item."""

    def __init__(self, parent, key):
        super().__init__()
        self._parent = parent
        self._key = key

    def append(self, item):  # first `- ` item: promote this block to a list
        promoted = self._parent[self._key]
        if not isinstance(promoted, list):
            promoted = []
            self._parent[self._key] = promoted
        promoted.append(item)

    def __setitem__(self, key, value):
        self._parent[self._key][key] = value

    def __getitem__(self, key):
        return self._parent[self._key][key]


def _scalar(value):
    value = value.split("  #")[0].strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1]
    return value


def frontmatter(text, label, failures):
    """Return the top-level scalar frontmatter keys of a Markdown agent file.

    Parsing is shared with lint-skills.py, so block scalars and multi-line
    quoted values resolve; an unparseable header is appended to `failures`.
    """
    parsed, _, error = parse_frontmatter(text)
    if error:
        failures.append(f"{label}: {error}")
        return {}
    fields = {}
    for key, field in parsed.items():
        if field.value is None:  # nested mapping: not a scalar we route on
            continue
        fields[key] = _scalar(field.value) if field.style == "plain" else field.value
    return fields


def selectors(node, trail=""):
    """Yield (trail, value) for every scalar reachable under `trail`.

    No `/` filter: a value like `claude-opus-5:medium` — provider omitted —
    is exactly the malformed selector this check exists to catch, and the
    caller decides which trails are routing values.
    """
    if isinstance(node, dict):
        for key, value in node.items():
            yield from selectors(value, f"{trail}.{key}" if trail else key)
    elif isinstance(node, list):
        for index, value in enumerate(node):
            yield from selectors(value, f"{trail}[{index}]")
    elif isinstance(node, str):
        yield trail, node


def check(config, agents, pi_agents, pi_settings=None, pi_search=None):
    """Return routing failures for already-read inputs; performs no I/O.

    config: parsed omp/config.yml mapping.
    agents / pi_agents: {filename: text} for omp/agents/*.md and pi/agents/*.md.
    pi_settings / pi_search: parsed pi/settings.json / pi/web-search.json, or None.
    """
    failures = []
    roles = config.get("modelRoles") or {}
    overrides = (config.get("task") or {}).get("agentModelOverrides") or {}
    if not roles or not overrides:
        failures.append("omp/config.yml: modelRoles or task.agentModelOverrides missing")
        return failures

    # 1. Selector shape, plus provider-vs-disabledProviders.
    disabled = set(config.get("disabledProviders") or [])
    for trail, value in selectors(config):
        if not trail.startswith(("modelRoles", "task.agentModelOverrides", "retry.fallbackChains", "enabledModels")):
            continue
        match = SELECTOR_RE.match(value)
        if not match:
            failures.append(f"omp/config.yml: {trail} = {value!r} is not provider/model[:effort]")
            continue
        provider = match.group("provider")
        if provider in disabled:
            failures.append(
                f"omp/config.yml: {trail} pins {provider!r}, which the same file lists in disabledProviders"
            )

    # 2. Override keys must name a real agent.
    agent_files = {}
    for name, text in sorted(agents.items()):
        fields = frontmatter(text, f"omp/agents/{name}", failures)
        agent_files[fields.get("name") or name[: -len(".md")]] = (name, fields)
    known_agents = set(agent_files) | BUNDLED_AGENTS
    for agent in overrides:
        if agent not in known_agents:
            failures.append(
                f"omp/config.yml: task.agentModelOverrides.{agent} names no agent "
                f"(no omp/agents/{agent}.md and not bundled)"
            )

    # 3. Repo-owned agent frontmatter must resolve to its override.
    for agent, (filename, fields) in sorted(agent_files.items()):
        declared = fields.get("model")
        override = overrides.get(agent)
        if declared is None:
            failures.append(f"omp/agents/{filename}: no `model:` key")
            continue
        alias = ALIAS_RE.match(declared)
        if alias:
            role = alias.group(1)
            if role not in roles:
                failures.append(
                    f"omp/agents/{filename}: model alias @{role} is not a role in omp/config.yml"
                )
                continue
            resolved = roles[role]
        else:
            resolved = declared
        if override is not None and resolved != override:
            failures.append(
                f"omp/agents/{filename}: model {declared!r} resolves to {resolved!r} but "
                f"task.agentModelOverrides.{agent} is {override!r} — a session that omits "
                f"{agent} from its overrides would route it to the wrong model"
            )

    # 4. Pi may not pin a provider it cannot reach.
    #
    # `anthropic/*` is the one conditional case. With the shim installed an
    # explicit agent pin is a deliberate routing decision and is allowed; as a
    # default or in the Ctrl+P cycle it is not, because the shim impersonates
    # Claude Code and should never be the face of the harness. Without the shim
    # the provider is unreachable and every use is a failure.
    for name, text in sorted(pi_agents.items()):
        fields = frontmatter(text, f"pi/agents/{name}", failures)
        declared = fields.get("model")
        if not declared:
            failures.append(f"pi/agents/{name}: no `model:` key")
            continue
        match = SELECTOR_RE.match(declared)
        if not match:
            failures.append(f"pi/agents/{name}: model {declared!r} is not provider/model[:effort]")
            continue
        provider = match.group("provider")
        if provider in PI_UNREACHABLE:
            failures.append(
                f"pi/agents/{name}: model {declared!r} uses {provider!r}, "
                "which Pi has no working credential path to"
            )
        elif provider == "anthropic" and not PI_CLAUDE_ALLOWED:
            failures.append(
                f"pi/agents/{name}: model {declared!r} pins Claude, but "
                f"{PI_ANTHROPIC_SHIM!r} is not installed in Pi, so the "
                "subscription bills third-party usage and the request fails"
            )

    if pi_settings is not None:
        # Default and cycle entries always stay off Claude, shim or not.
        always_unreachable = PI_UNREACHABLE | {"anthropic"}
        provider = pi_settings.get("defaultProvider")
        if provider in always_unreachable:
            failures.append(
                f"pi/settings.json: defaultProvider {provider!r} is unreachable from Pi"
            )
        for entry in pi_settings.get("enabledModels") or []:
            if entry.split("/", 1)[0] in always_unreachable:
                failures.append(
                    f"pi/settings.json: enabledModels entry {entry!r} is unreachable from Pi"
                )

    if pi_search is not None:
        summary = pi_search.get("summaryModel") or ""
        if summary.split("/", 1)[0] in PI_UNREACHABLE | {"anthropic"}:
            failures.append(
                f"pi/web-search.json: summaryModel {summary!r} is unreachable from Pi"
            )

    return failures


def _read_dir(path, suffix):
    if not os.path.isdir(path):
        return {}
    texts = {}
    for name in sorted(os.listdir(path)):
        if name.endswith(suffix):
            with open(os.path.join(path, name), encoding="utf-8") as handle:
                texts[name] = handle.read()
    return texts


def _read_json(path):
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as handle:
        return json.load(handle) or {}


def check_repo(repo):
    """Read the repo's routing files and run `check` over them."""
    with open(os.path.join(repo, "omp", "config.yml"), encoding="utf-8") as handle:
        config, failures = parse_config(handle.read(), "omp/config.yml")
    return failures + check(
        config,
        _read_dir(os.path.join(repo, "omp", "agents"), ".md"),
        _read_dir(os.path.join(repo, "pi", "agents"), ".md"),
        _read_json(os.path.join(repo, "pi", "settings.json")),
        _read_json(os.path.join(repo, "pi", "web-search.json")),
    )


def main(argv):
    repo = argv[1] if len(argv) > 1 else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    failures = check_repo(repo)
    for failure in failures:
        print(f"FAIL {failure}")
    if failures:
        print(f"\n{len(failures)} routing problem(s)")
        return 1
    print("model routing consistent")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
