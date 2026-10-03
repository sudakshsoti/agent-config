---
name: overnight-run
description: "Run ready-for-agent tickets unattended and serially, one fresh /implement worker per ticket, behind a usage gate. Invoke only when the user asks for an overnight, AFK or unattended run."
disable-model-invocation: true
---

# Overnight run

Automate "/implement per ticket, fresh context between each" for tickets that
`/to-tickets` already made agent-ready. There is no grilling, spec, triage or
design work here.

This session does the **preflight** only. It then starts `overnight.sh` in a
detached terminal multiplexer (the operator's choice; tmux is the example) and
ends. The script owns all looping, waiting, killing, committing and stashing,
and on macOS it holds its own idle-sleep assertion; this session never sleeps
and never implements.

`S` is this skill's `scripts/` directory: the `scripts/` folder beside this
`SKILL.md`, wherever the harness installed it. Derive it from this file's path
and quote it; never hard-code a per-harness home path.

Arguments, if given, preset the deadline (default 07:00), a max-tickets cap
(default none), the worker harness, and the two optional modes:

- **Visible** (the default for an OMP worker inside herdr; `--headless` opts out, `--visible` forces it): each worker runs as
  the interactive omp TUI in its own herdr tab, so a human can watch it. The
  tab closes when the worker writes its result file, goes quiet for 60 s after
  a terminal turn, or hits the timeout. Transcripts go to
  `.scratch/overnight/sessions/`. A claude worker is always headless; the dry
  run's `visible` line says which mode the run uses.
- **PR per ticket** (`--pr-per-ticket`): each ticket runs in its own worktree
  at `<repo>-overnight/<N>` on `ticket/<N>-<slug>`. Every worktree stacks on
  the previous passed ticket's branch; the first one stacks on `origin/main`.
  A passing ticket is committed, pushed and opened as a **draft** PR against
  its base. A failing ticket keeps its worktree for inspection. Pushing and
  opening PRs are external side effects, so this mode needs the user's
  explicit yes.

## Preflight

Keep tracker access read-only for the whole run: `gh issue list/view` and
`gh api` GETs only. Run the steps in order; a failed check ends the preflight with a report.
Questions to the user are not failures.

1. **Read the rules.** Read `AGENTS.md`, `docs/agents/issue-tracker.md`,
   `docs/agents/triage-labels.md` and any build-order or wave doc (e.g.
   `docs/agents/work-order.md`). The wave doc's order and exclusions override
   issue-number order.
2. **Build the run set.** Take the open issues labelled with the repo's
   ready-for-agent label. Remove spec and parent issues, and anything the docs
   defer, hold or reserve for a human. Order by the wave doc, else by issue
   number. Read each issue's blockers with
   `gh api repos/{owner}/{repo}/issues/<N>/dependencies/blocked_by`. List the
   issues blocked by a ready-for-human issue and ask once whether to waive
   those edges. The run set is done when every remaining issue is either in
   the queue or excluded with a stated reason.
3. **Find the checks.** Read the typecheck, build, lint and test commands from
   the package scripts or `AGENTS.md`. Show them. A command the repo does not
   have is `""` (n/a); ask about any you cannot find instead of inventing one.
4. **Prepare git.**
   - The tree is clean (`git status --porcelain` prints nothing).
   - `git fetch origin`. Base the run on `origin/main` and never
     `git switch main`: this checkout may be a worktree, with `main` checked
     out elsewhere. If `git rev-list --count origin/main..main` is non-zero,
     report the unpushed commits and ask once: push them first, or base on
     `main`.
   - `.scratch/overnight/` is ignored: if `git check-ignore -q
     .scratch/overnight/x` fails, append `/.scratch/overnight/` to
     `$(git rev-parse --git-path info/exclude)`.
   - If `.scratch/overnight/state.json` exists: when its `pid` is alive and
     its `stop_reason` is null, a run is in progress; stop and report it.
     Otherwise ask once: `--resume` it on its branch, or start over (the `mv`
     is in Morning).
   - Run branch: `overnight/<YYYY-MM-DD>`, or `-2`, `-3`, … when
     `git show-ref -q --verify refs/heads/<name>` finds the name taken.
     `git switch --no-track -c <run-branch> origin/main` (or `main`, if chosen
     above); `--no-track` stops the branch from tracking `origin/main`.
   - Install dependencies, then run typecheck, build and lint once, and the
     test command once under a 20-minute limit. Abort if any is red or times
     out. In PR-per-ticket mode this checkout only holds
     `.scratch/overnight/`; the tickets branch from `origin/main`.
5. **Pick the worker.** Default: `omp` with omp's `modelRoles.task`
   (`omp config get modelRoles --json | jq -r .value.task`). Leave
   `worker_model` out of plan.json and the script resolves it; show the
   value the dry run prints.
   - An override goes in plan.json `worker_model`, never in
     `OVERNIGHT_WORKER_MODEL`: the multiplexer launch does not inherit this
     session's environment. Example: `opencode-go/deepseek-v4.1-flash:high`,
     to spend the OpenCode Go allowance instead of Anthropic.
   - The model must be an exact `omp models` selector, optionally with a
     `:<thinking>` suffix. `~`-prefixed aliases are not accepted.
   - `--worker claude` takes an Anthropic model, or the same default. It
     always runs headless.
   - The usage gate follows the model's provider.
6. **Write the plan** to `.scratch/overnight/plan.json`:

   ```json
   {"branch": "overnight/2026-09-28", "queue": [12, 14, 15],
    "waived": [[15, 9]],
    "checks": {"typecheck": "...", "build": "...", "lint": "...", "test": "..."},
    "setup": "npm ci"}
   ```

   `waived` holds `[issue, blocker]` pairs the user agreed to ignore.
   `worker_model` is optional (`provider/model[:level]`); absent means omp's
   `modelRoles.task`. `setup`
   installs dependencies in each new worktree and is used only with
   `--pr-per-ticket`; ask for it if the repo's install command is unclear.
7. **Dry run.** `"$S/overnight.sh" --dry-run --worker <w> --deadline <HH:MM>
   [--max-tickets N] [--headless] [--pr-per-ticket]`. It runs `usage-gate.sh` once for
   the worker's provider, checks the account, and prints the model with its
   source and the `omp models` check, the gated provider, a `visible` line,
   thresholds, run order and the tickets with no extractable acceptance
   criteria. A model missing from `omp models` stops the dry run: fix
   `worker_model` and rerun. If the account line says `mismatch` or
   `unknown`, or the gate exits 30, say so: the run then stops after
   `FALLBACK_MAX_TICKETS` (4) tickets.
8. **Confirm once.** Show one summary: the ordered queue, the worker command,
   the model and the provider being gated, the visibility (the dry run's
   `visible` line), the thresholds (5h sleep at 70%; 7d
   stop when 15+ points over elapsed pace past 5% elapsed, or at 90%; for Go
   also a monthly hard stop at 90%), the caps (45 min per ticket, max
   tickets, fallback cap), the deadline (default 07:00), the tickets without
   acceptance criteria (ask include or exclude for each; included ones run on
   the ticket's own wording), and the git policy below for the chosen mode.
   Wait for one explicit yes.
9. **Launch and exit.** The command always carries `--worker <w>` and the dry
   run's `--visible` or `--headless` explicitly, so the launched run cannot
   resolve them differently. `<run>` is the run branch with `/` replaced by
   `-`, which keeps the name unique per same-day run.

   The command is the same on macOS and Linux. Host it in any multiplexer
   that keeps a detached command alive; the operator picks. With tmux:

   ```bash
   tmux new-session -d -s "<run>" -c "$PWD" \
     "'$S/overnight.sh' --worker <w> --deadline <HH:MM> --visible|--headless [flags] 2>&1 | tee -a .scratch/overnight/run.log"
   ```

   Inside herdr (`HERDR_ENV=1`) use a tab instead: create it with
   `herdr tab create --workspace "$HERDR_WORKSPACE_ID" --cwd "$PWD" --label
   <run> --no-focus` and send the same `'$S/overnight.sh' …` command to its
   root pane with `herdr pane run <pane> "<command>"`.

   Print how to attach (`tmux attach -t <run>`, the herdr tab or the
   operator's multiplexer equivalent), the report path, and the stop command
   `"$S/overnight.sh" --stop`, run from the repo. On macOS also remind the
   user that the run prevents only idle sleep (stay on power with the lid
   open); say nothing about it on other hosts. Then end the session.

## What the script does

Per ticket, strictly serial: usage gate → one fresh worker running
`worker-brief.md` with a 45-minute wall clock → protected-paths check → build
gate (typecheck + build + lint + **test**) → commit `<subject> (#N)` on pass.
Rate-limited workers are reset and requeued, never failed. A red build after a
stash (typecheck + build + lint, no test) halts the run. In PR-per-ticket mode
the worker and the gate run in the ticket's worktree; a pass also pushes the
branch and opens the draft PR.

- **Protected paths.** Env files, `*.pem`, `*.key`, SSH private keys,
  `.git/` and `.github/workflows/` (`OVERNIGHT_PROTECTED_RE` overrides the
  pattern). A change fails the ticket permanently; the files are removed
  before any patch, stash or commit, so they never reach them.
- **Failures.** Temporary (timeout, worker crash, no final JSON, red checks,
  `partial`, setup failed) get one retry: the attempt is saved as a patch
  and a handoff note (`logs/<N>.handoff.md`), the tree is reset (stashed as
  `overnight #N attempt <k>`), and when the ticket's turn comes the patch is
  reapplied before the worker starts. A patch that no longer applies means a
  clean start, noted in the handoff. Permanent failures (`blocked`, `done`
  with no changes, protected paths, refused commit) fail at once. A final
  failure is stashed as `overnight #N` (PR mode keeps the worktree) and
  skips its dependents; a retry does not. A retry only starts when a whole
  attempt fits before the deadline. A failed worktree setup fails only its
  ticket.
- **Notification.** A macOS notification fires on every stop, aborts
  included; `OVERNIGHT_NOTIFY=0` silences it.
- **Model rejected.** A worker that exits non-zero with a model-not-found
  error stops the whole run (`stop_reason` "worker model … rejected"). The
  ticket is neither failed nor retried; fix the model and `--resume`.

The gate (`usage-gate.sh --provider <p>`) reads `omp usage --provider <p>
--json` after an `invalidate`, for the provider of the worker's model. Exit 0
go, 10 sleep until the 5h reset + 120 s, 20 stop on a weekly or monthly
window, 30 unknown. Thresholds live at the top of that file. On a work
machine without OMP config the gate reads unknown, so the run caps at
`FALLBACK_MAX_TICKETS` (4) tickets.

**Git policy (default):** one run branch, one commit per ticket. Nothing is
pushed, merged, deployed or opened as a PR, and no issue is commented on,
labelled or closed; progress lives in `.scratch/overnight/state.json`.

**Git policy (`--pr-per-ticket`):** one branch, commit and draft PR per passed
ticket. Each PR body says `Closes #N`, so the issue closes only when a human
merges the PR into the default branch. Nothing is merged or deployed, and the
tracker is not written to. Merge the stack bottom-up with merge commits or
rebase-merge: a squash forces conflicts in the PRs above it.

## Morning

The report is `.scratch/overnight/<YYYY-MM-DD>.md`; it documents itself
(queue, per-ticket outcome, failures, stop reason). Read it first.

**Stopping.** `"$S/overnight.sh" --stop` from the repo ends the run after the
current ticket, or wakes it from a usage sleep. It writes the report and
exits 0. For an immediate abort, `kill -TERM "$(jq .pid
.scratch/overnight/state.json)"`; the interrupted ticket is stashed on
`--resume`. The `<N>-attempt<k>.patch` files and handoffs in `logs/` are kept
on purpose, for retries and the report.

To continue an interrupted or stopped run on the same branch:
`"$S/overnight.sh" --resume [--deadline HH:MM] [--visible|--headless] [--pr-per-ticket]`,
launched the same way. A mode flag given on resume stays on; the state
remembers the modes and the model of the original run. To start over, `mv`
`.scratch/overnight/state.json` to `.scratch/overnight/state.prev-<YYYYMMDD-HHMMSS>.json`.
