# Use and maintain the library

## Invoke directly

```text
Use frontend-artifact; style: technical-field-guide.
Build an explainer showing how streaming latency accumulates.
Technical but approachable; medium density; HTML/CSS with JavaScript only where useful.
```

```text
Use frontend-artifact; style: personal-software.
Build a compact searchable research list with tags. No marketing treatment.
```

```text
Use frontend-artifact. Recommend a language for this content and explain the fit.
```

The third request stops for confirmation. The first two approve the selected profile's visual defaults. Another workflow, including `vibe`, can pass the brief and selected language to this same entry point; it should not embed a copy of the profiles or ask for an already-confirmed choice.

A non-interactive run (`pi -p`, `omp -p`, a subagent) cannot answer the confirmation gate. Name the language in the request. If the run must proceed without one, say so in the request ("pick the language yourself and record it as inferred"); the build then records the selection as `[inferred]` rather than `[stated]`.

## What the build uses

- `references/skeletons/<language>.html`: the starting file. Tokens, fonts, structure and `REPLACE` slots. Every skeleton passes `audit.js` with zero FAIL and zero WARN at 390 and 1440 px when its fonts load.
- `references/fonts.md`: three validated pairings per language with the exact `<link>`. Each URL was fetched and returned 200 on the date recorded.
- `references/essentials.md`: the rules from the three design skills that apply to a standalone page, with the numbers the audit enforces.
- `references/anti-patterns.md`: generic tells, marked as measured or eye-checked.
- `references/audit.js`: the measurement script. `node audit.js <url-or-file> --width 390 --height 844 [--compact|--display]`.
- `references/critic-prompt.md`: the fresh-context reviewer's prompt and the fixed answer structure.
- `screenshots/<language>/notes.md`: measured relationships from the reference, and what not to borrow.

## Shared installation

The canonical source is `skills/frontend-artifact/` in agent-config. The installer links repo skills into `~/.agents/skills`, the single shared root that both OMP and Pi discover. Do not create a second copy in `~/.pi/agent/skills` or any harness-specific skills directory. After adding the skill, install from the durable canonical checkout, not an ephemeral worktree. Reload the harness session so its catalogue includes the new skill.

For a focused installation without changing model settings or agent configuration, run `./install.sh --skills-only=frontend-artifact,design-interface,design-visual-system,design-typography` from that checkout. The selected-skill mode validates all targets first and refuses real non-symlink destinations; it does not fetch externals, prune other links or merge configuration.

The skill intentionally depends on the adjacent `design-typography`, `design-interface` and `design-visual-system` skills in this repository, so install them together. Only this skill's own files live under `skills/frontend-artifact/`.

## Add a visual language

Create `references/languages/<kebab-case-name>.md` using an existing profile's sections. Describe the job it fits, concrete defaults, three visible distinctions, permitted variation, things to avoid, a reference link and review criteria. Keep shared typography and interaction rules in their existing owners. Add one row to the entry-point table so the profile is discoverable without loading the whole library.

A language is not complete without its skeleton and pairing. Add `references/skeletons/<name>.html` with a `:root` token block, one validated font link and the page structure with `REPLACE` slots; add three pairings under the language in `fonts.md`, each fetched and returning 200; add the audit flag to the entry-point table if the language is compact or display-led; and run `audit.js` on the skeleton at 390 and 1440 px until it reports zero FAIL. Write the `notes.md` for its reference with measured values (body size, measure, heading ratio, spacing, colour roles), not descriptions.

Test it on content also rendered in its closest neighbouring language. A new colour scheme alone is not a new language. Keep the task and data unchanged while comparing composition, hierarchy and interaction treatment.

## Add or replace a reference

Capture a useful viewport from an actual public page into `screenshots/<language>/`. Inspect the image before writing its companion `notes.md`; do not archive a consent dialog, loading skeleton or inaccessible page as the reference. Prefer a focused PNG and avoid full-page captures whose useful details become unreadably small.

Record source URL, page title, capture date, viewport dimensions, the screenshot's relative path and a table of measured relationships: body size and leading, measure in pixels and characters, title-to-body ratio, row or figure spacing, column positions and colour roles. Estimates from the capture are fine when marked approximate; adjectives are not. Separately name what should not transfer: brand assets, exact palette or fonts, claims, content and interactions unrelated to the new brief. The screenshot illustrates selected attributes; it does not authorise cloning the site or establish font licensing. Keep third-party reference imagery out of generated user artifacts unless separately authorised.

Start at one strong annotated reference per language. Add further examples only when they demonstrate a useful variation or clarify a boundary. After edits, run `./scripts/check.sh` from agent-config. Verify that every `screenshots/<language>/reference.png` referenced by `references/languages/*.md` exists and is readable through the installed skill path.
