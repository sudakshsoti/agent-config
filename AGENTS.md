# AGENTS.md

This file applies to this checkout. Shared, harness-neutral preferences live in
`global-agents.md` and are installed into OMP and Pi; do not confuse the two.

## What this repo installs

`./install.sh` writes to exactly these destinations:

| Destination | Source | Delivery |
| --- | --- | --- |
| `~/.agents/skills/` | `skills/`, `vendor/` | one symlink per skill; filled only when a shared-root consumer exists |
| `~/.claude/skills/` | `skills/`, `vendor/` | one symlink per skill; filled only when `~/.claude` already exists |
| `~/.claude/` config | `claude/`, `snapshots/claude/mcp.json` | statusline pair + `claude-powerline.json` linked (identical real copies adopted); `settings.json` **merged**; plugins via `claude/plugins.txt` (skipped by `--no-external`); MCP servers added if missing. Only when `~/.claude` exists; run `claude` once on a new box first |
| `~/.omp/agent/` + `~/.config/omp/` | `omp/`, `global-agents.md` | one symlink per file; OMP writes through links |
| `~/.omp/agent/` extras | `omp/plugins.txt`, `snapshots/omp/mcp.json` | `omp plugin install` (skipped by `--no-external`; needs bun); MCP servers added to `mcp.json` if missing, never edited |
| `~/.pi/agent/` | `pi/`, `global-agents.md` | one symlink per file; Pi writes through links |
| `~/.config/herdr/config.toml` | `herdr/config.toml` | one symlink; herdr writes through it; only when `~/.config/herdr` exists. `herdr/plugins.txt` entries go through `herdr plugin install` (skipped by `--no-external`); `herdr/<dir>/herdr-plugin.toml` local plugins are `herdr plugin link`ed (`herdr/marksman-root` drops `.marksman.toml` into linked worktrees, since Marksman rejects a `.git` file) |

`pi/web-search.json` and `claude/settings.json` are **merges**, not links
(`scripts/apply-json-config.py`): the first is pi-web-access's credential
store, the second is written by Claude Code, carries herdr's `hooks` entry and
holds `OPENROUTER_API_KEY` for the Jev compaction plugin. Only repo-owned keys
are pushed. The key is never tracked: install copies `JEV_OPENROUTER_API_KEY`
(item `OpenRouter API Key - Jev`) from `~/.omp/.env` into the live `env` as
`OPENROUTER_API_KEY`, kept apart from OMP's own `OPENROUTER_API_KEY` (item
`OpenRouter API Key - omp.sh`) so each is billed separately. `~/.omp/.env` is
1Password-injected from `omp/overlays/search-keys.tpl`, so run `op inject`
before installing on a new box; on the homelab box use the read-only
service-account token (see `global-agents.md`). The tracked file is checked
for credential-shaped keys.

- Link skills **once** into `~/.agents/skills`; never also link
  `~/.pi/agent/skills` or skills are discovered twice and consume double the
  context budget. Codex and OpenCode read this shared root natively; this repo
  only checks their directories and writes no config for them.
- **Claude Code is the one exception**, because it does not read the shared
  root at all: the same declared set is linked a second time into
  `~/.claude/skills`. That is not double discovery, because no harness reads
  both roots — but it only stays true while `omp/config.yml` pins
  `skills.enableClaudeUser: false`. OMP scans `~/.claude/skills` by default;
  drop that pin and every skill is discovered twice in OMP. The pin is the
  load-bearing half of this arrangement, not a stylistic preference.
  `install.sh` never creates `~/.claude`, so a machine without Claude Code is
  untouched. `~/.claude/CLAUDE.md`, `hooks/` (herdr writes it), `agents/` and
  `~/.claude.json` stay out of scope; `--prune` still treats `CLAUDE.md` and
  `~/.claude/agents` as retired surfaces.
- `--skills-only` fills the shared root **only**, never `~/.claude/skills`;
  it is a shared-root operation by definition. A selective run therefore does
  not keep Claude Code in sync — use a full `./install.sh` for that.
