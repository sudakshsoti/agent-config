# Build Loop Repair Plan

**Date:** 2026-08-06
**Repo:** `~/dev/agent-config` (branch `dazzling-mellow-drift`)
**Status:** Proposal, not started. One prerequisite already landed (see "Already done").

> **For the reviewing model:** this document is written to be read cold, without
> repo access. Everything you need is inline. I want an adversarial second
> opinion, not validation. The specific questions I want attacked are at the
> bottom, but do not limit yourself to them. If the diagnosis in section 2 is
> wrong, say so first and ignore the rest of the plan.

---

## 1. Context you need

**Who.** A solo builder. Senior UX designer by trade, not a professional
engineer. Ships personal side projects and homelab tooling almost entirely
through Claude Code and Codex. Has ADHD, which matters here for one specific
reason: anything not currently on screen is effectively forgotten, and an idea
that has no safe place to go gets acted on immediately.

**What this repo is.** A configuration repo for AI coding agents. Its main
contents are *skills*: directories containing a `SKILL.md`, which is markdown
with YAML frontmatter holding a `name` and a `description`. The agent reads
every installed skill's `description` and decides, per turn, which skill bodies
to load into its context. A skill is therefore two things at once: a piece of
instruction, and a routing target competing with every other skill for the same
trigger.

**How they get installed.** `install.sh` symlinks each `skills/<name>/` to both
`~/.claude/skills/<name>` and `~/.agents/skills/<name>`. The repo is the live
source of truth, so editing a `SKILL.md` takes effect immediately on both
surfaces without reinstalling.

**Two surfaces, asymmetric controls.**

- Claude Code reads `~/.claude/skills` and supports a `skillOverrides` map in
  `settings.json` that can switch an individual skill off.
- Codex reads `~/.agents/skills` and has **no per-skill disable**. It also caps
  total skill content at 2% of its context window and starts truncating every
  skill's description once that budget fills. So an unused skill is not free on
  Codex: it degrades discovery for the whole set.
- Consequence, and this corrects something I said earlier in conversation:
  `skillOverrides` alone is not enough to retire a skill. It fixes Claude and
  does nothing for Codex. The repo's actual retirement mechanism is moving the
  directory to `skills/_archive/`, which is deliberately not installed but stays
  recoverable in git.

**Repo hygiene constraints.** A pre-commit hook validates skill frontmatter and
checks that `dist/<name>.zip` matches each skill. Retiring a skill means
removing its zip. Plans live in a tracked `plans/` directory at the repo root.

**Current inventory.** 39 installed skills. 13 of them are vendored from the
"superpowers" skill collection, marked `(V)` below, and were adopted wholesale
rather than written for this setup.

---

## 2. The pain point

In the builder's own words:

> "I'm too confused and run it too many directions then I find myself building
> 5 features at once which all break."

They believed the fix was a PRD-writing skill: interview them up front, produce
a locked scope document, and thereby prevent the spiral.

**My diagnosis is that this is three separate failures, and a PRD addresses
only the first.**

1. **Too big.** A project is started without a defined edge, so a two-day task
   becomes a twenty-day one. A scoping document genuinely fixes this.
2. **Too many.** Five things in flight simultaneously. A scoping document does
   nothing here. You can hold five perfectly scoped documents and still be
   editing all five projects on the same afternoon.
3. **Everything breaks at once.** This is a symptom of #2, not an independent
   coding problem. Five interleaved, uncommitted changes in one working tree
   mean a failure has five candidate causes and no known-good state to revert
   to. Each change alone would be a ten-minute debug. Together the debugging
   cost is unbounded, so the builder bounces off and starts a sixth thing.

**Why #2 happens, specifically.** Not weak discipline. An idea that arrives
mid-build has nowhere to go except the working tree. There is a Linear backlog
and a skill that manages it, but nothing connects that backlog to the *moment of
temptation*. Writing an idea down feels like losing it, so it gets built
instead. Under ADHD this is not a preference, it is close to a reflex.

The load-bearing claim of this whole plan is therefore: **deferral only works if
deferral is visibly safe.** Cutting scope has to produce a filed, numbered,
returning artefact, or the builder will not cut.

---

## 3. Current state of the build loop

