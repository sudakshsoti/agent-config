# Personal software

## Fit and job

Use for small utilities, research artifacts, notes and internal reference tools that should feel immediately useful. The character comes from direct access to content, simple structure and minimal chrome. Compared with precision software, this direction defaults to fewer structural layers and less workspace framing. Small does not mean incomplete or inaccessible.

These defaults authorise visual choices within the requested content and behaviour; they do not authorise new features or changes to the artifact's job.

## Defaults

- Composition: expose the primary action, list or reference content immediately. Use the shortest navigation path that fits the supplied content. Keep supporting controls beside the task they serve instead of creating a separate application shell.
- Density: use compact rows and modest spacing so useful information stays in view. Leave enough room for readable content, real labels and comfortable input. State a useful-unit target appropriate to the repeated task.
- Typography roles: use a small, coherent hierarchy for orientation, content, links and metadata. A clear UI or reading face should support quick scanning; reserve specialised type treatments for content that needs them. Distinguish links and selected content reliably.
- Palette roles: use a simple neutral base and one intentional accent for navigation, action or selection. Keep semantic feedback distinct. Choose a light or dark treatment for the actual use conditions rather than a reference brand.
- Grouping and surfaces: prefer lists, links, tables and open sections. Add a container only when it separates a meaningful group or an overlapping control. Avoid nested panels around straightforward content.
- Interaction: make requested actions direct, with feedback close to the change. Preserve familiar browser behaviour, keyboard access and clear focus. Add helpers only when requested or necessary for the existing function, not to make a small tool resemble a product suite.

## Three distinguishing features

1. Useful content or the primary action appears before explanatory or decorative framing.
2. Most information lives in direct lists, links, rows or tables with few surface layers.
3. Navigation and controls stay proportionate to the small task instead of introducing a full workspace shell.

## Permitted variation

The artifact may be a single page or a small set of views according to its requirements. Lists, tables, notes and compact forms can share the language. Typeface, accent and small details may carry personal character while preserving direct use. A real need for comparison, error recovery or explanation takes precedence over reducing the visible interface.

## Avoid

- A welcome hero, permanent onboarding panel or feature-card introduction.
- Sidebars, dashboards, tabs or account-like furniture added without a requested need.
- Mistaking minimal chrome for missing labels, inaccessible controls or absent feedback.
- Styling a technical subject as a terminal or filling empty space with decorative widgets.

## Starter

Copy [the skeleton](../skeletons/personal-software.html) and fill its `REPLACE` slots. Its `:root` block holds this language's starting tokens; its font link is Geist with Geist Mono, the first pairing under this language in [fonts.md](../fonts.md). Change a token only with a reason stated in the report. Run `audit.js` with `--compact`.

## Reference notes

Inspect [the selected reference and its annotations](../../screenshots/personal-software/notes.md). Borrow the recorded relationships, not the reference's brand identity or exact values.

## Visible review criteria

- At the narrowest target viewport, the first action or complete useful entry is available within the task's viewport target.
- The user can identify the primary action and navigate the content without reading an introduction.
- Removing any panel or navigation layer would remove a real grouping or task function; otherwise simplify it.
- Long content, empty results and feedback remain understandable without adding a second visual system.
