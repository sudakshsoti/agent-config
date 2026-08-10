# Vendored mattpocock/skills skills

Nine skills were vendored from Matt Pocock's [`mattpocock/skills`](https://github.com/mattpocock/skills)
repo, at commit `84fdeffd12f2ee307994d1eb6feb48173b6e0502` (2026-08-10). They
replace the five superpowers skills removed the same day — see the "Why"
section below and `git log --follow` on the individual skill directories for
that removal.

Installed under `skills/`:

`diagnosing-bugs`, `git-guardrails`, `grilling`, `research`,
`tdd`, `to-spec`, `wait-what`, `wizard`, `writing-for-agents`.

Deliberately not vendored — either redundant with a skill already in this
repo, or tuned for team-scale process this repo doesn't run:

- `code-review`, `handoff`, `prototype` — this repo already has one of each,
  more fully featured for this setup.
- `to-tickets`, `wayfinder` — overlap `homelab-backlog` and `scope-brief`
  respectively; the upstream versions assume a generic issue tracker instead
  of this repo's Linear/OKLCH conventions.
- `codebase-design`, `domain-modeling`, `improve-codebase-architecture`,
  `triage` — assume team-scale process (ADRs, ubiquitous-language docs, a
  formal triage pipeline) this repo doesn't run solo.
- `resolving-merge-conflicts`, `to-questionnaire`, `teach` — low-frequency
  enough to invoke ad hoc without a dedicated skill.
- `ask-matt`, `setup-matt-pocock-skills`, `misc/migrate-to-shoehorn`,
  `misc/scaffold-exercises`, `misc/setup-pre-commit` — tied to Matt's own
  repo/stack conventions, not portable.
- Everything under `in-progress/` — marked work-in-progress upstream.

## What was adapted

Copied as-is except for cross-references to skills that weren't vendored:

- `diagnosing-bugs`: the closing pointer to `/improve-codebase-architecture`
  (not vendored) became a plain instruction to state the architectural
  recommendation directly.
- `tdd`: the pointer to `/codebase-design` (not vendored) for seam-shape
  questions became an instruction to settle the question with the user
  directly instead of consulting a shared vocabulary skill.
- `to-spec`: upstream publishes the spec to Matt's configured issue tracker
  and depends on `/setup-matt-pocock-skills` having run first (tracker +
  triage-label setup). Neither exists here, so it now writes the spec to a
  Markdown file in whatever directory the repo already uses for such notes
  (falling back to asking the user), and the `ready-for-agent` tracker label
  step was dropped.
- `misc/git-guardrails-claude-code` was renamed to `git-guardrails` — skill
  names may not contain "claude" (`scripts/lint-skills.py`).

Each skill's `agents/openai.yaml` (an OpenAI-agent registration file specific
to Matt's own tooling, not part of this repo's `SKILL.md`-only convention —
see `skills/README.md`) was dropped rather than copied.

## Licence

MIT, Copyright (c) 2026 Matt Pocock. Full text kept beside this note at
`vendored-mattpocock-skills-LICENSE`.
