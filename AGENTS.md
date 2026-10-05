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
`OpenRouter API Key - omp.sh`) so each is billed separately. `~/.omp/.env` is
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
  OpenCode Go and Muse Code, `claude-compact-openrouter` sends transcripts to
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
  | `task` role; `task`/`workflow` agents | `anthropic/claude-sonnet-5-5:medium` |
  | `code-worker` agent | `muse-code/muse-spark-1.3-contributor:high` |
  | `sonic` agent | `muse-code/muse-spark-1.3-contributor:low` |
  | `smol`/`tiny`/`commit` roles | `opencode-go/glm-5.3-flash:low` |
  | `adversary`/`reviewer`/`advisor` roles; `adversary`/`reviewer` agents | `opencode-go/glm-5.3-flash:high` |
  | `scout` agent | `opencode-go/glm-5.3-flash:low` |
  | `research` agent | `muse-code/muse-spark-1.3-contributor:high` |
  | `disabledProviders` | `[openai-codex]` |
  | `retry.usageAwareFallback` / `retry.usageReservePct` / `retry.usageReservePolicy` | `true` / `20` / `auto` |
  | `task.maxEffort` / `providers.autoThinkingMaxEffort` | `high` / `high` |

  `slow` is explicit escalation only. Agent models are set in
  `task.agentModelOverrides`, which beats agent frontmatter. OMP's bundled
  `scout`, `reviewer`, `security-reviewer`, `task` and `sonic` are kept, not
  shadowed: `/review` depends on bundled `reviewer`. `adversary`/`reviewer`/
  `advisor` stay on GLM so a hostile pass is a second lineage, not Claude
  reviewing Claude. Why each role sits where it does: `design/decisions.md`,
  "OMP model routing".

  `code-worker`, `sonic` and `research` on `muse-spark-*-contributor` means
  Meta may train on their prompts, including repository source (allowed by user
  decision 2026-09-18; `docs/research/muse-code-subscription-2026-09.md`).
  Route a session that touches client or sensitive material away from those
  agents, or pin `muse-code/muse-spark-1.3` (standard tier, not trained on,
  ~12.5x the quota burn).

  `retry.usageAwareFallback` shifts to the Go rung at 20% coding-plan usage
  remaining; an unmapped usage report fails open, so it is a backstop, not a
  guarantee. `openai-codex` is disabled so no plain-session role, chain or
  `/model` pick reaches the lapsing ChatGPT account; there are no routing
  overlays (`omp/overlays/` holds only `search-keys.tpl`).
- `python3 scripts/check-model-routing.py` enforces routing invariants that
  used to fail silently, and diffs the table above, `pi/model-ladder.md` and
  every `<!-- routing:current -->` block against the config (format rules in
  its docstring). Fix drift in the docs, not by bending the config.
- `omp -p` from a persistent kernel needs closed stdin
  (`stdin=DEVNULL` or `</dev/null`) or it waits at `readPipedInput`.
- `omp` is the binary, not a restoring wrapper; never add persistent
  apply/restore state.
- Thinking levels are model-specific: the Go models (`glm-5.3-flash`,
  `kimi-k3`, `deepseek-v4*-flash`) accept only low/high/max; Opus 5/5.5 cannot
  disable thinking at xhigh/max; `claude-haiku-4-5` has no effort parameter
  (OMP's `:low` is accepted); `muse-spark-1.3-contributor` has no `max`.
  Evidence: `docs/research/`.
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
- Muse Spark requires omp ≥18.1.6. `muse-code` (subscription;
  `omp usage -p muse-code`) and `opencode-go` (shared Go cap) both serve it and
  meter separately; plain OMP uses only `muse-code`:

  <!-- routing:current -->
  `code-worker` and `research` → `muse-code/muse-spark-1.3-contributor` high
  `sonic` → `muse-code/muse-spark-1.3-contributor` low
  <!-- routing:end -->
- Pi has no `modelRoles` or `fallbackChains`; per-job models are in
  `pi/agents/*.md` frontmatter, and the routing lives in `pi/model-ladder.md`.
  Pi defaults to Muse, Meta's training-eligible tier: any session touching
  private or sensitive material must be rerouted to GLM/DeepSeek.
- Pi reaches Claude only through the `@gotgenes/pi-anthropic-auth` extension,
  which impersonates Claude Code (Anthropic's legal page prohibits that; it has
  broken twice on Pi prompt changes). **Never make it the default or a
  fallback**; `check-model-routing.py` allows an explicit agent pin only while
  the package is in `pi/settings.json` `packages[]`. OMP remains the Claude
  harness. Evidence: `docs/research/pi-claude-subscription-2026-10.md`.
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
