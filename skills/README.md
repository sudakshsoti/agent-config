# Skills library

Agent Skills usable by **OMP and Pi**. Each skill is a directory holding a
`SKILL.md`; the format is the same on both.

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
  bare unquoted value.** A strict YAML parser treats an unquoted multi-line
  scalar containing a `:` (colon-space, e.g. "engineering side: teaches…") as a
  nested mapping, and the whole skill then fails to load
  (`mapping values are not allowed in this context`). The `|` block scalar in
  the template above makes colons and quotes literal — keep it. Single-line
  descriptions are also fine.

The list below covers the 36 repo-owned skills. Keep it synchronized with the
actual `skills/*/SKILL.md` directories; `scripts/lint-skills.py` validates each
skill's frontmatter and fails when this list and the source tree disagree.
The active design set is `design-interface`, `design-visual-system`, and
`design-typography`; they classify surface intent before applying hierarchy.
`frontend-artifact` reuses them for standalone browser artifacts with eight
selectable visual languages and rendered review. `frontend-design` remains an
external marketing/brand skill, not the route for product, reference, utility,
dashboard, settings, or lookup-documentation work.

- `backlog` — Run any project's backlog in Linear like a PM: capture, triage, grooming, acceptance criteria, and milestone/session planning (batch Ready issues into equal-effort, one-sitting Linear Milestones).
- `clinical-reasoning` — Clinical decision support for clinicians in India: diagnostics, differentials, labs, imaging, drug interactions, prescribing, and escalation.
- `codebase-memory` — Query a codebase knowledge graph for architecture, callers, dependencies, dead code, and impact analysis.
- `design-grill` — Interview through visual and behavioural interface decisions while recording agreed design decisions.
- `design-interface` — Design and review controls, forms, lists, dashboards, settings, documentation, and non-happy-path states.
- `design-strategy` — Industry-agnostic product and UX strategy, positioning, workflow critique, and decision logs.
- `design-typography` — Choose typefaces, pairings, hierarchy, scales, OpenType features, and font loading.
- `design-visual-system` — Define product UI art direction, colour, hierarchy, responsive layout, and CSS tokens.
- `diagnosing-bugs` — Diagnosis loop for hard bugs and performance regressions: build a tight red-capable feedback loop, minimise, rank hypotheses, instrument, fix with a regression test.
- `execute-plan` — Autonomously run a checklist plan file item-by-item — one fresh subagent per item, commit after each. Point it at a `PLAN.md`. `/execute-plan <path>`.
- `frontend-artifact` — Standalone browser explainers, visual documents and small tools, with eight selectable visual languages, a starter skeleton and validated font pairing per language, measured references, a numeric audit (`references/audit.js`) and a fresh-context critic prompt. A named language approves its defaults; otherwise the agent recommends one and waits.
- `vibe` — The interface workflow: quick tweak, shape first or risky change; Plan, Builder and Critic roles that run as subagents where the harness has them and sequentially otherwise. `pi/prompts/vibe.md` is a thin wrapper that invokes it.
- `find-skills` — Discover and install agent skills when asked "is there a skill for X".
- `geopolitics` — Opinionated analyst for wars, sanctions, trade, defence, elections, negotiations, and other statecraft between countries.
- `grilling` — Interview the user relentlessly about a plan/decision, round by round over a design tree, until nothing is left unsettled.
- `gtd` — Sudaksh's personal GTD system: capture, inbox processing, daily/weekly reviews, Todoist/calendar routing, overwhelm triage, email triage, and procrastination audits.
- `handoff` — Structured session-handoff docs for continuity across sessions.
- `harness-config-maintenance` — Safely change OMP and Pi configuration while preserving ownership and secret boundaries.
- `homelab-deploy` — RIGID homelab procedure: the deploy ritual for `/opt/stacks`, with three modes — generic stack change, the rclone-torbox safe recreate, and the n8n sqlite3 workflow dance.
- `humanizer` — Rewrite AI-sounding prose so it reads like a person, using Wikipedia's 35 "Signs of AI writing" patterns. Vendored from [blader/humanizer](https://github.com/blader/humanizer) (MIT). `/humanizer`.
- `macos-design-guidelines` — Apply Apple Human Interface Guidelines when building Mac apps with SwiftUI or AppKit.
- `maintainability-review` — Review web/frontend code for long-term maintainability (DRY, over-engineering, drift). diff/audit/triage modes. `/maintainability-review`.
- `obsidian-markdown` — Author Obsidian Flavored Markdown — wikilinks, embeds, callouts, properties.
- `peer-review` — Adversarial cross-lineage review of an engineering plan written by another agent. `/peer-review`.
- `research` — Investigate primary sources and record cited findings in a Markdown report.
- `rights-counsel` — Indian consumer, EPF, and insurance rights analyst for advice, complaints, notices, and representations.
- `self-review` — Critique your own plan against a fixed checklist, then revise it. `/self-review`.
- `shopping-research` — Purchase advisor for buying in India: product comparisons, pricing, sellers, deals, and when to buy.
- `skill-lifecycle` — Add, rename, retire, install, and audit repo-owned skills without stale inventory or orphan references.
- `specialist-delegation` — In Pi or OMP, choose specialist subagents, brief bounded work, and retain synthesis and verification responsibility.
- `strategy-counsel` — Strategic advisor for power, influence, and negotiation inside organisations and in arm's-length dealings.
- `ux-writing` — User-centered interface microcopy: buttons, errors, empty states, onboarding, voice/tone, a11y.
- `vbc-design` — Deep payer/provider healthcare design: value-based-care economics, role workflows, data and attribution gotchas, registry and cohort design, grounded in Value Connect.
- `vedic-astrology` — Vedic astrology (Jyotish) advisor for charts, dashas, transits, timing, compatibility, and remedies.
- `workstreams` — In Pi or OMP, coordinate approved implementation streams with dependencies, exclusive edit ownership, blockers, and integration verification.
- `writing-editor` — Writing partner for personal essays and blog posts: get words onto the page, then shape them into something publishable.

