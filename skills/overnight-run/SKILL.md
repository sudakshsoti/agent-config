---
name: overnight-run
description: "Use only when the user asks for an overnight, AFK, or unattended run: works ready-for-agent tickets serially, one fresh /implement worker per ticket, behind a usage gate. Not for a single plan checklist (execute-plan) or dependent workstreams (workstreams)."
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
(default none), the worker harness, and the optional visibility mode:

- **Visible** (the default for an OMP worker inside herdr; `--headless` opts out, `--visible` forces it): each worker runs as
  the interactive omp TUI in its own herdr tab, so a human can watch it. The
  tab closes when the worker writes its result file, goes quiet for 60 s after
  a terminal turn, or hits the timeout. Transcripts go to
  `.scratch/overnight/sessions/`. A claude worker is always headless; the dry
  run's `visible` line says which mode the run uses.

## Preflight

This session keeps tracker access read-only: `gh issue list/view` and `gh api`
GETs only. The runner alone pushes branches and opens PRs, and the user's yes
in step 8 covers both. Run the steps in order; a failed check ends the
preflight with a report. Questions to the user are not failures.

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
   - `git fetch origin`. The base is the repo's default branch
     (`gh repo view --json defaultBranchRef --jq .defaultBranchRef.name`),
     normally `main`. The runner branches from `origin/<base>` and never
     `git switch <base>`: this checkout may be a worktree, with the base
     checked out elsewhere. If `git rev-list --count origin/<base>..<base>` is
     non-zero, report the unpushed commits and ask once: push them first, or
     continue without them.
   - **Publishing works.** The run pushes and opens PRs, so before step 8:
     `origin` exists, `gh auth status` succeeds, and `gh repo view --json
     viewerPermission --jq .viewerPermission` prints `WRITE`, `MAINTAIN` or
     `ADMIN`. Otherwise stop and report that `gh` lacks write access.
   - `.scratch/overnight/` is ignored: if `git check-ignore -q
     .scratch/overnight/x` fails, append `/.scratch/overnight/` to
     `$(git rev-parse --git-path info/exclude)`.
   - If `.scratch/overnight/state.json` exists: when its `pid` is alive and
     its `stop_reason` is null, a run is in progress; stop and report it.
     Otherwise ask once: `--resume` it, or start over (see Morning).
   - Branch prefix: `overnight/<YYYY-MM-DD>`, or `-2`, `-3`, … when any
     `refs/heads/<prefix>` or `refs/heads/<prefix>/*` (local or on `origin`)
     already exists. No run branch is created: each ticket gets
     `<prefix>/<N>`.
   - Install dependencies, then run typecheck, build and lint once, and the
     test command once under a 20-minute limit. Abort if any is red or times
     out.
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
   {"prefix": "overnight/2026-09-28", "base": "main", "queue": [12, 14, 15],
    "waived": [[15, 9]],
    "checks": {"typecheck": "...", "build": "...", "lint": "...", "test": "..."}}
   ```

   `waived` holds `[issue, blocker]` pairs the user agreed to ignore.
   `worker_model` is optional (`provider/model[:level]`); absent means omp's
   `modelRoles.task`.
7. **Dry run.** `"$S/overnight.sh" --dry-run --worker <w> --deadline <HH:MM>
   [--max-tickets N] [--headless]`. It runs `usage-gate.sh` once for
   the worker's provider, checks the account, and prints the model with its
   source and the `omp models` check, the gated provider, a `visible` line,
   the `gh access` line, thresholds, run order with each ticket's branch and
   PR base, and the tickets with no extractable acceptance
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
   the ticket's own wording), and the git policy below.
   Wait for one explicit yes.
9. **Launch and exit.** The command always carries `--worker <w>` and the dry
   run's `--visible` or `--headless` explicitly, so the launched run cannot
   resolve them differently. `<run>` is the branch prefix with `/` replaced by
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
stash (typecheck + build + lint, no test) halts the run. A pass also pushes the
ticket's branch and opens its PR.

- **Protected paths.** Env files, `*.pem`, `*.key`, SSH private keys,
  `.git/` and `.github/workflows/` (`OVERNIGHT_PROTECTED_RE` overrides the
  pattern). A change fails the ticket permanently; the files are removed
  before any patch, stash or commit, so they never reach them.
- **Failures.** Temporary (timeout, worker crash, no final JSON, red checks,
  `partial`) get one retry: the attempt is saved as a patch
  and a handoff note (`logs/<N>.handoff.md`), the tree is reset (stashed as
  `overnight #N attempt <k>`), and when the ticket's turn comes the patch is
  reapplied before the worker starts. A patch that no longer applies means a
  clean start, noted in the handoff. Permanent failures (`blocked`, `done`
  with no changes, protected paths, refused commit) fail at once. A final
  failure is stashed as `overnight #N` and
  skips its dependents; a retry does not. A retry only starts when a whole
  attempt fits before the deadline. A ticket that fails or is requeued leaves
  no branch: the runner returns to `origin/<base>`, deletes the ticket's
  branch and restarts it from the base.
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

**Git policy:** one branch, one commit and one PR per passed ticket, none on
the base.

- Branch `<prefix>/<N>`. No in-run blocker: from `origin/<base>`, PR against
  the base. One completed in-run blocker: stacked on that blocker's branch, PR
  against that branch. Several: from the base with their branches merged in
  (`git merge`; a conflict fails the ticket with that reason), PR against the
  base naming the PRs it contains.
- After the gate passes and the commit lands, the runner pushes the branch and
  opens a ready-for-review PR titled with the commit subject. The body says
  `Closes #N` and summarises the worker's checks, unmet criteria, routes to
  check and notes. It carries no agent attribution. The issue closes only when
  a human merges the PR into the default branch.
- **Nothing is merged.** No code path merges a PR or enables auto-merge. The
  worker is read-only on git and GitHub. No issue is commented on, labelled or
  closed, and nothing is deployed.
- A push or PR failure does not fail a green ticket: it is done with no PR and
  a publish error, and `--resume` retries publishing for every such ticket
  without re-running a worker.
- Between tickets the checkout is detached at `origin/<base>`.

## Morning

The report is `.scratch/overnight/<YYYY-MM-DD>.md`; it documents itself
(queue, per-ticket outcome, failures, stop reason). Read it first. Its
**Pull requests** section lists each ticket's branch, PR base and PR link (or
the publish error), then states the stacking order. Review and merge
bottom-up, with merge commits or rebase-merge: a squash forces conflicts in
the PRs above it. The runner merges nothing.

**Stopping.** `"$S/overnight.sh" --stop` from the repo ends the run after the
current ticket, or wakes it from a usage sleep. It writes the report and
exits 0. For an immediate abort, `kill -TERM "$(jq .pid
.scratch/overnight/state.json)"`; the interrupted ticket is stashed on
`--resume`. The `<N>-attempt<k>.patch` files and handoffs in `logs/` are kept
on purpose, for retries and the report.

To continue an interrupted or stopped run: `"$S/overnight.sh" --resume
[--deadline HH:MM] [--visible|--headless]`, launched the same way. A mode flag
given on resume stays on; the state remembers the mode and the model of the
original run. Resuming also retries publishing for every done ticket that has
no PR. To start over, `mv` `.scratch/overnight/state.json` to
`.scratch/overnight/state.prev-<YYYYMMDD-HHMMSS>.json`.