- **Work machine gate.** When `chezmoi data` reports `.machine` = `work`,
  install links skills only and skips every OMP, Pi and Claude config step
  (`global-agents.md`, `omp/`, overlays, `pi/`, `web-search.json`,
  `claude/`, plugins, MCP seeding). Their model routing sends prompts and
  repository source to OpenCode Go and Muse Code, `claude-compact-openrouter`
  sends transcripts to Jev via OpenRouter, and employer code may only reach the
  employer's sanctioned vendor. Dotfiles
  owns the profile; this repo only reads it. With no chezmoi or no profile the
  machine counts as unknown and installs as before, so apply dotfiles first.
  Claude.ai connectors (Gmail, Todoist, Notion) belong to the claude.ai account,
  not this repo, and are not gated here.
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
| `skills/`, `plugins.txt` | agent-config | source; only `distribution.txt` skills are also packaged |
| `distribution.txt`, `dist/*.zip` | agent-config | list of claude.ai skills; zips are generated, never hand-edited |
| `global-agents.md` | agent-config | linked to `~/.omp/agent/AGENTS.md` and `~/.pi/agent/AGENTS.md` |
| `omp/config.yml`, `lsp.yml`, `keybindings.yml`, `themes/`, `agents/`, `commands/`, `overlays/` | agent-config | OMP writes through links; `commands/*.md` are `/name` wrappers over same-named skills |
| `pi/settings.json`, `verbosity.json`, `subagents.json`, `pi-fff.json`, `keybindings.json`, `prompts/`, `themes/`, `extensions/`, `agents/` | agent-config | Pi writes through links |
| `herdr/config.toml`, `herdr/plugins.txt` | agent-config | keybindings and pinned plugins; plugin state under `~/.config/herdr/plugins/` is untracked |
| `pi/web-search.json` | **shared** | merged; credentials and unmanaged keys stay machine-local |
| `claude/settings.json`, `statusline.sh`, `subagent-statusline.sh`, `claude-powerline.json`, `plugins.txt` | agent-config / **shared** (settings) | settings merged; the rest linked or declarative |
| `omp/plugins.txt`, `snapshots/*/mcp.json` | agent-config | declared sets, add-only; snapshots refreshed from live by `scripts/snapshot-machine-config.sh` |
| `~/.omp/agent/mcp.json`, `~/.omp/agent/extensions/`, `~/.omp/agent/agent.db` (logins), `~/.claude.json`, `~/.claude/plugins/`, `~/.claude/hooks/`, `~/.pi/agent/auth.json`, `~/.pi/agent/models-store.json`, `~/.pi/agent/sessions/`, `~/.pi/agent/npm/` | **neither** | credentials or runtime state; untracked. Logins (`/login`, `claude`) are per box |
| `~/.local/bin/omp-*-overlay`, `~/.zshrc`, Brewfile, fonts | **dotfiles** | chezmoi |
| `scripts/` | agent-config | checks and installer helpers, referenced by `check.sh` |

## Skills

- Repo-owned skills are `skills/<name>/SKILL.md`; `external` lines in
  `plugins.txt` clone third-party sources into ignored `vendor/`, vendored by
  reference only. A bare external repo imports every skill and can consume the
  shared context budget; name only the skills wanted on an `external` line.
  Name collisions resolve by fixed precedence: repo-owned `skills/<name>` beats
  every external source; an `external` line naming the skill beats a bare line;
  among lines of the same kind the earliest one in `plugins.txt` wins. Losers are
  skipped with a `SKIP … shadowed by` warning, not an error.
- Skill `name` must equal its directory, be lowercase kebab-case, and contain
  neither `claude` nor `anthropic`. Multi-line descriptions require `|` or `>-`;
  an unquoted colon-space can parse as a nested mapping and break loading.
- `python3 scripts/lint-skills.py` enforces these rules and synchronizes the
  `skills/README.md` list, including its sentence stating the count of 35
  repo-owned skills. It also fails on dangling references in
  `SKILL.md` and `references/*.md`: links or `references/`, `scripts/`, `skills/`
  paths that do not resolve, and skill names in hand-off contexts or a
  description's "Not for … (x)" clause that are not repo-owned, named on a
  `plugins.txt` `external` line, cloned under `vendor/`, or in the script's
  `EXTERNAL_ALLOWLIST` (skills of bare `external` sources). `python3 scripts/check-manifest.py` (run by `check.sh`)
  rejects malformed `plugins.txt` lines and duplicate external allowlisting;
  `scripts/manifest.py` is the shared parser.
- `distribution.txt` lists the skills shipped to claude.ai as `dist/<name>.zip`
  by `scripts/build-dist.py`. The packaged `SKILL.md` drops frontmatter keys
  claude.ai rejects (e.g. `disable-model-invocation`) and is validated against
  the upload rules. The pre-commit hook rebuilds from the staged tree and stages
  `dist/`; `check.sh` runs `--check`. List only skills that work without a
  local harness: `research` and `design-grill` are excluded because they rely
  on Pi/OMP subagents, repo files or an unshipped skill.
