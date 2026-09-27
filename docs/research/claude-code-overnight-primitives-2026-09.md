# Claude Code primitives for an overnight ticket runner (2026-09-27)

Question: the draft `overnight-run` skill prompt runs agent-ready GitHub issues
serially and unattended — one fresh `claude -p` process per ticket, with a usage
gate that reads Claude Code rate limits. Which of its claims about Claude Code
(statusline JSON, headless mode, usage surfaces, flags, timeouts) hold against
primary sources, and what must the prompt correct? A later scope addition asks
the same for the OMP harness (`omp` binary): `omp usage`, headless flags, and
bash timeouts.

Answer: the statusline schema and gating conditions check out, all three cited
issues exist as described, and every `claude -p` flag cited exists — but the
model-specific weekly bar is absent from the JSON (two open issues), an open bug
says `rate_limits` can be absent entirely on v2.1.278, nothing documents that
`claude -p` ever invokes the statusLine command, and there is no documented
`sleep`-based wait that survives inside a `-p` run for hours. The most reliable
usage gate is not the statusline at all: `omp usage --provider anthropic --json`
reports all three subscription windows (5-hour, 7-day, 7-day Fable) from outside
any session, against the same subscription pool both harnesses burn.

Local probes: `claude --version` → `2.1.283`; `omp --help` → `omp v18.3.5`. No
paid prompts were run.

## 1. Statusline stdin JSON: `rate_limits` shape — VERIFIED

The documented fields are exactly `rate_limits.five_hour` and
`rate_limits.seven_day`, each with `used_percentage` (0–100) and `resets_at` as
**Unix epoch seconds** (not ISO):

- Table rows: `` `rate_limits.five_hour.used_percentage`,
  `rate_limits.seven_day.used_percentage` `` — "Percentage of the 5-hour or
  7-day rate limit consumed, from 0 to 100"; `` `rate_limits.five_hour.resets_at`,
  `rate_limits.seven_day.resets_at` `` — "Unix epoch seconds when the 5-hour or
  7-day rate limit window resets". Source:
  <https://code.claude.com/docs/en/statusline> (read 2026-09-27).
- Example payload uses `"used_percentage": 23.5, "resets_at": 1738425600`
  (epoch seconds scale). Same page.
- There is a third, conditional window: `rate_limits.spend_limit` with the same
  two fields, but only "behind a Claude apps gateway", and its
  `used_percentage` "can go above 100 once you exceed the limit". Requires
  v2.1.251+. Same page.

Correction for the draft: any claim that `resets_at` is ISO is wrong; parse
epoch seconds. And the schema has three possible windows, not two.

## 2. `rate_limits` availability conditions — VERIFIED

- "appears only for claude.ai Pro and Max subscribers, or behind a Claude apps
  gateway that sets a spend limit for you, **and only after the first API
  response in the session**." Each window "may be independently absent, and
  Claude Code drops a window once its `resets_at` time passes." The docs'
  own jq idiom is `.rate_limits.five_hour.used_percentage // empty`. Source:
  <https://code.claude.com/docs/en/statusline> (read 2026-09-27).
- The "Rate limit usage" example handles the absent field gracefully in all
  three languages. Same page.
- The live `~/.claude/claude-powerline.json` on this machine is consistent
  with a subscriber-gated, post-first-response field (not independently probed
  beyond that).

Correction for the draft: "only for Claude.ai subscribers" should read "Pro
and Max subscribers (Team/Enterprise see plan usage in `/usage`; gateway
sessions see `spend_limit`)". The "only after first API response" half is
exact.

## 3. Cited issues — all three VERIFIED (plus corroboration)

