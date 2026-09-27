# Overnight issue-runner options: ~10 issues → one PR per issue, no auto-merge (2026-09-28)

Question: for "take ~10 ready GitHub issues, work them unattended overnight, produce one
reviewable PR per issue (or clearly grouped PRs), never merge", what skill- or
skill-shaped options exist, and is any better than Elves for this user?

## Direct answer

**Yes — use the first-party Claude Code GitHub Action, not Elves, for this use case.**
Rank for this user's setup (Claude subscription + flat-rate OpenCode Go, Mac may sleep,
PR-per-issue, no auto-merge):

1. **`anthropics/claude-code-action` with a per-issue trigger (label or assignee).** It is
   the only option whose native shape is *one GitHub event per issue → one cloud run → one
   branch/PR*, that runs with the Mac asleep, and that never merges. Authenticate it with
   the OAuth token so it burns the Claude subscription, not API spend. Elves is the wrong
   shape here (one run → one branch → one PR; see §5) plus a heavy contract surface the
   user is already uninstalling.
2. **`claude --cloud` fan-out (one cloud session per issue, fired before sleep).** Zero
   repo workflow files, Mac sleeps, same subscription pool. Weaker than #1 only in
   orchestration: no label trigger, PR creation is a per-session step, and the morning
   review is 10 browser sessions instead of 10 PRs arriving on their own.
3. **Extend the in-house `overnight-run` draft with the repo's existing `pr` skill.**
   Zero new dependencies and the usage gate already exists — but the Mac must stay awake
   (`caffeinate -i`, lid open, on power), which fails the stated sleep requirement. Only
   pick this if cloud execution is ever off the table.

GitHub Copilot's coding agent is a legitimate fallback *if* the user holds a Copilot seat
with coding-agent access (quota/mechanics partly [UNVERIFIED], §4). Everything else
evaluated (Codex cloud/`codex exec`, Claude routines, Ralph loops, troykelly/claude-skills,
Lanes, OMP-local loops) is ruled out in §4–§6 with reasons.

Prior research this builds on (not repeated): `claude-code-overnight-primitives-2026-09.md`
verified `claude -p` flags, the `omp usage --provider anthropic --json` gate (all three
subscription windows, machine-readable), OMP headless flags (`--mode json`,
`--auto-approve`, `--max-time`, `--no-session`, stdin must be closed), and that no
in-session `sleep`/Monitor can bridge hours-long waits.

## Comparison table

