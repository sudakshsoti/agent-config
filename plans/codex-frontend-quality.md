# Plan: raise Codex's frontend output

## What shipped

`skills/frontend-craft/` — one SKILL.md merging Anthropic's `frontend-design` shape
(direction first, don't default) with this repo's `design-craft` (type systems, OKLCH, APCA,
production CSS, operator context). Adds an enumerated direction list with a `node -e` random
picker, a banned-defaults list, and a non-negotiables checklist for states, contrast and
390px.

`design-craft` is deleted, its type and colour material folded in whole. The `design-craft`
subagent is renamed to `frontend-craft`; `design-foil`, `value-connect` and both READMEs now
point at the new name.

## Deferred to a separate worktree

**Overlap removal.** Twelve frontend-adjacent entries still reach Codex: `apple-design`,
`emil-design-eng`, `frontend-craft`, `design-foil`, `prototype`, `pick-ui-library`,
`ux-writing`, four animation skills, `html-doc`, and the enabled
`frontend-design@claude-plugins-official` plugin. Codex caps skills at 2% of context and
truncates descriptions once that fills, so overlap degrades discovery library-wide.

Two things that pass must know before it starts:

1. **`skills/_archive/` is not Codex-only.** `install.sh:134-138` runs one loop that links
   every skill into both `~/.claude/skills` and `~/.agents/skills`, with no exclusion hook.
   Archiving removes a skill from Claude too. Making something Codex-only requires adding a
   `CLAUDE_ONLY` list that skips the `mirror_into` call.
2. **`frontend-design` is a plugin, not a repo skill.** It can't be archived. The lever is
   `enabled = false` in `~/.codex/config.toml` (currently `:99-100`), which affects Codex
   only. Record the prior value first — `config.toml` is untracked.

**Verification, if it's ever worth the cost.** The earlier draft of this plan specified a
four-brief eval with a pinned Playwright + axe-core gate. Dropped as disproportionate for a
one-person config repo. If output still disappoints after `frontend-craft` has had real use,
that plan is in git history at `3b1e4c9` and can be revived rather than rewritten.