| Stage | Skills that currently claim it |
|---|---|
| Capture an idea | `homelab-backlog` (writes to Linear) |
| Pick what to work on | `homelab-backlog` |
| Decide what the thing is | `brainstorming` (V) |
| Break into steps | `writing-plans` (V) |
| Check the plan | `self-review`, `peer-review` |
| Build | `build-mode`, `execute-plan`, `executing-plans` (V), `subagent-driven-development` (V), `dispatching-parallel-agents` (V), `using-git-worktrees` (V) |
| Prove it works | `test-driven-development` (V), `verification-before-completion` (V), `systematic-debugging` (V), `requesting-code-review` (V), `receiving-code-review` (V), `maintainability-review` |
| Ship | `commit`, `push`, `pr`, `merge`, `finishing-a-development-branch` (V) |
| Return later | `orient`, `handoff`, `explain-this` |

Three structural problems in that table:

**A. Nothing anywhere enforces a work-in-progress limit.** No stage checks
whether unfinished work already exists before starting new work. This is the
direct cause of failure #2 and it is absent from every skill.

**B. Capture and scoping are disconnected.** No mechanism turns "we decided not
to do this" into a backlog item. So deferral equals deletion, and the builder
avoids deferring.

**C. Several stages have multiple owners, so routing is nondeterministic.** The
worst case is the "decide what the thing is" stage. `brainstorming` opens with
"You MUST use this before any creative work" and contains a hard gate blocking
all implementation until a design is verbally approved. It produces no saved
artefact. Any new scoping skill lands in exactly this trigger window and loses
to the stronger imperative, or fights it. Similarly, the build stage has six
claimants and the verification stage has six.

---

## 4. Already done

Commit `4771b20` deleted the `discovery-first` skill. It existed to stop Codex
jumping straight to a solution, and it overlapped the scoping stage this plan
introduces. References in `build-mode` and the skills README were removed.

Note: it remains live on both surfaces until this branch merges into the main
checkout and `install.sh` is re-run, because the symlinks resolve to
`~/dev/agent-config`, not to this worktree.

---

## 5. Proposal

Five changes, in priority order. Changes 1 and 2 are mechanisms and are the
point of the plan. Changes 3 to 5 are consolidation and only buy predictability.

### Change 1: a work-in-progress gate in `build-mode`

**The fix for failure #2.** Before `build-mode` makes any edit, it checks for
existing unfinished work and refuses to proceed silently.

Proposed check:

- `git status --porcelain` for uncommitted changes unrelated to the current ask
- unmerged local feature branches, and how old each is

If either is non-empty, `build-mode` stops and presents what is already open,
then asks for one of three answers: finish that first, park it (commit as
work-in-progress and file a Linear issue to resume), or proceed anyway with a
stated reason. It does not choose on the builder's behalf.

**Effort:** about 15 minutes. It is roughly 20 lines added to an existing skill.

**Why it goes in `build-mode` and not the scoping skill:** the scoping skill is
not loaded at the moment the fifth feature starts. `build-mode` is, by
definition, because that is the skill that starts work.

### Change 2: a scoping skill, `prd-builder`, that files what it cuts

**The fix for failures #1 and, indirectly, #2.** A skill that interviews before
a build, produces a short saved document, and files every cut item into Linear
at lock time.

A draft of this skill already exists and was reviewed adversarially. The
findings that shaped the spec below: the original duplicated four existing
skills, hardcoded the builder's name and job title into the body, put its output
in a third competing directory, summarised its own workflow in the description
(which the repo's own skill-authoring guidance identifies as a trap that makes
agents skip the body), ran an unbounded interview, and placed its anti-scope-creep
step in a session that will have been cleared before the build begins.

Revised spec:

- **Description:** when-to-use only, no workflow summary, under 40 words. Codex
  truncates long descriptions and degrades the whole catalogue.
- **Step 0.** Ask whether something already does this, and search before
  building. The most expensive scope failure is building an existing thing.
- **Step 1.** Interview, two to three questions per turn, **hard cap of two
  rounds**. Then write the draft with unresolved points marked as assumptions
  and let the builder correct the document. Correcting a wrong draft costs far
  less activation energy than answering open questions, which matters here more
  than document quality.
- **Step 2.** Non-goals are not asked open-endedly. The skill proposes three
  plausible adjacent features itself and forces each into in-scope, later, or
  dropped. People cannot reliably enumerate their own non-goals.
- **Step 3.** Write to `plans/YYYY-MM-DD-<slug>-prd.md`. Not `docs/prd/`, which
  would be a third convention alongside `plans/` and the vendored
  `docs/superpowers/plans/`.
- **Step 4.** On lock, every "later" and "dropped" row is filed into Linear
  through `homelab-backlog`. **This step is the whole point.** Without it the
  cuts are text in a file nobody reopens.
