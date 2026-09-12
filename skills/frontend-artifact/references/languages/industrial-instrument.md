# Industrial instrument

## Fit and job

Use for technical demonstrations, model comparisons and audio, networking or hardware-related interfaces where inputs, settings and outputs have explicit relationships. The character comes from useful labelling, functional modules and deliberate controls. Compared with Swiss graphic, geometry describes operation and measurement rather than primarily composing a conceptual message.

These defaults authorise visual choices within the requested content and behaviour; they do not authorise new features or changes to the artifact's job.

## Defaults

- Composition: place controls next to the values, diagrams or outputs they affect. Organise modules around actual functions or stages, keeping the path from input to result legible.
- Density: keep operational groups compact enough to compare while separating unrelated functions. Give adjustable controls adequate target space and values enough room for their full units and precision.
- Typography roles: distinguish function labels, setting values, units, status and explanatory text. Use aligned figures where comparison requires them. Monospace can serve identifiers, logs or technical values; ordinary labels and instructions need not look like terminal output.
- Palette roles: begin with a restrained neutral base. Use colour for active operation, selection, warning or a meaningful signal path. Keep decorative colour from competing with status, and pair colour with another visible cue.
- Grouping and surfaces: use clear module boundaries when they describe functional independence. Rules, panels and corner treatments should explain the operating structure. Measurement marks or indexing appear only when they represent a real scale, sequence or reference.
- Interaction: make control-to-output relationships immediate and visible. Provide clear feedback and reset behaviour where requested. Prefer familiar accessible controls; a physical-control analogy must not reduce keyboard access or require precise dragging.

## Three distinguishing features

1. Inputs, controls and their outputs are visibly adjacent or connected.
2. Functional modules expose their labels, current values and relevant units.
3. Indexing, status marks and calibration cues encode actual operation or measurement.

## Permitted variation

The language can be light or dark, restrained or use a stronger functional accent. Module boundaries may be flat or subtly dimensional according to the interface's actual layers. Use the subject's real technical conventions where they help the audience; omit hardware motifs when they do not explain anything.

## Avoid

- Fake hacker terminals, decorative serial numbers and meaningless calibration ticks.
- Knobs, switches or LEDs introduced solely to imitate physical equipment.
- Hiding labels behind icons or omitting units to make a panel look sparse.
- Decorative warning colours, unreadable dim values or elaborate textures that obscure state.

## Starter

Copy [the skeleton](../skeletons/industrial-instrument.html) and fill its `REPLACE` slots. Its `:root` block holds this language's starting tokens; its font link is Chivo with Chivo Mono, the first pairing under this language in [fonts.md](../fonts.md). Change a token only with a reason stated in the report. Run `audit.js` with `--compact`.

## Reference notes

Inspect [the selected reference and its annotations](../../screenshots/industrial-instrument/notes.md). Borrow the recorded relationships, not the reference's brand identity or exact values.

## Visible review criteria

- For every control, the affected output or setting is visually evident and reachable without searching another section.
- Values show the units and precision needed for interpretation, including extremes and unavailable states.
- Every module boundary, indicator and measurement mark has a real function.
- Requested controls remain usable with keyboard, touch and reduced motion; physical styling never supplies the only state cue.
