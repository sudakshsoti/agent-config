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
  strict: an unquoted multi-line scalar containing a `:` (colon-space, e.g.
  "engineering side: teaches…") parses as a nested mapping and the whole skill
  fails to load (`mapping values are not allowed in this context`). The `|`
  block scalar in the template above makes colons and quotes literal — keep it.
  Single-line descriptions are also fine.

The list below covers the repo-owned skills. Trimmed to 36 on 2026-08-19 after a
usage audit: any skill unused across 1,203 transcripts (2026-07 through
2026-08-19, at least 9 days old) was retired. The active design set is
`design-interface`, `design-visual-system`, and `design-typography`; they classify
surface intent before applying hierarchy. `frontend-design` remains an external
marketing/brand skill, not the route for product, reference, utility, dashboard,
settings, or lookup-documentation work. Retired design-pipeline skills remain
recoverable under `archive/skills/`.

- `backlog` — Run any project's backlog in Linear like a PM: capture, triage, grooming, acceptance criteria, and milestone/session planning (batch Ready issues into equal-effort, one-sitting Linear Milestones).
- `clinical-reasoning` — Clinical decision support for clinicians in India: diagnostics, differentials, labs, imaging, drug interactions, prescribing, and escalation.
- `commit` — Stage + commit in the user's house style (`scope: summary` + why-first body, no attribution). `/commit`.
- `dbt` — Dialectical Behaviour Therapy in the Linehan tradition: skills coaching, chain analysis, and DBT materials.
- `diagnosing-bugs` — Diagnosis loop for hard bugs and performance regressions: build a tight red-capable feedback loop, minimise, rank hypotheses, instrument, fix with a regression test.
- `execute-plan` — Autonomously run a checklist plan file item-by-item — one fresh subagent per item, commit after each. Point it at a `PLAN.md`. `/execute-plan <path>`.
- `find-skills` — Discover and install agent skills when asked "is there a skill for X".
- `finite` — The advisor for a finite life: a daily orient across Linear/Todoist/notes, on-demand triage that names what a new commitment displaces, and the forced cull into a durable Season ledger. Burkeman-flavoured — kind, unflinching, subtractive.
- `geopolitics` — Opinionated analyst for wars, sanctions, trade, defence, elections, negotiations, and other statecraft between countries.
- `grilling` — Interview the user relentlessly about a plan/decision, round by round over a design tree, until nothing is left unsettled.
- `gtd` — Sudaksh's personal GTD system: capture, inbox processing, daily/weekly reviews, Todoist/calendar routing, overwhelm triage, email triage, and procrastination audits.
- `handoff` — Structured session-handoff docs for continuity across sessions.
- `homelab-deploy` — RIGID homelab procedure: the deploy ritual for `/opt/stacks`, including the safe rclone-torbox recreate.
- `humanizer` — Rewrite AI-sounding prose so it reads like a person, using Wikipedia's 35 "Signs of AI writing" patterns. Vendored from [blader/humanizer](https://github.com/blader/humanizer) (MIT). `/humanizer`.
- `maintainability-review` — Review web/frontend code for long-term maintainability (DRY, over-engineering, drift). diff/audit/triage modes. `/maintainability-review`.
- `merge` — Land the current branch's PR via `gh` — checks CI, squash by default, deletes branch. `/merge`.
- `n8n-deploy` — RIGID homelab procedure: deploy/edit n8n workflows via the sqlite3 dance without clobbering the DB.
- `obsidian-markdown` — Author Obsidian Flavored Markdown — wikilinks, embeds, callouts, properties.
- `orient` — HTML guide to a repo — what it is, what decisions shaped it, and where sprawl lives. Every claim cited to file:line. `/orient`.
- `peer-review` — Adversarial cross-lineage review of an engineering plan written by another agent. `/peer-review`.
- `pr` — Open a GitHub PR via `gh` — title from commits, why-first body, no AI footer. `/pr`.
- `push` — Safe push — sets upstream, shows outgoing commits, `--force-with-lease`, warns on main. `/push`.
- `rights-counsel` — Indian consumer, EPF, and insurance rights analyst for advice, complaints, notices, and representations.
- `self-review` — Self-review the plan you just proposed via the plan-critic subagent, then revise it. `/self-review`.
- `shopping-research` — Purchase advisor for buying in India: product comparisons, pricing, sellers, deals, and when to buy.
- `strategy-counsel` — Strategic advisor for power, influence, and negotiation inside organisations and in arm's-length dealings.
- `update-branch-name` — Rename the current branch to a semantic-prefix + kebab-case convention, preferring GitHub's server-side rename so an open PR isn't orphaned. `/update-branch-name`.
- `ux-writing` — User-centered interface microcopy: buttons, errors, empty states, onboarding, voice/tone, a11y.
- `vbc-design` — Deep payer/provider healthcare design: value-based-care economics, role workflows, data and attribution gotchas, registry and cohort design, grounded in Value Connect.
- `vedic-astrology` — Vedic astrology (Jyotish) advisor for charts, dashas, transits, timing, compatibility, and remedies.
- `writing-editor` — Writing partner for personal essays and blog posts: get words onto the page, then shape them into something publishable.

The retired `design-brief` pipeline (`design-brief`, `app-ui`,
`interface-composition`, `brand-studio`, `design-strategy`, and `design-review`)
and `nightjar` remain under `archive/skills/`. `design-interface`,
`design-visual-system`, and `design-typography` are active repo-owned skills. `frontend-design` is an external marketing and brand skill installed by the
manifest, and is limited to those surfaces by the global interface-intent
contract. Everything retired is recoverable from git history or
`archive/skills/`.

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
ln -s "$PWD/skills/commit" ~/.claude/skills/commit      # personal
ln -s "$PWD/skills/commit" /path/to/project/.claude/skills/   # project-scoped
```

Claude discovers each by `name`/`description`; invoke implicitly or with `/commit`.

### Claude.ai (Pro / Max / Team / Enterprise, code execution on)

Upload as a **zip of the skill folder** via Settings → Features → Skills:

```bash
cd skills && zip -r commit.zip commit && cd -
```

Then upload `commit.zip`. Uploaded per-user; re-upload after edits.

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
