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

The 34 skills below are the ones worth reaching for by name. Thirty-seven are
installed in all; `build-mode`, `to-spec`, and `wait-what` are omitted here
and route on their own triggers rather than being picked from a list.
Anything under `skills/_archive/` is kept for reference only and is
deliberately not installed — see [`_archive/README.md`](_archive/README.md).

- `commit` — Stage + commit in the user's house style (`scope: summary` + why-first body, no attribution). `/commit`.
- `diagnosing-bugs` — Diagnosis loop for hard bugs and performance regressions: build a tight red-capable feedback loop, minimise, rank hypotheses, instrument, fix with a regression test.
- `frontend-craft` — Visual direction for new UI, plus typography systems, OKLCH colour ramps, variable fonts, Tailwind/shadcn token architecture.
- `typography-craft` — Typography-only authority across screen, print/editorial, brand, display, and type-led layout.
- `design-foil` — Industry-agnostic strategy + UX advisor: brainstorm, critique, strategy docs, teardowns.
- `execute-plan` — Autonomously run a checklist plan file item-by-item — one fresh subagent per item, commit after each. Point it at a `PLAN.md`. `/execute-plan <path>`.
- `find-skills` — Discover and install agent skills when asked "is there a skill for X".
- `finite` — The advisor for a finite life: a daily orient across Linear/Todoist/notes, on-demand triage that names what a new commitment displaces, and the forced cull into a durable Season ledger. Burkeman-flavoured — kind, unflinching, subtractive.
- `git-guardrails` — Set up a hook that blocks dangerous git commands (`push`, `reset --hard`, `clean -f`, `branch -D`) before Claude Code runs them.
- `grilling` — Interview the user relentlessly about a plan/decision, round by round over a design tree, until nothing is left unsettled.
- `handoff` — Structured session-handoff docs for continuity across sessions.
- `backlog` — Run any project's backlog in Linear like a PM: capture, triage, grooming, acceptance criteria, and milestone/session planning (batch Ready issues into equal-effort, one-sitting Linear Milestones).
- `homelab-deploy` — RIGID homelab procedure: the deploy ritual for `/opt/stacks`, including the safe rclone-torbox recreate.
- `html-doc` — Turn notes, briefs and reports into one polished self-contained HTML document instead of a `.md`. `/html-doc`.
- `maintainability-review` — Review web/frontend code for long-term maintainability (DRY, over-engineering, drift). diff/audit/triage modes. `/maintainability-review`.
- `merge` — Land the current branch's PR via `gh` — checks CI, squash by default, deletes branch. `/merge`.
- `motion-craft` — Implement motion, gesture physics and component interaction polish, or name an animation effect exactly.
- `motion-review` — Find justified motion opportunities, audit a repo's existing motion, or review a motion diff without modifying product source.
- `n8n-deploy` — RIGID homelab procedure: deploy/edit n8n workflows via the sqlite3 dance without clobbering the DB.
- `obsidian-markdown` — Author Obsidian Flavored Markdown — wikilinks, embeds, callouts, properties.
- `orient` — HTML guide to a repo — what it is, what decisions shaped it, and where sprawl lives. Every claim cited to file:line. `/orient`.
- `peer-review` — Adversarial cross-lineage review of an engineering plan written by another agent. `/peer-review`.
- `pick-ui-library` — Pick the right frontend library for a task from a curated, opinionated list. `/pick-ui-library`.
- `pr` — Open a GitHub PR via `gh` — title from commits, why-first body, no AI footer. `/pr`.
- `prose-editor` — Critique + rewrite personal essays to a high editorial bar.
- `prototype` — Build several genuinely different versions of a UI piece behind a visual picker. `/prototype`.
- `push` — Safe push — sets upstream, shows outgoing commits, `--force-with-lease`, warns on main. `/push`.
- `research` — Delegate reading legwork to a background agent: investigate a question against primary sources, write findings to a cited Markdown file.
- `scope-brief` — Tiered scoping document for multi-session or ambiguous work: interview, forced non-goals, a locked scope table, then write the plan directly. `/scope-brief`.
- `self-review` — Self-review the plan you just proposed via the plan-critic subagent, then revise it. `/self-review`.
- `tdd` — Test-driven development reference: what a good test is, seams, anti-patterns, the red-green loop's rules.
- `ux-writing` — User-centered interface microcopy: buttons, errors, empty states, onboarding, voice/tone, a11y.
- `wizard` — Generate an interactive bash wizard for a manual procedure only a human can do (provisioning, credentials, third-party dashboards). `/wizard`.
- `writing-for-agents` — Reference for writing any document an agent consumes: context pointers, information hierarchy, leading words, pruning.

The nine frontend/design skills are `frontend-craft`, `typography-craft`,
`motion-craft`, `motion-review`, `design-foil`, `prototype`, `ux-writing`,
`pick-ui-library`, and `maintainability-review`. `html-doc` remains installed
as an adjacent document skill, outside that nine-skill count.

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