| Draft citation | State | Finding |
| --- | --- | --- |
| #45133 | **Closed** (duplicate of #40094, auto-closed 2026-04-12; opened 2026-04-08) | Reporter on Claude Max / v2.1.96 saw `rate_limits.seven_day` + `five_hour` absent from statusLine JSON while `cost` was present. Matches the draft's "missing in some releases" claim. Source: <https://github.com/anthropics/claude-code/issues/45133> |
| #95918 | **Open** bug (opened 2026-09-21, v2.1.278, macOS) | `rate_limits` absent from *both* statusLine and hook input JSON; reporter's spend-limit progress bar never renders although claude.ai shows $386/$500. Matches the draft's "missing in some releases" claim and extends it to hooks. Source: <https://github.com/anthropics/claude-code/issues/95918> |
| #91920 | **Open** enhancement (opened 2026-09-03, v2.1.252, Team plan) | `/usage` shows three bars (5h 21%, weekly all-models 23%, weekly Fable 42%) while the statusline JSON carries only `five_hour` + `seven_day`. Requests a `seven_day_model`-shaped third entry. Exactly the draft's "model-specific weekly bar from /usage is not in the JSON" claim. Source: <https://github.com/anthropics/claude-code/issues/91920> |

Corroborating (not draft-cited, same gap): #62082 (closed, 2026-05-24,
Sonnet-only weekly limit missing from statusline JSON, with a maintainer-era
comment thread pointing at undocumented endpoints) and #40094 (`rate_limits`
missing for Claude Max 20x / first-party OAuth), #19385 (feature request:
expose rate-limit data in statusline JSON). Treat commenter-posted endpoint
URLs in #62082 as unverified third-party claims, not documentation.

Correction for the draft: cite states and dates — #45133 is closed (duplicate),
#95918 and #91920 are still open. The prompt must not assume the JSON ever
carries the model-scoped weekly window.

## 4. Whether headless `claude -p` invokes the statusLine command — UNVERIFIABLE

- No documented statement either way. The statusline page describes the
  status line strictly as an interactive footer UI ("a customizable bar at the
  bottom of Claude Code"); its update triggers are UI/session events (new
  assistant message, `/compact`, permission-mode change, vim toggle,
  `refreshInterval`, `resets_at`/`expires_at` timers). Source:
  <https://code.claude.com/docs/en/statusline> (read 2026-09-27).
- The headless page (`-p` lifecycle, background tasks at exit, SIGTERM,
  structured output, permission modes) never mentions `statusLine`. Source:
  <https://code.claude.com/docs/en/headless> (read 2026-09-27).
- Changelog grep for `statusLine` × `-p`/print/headless: no hit (local
  `curl` + `grep`, 2026-09-27).
- A paid `claude -p` probe with a logging statusLine script would settle it
  but was out of scope (no paid prompts).

Correction for the draft: the gate **MUST assume `claude -p` never runs the
statusLine command**. Any design that reads usage from inside the `-p`
session via statusline is building on an undocumented mechanism; read usage
from outside the session instead (§9).

## 5. Non-statusline ways to read usage / rate limits

- **`/usage` (interactive session command) — VERIFIED, interactive-only.**
  Shows session tokens/cost, plan usage bars, attribution, and (v2.1.251+) a
  `Prompt cache (main)` line. There is no documented `-p` or pipeable form;
  the sibling `/usage-credits` explicitly "sends no request" in
  non-interactive mode and tells you to run it interactively. Sources:
  <https://code.claude.com/docs/en/costs> (read 2026-09-27),
  <https://code.claude.com/docs/en/headless>.
- **`claude usage` subcommand — VERIFIED ABSENT.** The CLI reference command
  table lists `agents, attach, auth, auto-mode, daemon, doctor, import,
  install, logs, mcp, plugin, project, remote-control, respawn, rm,
  self-hosted-runner, setup-token, stop, ultrareview, update` — no `usage`.
  Source: <https://code.claude.com/docs/en/cli-reference> (read 2026-09-27).
  (Local `claude --help`, v2.1.283, likewise shows no `usage` command.)
- **OpenTelemetry — VERIFIED present but not a quota gate.** Exported
  metrics are `claude_code.token.usage`, `claude_code.cost.usage`,
  `claude_code.session.count`, `lines_of_code`, `pull_request`, `commit`,
  `active_time`, etc. — token/cost accounting, no quota-percentage or
  reset-time metric (`grep rate/quota/usage_limit` over the monitoring page
  finds nothing quota-shaped). Events (`user_prompt`, `assistant_response`,
  `tool_result`, `api_request`) carry no quota fields. Source:
  <https://code.claude.com/docs/en/monitoring-usage> (read 2026-09-27).
