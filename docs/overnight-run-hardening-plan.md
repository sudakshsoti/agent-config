# Overnight-run hardening plan

Status: planned 2026-09-29, revised after the GLM adversary review the same
day; implemented 2026-09-29 for issue #55. Source of the ideas:
`docs/research/overnight-run-improvements-2026-09.md` (R1–R6 plus the
runner-test gap, gap 9). Larger bets R7–R11 (parallel lanes, GLM review pass,
cloud mode, per-ticket cost, event intake) are **out of scope** here.

Files touched: `skills/overnight-run/SKILL.md`,
`skills/overnight-run/scripts/{overnight.sh,usage-gate.sh,worker-brief.md}`,
`skills/overnight-run/scripts/fixtures/`, `scripts/test-overnight-usage-gate.sh`,
new `scripts/test-overnight-runner.sh`.

## Decisions

- **Worker model: `opencode-go/deepseek-v4.1-flash:high`**, harness `omp`
  (Claude Code cannot run it). The model accepts only low/high/max
  (`omp models`); a retry-disabled `omp -p` probe answered `ok` on
  2026-09-29. DeepSeek is the non-training-eligible Go option for sensitive
  material (`AGENTS.md`), so the Muse-tier warning no longer applies to the
  default.
- **The usage gate follows the worker's model.** The gated provider is the
  model's prefix (`opencode-go/…` → `opencode-go`, `anthropic/…` →
  `anthropic`), so an `omp` worker pinned to an Anthropic model is gated on
  Anthropic. Worker `claude` with an empty model → `anthropic`. Worker `omp`
  with an empty model is refused: the harness default is not DeepSeek and its
  pool is unknown. Worker `claude` with a non-Anthropic model is refused.
- **Go windows (live 2026-09-29):** limit ids `rolling-5h` (window `5h`,
  `durationMs` 18000000), `weekly` (window `7d`) and `monthly` (window
  `monthly`, `durationMs` null). The gate selects windows by `.window.id`.
  The Go cap is shared with daytime `scout`/`adversary`/`commit`, so the
  weekly pace stop matters more, not less.
- **Any window without a length gets the hard stop only.** One generic rule in
  the jq; no provider-specific pace path.
- **Retries resume from the previous attempt's work, applied by the runner.**
  The runner saves the attempt as a binary-safe patch, resets the tree, and
  re-applies the patch before starting the retry worker. The brief tells the
  worker it is continuing a previous attempt. A patch that no longer applies
  starts the retry clean and says so in the handoff. The worker never decides
  whether to apply it.
- **Tests join the runner gate** whenever `checks.test` is set. The post-stash
  "is the tree still healthy" gate stays typecheck + build + lint, so a flaky
  test cannot halt the whole run.
- **One retry per ticket** (`MAX_RETRIES=1`), counted separately from
  rate-limit requeues (`MAX_REQUEUES=3`).
- **Old files on `--resume`:** a `plan.json` without `worker_model` and no
  `OVERNIGHT_WORKER_MODEL` → refuse with a message naming the key. A
  `state.json` without `retries` works: every read and write uses
  `(.retries // {})`.

## Failure taxonomy (drives R1)

|Reason (from `run_ticket`)|Class|
|---|---|
|timed out · worker exited ≠0 · no final JSON · build gate red · test gate red · worker `partial` · setup failed|transient → retry once|
|worker `blocked` · `done` with no changes · protected paths touched · commit hook refused|terminal → fail now|
|rate-limit text · failure while the gate reads 10/20|unchanged → requeue|

## Phase 1 — DeepSeek worker and provider-aware gate

- [ ] `plan.json` gains `"worker_model"`; `overnight.sh` reads it
      (`OVERNIGHT_WORKER_MODEL` still wins) and stores it in `state.json` so
      `--resume` keeps it. `resolve_model` returns it; `worker_cmd` already
      passes `--model`. Apply the provider rules and refusals from Decisions.
- [ ] `usage-gate.sh --provider <p>` (default `anthropic`). Replace **every**
      `anthropic` literal: the `invalidate` call, the poll loop's
      `.provider == "anthropic"` test, the report filter, and the
      `lim("anthropic:5h")`/`lim("anthropic:7d")` lookups (now by
      `.window.id` `5h`/`7d`, plus `monthly` when present). Messages name the
      provider. Model-scoped 7d windows stay Anthropic-only.
- [ ] `account_check`: for a non-Anthropic provider, report
      `match: omp reads its own <provider> login`, with a comment saying why
      the org-mismatch check does not apply.
- [ ] Fixtures copied from a live `omp usage --provider opencode-go --json`
      capture with the real ids: `go-provider-go.json`,
      `go-provider-sleep-5h.json`, `go-provider-monthly-stop.json`. Existing
      Anthropic fixtures stay green unchanged.
- [ ] `SKILL.md` step 5: default worker `omp` + DeepSeek, Claude as override.
      Step 8 confirm prints model, gated provider and its thresholds.

## Phase 2 — Trustworthy results (R1, runner tests, R5)

- [ ] `build_gate` takes a mode: `full` (typecheck, build, lint, test) for the
      ticket gate, `static` (no test) for `-after-stash`. The report says
      which check went red.
- [ ] Preflight step 4 also runs the test command once on the fresh branch,
      under the same `CHECK_TIMEOUT_SECS` (20 min) as every gate command; red
      or timed out aborts.
