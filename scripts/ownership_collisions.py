#!/usr/bin/env python3
"""Chezmoi collision detection for agent-config's install destinations.

Adapts the "Non-destructive detection rule" from
`git show sprawl/phase-0-2:docs/ownership.md` (section "chezmoi collision
inventory" / "Non-destructive detection rule") to the destinations
`install.sh` actually writes today. That spec predates commit 4a7edc49, which
narrowed the install to OMP and Pi only and deleted `codex/config.toml`;
`docs/ownership.md`/`ownership.tsv` never landed on `main`. This module keeps
only what still applies:

  - The chezmoi source-name decoder (attribute prefixes, `dot_`, `.tmpl`,
    `.age`, dot-leading source entries).
  - The collision rule: a decoded target equal to, an ancestor of, or a
    descendant of a managed destination; a `symlink_` entry whose target
    (link content) points into agent-config.
  - Conservative `.chezmoiignore` evaluation: an ignore line inside a
    template conditional (`{{ if ... }} ... {{ end }}`) might not be active
    on every machine, so a destination it covers is still reported as a
    collision. An *unconditional* (top-level) ignore line is a hard gate —
    chezmoi will never manage that path on any machine, so a source that
    would otherwise claim it is inert and is not reported.

Dropped from the original spec, and why:
  - S16 (`~/.codex/config.toml`, a dotfiles/agent-config key-partitioned
    merge) doesn't exist any more: `codex/config.toml` was deleted from this
    repo and Codex is out of scope. There is no Codex-only exemption to
    carry forward.
  - The `~/.config/opencode/*` destinations from the old inventory table are
    gone. `~/.claude/skills` is a live destination again (Claude Code does not
    read the shared `~/.agents` root, so it gets its own link per skill), but
    `~/.claude/agents/*.md` is linked from `claude/agents/`; the rest of
    `~/.claude` — `CLAUDE.md`, `settings.json` — stays out of scope and
    hand-managed. `install.sh` writes to exactly four roots
    now (see MANAGED_DESTINATIONS below), plus the `pi/web-search.json` shared
    merge.
  - `ownership.tsv` and `docs/ownership.md` never landed on `main`, so this
    module does not read them; it hardcodes the destination list from
    `install.sh` directly (see AGENTS.md's install table, which is the
    living source of truth).

This module is read-only: it never touches `~/dev/dotfiles`, `chezmoi`, or
this checkout's own tree. It only classifies chezmoi *source* paths supplied
by the caller (a real `git ls-files` listing, or a fixture).
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import PurePosixPath
from typing import Iterable, Mapping, Sequence

# --------------------------------------------------------------------------
# Managed destinations
#
# One data structure, adapted directly from install.sh's three destinations
# (see its header comment and AGENTS.md's "What this repo installs" table).
# Every path below is HOME-relative POSIX, without a leading slash.
#
# - "tree": the destination and every path under it is a claim (this is the
#   one directory-level delivery — install.sh symlinks a whole directory per
#   skill, and the parent root is shared by every skill name). An ancestor of
#   the tree root (e.g. "~/.agents") is also a claim: a dotfiles source that
#   takes over "~/.agents" as a whole would swallow the skills root too.
# - "file": an exact HOME-relative path. install.sh symlinks these one file
#   at a time, so only an exact match (or an ancestor directory swallowing
#   it) is a claim.
# - "glob": a directory plus a filename pattern for arbitrary basenames
#   install.sh links individually (themes, prompts, per-agent files, OMP
#   overlays). Any file directly inside the directory matching the pattern
#   is a claim, and so is the directory itself or an ancestor of it.
# - "nested_glob": like "glob", but one more path component deep (Pi
#   extensions: <name>/{index.js,index.ts,theme.json}).
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class ManagedDestination:
    kind: str  # "tree" | "file" | "glob" | "nested_glob"
    path: str  # HOME-relative directory (tree/glob/nested_glob) or file (file)
    patterns: tuple[str, ...] = ()  # glob: filename patterns; nested_glob: exact filenames
    note: str = ""


MANAGED_DESTINATIONS: tuple[ManagedDestination, ...] = (
    # Shared skills root: skills/<name>/ and vendor external skills, one
    # symlinked directory per skill name.
    ManagedDestination("tree", ".agents/skills", note="shared skills root"),
    # Claude Code's own skills root. Claude Code does not read the shared root,
    # so install.sh links the same set a second time here (only when ~/.claude
    # already exists). Same directory-per-skill shape as the shared root.
    ManagedDestination("tree", ".claude/skills", note="Claude Code skills root"),
    # Claude Code config: the statusline pair and its theme are linked;
    # settings.json is merged (see EXEMPT_SHARED_WRITERS).
    ManagedDestination("file", ".claude/statusline.sh"),
    ManagedDestination("file", ".claude/subagent-statusline.sh"),
    ManagedDestination("file", ".claude/claude-powerline.json"),
    # Claude Code agents, one link per claude/agents/*.md.
    ManagedDestination("glob", ".claude/agents", ("*.md",)),
    # OMP configuration under ~/.omp/agent.
    ManagedDestination("file", ".omp/agent/AGENTS.md"),
    ManagedDestination("file", ".omp/agent/config.yml"),
    ManagedDestination("file", ".omp/agent/keybindings.yml"),
    ManagedDestination("file", ".omp/agent/lsp.yml"),
    ManagedDestination("glob", ".omp/agent/themes", ("*.json",)),
    ManagedDestination("glob", ".omp/agent/agents", ("*.md",)),
    ManagedDestination("glob", ".omp/agent/commands", ("*.md",)),
    # OMP overlays, linked file by file into ~/.config/omp so the runtime
    # .active-overlay file (not ours) is left alone.
    ManagedDestination("glob", ".config/omp", ("*",), note="OMP overlays"),
    # Pi configuration under ~/.pi/agent.
    ManagedDestination("file", ".pi/agent/AGENTS.md"),
    ManagedDestination("file", ".pi/agent/settings.json"),
    ManagedDestination("file", ".pi/agent/verbosity.json"),
    ManagedDestination("file", ".pi/agent/pi-fff.json"),
    ManagedDestination("file", ".pi/agent/keybindings.json"),
    ManagedDestination("file", ".pi/agent/subagents.json"),
    ManagedDestination("glob", ".pi/agent/prompts", ("*.md",)),
    ManagedDestination("glob", ".pi/agent/themes", ("*.json",)),
    ManagedDestination("glob", ".pi/agent/agents", ("*.md",)),
    ManagedDestination("file", ".config/herdr/config.toml"),
    ManagedDestination(
        "nested_glob",
        ".pi/agent/extensions",
        ("index.js", "index.ts", "theme.json"),
    ),
)

# Intentional shared writers: `install.sh` merges repo-owned keys into these
# live files instead of symlinking them (pi-web-access's own credential
# store lives at the same path; Claude Code writes settings.json itself and
# herdr owns its hook entry; OMP owns mcp.json and only gets missing servers
# seeded). A dotfiles source targeting one of these is not a collision — it
# is the other declared writer, same as S16 used to be for
# `~/.codex/config.toml` before that surface was retired.
EXEMPT_SHARED_WRITERS: tuple[str, ...] = (
    ".pi/web-search.json",
    ".pi/agent/web-search.json",
    ".claude/settings.json",
    ".omp/agent/mcp.json",
)

# --------------------------------------------------------------------------
# Chezmoi source-name decoding
# --------------------------------------------------------------------------

# Attribute prefixes chezmoi strips from a source name to get the target
# name. Stripped repeatedly, per path component, so combinations like
# `run_once_after_` decode correctly one prefix at a time.
_ATTRIBUTE_PREFIXES: tuple[str, ...] = (
    "private_",
    "readonly_",
    "empty_",
    "executable_",
    "create_",
    "modify_",
    "remove_",
    "symlink_",
    "encrypted_",
    "exact_",
    "external_",
    "once_",
    "onchange_",
    "run_",
    "before_",
    "after_",
)


def _strip_attribute_prefixes(component: str) -> str:
    changed = True
    while changed:
        changed = False
        for prefix in _ATTRIBUTE_PREFIXES:
            if component.startswith(prefix):
                component = component[len(prefix) :]
                changed = True
    return component


def _decode_component(component: str) -> str:
    component = _strip_attribute_prefixes(component)
    if component.startswith("dot_"):
        component = "." + component[len("dot_") :]
    return component


def _strip_source_suffixes(path: str) -> str:
    for suffix in (".tmpl", ".age"):
        if path.endswith(suffix):
            path = path[: -len(suffix)]
    return path


def is_symlink_source(source_path: str) -> bool:
    """True when any component of the source path carries the symlink_ attribute."""
    for raw_component in source_path.split("/"):
        component = raw_component
        while True:
            stripped = False
            for prefix in _ATTRIBUTE_PREFIXES:
                if component.startswith(prefix):
                    if prefix == "symlink_":
                        return True
                    component = component[len(prefix) :]
                    stripped = True
                    break
            if not stripped:
                break
    return False


def decode_source_path(source_path: str) -> str | None:
    """Decode a chezmoi source-relative path to its HOME-relative target.

    Returns None for entries chezmoi ignores outright: a path whose first
    raw (pre-decode) component starts with "." — chezmoi source names for
    managed dotfiles never start with a literal dot (they use `dot_`), so a
    leading dot marks a chezmoi-special or unmanaged file such as
    `.chezmoiignore`, `.chezmoi.toml.tmpl` or anything under
    `.chezmoiscripts/`.
    """
    components = source_path.split("/")
    if components and components[0].startswith("."):
        return None
    decoded = "/".join(_decode_component(c) for c in components)
    decoded = _strip_source_suffixes(decoded)
    return decoded


# --------------------------------------------------------------------------
# .chezmoiignore evaluation (conservative)
# --------------------------------------------------------------------------

_IF_RE = re.compile(r"^\s*\{\{-?\s*if\b")
_END_RE = re.compile(r"^\s*\{\{-?\s*end\b")


@dataclass(frozen=True)
class IgnorePattern:
    pattern: str
    conditional: bool  # True if inside a {{ if }} ... {{ end }} block


def parse_chezmoiignore(text: str) -> tuple[IgnorePattern, ...]:
    """Parse .chezmoiignore conservatively.

    A line inside a template conditional block might not be active on every
    machine, so it is kept as a "soft" (conditional) pattern: it still
    reports collisions, only annotated as gated. A plain top-level line is a
    "hard" gate that always applies, so it fully suppresses a report for the
    paths it covers.
    """
    patterns: list[IgnorePattern] = []
    depth = 0
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if _IF_RE.match(line):
            depth += 1
            continue
        if _END_RE.match(line):
            depth = max(0, depth - 1)
            continue
        if line.startswith("#"):
            continue
        if line.startswith("{{") :
            # Other template directives (else, etc.) — not a pattern line.
            continue
        pattern = line.lstrip("/")
        patterns.append(IgnorePattern(pattern=pattern, conditional=depth > 0))
    return tuple(patterns)


def _pattern_matches(pattern: str, target: str) -> bool:
    import fnmatch

    target_path = PurePosixPath(target)
    pattern_path = PurePosixPath(pattern)
    if target_path == pattern_path:
        return True
    try:
        if target_path.is_relative_to(pattern_path):
            return True
    except ValueError:
        pass
    if fnmatch.fnmatch(target, pattern):
        return True
    return False


@dataclass(frozen=True)
class GateResult:
    hard: bool
    soft: bool


def evaluate_gate(target: str, ignore_patterns: Sequence[IgnorePattern]) -> GateResult:
    hard = False
    soft = False
    for entry in ignore_patterns:
        if _pattern_matches(entry.pattern, target):
            if entry.conditional:
                soft = True
            else:
                hard = True
    return GateResult(hard=hard, soft=soft)


# --------------------------------------------------------------------------
# Collision classification
# --------------------------------------------------------------------------


def _is_ancestor_or_descendant(a: str, b: str) -> bool:
    pa, pb = PurePosixPath(a), PurePosixPath(b)
    if pa == pb:
        return True
    try:
        return pa.is_relative_to(pb) or pb.is_relative_to(pa)
    except ValueError:
        return False


def _classify_against_destination(target: str, destination: ManagedDestination) -> str | None:
    if destination.kind == "tree":
        if _is_ancestor_or_descendant(target, destination.path):
            return f"claims managed directory {destination.path!r}"
        return None

    if destination.kind == "file":
        if _is_ancestor_or_descendant(target, destination.path):
            return f"claims managed file {destination.path!r}"
        return None

    if destination.kind == "glob":
        target_path = PurePosixPath(target)
        dest_path = PurePosixPath(destination.path)
        if _is_ancestor_or_descendant(target, destination.path):
            # The directory itself, or an ancestor of it.
            if target_path == dest_path or dest_path.is_relative_to(target_path):
                return f"claims managed directory {destination.path!r}"
        if target_path.parent == dest_path:
            import fnmatch

            for glob_pattern in destination.patterns:
                if fnmatch.fnmatch(target_path.name, glob_pattern):
                    return f"claims managed file under {destination.path!r} ({glob_pattern})"
        return None

    if destination.kind == "nested_glob":
        target_path = PurePosixPath(target)
        dest_path = PurePosixPath(destination.path)
        if _is_ancestor_or_descendant(target, destination.path):
            if target_path == dest_path or dest_path.is_relative_to(target_path):
                return f"claims managed directory {destination.path!r}"
        # <dest>/<name>/<filename>
        try:
            relative = target_path.relative_to(dest_path)
        except ValueError:
            return None
        if len(relative.parts) == 2 and relative.parts[1] in destination.patterns:
            return f"claims managed file under {destination.path!r}/*/{relative.parts[1]}"
        return None

    raise ValueError(f"unknown ManagedDestination kind: {destination.kind!r}")


def classify_target(target: str) -> str | None:
    """Return a reason string if `target` collides with a managed destination.

    Returns None for a target that is one of the intentional shared-writer
    exemptions (EXEMPT_SHARED_WRITERS), or that touches no managed
    destination at all.
    """
    if target in EXEMPT_SHARED_WRITERS:
        return None
    for destination in MANAGED_DESTINATIONS:
        reason = _classify_against_destination(target, destination)
        if reason is not None:
            return reason
    return None


AGENT_CONFIG_MARKERS: tuple[str, ...] = (
    "agent-config",
    "dev/agent-config",
)


def _points_into_agent_config(link_target: str) -> bool:
    return any(marker in link_target for marker in AGENT_CONFIG_MARKERS)


# --------------------------------------------------------------------------
# Public report type and entry point
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class Collision:
    source_path: str
    target: str
    reason: str
    gated: bool = False  # covered by a conditional (soft) .chezmoiignore gate


def find_collisions(
    source_paths: Iterable[str],
    chezmoiignore_text: str = "",
    symlink_targets: Mapping[str, str] | None = None,
) -> list[Collision]:
    """Find chezmoi source paths that collide with agent-config's install destinations.

    `source_paths` is a chezmoi source tree listing (e.g. `git ls-files`
    output from a dotfiles checkout, or a fixture). `chezmoiignore_text` is
    the contents of dotfiles' `.chezmoiignore`. `symlink_targets` optionally
    maps a `symlink_`-attributed source path to the literal link target it
    would create (the file's content in chezmoi's source repo) — supply it
    to also catch a symlink whose *target* points back into agent-config
    even when its own decoded path does not collide.

    A destination hidden by an unconditional (non-templated) ignore line is
    never reported: chezmoi will not manage that path on any machine, so a
    source that would otherwise claim it is inert. A destination hidden only
    inside a `{{ if }}` block is still reported (annotated `gated=True`),
    because the condition may be false on some machine.
    """
    symlink_targets = symlink_targets or {}
    ignore_patterns = parse_chezmoiignore(chezmoiignore_text)
    collisions: list[Collision] = []

    for source_path in source_paths:
        target = decode_source_path(source_path)
        if target is None:
            continue

        reason = classify_target(target)
        if reason is not None:
            gate = evaluate_gate(target, ignore_patterns)
            if gate.hard:
                continue
            collisions.append(
                Collision(source_path=source_path, target=target, reason=reason, gated=gate.soft)
            )
            continue

        if is_symlink_source(source_path) and source_path in symlink_targets:
            link_target = symlink_targets[source_path]
            if _points_into_agent_config(link_target):
                gate = evaluate_gate(target, ignore_patterns)
                if gate.hard:
                    continue
                collisions.append(
                    Collision(
                        source_path=source_path,
                        target=target,
                        reason=f"symlink target points into agent-config ({link_target})",
                        gated=gate.soft,
                    )
                )

    return collisions
