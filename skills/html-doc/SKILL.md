---
name: html-doc
description: |
  Turn notes, briefs, reports, plans, explanations and handoffs into one polished,
  portable, self-contained HTML file that opens straight in a browser — an alternative
  to handing back a .md. Use when the user asks for "a report", "write this up", "a
  brief", "make this readable", "as HTML instead of markdown", or types /html-doc.
  Documents only: for UI, app or landing-page work use frontend-design or prototype;
  for a repo guide use orient; for a session handoff use handoff. It writes a local
  file and never publishes to claude.ai — that is the Artifact tool.
user-invocable: true
---

# HTML Doc

It does ONE thing: take content that already exists (a thread, a markdown file, a
set of notes) and emit one self-contained `.html` document that opens in a browser,
prints cleanly and reads on a phone. It does not design interfaces (`frontend-design`,
`prototype`), it does not explain a repo (`orient`), it does not write a session
handoff (`handoff`), and it does not publish anything to claude.ai (the Artifact
tool does that).

The output is a document, not a page. Every invocation must produce something that
looks like every other document this skill has produced. That determinism is the
whole product.

## Operating Posture

The failure this skill exists to prevent is treating a document request as a web-design
request: inventing a palette, a hero, a card grid and a gradient, and shipping a
different-looking artifact every time. You are not deciding how documents look. That
was decided once, in [assets/base.html](assets/base.html), and your job is to fill it.

Two files are load-bearing and you read them at the right moment, not eagerly:

- [references/anti-patterns.md](references/anti-patterns.md): read it **before making
  any visual decision at all**. It is the banned list with the reason for each ban,
  and most visual instincts you have here are on it.
- [references/themes.md](references/themes.md): read it **only when the theme is not
  `manuscript`**. `manuscript` already ships active in `base.html`, so the default
  path never opens this file.

A theme is one `:root` swap and nothing else. Every rule below `:root` reads a token,
including the type scale (`--text-base`, `--text-h1`, `--text-h2`, `--text-h3`). If a
theme seems to need an edit below `:root`, that is a bug in `base.html` to report, not
something to patch per document.

## Hard Rules

1. **One file, zero external requests.** No `<script src>`, no `<link rel=stylesheet>`,
   no webfonts, no remote images, no `@import url()`. System font stacks only. The file
   has to work offline, from a USB stick, and in five years.
2. **Zero JavaScript by default.** `<details>` covers collapsing and `position: sticky`
   covers the TOC, so nothing standard needs it. If the user explicitly asks for
   interaction: 20 lines inline, maximum, and no libraries.
3. **Never rewrite the source.** Reorganise into headings, tables and callouts freely;
   preserve code, links, citations, dates, numbers and names byte-for-byte. Never
   summarise content to make it fit a layout; the layout loses that argument.
4. **Copy the template; do not author CSS.** Read `assets/base.html`, keep its `<style>`
   block, delete the rules for primitives you did not use. Adding a selector means the
   content needs a shape the vocabulary lacks, so say that in the hand-off instead of
   inventing one. `check.py` WARNs on any selector absent from `base.html`.
5. **Visual complexity follows informational complexity.** A 400-word note gets a header
   and prose, nothing else. TOC only past roughly 6 sections. Stat blocks only for real
   measured numbers. A chart only when there are 10 data points or fewer and a table
   genuinely serves them worse.
6. **Never invent data.** No placeholder metrics, no illustrative sparkline, no lorem,
   no rounded-up figure that reads better. If a number is not in the source, it is not
   in the document.
7. **Update in place.** If the target file already exists, `Edit` it. Regenerating from
   scratch silently discards the user's own edits to it.
8. **Diagrams are inline SVG or nothing.** No mermaid, because it does not render in a
   bare browser, which is the only environment this file is promised to work in. No
   raster images unless the user supplies a path and accepts base64.

## Brief

Every parameter is optional and defaulted. An unparameterised invocation must just work.

| Param | Values | Default |
| --- | --- | --- |
| `pattern` | `reading` \| `brief` \| `reference` \| `report` | inferred from content |
| `density` | `comfortable` \| `compact` | from pattern |
| `theme` | `manuscript` \| `console` \| `report` | bound to pattern |
| `accent` | any hex | from theme |
| `nav` | `none` \| `toc` | `toc` past ~6 sections |
| `output` | path | `./<slug>.html` |

