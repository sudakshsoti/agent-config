# Overnight-run improvements: current state, comparable workflows, ranked ideas (2026-09-29)

Question: the repo-owned `overnight-run` skill (`skills/overnight-run/`) runs
agent-ready tickets unattended and serially. What does it currently do, what do
comparable unattended/long-running agent workflows do better, and which concrete
improvements should the skill adopt?

Direct answer: the skill is a solid serial loop (usage gate → fresh worker →
build gate → commit-or-stash → morning report) with unusually good quota pacing
and resume semantics for a local script. Its biggest gaps, measured against
primary sources, are (1) no failure classification or retry — one flaky ticket
fails permanently and cascades `skipped-blocked` through its dependents; (2) no
cross-ticket progress memory beyond machine-readable `state.json`; (3) no
notification on completion; (4) serial-only execution despite computing a
dependency DAG it could parallelize; (5) prompt-only safety boundaries with one
deterministic guard. The top quick wins are a retry tier for transient failures,
a "done-when" brief block, a per-ticket handoff note, an `osascript`
completion notification, and a runner-side protected-paths check — all S effort,
all inside existing files.

Prior research this builds on (not repeated): the skill-vs-cloud ranking and
PR-per-issue gap in `docs/research/overnight-issue-runner-options-2026-09.md`;
headless flags, usage surfaces, and `-p` wait limits in
`docs/research/claude-code-overnight-primitives-2026-09.md`; the pace formula,
thresholds, and fixtures in `docs/research/claude-usage-pacing-2026-09.md`; the
Muse training-eligible tier and quota pools in
`docs/research/muse-code-subscription-2026-09.md`. All repo-path citations below
are read 2026-09-29 against the current checkout.

## 1. Current state (with file:line)

### What the skill does

The invoking session does **preflight only**, then launches `overnight.sh` under
tmux (or a herdr tab) with `caffeinate -i` and exits; the script owns all
looping, waiting, killing, committing, and stashing
(`skills/overnight-run/SKILL.md` ll.13–16). Nine preflight steps run in order
and stop at the first failure (`SKILL.md` ll.37–40): read repo rules, build the
run set from the ready-for-agent label minus spec/parent/deferred issues,
ordered by wave doc or issue number, with `blocked_by` edges the user may waive
once (`SKILL.md` ll.42–53); read check commands, asking rather than inventing
(`SKILL.md` ll.54–56); clean tree, ff-only sync to `origin/main`, git-ignore
`.scratch/overnight/`, branch `overnight/<date>`, install deps, and run
typecheck/build/lint once, aborting if red (`SKILL.md` ll.57–66); pick the
worker harness (`SKILL.md` ll.67–68); write `.scratch/overnight/plan.json`
(queue, waived edges, checks, per-worktree setup) (`SKILL.md` ll.69–80);
`--dry-run` (usage gate + `claude auth status` vs `omp usage` account check +
run order; mismatch/unknown caps the run at `FALLBACK_MAX_TICKETS` = 4)
(`SKILL.md` ll.81–86); one explicit confirmation of queue, worker command,
thresholds, caps, deadline, and git policy (`SKILL.md` ll.87–90); launch and
exit with attach instructions and the lid-open warning (`SKILL.md` ll.91–105).

Per ticket, strictly serial: usage gate → one fresh worker running
`worker-brief.md` under a 45-minute wall clock → build gate (typecheck + build
+ lint; test goes to the worker only) → commit `<subject> (#N)` on pass, or
`git stash push -u -m "overnight #N"` on fail, which marks the ticket failed
and its dependents `skipped-blocked`; rate-limited workers are reset and
requeued, never failed; a red build after a stash halts the run
(`SKILL.md` ll.107–116; `scripts/overnight.sh` ll.587–718). The gate reads
`omp usage --provider anthropic --json` after `invalidate`: exit 0 go, 10 sleep
until 5h reset + 120 s, 20 stop on a weekly window, 30 unknown
(`SKILL.md` ll.118–120; `scripts/usage-gate.sh` ll.15–23). Default git policy is
one run branch, one commit per ticket, nothing pushed/merged/deployed, no
tracker writes (`SKILL.md` ll.122–124); `--pr-per-ticket` stacks one
worktree/branch/draft-PR per passed ticket off the previous pass and keeps
failed worktrees for inspection (`SKILL.md` ll.29–35, 126–130;
`scripts/overnight.sh` ll.540–585). The morning report
(`.scratch/overnight/<date>.md`) covers planned vs actual queue, per-ticket
status/SHA-or-PR/duration/unmet-criteria, failures with stash names or worktree
paths, skipped tickets with blockers, usage readings, stop reason, and visual
routes (`SKILL.md` ll.132–137; `scripts/overnight.sh` ll.428–466). An
interrupted run continues with `--resume` on the same branch, preserving modes
(`SKILL.md` ll.139–142; `scripts/overnight.sh` ll.723–729, 824–838).