| Option | PR-per-issue | Needs Mac awake | Quota burned | Merge safety | Maturity | Sources |
| --- | --- | --- | --- | --- | --- | --- |
| 1. `claude-code-action`, label/assignee trigger | Yes — one workflow run per issue event, `claude/`-prefixed branch each | No — runs on GitHub-hosted runners | OAuth token → Claude subscription; API key → metered API usage (your choice) | Never merges; acts as `claude[bot]`; branch protection still applies; no merge input exists | First-party, `anthropics/` org, `v1` tag, beta label | [usage.md](https://github.com/anthropics/claude-code-action/blob/main/docs/usage.md), [github-actions docs](https://code.claude.com/docs/en/github-actions) |
| 2. `claude --cloud` × N sessions | Mostly — one session per issue; PR created from each session (manual step or prompted) | No — sessions persist after laptop closes | Claude subscription, same as interactive | Push guards reject protected branches / others' PR branches; no auto-merge described | First-party, GA docs (Pro/Max/Team/Enterprise) | [cloud docs](https://code.claude.com/docs/en/claude-code-on-the-web) |
| 3. In-house `overnight-run` + `pr` skill | Yes after a small addition (draft today: commits only, no PRs) | **Yes** — `caffeinate -i`, lid open, on power | Same pool as today (`omp usage` gate already built) | Local only; `merge` skill refuses drafts/conflicts/changes-requested and needs explicit `--admin`/`--auto` | Draft, uncommitted, this repo | `skills/overnight-run/SKILL.md` ll.69–95, `skills/pr/SKILL.md`, `skills/merge/SKILL.md` |
| Copilot coding agent (fallback) | Yes — assign issue → PR + review request | No — GitHub cloud | Copilot plan quota (premium requests / AI credits); exact per-session metering [UNVERIFIED] | Opens PR, requests review, needs "Approve and run workflows"; no auto-merge | First-party, public preview for assign-issue | [assign-issue docs](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/cloud-agent/use-cloud-agent-on-github) |
| Elves (status quo, uninstalling) | **No** — one run → one branch → one PR | Depends on driver (local driver = awake) | Driver/worker subscription or API, per route | No merge by default, but contract weight is the complaint | 223★/15 forks, MIT, v2.38.0, single-maintainer-shaped | [repo](https://github.com/aigorahub/elves), [SKILL.md](https://github.com/aigorahub/elves/blob/main/SKILL.md), [parallelves.md](https://github.com/aigorahub/elves/blob/main/references/parallelves.md) |
| Codex cloud / `codex exec` | Possible (parallel cloud chats; exec in CI) | No (cloud) / n/a (CI) | ChatGPT/Codex account or API key — **subscription dropped, provider disabled here** | Review-before-merge posture; CI pattern isolates write perms | First-party, Stable `codex exec` | [cloud](https://developers.openai.com/codex/cloud), [non-interactive](https://learn.chatgpt.com/docs/non-interactive-mode) |
| Claude routines (scheduled) | No — GitHub triggers cover **PR and Release events only, not issues** | No — Anthropic cloud | Subscription + daily routine-run cap | `claude/` branches; protected-branch push rejected | Research preview | [routines](https://code.claude.com/docs/en/routines) |
| Ralph loops (official plugin) | No — single-task in-session iteration loop | Yes — runs in your session | Session's own quota | No merge machinery at all | Official, in `anthropics/claude-code` monorepo | [README](https://github.com/anthropics/claude-code/blob/main/plugins/ralph-wiggum/README.md) |
| troykelly/claude-skills | Nominally (parallel workers over issues) | Yes — local Task agents | Claude subscription (+ credential juggling) | **Auto-merges PRs itself** (`gh pr merge --squash`); consent-implied — fails the brief | 11★, 0 forks, single maintainer, opinionated stack | [repo](https://github.com/troykelly/claude-skills), [autonomous-orchestration](https://github.com/troykelly/claude-skills/blob/main/skills/autonomous-orchestration/SKILL.md) |
| Lanes GH/Linear integration | No — local board + local sessions, PR link posted back as comment | Yes — tokens stay on the machine, sessions local | Local harness quota | Human-driven | Commercial, v0.39 (2026-05) | [announcement](https://lanes.sh/blog/integrations-have-arrived) |
| OMP-local loop (`omp -p` per ticket) | Yes, scriptable (isolated task worktrees exist) | **Yes** — local process | Routed model: Claude subscription, Go flat-rate, or Muse | Local only; nothing merges unless scripted | First-party (this harness), v18.3.5 | [omp://tools/task.md](omp://tools/task.md), prior research §9 |

## 1. First-party routes in detail

### 1a. Claude Code GitHub Action — RECOMMENDED (rank 1)

Attach the action so that labelling (or assigning) an issue starts exactly one run for that
issue. The action's own `usage.md` documents both `label_trigger` ("label name that triggers
the action when applied to an issue") and `assignee_trigger` ("assignee username that
triggers the action … only used for issue assignment"), alongside the default `@claude`
`trigger_phrase`, in a workflow that already subscribes to `issues: [opened, assigned,
labeled]` plus `issue_comment` events. Each run works on a `claude/`-prefixed branch
(`branch_prefix`, default `claude/`). The docs page frames the product as "turn issues into
pull requests" via `@claude` mention or automatic `prompt` on any GitHub event.
Sources: [usage.md](https://github.com/anthropics/claude-code-action/blob/main/docs/usage.md)
(read 2026-09-28); [github-actions docs](https://code.claude.com/docs/en/github-actions)
(read 2026-09-28).

- **PR-per-issue:** yes, structurally. Event-driven: N labelled issues → N independent
  workflow runs → N branches. Overnight procedure: push the workflow once, then apply the
  trigger label to the ~10 ready issues (manually, or one `gh issue edit --add-label`
  loop) and go to sleep. Morning: one PR per issue to review. Exact PR-vs-branch-push
  mechanics of the issue flow should be confirmed in one trial run ([UNVERIFIED] at the
  mechanical level; the docs promise "turn issues into pull requests").
- **Mac awake:** no. Runs on `ubuntu-latest` GitHub runners.
- **Quota:** your choice at setup. `claude_code_oauth_token` ("authenticates with your
  Claude subscription … generate one by running `claude setup-token` locally", available on
  Pro/Max/Team/Enterprise) burns the subscription; `anthropic_api_key` burns metered API
  spend; org rollouts should prefer a Console API key because "an OAuth token is tied to
  the subscription of the person who ran `claude setup-token`". Sources: same two pages.
  For this user, OAuth is the right pick (subscription already held; no API bill).
- **Merge safety:** the action never merges. It acts as `claude[bot]` (defaults
  `bot_id 41898282`, `bot_name claude[bot]`), its inputs table has no merge/auto-merge
  control, and runs additionally gate on write-access + human-actor checks (bots rejected
  unless in `allowed_bots`). GitHub branch protection / required reviews still apply on
  top. Sources: [usage.md inputs table](https://github.com/anthropics/claude-code-action/blob/main/docs/usage.md);
  [who-can-trigger-runs](https://code.claude.com/docs/en/github-actions#who-can-trigger-runs).
- **Fit note:** per-run bounds exist (`claude_args` passes `--max-turns`, `--model`, etc.;
  the deprecated `max_turns`/`model` inputs must not be used). Prompt-injected-malicious-issue
  risk is inherent to issue-driven runs on any option; keep the workflow's least privilege
  and review every PR in the morning — which is the stated plan anyway.

### 1b. `claude --cloud`, one session per issue (rank 2)

"Start a cloud session … The session keeps running after you close your laptop" —
available on Pro/Max/Team/Enterprise, and "each `--cloud` command creates its own cloud
session that runs independently", so 10 issues = 10 parallel sessions fired from one
terminal loop before sleep ("plan locally, execute in the cloud" is the documented
pattern). Review per session shows a diff indicator; "you can create a PR from
claude.ai/code or teleport the session to your terminal". Source:
[cloud docs](https://code.claude.com/docs/en/claude-code-on-the-web) (read 2026-09-28).

- **PR-per-issue:** mostly. Each session is per-issue, but PR creation is a per-session
  action (button or instructed in the prompt, e.g. "open a PR when done"), not an
  automatic fan-out — weaker than #1's automaticity.
- **Mac awake:** no after launch; follow-ups can even be queued from elsewhere
  (`claude -p "…" --cloud <session-id>`, exits without waiting).
- **Quota:** the Claude subscription (cloud sessions are subscription-authenticated; not
  available under Bedrock/API-key setups).
- **Merge safety:** good. "Claude creates `claude/`-prefixed branches … always accepted.
  When your prompt directs Claude to push to another branch, Claude Code checks the push
  first and rejects it if … the branch is protected … someone else has an open PR from
  that branch" (routines page, same cloud-session substrate; source:
  [routines § repositories and branch permissions](https://code.claude.com/docs/en/routines)).
  Commits/PRs carry the user's GitHub identity; nothing auto-merges.
- **Setup cost:** install the Claude GitHub App on the repo (also enables auto-fix);
  `/web-setup` alone "does not install the Claude GitHub App". Source: cloud docs § GitHub
  auth options.

### 1c. Claude routines — not suitable as the runner

Routines run on Anthropic cloud ("keep working when your laptop is closed"), draw down
subscription usage plus a daily routine-run cap, and support schedule/API/**GitHub**
triggers — but the GitHub trigger's supported events are exactly **Pull request** and
**Release** ("you can pick a specific action … or react to all actions in the category";
filter fields are PR fields). There is **no issue event**, so a routine cannot fan out
one run per issue. A nightly schedule trigger *could* run a "work the ready-issues queue"
prompt, but that reintroduces a hand-rolled loop inside one session with manual PR
per-issue handling — strictly worse than #1. Routines are also in research preview.
Source: [routines docs](https://code.claude.com/docs/en/routines) (read 2026-09-28).

### 1d. Codex — ruled out by environment, recorded for completeness

Codex cloud runs parallel tasks in isolated cloud environments from web/GitHub/Linear/
Slack ("delegate several tasks … review the result", sign-in with ChatGPT account) and
`codex exec` is Stable for non-interactive/scripted runs with explicit sandbox flags and
JSONL output; a documented CI pattern even isolates write permission (patch artifact →
separate `open_pr` job). Sources: [cloud](https://developers.openai.com/codex/cloud),
[third-party GitHub](https://developers.openai.com/codex/third-party/github),
[non-interactive](https://learn.chatgpt.com/docs/non-interactive-mode) (all read 2026-09-28).
**Ruled out here:** the OpenAI Codex subscription is dropped and `openai-codex` sits in
OMP's base `disabledProviders` (repo fact: `AGENTS.md` ll.142–144, 234–238), so every Codex
route would burn API-key spend or a resurrected subscription against the user's explicit
decision. If Codex ever returns, its shape (parallel cloud chats, review-before-merge)
fits PR-per-issue.

### 1e. GitHub Copilot coding agent — fallback if a seat exists

Assigning an issue to Copilot (Assignees → Copilot, optional prompt/branch/model) makes it
"start working on the task, raise a pull request, then request a review from you when
it's finished" — exactly the desired shape, one PR per issue, cloud-hosted (Mac sleeps).
Workflows do not auto-run on Copilot pushes ("Approve and run workflows"); nothing in the
flow merges — morning review then manual merge. Caveats: assign-issue is in public
preview; post-assignment issue comments are *not* seen by the agent ("Copilot will not be
aware of … any further comments added to the issue"); quota is the Copilot plan's premium
requests / AI-credits pool, and per-session metering could not be verified against primary
billing docs ([UNVERIFIED] — a secondary discussion states one premium request per coding
session; confirm against the account's current Copilot plan). Also note the user holds a
*Muse Code* subscription, not a stated Copilot seat — seat existence itself is
[UNVERIFIED]. Sources: [agent docs](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/cloud-agent/use-cloud-agent-on-github)
(read 2026-09-28); [premium requests](https://docs.github.com/en/copilot/reference/copilot-billing/request-based-billing-legacy/github-copilot-premium-requests).

### 1f. OMP (`task` subagents, isolated worktrees, headless `omp -p`) — local only

OMP's `task` tool spawns batch subagents with a session-scoped concurrency semaphore,
optional `isolated` workspaces (isolation backends incl. APFS clones; branch merge mode
commits to `omp/task/<id>` then cherry-picks, patch mode captures/applies root patches),
and headless `omp -p` runs exist with `--mode json` / `--auto-approve` / `--max-time`
(prior research §9; note OMP has no max-turns flag and no documented bash ceiling).
Source: [omp://tools/task.md](omp://tools/task.md) (read 2026-09-28); prior research file.
Any OMP loop is a local process: it needs the Mac awake exactly like option 3, and its
quota advantage (routing workers to flat-rate Go or Muse Spark per `AGENTS.md` ll.127–175)
does not overcome the sleep requirement. OMP is the right *substrate* for local
orchestration, not the overnight answer while the Mac sleeps.

## 2. Third-party skills/plugins aimed at issue→PR or long runs

| Candidate | What it is | PR-per-issue? | Verdict for this brief |
| --- | --- | --- | --- |
| Official Ralph Wiggum plugin (`anthropics/claude-code`, `plugins/ralph-wiggum`) | Stop-hook loop: same prompt re-fed in-session until a completion promise; single task, in your session | No | Wrong shape (one task grinder, not an issue fan-out). Official/first-party, but answers a different question. Source: [README](https://github.com/anthropics/claude-code/blob/main/plugins/ralph-wiggum/README.md). |
| troykelly/claude-skills (issue-driven development plugin, 28–52 skills) | `claude-autonomous`: works open issues via parallel Task workers, state in GitHub project board, crash recovery, multi-account rotation | Nominally | **Reject.** 11★ / 0 forks / 1 open issue (immature); bootstrap **merges PRs itself** (`gh pr merge --squash`) violating no-merge; "user's request IS consent, no confirmation"; saves OAuth tokens to project `.env` (credential hygiene smell); opinionated stack (strict-typing, IPv6-first, Postgres RLS) unlikely to match arbitrary repos. Sources: [repo](https://github.com/troykelly/claude-skills), [SKILL.md](https://github.com/troykelly/claude-skills/blob/main/skills/autonomous-orchestration/SKILL.md) (read 2026-09-28). |
| Lanes GitHub/Linear integration (v0.39) | Local board: import issues, run agent sessions in fresh worktrees, post PR link back as comment | Via local sessions only | **Reject for overnight.** Tokens stay on-machine, sessions are local — Mac must be awake. Commercial product, not a skill. Source: [announcement](https://lanes.sh/blog/integrations-have-arrived) (2026-05-13). |
| Awesome-list long tail (superpowers, toolkits, 1000+ skill collections) | Methodology skills (TDD, review, planning), not runners | No | Searched; no other issue→PR runner with standing emerged. The skill-shaped answer to "run my queue overnight" in the Claude ecosystem is the GitHub Action + `prompt` invoking repo skills (the action's `plugins`/`prompt` inputs load repo `.claude/skills/` directly). |

No third-party skill found beats the first-party Action on this brief: the runners that
match the shape either auto-merge (troykelly) or are local-only (Lanes), and the
methodology collections don't run anything.

## 3. Composition from skills already in this repo — the remaining gap is small

Per-ticket lifecycle is already covered: `execute-plan` (hands-off checklist execution,
fresh subagent per item, evidence-before-tick, path-limited parallel commits),
`workstreams` + `specialist-delegation` (dependency graph, exclusive write ownership,
integration gate), `tdd`, `code-review`, `pr` (branch → push → `gh pr create`, draft
supported), `commit-push`/`push`, `merge` (refuses drafts, conflicts, changes-requested;
`--admin`/`--auto` only on explicit ask), `backlog` (issue readiness). The draft
`overnight-run` adds the loop + `omp usage` gate + serial isolation (one fresh worker per
ticket, 45-min cap, stash-on-fail, resume). Concretely verified in-draft: "one run branch,
one commit per ticket. Nothing is pushed, merged, deployed or opened as a PR"
(`skills/overnight-run/SKILL.md` ll.93–95) and launch under `caffeinate -i` with "stay on
power with the lid open" (ll.69–78).

So the gap to PR-per-issue is exactly two small, boring additions — no new skill system
needed:

1. **PR fan-out:** after the per-ticket commit, invoke the existing `pr` skill's steps per
   ticket (one branch per ticket instead of one run branch, then `gh pr create` —
   non-draft, no `--auto`, no merge). The `merge` skill already encodes the morning
   reviewer's gate and stays human-invoked.
2. **Cloud execution (only if the Mac must sleep):** that is precisely what options 1–2
   buy. A local loop cannot be fixed by any skill to survive sleep; `caffeinate -i`
   prevents only idle sleep.

If the user ever wants cloud *and* in-house control, the Action's `prompt`/`plugins`
inputs can invoke these same repo skills inside each cloud run (repo `.claude/skills/`
are checked out onto the runner) — first-party scheduling, in-house methodology.

## 4. Room for verification (things I could not fully verify)

1. **Action's exact issue→PR mechanics** (auto-opens PR vs pushes branch + comments):
   docs promise "turn issues into pull requests" but the `usage.md` excerpt verified here
   centers on mention-response; one trial run on a scratch repo settles it. [UNVERIFIED]
2. **Copilot seat + metering:** whether the user's Muse Code subscription includes coding
   agent, and current premium-request/AI-credit metering per session (billing docs are
   mid-migration to AI credits). [UNVERIFIED]
3. **OAuth-token scope details** (single- vs multi-repo, expiry/rotation) beyond "tied to
   the subscriber" — check the setup guide at run time. [UNVERIFIED]
4. **`claude --cloud` PR step automaticity** (button vs prompt-instructed open) per current
   web UI. [UNVERIFIED]
5. **Elves Parallelves detail** beyond the verified single-PR shape ("merges lanes into an
   integration branch … and produces one PR", per the indexed snippet of
   `references/parallelves.md`): full lane semantics not read. [PARTLY UNVERIFIED]

## 5. How Elves compares (from its own repo docs)

- **Shape mismatch (decisive).** A run funnels to a single branch and a single reviewable
  unit: "the host stays parked … one cumulative terminal review … a host-owned **landable
  PR**" ([SKILL.md](https://github.com/aigorahub/elves/blob/main/SKILL.md)); "Implementation
  runs get a draft PR at the first useful pushed commit" (repo
  [README](https://github.com/aigorahub/elves)); Parallelves "merges lanes into an
  integration branch … and produces one PR"
  ([parallelves.md](https://github.com/aigorahub/elves/blob/main/references/parallelves.md)).
  Ten independent issues would land as one giant PR (or force ten full runs, each paying
  the whole ceremony) — the opposite of the brief.
- **Complexity (the uninstall reason, confirmed).** Default Cobbler-first coordination,
  required/experimental prewalk qualification, same-model lower-effort native-worker
  routing table, Fugu/Manus/Grok/Devin/omp provider shortcuts, landable-PR authority
  separation (`ready=true` never grants merge) — all real machinery for a different
  problem (one big plan, executed while you sleep). Repo stats: 223★, 15 forks, MIT,
  v2.38.0 ([repo](https://github.com/aigorahub/elves), read 2026-09-28).
- **Merge posture is fine** ("You never merge by default — the user merges when they
  return"), so merge safety is not the complaint; shape and weight are.
- **Verdict:** uninstalling is correct for *this* use case. Elves would be the right tool
  for "implement this one big plan overnight into one PR"; it is the wrong tool for
  "ten small independent issues into ten PRs".

## Sources (all read 2026-09-28 unless noted)

- https://github.com/aigorahub/elves (repo: 223★, 15 forks, MIT, v2.38.0)
- https://github.com/aigorahub/elves/blob/main/SKILL.md (single landable PR, Cobbler default, prewalk, no-merge default)
- https://github.com/aigorahub/elves/blob/main/references/parallelves.md (one-PR integration; via index snippet)
- https://github.com/anthropics/claude-code-action/blob/main/docs/usage.md (`label_trigger`, `assignee_trigger`, `branch_prefix`, OAuth/API-key auth, bot identity, `claude_args` bounds)
- https://code.claude.com/docs/en/github-actions (issue→PR framing, OAuth subscription token, trigger checks)
- https://code.claude.com/docs/en/claude-code-on-the-web (cloud sessions survive laptop close, `--cloud` fan-out, PR/teleport review)
- https://code.claude.com/docs/en/routines (research preview, cloud execution, PR+Release-only GitHub events, `claude/` branch push guards, subscription + daily-cap usage)
- https://developers.openai.com/codex/cloud ; https://developers.openai.com/codex/third-party/github ; https://learn.chatgpt.com/docs/non-interactive-mode (Codex options; ruled out by dropped subscription)
- https://docs.github.com/en/copilot/how-tos/use-copilot-agents/cloud-agent/use-cloud-agent-on-github (assign-issue → PR + review; approve-and-run workflows)
- https://docs.github.com/en/copilot/reference/copilot-billing/request-based-billing-legacy/github-copilot-premium-requests (quota pool)
- https://github.com/anthropics/claude-code/blob/main/plugins/ralph-wiggum/README.md (official Ralph loop shape)
- https://github.com/troykelly/claude-skills ; …/skills/autonomous-orchestration/SKILL.md (11★, auto-merge, consent-implied, token-to-.env)
- https://lanes.sh/blog/integrations-have-arrived (local-board shape)
- omp://tools/task.md (OMP subagents, isolated worktrees, branch/patch merge modes)
- Repo: `AGENTS.md` ll.127–175, 234–238 (routing, `openai-codex` disabled); `skills/overnight-run/SKILL.md` ll.69–95; `skills/pr/SKILL.md`; `skills/merge/SKILL.md`; `skills/execute-plan/SKILL.md` ll.1–43; `skills/workstreams/SKILL.md` ll.1–83
- Prior research: `docs/research/claude-code-overnight-primitives-2026-09.md` (2026-09-27; usage gate, headless flags, no in-session long waits)
