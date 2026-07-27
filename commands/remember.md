---
description: Save what we just decided or learned to the ~/dev/claude-memory vault and ingest it
argument-hint: [optional note on what to remember]
---

Save to the persistent memory vault at `~/dev/claude-memory`, then fold it in —
but do none of that work here. Your entire job in this session is to dispatch a
fork and relay its one confirmation line.

Make exactly one `Agent` tool call with `subagent_type: "fork"`. Do not read the
vault, do not distil, do not run `date`, do not write or commit anything
yourself. A fork inherits this whole conversation, so it can see the material
directly; the ingest procedure loads in its context, never in ours.

Pass the fork this prompt (substituting `$ARGUMENTS` inline):

> You have inherited the full conversation from the parent session. Save its
> durable material to the memory vault at `~/dev/claude-memory`.
>
> 1. Distil what this session decided, learned, or established. Use this steer if
>    it is non-empty: `$ARGUMENTS`. Durable facts only: decisions with reasoning,
>    stated preferences, project status changes, non-obvious configuration. Skip
>    transient session state and anything git history already records.
> 2. Get the real timestamp with `date +%Y-%m-%d-%H%M` (never guess it) and write
>    the material as a new file in `~/dev/claude-memory/raw/` named
>    `YYYY-MM-DD-HHMM-short-slug.md`, slug in lowercase-kebab-case. `raw/` is
>    immutable source material: add this new file, never edit an existing one.
> 3. Run the INGEST operation on that file. Read `~/dev/claude-memory/CLAUDE.md`
>    and the full procedure in `~/dev/claude-memory/.claude/commands/ingest.md`
>    and follow them exactly — create or update the relevant `wiki/` pages, add
>    backlinks, update `wiki/index.md`, append an entry to `wiki/log.md`. Prefer
>    updating an existing page over creating a near-duplicate, and respect the
>    supersession rules for anything the new material contradicts.
> 4. Commit in `~/dev/claude-memory` following that repo's conventions.
> 5. Return **exactly one line** and nothing else: which raw file was written and
>    which wiki page(s) were created or updated.
>
> Bound: step 2 is the one step that must not fail. If you cannot complete the
> INGEST or the commit (steps 3-4), still ensure the `raw/` file from step 2 is
> written to disk, and say so explicitly in your one confirmation line (e.g.
> "raw file written, INGEST incomplete: <reason>"). A half-ingested vault is
> recoverable; a lost raw file is not.

When the fork returns, relay only its confirmation line to me. Nothing else from
the fork belongs in this session.