- **Step 5.** Hand off to `writing-plans` for the phase breakdown and stop.
  Do not reimplement planning.

Document template sections: Problem, Goals, Non-goals, a scope table with
in-v1 / later / dropped columns, Definition of done (checkable statements only),
Success (distinct from done), Constraints including a stated time budget, a
**tripwire** ("if this is not done after N sessions, stop and re-scope rather
than push through"), an **Amendments log** (date, what changed, why), and Open
questions.

The amendments log matters more than it looks. Three individually reasonable
amendments are what a twenty-day spiral is actually made of, and without a log
that pattern is invisible.

The plan file that `writing-plans` produces gets a `Source PRD: <path>` header
plus a standing instruction to stop and ask when work appears that is not in
scope. The scope guard has to live in the execution artefact, because the
scoping session will have been cleared by then.

**Effort:** about 30 minutes.

### Change 3: retire `brainstorming`

It occupies the same trigger window as `prd-builder`, asserts a stronger
imperative, and saves nothing. Two owners of one stage is worse than either
owner alone. Move to `skills/_archive/`, and add a `skillOverrides` entry so
Claude stops loading it immediately.

### Change 4: thin the build and verification stages

Retire `executing-plans`, `subagent-driven-development`,
`dispatching-parallel-agents`, `requesting-code-review`,
`receiving-code-review`, and `finishing-a-development-branch`. All are vendored,
all duplicate a skill that is kept, and all are recoverable from git and
`dist/`.

Kept at build: `build-mode` for a single change, `execute-plan` for a checklist,
`using-git-worktrees` for isolation (noting that worktrees also make it *easier*
to run several features at once, which is the disease).

Kept at verification: `verification-before-completion`, `systematic-debugging`,
`test-driven-development` for logic, `maintainability-review` for periodic
audits.

### Change 5: correct the plan-path convention

`writing-plans` writes to `docs/superpowers/plans/`. The repo convention and the
builder's global instructions say `plans/` at the repo root. One-line edit.

**Net inventory:** 39 skills to 33. Seven retired, one added.

---

## 6. Explicit non-goals of this plan

- Not rewriting the vendored superpowers skills that are kept.
- Not introducing hooks or automation that run outside the agent.
- Not changing anything about the craft skills (frontend, motion, UX writing,
  design strategy) or the homelab operations skills.
- Not adding a project-management layer beyond the Linear backlog that already
  exists.

---

## 7. Risks and things that could be wrong

1. **The WIP gate could become alarm fatigue.** This repo is worked on in git
   worktrees, so unmerged branches are normal rather than exceptional. A gate
   that fires on every session gets dismissed reflexively within a week, at
   which point it is worse than nothing because it creates a false sense of
   protection. Threshold design is the open problem: which branches count, how
   old, and does an unrelated dirty file really block a start.
2. **The Linear filing step adds friction at the exact moment scope is being
   cut.** If filing four deferred items takes four round trips, the builder will
   stop locking documents at all.
3. **Retiring six vendored skills may remove capability that is not currently
   used but would be valuable later**, particularly the multi-agent execution
   path. Mitigated by archiving rather than deleting.
4. **The diagnosis could be wrong.** If the real cause of five-things-at-once is
   boredom with the current task rather than fear of losing an idea, then the
   Linear wiring solves nothing and the WIP gate becomes something to route
   around. I do not have evidence to separate these two explanations.
5. **This plan is itself scope creep.** It proposes touching nine skills to fix
   a problem where two changes carry all the value. A reviewer should consider
   whether changes 3 to 5 should be dropped or deferred.

---

## 8. Questions for the reviewing model

1. Is the three-failure decomposition in section 2 right? Is there a simpler
   explanation for "five features at once" that this plan misses entirely?
2. Is the WIP gate placed correctly in `build-mode`, given that the builder can
   always start work without invoking any skill at all? Is there a placement
   that cannot be bypassed, short of a git hook?
3. Risk 1 is the one I am least sure about. What threshold makes a WIP gate
   survive daily use without being ignored?
4. Is "file every cut item into the backlog" actually sufficient to make
   deferral feel safe, or is it a rationalisation? What would falsify it?
5. Changes 3 to 5 remove seven skills. Is consolidating routing worth that, or
   is the honest answer to ship changes 1 and 2 and leave the rest alone?
6. Is there a cheaper intervention than all of this that would move the same
   needle? Assume the builder will adopt exactly one habit, not five.
