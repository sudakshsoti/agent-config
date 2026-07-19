---
description: Save what we just decided or learned to the ~/dev/claude-memory vault and ingest it
argument-hint: [optional note on what to remember]
---

Save to the persistent memory vault at `~/dev/claude-memory`, then fold it in.

1. Distil what this session just decided, learned, or established (use
   `$ARGUMENTS` as the steer if given). Durable facts only: decisions with
   reasoning, stated preferences, project status changes, non-obvious
   configuration. Skip transient session state and anything git history already
   records.
2. Get the real timestamp with `date +%Y-%m-%d-%H%M` (never guess it) and write
   the material as a new file in `~/dev/claude-memory/raw/` named
   `YYYY-MM-DD-HHMM-short-slug.md`, slug in lowercase-kebab-case. `raw/` is
   immutable source material: add this new file, never edit an existing one.
3. Run the INGEST operation on that file, exactly as defined by
   `~/dev/claude-memory/CLAUDE.md` and the full procedure in
   `~/dev/claude-memory/.claude/commands/ingest.md`: create or update the relevant
   `wiki/` pages, add backlinks, update `wiki/index.md`, and append an entry to
   `wiki/log.md`. Prefer updating an existing page over creating a
   near-duplicate, and respect the supersession rules for anything the new
   material contradicts.
4. Commit in `~/dev/claude-memory` following that repo's conventions.
5. Confirm back to me exactly which raw file was written and which wiki page(s)
   were created or updated.
