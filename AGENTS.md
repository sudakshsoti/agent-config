# AGENTS.md

This file applies to this checkout. Shared, harness-neutral preferences live in
`global-agents.md` and are installed into OMP and Pi; do not confuse the two.

## What this repo installs

`./install.sh` writes to exactly these destinations:

| Destination | Source | Delivery |
| --- | --- | --- |
| `~/.agents/skills/` | `skills/`, `vendor/` | one symlink per skill; filled only when a shared-root consumer exists |
| `~/.claude/skills/` | `skills/`, `vendor/` | one symlink per skill; filled only when `~/.claude` already exists |
| `~/.claude/agents/` | `claude/agents/` | one symlink per agent; only when `~/.claude` exists; on the work machine only with `--claude-agents` |
| `~/.claude/` config | `claude/`, `snapshots/claude/mcp.json` | statusline pair + `claude-powerline.json` linked (identical real copies adopted); `settings.json` **merged**; plugins via `claude/plugins.txt` (skipped by `--no-external`); MCP servers added if missing. Only when `~/.claude` exists; run `claude` once on a new box first |
| `~/.omp/agent/` + `~/.config/omp/` | `omp/`, `global-agents.md` | one symlink per file; OMP writes through links |
| `~/.omp/agent/` extras | `omp/plugins.txt`, `snapshots/omp/mcp.json` | `omp plugin install` (skipped by `--no-external`; needs bun); MCP servers added to `mcp.json` if missing, never edited |
| `~/.pi/agent/` | `pi/`, `global-agents.md` | one symlink per file; Pi writes through links |
| `~/.config/herdr/config.toml` | `herdr/config.toml` | one symlink; herdr writes through it; only when `~/.config/herdr` exists. `herdr/plugins.txt` entries go through `herdr plugin install` (skipped by `--no-external`); `herdr/<dir>/herdr-plugin.toml` local plugins are `herdr plugin link`ed (`herdr/marksman-root` drops `.marksman.toml` into linked worktrees, since Marksman rejects a `.git` file) |

`pi/web-search.json` and `claude/settings.json` are **merges**, not links
(`scripts/apply-json-config.py`); only repo-owned keys are pushed. The first is
pi-web-access's credential store; the second is written by Claude Code and
carries herdr's `hooks` entry. The OpenRouter key is never tracked: install
copies `JEV_OPENROUTER_API_KEY` (item `OpenRouter API Key - Jev`) from
`~/.omp/.env` into the live `env` as `OPENROUTER_API_KEY` for the Jev
compaction plugin, kept apart from OMP's own `OPENROUTER_API_KEY` (item
`OpenRouter API Key - omp.sh`) so each is billed separately. Pi's `pi-jev`
compaction uses a different key, item `Mail - TypeSafe API key`, which
dotfiles' `pi()` wrapper reads from 1Password at launch and passes to that
process alone as `TYPESAFE_API_KEY`; it is in no file here. `~/.omp/.env` is
1Password-injected from `omp/overlays/search-keys.tpl`: run `op inject` before
installing on a new box; on the homelab box use the read-only service-account
token (see `global-agents.md`).

- Link skills **once** into `~/.agents/skills`; never also link
  `~/.pi/agent/skills` or skills are discovered twice and consume double the
  context budget.
- **Claude Code is the one exception** (it does not read the shared root): the
  same set is linked again into `~/.claude/skills`. That stays single discovery
  only while `omp/config.yml` pins `skills.enableClaudeUser: false`; OMP scans
  `~/.claude/skills` by default, so dropping the pin doubles every skill in
  OMP. The pin is load-bearing. `install.sh` never creates `~/.claude`.
- Claude Code syncs every skill uploaded to claude.ai back as
  `anthropic-skills:<name>`, duplicating each skill in `distribution.txt` and
  `distribution-vendor.txt`. `claude/settings.json` `skillOverrides` sets each
  qualified name to `"off"`; a bare-name key would hide the local copy too.
  `scripts/check-claude-skill-overrides.py --fix` rewrites them.
- `--skills-only=name,other-name` fills the shared root **only** (never
  `~/.claude/skills`), links only named repo-owned skills, writes no config,
  fetches nothing, and cannot be combined with `--prune`. Use a full
  `./install.sh` to keep Claude Code in sync.
