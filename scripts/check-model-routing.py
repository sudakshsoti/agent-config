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
   `@gotgenes/pi-anthropic-auth` extension is declared in the tracked
   `pi/settings.json` `packages[]` (install links it into `~/.pi`) *and* an
   OAuth credential exists; `openrouter/*` has a dead key. Those pins fail on
   first request otherwise, per
   `docs/research/harness-provider-access-2026-09.md`. `role/<name>`
   selectors (the `pi/extensions/model-roles` virtual models) are resolved
   through `pi/model-roles.json` first, so a role cannot hide either case.

5. **Docs vs config drift.** `AGENTS.md`'s OMP routing table and
   `pi/model-ladder.md`'s ladder table state the routing in prose; between
   `<!-- routing:current -->` and `<!-- routing:end -->` single-line claims
   are checked too. The `default` role sat as Opus in the docs and Sonnet in
   the config for five days. Docs are corrected to the config, never the
   reverse.

6. **A non-Claude model on a Claude Code agent.** `claude/agents/*.md` runs
   inside Claude Code, which serves only Claude; any other `model:` fails on
   first launch, and an omitted one silently inherits the parent's Opus.

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
    r"^(?P<provider>[a-z0-9][a-z0-9-]*)/(?P<model>[A-Za-z0-9][A-Za-z0-9._/-]*)"
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

# Doc surfaces whose routing claims are compared with the config.
OMP_DOC = "AGENTS.md"
PI_DOC = "pi/model-ladder.md"
OMP_TABLE_HEADER = ["Roles/settings", "Value"]
PI_TABLE_HEADER = ["Task / agent", "Provider and model", "Effort"]
MARK_START = "<!-- routing:current -->"
MARK_END = "<!-- routing:end -->"

# Settings rows of the OMP table: documented key -> dotted path in omp/config.yml.
OMP_SETTINGS = (
    "disabledProviders",
    "retry.usageAwareFallback",
    "retry.usageReservePct",
    "retry.usageReservePolicy",
    "task.maxEffort",
    "providers.autoThinkingMaxEffort",
)

_TICKED = re.compile(r"`([^`]+)`")
_GROUP_RE = re.compile(r"^(`[^`]+`(?:/`[^`]+`)*) (roles?|agents?)$")
_TICKED_LIST_RE = re.compile(r"^`[^`]+`(?: / `[^`]+`)*$")
_MARKED_LINE_RE = re.compile(
    r"^(?P<names>`[^`]+`(?:(?: and |, )`[^`]+`)*) \u2192 `(?P<model>[^`]+)` (?P<level>\S+)$"
)