- **Hooks input — VERIFIED ABSENT.** `grep rate_limits` over the hooks doc
  returns nothing; #95918's reporter independently observes the field absent
  in hook context. Sources: <https://code.claude.com/docs/en/hooks> (fetched
  2026-09-27), <https://github.com/anthropics/claude-code/issues/95918>.
- **`--output-format json` / `stream-json` — VERIFIED, reactive only.**
  `--output-format json` returns the result object (§6); `stream-json`
  emits `system/api_retry` events whose `error` enum includes `rate_limit`
  (alongside `overloaded`, `billing_error`, `account_on_hold`, …). That is
  an in-run retry signal, not a preflight gate. `system/init` carries
  model/tools/plugins/MCP state, no quota. Source:
  <https://code.claude.com/docs/en/headless> (read 2026-09-27).
- **Exact rate-limit error text a `-p` run returns — VERIFIED (docs):**

  ```text
  You've hit your session limit · resets 3:45pm
  You've hit your weekly limit · resets Mon 12:00am
  You've hit your Opus limit · resets 3:45pm
  You've hit your Sonnet limit · resets 3:45pm
  ```

  Session/weekly windows are shared across models (switching does not help);
  Opus/Sonnet windows are per-family (switching out of the family does).
  API-key/ Bedrock-style throttles instead surface as `API Error: Request
  rejected (429) · …`. Pre-exhaustion warning: `You've used 85% of your
  session limit · resets 3:45pm`. Source:
  <https://code.claude.com/docs/en/errors#youve-hit-your-session-limit>
  (read 2026-09-27).
- **Unattended-retry knobs — VERIFIED.** `CLAUDE_CODE_RETRY_WATCHDOG=1`
  retries 429/529 capacity errors indefinitely (but fails fast on
  spend-limit / exhausted-credits 429s); `CLAUDE_CODE_MAX_RETRIES` (default
  10, cap 15; watchdog raises it to 300 for transient errors). The
  wait-and-auto-continue-after-reset behavior is interactive-only (v2.1.234+;
  Desktop auto-continue checkbox covers the session card only). Source:
  <https://code.claude.com/docs/en/errors> (read 2026-09-27).

Correction for the draft: enumerate the error strings above as the strings
the runner parses; do not claim OTel, hooks, or stream-json expose quota
percentages; do not claim `/usage` or any `claude usage` works from `-p`.

## 6. `claude -p` flags and JSON result schema — VERIFIED (local 2.1.283 + docs)

Observed `claude --help` (2.1.283, 2026-09-27; `claude -p --help` prints the
same flag list — there is no separate `-p` help) plus the CLI reference:

| Draft claim | Status |
| --- | --- |
| `--output-format json` (also `text`, `stream-json`; print-only) | VERIFIED |
| `--max-turns` (print-only; exits with error at the cap) | VERIFIED |
| `--permission-mode` with `acceptEdits`, `bypassPermissions`, `dontAsk`, `auto` | VERIFIED — all four exist; full set is `default, acceptEdits, plan, auto, dontAsk, bypassPermissions, manual` (`manual` = alias for `default`, v2.1.200+). For `-p` the starting mode is Manual unless configured, so the prompt must pass one explicitly. Sources: local `--help`; <https://code.claude.com/docs/en/cli-reference> |
| `--dangerously-skip-permissions` (= `--permission-mode bypassPermissions`) | VERIFIED |
| `--allowedTools` / `--disallowedTools` | VERIFIED (both spellings `--allowedTools, --allowed-tools`) |
| `--append-system-prompt` (plus `--append-system-prompt-file`) | VERIFIED |
| `--max-budget-usd` (print-only; subagent spend counts; restored totals on `--continue/--resume` do not) | VERIFIED |
| `--no-session-persistence` (print-only) | VERIFIED |