Notable engineering already in the script: process-group kills via job control
(`set -m`, TERM then KILL after `KILL_GRACE_SECS`), which is the macOS-legal
answer to "no GNU timeout" (`scripts/overnight.sh` ll.272–300;
`AGENTS.md` ll.125–126); a jq dependency-frontier (`settle`/`pick`) with
cycle detection (`scripts/overnight.sh` ll.341–375); deterministic repair when
a worker violates the no-commit rule (fold commits back into the tree) or
leaves its branch (`scripts/overnight.sh` ll.619–624); account-mismatch
downgrade of the gate to unknown (`scripts/overnight.sh` ll.180–191);
`--visible` finish detection on result-file, tab-close, timeout, or 60 s of
transcript quiet after a terminal turn (`scripts/overnight.sh` ll.224–266);
and an `on_exit` trap that records an abort reason and still writes the report
(`scripts/overnight.sh` ll.479–492).

The worker brief (`scripts/worker-brief.md`, full file 61 lines) sets read-only
git/tracker boundaries, bans subagents/deploys, defines the `done/partial/
blocked` final-JSON contract, and requires implement-skill flow, checks,
browser route listing, and a code-review self-pass
(`scripts/worker-brief.md` ll.12–26, 28–61).

### Gaps and risks

1. **No failure classification or retry for ordinary failures.** Any non-rate-limit
   failure — flaky test, timeout with 90% of the work done, missing final JSON,
   empty diff, red build gate, `git commit` hook refusal — is recorded once and
   the ticket is failed permanently (`scripts/overnight.sh` ll.656–717). Only
   rate-limit text earns a requeue (ll.639–647, `MAX_REQUEUES=3` at l.55).
   Dependents then cascade to `skipped-blocked` via the frontier (ll.341–356),
   so one flaky leaf can poison its subtree for the night. [INFERENCE — severity
   assessment; mechanics cited.]
2. **No resume within a ticket.** A timed-out or killed worker's partial work is
   stashed (or its worktree dropped on requeue, l.496–503) and the next attempt
   — which only happens for rate limits — starts cold. There is no
   progress-file or diff-summary handoff into a retried brief, unlike the
   progress-log pattern in §2.
3. **No cross-ticket memory for workers.** Each worker gets the issue plus a
   fresh brief; `state.json` is machine state (queue/SHAs/usage), not narrative
   handoff. A worker that needs "what did the previous ticket decide" must
   re-derive it from git log, which the brief does not even instruct (contrast
   the get-up-to-speed checklist in §2).
4. **Serial-only despite computing a DAG.** The frontier already identifies
   which queued tickets are unblocked (ll.359–364); independent tickets still
   run one at a time behind a 45-minute wall clock each (l.48).
5. **Prompt-only safety boundaries.** The brief's git/tracker/deploy bans are
   instructions to the worker (`worker-brief.md` ll.28–40); the only
   deterministic enforcements are the branch/commit repair (ll.619–624). There
   is no runner-side protected-paths check before `git add -A` (l.672).
6. **No completion notification.** The run ends by writing a local Markdown
   file; nobody is pinged. The operator must remember to check in the morning.
7. **Liveness depends on one laptop staying awake.** `caffeinate -i` prevents
   only idle sleep; lid-closed, reboot, or dead battery kills the loop
   (`SKILL.md` l.105). `on_exit` writes an abort report (ll.479–492) but
   nothing re-arms the run.
8. **Per-worktree setup failure stops the whole run** (`stop "setup failed…"`,
   ll.553–556) rather than failing just that ticket — harsh for a step that is
   inherently per-ticket flakiness-prone.
9. **Runner never runs tests.** The build gate is typecheck + build + lint by
   design (`scripts/overnight.sh` ll.302–317; header comment ll.27–28); test
   evidence is whatever the worker self-reports in its final JSON. A worker
   that marks tests `pass` without running them is caught only by the
   self-review step.
10. **Visible-mode finish heuristic can misfire.** A result file, tab close, or
    60 s of transcript quiet after a terminal turn ends the wait (ll.240–262;
    `VISIBLE_IDLE_SECS=60` at l.57). A worker in a long tool call that emits no
    transcript rows for >60 s after a `stop` turn would be reaped early.
    [INFERENCE — failure mode; detection logic cited.]