def _declared_pi_packages(pi_settings):
    """Return the bare names in the tracked `pi/settings.json` `packages[]`.

    The repo's declared set, not the machine's: install links that file into
    `~/.pi/agent/`, so it is what a box gets, and unlike `~/.pi` it is the same
    on every box. A missing settings file means no package is declared.
    """
    return frozenset(
        _package_name(entry) for entry in ((pi_settings or {}).get("packages") or [])
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


# --- Docs vs config -------------------------------------------------------


def _dig(node, dotted):
    for part in dotted.split("."):
        if not isinstance(node, dict) or part not in node:
            return None
        node = node[part]
    return node


def _render(value):
    if isinstance(value, list):
        return "[" + ", ".join(str(v) for v in value) + "]"
    return None if value is None else str(value)


def _split_row(line):
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


_SEPARATOR_CELL = re.compile(r"^:?-+:?$")
_MARKER_LIKE = re.compile(r"<!--\s*routing:")


def _table_rows(label, text, header, failures):
    """Return [(lineno, cells)] from every table whose header row is `header`.

    A header with no separator row, a malformed separator, or no rows below
    it is reported, never skipped. Returns None when no table matches.
    """
    lines = text.splitlines()
    rows, found = [], False
    for index, line in enumerate(lines):
        if not (line.lstrip().startswith("|") and _split_row(line) == header):
            continue
        found = True
        separator = _split_row(lines[index + 1]) if index + 1 < len(lines) else []
        if len(separator) != len(header) or not all(_SEPARATOR_CELL.match(c) for c in separator):
            failures.append(f"{label}:{index + 2}: expected a table separator row under the header at line {index + 1}")
            continue
        body = 0
        for offset in range(index + 2, len(lines)):
            if not lines[offset].lstrip().startswith("|"):
                break
            rows.append((offset + 1, _split_row(lines[offset])))
            body += 1
        if not body:
            failures.append(f"{label}:{index + 1}: table has no rows to check")
    return rows if found else None


def _pi_agent_selector(name, pi_agents):
    """Return (`provider/model:level`, error) for a Pi agent's frontmatter."""
    text = pi_agents.get(f"{name}.md")
    if text is None:
        return None, f"no pi/agents/{name}.md"
    fields = frontmatter(text, f"pi/agents/{name}.md", [])
    model = fields.get("model")
    if not model:
        return None, f"pi/agents/{name}.md has no `model:`"
    if SELECTOR_RE.match(model) and SELECTOR_RE.match(model).group("effort"):
        return model, None
    thinking = fields.get("thinking")
    return (f"{model}:{thinking}" if thinking else model), None


def _pi_default_raw(pi_settings):
    if not pi_settings:
        return None
    provider, model = pi_settings.get("defaultProvider"), pi_settings.get("defaultModel")
    level = pi_settings.get("defaultThinkingLevel")
    if not provider or not model:
        return None
    return f"{provider}/{model}" + (f":{level}" if level else "")


def _resolve_pi(selector, pi_roles):
    """Return (physical `provider/model[:level]`, error) for a Pi selector.

    `role/<name>[:level]` resolves through `pi/model-roles.json` `roles`; the
    selector's own level beats the role's, as in pi/extensions/model-roles.
    Any other selector is already physical and is returned unchanged.
    """
    match = SELECTOR_RE.match(selector or "")
    if not match:
        return None, "is not provider/model[:effort]"
    if match.group("provider") != "role":
        return selector, None
    target = ((pi_roles or {}).get("roles") or {}).get(match.group("model"))
    if target is None:
        return None, "names no role in pi/model-roles.json"
    resolved = SELECTOR_RE.match(target)
    if not resolved or resolved.group("provider") == "role":
        return None, f"resolves to {target!r}, not a physical provider/model[:effort]"
    level = match.group("effort") or resolved.group("effort")
    return f"{resolved.group('provider')}/{resolved.group('model')}" + (f":{level}" if level else ""), None


def _pi_default_selector(pi_settings, pi_roles):
    raw = _pi_default_raw(pi_settings)
    physical, _ = _resolve_pi(raw, pi_roles)
    return physical or raw


def _mismatch(where, subject, doc_value, source, config_value):
    return (
        f"{where}: {subject} is {doc_value!r} in the docs but {source} is {config_value!r}"
    )


def _omp_sources(config):
    return config.get("modelRoles") or {}, (config.get("task") or {}).get("agentModelOverrides") or {}


def _compare(failures, where, subject, doc_value, source, actual):
    if actual != doc_value:
        failures.append(_mismatch(where, subject, doc_value, source, actual))


def _check_omp_table(text, config, failures):
    roles, overrides = _omp_sources(config)
    rows = _table_rows(OMP_DOC, text, OMP_TABLE_HEADER, failures)
    if rows is None:
        failures.append(f"{OMP_DOC}: routing table with header {'| '.join(OMP_TABLE_HEADER)!r} not found")
        return
    for lineno, cells in rows:
        where = f"{OMP_DOC}:{lineno}"
        if len(cells) != 2:
            failures.append(f"{where}: routing row must have 2 cells, got {len(cells)}")
            continue
        first, value = cells
        parts = [part.strip() for part in first.split(";")]
        groups = [_GROUP_RE.match(part) for part in parts]
        if all(groups):
            selector = _TICKED.fullmatch(value)
            if not selector or not SELECTOR_RE.match(selector.group(1)):
                failures.append(
                    f"{where}: value {value!r} is not one backticked provider/model:level selector"
                )
                continue
            for group in groups:
                kind = "role" if group.group(2).startswith("role") else "agent"
                source = roles if kind == "role" else overrides
                prefix = "modelRoles" if kind == "role" else "task.agentModelOverrides"
                for name in _TICKED.findall(group.group(1)):
                    actual = source.get(name)
                    if actual is None:
                        failures.append(f"{where}: {kind} `{name}` is not in {prefix} of omp/config.yml")
                    else:
                        _compare(failures, where, f"{kind} `{name}`", selector.group(1), f"{prefix}.{name}", actual)
        elif _TICKED_LIST_RE.match(first) and _TICKED_LIST_RE.match(value):
            keys = _TICKED.findall(first)
            values = _TICKED.findall(value)
            if len(keys) != len(values):
                failures.append(f"{where}: {len(keys)} setting(s) but {len(values)} value(s)")
                continue
            for key, doc_value in zip(keys, values):
                if key not in OMP_SETTINGS:
                    failures.append(f"{where}: `{key}` is not a checked setting ({', '.join(OMP_SETTINGS)})")
                    continue
                _compare(failures, where, f"setting `{key}`", doc_value, key, _render(_dig(config, key)))
        else:
            failures.append(
                f"{where}: cannot parse routing row {first!r} | {value!r} (expected "
                "`name`/`name` role|agent groups separated by ';', or backticked setting keys)"
            )


def _check_pi_table(text, pi_agents, pi_settings, pi_roles, failures):
    rows = _table_rows(PI_DOC, text, PI_TABLE_HEADER, failures)
    if rows is None:
        failures.append(f"{PI_DOC}: ladder table with header {'| '.join(PI_TABLE_HEADER)!r} not found")
        return
    for lineno, cells in rows:
        where = f"{PI_DOC}:{lineno}"
        if len(cells) != 3:
            failures.append(f"{where}: ladder row must have 3 cells, got {len(cells)}")
            continue
        first, model_cell, effort_cell = cells
        model = _TICKED.fullmatch(model_cell)
        effort = effort_cell.strip("`")
        shape = SELECTOR_RE.match(model.group(1)) if model else None
        if not shape or shape.group("effort") or effort not in EFFORTS:
            failures.append(
                f"{where}: cannot parse {model_cell!r} | {effort_cell!r} "
                "(expected a backticked provider/model and an effort level)"
            )
            continue
        doc = f"{model.group(1)}:{effort}"
        if first.startswith("Main session"):
            _compare(failures, where, "Main session", doc, "pi/settings.json default", _pi_default_selector(pi_settings, pi_roles))
        elif first.startswith("Manual fallback"):
            cycle = [_resolve_pi(entry, pi_roles)[0] or entry for entry in (pi_settings or {}).get("enabledModels") or []]
            if doc not in cycle:
                failures.append(
                    f"{where}: Manual fallback is {doc!r} in the docs but pi/settings.json "
                    f"enabledModels resolves to {cycle!r}"
                )
        else:
            names = _TICKED.findall(first)
            if not names:
                failures.append(f"{where}: cannot parse row {first!r}: no backticked agent name")
            for name in names:
                actual, error = _pi_agent_selector(name, pi_agents)
                if error:
                    failures.append(f"{where}: agent `{name}`: {error}")
                else:
                    _compare(failures, where, f"agent `{name}`", doc, f"pi/agents/{name}.md", actual)


def _marked_lines(label, text, failures):
    """Yield (lineno, line) for non-blank lines between routing markers."""
    inside = False
    start = content = 0
    for lineno, raw in enumerate(text.splitlines(), 1):
        stripped = raw.strip()
        if _MARKER_LIKE.search(re.sub(r"`[^`]*`", "", raw)) and stripped not in (MARK_START, MARK_END):
            failures.append(
                f"{label}:{lineno}: malformed routing marker {stripped!r}; a marker must be "
                f"exactly {MARK_START} or {MARK_END} alone on its line"
            )
        elif stripped == MARK_START:
            if inside:
                failures.append(f"{label}:{lineno}: {MARK_START} inside an open marked block (opened line {start})")
            inside, start, content = True, lineno, 0
        elif stripped == MARK_END:
            if not inside:
                failures.append(f"{label}:{lineno}: {MARK_END} without {MARK_START}")
            if inside and not content:
                failures.append(f"{label}:{start}: marked block has no lines to check")
            inside, content = False, 0
        elif inside and stripped:
            content += 1
            yield lineno, stripped
    if inside:
        failures.append(f"{label}:{start}: {MARK_START} never closed by {MARK_END}")


def _check_marked(label, text, native, config, pi_agents, pi_settings, pi_roles, failures):
    """Check `name` -> `provider/model` level sentences between the markers.

    A name resolves in the doc's native source (AGENTS.md: OMP roles and agents;
    pi/model-ladder.md: Pi agents and `main`). Prefix it `omp:` or `pi:` to
    reach the other source.
    """
    roles, overrides = _omp_sources(config)
    for lineno, line in _marked_lines(label, text, failures):
        where = f"{label}:{lineno}"
        match = _MARKED_LINE_RE.match(line)
        if not match:
            failures.append(
                f"{where}: cannot parse marked line {line!r} (expected "
                "`name` \u2192 `provider/model` level; several names joined by ' and ' or ', ')"
            )
            continue
        doc = f"{match.group('model')}:{match.group('level')}"
        if not SELECTOR_RE.match(doc) or not SELECTOR_RE.match(doc).group("effort"):
            failures.append(f"{where}: {doc!r} is not provider/model with a valid level")
            continue
        for name in _TICKED.findall(match.group("names")):
            scope, _, bare = name.rpartition(":")
            scope = scope or native
            if scope not in ("omp", "pi"):
                failures.append(f"{where}: unknown scope {scope!r} in `{name}` (use omp: or pi:)")
                continue
            if scope == "omp":
                found = {
                    f"modelRoles.{bare}": roles.get(bare),
                    f"task.agentModelOverrides.{bare}": overrides.get(bare),
                }
                found = {k: v for k, v in found.items() if v is not None}
                if not found:
                    failures.append(f"{where}: `{name}` is neither a modelRoles nor an agentModelOverrides entry")
                for source, actual in found.items():
                    _compare(failures, where, f"`{name}`", doc, source, actual)
            elif bare == "main":
                _compare(failures, where, f"`{name}`", doc, "pi/settings.json default", _pi_default_selector(pi_settings, pi_roles))
            else:
                actual, error = _pi_agent_selector(bare, pi_agents)
                if error:
                    failures.append(f"{where}: `{name}`: {error}")
                else:
                    _compare(failures, where, f"`{name}`", doc, f"pi/agents/{bare}.md", actual)


def check_docs(docs, config, pi_agents, pi_settings, pi_roles=None):
    """Compare routing claims in AGENTS.md and pi/model-ladder.md with the config."""
    failures = []
    for label, native in ((OMP_DOC, "omp"), (PI_DOC, "pi")):
        text = docs.get(label)
        if text is None:
            failures.append(f"{label}: missing, cannot compare its routing claims with the config")
            continue
        if label == OMP_DOC:
            _check_omp_table(text, config, failures)
        else:
            _check_pi_table(text, pi_agents, pi_settings, pi_roles, failures)
        if not any(line.strip() == MARK_START for line in text.splitlines()):
            failures.append(f"{label}: no routing:current block ({MARK_START} ... {MARK_END}); mark the current-state routing lines")
        _check_marked(label, text, native, config, pi_agents, pi_settings, pi_roles, failures)
    return failures


def check(config, agents, pi_agents, pi_settings=None, pi_search=None, docs=None, pi_roles=None):
    """Return routing failures for already-read inputs; performs no I/O.

    config: parsed omp/config.yml mapping.
    agents / pi_agents: {filename: text} for omp/agents/*.md and pi/agents/*.md.
    pi_settings / pi_search / pi_roles: parsed pi/settings.json /
        pi/web-search.json / pi/model-roles.json, or None.
    docs: {repo-relative path: text} of AGENTS.md and pi/model-ladder.md, or None
        to skip the docs-vs-config comparison.
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

    # 4. Pi may not route to a provider it cannot reach.
    #
    # `anthropic/*` is reachable only through the shim declared in
    # pi/settings.json. With it, Claude is allowed wherever Pi selects a model,
    # default and Ctrl+P cycle included (user decision 2026-10-09,
    # design/decisions.md "Pi Claude default"); without it every use is a
    # failure. See docs/research/pi-claude-subscription-2026-10.md.
    claude_allowed = PI_ANTHROPIC_SHIM in _declared_pi_packages(pi_settings)

    def reach(where, selector):
        physical, error = _resolve_pi(selector, pi_roles)
        if error:
            failures.append(f"{where} {selector!r} {error}")
            return
        provider = physical.split("/", 1)[0]
        if provider in PI_UNREACHABLE:
            failures.append(
                f"{where} {selector!r} routes to {provider!r}, which Pi has no working credential path to"
            )
        elif provider == "anthropic" and not claude_allowed:
            failures.append(
                f"{where} {selector!r} pins Claude, but {PI_ANTHROPIC_SHIM!r} is not in "
                "pi/settings.json packages[], so the subscription bills third-party usage "
                "and the request fails"
            )

    for name, text in sorted(pi_agents.items()):
        fields = frontmatter(text, f"pi/agents/{name}", failures)
        declared = fields.get("model")
        if not declared:
            failures.append(f"pi/agents/{name}: no `model:` key")
            continue
        reach(f"pi/agents/{name}: model", declared)

    if pi_settings is not None:
        default = _pi_default_raw(pi_settings)
        if default:
            reach("pi/settings.json: defaultProvider/defaultModel", default)
        for entry in pi_settings.get("enabledModels") or []:
            reach("pi/settings.json: enabledModels entry", entry)

    if pi_search is not None and pi_search.get("summaryModel"):
        reach("pi/web-search.json: summaryModel", pi_search["summaryModel"])

    if pi_roles is not None:
        # Role targets are what a role selection lands on, so they are held to
        # the same reachability rule. Chain rungs are not: the router skips a
        # rung without credentials, so an unreachable rung is inert.
        for name, target in sorted((pi_roles.get("roles") or {}).items()):
            match = SELECTOR_RE.match(target)
            if not match or match.group("provider") == "role":
                failures.append(
                    f"pi/model-roles.json: roles.{name} = {target!r} is not a physical provider/model[:effort]"
                )
                continue
            reach(f"pi/model-roles.json: roles.{name}", target)
        for key, rungs in sorted((pi_roles.get("chains") or {}).items()):
            match = SELECTOR_RE.match(key)
            if not match or match.group("effort") or match.group("provider") == "role":
                failures.append(
                    f"pi/model-roles.json: chains key {key!r} is not a physical provider/model "
                    "(chains are keyed by exact model, without effort)"
                )
            for rung in rungs or []:
                match = SELECTOR_RE.match(rung)
                if not match or match.group("provider") == "role":
                    failures.append(
                        f"pi/model-roles.json: chains.{key} rung {rung!r} is not a physical provider/model[:effort]"
                    )

    if docs is not None:
        failures.extend(check_docs(docs, config, pi_agents, pi_settings, pi_roles))

    return failures


CLAUDE_ALIASES = {"haiku", "sonnet", "opus", "fable", "inherit"}


def check_claude_agents(agents):
    """Failures for claude/agents/*.md: each needs a Claude alias or claude-* id."""
    failures = []
    for name, text in sorted(agents.items()):
        fields = frontmatter(text, f"claude/agents/{name}", failures)
        declared = fields.get("model")
        if not declared:
            failures.append(
                f"claude/agents/{name}: no `model:` key, so it inherits the parent's model"
            )
        elif declared not in CLAUDE_ALIASES and not declared.startswith("claude-"):
            failures.append(
                f"claude/agents/{name}: model {declared!r} is not a Claude alias "
                f"({', '.join(sorted(CLAUDE_ALIASES))}) or claude-* id"
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
    docs = {}
    for relative in (OMP_DOC, PI_DOC):
        path = os.path.join(repo, relative)
        if os.path.exists(path):
            with open(path, encoding="utf-8") as handle:
                docs[relative] = handle.read()
    return failures + check(
        config,
        _read_dir(os.path.join(repo, "omp", "agents"), ".md"),
        _read_dir(os.path.join(repo, "pi", "agents"), ".md"),
        _read_json(os.path.join(repo, "pi", "settings.json")),
        _read_json(os.path.join(repo, "pi", "web-search.json")),
        docs,
        _read_json(os.path.join(repo, "pi", "model-roles.json")),
    ) + check_claude_agents(_read_dir(os.path.join(repo, "claude", "agents"), ".md"))


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