- **Work machine gate.** When `chezmoi data` reports `.machine` = `work`,
  install links skills only and skips every OMP, Pi and Claude config step
  (`global-agents.md`, `omp/`, overlays, `pi/`, `web-search.json`, `claude/`,
  plugins, MCP seeding). Their routing sends prompts and repository source to
  xAI (`xai-oauth`) and OpenRouter, `claude-compact-openrouter` sends transcripts to
  Jev via OpenRouter, and employer code may only reach the employer's
  sanctioned vendor. `--claude-agents` opts back into `claude/agents/` alone
  (Claude only, no new vendor). With no chezmoi or no profile the machine counts
  as unknown and installs as before, so apply dotfiles first. Claude.ai
  connectors belong to the claude.ai account and are not gated here.
- OMP and Pi rewrite linked config in this checkout: **check `git diff`
  before committing**; `pi/settings.json` and `omp/config.yml` are the usual
  suspects.

## Ownership

`~/dev/agent-config` owns agent behaviour; `~/dev/dotfiles` owns the machine.
Secrets belong in dotfiles (1Password + age), never here.

| Path | Owner | Notes |
| --- | --- | --- |
| `skills/`, `plugins.txt` | agent-config | source; only `distribution.txt` skills are also packaged |
| `distribution.txt`, `dist/*.zip` | agent-config | list of claude.ai skills; zips are generated, never hand-edited |
| `global-agents.md` | agent-config | linked to `~/.omp/agent/AGENTS.md` and `~/.pi/agent/AGENTS.md` |
| `omp/`, `pi/`, `herdr/` config | agent-config | harnesses write through links; `omp/commands/*.md` are `/name` wrappers over same-named skills |
| `pi/web-search.json`, `claude/settings.json` | **shared** | merged; credentials and unmanaged keys stay machine-local |
| `omp/plugins.txt`, `snapshots/*/mcp.json` | agent-config | add-only; snapshots refreshed by `scripts/snapshot-machine-config.sh` |
| `~/.omp/agent/mcp.json`, `extensions/`, `agent.db`, `~/.claude.json`, `~/.claude/plugins/`, `~/.claude/hooks/`, `~/.pi/agent/auth.json`, `models-store.json`, `sessions/`, `npm/` | **neither** | credentials or runtime state; untracked. Logins (`/login`, `claude`) are per box |
| `~/.local/bin/omp-*-overlay`, `~/.zshrc`, Brewfile, fonts | **dotfiles** | chezmoi |
| `repo-audit/`, `scripts/repo-audit.py` | agent-config | its timer is dotfiles' `repo-audit.timer` |

## Skills

- Repo-owned skills are `skills/<name>/SKILL.md`; `external` lines in
  `plugins.txt` clone third-party sources into ignored `vendor/`. A bare
  external repo imports every skill and eats the shared context budget; name
  only the skills wanted. Collisions: repo-owned beats external; an `external`
  line naming the skill beats a bare line; else the earliest line wins. Losers
  are skipped with a `SKIP … shadowed by` warning.
- Skill `name` must equal its directory, be lowercase kebab-case, and contain
  neither `claude` nor `anthropic`. Multi-line descriptions require `|` or `>-`;
  an unquoted colon-space can parse as a nested mapping and break loading.
- `python3 scripts/lint-skills.py` enforces these rules, syncs
  `skills/README.md`, and fails on dangling skill references. When a bare
  upstream ships a new skill, add its name to `external-skills.txt`.
- `distribution.txt` and `distribution-vendor.txt` list skills packaged for
  claude.ai by `scripts/build-dist.py` (list only skills that work without a
  local harness). Vendored zips go to gitignored `dist/vendor/`, so third-party
  content never enters this history; rebuild them per machine after `./install.sh`.
- `scripts/repo-audit.py` (weekly on the homelab box) files issues carrying a
  `<!-- repo-audit:<key> -->` marker, never refiled in any state. Reject a
  finding with `wontfix` (plus an `.out-of-scope/` note for a recurring idea).
  It runs on Sonnet, not GLM (user decision 2026-10-04): architecture findings
  need depth, and `/triage` is the human second check.
- Never `npx skills add`: its machine-local `~/.agents/.skill-lock.json` has no
  restore command and is invisible to this repo. Every `~/.agents/skills/*`
  entry must be a symlink; audit with:
  `for d in ~/.agents/skills/*/; do [ -L "${d%/}" ] || echo "${d%/}"; done`
- The `codebase-memory` MCP server does not supply the repo-owned skill.

## Gotchas