Result schema (`--output-format json` emits the SDK result object; schema
from the Agent SDK TypeScript reference — VERIFIED):

- Success arm: `type: "result", subtype: "success", is_error, num_turns,
  result, total_cost_usd, usage, modelUsage, duration_ms, duration_api_ms,
  stop_reason, session_id, permission_denials, …`
- Error arm: `subtype: "error_max_turns" | "error_during_execution" |
  "error_max_budget_usd" | "error_max_structured_output_retries"` with
  `errors: string[]` (plus `api_error_status`, `startup_failure_reason`,
  `terminal_reason` where applicable). Source:
  <https://code.claude.com/docs/en/agent-sdk/typescript> (`SDKResultMessage`,
  read 2026-09-27).

Unattended-run companion flags the draft should add (both VERIFIED):
`--permission-prompts none` (v2.1.259+; denied-without-retry instead of
hanging on a host) and `--bare` (skips hooks/skills/MCP/CLAUDE.md
auto-discovery; recommended for scripted `-p`).

## 7. Bash timeouts, background execution, Monitor — VERIFIED

- **Bash tool timeout: default 2 minutes, ceiling 10 minutes, and
  `BASH_MAX_TIMEOUT_MS` does change the ceiling.** "Each command runs under
  a timeout… `BASH_DEFAULT_TIMEOUT_MS` — the default when Claude passes no
  timeout; two minutes out of the box. `BASH_MAX_TIMEOUT_MS` — … sets the
  ceiling that caps whatever Claude requests: the effective ceiling is the
  larger of the two, ten minutes out of the box." Source:
  <https://code.claude.com/docs/en/tools-reference> ("Timeout and output
  limits", read 2026-09-27). So the draft's "max timeout is 10 minutes" is
  the out-of-box ceiling, not a hard constant — raising the env var raises it.
- **Auto-backgrounding exists, but `sleep` is excluded.** "When a command
  reaches its timeout without finishing, Claude Code moves it to the
  background instead of stopping it, **unless the command starts with
  `sleep`**." The moved command reports `Command did not complete within
  its 120s timeout and was moved to the background` + task ID + output file;
  `/tasks` lists/stops them. Disabler:
  `CLAUDE_CODE_DISABLE_BACKGROUND_TASKS=1`. Same source.
- **Monitor tool exists with short deadlines — not an overnight wait.**
  Default watch deadline 5 min, at most 30 min, **at most 10 min in a
  non-interactive `-p` run**. Same source.
- **`-p`-exit semantics bound any in-session wait.** Background Bash shells
  are killed ~5 s after the final result; `-p` instead waits for background
  subagents/workflows up to **10 min** (`CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS`,
  `0` = unbounded). Source: <https://code.claude.com/docs/en/headless>
  (read 2026-09-27).

Correction for the draft: chunked in-session `sleep`s neither auto-background
nor survive `-p` exit, and no documented mechanism waits hours inside one
`-p` run. Sleep/wait in the **outer runner** (shell loop, cron, launchd)
between fresh `claude -p` invocations — which is the draft's architecture
anyway. Keep `BASH_MAX_TIMEOUT_MS` at default; per-ticket bounds belong on
`--max-turns` / `--max-budget-usd`, not the Bash ceiling.

## 8. Max2535/claude-code-statusline — SECONDARY (flag as such)

0 stars / 0 forks / Python / MIT. What it actually claims (source:
<https://github.com/Max2535/claude-code-statusline>, read 2026-09-27):

- Renders `rate_limits.five_hour` ("Current session") and
  `rate_limits.seven_day` ("Weekly · All models") bars plus context/cost/git
  lines, mimicking the claude.ai Plan Usage Limits popup.
- Explicitly notes the **"Sonnet only" weekly limit, daily routine runs,
  and usage-credits balance are NOT available via the status line API**.
- Mirrors the two windows to `~/.claude/statusline-state.json`
  (`updated_at`, `five_hour`/`seven_day` with `used_percentage` +
  `resets_at`), precisely because "Claude Code hands `rate_limits` to a
  status line and to nothing else — there's no CLI flag, no state file, no
  local API."
- Notes `rate_limits` is subscriber-only and populated after the first API
  call (matching §2).

Correction for the draft: cite it only as a secondary illustration of the
push-only problem and the state-file workaround pattern — never as evidence
for a schema or availability claim. Its `statusline-state.json` mirror is a
usable pattern for interactive sessions but does not help `-p` runs (§4).

## 9. OMP harness (`omp` v18.3.5) — VERIFIED live, read-only

### (a) `omp usage` prints the Anthropic subscription's windows — VERIFIED

Live run, 2026-09-27 (`omp usage --provider anthropic`; no paid prompt, only
a usage read):

```text
Usage · fetched 5.5s ago

