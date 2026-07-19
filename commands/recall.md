---
description: Load relevant context from the ~/dev/claude-memory vault for the current task
argument-hint: [optional topic to recall]
---

Recall from the persistent memory vault at `~/dev/claude-memory`. This is the QUERY
operation defined in that repo's `CLAUDE.md`; follow it exactly:

1. Read `~/dev/claude-memory/CLAUDE.md` and `~/dev/claude-memory/wiki/index.md` first.
   That is the whole startup cost.
2. Work out what I am currently doing in the active repo (the conversation so
   far, plus `$ARGUMENTS` if given). From the index summaries, decide which wiki
   pages that task actually needs, and read ONLY those from
   `~/dev/claude-memory/wiki/`. Follow `[[links]]` outward only when they point
   somewhere the task needs.
3. Do NOT dump the whole wiki into context. Never bulk-read `wiki/`, and never
   read anything in `raw/` during recall.
4. If the index implies a page should exist but it does not, say so rather than
   guessing at its contents.

Finish with a one-paragraph summary of what you loaded and how it bears on the
task at hand. If nothing in the vault is relevant, say exactly that.