The four patterns are presets over three axes, not four separate designs. This table is
closed: there is no fifth pattern, and inventing one is a Hard Rule 4 violation:

| Pattern | measure | leading | density | default theme |
| --- | --- | --- | --- | --- |
| `reading` | 68ch | 1.7 | comfortable | manuscript |
| `brief` | 72ch | 1.6 | comfortable | report |
| `reference` | 1080px | 1.5 | compact | console |
| `report` | 900px | 1.6 | comfortable | report |

Inference: continuous prose and essays are `reading`; a decision or recommendation for
someone else to act on is `brief`; lookup material, checklists and command references
are `reference`; findings with numbers in them are `report`.

## Workflow

### Phase 0 — Brief

Parse the parameters, fill the defaults, infer the pattern from the content. State
pattern, theme and output path in **one line**, then proceed. Ask a question only if
the output path is genuinely ambiguous; every other gap has a default.

**Completion criterion:** one line printed, no questions asked.

### Phase 1 — Structure

Outline the headings and decide which primitives each section needs before writing any
HTML. The vocabulary is closed at 15: `.doc-header` + `.doc-meta`, `.lead`, `nav.toc`,
`.summary`, `aside.callout` (`--note` / `--warn` / `--rec`), `dl.kv`, `.table-wrap >
table`, `pre > code`, `blockquote`, `ol.steps`, `.stat-row > .stat`, `.bar`,
`details.appendix`, `footer > ol.sources`, footnotes (`sup` → `#fn-N`).

Hard Rule 3 binds here: this is a reorganisation pass, not an editing pass.

**Completion criterion:** every section mapped to primitives from that list, no
primitive chosen that the content does not actually need.

### Phase 2 — Build

Read `assets/base.html`. Write the output file with its `<style>` block intact, minus
the rules for primitives you did not use. Swap the `:root` block only if the theme is
not `manuscript`, taking both the light and dark blocks from `references/themes.md`.

**Completion criterion:** the file exists, contains no selector that is not in
`base.html`, and still carries the `@media print` and `prefers-reduced-motion` blocks.

### Phase 3 — Check

```bash
CHECK="$(ls ~/.claude/skills/html-doc/scripts/check.py \
            ~/.agents/skills/html-doc/scripts/check.py 2>/dev/null | head -1)"
python3 "$CHECK" <output.html>
```

Fix and re-run, **two rounds maximum**. On a third failure, ship the file and name the
failing check in the hand-off. A silent skip is the one failure nobody can see.

**Completion criterion:** exit 0, or exit 1 with the failing check named out loud.

### Phase 4 — Hand off

Print the absolute path and the `open <path>` command. Say which pattern and theme were
used and anything Hard Rule 4 forced you to leave out. Then stop.

**Completion criterion:** path printed, nothing committed.

## Anti-scope

- **Never commit, stage or push.** The file is handed to the user; `git add` is theirs.
- **No content generation.** If the source does not say it, the document does not say
  it. This skill formats; it does not research or draft.
- **No multi-file output.** No sidecar CSS, no assets directory, no index of documents.
  One invocation, one `.html` file.
- **No publishing.** Uploading to claude.ai is the Artifact tool. A document that needs
  to be a shareable URL is a different request.
- Landing pages, dashboards, app UI → `frontend-design` or `prototype`. A guide to a
  repo → `orient`. A session handoff → `handoff`.

## Invocation Variants

| Invocation | Behavior |
| --- | --- |
| bare | Turn the current thread's material into a document, defaults throughout |
| `<path.md>` | Convert that file; output beside it as `<slug>.html` |
| `pattern=X theme=Y` | Same run with those presets pinned, defaults for the rest |
| `output=<path>` | Write there; if the file exists, `Edit` it (Hard Rule 7) |
| `check <path>` | Phase 3 only against an existing file, build nothing |

## Tone

The document's voice is the source's voice. Do not add an introduction the author did
not write, a conclusion that restates the body, or section blurbs that pad a table of
contents. Headings are labels, not sentences.

In the hand-off, be plain: what was produced, where, and what you could not represent
in the vocabulary. Naming a gap is more useful than a document that quietly dropped it.
