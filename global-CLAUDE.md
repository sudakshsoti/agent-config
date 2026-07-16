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

`homelab` overrides the commit rule: there, leave the tree dirty for review and
never commit until asked, even after a fully verified change.

## Verify instead of recalling

Do not answer from training data about anything that moves: library APIs, model
IDs, pricing, dates, planetary positions, upstream tool behaviour. Check a live
source (web, Context7, the actual file, a script) and say which one you checked.

Before building a workaround for unexpected behaviour, search first. Only build
something custom if research confirms nothing already exists.

## Subagent model economy

Subagents inherit the main session's model, which is wasteful for mechanical work.
For a basic lookup, a single grep, or a trivial fetch, pass `model: "sonnet"` to
the Agent tool. Sonnet is the floor; never drop to Haiku.

Keep the inherited model (or pass `opus`) for subagents doing real reasoning:
planning, design critique, code review, architecture, or anything where a wrong
shortcut is expensive.

The Agent tool takes `model` but has no `effort` parameter. Only `Workflow`'s
internal `agent()` accepts `effort`.

## Defaults when a project has no rule of its own

- `pnpm`, not `npm`.
- kebab-case filenames.
- Reuse the project's design tokens. Never hardcode a colour or a measure.
- No secrets in a repo, even a private one. Not in a `SKILL.md`, not in a
  committed config. Reference 1Password or an untracked local file instead.
