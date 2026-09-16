# AGENTS.md

This file applies to this checkout. Shared, harness-neutral preferences live in
`global-agents.md` and are installed into OMP and Pi; do not confuse the two.

## What this repo installs

`./install.sh` writes to exactly these destinations:

| Destination | Source | Delivery |
| --- | --- | --- |
| `~/.agents/skills/` | `skills/`, `vendor/` | one symlink per skill; filled only when a shared-root consumer exists |
| `~/.omp/agent/` + `~/.config/omp/` | `omp/`, `global-agents.md` | one symlink per file; OMP writes through links |
| `~/.pi/agent/` | `pi/`, `global-agents.md` | one symlink per file; Pi writes through links |

`pi/web-search.json` is the one **merge**, not a link: it is also
pi-web-access's credential store, so only repo-owned keys are pushed.

- Link skills **once** into `~/.agents/skills`; never also link
  `~/.pi/agent/skills` or skills are discovered twice and consume double the
  context budget. Codex and OpenCode read this shared root natively; this repo
  only checks their directories and writes no config for them.
- Edits are live through symlinks; there is no sync step. OMP and Pi can rewrite
  linked config in this checkout. **Check `git diff` before committing** after
  interactive setting changes; `pi/settings.json` and `omp/config.yml` are the
  usual suspects.
- `--prune` removes only managed links pointing into this checkout and copies
  marked `.agent-config-managed`; unmarked real files/directories are left with
  a warning.
- `--skills-only=name,other-name` links only named repo-owned skills, with no
  config writes or external fetches. It cannot be combined with `--prune`.
- Full, `--skills-only` and `--prune` runs share the
  `shared_root_consumers_present` predicate: one of `~/.omp/agent`,
  `~/.pi/agent`, `~/.codex` or `~/.config/opencode` must exist. With none,
  `~/.agents` is not created and `--prune` skips the shared root.
- `--no-external` skips external git fetches but still relinks existing clones.
- Install refuses paths matching `*/.git/worktrees/*` or `*/worktrees/*`, and
  refuses a linked `git worktree add` checkout when `rev-parse --git-dir` and
  `--git-common-dir` differ. Both guards exit 1 with `linked worktree` and are
  overridden by `--force`; symlinks contain absolute paths that would dangle.
  Git older than 2.31 falls back when `--path-format=absolute` is unavailable;
  if Git cannot answer, only the path guard remains.

## Ownership

`~/dev/agent-config` owns agent behaviour; `~/dev/dotfiles` owns the machine.
Secrets belong in dotfiles (1Password + age), never here.

| Path | Owner | Notes |
| --- | --- | --- |
| `skills/`, `plugins.txt` | agent-config | source-only; no packaged artifact |
| `global-agents.md` | agent-config | linked to `~/.omp/agent/AGENTS.md` and `~/.pi/agent/AGENTS.md` |
| `omp/config.yml`, `lsp.yml`, `keybindings.yml`, `themes/`, `agents/`, `overlays/` | agent-config | OMP writes through links |
| `pi/settings.json`, `verbosity.json`, `subagents.json`, `pi-fff.json`, `keybindings.json`, `prompts/`, `themes/`, `extensions/`, `agents/` | agent-config | Pi writes through links |
| `pi/web-search.json` | **shared** | merged; credentials and unmanaged keys stay machine-local |
| `~/.omp/agent/mcp.json`, `~/.omp/agent/extensions/`, `~/.pi/agent/auth.json`, `~/.pi/agent/models-store.json`, `~/.pi/agent/sessions/`, `~/.pi/agent/npm/` | **neither** | credentials or runtime state; untracked |
| `~/.local/bin/omp-*-overlay`, `~/.zshrc`, Brewfile, fonts | **dotfiles** | chezmoi |
| `scripts/` | agent-config | checks and installer helpers, referenced by `check.sh` |

## Skills

- Repo-owned skills are `skills/<name>/SKILL.md`; `external` lines in
  `plugins.txt` clone third-party sources into ignored `vendor/`, vendored by
  reference only. A bare external repo imports every skill and can consume the
  shared context budget; name only the skills wanted on an `external` line.
- Skill `name` must equal its directory, be lowercase kebab-case, and contain
  neither `claude` nor `anthropic`. Multi-line descriptions require `|` or `>-`;
  an unquoted colon-space can parse as a nested mapping and break loading.
