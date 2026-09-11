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

The third request stops for confirmation. The first two approve the selected profile's visual defaults. Another workflow, including Vibe, can pass the brief and selected language to this same entry point; it should not embed a copy of the profiles or ask for an already-confirmed choice.

## Shared installation

The canonical source is `skills/frontend-artifact/` in agent-config. The existing installer links repo skills into `~/.agents/skills`, which Codex and Pi both discover, and into the Claude skill root. Do not create a second copy in `~/.codex/skills` or a Pi-specific copy. After adding the skill, install from the durable canonical checkout, not an ephemeral worktree. Reload the harness session so its catalogue includes the new skill.

For a focused installation without changing model settings or agent configuration, run `./install.sh --skills-only=frontend-artifact,design-interface,design-visual-system,design-typography` from that checkout. The selected-skill mode validates all targets first and refuses real non-symlink destinations; it does not fetch plugins, prune other links or merge configuration.

The skill intentionally depends on the adjacent `design-typography`, `design-interface` and `design-visual-system` skills in this repository. A ZIP contains this skill's own files only; users of an isolated upload must also provide those companions. It is not a standalone replacement for them.

## Add a visual language

Create `references/languages/<kebab-case-name>.md` using an existing profile's sections. Describe the job it fits, concrete defaults, three visible distinctions, permitted variation, things to avoid, a reference link and review criteria. Keep shared typography and interaction rules in their existing owners. Add one row to the entry-point table so the profile is discoverable without loading the whole library.

Test it on content also rendered in its closest neighbouring language. A new colour scheme alone is not a new language. Keep the task and data unchanged while comparing composition, hierarchy and interaction treatment.

## Add or replace a reference

Capture a useful viewport from an actual public page into `screenshots/<language>/`. Inspect the image before writing its companion `notes.md`; do not archive a consent dialog, loading skeleton or inaccessible page as the reference. Prefer a focused PNG and avoid full-page captures whose useful details become unreadably small.

Record source URL, page title, capture date, viewport dimensions, the screenshot's relative path and the concrete visible characteristics worth borrowing. Separately name what should not transfer: brand assets, exact palette or fonts, claims, content and interactions unrelated to the new brief. The screenshot illustrates selected attributes; it does not authorise cloning the site or establish font licensing. Keep third-party reference imagery out of generated user artifacts unless separately authorised.

Start at one strong annotated reference per language. Add further examples only when they demonstrate a useful variation or clarify a boundary. After edits, run `scripts/build-zip.sh frontend-artifact` from agent-config and the repository checks. Verify that images and notes are present in the package and readable through the installed skill path.
