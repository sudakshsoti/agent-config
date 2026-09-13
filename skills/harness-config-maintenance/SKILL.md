---
name: harness-config-maintenance
description: "Use when changing agent-config settings, model routing, installation, plugins, prompts, agents, extensions, or cross-harness instructions. Preserve ownership boundaries and verify the affected Claude, Codex, OMP, and Pi surfaces safely."
---

# Harness configuration maintenance

Treat this repository as the source of truth for agent behavior across four
harnesses. Before editing, read `AGENTS.md`, the relevant `README.md` section,
and any plan or handoff named by the task. Check `git status --short` and do not
absorb unrelated changes.

## Identify the owner before editing

| Concern | Source of truth | Important behavior |
| --- | --- | --- |
| Shared instructions | `global-agents.md` | Symlinked into every installed harness; changes have broad effect. |
| Instructions for this checkout | root `AGENTS.md` | Do not confuse it with the shared `global-agents.md`. |
| Claude settings | `settings.json` plus live `~/.claude/settings.json` | The repo file is a sanitized snapshot; use `sync.sh` for live-to-repo updates. |
| Codex settings | `codex/config.toml` | Selectively merged; never replace the user's full config or credentials. |
| OMP behavior | `omp/config.yml`, `omp/lsp.yml`, overlays | Symlinked and may be rewritten by OMP; review the diff after TUI changes. |
| Pi behavior | `pi/settings.json`, `pi/subagents.json`, prompts, agents, extensions | Symlinked and may be rewritten by Pi; auth and runtime state stay machine-local. |
| Skill catalogue | `skills/`, `plugins.txt`, `dist/` | Follow `skill-lifecycle`; keep repo-owned ZIPs in sync. |
| Shell and machine tooling | `dotfiles` repository | Do not move launcher or chezmoi changes here just because this repo documents them. |

When a file is a live symlink target, edit the tracked source intentionally and
inspect the resulting `git diff`. Never edit `~/.pi/agent/auth.json`,
`~/.omp/agent/mcp.json`, `.env` files, session stores, or model caches.

## Model and harness routing

Use `pi/model-ladder.md` and the routing notes in `AGENTS.md` as the authority.
Keep these distinctions intact:

- Pi agent roles select models in each `pi/agents/*.md` frontmatter.
- OMP roles select models in `omp/config.yml`; overlays are per invocation.
- A model listed in Pi `enabledModels` is a quick-switch entry, not an agent
  routing rule.
- Use the least expensive suitable tier for bounded discovery and reserve the
  stronger tiers for architecture, security, and difficult bugs.
- Do not add Anthropic subscription models to Pi; its authentication path is
  incompatible with third-party subscription OAuth in this setup.
- Do not encode a fallback or routing decision in only one harness when the
  behavior is intended to be shared. Update the relevant source and document
  intentional differences.

## Safe change procedure

1. **Name the affected surfaces.** Is this a skill, prompt, agent, extension,
   model route, installer path, or shared instruction?
2. **Trace consumers.** Search `install.sh`, the relevant settings file, tests,
   and documentation before changing a key or path.
3. **Make the smallest source change.** Preserve comments that explain policy;
   OMP may strip comments when it rewrites its YAML, so durable rationale
   belongs in repository docs.
4. **Keep secrets out.** Configuration shape may be documented, but credentials
   remain in machine-local stores or dotfiles-managed secret paths.
5. **Verify the exact surface.** Run the focused test for the changed merger,
   installer, extension, or policy before running the full suite.
6. **Inspect the boundary.** Review `git diff --check`, `git status --short`,
   generated artifacts, and any live configuration that the task explicitly
   asked you to apply. Do not run `chezmoi apply` or a global installer
   speculatively.

## Common change recipes

### Shared instruction or policy

- Update `global-agents.md` only when the rule truly applies to all harnesses.
- Update root `AGENTS.md` for repository-local facts and commands.
- Run the applicable instruction-contract tests and inspect both files for
  duplicated or conflicting rules.

### Pi or OMP agent

- Read the agent's current frontmatter/config and its neighboring agents.
- Preserve explicit model, effort, `prompt_mode`, and tool restrictions unless
  the task changes them.
- Check whether child sessions inherit or replace prompts; this matters for
  bridge and subagent behavior.
- Run the relevant JSON/YAML syntax and policy tests, then restart the harness
  when live reload is not guaranteed.

### Skill installation policy

- Repo-owned skills belong under `skills/<name>/` and are linked by
  `install.sh`.
- Third-party skills that must reach all harnesses use a named `external`
  allowlist; Claude-only packages use the marketplace/plugin lane.
- Prefer a narrow allowlist. A bare upstream collection can silently consume
  the shared context budget.
- Follow `skills/skill-lifecycle/SKILL.md` for ZIPs, inventory, and pruning.

### Installer or sync behavior

- Read the relevant installer function and its tests before editing.
- Preserve the refusal behavior for real unmanaged files and ephemeral
  worktrees.
- Test with a disposable `HOME`; never use the real home directory for an
  installer regression test.
- Keep `--no-plugins` and `--skills-only` isolation guarantees intact.

## Verification matrix

Use focused checks first:

```bash
python3 scripts/test-install-selected-skills.py
python3 scripts/test-apply-codex-config.py
python3 scripts/test-apply-web-search-config.py
python3 scripts/test-design-instructions.py
python3 scripts/test-omp-catastrophe-policy.py
node scripts/test-catastrophe-guard.mjs
```

For skill, installer, or cross-harness changes, finish with:

```bash
./scripts/check.sh
git diff --check
git status --short
```

For shell changes also run `bash -n` or `zsh -n` on the affected source. For
Pi JavaScript extensions, run the narrow extension test and use LSP/AST checks
when available. Report any check that could not run rather than treating it as
passing.

## Stop conditions

Stop and ask for a decision when the change would require:

- modifying a machine-local or credential-bearing file;
- changing a public behavior without a plan or acceptance criteria;
- adding a dependency or upstream skill collection beyond the requested scope;
- applying dotfiles or installing globally when the user asked only for a repo
  change;
- changing both this repo and `dotfiles` without an explicit cross-repository
  plan.