- `pi-playwright`'s `pw.js` expects an uninstalled package-local CLI. Use the
  hoisted `~/.pi/agent/npm/node_modules/.bin/playwright-cli` with
  `--browser=chromium`; do not assume system Chrome.
- macOS has no GNU `timeout`; use Python `subprocess.run(..., timeout=...)` or a
  background process plus `kill`.
- `.githooks/pre-commit` runs fast checks; `scripts/check.sh` the full set.
  Never commit `node_modules/`.
- **Plain OMP routing is authoritative in `omp/config.yml`:**

  | Roles/settings | Value |
  | --- | --- |
  | `default` role | `anthropic/claude-opus-5-5:medium` |
  | `plan`/`designer`/`vision` roles; `plan` agent | `anthropic/claude-opus-5-5:high` |
  | `critic` agent | `anthropic/claude-opus-5-5:medium` |
  | `slow` role | `anthropic/claude-opus-5-5:xhigh` |
  | `security-reviewer` role; `security-reviewer` agent | `anthropic/claude-opus-5-5:high` |
  | `builder` agent | `anthropic/claude-sonnet-5-5:medium` |
  | `task` role; `task`/`workflow`/`code-worker` agents | `anthropic/claude-sonnet-5-5:medium` |
  | `sonic` agent | `anthropic/claude-haiku-5-5:medium` |
  | `smol`/`tiny`/`commit` roles | `anthropic/claude-haiku-5-5:low` |
  | `adversary`/`reviewer`/`advisor` roles; `adversary`/`reviewer` agents | `xai-oauth/grok-4.7:high` |
  | `scout` agent | `xai-oauth/grok-4.7:low` |
  | `research` agent | `xai-oauth/grok-4.7:high` |
  | `disabledProviders` | `[openai-codex, opencode-go, muse-code]` |
  | `retry.usageAwareFallback` / `retry.usageReservePct` / `retry.usageReservePolicy` | `true` / `20` / `auto` |
  | `task.maxEffort` / `providers.autoThinkingMaxEffort` | `high` / `high` |

  `slow` is explicit escalation only. Agent models are set in
  `task.agentModelOverrides`, which beats agent frontmatter. OMP's bundled
  `scout`, `reviewer`, `security-reviewer`, `task` and `sonic` are kept, not
  shadowed: `/review` depends on bundled `reviewer`. `adversary`/`reviewer`/
  `advisor` stay on Grok so a hostile pass is a second lineage, not Claude
  reviewing Claude. Why each role sits where it does: `design/decisions.md`,
  "OMP model routing".

  Claude carries everything that does not need a second lineage (the plan is
  underused); Grok carries only review, `research` (X search) and `scout`,
  because its one weekly pool is shared with Grok Chat/Build/Bot and its size is
  unpublished. Haiku 5.5 is 100K context in omp, so it backs only short-prompt
  roles and is never a rung under Opus or Sonnet. OpenRouter
  `z-ai/glm-5.3-flash` is the metered last resort (pay per token).

  `retry.usageAwareFallback` covers both subscriptions: before each turn and at
  subagent start, a provider at or below its reserve moves to the next rung of
  its exact-model chain. Claude's reserve is the global 20%; SuperGrok's is 35%
  (`auth.accountPolicies`, keyed by xAI `accountId`) to leave headroom for the
  Grok apps. Grok is measured on "SuperGrok Weekly Credits" (monthly included
  allowance if there is no weekly one). Unknown usage fails open: xAI marking the
  quota advisory, or paid on-demand usage switched on, keeps Grok spending, so
  keep on-demand off. `openai-codex`, `opencode-go` and `muse-code` are disabled
  so no role, chain or `/model` pick reaches a dropped subscription. The one
  routing overlay, `omp/overlays/openrouter-overlay.yml`, is session-only
  (`omp --config ~/.config/omp/openrouter-overlay.yml`) for grey-area work
  Claude refuses; it disables `anthropic` and routes to OpenRouter GLM 5.3 and
  Grok 4.20 (`design/decisions.md`, "OpenRouter refusal overlay").
- `python3 scripts/check-model-routing.py` enforces routing invariants that
  used to fail silently, and diffs the table above, `pi/model-ladder.md` and
  every `<!-- routing:current -->` block against the config (format rules in
  its docstring). Fix drift in the docs, not by bending the config.
- `omp -p` from a persistent kernel needs closed stdin
  (`stdin=DEVNULL` or `</dev/null`) or it waits at `readPipedInput`.
