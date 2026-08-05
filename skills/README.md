# Skills library

Agent Skills usable by **both Claude Code and Claude.ai**. Each skill is a
directory holding a `SKILL.md`; the format is identical across surfaces.

## Convention

```
skills/
  <skill-name>/
    SKILL.md            ← required: YAML frontmatter + instructions
    references/         ← optional: extra markdown loaded on demand
    scripts/            ← optional: executable helpers run via bash
    assets/             ← optional: templates, data, examples
```

`SKILL.md` frontmatter (only `name` and `description` are required):

```yaml
---
name:
  skill-name # ≤64 chars, [a-z0-9-] only, must match the folder
  # name, no "claude"/"anthropic", no XML tags
description: | # ≤1024 chars. Say what it does AND when to use it —
  # this is the only text always in context, so triggers
  # belong here.
---
```

- **Directory name must equal `name`.** Rename both together.
- Keep the `SKILL.md` body under ~5k tokens; push bulk (reference tables, long
  protocols, schemas) into `references/` and point to it by relative path
  (`references/foo.md`). It loads only when needed — no context cost otherwise.
- `description` is the discovery surface. If a skill isn't triggering, the fix
  is almost always a sharper `description`, not a longer body.
- **Multi-line `description`s must use a block scalar (`|` or `>-`), never a
  bare unquoted value.** Claude Code's YAML parser is lenient, but Codex's is
  strict: an unquoted multi-line scalar containing a `: ` (colon-space, e.g.
  "engineering side: teaches…") parses as a nested mapping and the whole skill
  fails to load (`mapping values are not allowed in this context`). The `|`
  block scalar in the template above makes colons and quotes literal — keep it.
  Single-line descriptions are also fine.

## Current skills

The 31 skills below are the installed set. Anything under `skills/_archive/` is
kept for reference only and is deliberately not installed — see
[`_archive/README.md`](_archive/README.md).

- `animation-vocabulary` — Reverse-lookup glossary: describe a motion effect, get its exact name.
- `apple-design` — Apple's interface and fluid-motion approach translated for the web: gestures, springs, materials, type.
- `commit` — Stage + commit in the user's house style (`scope: summary` + why-first body, no attribution). `/commit`.
- `frontend-craft` — Visual direction for new UI, plus typography systems, OKLCH colour ramps, variable fonts, Tailwind/shadcn token architecture.
- `design-foil` — Industry-agnostic strategy + UX advisor: brainstorm, critique, strategy docs, teardowns.
- `discovery-first` — Light discovery pass for vague/subjective/exploratory requests: frame the problem, name unknowns, recommend a direction, then implement. `/discovery-first`.
- `emil-design-eng` — Emil Kowalski's philosophy on UI polish, component design, and animation judgement.
- `execute-plan` — Autonomously run a checklist plan file item-by-item — one fresh subagent per item, commit after each. Point it at a `PLAN.md`. `/execute-plan <path>`.
- `explain-this` — Explain the plan or the finished work in plain English, then teach the one concept behind it. `/explain-this`.
- `find-animation-opportunities` — Find places that don't animate but should, with exact values. Read-only; proposes, doesn't implement.
- `find-skills` — Discover and install agent skills when asked "is there a skill for X".
- `handoff` — Structured session-handoff docs for continuity across sessions.
- `homelab-backlog` — Run the homelab/finance backlog in Linear (team OKLCH): capture, triage, grooming, acceptance criteria.
- `homelab-deploy` — RIGID homelab procedure: the deploy ritual for `/opt/stacks`, including the safe rclone-torbox recreate.
- `html-doc` — Turn notes, briefs and reports into one polished self-contained HTML document instead of a `.md`. `/html-doc`.
- `improve-animations` — Survey a codebase's motion code and produce a prioritised audit plus implementation plans. Read-only.
- `maintainability-review` — Review web/frontend code for long-term maintainability (DRY, over-engineering, drift). diff/audit/triage modes. `/maintainability-review`.
- `merge` — Land the current branch's PR via `gh` — checks CI, squash by default, deletes branch. `/merge`.
- `n8n-deploy` — RIGID homelab procedure: deploy/edit n8n workflows via the sqlite3 dance without clobbering the DB.
- `obsidian-markdown` — Author Obsidian Flavored Markdown — wikilinks, embeds, callouts, properties.
- `orient` — HTML guide to a repo — what it is, what decisions shaped it, and where sprawl lives. Every claim cited to file:line. `/orient`.
- `peer-review` — Adversarial cross-lineage review of an engineering plan written by another agent. `/peer-review`.
- `pick-ui-library` — Pick the right frontend library for a task from a curated, opinionated list. `/pick-ui-library`.
- `pr` — Open a GitHub PR via `gh` — title from commits, why-first body, no AI footer. `/pr`.
- `prose-editor` — Critique + rewrite personal essays to a high editorial bar.
- `prototype` — Build several genuinely different versions of a UI piece behind a visual picker. `/prototype`.
- `push` — Safe push — sets upstream, shows outgoing commits, `--force-with-lease`, warns on main. `/push`.
- `review-animations` — Review animation code against a high craft bar; approval is earned. `/review-animations`.
- `self-review` — Self-review the plan you just proposed via the plan-critic subagent, then revise it. `/self-review`.
- `ux-writing` — User-centered interface microcopy: buttons, errors, empty states, onboarding, voice/tone, a11y.
- `value-connect` — Strategy + UX advisor for enterprise/healthcare design: brainstorm, audit, design-process artifacts.

## Installing per surface

Skills **do not sync** between surfaces — install separately where you want each one.

### Claude Code

Filesystem-based, no upload. **On a new machine, clone this repo and run the
linker** — it symlinks every skill here into `~/.claude/skills/`:

```bash
git clone https://github.com/sudakshsoti/agent-config.git ~/dev/agent-config
cd ~/dev/agent-config && ./install.sh
```

`./install.sh` is idempotent (safe to re-run after adding a skill) and
`./install.sh --prune` clears symlinks for skills you've removed. To link a
single skill by hand instead:

```bash
ln -s "$PWD/skills/prose-editor" ~/.claude/skills/prose-editor      # personal
ln -s "$PWD/skills/prose-editor" /path/to/project/.claude/skills/   # project-scoped
```

Claude discovers each by `name`/`description`; invoke implicitly or with `/prose-editor`.

### Claude.ai (Pro / Max / Team / Enterprise, code execution on)

Upload as a **zip of the skill folder** via Settings → Features → Skills:

```bash
cd skills && zip -r prose-editor.zip prose-editor && cd -
```

Then upload `prose-editor.zip`. Uploaded per-user; re-upload after edits.

### Claude API

Upload via the `/v1/skills` endpoints and reference the `skill_id` in the
`container` param (needs the `skills-2025-10-02` + `code-execution-2025-08-25`
beta headers). Note: API skills run with **no network access**.

## Notes

- **Secrets:** anything in a `SKILL.md` is committed in plaintext — never put
  a token in one. (Historical note: an old `todoist-gtd/SKILL.md` embedded a
  live Todoist token; it remains in the **claude-projects** repo's git
  history — rotate that token if you haven't.)
- Audit any third-party skill before installing; a `SKILL.md` can direct Claude
  to run code and use tools.