Anthropic — 1 account
  ● sudaksh.soti@gmail.com · sudaksh.soti@gmail.com's Organization · ✦ 1 saved reset · soonest expires in 24d21h (2026-10-22)
      ● Claude 5 Hour         ██░░░░░░░░░░░░░░░░░░░░░░░░░░  6.0% used · resets in 4h15m
      ● Claude 7 Day          ██████░░░░░░░░░░░░░░░░░░░░░░  20.0% used · resets in 2d20h
      ● Claude 7 Day (Fable)  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░  0.0% used · resets in 2d20h
  capacity: 5h → 0.06/1 account used (0.94× quota left) · 7d → 0.20/1 account used (0.80× quota left) · 7d (Fable) → 0.00/1 account used (1.00× quota left)
```

- Covers **all three windows including the model-specific Fable bar** that
  the Claude Code JSON lacks (§3, #91920).
- `--json` is machine-readable: per-window `id` (`anthropic:5h`,
  `anthropic:7d`, `anthropic:7d:fable`), `label`, `window.resetsAt` in
  **epoch milliseconds** (e.g. `1790548200000`), `amount.{used, limit,
  remaining, usedFraction, remainingFraction, unit: "percent"}`,
  `status: "ok"`, plus `fetchedAt`/`generatedAt`. Sources: live
  `omp usage --provider anthropic [--json]` output; flags from
  `omp usage --help` (`-j/--json`, `-p/--provider`, `-r/--redact`,
  `--history`, `invalidate`).
- Caveats: figures are cached ("fetched 5.5s ago") — run
  `omp usage invalidate [--provider anthropic]` before gating, same as the
  prior `docs/research/muse-code-subscription-2026-09.md` procedure.
- Same-pool note: per `docs/research/harness-provider-access-2026-09.md`,
  Claude models are reachable from OMP on the subscription (and only from
  OMP), so `omp usage` meters the pool the overnight tickets burn
  regardless of which harness runs them.

### (b) OMP headless `-p` flags — VERIFIED from `omp --help`

(`omp -p --help` prints the same `launch` flag list; no separate `-p` help.)

| Need | OMP equivalent | Status |
| --- | --- | --- |
| Output format | `--mode text\|json\|rpc\|rpc-ui` | VERIFIED |
| Permissions / auto-approve | `--auto-approve` (skip all prompts); `--approval-mode always-ask\|write\|yolo` | VERIFIED |
| Max turns | **none found** — full `--help` grep for `turn\|budget\|step` is empty | UNVERIFIABLE (absent) — bound runs with `--max-time` (e.g. `10m`, `1h`) instead |
| Ephemeral runs | `--no-session` | VERIFIED |
| Stdin | **must be closed** (`stdin=DEVNULL` or `</dev/null`), else `-p` waits at `readPipedInput` | VERIFIED per-repo: `AGENTS.md` ll.177–178; probes in `docs/research/harness-provider-access-2026-09.md` |

### (c) OMP bash tool timeout — UNVERIFIABLE

- No bash-timeout flag, key, or env var in `omp --help` (full-text grep for
  `timeout|interval|poll|wait|sleep` hits only `PI_NO_PTY` and `ps stop
  --timeout`) nor in `omp/config.yml` (`tools:` carries only
  `approvalMode: yolo` + empty `approval:`). OMP does supervise background
  processes (`omp ps list|logs|stop|kill|restart`, incl. `--json`), but that
  is the operator's process supervision, not a documented model-bash-tool
  ceiling.
- Per-repo convention (AGENTS.md l.123): macOS has no GNU `timeout`; wrap
  with Python `subprocess.run(..., timeout=...)` or background-plus-`kill`.

Correction: the skill must not assert any OMP bash ceiling; enforce waits
and kills from the outer runner script.

### Reliability verdict per harness

- **Claude Code runs (`claude -p` tickets): gate on `omp usage
  --provider anthropic --json`** (after `invalidate`). It sees all three
  windows from outside the session with zero API burn; the statusline JSON
  sees at most two, only mid-session, and is currently reported broken on
  2.1.278 (#95918). The one gap: `omp usage` reflects the subscription pool
  shared with interactive use, which is exactly what you want a gate to see.
- **OMP runs (`omp -p` tickets): gate on the same `omp usage` output** —
  native to the harness, same pool, same command. No second source needed.
- In both cases, treat the Claude Code statusline as a human display, not a
  machine gate.

## Implications for the overnight-run prompt (concrete corrections)

1. **Schema fix:** `resets_at` is Unix epoch **seconds**; percentages are
   0–100 floats. Parse accordingly; never claim ISO.
2. **Scope fix:** `rate_limits` = Pro/Max subscribers (gateway sessions get
   `spend_limit` instead), post-first-API-response only, each window
   independently omittable, windows vanish after `resets_at`. Every access
   must use `// empty`-style absence handling.