- `omp` is the binary, not a restoring wrapper; never add persistent
  apply/restore state.
- Thinking levels are model-specific: OpenRouter `z-ai/glm-5.3*` and
  `deepseek-v4*-flash` accept only low/high/max; `xai-oauth/grok-4.7` takes
  minimal..xhigh (no `max`); Opus 5/5.5 cannot disable thinking at xhigh/max;
  `claude-haiku-5-5` takes low..max and has a 100K context in omp (the API's 1M
  is not exposed). Evidence: `docs/research/`.
- The homelab box self-updates omp daily (dotfiles' `omp-update.timer`), so
  never pin an omp version in these docs; if a probe disagrees with a note
  here, check `journalctl --user -u omp-update.service` for a version bump first.
- OMP rewrites `omp/config.yml` and strips comments; keep rationale in
  `design/decisions.md` or here, never in that file. A bare
  `omp -p --model <id>` can hide failures behind fallback; probe with retry
  disabled:
  `omp -p --model <id> --config <(printf 'retry:\n  enabled: false\n') "Reply with exactly: ok"`
- `retry.fallbackChains` specificity is exact model → provider key → role →
  default. `provider/*` is a chain key, not a rung; as a rung it preserves the
  model id and can build an invalid gateway id. OMP loads `~/.omp/.env` at
  startup and existing process variables win; after `op inject`, restart OMP.
  `omp token <provider>` shows the key actually used.
- SuperGrok (`xai-oauth`, three-month deal from 2026-10) is one weekly credit
  pool shared with Grok Chat, Build and Bot; xAI publishes no size. `omp usage
  --provider xai-oauth` shows it. It reports no `5h` window, so
  `skills/overnight-run/scripts/usage-gate.sh` cannot gate it and overnight
  workers stay on Anthropic. Before the deal ends, decide renew vs ChatGPT Plus
  (`docs/research/chatgpt-vs-supergrok-coding-2026-10.md`):

  <!-- routing:current -->
  `code-worker` → `anthropic/claude-sonnet-5-5` medium
  `research` → `xai-oauth/grok-4.7` high
  `sonic` → `anthropic/claude-haiku-5-5` medium
  <!-- routing:end -->
- Pi selects by role: `pi/extensions/model-roles` turns each
  `pi/model-roles.json` role into a virtual `role/<name>` model with its own
  fallback chain; agents in `pi/agents/*.md` still pin physical models. Routing
  prose lives in `pi/model-ladder.md`. Pi's Grok roles need `/login` → "xAI
  (Grok/X subscription)" per box (provider `xai`; Pi ≥1.1.0 lists `grok-4.7`).
- Pi reaches Claude only through the `@gotgenes/pi-anthropic-auth` extension,
  which impersonates Claude Code (Anthropic's legal page prohibits that; it has
  broken twice on Pi prompt changes). By user decision (2026-10-09,
  `design/decisions.md` "Pi Claude default") it is nevertheless Pi's default
  and a chain rung; `check-model-routing.py` allows any Claude route, `role/*`
  resolved, only while the package is in `pi/settings.json` `packages[]`.
  Evidence: `docs/research/pi-claude-subscription-2026-10.md`.
- Pi `enabledModels` is the Ctrl+P cycle list, not an access restriction. It
  deduplicates by provider/model ID, keeping the first effort preset; use
  `/thinking` or agent thinking overrides instead of duplicate entries.
  Restoring Pi's Claude path needs `/login anthropic` per box.
- Fetch before pushing. If another process advanced the branch, preserve
  unrelated dirty files, rebase, then restore them.

## Plans and docs

- Plans and runbooks live in `plans/`; the first line is exactly
  `Status: planned` or `Status: active` (add it to an OMP-autosaved plan before
  committing). A finished plan is deleted, not archived.
- `docs/` holds only `docs/research/` (dated history) and `docs/agents/`.
  Decisions go in `design/decisions.md`.

## Agent skills

- **Issue tracker:** GitHub Issues via `gh`. See `docs/agents/issue-tracker.md`.
- **Triage labels:** `needs-triage`, `needs-info`, `ready-for-agent`,
  `ready-for-human`, `wontfix`. See `docs/agents/triage-labels.md`.
- **Domain docs:** `GLOSSARY.md` (formerly `CONTEXT.md`; `git mv` an old one)
  is the domain vocabulary. `docs/adr/` is absent in this checkout.
