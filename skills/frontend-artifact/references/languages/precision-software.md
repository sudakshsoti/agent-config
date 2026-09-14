# Precision software

## Fit and job

Use for tools, dashboards, comparison interfaces and system views where people repeatedly scan information and act on it. The character comes from precise alignment, compact hierarchy and clear state. Dark mode is optional. Compared with personal software, this direction supports more structured groups, controls and surface layers when the existing task needs them.

These defaults authorise visual choices within the requested content and behaviour; they do not authorise new features or changes to the artifact's job.

## Defaults

- Composition: put the working region first; align labels, values and controls on consistent columns. Place secondary context beside or beneath its subject rather than in a separate promotional opening.
- Density: use compact rows and short vertical gaps for scanning. Set a useful-unit viewport target from the real content and target size before implementation; do not compress text or touch targets to meet it.
- Typography roles: select a UI sans with distinguishable small forms. Keep orientation, content and metadata close in scale, separating them through weight and placement. Use tabular figures for aligned quantities; reserve monospace for technical strings.
- Palette roles: use low-chroma neutrals with one primary accent for the main action or selected state. Preserve semantic status colours. Differentiate adjacent surfaces only enough to reveal grouping or depth.
- Grouping and surfaces: prefer rows, section spacing and thin rules. A bordered or elevated surface must represent an independent object, a bounded control region or an overlapping layer. Keep corner treatment consistent with those roles.
- Interaction: show selection, focus, loading and feedback where the action occurs. Use brief state transitions when they improve continuity; do not animate ordinary reading content into view.

## Three distinguishing features

1. Related values and controls share visible alignment across multiple rows.
2. The type hierarchy remains compact even when the interface has several information levels.
3. Surface differences explain grouping, selection or depth rather than decorating every item.

## Permitted variation

Light and dark treatments are equally valid. Choose the actual family, neutral temperature, accent and spacing from the subject, available fonts and project tokens. Add surface layers only when the requested task requires them; a simple page need not become a workspace. Charts retain data meaning and legibility even when this requires more than one colour.

## Avoid

- A centred headline, oversized title or feature-card opening that delays use.
- Making everything a pill or floating panel to imply polish.
- Tiny low-contrast metadata, ambiguous icons or hidden labels to force density.
- Copying Linear's branding, shell or dark palette as the definition of precision.

## Starter

Copy [the skeleton](../skeletons/precision-software.html) and fill its `REPLACE` slots. Its `:root` block holds this language's starting tokens; its font link is IBM Plex Sans with IBM Plex Mono, the first pairing under this language in [fonts.md](../fonts.md). Change a token only with a reason stated in the report. Run `audit.js` with `--compact`.

## Reference notes

Inspect [the selected reference and its annotations](../../screenshots/precision-software/notes.md). The primary image is a records table with the workspace sidebar; companion captures show a board of cards, a chart with a configuration panel, and a dialog over the app. Borrow the recorded relationships, not the reference's brand identity or exact values.

## Visible review criteria

- At the narrowest target viewport, the primary working region and at least one complete useful unit are visible according to the task's viewport target.
- Repeated values and controls remain aligned, including with long labels and empty values.
- Every border, panel and accent has an identifiable grouping, state or action role.
- Removing decorative effects would leave a coherent, usable hierarchy.
