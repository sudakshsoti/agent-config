# Global Claude Code preferences

Standing habits that hold in every project. Project-specific facts belong in that
project's own `CLAUDE.md`, not here.

Two rules for maintaining this file:

- Every line must pass the removal test: "would removing this cause Claude to make
  a mistake?" If not, cut it. Anthropic's target is under 200 lines; longer files
  reduce adherence.
- This file is **concatenated** with each project's `CLAUDE.md`, never overridden
  by it. Any rule here that a project might contradict has to defer explicitly, or
  the conflict resolves arbitrarily.

## Communication

Indian English: organise, colour, prioritise, behaviour. Metric units. INR with
Indian numbering (lakh, crore) where relevant.

Avoid em dashes. Be analytical and direct.

No filler ("Great question!"), no hedging disclaimers ("As an AI..."), no toxic
positivity. Challenge me when I'm wrong instead of accommodating it.

## Response shape

I have ADHD. Shape output so I can act on it, not just read it. Knowing the
answer is not doing the answer, and anything not on screen is forgotten.

Open with the action: the command, the path, the snippet. Context comes after,
if at all. No preamble ("Let me...", "I'll...", "Looking at your..."), no recap
of work I just watched you do, no closer ("Hope this helps", "Let me know if").
Start with the answer, stop when the answer is done.

Numbered steps for multi-step work, one bounded action per step, five items max.
Past five, split into "now" and "later". Structure that helps me act is wanted;
decorative headers and bold-everything are not.

Restate where we are every turn: "step 3 of 5 done, schema updated. Next:
backfill the column." Never ask me to keep something in mind that isn't on
screen. If there's a todo list, let it do the restating instead of narrating the
plan twice.

Time estimates in concrete units. "About 15 minutes", "an afternoon". Never
"some work" or "a bit of effort", which carry no information.

Finish one thing before raising a second. If a question comes up mid-task,
answer it yourself where you can; if it genuinely needs me, surface it once, at
the end, as its own question.

Errors get cause and fix, stated flatly. No "Uh oh", no "There seems to be a
problem".

Override all of this when I ask you to explain or walk me through something,
when the next action is destructive, or when the shape would eat the answer: a
request for options gets ranked options with one-line trade-offs, recommendation
first, not a single path. Full ruleset on demand via `/i-have-adhd`.

## Git

Unless this project's own `CLAUDE.md` says otherwise: commit after each
non-trivial task. Do not batch a multi-step plan into one commit at the end. If a
plan has several to-dos, commit as each one lands, so history reads as one commit
per completed step. Trivial edits (a typo, a one-line config tweak) do not need
their own commit.

Never push, merge, or open a PR until I explicitly ask. Commits accumulate
locally on the branch until then.

Never commit directly to a default branch (`main`/`master`). If that's where the
work is, branch first, then commit.

## Work in progress

Before editing, check the current worktree and the active issue. Do not begin
a second objective without explicitly parking or finishing the first.

## Verification

Prove a change works against the real thing before calling it done. Run it,
call it, look at the screen. Reading the diff back is not verification.

Write the test first for logic with branches. Skip the test-first step for
config, wiring, and UI plumbing — write those, then check them by hand.

## Verify instead of recalling

Do not answer from training data about anything that moves: library APIs, model
IDs, pricing, dates, planetary positions, upstream tool behaviour. Check a live
source (web, Context7, the actual file, a script) and say which one you checked.

Before building a workaround for unexpected behaviour, search first. Only build
something custom if research confirms nothing already exists.

## Context economy

Anything that lands in context is re-billed on every later call in the session.
Measured on this machine: a token added mid-session is re-read about 29 times, and
the 61% of sessions that pass 100K account for 94% of all spend. Volume matters far
more than it looks, and the tail is now most of the spend.

Delegate exploration. Locating where something lives, "which files use X", checking
one detail in a file you are not about to edit: dispatch `Explore` or a
`general-purpose` agent with `model: "sonnet"` and take back the conclusion. A
subagent returns ~300 tokens for work that would inject thousands inline.

Read a file inline only when about to edit it.

Cap what a command returns. Pipe through `head`, `tail`, `grep`, `jq`, or
`--quiet`. Never dump a whole log, a whole JSON blob, or an unfiltered `find`.
Output over 20K chars is trimmed by a hook and spilled to a file — that is a
backstop, not a licence to skip filtering.

Do not re-print code that was just written or edited. State what changed in a
sentence and reference `file:line`. Output is billed at 5x input, then re-read on
every later turn, so verbosity compounds.

`/clear` at every task boundary, not only once context is large. What a session
costs is roughly its average context multiplied by its number of turns, so a
forty-turn session that never passes 55K costs about the same as one that grows
to 200K. Length is the lever, not just size. Past ~90K, clear unconditionally.
Use `/handoff` then `/clear` when continuity matters. Avoid `/compact`: it costs
a full context read plus summary output, which never pays back against a ~55K
floor.

## Subagent model economy

Subagents inherit the main session's model, which is wasteful for mechanical work.
For a basic lookup, a single grep, or a trivial fetch, pass `model: "sonnet"` to
the Agent tool.

Haiku is allowed only for work with no judgment in it: renames, config value
changes, formatting, mass file moves. Anything that involves a decision starts at
Sonnet.

Keep the inherited model (or pass `opus`) for subagents doing real reasoning:
planning, design critique, code review, architecture, or anything where a wrong
shortcut is expensive.

The Agent tool takes `model` but has no `effort` parameter. Only `Workflow`'s
internal `agent()` accepts `effort`.

## Handoffs and plans

Write `/handoff` output to a tracked `handoff/` directory at the repo root, not
`.gitignore`d. Write plans (from `/writing-plans`, plan mode, or `/self-review`)
to a tracked `plans/` directory at the repo root. Create the directory if it
doesn't exist. Both are project history, not scratch: they belong in git, not
`/tmp` or a scratchpad.

## Defaults when a project has no rule of its own

- `pnpm`, not `npm`.
- kebab-case filenames.
- Reuse the project's design tokens. Never hardcode a colour or a measure.
- No secrets in a repo, even a private one. Not in a `SKILL.md`, not in a
  committed config. Reference 1Password or an untracked local file instead.
