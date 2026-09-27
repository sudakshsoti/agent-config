---
name: overnight-run
description: "Run ready-for-agent tickets unattended and serially, one fresh /implement worker per ticket, behind a usage gate. Invoke only when the user asks for an overnight, AFK or unattended run."
disable-model-invocation: true
---

# Overnight run

Automate "/implement per ticket, fresh context between each" for tickets that
`/to-tickets` already made agent-ready. There is no grilling, spec, triage or
design work here.

This session does the **preflight** only. It then starts `overnight.sh` in tmux
under `caffeinate -i` and ends. The script owns all looping, waiting, killing,
committing and stashing; this session never sleeps and never implements.

`S` is this skill's `scripts/` directory: `~/.claude/skills/overnight-run/scripts`
in Claude Code, `~/.agents/skills/overnight-run/scripts` in OMP.

Arguments, if given, preset the deadline (default 07:00), a max-tickets cap
(default none) and the worker harness.

## Preflight

Keep tracker access read-only for the whole run: `gh issue list/view` and
`gh api` GETs only. Run every step; stop at the first failure and report it.

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
   - `git fetch origin && git switch main && git merge --ff-only origin/main`.
   - `.scratch/overnight/` is ignored: if `git check-ignore -q
     .scratch/overnight/x` fails, append `/.scratch/overnight/` to
     `$(git rev-parse --git-path info/exclude)`.
   - `git switch -c overnight/<YYYY-MM-DD>`, install dependencies, then run
     typecheck, build and lint once. Abort if any is red.
5. **Pick the worker.** Default to the harness running this session (`claude`
   in Claude Code, `omp` in OMP); offer the other as an override.
6. **Write the plan** to `.scratch/overnight/plan.json`:

   ```json
   {"branch": "overnight/2026-09-28", "queue": [12, 14, 15],
    "waived": [[15, 9]],
    "checks": {"typecheck": "...", "build": "...", "lint": "...", "test": "..."}}
   ```

   `waived` holds `[issue, blocker]` pairs the user agreed to ignore.
7. **Dry run.** `"$S/overnight.sh" --dry-run --worker <w> --deadline <HH:MM>
   [--max-tickets N]`. It runs `usage-gate.sh` once, compares
   `claude auth status` with the account `omp usage` reports, and prints the
   run order. If the account line says `mismatch` or `unknown`, or the gate
   exits 30, say so: the run then stops after `FALLBACK_MAX_TICKETS` (4)
   tickets.
8. **Confirm once.** Show one summary: the ordered queue, the worker command,
   the thresholds (5h sleep at 70%, 7d stop at 60%), the caps (45 min per
   ticket, max tickets, fallback cap), the deadline (default 07:00), and the
   git policy below. Wait for one explicit yes.
9. **Launch and exit.**

   ```bash
   tmux new-session -d -s "overnight-<YYYY-MM-DD>" -c "$PWD" \
     "caffeinate -i '$S/overnight.sh' --worker <w> --deadline <HH:MM> 2>&1 | tee -a .scratch/overnight/run.log"
   ```

   Print `tmux attach -t overnight-<YYYY-MM-DD>` and the report path, remind
   the user that `caffeinate -i` prevents only idle sleep (stay on power with
   the lid open), then end the session.

## What the script does

Per ticket, strictly serial: usage gate → one fresh worker running
`worker-brief.md` with a 45-minute wall clock → build gate (typecheck + build
+ lint) → commit `<subject> (#N)` on pass, or `git stash push -u -m
"overnight #N"` on fail, which marks the ticket failed and its dependents
skipped-blocked. Rate-limited workers are reset and requeued, never failed.
A red build after a stash halts the run.

The gate (`usage-gate.sh`) reads `omp usage --provider anthropic --json` after
an `invalidate`. Exit 0 go, 10 sleep until the 5h reset + 120 s, 20 stop on a
weekly window, 30 unknown. Thresholds live at the top of that file.

**Git policy:** one run branch, one commit per ticket. Nothing is pushed,
merged, deployed or opened as a PR, and no issue is commented on, labelled or
closed; progress lives in `.scratch/overnight/state.json`.

## Morning

The report is `.scratch/overnight/<YYYY-MM-DD>.md`: planned vs actual queue,
per-ticket status, SHA, duration and unmet criteria, failures with stash
names, skipped tickets with blockers, usage readings, the stop reason and the
routes to check visually.

To continue an interrupted or stopped run on the same branch:
`"$S/overnight.sh" --resume [--deadline HH:MM]`, launched the same way.
