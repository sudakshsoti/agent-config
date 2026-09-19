# references: visual system

Concrete values and recipes that support `../SKILL.md`: surface and icon mechanics, colour ramp and token systems, layout measurements, and motion values that override or extend the vendored `animate` and `emil-design-eng` skills.

- `surfaces-and-icons.md`: concentric radius, shadow-as-border, image outlines, optical alignment, icon stroke and sizing, state colour, RTL icon flipping.
- `colour-systems.md`: ramp formation, Radix versus Tailwind step models, token grammar and tiering, APCA and WCAG thresholds, brand pinning, per-hue vividness, dark mode switching, palette audits.
- `layout-mechanics.md`: group and control spacing, logical properties, container queries, peeking scrollers, pseudo-localisation.
- `motion-values.md`: numeric overrides and additions to the vendored motion skills, since those files cannot be edited durably here.

Every value here is a default to apply, not a law. A project's own tokens, density scale, or motion system always win; reuse them before reaching for a number in this directory.

Naming: kebab-case, one topic per file.
