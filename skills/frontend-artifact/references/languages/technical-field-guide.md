# Technical field guide

## Fit and job

Use for mechanism explanations, architecture walkthroughs and technical reference material. The page should make a system understandable through sections, diagrams and annotations. Compared with visual essay, the structure helps readers inspect a mechanism or revisit a section; it need not build towards a persuasive conclusion. Classify a sequential tutorial as content/editorial and a lookup manual as reference/documentation before choosing its opening.

These defaults authorise visual choices within the requested content and behaviour; they do not authorise new features or changes to the artifact's job.

## Defaults

- Composition: organise around the actual mechanism, stages or questions. Keep each diagram with the text that explains it. Use section headings and descriptive captions so a reader can locate an explanation again.
- Density: balance readable prose with sufficiently detailed diagrams. Keep related labels and annotations close; do not add generous gaps between steps that must be compared.
- Typography roles: provide distinct roles for section headings, explanatory text, figure labels, captions and technical identifiers. Choose the reading face for sustained comprehension. Monospace belongs to code, commands, identifiers and comparable technical data, not every heading or label.
- Palette roles: use a restrained neutral base. Give colour a stable explanatory role, such as distinguishing a path, component or stage, and repeat that meaning in diagrams and text. Do not encode distinctions through colour alone.
- Grouping and surfaces: use section spacing, rules, indentation and diagram boundaries before cards. A callout earns containment when it separates a warning, definition or essential qualification from the main explanation.
- Interaction: prefer understandable static diagrams. Add controls only when the requested explanation benefits from changing a variable, revealing a stage or comparing states; keep the relationship between the control and its result explicit.

## Three distinguishing features

1. Sections correspond to real parts, stages or questions in the mechanism.
2. Diagrams and their explanations can be read together without searching elsewhere on the page.
3. Captions, labels and cross-references let readers revisit a specific explanation independently.

## Permitted variation

The guide may be a continuous document or a browsable reference, according to its job. Diagram style can follow the subject: flow, cross-section, sequence, annotated object or another justified form. Choose light or dark rendering for the actual reading conditions. A serif or sans reading face is acceptable when proofed against the content and available licence.

## Avoid

- Turning a technical subject into a fake terminal or an all-monospace page.
- A marketing introduction that delays the mechanism or lookup content.
- Numbered stages that imply an order the system does not have.
- Decorative diagrams, unlabeled arrows or callout boxes that repeat ordinary prose.

## Starter

Copy [the skeleton](../skeletons/technical-field-guide.html) and fill its `REPLACE` slots. Its `:root` block holds this language's starting tokens; its font link is Source Serif 4 with IBM Plex Mono, the first pairing under this language in [fonts.md](../fonts.md). Change a token only with a reason stated in the report. Run `audit.js` with no flag.

## Reference notes

Inspect [the selected reference and its annotations](../../screenshots/technical-field-guide/notes.md). The primary image is a section with a figure and caption; two companion crops show an interactive figure with its controls and a chapter opening with centred illustrations. Borrow the recorded relationships, not the reference's brand identity or exact values.

## Visible review criteria

- A reader can identify the mechanism and follow a complete explanation from text to diagram and back.
- Diagram labels, units and captions remain readable at the narrowest target viewport; any necessary diagram scrolling is contained and evident.
- Repeated graphic marks and colours retain the same meaning across sections.
- A lookup guide exposes useful reference content immediately; a sequential explanation opens with the concept needed to understand its first stage.