3. **Third-window fix:** do not promise the model-scoped weekly bar
   (Sonnet/Opus/Fable) in statusline JSON — #91920 and #62082 show it is
   absent; #95918 shows the whole object can be absent on 2.1.278. If the
   prompt needs the Fable/Sonnet bar, it must call `omp usage`, not read
   statusline JSON.
4. **Headless fix:** delete any claim that `-p` runs the statusLine command
   (undocumented; §4 UNVERIFIABLE). The usage gate runs **before** spawning
   `claude -p`, in the outer loop, via `omp usage --provider anthropic
   --json` after `omp usage invalidate --provider anthropic`.
5. **Surface fixes:** `/usage` is interactive-only; there is no
   `claude usage` subcommand; OTel metrics (`token.usage`, `cost.usage`)
   and hook input carry no quota percentages; `stream-json` `api_retry`
   events (with `error: "rate_limit"`) are reactive retry signals, not a
   preflight gate.
6. **Failure-string fixes:** match `You've hit your session limit · resets
   …`, `… weekly limit …`, `… Opus limit …`, `… Sonnet limit …` (and `API
   Error: Request rejected (429) · …` for key-side throttles) in the JSON
   result's `errors[]` / `subtype: "error_during_execution"` (or stdout
   text), then sleep until the parsed reset time. Never claim the CLI
   auto-waits: auto-continue-after-reset is interactive-only.
7. **Flag fixes:** all eight cited flags exist as named (table §6); add
   `--permission-prompts none` and consider `--bare` for unattended runs;
   start `-p` explicitly in `acceptEdits`/`dontAsk`/`auto` (default start is
   Manual). Bound tickets with `--max-turns` + `--max-budget-usd`, and read
   `subtype`/`num_turns`/`total_cost_usd`/`errors[]` from `--output-format
   json`.
8. **Wait-strategy fix:** no in-session `sleep` chunking (excluded from
   auto-backgrounding; dies with `-p` exit) and no Monitor watch (≤10 min
   in `-p`) can bridge a hours-long reset. All waiting happens in the outer
   runner between fresh processes. Leave `BASH_MAX_TIMEOUT_MS` at default;
   it raises the 10-minute per-command ceiling but is not a scheduling
   primitive.
