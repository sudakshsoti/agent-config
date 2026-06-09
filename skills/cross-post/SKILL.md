---
name: cross-post
description: |
  Repurpose a sudaksh.io writing post or project case study into LinkedIn and
  Medium drafts in Sudaksh's voice, with canonical backlinks to the original.
  Use when the user wants to cross-post, share on LinkedIn/Medium, "post this to
  LinkedIn", "make a LinkedIn version", "draft a Medium post", repurpose an essay
  or case study for social, or announce a new piece of writing or project.
  Drafts only — never publishes. Triggers on a slug, a file path under
  app/writing/_posts or app/projects, or a description of the piece.
---

# Cross-post

Turn one piece of writing or one project case study on sudaksh.io into
ready-to-paste **LinkedIn** and **Medium** drafts — adapted per platform, in
Sudaksh's voice, always linking back to the canonical original. This skill
**drafts only**; the user copies and pastes. Never attempt to publish.

## 1. Resolve the source

The user names a piece by slug, path, title, or topic. Resolve it to one file:

- **Writing** → `app/writing/_posts/<slug>.mdx` (or `.md`). Canonical URL:
  `https://sudaksh.io/writing/<slug>`
- **Project** → `app/projects/<slug>/page.mdx`. Canonical URL:
  `https://sudaksh.io/projects/<slug>`

If the reference is ambiguous, `ls app/writing/_posts/` and `ls app/projects/`
and ask which one. If it's a `draft: true` writing post, warn that the canonical
page isn't live in production yet — the backlink will 404 until it ships.

Read the file. Strip YAML frontmatter and JSX component tags (`<Meta>`, `<Lead>`,
`<BucketTable>`, `<RepoLink>`, etc.) — keep the prose they wrap. Pull `title` and
`description` from frontmatter; for projects the `<Lead>` is the de-facto summary.

## 2. Hold the voice

Match the source, don't market over it. The house style (see
`app/writing/_posts/` and the `prose-editor` skill):

- **Concrete before abstract.** One observed detail carries the point — "her
  bottom settles on the floor like a leaf," not "babies are remarkable."
- **No hype, no LinkedIn-broetry.** No "🚀", no "I'm thrilled to announce", no
  one-line-per-paragraph stacking, no "Here's the thing:", no engagement-bait
  questions tacked on the end.
- **Plain, exact sentences.** Em-dashes and semicolons are fine — the source
  uses them. Don't sand the prose into corporate cadence.
- **Earned authority.** State what's true and why. The Kohra piece says "HSL
  lies" and then proves it — confidence from precision, not adjectives.
- **First person, unhurried.** It's a person thinking out loud, not a brand.

When unsure, lift the strongest real sentence from the source rather than
inventing a punchier one.

## 3. Draft per platform

Cross-posting full text competes with the canonical page for search ranking.
Protect the original — the link back is the point, not the repost.

### LinkedIn (default: feed teaser)

A native feed post. Goal is to make someone click through to sudaksh.io, not to
reproduce the essay.

- **Hook** (first 1–2 lines, before the "…more" fold): the single most concrete
  or surprising line. No preamble.
- **Body** (~3–6 short paragraphs): the gist — the observation or the central
  idea of the case study. Enough to be worth reading on its own; not the whole
  thing.
- **Close**: one plain line pointing to the full piece + the canonical URL.
  LinkedIn ranks posts with links lower, so optionally note: "link in first
  comment" as an alternative, and supply that comment text.
- **No hashtag spam.** At most 2–3, lowercase, genuinely topical, or none.

If the user explicitly wants the **full** piece on LinkedIn, draft a LinkedIn
**Article** instead (long-form) and still open with a line noting it was first
published on sudaksh.io, linking the canonical.

### Medium (default: full repost, canonical-safe)

Medium handles canonical correctly when you use **Import a story**
(`https://medium.com/p/import`) pointed at the canonical URL — it sets
`rel=canonical` back to sudaksh.io automatically, so there's no duplicate-content
penalty. Recommend that path first.

Provide, ready to paste if importing isn't used:

- **Title**: the source title (drop the "— Case Study" suffix for projects if it
  reads oddly on Medium; keep it if it's informative).
- **Subtitle**: one line — the `description` frontmatter, or a distilled premise.
- **Body**: the full prose, lightly adapted for Medium (expand any reference that
  depended on a stripped JSX artifact — e.g. describe what the bucket table
  showed rather than linking a component). Keep links.
- **Canonical footer**: a first line or closing italic note —
  *"Originally published at [sudaksh.io](<canonical-url>)."* — for when the post
  is pasted rather than imported.

## 4. Output

Write the drafts to `.claude/cross-post-drafts/<slug>.md` (gitignored; create the
folder if missing) with clearly separated `## LinkedIn` and `## Medium` sections,
and also show them inline in the reply so the user can copy immediately.

End with: the canonical URL, a one-line reminder of the recommended publish path
per platform (LinkedIn: paste as feed post / link in first comment; Medium: use
Import a story with the canonical URL), and an offer to adjust tone, length, or
hook.

## Boundaries

- **Drafts only.** No API calls, no auto-publishing, no third-party publishers.
  If the user wants real automated posting, that's a separate decision (Medium
  API token; LinkedIn's gated API or a broker like Publora) — surface it, don't
  assume it.
- Don't invent facts, metrics, or quotes not in the source.
- Don't violate the site's voice to chase engagement.
