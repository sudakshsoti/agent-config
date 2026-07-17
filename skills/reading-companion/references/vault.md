# Vault map — paths, schema, locations

Ground truth for where things live and what they're called. Verified against the
live vault on 2026-06-07. If a path stops resolving, re-check rather than guess.

## Paths

| Thing                | Path                                                                                   |
| -------------------- | -------------------------------------------------------------------------------------- |
| Vault root           | `/Users/sudakshsoti/dev/vault`                                                         |
| Book notes           | `02 Areas/Reading/Books/<Title> - <Author>.md`                                         |
| The database (Bases) | `02 Areas/Reading/Library.base` (views: To Read · Reading · Read · Shelf · All)        |
| Reading hub          | `02 Areas/Reading/Reading Hub.md`                                                      |
| Daily notes          | `Journal/YYYY-MM-DD.md` (created by Templater folder-template `99 Templates/Daily.md`) |
| Writing seeds        | `03 Resources/Seeds/<slug>.md` (one note per seed)                                     |
| Book note template   | `99 Templates/Book Note.md`                                                            |

Note: the core Daily Notes plugin config points at `00 Inbox`, but real daily
notes are written to `Journal/` via Templater. Use `Journal/`.

## Book-note frontmatter schema

Read from real notes, not assumed. Property names are exact.

```yaml
title: # string
aliases: # list — includes bare title and any Devanagari title
type: book-note # constant; the Base filters on this
status: # to-read | reading | read | abandoned   ← lifecycle
priority: # number, 1 = next up; tiebreaker only
author: # LIST (e.g. [Claire Keegan])
published: # year
publisher: # string
pages: # integer  ← length signal for PICK
isbn: # string
cover: # image URL
categories: # LIST — literary FORM: Fiction, Nonfiction, Play, Satire,
  #   Memoir, Diary, Travel Memoir, Short Stories, Classics…
  #   (this is how fiction/non-fiction is encoded — no boolean)
language: # English | Hindi   ← language signal for PICK
rating: # 1–5, blank until read
started: # YYYY-MM-DD, set when status→reading
finished: # YYYY-MM-DD, set when status→read
position: # current spot: "p.84" or "60%"  ← ADD if missing (see below)
list: # freeform shelf, e.g. "Saunders picks", "2026 favourites"
source: # optional wikilink to where the book came from
created: # YYYY-MM-DD
updated: # YYYY-MM-DD  ← bump on every edit
tags: # includes status/<state> mirror — see below
```

### `position` is the one field you may add

The schema didn't originally carry a current-position field. TRACK needs one.
Add `position:` to a book's frontmatter the first time you record progress.
Place it near `started`/`finished`. Format: `position: "p.84"` or
`position: "60%"`. Clear it (or leave it) on finish.

### Status values (exact)

- `to-read` — on the shelf, unstarted
- `reading` — in progress (stamp `started`)
- `read` — finished (stamp `finished`) — **this is the "done" value, not
  "finished"**; the Base and hub filter on `status == "read"`
- `abandoned` — set aside, no guilt

### Lifecycle tags mirror status

Notes carry a `status/*` tag that tracks `status`:

- `status: to-read` ↔ tag `status/to-read`
- `status: reading` ↔ tag `status/active`
- `status: read` ↔ tag `status/completed`

When you change `status`, update this tag too if it's present.

### Body scaffold (headings in book notes)

`# Title` → italic hook line → `## Why I'm reading / how I found it` →
`## Brief` → `## Key ideas` → `## Key quotes/highlights` → `## Chapter notes` →
`## My take` → `## Related`.

- Quotes/highlights → under `## Key quotes/highlights` (create if missing).
- His reaction → as a sub-bullet beneath the quote.
- A long disagreement (the 200-word push) → under `## My take` or its own note
  linked back.

## Daily-note reading log

Append to today's `Journal/YYYY-MM-DD.md`. Existing sections: `## Ira`,
`## Work`, `## Body`, `## One thing noticed`, `## Tasks`. Add a `## Reading`
section (create it the first time that day), one line per session:

```markdown
## Reading

- 📖 Foster — p.40/112 · "the kind of quiet that holds its breath"
```

Just the line. No counts, no streak markers, no time-tracked totals.

If today's daily note doesn't exist yet, it's fine to create it from
`99 Templates/Daily.md`'s shape (or just write the `## Reading` line into a new
`Journal/YYYY-MM-DD.md`) — but don't block reading on note-keeping.

## Seed note

One atomic note per seed in `03 Resources/Seeds/`. Use
`assets/seed-template.md`. Filename = the seed, kebab-cased. Format of the seed
line itself: **`[concrete subject] as [angled lens]`**. Always set `source:` to
the book wikilink. Never gloss Hindi/Urdu.
