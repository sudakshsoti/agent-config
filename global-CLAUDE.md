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

Avoid em dashes. Minimal formatting. Be analytical and direct.

No filler ("Great question!"), no hedging disclaimers ("As an AI..."), no toxic
positivity. Challenge me when I'm wrong instead of accommodating it.

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

## Verify instead of recalling

Do not answer from training data about anything that moves: library APIs, model
IDs, pricing, dates, planetary positions, upstream tool behaviour. Check a live
source (web, Context7, the actual file, a script) and say which one you checked.

Before building a workaround for unexpected behaviour, search first. Only build
something custom if research confirms nothing already exists.

## Context economy

Anything that lands in context is re-billed on every later call in the session.
Measured on this machine: a token added mid-session is re-read about 33 times, and
the 35% of sessions that pass 100K account for 78% of all spend. Volume matters far
more than it looks.

Delegate exploration. Locating where something lives, "which files use X", checking
one detail in a file you are not about to edit: dispatch `Explore` or a
`general-purpose` agent with `model: "sonnet"` and take back the conclusion. A
subagent returns ~300 tokens for work that would inject thousands inline.

Read a file inline only when about to edit it.

Do not re-print code that was just written or edited. State what changed in a
sentence and reference `file:line`. Output is billed at 5x input, then re-read on
every later turn, so verbosity compounds.

At a task boundary past ~180K, stop and `/clear` rather than pushing on. Use
`/handoff` then `/clear` when continuity matters. Avoid `/compact`: it costs a full
context read plus summary output, which never pays back against a ~38K floor.

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