11. **Intake assumes label hygiene.** The run set is only as good as the
    ready-for-agent label plus wave-doc exclusions (`SKILL.md` ll.46–53). There
    is no "does this issue read as an executable prompt" quality check before
    the night burns quota on it.

## 2. Comparable workflows (primary sources, verified 2026-09-29)

| Workflow | Queue / intake | Budget & pacing | Checkpoint / resume | Progress log | Verification gates | Isolation | Failure triage & retry | Report / handoff | Safety | Notifications |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Overnight-run (current) | label + wave doc + `blocked_by` DAG, one waive prompt (`SKILL.md` ll.42–53) | 5h sleep ≥70%, 7d pace/stop, unknown→4-ticket cap (`usage-gate.sh` ll.36–42) | run-level `--resume`; none within a ticket (§1 gaps 1–2) | machine `state.json` only | runner: typecheck/build/lint; worker self-reports tests | one branch, or stacked worktrees in PR mode | rate-limit requeue only; red-after-stash halts | local `.md` report | brief bans + branch/commit repair | none |
| Anthropic long-running harness (post + quickstart) | initializer writes a 200+-item JSON feature list, all `passes:false` — the queue *is* the spec | incremental one-feature-at-a-time scope cap per session | every session re-orients from git log + progress file; `init.sh` re-establishes the dev server first | `claude-progress.txt` narrative log + descriptive git commits per session; JSON for machine state ("less likely to inappropriately change or overwrite JSON") | explicit end-to-end verification as a human user (Puppeteer MCP browser testing); never mark passing without testing | fresh context window per session; `init.sh` rebuilds environment | fix-before-feature: verify basics work before new work; git revert to recover working states | progress file + commit history *are* the handoff | strongly-worded "unacceptable to remove or edit tests" | n/a (research harness) |
| Claude Code GitHub Action (first-party) | one issue event → one run (`label_trigger`/`assignee_trigger`); N issues → N branches | per-run bounds via `claude_args` (`--max-turns`, `--model`) | n/a (one-shot per event) | PR + comments | branch protection / required reviews still apply; acts as `claude[bot]`; no merge input | GitHub-hosted runner per event | human-actor + write-access gates; bots rejected unless `allowed_bots` | PR per issue arrives on its own | least-privilege workflow; prompt-injection caution | GitHub-native (PR assignment) |
| GitHub Copilot coding agent | assign issue; issue text *is* the prompt — must include problem, acceptance criteria, target files | Copilot plan quota (premium requests / AI credits) | iterate via `@copilot` PR comments; batch review comments | PR title/body kept up to date by the agent | agent builds/tests/lints in its own ephemeral env (GitHub Actions); `copilot-setup-steps.yml` pre-installs deps; research→plan→iterate before opening PR | ephemeral dev environment per task | `@copilot` follow-ups push to the same branch; resolves merge conflicts on request | PR + review request; session logs | custom instructions (`copilot-instructions.md`, `AGENTS.md`, `CLAUDE.md` all honored); MCP allowlist; network policy analogue | review request on completion |
| OpenAI Codex (CLI/IDE/cloud/scheduled) | prompt with Goal/Context/Constraints/"Done when"; `AGENTS.md` as durable repo guidance; `/plan` or interview before coding | reasoning effort levels (Low→Extra High); per-run sandbox + approval policy | scheduled tasks re-run stable workflows in a worktree or local env; skills package repeatable work | diff panel review; `/review` against base/uncommitted/commit | worker loop must write/update tests, run suites, lint/typecheck, confirm behavior, review diff (`/review`, `code_review.md`) | sandbox modes; scheduled tasks optionally in a dedicated Git worktree | retrospective-to-`AGENTS.md` ("when Codex makes the same mistake twice… update `AGENTS.md`") — failure memory as repo guidance | scheduled-task output; PR review (Codex reviews 100% of PRs at OpenAI) | tight-by-default approvals + sandboxing, loosen only for trusted repos | scheduled-task surfacing |
| Devin automations | triggers: Slack/GitHub/Linear/Jira/PagerDuty/schedule/webhook + conditions; event payload auto-appended to prompt; triage-monitor spawns child sub-devins | per-session ACU budget cap (session stops at limit); invocation rate limit (default 50/hr) | message-an-existing-session action feeds events into a persistent stateful session | automation Activity tab: invocations, success/skip, session links, error messages | Fix-CI-failures template: reads build logs, fixes, pushes, verifies; playbooks (`@playbook-name`) inject extra instructions | new session per event, or one persistent monitor session | triage action (monitor decides, spawns children); email notification on every run / failures-only / success-only | weekly status digest / sprint report templates; email notifications | network policy intersected with security profile; public-repo triggers flagged as prompt-injection risk | email + Slack thread replies |
| Aider (git-native loop) | n/a (interactive) | n/a | `/undo` + full git history of micro-commits | **auto-commit per edit** with generated Conventional-Commit messages; `(aider)` author/committer attribution; dirty-file pre-commit keeps human edits separate | `--git-commit-verify` runs pre-commit hooks on agent commits (default skips) | branch-per-series workflow | `/diff` since last message; `/undo` instant revert; git history as the recovery mechanism | commit messages as log | protected edits via prompt; `--no-auto-commits` opt-out | n/a |
| Claude Code hooks + checkpointing (primitives) | n/a | `quota_auto_resume_*` notification matchers (v2.1.234+) | per-turn checkpoints (100/session, survive `--resume`); `/rewind` restores code / conversation / both; SDK `--rewind-files`; "not a replacement for version control" | n/a | `PreToolUse` exit-2 blocks (protected files); `PostToolUse` auto-format; prompt/agent-based review hooks (e.g. `security-guidance` plugin) | n/a | rewind-past-mistake; summarize-to-free-context (`/rewind`, `/branch`, `--fork-session`) | n/a | hooks are deterministic where prompts are advisory | `Notification` hooks: `osascript` (macOS) / `notify-send` / dialog; matchers incl. `agent_completed`, `idle_prompt`, `permission_prompt` |

