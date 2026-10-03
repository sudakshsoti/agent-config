---
name: harness-config-maintenance
description: "Use when changing OMP/Pi/Claude Code/herdr config, model routing, install.sh, plugins.txt, global-agents.md, or Pi/OMP agents and extensions in agent-config. Not for adding, renaming or retiring a skill (skill-lifecycle) or prose quality (writing-for-agents)."
---

# Harness configuration maintenance

Treat this repository as the source of truth for agent behavior across OMP and
Pi, plus the Claude Code and herdr configuration surfaces. Before editing, read
`AGENTS.md`, the relevant `README.md` section, and any plan or handoff named by
the task.

## Identify the owner before editing

| Concern | Source of truth | Important behavior |
| --- | --- | --- |
| Shared instructions | `global-agents.md` | Linked into the installed harnesses as `AGENTS.md`; changes have broad effect. |
| Instructions for this checkout | root `AGENTS.md` | Do not confuse it with the shared `global-agents.md`. |
| OMP behavior | `omp/config.yml`, `omp/lsp.yml`, `omp/keybindings.yml`, `omp/agents/`, `omp/overlays/` | Symlinked and rewritten by OMP; review the diff after TUI changes. |
| Pi behavior | `pi/settings.json`, `pi/subagents.json`, `pi/pi-fff.json`, `pi/keybindings.json`, prompts, agents, extensions | Symlinked and rewritten by Pi; auth and runtime state stay machine-local. |
| Claude Code behavior | `claude/` (`settings.json`, `statusline.sh`, `claude-powerline.json`, `plugins.txt`) | `settings.json` is merged, the rest linked or declarative; applied only when `~/.claude` exists. |
| herdr behavior | `herdr/` (`config.toml`, `plugins.txt`) | Declarative; herdr writes its own hooks into Claude settings. |
| Shared skills | `skills/`, `plugins.txt` | Source-only. Follow `skill-lifecycle`; links go into `~/.agents/skills` and, when `~/.claude` exists, `~/.claude/skills`. |
| Shell and machine tooling | `dotfiles` repository | Do not move launcher or chezmoi changes here just because this repo documents them. |

When a file is a live symlink target, edit the tracked source intentionally and
inspect the resulting `git diff`. Never edit credential-bearing or machine-local files: `~/.pi/agent/auth.json`,
`~/.omp/agent/mcp.json`, `.env` files, session stores, or model caches.

## Model and harness routing

`pi/model-ladder.md` and the routing notes in `AGENTS.md` are the authority for
roles, tiers and `enabledModels`. Keep these guardrails intact:

- `anthropic/*`, `openai-codex/*` and `opencode-go/*` are **provider IDs**, not
  harnesses. A provider ID stays valid long after any standalone Codex or
  OpenCode installation was retired; never strip one while "removing Codex".
  Remove a provider from routing only when its *subscription or credential* is
  gone, and then disable it explicitly rather than leaving it reachable by
  fallback.
- Claude in Pi is an explicit pin gated by `scripts/check-model-routing.py`;
  see the AGENTS.md model-routing notes. Never put it in a fallback chain.
- Do not encode a fallback or routing decision in only one harness when the
  behavior is intended to be shared. Update the relevant source and document
  intentional differences.

## Safe change procedure

1. **Trace consumers.** Search `install.sh`, the relevant settings file, tests,
   and documentation before changing a key or path.
2. **Preserve policy.** OMP may strip comments when it rewrites its YAML, so
   durable rationale belongs in repository docs.
3. **Verify the exact surface.** Run the focused test for the changed installer,
   merger, extension, or policy before running the full suite.
4. **Inspect the boundary.** Review generated artifacts and any live
   configuration the task explicitly asked you to apply. Do not run
   `chezmoi apply` or a global installer speculatively.

## Common change recipes

### Shared instruction or policy

- Update `global-agents.md` only when the rule truly applies to both harnesses.
- Update root `AGENTS.md` for repository-local facts and commands.
- Run the applicable instruction-contract tests and inspect both files for
  duplicated or conflicting rules.

### Pi or OMP agent

- Read the agent's current frontmatter/config and its neighboring agents.
- Preserve explicit model, effort, `prompt_mode`, and tool restrictions unless
  the task changes them.
- Check whether child sessions inherit or replace prompts; this matters for
  subagent and bridge behavior.
- Run the relevant JSON/YAML syntax and policy tests, then restart the harness
  when live reload is not guaranteed.

### Skill installation policy

Follow `skills/skill-lifecycle/SKILL.md`. Third-party sets use a named
`external` allowlist in `plugins.txt`. `omp/plugins.txt`, `claude/plugins.txt`
and `herdr/plugins.txt` declare harness plugins, not skill sources.

### Installer or prune behavior

- Read the relevant installer function and its tests before editing.
- `--prune` removes only symlinks into this repository and copies carrying the
  `.agent-config-managed` marker, and must stay idempotent.
- Test with a disposable `HOME`; never use the real home directory for an
  installer regression test.
- Keep `--skills-only` and `--no-external` isolation guarantees intact.

## Verification matrix

Use focused checks first:

```bash
python3 scripts/check-model-routing.py
python3 scripts/test-install-selected-skills.py
python3 scripts/test-apply-json-config.py
```

Any model-routing edit — a role, an agent override, an overlay, an agent
`model:` frontmatter key — MUST end with `check-model-routing.py`; its header
lists what it checks, and none of those failures show at runtime.

For skill, installer, or cross-harness changes, finish with:

```bash
./scripts/check.sh
git diff --check
git status --short
```

For shell changes also run `bash -n` or `zsh -n` on the affected source. For Pi
JavaScript extensions, run the narrow test (e.g.
`node scripts/test-operational-footer.mjs`) and use LSP/AST checks when
available. Report any check that could not run rather than treating it as
passing.

## Stop conditions

Stop and ask for a decision when the change would require:

- modifying a machine-local or credential-bearing file (see above);
- changing a public behavior without a plan or acceptance criteria;
- adding a dependency or upstream skill collection beyond the requested scope;
- applying dotfiles or installing globally when the user asked only for a repo
  change;
- changing both this repo and `dotfiles` without an explicit cross-repository
  plan.
