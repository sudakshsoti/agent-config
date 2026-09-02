# Muse Spark 1.3 resolution check — 2026-09-03 (resolved)

## Result

Both faults confirmed and fixed in this follow-up session, all with `retry:
enabled: false` overlays so no fallback could mask a result.

## Fault 1 — muse 1.3 is a provider-side catalog stub

`opencode-go/muse-spark-1.3-contributor` never completes a live request.

- Bare probe (`--model opencode-go/muse-spark-1.3-contributor`, no effort
  suffix): `500 Internal server error`, reproduced 4/4 times.
- Any `:effort` suffix (`minimal`/`low`/`medium`/`high`/`xhigh`, with or
  without the `opencode-go/` prefix) fails to resolve locally: `Model
  "…:high" not found`, before any request is sent.
- Its row in `~/.omp/agent/models.db` (opencode-go catalog, refreshed
  2026-09-03 01:07 — not stale) is a stub compared to 1.2's row: `api:
  "openai-completions"` vs 1.2's `"openai-responses"`, `name` equal to the
  raw id instead of a display name, and all four `cost` fields `0`.
- `muse-spark-1.2-contributor` answers `ok` cleanly at both `:high` and
  `:xhigh` under the same overlay — it is not an outage, 1.3 specifically is
  broken.

Fix: reverted all five routing sites in `omp/config.yml` — `smol`, `advisor`,
and the three fallback-chain mentions (two rungs plus the chain key) — from
`muse-spark-1.3-contributor` back to `muse-spark-1.2-contributor`. Applied
identically to the live file behind `~/.omp/agent/config.yml`
(`~/dev/agent-config/omp/config.yml`, since that symlink points at the main
checkout, not this worktree).

## Fault 2 — OpenRouter was never actually broken

Every `openrouter/*` probe returned `401 User not found`, which looked like a
dead OpenRouter account. It was a shadowed environment variable, not an
account or key problem:

- `~/.zshrc.local` line 2 hardcoded `export
  OPENROUTER_API_KEY='sk-or-v1-66c2f87a…'` — dead, confirmed by `curl
  https://openrouter.ai/api/v1/key` returning 401 with it.
- `~/.omp/.env` (1Password-managed, `sk-or-v1-c707…`) is the working key:
  `curl` with it returns 200, `limit: 15`, `limit_remaining: 15`.
- `~/.local/share/opencode/auth.json` also carries a third, separately dead
  key (`sk-or-v1-d474…`) — irrelevant once the shell export is gone, since
  `omp token openrouter` resolves from environment before that file.
- `omp token openrouter` printed the shadowing key, proving omp was reading
  the shell export, not `.env`.
- With the export removed and a fresh shell, `omp -p --model
  openrouter/x-ai/grok-4.5 --config /tmp/nofallback.yml "Reply with exactly:
  ok"` returns `ok`.

Fix: deleted the `OPENROUTER_API_KEY` line from `~/.zshrc.local`, keeping the
other two exports (`TAVILY_API_KEY`, `EXA_API_KEY`) — both already identical
to `.env`.

## Side finding — grok-4.5's reserved tool name

`opencode-go/grok-4.5` 400s with omp's default web-search tool enabled:
`invalid tools in request: custom function name "web_search" is reserved`.
It answers fine with `web_search: enabled: false`. `opencode-go/grok-4.6`
answers with web search left on. Both ids are live on the Go plan; this is
not a missing-model problem. Use 4.6 when Grok + web search are both wanted.

## What changed

- `omp/config.yml` (this worktree and the live file at
  `~/dev/agent-config/omp/config.yml`): five `muse-spark-1.3-contributor` →
  `muse-spark-1.2-contributor` substitutions.
- `~/.zshrc.local`: removed the dead `OPENROUTER_API_KEY` export.
- `AGENTS.md`: amended the bare-probe and env-shadowing gotchas, added two new
  ones (muse 1.3 stub, grok web_search reservation).

## Follow-up for whoever merges this branch

The main checkout (`~/dev/agent-config`, `main`) has the same `omp/config.yml`
edit applied locally but uncommitted, since that's the file the live symlink
points at. Before `git pull` there after this branch merges, run `git -C
~/dev/agent-config checkout -- omp/config.yml` — the incoming committed
content is byte-identical to the local edit, so this is a no-op that just
clears the pull-blocking local diff.
