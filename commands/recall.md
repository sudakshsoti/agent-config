---
description: Load relevant context from the ~/dev/claude-memory vault for the current task
argument-hint: [optional topic to recall]
---

Recall from the persistent memory vault at `~/dev/claude-memory`. This is the QUERY
operation defined in that repo's `CLAUDE.md`; follow it exactly:

1. Work out what I am currently doing in the active repo (the conversation so far,
   plus `$ARGUMENTS` if given) and derive the task's key terms from that. Grep
   `~/dev/claude-memory/wiki/` for those terms (e.g. `grep -ril <term>
   ~/dev/claude-memory/wiki/`) and read ONLY the pages that hit. Follow `[[links]]`
   outward only when they point somewhere the task needs.
2. If grep comes up empty, fall back to reading `~/dev/claude-memory/CLAUDE.md` and
   `~/dev/claude-memory/wiki/index.md` and decide from the index summaries whether
   any page is relevant under different wording than the terms tried. That is the
   whole cost of the fallback.
3. Do NOT dump the whole wiki into context. Never bulk-read `wiki/`, and never
   read anything in `raw/` during recall.
4. If neither grep nor the index turns up anything, say so rather than guessing
   at what the vault contains.

Finish with a one-paragraph summary of what you loaded and how it bears on the
task at hand. If nothing in the vault is relevant, say exactly that.