- `python3 scripts/lint-skills.py` enforces these rules and synchronizes the
  `skills/README.md` list, including its sentence stating the count of 35
  repo-owned skills. `python3 scripts/check-manifest.py` (run by `check.sh`)
  rejects malformed `plugins.txt` lines and duplicate external allowlisting;
  `scripts/manifest.py` is the shared parser.
- `scripts/ownership_collisions.py` (tested by `check.sh`) detects chezmoi
  entries claiming install destinations.
- `python3 scripts/audit-local.py [--home DIR] [--dotfiles DIR] [--json]` is an
  opt-in, read-only, offline local drift audit; it exits 0 with findings and is
  not run by `check.sh`.
- Never `npx skills add`: its machine-local `~/.agents/.skill-lock.json` has no
  restore command and is invisible to this repo. Every `~/.agents/skills/*`
  entry must be a symlink; audit with:
  `for d in ~/.agents/skills/*/; do [ -L "${d%/}" ] || echo "${d%/}"; done`
- `codebase-memory` is repo-owned in `skills/codebase-memory/`; its MCP server
  is separate and does not supply the skill.

## Gotchas

- `pi-playwright`'s `pw.js` expects an uninstalled package-local CLI. Use the
  hoisted `~/.pi/agent/npm/node_modules/.bin/playwright-cli` with
  `--browser=chromium`; do not assume system Chrome.
- macOS has no GNU `timeout`; use Python `subprocess.run(..., timeout=...)` or a
  background process plus `kill`.
- The repo-local `.githooks/pre-commit` runs fast checks; `scripts/check.sh` runs
  the full set. After commits, inspect `git status` for unrelated changes.
- **Plain OMP routing is authoritative in `omp/config.yml`:**

  | Roles/settings | Value |
  | --- | --- |
  | `default` role | `anthropic/claude-opus-5:medium` |
  | `plan`/`designer`/`vision` roles; `plan` agent | `anthropic/claude-opus-5:high` |
  | `critic` agent | `anthropic/claude-opus-5:medium` |
  | `slow` role | `anthropic/claude-opus-5:xhigh` (explicit escalation only) |
  | `security-reviewer` role and agent | `anthropic/claude-opus-5:high` |
  | `builder` agent | `anthropic/claude-sonnet-5:high` |
  | `task` role and agent; `workflow` agent | `anthropic/claude-sonnet-5:medium` |
  | `code-worker`/`sonic` agents | `opencode-go/deepseek-v4.1-flash:high` |
  | `smol`/`tiny`/`commit` roles | `opencode-go/glm-5.3-flash:low` |
  | `adversary`/`reviewer`/`advisor` | `opencode-go/glm-5.3-flash:high` |
  | `scout` agent | `opencode-go/glm-5.3-flash:low` |
  | `research` agent | `opencode-go/muse-spark-1.3-contributor:high` |
  | `disabledProviders` | `[openai-codex]` |
  | `usageAwareFallback` / `usageReservePct` / policy | `true` / `20` / `auto` |
  | `task.maxEffort` / `providers.autoThinkingMaxEffort` | `high` / `high` |

  Agent models are set in `task.agentModelOverrides`, which beats agent
  frontmatter; each overlay must override every agent too, or a base
  `anthropic` pin leaks into `ompgo`. OMP's bundled `scout`, `reviewer`,
  `security-reviewer`, `task` and `sonic` are kept, not shadowed: `/review`
  depends on bundled `reviewer`. Pi `Explore`/`public-scout` map to OMP
  `scout`, Pi `reviewer` to `adversary`, Pi `general-purpose` to `task`.
  `adversary`/`reviewer`/`advisor` stay on GLM so a hostile pass is a second
  lineage, not Claude reviewing Claude; `scout` stays on GLM to spend flat-rate
  Go tokens on discovery instead of subscription allowance.
  Claude load is deliberately bounded: `thinkingBudgets` maps `medium` to 8192
  reasoning tokens against `high`'s 16384 and `xhigh`'s 32768, so the main
  session (`default`) runs Opus 5 at `medium` and only the roles that judge
  pixels or plan a screen pay `high`. Housekeeping roles (`smol`, `tiny`,
  `commit`), mechanical agents (`sonic`) and bounded implementation
  (`code-worker`) run on flat-rate Go instead of plan usage — spread across two
  $60/month caps (GLM for housekeeping and discovery, DeepSeek for
  implementation). `code-worker` must not run on `muse-spark-*-contributor`:
  it edits private source and Meta trains on contributor prompts.
  `retry.usageAwareFallback` preflights the coding-plan usage report and, at
  20% remaining, shifts to the configured Go rung without asking; an unmapped
  usage report fails open, so it is a backstop, not a guarantee.

  Overlays differ. `omp -p` from a persistent kernel needs closed stdin
  (`stdin=DEVNULL` or `</dev/null`) or it waits at `readPipedInput`.
