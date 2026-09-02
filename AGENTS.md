# AGENTS.md

This is a Codex-specific overlay, not a standalone guide. **Read `CLAUDE.md` in
this directory first** — it is the full, accurate guide to this repo, and it
holds for Codex too except where this file says otherwise. Codex auto-loads
`AGENTS.md` and never reads `CLAUDE.md` on its own, which is the only reason
this file exists.

## What actually reaches Codex

Only skills, and only as symlinks in `~/.agents/skills` (the shared
cross-agent root). Editing a `SKILL.md` in this repo is live for Codex
immediately — no `./install.sh` re-run needed. A re-run is only needed for
adding, renaming, or deleting a skill. For a deletion specifically, plain
`./install.sh` is not enough — it leaves the now-dangling symlink in place.
Run `./install.sh --prune` to actually clear it; otherwise the retired skill
stays listed (and counts against Codex's 2% skill budget) even though its
directory is gone.

**Never install skills into `~/.codex/skills`.** Codex scans both
`~/.codex/skills` and `~/.agents/skills`, so a skill present in both is listed
twice. That's not cosmetic: Codex caps skills at 2% of context and truncates
every skill's description once that budget fills, so the duplication degrades
discovery across the whole set, not just the doubled skill. `install.sh` step
1b (lines 136-150) actively deletes leftover `~/.codex/skills` copies that
carry the `.agent-config-managed` marker.

Verify with `codex exec "list skill names"` — each name must appear exactly
once.

## No `skillOverrides` in Codex

`skillOverrides` is a Claude Code `settings.json` key; Codex has nothing
equivalent. `~/.codex/config.toml` only has `[plugins.<name>] enabled =
true/false` toggles for plugins, nothing per-skill for filesystem skills.
Consequence: a skill sitting in `skills/` counts against Codex's 2% budget
even if it's switched off for Claude via `skillOverrides`.

## Claude-only — do not edit these as Codex

`agents/`, `settings.json`, `claude-powerline.json`, `hooks/`, `plugins.txt`,
`dist/`. These configure Claude Code specifically (subagents, its settings
file, its statusline, its hooks, its plugin list, its skill zips) and Codex
has no equivalent for any of them.

## Gotchas

- Model thinking levels are per-model. `deepseek-v4-flash`, `glm-5.3-flash` and
  `kimi-k3` expose only low/high/max. Writing `medium` on those is not rejected:
  it silently runs, and bills, as `high`.
- omp rewrites `omp/config.yml` and deletes every comment line while keeping the
  values byte-identical. Never keep decision rationale in that file; it belongs
  in `docs/`.
- In omp only one user-level context file survives, by provider priority: native
  `~/.omp/agent/AGENTS.md` (100) beats `~/.claude/CLAUDE.md` (80) beats
  `~/.codex/AGENTS.md` (70). Two different global files means the lower one is
  never loaded. All four paths are symlinks to `global-agents.md`, so keep them
  that way rather than editing one destination.
- `link_into` in `install.sh` refuses to replace a real non-symlink file: it
  prints a SKIP warning and continues. A missing symlink after an install run
  usually means a real file is sitting in the destination.
- A bare `omp -p --model <id>` probe cannot prove a model works. When the model
  fails, the fallback chain answers and the reply looks like a success. Three
  `opencode-zen` `-free` ids returned a clean `ok` this way while actually
  returning `401 Model is disabled`. Probe with retry off instead —
  `printf 'retry:\n  enabled: false\n' > /tmp/nofallback.yml` then
  `omp -p --model <id> --config /tmp/nofallback.yml "Reply with exactly: ok"` —
  where a clean reply is proof and a failure prints the provider's own error.
  `omp -p` runs write no row to `~/.omp/stats.db`, so reading `error_message`
  there only works after a real interactive or subagent turn.
- `opencode-zen`'s `-free` model ids are dead: `muse-spark-1.2-contributor-free`
  and `deepseek-v4-flash-free` return `401 Model is disabled`,
  `minimax-m3-free` returns `401 ... is not supported`. Never put them in a
  fallback chain. Paid `opencode-zen/deepseek-v4-flash` does work, billed
  against the workspace spending limit at `opencode.ai/workspace/<id>/billing`,
  which is real money separate from the Go subscription.
- `retry.fallbackChains` resolves by specificity: exact `provider/model-id`
  beats `provider/*`, then the role's chain, then `default`
  (`omp://settings.md`). A role that must avoid a provider needs its own
  exact-model key — and even then, chain exhaustion falls through to `default`,
  so a chain cannot guarantee a provider is never reached.
- OpenCode Go's monthly limit is a **sum of per-model quota fractions**, not a
  dollar total. Each model has its own $15/$30/$60 monthly quota and the plan
  caps the sum of used fractions at 100%. So $1 on a $60-quota model costs 1.67
  points and $1 on a $15-quota model costs 6.67 points. Only the OpenCode
  dashboard shows the per-model rows; `omp usage` shows the capped aggregate and
  `omp stats` reports list-price estimates that ran 6x high and 4x low against
  OpenCode's own meter on the same day. Keep Go usage to
  `muse-spark-1.2-contributor` ($60), `deepseek-v4-flash` ($30) and
  `glm-5.3-flash` ($30).
- `retry.usageAwareFallback: true` skips **every** model of a provider whose
  aggregate usage reads exhausted, even models at 2% of their own quota, because
  omp never sees the per-model rows. It is set `false` here for that reason; the
  cost is one failed attempt when a model really is out, absorbed by
  `fallbackChains`.
- A `provider/*` value used as a fallback **rung** keeps the failing model's id
  and only swaps the provider, so it builds ids that do not exist on the target
  gateway. OpenRouter needs its vendor-prefixed ids
  (`meta/muse-spark-1.2-contributor`, not `muse-spark-1.2-contributor`). Use
  `provider/*` only as a chain **key**.
- omp loads `~/.omp/.env` into its own process environment at startup, and an
  already-set process variable beats every `.env` file. After
  `op inject` refreshes a key, a running omp session and every child it spawns
  still hold the old value. Test with
  `env -u <VAR> bash -lc 'set -a; . ~/.omp/.env; set +a; ...'`, and restart omp
  for the session itself to pick the key up.
  A hardcoded export shadows it permanently, not just for one session:
  `~/.zshrc.local` carried a dead `OPENROUTER_API_KEY` that beat the 1Password
  value in `~/.omp/.env` in every new shell, so every `openrouter/*` route
  returned `401 User not found` while `curl` with the `.env` key returned 200.
  `omp token <provider>` prints the key omp will actually use — check it before
  blaming the provider.
- `install.sh` refuses to run from a Supacode or temp git worktree (any path
  under `.supacode/repos/`, `.git/worktrees/` or `worktrees/`). The symlinks
  bake in the checkout's absolute path, so an install from a worktree points
  every `~/.claude/skills` and `~/.agents/skills` link at a directory that
  vanishes when the worktree is cleaned up. Always run it from
  `~/dev/agent-config`; `--force` exists but is the wrong answer. A skill
  reported as "not installed" after a new one lands usually means that machine
  never re-ran `install.sh` (or, on claude.ai, never got the new `dist/*.zip`
  uploaded: it does no dependency resolution, so every skill `design-brief`
  routes to needs its own upload).
- `opencode-go/muse-spark-1.3-contributor` is a catalog stub, not a live route.
  Its row in `~/.omp/agent/models.db` has `api: openai-completions` where 1.2 has
  `openai-responses`, no display name, and zero cost on all four fields. Bare
  probes return `500 Internal server error` (4/4), and any `:effort` suffix fails
  locally with `Model not found` at every level, prefixed or not, because the
  effort path needs metadata the stub lacks. `omp models list` still lists it, and
  the catalog is not stale — the opencode-go rows in `models.db` refreshed
  2026-09-03 01:07. Stay on `muse-spark-1.2-contributor`; re-check 1.3 with
  `omp models refresh` plus a retry-off probe before routing anything at it again.
- `opencode-go/grok-4.5` rejects omp's web search tool: `400 … invalid tools in
  request: custom function name "web_search" is reserved`. It answers normally
  with a `web_search: enabled: false` overlay. `opencode-go/grok-4.6` answers with
  web search left on, so use 4.6 rather than disabling a global tool for one
  model. Both ids are live on the Go plan despite the reserved-name failure
  looking like an unavailable model.