- `distribution-vendor.txt` does the same for vendored third-party skills,
  resolved from `vendor/` via `plugins.txt`. A working-tree
  `./scripts/build-dist.py` writes them to `dist/vendor/`, which is gitignored
  (third-party content never enters this history); `--check` and `--from-index`
  ignore them, so rebuild per machine after `./install.sh`. Everything
  vendored is listed except `firecrawl-web` and `frontend-design`.
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
  | `default` role | `anthropic/claude-opus-5-5:medium` |
  | `plan`/`designer`/`vision` roles; `plan` agent | `anthropic/claude-opus-5-5:high` |
  | `critic` agent | `anthropic/claude-opus-5-5:medium` |
  | `slow` role | `anthropic/claude-opus-5-5:xhigh` (explicit escalation only) |
  | `security-reviewer` role and agent | `anthropic/claude-opus-5-5:high` |
  | `builder` agent | `anthropic/claude-sonnet-5-5:medium` |
  | `task` role and agent; `workflow` agent | `anthropic/claude-sonnet-5-5:medium` |
  | `code-worker`/`sonic` agents | `muse-code/muse-spark-1.3-contributor:high` / `:low` |
  | `smol`/`tiny`/`commit` roles | `opencode-go/glm-5.3-flash:low` |
  | `adversary`/`reviewer`/`advisor` | `opencode-go/glm-5.3-flash:high` |
  | `scout` agent | `opencode-go/glm-5.3-flash:low` |
  | `research` agent | `muse-code/muse-spark-1.3-contributor:high` |
  | `disabledProviders` | `[openai-codex]` |
  | `usageAwareFallback` / `usageReservePct` / policy | `true` / `20` / `auto` |
  | `task.maxEffort` / `providers.autoThinkingMaxEffort` | `high` / `high` |

  Agent models are set in `task.agentModelOverrides`, which beats agent
  frontmatter. OMP's bundled `scout`, `reviewer`,
  `security-reviewer`, `task` and `sonic` are kept, not shadowed: `/review`
  depends on bundled `reviewer`. Pi `Explore`/`public-scout` map to OMP
  `scout`, Pi `reviewer` to `adversary`, Pi `general-purpose` to `task`.
  `adversary`/`reviewer`/`advisor` stay on GLM so a hostile pass is a second
  lineage, not Claude reviewing Claude; `scout` stays on GLM to spend flat-rate
  Go tokens on discovery instead of subscription allowance.
  Claude load is deliberately bounded: `thinkingBudgets` maps `medium` to 8192
  reasoning tokens against `high`'s 16384 and `xhigh`'s 32768, so the main
  session (`default`) runs Opus 5.5 at `medium` and only the roles that judge
  pixels or plan a screen pay `high`. Housekeeping roles (`smol`, `tiny`,
  `commit`), discovery (`scout`) and the `adversary`/`reviewer`/`advisor` pass
  run on flat-rate Go ($60/month GLM cap) instead of plan usage, while
  mechanical agents (`sonic`) and bounded implementation (`code-worker`) run on
  the $5/month Muse Code Everyday Usage subscription. The split is deliberate:
  Muse and Go are separate quota pools, so exhausting one never stalls commits,
  discovery or review. `code-worker`, `sonic` and `research` on
  `muse-spark-*-contributor` means Meta may train on their prompts, including
  repository source; the earlier prohibition was lifted by user decision on
  2026-09-18 (evidence and scope:
  `docs/research/muse-code-subscription-2026-09.md`). Route a session that
  touches client or sensitive material away from those agents, or pin
  `muse-code/muse-spark-1.3` (standard tier, not trained on, ~12.5x the quota
  burn).
  `retry.usageAwareFallback` preflights the coding-plan usage report and, at
  20% remaining, shifts to the configured Go rung without asking; an unmapped
  usage report fails open, so it is a backstop, not a guarantee.

  `omp -p` from a persistent kernel needs closed stdin
  (`stdin=DEVNULL` or `</dev/null`) or it waits at `readPipedInput`.
- `omp` is the binary, not a restoring wrapper; never add persistent
  apply/restore state. Thinking levels are
  model-specific: `glm-5.3-flash` and `kimi-k3` accept only low/high/max;
  `deepseek-v4-flash`/`v4.1-flash` accept low/high/max (minimal→low,
  medium/xhigh→high). `claude-opus-5-5`/`claude-opus-5`/`claude-sonnet-5-5`/
  `claude-fable-5-1` use adaptive thinking (default `high`) over
  low/medium/high/xhigh/max, and Opus 5/5.5 cannot disable thinking at
  xhigh/max. `claude-haiku-4-5` has no effort
  parameter at all — it uses manual extended thinking, and OMP's `:low`
  selector is accepted (probed). `minimal` is not a real level on the Go
  models. `muse-spark-1.3-contributor` accepts minimal through xhigh (no
  `max`); standard `muse-spark-1.3` adds `max`. Evidence: `docs/research/`.