9. **OMP-runner fixes:** gate OMP tickets with the same `omp usage
   --provider anthropic --json`; invoke `omp -p` with stdin closed
   (`</dev/null`); use `--mode json`, `--auto-approve` or `--approval-mode`,
   `--max-time`, `--no-session`; do not assert a max-turns flag or a bash
   timeout ceiling for OMP — neither is documented.
10. **Secondary-source fix:** Max2535/claude-code-statusline may be cited
    only as prior art for the mirror-to-state-file pattern, labeled
    secondary (0★, unverified), never for schema facts.

## Sources

- <https://code.claude.com/docs/en/statusline> — `rate_limits` fields,
  epoch seconds, subscriber/first-response gating, absence handling (read
  2026-09-27).
- <https://code.claude.com/docs/en/headless> — `-p` lifecycle, background
  tasks at exit (10-min cap, `CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS`),
  `--output-format`, stream-json `api_retry`/`system-init` events,
  `--permission-prompts none`, `--bare`, Manual start for `-p` (read
  2026-09-27).
- <https://code.claude.com/docs/en/cli-reference> — full flag table
  (`--max-turns`, `--max-budget-usd`, `--no-session-persistence`,
  `--permission-mode` values, `--allowedTools`, `--append-system-prompt`);
  command table has no `usage` (read 2026-09-27).
- <https://code.claude.com/docs/en/costs> — `/usage` contents, prompt-cache
  line, usage-credits, limit-meaning table (read 2026-09-27).
- <https://code.claude.com/docs/en/errors> — exact `You've hit your …`
  strings, 429 text, `CLAUDE_CODE_RETRY_WATCHDOG` / `MAX_RETRIES`,
  interactive-only auto-continue (read 2026-09-27).
- <https://code.claude.com/docs/en/errors#youve-hit-your-session-limit> —
  per-family vs shared windows (read 2026-09-27).
- <https://code.claude.com/docs/en/tools-reference> — Bash default 2 min /
  ceiling 10 min / `BASH_MAX_TIMEOUT_MS`, `sleep` exclusion,
  auto-backgrounding, Monitor deadlines (read 2026-09-27).
- <https://code.claude.com/docs/en/monitoring-usage> — metric/event names,
  no quota metric (read 2026-09-27).
- <https://code.claude.com/docs/en/hooks> — no `rate_limits` in hook input
  (fetched 2026-09-27).
- <https://code.claude.com/docs/en/agent-sdk/typescript> —
  `SDKResultMessage` schema (`subtype`, `is_error`, `num_turns`,
  `total_cost_usd`, `errors[]`) (read 2026-09-27).
- <https://code.claude.com/docs/en/permission-modes> — mode list, `-p`
  start behavior (fetched 2026-09-27).
- <https://github.com/anthropics/claude-code/issues/45133> — closed
  duplicate (2026-04-08→04-12), Max, v2.1.96, `rate_limits` absent.
- <https://github.com/anthropics/claude-code/issues/95918> — open bug
  (2026-09-21), v2.1.278, absent in statusLine + hook input.
- <https://github.com/anthropics/claude-code/issues/91920> — open
  enhancement (2026-09-03), model-scoped weekly bar missing from JSON.
- <https://github.com/anthropics/claude-code/issues/62082> — closed,
  Sonnet-only weekly gap corroboration (2026-05-24).
- <https://github.com/Max2535/claude-code-statusline> — secondary statusline
  project: two-window display, explicit Sonnet-only/routines/credits gap
  note, `statusline-state.json` mirror (read 2026-09-27).
- Local: `claude --version` → `2.1.283`; `claude --help` / `claude -p
  --help` flag text; `omp v18.3.5 --help`, `omp usage --help`,
  `omp usage --provider anthropic [--json]` live output (2026-09-27).
- Repo: `AGENTS.md` ll.123–124 (no GNU timeout), ll.177–179 (closed stdin
  for `omp -p`); `omp/config.yml` `tools:` (approvalMode only);
  `docs/research/harness-provider-access-2026-09.md` (OMP-only Claude
  subscription path); `docs/research/muse-code-subscription-2026-09.md`
  (report style convention).
