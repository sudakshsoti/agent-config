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
   `docs/agents/triage-labels.md` and any build-order or wave doc, if one
   exists. The run order comes from the issue labels and issue numbers; a wave
   doc's order and exclusions override issue-number order.
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
     Otherwise ask once: `--resume` it, or start over (both in `references/runbook.md`).
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
     session's environment. Example: `anthropic/claude-opus-5-5:high`, for a
     harder queue than the Sonnet default.
   - The model must be an exact `omp models` selector, optionally with a
     `:<thinking>` suffix. `~`-prefixed aliases are not accepted.
   - `--worker claude` takes an Anthropic model, or the same default. It
     always runs headless.
   - The usage gate follows the model's provider. It needs `5h` and `7d`
     windows, so `xai-oauth` (SuperGrok reports weekly/monthly only) cannot
     pass it; keep overnight workers on Anthropic.
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
   `visible` line), the dry run's `limits` and `thresholds` lines verbatim, the
   tickets without
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

Per ticket, strictly serial: usage gate → one fresh worker → protected-paths
check → build gate → commit `<subject> (#N)` on pass, then push and PR. Read
`references/runbook.md` when the user asks about failures, retries, protected
paths, the usage gate, a stop, a resume, starting over or the morning report.

**Git policy:** one branch, one commit and one PR per passed ticket, none on
the base.

- Branch `<prefix>/<N>`. No in-run blocker: from `origin/<base>`, PR against
  the base. One completed in-run blocker: stacked on that blocker's branch, PR
  against that branch. Several: from the base with their branches merged in
  (`git merge`; a conflict, like any branch setup failure, fails only that
  ticket, as a temporary failure, so it gets its one retry), PR against the
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
- Stacked PRs merge bottom-up with merge commits or rebase-merge, never squash.