- On the homelab box the omp binary self-updates: an `omp-update.timer` user
  unit runs `omp update` (stable channel) daily at 04:30 ± 30min jitter. The
  unit is **machine state owned by dotfiles**
  (`dot_config/systemd/user/omp-update.{service,timer}`, Linux-gated in
  `.chezmoiignore`); this list documents the behaviour, not the file, and the
  Macs deliberately have no such job. Consequences: never pin an omp version in
  these docs, and if a routing or thinking-level probe suddenly disagrees with a
  note here, check `journalctl --user -u omp-update.service` for a version bump
  before assuming the note was wrong. Pause it with
  `systemctl --user disable --now omp-update.timer`.
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
  standing (DesignArena task boards ranks 22-37) costs little. It ran at
  `high` effort until 2026-09-28, when it dropped to `medium` (user decision)
  alongside `task` and `workflow`. Haiku
  4.5 is no longer pinned to a role: per-turn housekeeping (`smol`, `tiny`,
  `commit`) went to GLM 5.3 Flash, and `code-worker`/`sonic` to Muse Spark 1.3
  Contributor (AA 48 vs DeepSeek V4.1 Flash's 40 and Sonnet 5's 38), because
  pre-decided work belongs on the cheapest adequate quota. Haiku stays a
  fallback rung only. `scout` stays on GLM: it is the highest-frequency agent
  and Go's flat rate absorbs discovery without touching either subscription.
  DeepSeek V4.1 Flash's $60 Go cap is a promo ending 2026-09-20 (then $15,
  i.e. $3 per 5 hours), which is why `code-worker` left it on 2026-09-18; it
  remains the second rung under Muse and the manual throttle fallback.
  Anthropic publishes no per-model weekly message counts, so subscription
  burn rate per role is not predictable from primary docs.
  The Opus rung moved from `claude-opus-5` to `claude-opus-5-5` on 2026-09-23
  (user request, successor swap only): same provider, same 1M/128K limits and
  the same low/medium/high/xhigh/max effort set per `omp models`, and
  `anthropic/claude-opus-5-5` answered a retry-disabled `omp -p` probe. The
  benchmark figures above are the 2026-09-16 Opus 5 evidence and have not been
  re-measured for 5.5; the role split they justify is unchanged.
  The `opencode-go/glm-5.3-flash` fallback chain gained
  `opencode-go/mimo-v2.6-pro:high` as its first rung on 2026-10-02 (user
  decision), ahead of `deepseek-v4.1-flash:max`. Artificial Analysis v4.3.2
  per-benchmark data: hallucination rate GLM-5.3-Flash 27.6%, MiMo-V2.6-Pro
  40.6%, MiMo-V2.6-Flash 54.4%, DeepSeek V4.1 Flash (max) 96.5%; Terminal-Bench
  4.0 34.8 / 32.8 / 22.7 / 26.8. Review roles therefore fall back to the
  lower-hallucination model, not DeepSeek. MiMo-V2.6-Pro's Go cap is $15/month,
  so DeepSeek stays as the next rung. Chains match by exact model, so scout,
  smol and commit traffic also lands on MiMo-Pro `:high` during a GLM outage.
  No role was moved to MiMo: Pro's +4 index lead over GLM comes mostly from
  HLE/CritPt, the Terminal-Bench gap is within noise, and Pro hallucinates more.
  The same chain gained `openrouter/deepseek/deepseek-v4.1-flash:high` between
  `deepseek-v4.1-flash:max` and the Sonnet rung on 2026-10-04 (user decision):
  all three Go rungs share one provider, so the OpenRouter rung keeps review
  cross-lineage through a Go outage, and OpenRouter per-token billing (the
  `omp.sh` key) during that outage is accepted. The model answered a
  retry-disabled probe; Sonnet stays last so scout, smol and commit traffic
  still runs if Go and OpenRouter are both down.
- `openai-codex` is in the base `disabledProviders`, so no role, chain or
  `/model` pick in a **plain** session reaches the lapsing ChatGPT account.
  There are no routing overlays: `omp/overlays/` holds only `search-keys.tpl`.