The retired design-pipeline skills (`app-ui`, `brand-studio`, `design-brief`,
`design-foil`, `design-review`, `frontend-craft`, `interface-composition`,
`nightjar`, and `typography-craft`) are recoverable from Git history by their
path, `skills/<name>/`. Nothing is kept on disk for them: an uninstalled skill
left in the tree still counts as catalogue drift.
`design-interface`, `design-visual-system`, and `design-typography` are active
repo-owned skills. `frontend-design` is an external marketing and brand skill,
not the route for product, reference, utility, dashboard, settings, or
lookup-documentation work.

## Implementation coordination

`specialist-delegation` owns individual worker selection and handoffs;
`workstreams` uses it when multiple implementation streams need dependency
and integration management. Both cover Pi and OMP role names. Neither changes agent permissions, model routing, or enables
named workflow features. `execute-plan` remains the agent-agnostic checklist
executor; choose one execution loop rather than stacking schedulers. Existing
implementation, UI, and review skills still own their domain-specific checks.

## Installing

Skills are delivered as source. There is one shared skills root —
`~/.agents/skills` — and both OMP and Pi read it, so a repo-owned skill is
linked once rather than once per harness. **On a new machine, clone this repo
and run the linker**:

```bash
git clone https://github.com/sudakshsoti/agent-config.git ~/dev/agent-config
cd ~/dev/agent-config && ./install.sh
```

`./install.sh` is idempotent (safe to re-run after adding a skill) and
`./install.sh --prune` clears managed symlinks for skills you've removed. To
link a single skill by hand instead:

```bash
ln -s "$PWD/skills/research" ~/.agents/skills/research
```

Link the skill directory itself, never a copy: a real directory at that path is
treated as unmanaged and is left alone with a warning.

## Notes

- **Secrets:** anything in a `SKILL.md` is committed in plaintext — never put
  a token in one. (Historical note: an old `todoist-gtd/SKILL.md` embedded a
  live Todoist token; it remains in the **claude-projects** repo's git
  history — rotate that token if you haven't.)
- Audit any third-party skill before installing; a `SKILL.md` can direct an
  agent to run code and use tools.
