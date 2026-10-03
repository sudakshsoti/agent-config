# Overnight run: runbook

Read this when the user asks what the script does, why a ticket failed or was
requeued, how to stop, resume or start over, or how to read the morning report.
The preflight and the git policy stay in `SKILL.md`.

`S` is the skill's `scripts/` directory, as defined in `SKILL.md`.

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
  `partial`, branch setup failure) get one retry: the attempt is saved as a patch
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
window, 30 unknown. The thresholds live at the top of that file, and the dry
run prints them.

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

**Resuming.** To continue an interrupted or stopped run: `"$S/overnight.sh"
--resume [--deadline HH:MM] [--visible|--headless]`, launched the same way as
in `SKILL.md` step 9. A mode flag given on resume stays on; the state
remembers the mode and the model of the original run. Resuming also retries
publishing for every done ticket that has no PR.

**Starting over.** `mv` `.scratch/overnight/state.json` to
`.scratch/overnight/state.prev-<YYYYMMDD-HHMMSS>.json` (deleting it works
too); the next launch then begins a fresh run.