- `python3 scripts/check-model-routing.py` (in `check.sh` and the pre-commit
  fast set) enforces the routing invariants, all of which failed silently
  before: a repo-owned `omp/agents/*.md` `model:` — literal or `@role` — must
  resolve to that agent's base `task.agentModelOverrides` value; every
  override key must name a real agent (repo file or one of OMP's bundled
  `task`/`scout`/`sonic`/`reviewer`/`security-reviewer`); every selector must parse as
  `provider/model[:effort]` and must not name a provider the same file
  disables; and no `pi/agents/*.md`, `pi/settings.json` or
  `pi/web-search.json` entry may use `openrouter/*`, which Pi cannot reach.
  `anthropic/*` is conditional: an explicit agent pin passes only while
  `@gotgenes/pi-anthropic-auth` is in `pi/settings.json` `packages[]`, and Claude is always rejected as
  a Pi default, cycle entry or summary model. Tests:
  `scripts/test-check-model-routing.py`.
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
- Muse Spark requires `/v1/responses` and omp ≥18.1.6; check the installed
  build with `omp --version` rather than trusting a version pinned in docs.
  Two providers serve it and they meter separately: `muse-code` is the
  OAuth-logged Muse Code subscription ($5/month Everyday Usage, 5-hour and
  weekly windows, both visible in `omp usage -p muse-code`), and `opencode-go`
  serves it over `https://opencode.ai/zen/go/v1` against the shared Go cap.
  Plain OMP routes `code-worker`, `sonic` and `research` to `muse-code`; no
  role or agent uses `opencode-go/muse-spark-*` any more. The Muse window is
  cost-weighted, not prompt-counted: a full `code-worker`-shaped turn (two
  edits plus test runs) measured under 1% of the 5-hour window on the
  contributor tier, while a one-token standard-tier prompt measured 1%
  (`docs/research/muse-code-subscription-2026-09.md`).
- Pi has no OMP-style `modelRoles` or `fallbackChains`; per-job models are in
  `pi/agents/*.md` frontmatter. Pi runs on OpenCode Go by default; default is
  `opencode-go/muse-spark-1.3-contributor` xhigh. Routing: main and builder →
  Muse Spark 1.3 Contributor xhigh; Plan, workflow, code-worker and
  general-purpose → Muse Spark high; scout/Explore → Muse Spark minimal;
  reviewer and Critic → GLM 5.3 Flash high (second lineage); research and
  public-scout → Muse Spark (public or user-approved disposable material only);
  Kimi K3 not routed (scarcest Go cap, user cost decision); DeepSeek V4.1 Flash
  is the manual throttle fallback via Ctrl+P. Muse is Meta's training-eligible
  tier: any session touching private or sensitive material must be rerouted to
  GLM/DeepSeek. Claude is now reachable from Pi through the
  `@gotgenes/pi-anthropic-auth` shim, but only as an explicit agent pin — see
  the entry below. Full table: `pi/model-ladder.md`.
- Pi reaches Claude only through the `@gotgenes/pi-anthropic-auth` extension
  (installed 2026-10-02), which de-fingerprints Pi's system prompt and injects
  Claude Code's billing header. Without it the subscription rejects third-party
  clients with HTTP 400 "Third-party apps now draw from your extra usage"
  (`earendil-works/pi#3372`, which Pi's maintainer closed as a ToS violation he
  would not work around). The extension is a deliberate dependency on
  untrusted upstream behaviour: it impersonates Claude Code, Anthropic's legal
  page prohibits that, and it has already broken twice on Pi prompt changes
  (0.86.0 restructure, `pi#9838`). **Never make it the default or a fallback** —
  `check-model-routing.py` allows an explicit agent pin only while the package
  is declared in `pi/settings.json` `packages[]` (not read from `~/.pi`, so CI
  agrees with the box), and rejects `anthropic` as `defaultProvider`, in
  `enabledModels`, and as `summaryModel`. OMP remains the Claude harness on the
  subscription proper; Pi is still the flat-rate harness by default. The
  OpenRouter key stays dead (HTTP 401 "User not found"). Evidence:
  `docs/research/pi-claude-subscription-2026-10.md` and
  `docs/research/harness-provider-access-2026-09.md`.
- Pi `enabledModels` is the Ctrl+P cycle list, not an access restriction. It
  deduplicates by provider/model ID, retaining the first effort preset; use
  `/thinking` or explicit agent thinking overrides instead of duplicate entries.
  The only credential in untracked `~/.pi/agent/auth.json` is the
  `opencode-go` API key; the `openai-codex` and `anthropic` OAuth credentials
  and the OpenRouter key were removed on 2026-09-16. Restoring the Claude path
  needs `/login anthropic` again (machine-local, per box).
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