Source details:

- **Anthropic, "Effective harnesses for long-running agents" (2025-11-26,
  Justin Young).** Initializer agent writes `init.sh`, `claude-progress.txt`,
  feature-list JSON, and an initial commit; each coding session makes
  incremental progress and exits leaving merge-ready state (commit + progress
  update); sessions orient via `pwd` → progress file → feature list → git log
  → start dev server → verify basics before new work. Failure table maps
  victory-declaration → feature list, dirty state → progress notes + commits,
  premature marking → self-verification. Open question noted: single generalist
  vs specialized testing/QA/cleanup agents. Code in
  `anthropics/claude-quickstarts/tree/main/autonomous-coding`. Source:
  <https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents>
  (read 2026-09-29).
- **Claude Code GitHub Action.** Per-issue fan-out, `claude/` branches,
  OAuth-vs-API-key quota choice, `claude_args` bounds, bot identity, no merge
  path — verified in `docs/research/overnight-issue-runner-options-2026-09.md`
  §§1–1a against
  <https://github.com/anthropics/claude-code-action/blob/main/docs/usage.md> and
  <https://code.claude.com/docs/en/github-actions> (read 2026-09-28; not
  re-fetched — no claim here goes beyond that note).
- **GitHub Copilot, "Best practices for using GitHub Copilot to work on
  tasks".** Ideal task = problem + acceptance criteria + target files; issue
  text as prompt; keep-back list (broad refactors, security/PII, ambiguous,
  learning tasks); research→plan→iterate before PR; `@copilot` PR iteration
  with batched review comments; `copilot-setup-steps.yml` for deps; custom
  agents with limited toolsets (e.g. testing specialist without prod-write).
  Source: <https://docs.github.com/copilot/how-tos/agents/copilot-coding-agent/best-practices-for-using-copilot-to-work-on-tasks>
  (read 2026-09-29).
- **OpenAI Codex, "Best practices".** Goal/Context/Constraints/"Done when"
  prompt shape; `AGENTS.md` (global/repo/subdir layering, short-and-accurate,
  mistake retrospectives folded back in); plan-before-code (`/plan`,
  interview, `PLANS.md`); test+review loop with `code_review.md`; skills for
  repeatable work; scheduled tasks in worktrees; tight-by-default sandbox.
  Source: <https://learn.chatgpt.com/guides/best-practices> (read 2026-09-29).
- **Devin, "Automations".** Trigger/conditions/action model (start session,
  message session, triage monitor, email notification); schedule triggers
  (RRULE/custom/one-shot); GitHub check-run (CI) triggers; ACU per-session cap
  + invocation rate limit; network policy; MCP connections recommended;
  Activity tab per automation; template gallery (Fix CI Failures, Weekly
  Changelog, Backlog Cleanup, …). Source:
  <https://docs.devin.ai/product-guides/automations> (read 2026-09-29).
- **Aider, "Git integration".** Commit-per-edit with Conventional Commits,
  `(aider)` attribution (author/committer/message/co-author variants),
  dirty-file pre-commit, `/undo`/`/diff`/`/commit`, `--git-commit-verify`.
  Source: <https://aider.chat/docs/git.html> (read 2026-09-29).
