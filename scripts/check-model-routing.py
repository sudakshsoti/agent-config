#!/usr/bin/env python3
"""check-model-routing.py — catch silent model-routing drift in OMP and Pi config.

Every failure below has already happened in this repo at least once, and none
of them errors at runtime; they just quietly route work to the wrong model:

1. **Agent frontmatter vs override drift.** `omp/config.yml`'s
   `task.agentModelOverrides` beats `omp/agents/<name>.md` frontmatter, so a
   stale `model:` in frontmatter is invisible — until a session runs with an
   overlay that omits that agent, and the agent silently lands on whatever the
   frontmatter alias resolves to. `builder` sat on `"@default"` (Opus 5) for a
   whole re-base while its override said Sonnet 5.
2. **Dead override keys.** `librarian` was pinned in both overlays long after
   the agent stopped existing. A key naming no agent is never reported.
3. **Overlay coverage holes.** An overlay replaces the base value only for the
   keys it lists, so a missing role or agent key lets the base provider leak
   into a session whose whole point was to stay on one provider.
4. **Selector pinned to a provider the same file disables.** That request
   fails at runtime, but only for whichever role happens to fire first.
5. **A Claude pin in Pi.** Pi cannot reach `anthropic/*` (the subscription
   bills third-party clients against an extra-usage balance) or `openrouter/*`
   (dead key). Those pins fail on first request, per
   `docs/research/harness-provider-access-2026-09.md`.

  ./scripts/check-model-routing.py [repo-root]

Stdlib only, like `lint-skills.py`: PyYAML is not a dependency of this repo and
must not become one for a check. The parser below handles exactly the flat
mappings, scalar lists and inline empty containers these config files use, and
reports anything it cannot parse rather than guessing.
"""

import json
import os
import re
import sys

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
PI_UNREACHABLE = frozenset({"anthropic", "openrouter"})


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


