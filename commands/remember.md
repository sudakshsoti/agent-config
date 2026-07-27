---
description: Save what we just decided or learned to the ~/dev/claude-memory vault and ingest it
argument-hint: [optional note on what to remember]
---

Save to the persistent memory vault at `~/dev/claude-memory`, then fold it in.

Plan item A wanted a `fork` subagent for this. That primitive does not exist in
this harness, so this is the documented fallback: **distil here, dispatch the
file work to a Sonnet `general-purpose` agent**. Distilling is reasoning rather
than tool calls, so it stays cheap in the parent; the twelve-turn
read-modify-write is the part that must not run here.

## Step 1: distil, in this session

From this conversation, plus this steer if it is non-empty: `$ARGUMENTS`.

Durable facts only: decisions with their reasoning, stated preferences, project
status changes, non-obvious configuration. Skip transient session state and
anything git history already records. If nothing durable happened, say so and
stop, without dispatching.

Write the distillation as prose you could hand to someone who was not here,
because that is exactly what happens next. A `general-purpose` agent does **not**
inherit this conversation, so anything you leave out is lost.

## Step 2: dispatch, exactly once

Make exactly one `Agent` tool call, `subagent_type: "general-purpose"`,
`model: "sonnet"`. Do not read the vault, run `date`, write, or commit anything
yourself. The 123-line ingest procedure must load in the subagent's context,
never in ours, so pass it by reference and never inline it.

Pass this prompt, with the distilled material substituted inline and nothing else
from this session:

> Save the following material to the memory vault at `~/dev/claude-memory`. You do
> not have the originating conversation; this is the whole of it:
>
> <distilled material>
>
> 1. Get the real timestamp with `date +%Y-%m-%d-%H%M` (never guess it) and write
>    the material as a new file in `~/dev/claude-memory/raw/` named
>    `YYYY-MM-DD-HHMM-short-slug.md`, slug in lowercase-kebab-case. `raw/` is
>    immutable source material: add this new file, never edit an existing one.
> 2. Run the INGEST operation on that file. Read `~/dev/claude-memory/CLAUDE.md`
>    and the full procedure in `~/dev/claude-memory/.claude/commands/ingest.md`
>    and follow them exactly: create or update the relevant `wiki/` pages, add
>    backlinks, update `wiki/index.md`, append an entry to `wiki/log.md`. Prefer
>    updating an existing page over creating a near-duplicate, and respect the
>    supersession rules for anything the new material contradicts.
> 3. Commit in `~/dev/claude-memory` following that repo's conventions.
> 4. Return **exactly one line** and nothing else: which raw file was written and
>    which wiki page(s) were created or updated.
>
> Bound: step 1 is the one step that must not fail. If you cannot complete the
> INGEST or the commit (steps 2-3), still ensure the `raw/` file from step 1 is
> written to disk, and say so explicitly in your one confirmation line (e.g.
> "raw file written, INGEST incomplete: <reason>"). A half-ingested vault is
> recoverable; a lost raw file is not.

## Step 3: relay

Relay only the subagent's confirmation line to me. Nothing else from it belongs in
this session.
