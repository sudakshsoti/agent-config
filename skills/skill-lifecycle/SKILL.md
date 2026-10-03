---
name: skill-lifecycle
description: "Use when adding, renaming, retiring, or installing a repo-owned skill in agent-config. Not for editing a skill's prose (writing-for-agents)."
---

# Skill lifecycle

This skill applies to `skills/<name>/` entries owned by this repository;
third-party skills are vendored by reference through `plugins.txt`.

## Before changing a skill

1. Read `AGENTS.md` and the relevant sections of `skills/README.md`.
2. Pick the lane: `skills/<name>/` for an editable repo-owned skill, or an
   `external` line in `plugins.txt` for a third-party set (AGENTS.md owns the
   rules). Before adding an `external` line, read the upstream `SKILL.md` and any
   hooks or scripts it ships.

## Add or rename a repo-owned skill

Create exactly `skills/<name>/SKILL.md`. Its frontmatter must pass
`python3 scripts/lint-skills.py`; AGENTS.md owns the rules. Keep the description
a precise discovery surface, not the procedure, and move long material into
`references/`.

Update the matching entry in `skills/README.md`. On a rename, update all
references and remove the old entry and any alias. If the skill is listed in
`distribution.txt` (shipped to claude.ai as `dist/<name>.zip`), update that list
too; the pre-commit hook rebuilds the zips, and
`python3 scripts/build-dist.py --check` reports drift.

## Install

1. Run `./install.sh` from the canonical checkout `~/dev/agent-config`, never
   from a worktree. It links the skill into `~/.agents/skills/<name>` (OMP, Pi,
   Codex, OpenCode) and, when `~/.claude` exists, `~/.claude/skills/<name>`
   (Claude Code). It refuses to replace a real unmanaged directory, so remove a
   stale copied directory deliberately first.
2. Check both links: `ls -l ~/.agents/skills/<name>`, and
   `ls -l ~/.claude/skills/<name>` when `~/.claude` exists.
3. Optional: test the link in a disposable `HOME` first. `--skills-only` fills
   only the shared root, never `~/.claude/skills`.

   ```bash
   tmp_home="$(mktemp -d)"
   HOME="$tmp_home" ./install.sh --skills-only=<name>
   rm -rf "$tmp_home"
   ```

## Retire a skill

1. Search the repository for the skill name and references to its commands.
2. Remove or update callers, documentation, `skills/README.md`, manifest entries
   and its `distribution.txt` line.
3. Run `python3 scripts/lint-skills.py` and `python3 scripts/build-dist.py --check`.
4. When cleaning live symlinks is intended, run `./install.sh --prune` from the
   canonical checkout. It removes only managed dangling links; never delete
   unmanaged skills or machine-local configuration by hand.

## Verification checklist

```bash
python3 scripts/test-install-selected-skills.py
./scripts/check.sh   # includes lint-skills.py
```

A new skill is not complete if its source passes but its README inventory,
manifest lane, or installation behavior is stale.

## Safety boundaries

- Secrets and machine-local configuration stay out of skills and this
  repository; see AGENTS.md.
- Do not edit generated or machine-local configuration as part of a skill
  change unless that exact file is the requested source of truth.