def frontmatter(text):
    """Return the top-level frontmatter keys of a Markdown agent file."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    fields = {}
    for line in lines[1:]:
        if line.strip() == "---":
            break
        key, sep, value = line.partition(":")
        if sep and not line[:1].isspace():
            fields[key.strip()] = _scalar(value.strip())
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


def check(repo):
    failures = []
    config_path = os.path.join(repo, "omp", "config.yml")
    with open(config_path, encoding="utf-8") as handle:
        config, parse_failures = parse_config(handle.read(), "omp/config.yml")
    failures.extend(parse_failures)

    roles = config.get("modelRoles") or {}
    overrides = (config.get("task") or {}).get("agentModelOverrides") or {}
    if not roles or not overrides:
        failures.append("omp/config.yml: modelRoles or task.agentModelOverrides missing")
        return failures

    # 1. Selector shape, everywhere, plus provider-vs-disabledProviders.
    routing_files = [("omp/config.yml", config)]
    overlay_dir = os.path.join(repo, "omp", "overlays")
    overlays = {}
    for name in sorted(os.listdir(overlay_dir)):
        if not name.endswith((".yml", ".yaml")):
            continue
        with open(os.path.join(overlay_dir, name), encoding="utf-8") as handle:
            overlay, overlay_failures = parse_config(handle.read(), f"omp/overlays/{name}")
        failures.extend(overlay_failures)
        overlays[name] = overlay
        routing_files.append((f"omp/overlays/{name}", overlay))

    for path, tree in routing_files:
        disabled = set(tree.get("disabledProviders") or [])
        for trail, value in selectors(tree):
            if not trail.startswith(("modelRoles", "task.agentModelOverrides", "retry.fallbackChains", "enabledModels")):
                continue
            match = SELECTOR_RE.match(value)
            if not match:
                failures.append(f"{path}: {trail} = {value!r} is not provider/model[:effort]")
                continue
            provider = match.group("provider")
            if provider in disabled:
                failures.append(
                    f"{path}: {trail} pins {provider!r}, which the same file lists in disabledProviders"
                )

    # 2. Override keys must name a real agent.
    agent_dir = os.path.join(repo, "omp", "agents")
    agent_files = {}
    for name in sorted(os.listdir(agent_dir)):
        if not name.endswith(".md"):
            continue
        with open(os.path.join(agent_dir, name), encoding="utf-8") as handle:
            fields = frontmatter(handle.read())
        agent_files[fields.get("name") or name[: -len(".md")]] = (name, fields)
    known_agents = set(agent_files) | BUNDLED_AGENTS
    for path, tree in routing_files:
        keys = (tree.get("task") or {}).get("agentModelOverrides") or {}
        for agent in keys:
            if agent not in known_agents:
                failures.append(
                    f"{path}: task.agentModelOverrides.{agent} names no agent "
                    f"(no omp/agents/{agent}.md and not bundled)"
                )

    # 3. Repo-owned agent frontmatter must resolve to its base override.
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
                f"task.agentModelOverrides.{agent} is {override!r} — an overlay that omits "
                f"{agent} would route it to the wrong model"
            )

    # 4. Overlay coverage: every base role and agent key must be re-pinned.
    for name, overlay in overlays.items():
        overlay_roles = overlay.get("modelRoles") or {}
        overlay_agents = (overlay.get("task") or {}).get("agentModelOverrides") or {}
        for role in sorted(roles):
            if role not in overlay_roles:
                failures.append(
                    f"omp/overlays/{name}: modelRoles.{role} not overridden — the base "
                    f"value {roles[role]!r} leaks into this session"
                )
        for agent in sorted(overrides):
            if agent not in overlay_agents:
                failures.append(
                    f"omp/overlays/{name}: task.agentModelOverrides.{agent} not overridden — "
                    f"the base value {overrides[agent]!r} leaks into this session"
                )

    # 5. Pi may not pin a provider it cannot reach.
    pi_agent_dir = os.path.join(repo, "pi", "agents")
    if os.path.isdir(pi_agent_dir):
        for name in sorted(os.listdir(pi_agent_dir)):
            if not name.endswith(".md"):
                continue
            with open(os.path.join(pi_agent_dir, name), encoding="utf-8") as handle:
                fields = frontmatter(handle.read())
            declared = fields.get("model")
            if not declared:
                failures.append(f"pi/agents/{name}: no `model:` key")
                continue
            match = SELECTOR_RE.match(declared)
            if not match:
                failures.append(f"pi/agents/{name}: model {declared!r} is not provider/model[:effort]")
                continue
            if match.group("provider") in PI_UNREACHABLE:
                failures.append(
                    f"pi/agents/{name}: model {declared!r} uses {match.group('provider')!r}, "
                    "which Pi has no working credential path to"
                )

    settings_path = os.path.join(repo, "pi", "settings.json")
    if os.path.exists(settings_path):
        with open(settings_path, encoding="utf-8") as handle:
            settings = json.load(handle)
        provider = settings.get("defaultProvider")
        if provider in PI_UNREACHABLE:
            failures.append(
                f"pi/settings.json: defaultProvider {provider!r} is unreachable from Pi"
            )
        for entry in settings.get("enabledModels") or []:
            if entry.split("/", 1)[0] in PI_UNREACHABLE:
                failures.append(
                    f"pi/settings.json: enabledModels entry {entry!r} is unreachable from Pi"
                )

    search_path = os.path.join(repo, "pi", "web-search.json")
    if os.path.exists(search_path):
        with open(search_path, encoding="utf-8") as handle:
            summary = (json.load(handle) or {}).get("summaryModel") or ""
        if summary.split("/", 1)[0] in PI_UNREACHABLE:
            failures.append(
                f"pi/web-search.json: summaryModel {summary!r} is unreachable from Pi"
            )

    return failures


def main(argv):
    repo = argv[1] if len(argv) > 1 else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    failures = check(repo)
    for failure in failures:
        print(f"FAIL {failure}")
    if failures:
        print(f"\n{len(failures)} routing problem(s)")
        return 1
    print("model routing consistent")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
