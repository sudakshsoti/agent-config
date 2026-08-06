# Handoff: build loop repair

**Date:** 2026-08-06
**Branch:** `dazzling-mellow-drift` (worktree at `~/dev/worktrees/dazzling-mellow-drift`)
**Working tree:** clean. Four commits ahead of `main`, nothing pushed.

## What this session was

The user brought a draft `prd-builder` skill (from `~/Downloads/files.zip`) for
adversarial review. The review found the document good and the skill bad, and
the conversation turned into diagnosing the actual problem behind it. Output is
a plan, not an implementation. **No skill work has been done yet beyond one
deletion.**

## What changed

| Commit | What |
|---|---|
| `4771b20` | Deleted `skills/discovery-first/` and `dist/discovery-first.zip`; removed its references from `skills/build-mode/SKILL.md` (3 places) and `skills/README.md` (2 places, plus corrected the count to 25) |
| `51c53c6` | `plans/2026-08-06-build-loop-repair.md` v1 |
| `558d5d0` | Same file, rewritten as v2 after an external LLM review returned "fix before shipping" |
| `fde95d2` | Added section 5.8 to the plan: retire nine skills |

`plans/2026-08-06-build-loop-repair.md` is the single source of truth. It is
written to be read cold and supersedes anything in this handoff on detail.

## Decisions and why

**The PRD skill was the wrong fix.** The stated pain is "too confused, run in
too many directions, build 5 features at once which all break". That is three
failures: scope size (a brief fixes it), concurrency (nothing in the setup
addresses it), and isolation, meaning large uncommitted changes with no
checkpoints (also unaddressed). The PRD only touched the first and least costly.

**`discovery-first` deleted** at the user's instruction. It was a patch for
Codex jumping straight to solutions and overlapped the scoping stage the plan
introduces.

**The external review reshaped v2.** Sixteen points accepted, the important
ones being: isolation split out as its own failure with its own mechanism; the
WIP signal changed from branch age to dirty worktrees plus Linear `In Progress`
state, because branch age would have fired constantly in a repo worked via
worktrees; the causal hypothesis demoted to an instrumented experiment.

**Two pushbacks against the review**, both recorded in plan section 7: its
proposed two-week seven-metric diary is the exact high-friction ritual it warns
against elsewhere, so instrumentation is automatic instead, with the WIP gate's
override-reason field doubling as the instrument; and `brainstorming` gets
narrowed now rather than later, because its MUST-gate collision with the new
scoping skill is certain rather than speculative.

**The user then overrode the review's "retire nothing yet".** Nine skills go,
because most are cut for being too heavy to ever get invoked, which is a
judgement about working style that two weeks of logs would not settle. This is
recorded in the plan as a decision, not a finding.

## Current state

Nothing from the plan is implemented. All ten implementation steps are
outstanding. Nothing is half-done and there is no uncommitted work.

Two facts that will bite whoever picks this up:

1. **Worktree edits are not live.** `~/.claude/skills/*` and
   `~/.agents/skills/*` symlink to `~/dev/agent-config`, the main checkout, not
   to this worktree. `discovery-first` is still installed on both surfaces and
   stays that way until this branch merges and `install.sh` re-runs.
2. **The pre-commit hook** validates skill frontmatter and `dist/*.zip`
   freshness. Editing a `SKILL.md` requires `./scripts/build-zip.sh <name>`
   before the commit will pass; retiring one requires deleting its zip.

## Next action

Implementation step 1 of 10, about 5 minutes: add the WIP invariant to global
`CLAUDE.md` (the repo file `global-CLAUDE.md`, which symlinks to
`~/.claude/CLAUDE.md`). Wording is in plan section 5.1:

> Before editing, check the current worktree and the active issue. Do not begin
> a second objective without explicitly parking or finishing the first.

It goes in global instructions rather than in `build-mode` because `build-mode`
can be bypassed. Then continue down the plan's implementation order. Commit per
step, per the repo's own convention.
