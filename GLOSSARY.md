# agent-config

Source of truth for how coding agents behave on this user's machines: skills, harness config, model routing and the installer that delivers them. Machine state (shell, fonts, secrets) belongs to dotfiles, not here.

## Language

### Delivery

**Harness**:
An agent runtime that reads config from this repo: OMP, Pi, Claude Code, Codex or OpenCode.
_Avoid_: Tool, client, CLI

**Skill**:
A directory with a `SKILL.md` that a harness loads on demand. Repo-owned skills live in `skills/<name>/`.
_Avoid_: Plugin, prompt, command

**External skill**:
A skill cloned from a third-party repo into ignored `vendor/` and linked by reference. Declared as an `external` line in `plugins.txt`.
_Avoid_: Vendored copy, imported skill

**Allowlist**:
The skill names on an `external` line. A bare external line with no names imports every upstream skill.
_Avoid_: Filter, include list

**Shared root**:
`~/.agents/skills/`, the one directory Codex, OpenCode, OMP and Pi read skills from natively.
_Avoid_: Global skills dir

**Managed link**:
A symlink created by install that points back into this checkout. `--prune` removes only these.
_Avoid_: Symlink (unqualified), installed file

**Merge**:
Install behaviour for files a harness also writes (`claude/settings.json`, `pi/web-search.json`): repo-owned keys are pushed, other keys stay machine-local.
_Avoid_: Sync, overwrite

**Work machine gate**:
Install behaviour on a machine whose chezmoi profile is `work`: skills are linked, every harness config step is skipped.
_Avoid_: Work mode, corporate profile

**Distribution**:
The subset of skills packaged as `dist/<name>.zip` for claude.ai. Listed in `distribution.txt`.
_Avoid_: Release, bundle

### Routing

**Role**:
A named slot in OMP's `modelRoles` (`default`, `plan`, `slow`, `smol`…) that maps to a model selector.
_Avoid_: Profile, tier

**Agent**:
A subagent type spawned through the task tool, whose model comes from `task.agentModelOverrides`.
_Avoid_: Worker, bot

**Selector**:
A `provider/model[:effort]` string.
_Avoid_: Model ID, model name

**Effort**:
The thinking level suffix on a selector (`minimal` to `max`). Valid levels differ per model.
_Avoid_: Reasoning mode, thinking budget

**Fallback chain**:
An ordered list of selectors tried when a model is exhausted or erroring, keyed by exact model, provider, role or default.
_Avoid_: Failover, backup model

**Second lineage**:
A reviewing model from a different vendor than the one that produced the work, so a hostile pass is not the same model family checking itself.
_Avoid_: Independent review, cross-check

**Quota pool**:
A separately metered allowance (Anthropic subscription, OpenCode Go, Muse Code). Routing spreads load so exhausting one never stalls another.
_Avoid_: Budget, plan

### Ownership

**Dotfiles**:
The sibling repo that owns the machine: shell, fonts, secrets, the machine profile. This repo only reads it.
_Avoid_: Chezmoi (that is its tool)

**Neither-owned**:
Runtime state or credentials no repo tracks, such as logins, sessions and `~/.claude.json`.
_Avoid_: Untracked config