- `omp` is the binary, not a restoring wrapper; pass overlays per session with
  `--config`, never add persistent apply/restore state. Thinking levels are
  model-specific: `glm-5.3-flash` and `kimi-k3` accept only low/high/max;
  `deepseek-v4-flash`/`v4.1-flash` accept low/high/max (minimal→low,
  medium/xhigh→high). `claude-opus-5`/`claude-sonnet-5`/`claude-fable-5-1` use
  adaptive thinking (default `high`) over low/medium/high/xhigh/max, and Opus 5
  cannot disable thinking at xhigh/max. `claude-haiku-4-5` has no effort
  parameter at all — it uses manual extended thinking, and OMP's `:low`
  selector is accepted (probed). `minimal` is not a real level on the Go
  models. Evidence: `docs/research/`.
- Routing rationale (2026-09-16, `docs/research/*-2026-09.md`): the ladder ran
  on `openai-codex` until that subscription was dropped over frontend quality —
  Luna sits at DesignArena rank 48 overall (1242), the weakest routed model on
  every board. Claude Opus 5 is rank 8 (1338), above GPT-5.6 Sol medium (1334),
  and it wins DesignArena UI Components outright (#5, 1361, ahead of Fable 5.1
  at #12), so it takes `default` and the roles that *decide* or *judge* visual
  work (`plan`, `designer`, `vision`, `critic`). Claude
  Fable 5.1 is rank 6 overall and #2 on LMArena WebDev, but on Max-class plans
  Fable burns regular weekly limits at roughly double rate and is capped at 50%
  of them before it needs usage credits — on Pro-class plans it is
  credits-only from the first message. So Fable stays manual `/model`
  escalation, never a role pin. Sonnet 5 ($2/$10, AA index 38 vs Opus 5's 51)
  carries `task`, `workflow` and `builder`: `builder` implements a plan that
  `plan`/`designer` already fixed, so Sonnet 5's weaker from-scratch design
  standing (DesignArena task boards ranks 22-37) costs little, and it runs at
  `high` effort to keep implementation accuracy. Haiku
  4.5 is no longer pinned to a role: per-turn housekeeping (`smol`, `tiny`,
  `commit`) went to GLM 5.3 Flash, and `code-worker`/`sonic` to DeepSeek V4.1
  Flash (AA 40 vs Sonnet 5's 38), because flat-rate Go tokens are the cheaper
  place for bounded, pre-decided work. Haiku stays a fallback rung only.
  `scout` reads private code, so it stays off `muse-spark-*-contributor` (Meta
  trains on contributor prompts). DeepSeek V4.1 Flash's $60 Go cap is a promo
  ending 2026-09-20 (then $15, i.e. $3 per 5 hours); if `code-worker` throttles
  after that, move it to `opencode-go/glm-5.3-flash:high` or back to
  `anthropic/claude-sonnet-5:medium`.
  Anthropic publishes no per-model weekly message counts, so subscription
  burn rate per role is not predictable from primary docs.
- `openai-codex` is in the base `disabledProviders`, so no role, chain or
  `/model` pick in a **plain** session reaches the lapsing ChatGPT account.
  An overlay **replaces** that list rather than merging into it: probed
  2026-09-16, `omp -p --config omp/overlays/codex-only-overlay.yml` still ran
  `openai-codex/gpt-5.6-terra`. So `ompcodex` keeps working for as long as the
  credential does; retiring it needs the dotfiles-side `ompcodex` function and
  `~/.local/bin/omp-*-overlay` entry to go, which is a cross-repo change this
  repo does not make unilaterally.
- `python3 scripts/check-model-routing.py` (in `check.sh` and the pre-commit
  fast set) enforces the routing invariants, all of which failed silently
  before: a repo-owned `omp/agents/*.md` `model:` — literal or `@role` — must
  resolve to that agent's base `task.agentModelOverrides` value; every
  override key must name a real agent (repo file or one of OMP's bundled
  `task`/`scout`/`sonic`/`reviewer`/`security-reviewer`); every overlay must
  re-pin every base role and agent key; every selector must parse as
  `provider/model[:effort]` and must not name a provider the same file
  disables; and no `pi/agents/*.md`, `pi/settings.json` or
  `pi/web-search.json` entry may use `anthropic/*` or `openrouter/*`, which
  Pi cannot reach. Tests: `scripts/test-check-model-routing.py`.
- OMP rewrites `omp/config.yml` and removes comments while preserving values;
  keep rationale in `design/decisions.md` or here, never in that file. A bare
  `omp -p --model <id>` can hide failures behind fallback; probe with retry
  disabled:
  `omp -p --model <id> --config <(printf 'retry:\n  enabled: false\n') "Reply with exactly: ok"`
- `retry.fallbackChains` specificity is exact model → provider key → role →
  default. `provider/*` is a chain key, not a rung; as a rung it preserves the
  model id and can build an invalid gateway id. OMP loads `~/.omp/.env` at
  startup and existing process variables win; after `op inject`, restart OMP.
  `omp token <provider>` shows the key actually used.
- Muse Spark requires `/v1/responses` and omp ≥18.1.6; installed omp is 18.1.21.
  Pi's catalogue uses `api: openai-responses` at
  `https://opencode.ai/zen/go/v1`. Plain OMP uses Muse Spark only for the
  `research` agent; `omp/overlays/go-overlay.yml` uses it more.
- Pi has no OMP-style `modelRoles` or `fallbackChains`; per-job models are in
  `pi/agents/*.md` frontmatter. Pi runs entirely on OpenCode Go; default is
  `opencode-go/deepseek-v4.1-flash` high. Routing: main, Plan, workflow,
  code-worker and general-purpose → DeepSeek V4.1 Flash high; builder and
  Critic → Kimi K3 high (DesignArena rank 1, but the lowest Go cap at $15/mo,
  ~490 requests — fall back to DeepSeek, never to a Luna-class model);
  scout/Explore → GLM 5.3 Flash low; reviewer → GLM 5.3 Flash high as the
  second lineage; research and public-scout → Muse Spark 1.3 (public material
  only). Full table and the Claude-restoration options: `pi/model-ladder.md`.
- Pi cannot reach Claude. The Anthropic subscription rejects third-party
  clients with HTTP 400 "Third-party apps now draw from your extra usage"
  (`earendil-works/pi#3372`) and the stored OpenRouter key answers HTTP 401
  "User not found". OMP is the Claude harness; Pi is the flat-rate harness.
  Restoring a Pi path needs extra usage credits or a live OpenRouter key, both
  machine-local spend. Probes:
  `docs/research/harness-provider-access-2026-09.md`.
- Pi `enabledModels` is the Ctrl+P cycle list, not an access restriction. It
  deduplicates by provider/model ID, retaining the first effort preset; use
  `/thinking` or explicit agent thinking overrides instead of duplicate entries.
  OpenCode Go/OpenRouter credentials are API keys in untracked
  `~/.pi/agent/auth.json`; `openai-codex` and `anthropic` use OAuth.
- Fetch before pushing. If another process advanced the branch, preserve
  unrelated dirty files, rebase, then restore them.
- `scripts/check.sh` bootstraps ignored `node_modules/` with `npm ci` when
  `node_modules/@earendil-works/pi-tui` is missing; it carries `pi-token-speed`,
  consumed by `pi/settings.json`. Never commit `node_modules/`.

## Agent skills

### Issue tracker

Issues live in GitHub Issues and use the `gh` CLI. See `docs/agents/issue-tracker.md`.

### Triage labels

Use `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, and
`wontfix`. See `docs/agents/triage-labels.md`.

### Domain docs

The previously documented root `CONTEXT.md` and `docs/adr/` are absent in this
checkout; do not assume they exist.
