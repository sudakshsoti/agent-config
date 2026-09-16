---
name: skill-lifecycle
description: "Use when adding, renaming, retiring, installing, or auditing a repo-owned agent skill in agent-config. Keep frontmatter, inventory, manifest policy, and installation checks synchronized."
---

# Skill lifecycle

Maintain skills as a small, distributable catalogue rather than as loose prompt
files. This skill applies to `skills/<name>/` entries owned by this repository;
third-party skills remain vendored by reference through `plugins.txt`.

## Before changing a skill

1. Read `AGENTS.md` and the relevant sections of `skills/README.md`.
2. Check `git status --short` and preserve unrelated work.
3. Decide which lane owns the skill:
   - `skills/<name>/` for an editable repo-owned skill;
   - `external` in `plugins.txt` for a third-party skill set that must reach
     the shared root.
4. Do not copy third-party content into `skills/` without an explicit decision.
   Audit upstream instructions before installing anything.

## Add or rename a repo-owned skill

Create exactly:

```text
skills/<name>/SKILL.md
```

The frontmatter must satisfy the repository contract:

- `name` equals the directory name;
- the name is lowercase kebab-case and contains no `claude` or `anthropic`;
- `description` says what the skill does and when to use it;
- a multiline description uses `|` or `>-`, never a bare scalar;
- keep the always-loaded description concise and move long material into
  `references/`.

Make the description a precise discovery surface. Do not solve missed triggers
by putting the whole procedure in frontmatter.

Update the matching entry in `skills/README.md`. If the skill is renamed, update
all references and remove the old entry; do not leave aliases that make the
catalogue ambiguous.

## Install

A repo-owned skill is delivered as source under `skills/<name>/`. A skill listed
in `distribution.txt` is also packaged as `dist/<name>.zip` for claude.ai; when
renaming or retiring one, update that list too (the pre-commit hook rebuilds and
removes zips, and `python3 scripts/build-dist.py --check` reports drift). One symlink is written into the shared
`~/.agents/skills` root, and OMP and Pi both read it from there:

```bash
python3 scripts/lint-skills.py
```

The installer refuses to replace a real unmanaged directory, so a stale `mv`d
copy must be removed deliberately before a link can be created.

For a safe local link test, use a disposable `HOME` and the selective installer:

```bash
tmp_home="$(mktemp -d)"
HOME="$tmp_home" ./install.sh --skills-only=<name>
rm -rf "$tmp_home"
```

Do not run the full installer merely to test a new skill when external fetches,
settings, or machine-local configuration are not needed.

## Retire a skill

Before removing it:

1. search the repository for the skill name and references to its commands;
2. remove or update callers, documentation, and manifest entries;
3. run the frontmatter and installer checks;
4. run `./install.sh --prune` from the canonical checkout when cleaning live
   symlinks is explicitly intended.

Pruning only removes managed dangling links. Do not delete unmanaged skills or
machine-local configuration by hand.

## Verification checklist

For any catalogue change, run the narrowest checks first, then the full suite:

```bash
python3 scripts/lint-skills.py
python3 scripts/test-install-selected-skills.py
./scripts/check.sh
```

Inspect `git diff --check` and `git status --short` afterwards. A new skill is
not complete if its source passes but its README inventory, manifest lane, or
installation behavior is stale.

## Safety boundaries

- Never put tokens, API keys, auth stores, `.env` files, or `mcp.json` in a
  skill or this repository.
- Do not edit generated or machine-local configuration as part of a skill
  change unless that exact file is the requested source of truth.
- Do not silently add an entire upstream collection when a named allowlist is
  sufficient; extra descriptions consume the shared agent context budget.
- Do not claim a skill is installed globally until the canonical checkout has
  been installed with `install.sh` and the resulting links have been checked.