- [ ] Protected-paths check `protected_hits` over every changed path
      (tracked and untracked), against `PROTECTED_RE` (default:
      `(^|/)\.env(\.|$)`, `\.pem$`, `\.key$`, `(^|/)id_(rsa|ed25519)`,
      `(^|/)\.git/`, `^\.github/workflows/`; `OVERNIGHT_PROTECTED_RE`
      overrides). It runs **once per attempt, before any patch, stash or
      commit**. A hit fails the ticket as terminal, lists the paths, and
      removes those files before stashing, so secrets never reach a patch, a
      stash or a retry brief.
- [ ] Classify each failure per the taxonomy. A transient failure with
      `(.retries // {})[N] < MAX_RETRIES` and room for one more
      `TICKET_TIMEOUT_SECS` before the deadline:
      1. capture the attempt in one step (`git add -A` then
         `git diff --cached --binary HEAD > logs/<N>-attempt<k>.patch`);
      2. write the handoff note;
      3. then reset: stash as today (default mode) or drop and reopen the
         worktree (PR mode);
      4. increment `retries[N]`; leave N in the queue for the normal
         frontier pick, never force it to the front.
      Otherwise fail as today; dependents are skipped only on a final failure.
- [ ] Before a retry worker starts, `git apply --index` the saved patch; on
      failure, reset and start clean, noting it in the handoff.
- [ ] Report: per-ticket `attempts`, the final failure's class, the patch and
      handoff paths.

## Phase 3 — Better inputs (R2, R3)

- [ ] One function extracts acceptance criteria from an issue body: the
      bullets/checklist under the first heading matching
      `/acceptance criteria|done when/i`. No state is stored: `--dry-run`
      fetches bodies and lists tickets with none (`SKILL.md` step 8 shows the
      list and asks include/exclude inside the single confirmation);
      `render_brief` fetches the body again and fills `{{DONE_WHEN}}`, falling
      back to "the ticket's acceptance criteria as written".
- [ ] `worker-brief.md`: the `## Done when` block, plus a get-bearings step
      before implementing: read `{{HANDOFF}}` when it is not `none` (and note
      the tree already holds the previous attempt), run
      `git log --oneline -10`, run the checks once for a baseline.
- [ ] Handoff note `logs/<N>.handoff.md`, written only on a retry and on a
      final failure: attempt number, reason, diff stat, last 40 lines of the
      red check log, the worker's `notes` and `unmet_criteria`, patch path.

## Phase 4 — Operability (R4, R6)

- [ ] `notify <title> <msg>`: `osascript -e 'display notification …'` when
      `osascript` exists and `OVERNIGHT_NOTIFY` ≠ 0; errors ignored. Called
      from `stop()` (every stop reason) and the `on_exit` abort path.
- [ ] `open_worktree`: a failed `setup` returns nonzero instead of `stop`;
      `run_ticket` treats it as the transient `setup failed` reason.
- [ ] `SKILL.md`: document the DeepSeek default, the provider gate,
      notifications, retries, the test gate, protected paths, the report's new
      fields, "delete `.scratch/overnight/state.json` to start over", and
      that on a work machine (no OMP config) the gate reads unknown and the
      run caps at `FALLBACK_MAX_TICKETS`.

## Phase 5 — Verification

- [ ] `scripts/test-overnight-runner.sh` (permanent; picked up by `check.sh`):
      a temp git repo with stub `gh` (fixed issues, bodies, blocked_by) and
      stub `omp` on `PATH` whose behavior is set per ticket; `USAGE_GATE_JSON`
      pins the gate. Assert:
      - transient failure → retried once with the patch pre-applied → committed;
      - second transient failure → failed, patch + handoff written, dependents
        skipped;
      - a retried ticket with a queued dependent: the dependent never runs
        before the retry settles;
      - `blocked` is never retried;
      - protected path → terminal, nothing committed, the file absent from
        the stash and every patch;
      - red test fails its ticket but does not halt the run;
      - setup failure fails only its ticket (PR mode; stub `git push` and
        `gh pr create`);
      - model/worker matrix: DeepSeek → Go gate; `omp` + `anthropic/…` →
        Anthropic gate; `claude` + DeepSeek refused; `omp` + no model refused;
      - `--resume` on a `state.json` without `retries` continues.
- [ ] `scripts/test-overnight-usage-gate.sh` green with the Go fixtures,
      including the monthly hard stop with `durationMs` null.
- [ ] Live `usage-gate.sh --provider opencode-go` prints a `go:` reading
      with the 5h, weekly and monthly windows.
- [ ] `--dry-run` against a real repo's ready-for-agent queue shows the
      DeepSeek model, the Go gate and the no-criteria list.
- [ ] `scripts/check.sh` green.

## Risks

- DeepSeek V4.1 Flash is weaker than Opus at from-scratch implementation; the
  retry and runner test gate are what keep bad `done` claims out of commits.
  Expect more `partial`/failed tickets than a Claude worker would produce.
- Overnight runs now spend the shared Go cap. The weekly pace stop protects
  daytime `scout`/`adversary`/`commit`; the monthly hard stop protects the
  $60 cap.
- Criteria extraction is heuristic; a miss only produces a confirm-time
  warning, never a skipped ticket without the user's say.