- **Claude Code hooks guide + checkpointing.** `Notification` hooks with
  per-platform commands and matchers (`permission_prompt`, `idle_prompt`,
  `agent_completed`, `quota_auto_resume_*`); `PreToolUse` exit-2 blocks;
  `PostToolUse` formatting; per-turn checkpoints (100 kept, survive resume,
  `/rewind` code/conversation/both, SDK `--rewind-files`, Bash edits and
  background-subagent edits not tracked, "not a replacement for version
  control"). Sources: <https://code.claude.com/docs/en/hooks-guide>,
  <https://code.claude.com/docs/en/checkpointing> (read 2026-09-29).

Deliberately out of scope (verified far enough to exclude, per the "pick
whichever are relevant" brief): Claude routines (PR/Release triggers only, no
issue events — prior note §1c); Ralph loops (single-task in-session grinder —
prior note §2); troykelly/claude-skills (auto-merges, fails no-merge — prior
note §2); Lanes (local-only — prior note §2); mini-swe-agent/OpenHands
trajectory formats (nothing found at the primary-source level that transfers
beyond "log everything," which the script's `logs/` per-ticket outputs already
do — `scripts/overnight.sh` ll.593–597). Factory Droid and Sweep were not
verified against first-party docs and are excluded rather than cited
second-hand.

## 3. Transferable patterns (distilled)

1. **The queue is part of the spec.** Anthropic's initializer expands one vague
   prompt into hundreds of `passes:false` JSON items; Copilot/Codex demand the
   issue read as a prompt (acceptance criteria + files + done-when). Our
   preflight builds a queue but never quality-checks the tickets as prompts.
2. **Fresh context needs a re-orientation ritual.** Every Anthropic coding
   session runs progress-file → feature list → git log → `init.sh` → verify
   basics before touching new work. Our brief sends the worker straight to the
   issue.
3. **Progress memory is narrative + commits, not just machine state.** The
   progress file plus descriptive commits let the *next* session start in
   seconds; JSON is reserved for what must not be paraphrased. Our `state.json`
   is JSON-only and human-hostile.
4. **Verification is end-to-end, not gate-shaped.** Anthropic requires testing
   "as a human user would" (browser automation); Copilot validates in its own
   env before the PR exists; our runner re-checks three static gates and trusts
   the worker about tests and browsers.
5. **Isolation per unit of work.** Action runs, Copilot envs, Codex scheduled
   worktrees, Aider branches — one branch/env per ticket is the consensus. Our
   default mode shares one branch (PR mode already matches consensus).
6. **Budgets cap the blast radius per session.** Devin's ACU cap stops a runaway
   *session*; our caps are per-ticket time (45 min) and global quota windows —
   nothing bounds one ticket's token/cost burn except the wall clock.
7. **Failures are classified, retried by kind, and folded back into guidance.**
   Devin auto-fixes CI failures from logs; Codex writes retrospectives into
   `AGENTS.md`; Aider's `/undo` + micro-commits make revert one command. We
   retry only rate limits.
8. **The handoff is a pushed artifact, not a local file.** PRs that request
   review (Copilot), PR-per-event (Action), email/Slack digests (Devin) —
   morning state that finds the human. Ours waits in `.scratch/`.
9. **Deterministic guards beat advisory prompts.** `PreToolUse` exit-2 blocks,
   sandbox modes, approval policies, network policies — all execute regardless
   of what the model "decided." Our bans are brief prose plus two repairs.
10. **Wakeups are events, not mornings.** Devin triggers, Action issue events,
    Codex schedules, `Notification` hooks — the human is interrupted at the
    moment something needs them, including mid-run failures, not just at 07:00.

## 4. Ranked recommendations

Effort: S = hours in existing files, M = new script surface or mode, L = new
architecture or cloud dependency. Risk: what breaks or what it costs if wrong.

### Quick wins (do first)

**R1. Retry transient failures once before failing the ticket.**
Rationale: closes gap 1; every surveyed runner classifies failures (Devin
check-run auto-fix; Codex retrospective loop; Aider `/undo`-and-retry).
Evidence: Devin automations "Fix CI Failures" template and `@copilot`
same-branch iteration (both §2). Concrete change: in `run_ticket`
(`scripts/overnight.sh` ll.648–694), tag each failure reason
`transient` (timeout, worker exit ≠ 0 with partial diff, red build gate on a
previously-green tree, missing final JSON with non-empty diff) vs `terminal`
(worker `blocked`, empty diff with `done`, branch violation), and requeue
transient failures once with the prior attempt's reason + diff stat appended
to the brief; record `retries` in `state.json`. Effort S. Risk: low — one extra
45-min ticket worst case; cap total retries per run alongside `MAX_REQUEUES`.

**R2. Put a "Done when" block in the worker brief.**
Rationale: closes gap 11; Copilot ("acceptance criteria… which files") and
Codex (Goal/Context/Constraints/Done-when) agree the issue-as-prompt is the
highest-leverage quality control. Evidence: Copilot best-practices "Making sure
your issues are well-scoped"; Codex "Strong first use" (both §2). Concrete
change: `render_brief` (`scripts/overnight.sh` ll.377–386) gains
`OB_DONE_WHEN` (acceptance criteria quoted from the issue, fetched in
`fetch_tracker`) and `OB_TOUCH_FILES` (paths the issue names, else "discover");
preflight step 2 (`SKILL.md` ll.46–53) adds a quality gate — tickets without
extractable criteria are flagged to the user at confirm time, not discovered
at 03:00. Effort S. Risk: negligible; brief grows slightly.

**R3. Write a per-ticket handoff note the next attempt can read.**
Rationale: closes gaps 2–3 with Anthropic's progress-file pattern at ticket
granularity: narrative for the next session, JSON for what must not be
paraphrased. Evidence: Anthropic post §§ Environment management / Getting up
to speed (claude-progress.txt + JSON feature list + get-bearings ritual)
(§2). Concrete change: on fail *and* on requeue, `run_ticket` writes
`logs/<run>-<N>.handoff.md` (what was tried, diff stat, failing check output
tail, worker `notes`) and `render_brief` appends it to retried briefs;
add the get-bearings checklist (read handoff → `git log --oneline -5` →
verify checks) to `worker-brief.md` §Task. Effort S. Risk: low; files already
exist in `logs/`, only the handoff composition is new.

**R4. Notify on run end (and on early stop).**
Rationale: closes gap 6; the exact primitive is documented first-party for
macOS. Evidence: hooks-guide `Notification` + `osascript` pattern (§2); Devin
email-on-failure/success as the cloud analogue. Concrete change: `stop()`
(`scripts/overnight.sh` ll.469–477) emits
`osascript -e 'display notification …'` with the stop reason (gated behind a
`OVERNIGHT_NOTIFY=1` default-on env knob, since the runner may be remote);
mention it in `SKILL.md` step 9. Effort S. Risk: trivial; silent no-op over
ssh. [INFERENCE — `osascript` over a remote herdr pane needs a logged-in GUI
session; verify on the operator's Mac.]

**R5. Runner-side protected-paths check before `git add -A`.**
Rationale: closes gap 5 with the deterministic-guard pattern (pattern 9):
advisory bans stay, but the runner enforces. Evidence: hooks-reference
`PreToolUse` exit-2 protected-patterns script (hooks-guide §"Block edits to
protected files," §2); Codex tight-by-default sandboxing. Concrete change: a
`PROTECTED_RE` (default `.env|key|secret|token|pem|.git/`, overridable via
`OVERNIGHT_PROTECTED_RE`) checked in `run_ticket` between build gate and
`git add -A` (ll.668–673); on hit, fail the ticket as terminal with reason
`protected paths touched`. Effort S. Risk: low; false positives are a one-line
env override. Flag: keep the default list out of any repo-committed file that
advertises secret locations — thresholds live in-script today, same treatment.

**R6. Demote per-worktree setup failure to per-ticket failure.**
Rationale: gap 8 — setup is per-ticket work and should fail per-ticket, matching
the PR-mode "fail keeps its worktree" philosophy. Evidence: Copilot
`copilot-setup-steps.yml` treats env setup as fallible agent-side iteration
(§2), not run-abort. Concrete change: `open_worktree`
(`scripts/overnight.sh` ll.553–556) returns nonzero instead of `stop`; the
caller records `failed: setup failed` and continues the loop. Effort S. Risk:
low; strictly more tickets attempted.

### Larger bets (sequence after quick wins)

**R7. Parallel lanes for unblocked tickets (default width 1).**
Rationale: gap 4; the DAG already exposes the frontier, and every cloud
runner fans out (Action N-events→N-runs; Devin triage→sub-devins; OMP `task`
semaphore per prior note §1f). Evidence: prior note §§1a, 1f; Devin triage
action (§2). Concrete change: `OVERNIGHT_WIDTH=N` (default 1) running up to N
`run_ticket`s in disjoint PR-mode worktrees with the gate checked out-front;
default mode stays serial so behavior is unchanged until asked. Effort M.
Risk: medium — multiplies quota burn (pace gate must be consulted per lane),
stack-PR semantics need a lane-aware `stack_base`; gate the whole mode on
`--pr-per-ticket`. Conflicts with nothing, but widens the usage blast radius
the pacing work just narrowed.

**R8. Second-lineage review pass over done tickets before the report.**
Rationale: pattern 4 + the repo's own lineage rule (a hostile pass must be a
second lineage, never Claude reviewing Claude). Evidence:
`AGENTS.md` ll.156–157, 219 (`adversary`/`reviewer` on GLM); Codex
`code_review.md`-referenced review; `security-guidance`-style review hooks
(§2). Concrete change: after the loop, one GLM-backed `omp -p` per done ticket
(diff + brief + criteria in, `approve|flag: reason` out); flags go in the
report's Failures section as `review-flagged`. Effort S/M. Risk: low-medium —
GLM false positives cost morning attention; keep advisory, never auto-revert.
Constraint: routes review onto flat-rate Go, not plan quota — consistent with
`AGENTS.md` routing intent.

**R9. Cloud-execution mode for lid-closed nights.**
Rationale: gap 7; the prior note ranked the first-party Action above any local
improvement when the Mac must sleep. Evidence: prior note §§1–1a (rank 1:
`claude-code-action` label/assignee trigger; rank 2: `claude --cloud`
fan-out). Concrete change: new `SKILL.md` appendix + workflow file mapping
plan.json queue → trigger labels; repo skills ride along via the Action's
`prompt`/`plugins` inputs (prior note §3). Effort M. Risk: medium — OAuth
token scope/rotation unverified (prior note §4); prompt-injection surface of
issue-driven runs needs least-privilege workflow (Devin public-repo warning,
§2). No conflict with the local loop; it is an alternative launcher.

**R10. Budget the worker, not just the window.**
Rationale: pattern 6 — Devin's per-session ACU cap bounds the runaway *ticket*,
while our only per-ticket bound is time. Evidence: Devin ACU limit +
invocation limit (§2); Codex reasoning-effort ladder (Low→Extra High) as the
knob that trades quality for burn (§2). Concrete change: resolve and record a
per-ticket effort/cost ceiling (`--max-turns` already passed for claude at
l.51/l.393; add `CLAUDE_MAX_TURNS` honoring + `omp --max-time` already at
ll.396–398 — so the real addition is *reporting* per-ticket spend: capture
`total_cost_usd`/`num_turns` from claude JSON results and omp session stats
into `state.json` and the report). Effort M (reporting plumbing across two
harness output schemas). Risk: low; read-only accounting. [INFERENCE — omp
headless JSON exposes per-session cost in a parseable field; confirm against
`omp -p --mode json` output before building.]

**R11. Event-driven intake (labels → runs) instead of nightly batch.**
Rationale: pattern 10; Devin's trigger/condition/action model and the Action's
issue-event fan-out remove the "assemble tonight's queue by hand" preflight.
Evidence: Devin automations triggers + conditions (§2); prior note §1a.
Concrete change: L-effort — webhook or scheduled GH Action that translates a
`ready-for-agent` label event into a scoped single-ticket run; preflight steps
1–8 become per-event. Risk: high — concurrent runs need R7 isolation first,
prompt-injection review of label-triggered prompts, and tracker write policy.
Sequence strictly after R7 + R9. Does not conflict with repo constraints but
needs the OAuth/secret handling the repo currently avoids (secrets belong in
dotfiles per `AGENTS.md` ll.71–72).

### Considered and not recommended

- **Historical-profile pacing** (compare against past weeks instead of uniform
  burn): CodexBar's `HistoricalUsagePace` is the sophisticated alternative, but
  overnight burn is bursty by nature — uniform schedule stays the honest prior
  (pacing note §5; CodexBar source §2.4). Revisit only if early-window stops
  prove too eager after a month of logs.
- **In-worker Stop/SessionStart hooks for guardrails**: hooks are per-harness
  config (`~/.claude/settings.json`), not something the runner can inject into
  a fresh `claude -p`/`omp -p` worker — and `claude -p` never runs the
  statusLine path (primitives note §4). Keep guards runner-side (R5).
- **Checkpoint/rewind as the ticket recovery mechanism**: checkpoints track
  only file-tool edits (not Bash), keep 100/session, expire in ~30 days, and
  are "not a replacement for version control" (checkpointing docs §"Not a
  replacement for version control"). Our stash/worktree mechanism already
  covers this ground better; use rewind knowledge only to *not* build on it.
- **Persistent triage-supervisor session** (Devin monitor pattern): contradicts
  the skill's fresh-context-per-ticket design and the repo's bounded-context
  instincts; the DAG + report already coordinate. Revisit if R11 happens.

## 5. Repo-constraint flags

- **Training-eligible tier.** `code-worker`/`sonic`/`research` run on
  `muse-spark-1.3-contributor`, which Meta may train on, including repository
  source (`AGENTS.md` ll.165–174, 263–274; muse note §§Plan terms/Privacy
  scope). An overnight worker resolving to that tier (via `resolve_model`,
  `scripts/overnight.sh` ll.147–155, or `OVERNIGHT_WORKER_MODEL` at l.53)
  ships every touched ticket's source to a training-eligible endpoint all
  night. Recommendation: the preflight confirm step (`SKILL.md` ll.87–90)
  should print the resolved worker model *and its tier*, and any session
  touching client/sensitive material must pin standard-tier or Claude per
  `AGENTS.md` ll.169–174. R8's GLM reviewer is already on the safe side.
- **Work-machine gate.** On a `work` machine, install links skills only and
  skips OMP/Pi config (`AGENTS.md` ll.39–47). The usage gate needs `omp usage`
  against the Anthropic login and the worker needs the harness default model —
  both may be absent or differently authenticated there, pushing every run
  into the 4-ticket unknown-gate fallback (`usage-gate.sh` ll.36–42;
  `overnight.sh` ll.865–869). Recommendation: document the degraded mode in
  `SKILL.md` preflight step 7 rather than discovering it at midnight.
- **macOS has no GNU `timeout`** (`AGENTS.md` ll.125–126). The runner is
  already compliant (job-control process groups, ll.272–300). Any future
  contributor adding timeouts (e.g. R7 lane supervision) must reuse
  `run_with_timeout`, not `timeout(1)`.
- **`openai-codex` stays disabled** (`AGENTS.md` ll.237–241). Codex-cloud
  patterns transfer as *ideas* (R2's prompt shape, `/plan` planning), but no
  recommendation may route work through the lapsed account.

## Sources (all read 2026-09-29 unless noted)

- <https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents> — initializer/coding agents, feature-list JSON, incremental progress, progress file + commits, get-up-to-speed ritual, browser-as-human verification, failure table, multi-agent open question.
- <https://docs.github.com/copilot/how-tos/agents/copilot-coding-agent/best-practices-for-using-copilot-to-work-on-tasks> — issue-as-prompt, task-type keep-back list, research→plan→iterate, `@copilot` iteration, custom instructions, `copilot-setup-steps.yml`, custom agents.
- <https://learn.chatgpt.com/guides/best-practices> — Goal/Context/Constraints/Done-when, `AGENTS.md` layering, plan-first, test+review loop, skills, scheduled tasks in worktrees, tight-by-default sandbox.
- <https://docs.devin.ai/product-guides/automations> — triggers/conditions/actions, schedule + check-run triggers, ACU + invocation limits, network policy, Activity tab, templates.
- <https://aider.chat/docs/git.html> — commit-per-edit, Conventional Commits, `(aider)` attribution, dirty-file pre-commit, `/undo`, `--git-commit-verify`.
- <https://code.claude.com/docs/en/hooks-guide> — `Notification` hooks (`osascript`/`notify-send`), matchers incl. `agent_completed` and `quota_auto_resume_*`, `PreToolUse` exit-2 blocks, `PostToolUse` formatting.
- <https://code.claude.com/docs/en/checkpointing> — per-turn checkpoints, `/rewind` restore/summarize, Bash/subagent blind spots, not-a-replacement-for-version-control.
- Repo: `skills/overnight-run/SKILL.md`; `skills/overnight-run/scripts/overnight.sh`; `skills/overnight-run/scripts/usage-gate.sh`; `skills/overnight-run/scripts/worker-brief.md`; `AGENTS.md` ll.39–47, 125–126, 156–175, 219, 237–241, 263–274.
- Prior notes (2026-09-27/28, not re-fetched): `docs/research/overnight-issue-runner-options-2026-09.md` (Action rank 1, cloud rank 2, PR-per-issue gap); `docs/research/claude-code-overnight-primitives-2026-09.md` (headless flags, `-p` never runs statusLine, wait limits); `docs/research/claude-usage-pacing-2026-09.md` (pace formula, thresholds, fixtures); `docs/research/muse-code-subscription-2026-09.md` (cost-weighted metering, training-eligible tier).
