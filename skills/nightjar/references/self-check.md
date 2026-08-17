# NIGHTJAR — rejection list and self-check

§11 and §12 of the house style. Walk §12 line by line before returning an
artifact. The system itself is in `spec.md`.

---

## 11. Rejection list

Do not produce, under any framing:

- Pure `#000000` or pure `#ffffff` as a base surface
- Any multi-hue gradient background; any purple→pink or blue→violet wash
- Inter, Roboto, Arial, Helvetica, Fraunces
- Emoji as icons, bullets, or status
- Rounded card with a coloured left border
- Drop shadows, glows, glassmorphism, neumorphism
- Full-pill (`999px`) radii on cards or rows
- Zebra-striped tables; vertical table rules
- Three-column icon-in-a-circle feature grids
- Decorative stat blocks with invented numbers
- Centred body text at paragraph length
- More than one primary button in a view
- A second accent hue

---

## 12. Self-check before returning an artifact

### Every artifact

1. Is the base a neutral dark grey, not black? Are there exactly three surface
   steps? State variations of a step do not count as a fourth.
2. Does every container earn its edge by fill step or hairline, with no shadow?
3. Is every accent use on the permitted list? A document gets one at most. An
   interactive view gets selection, focus, the active control, the primary chart
   series, and link hover — nothing beyond those.
4. Are sans and mono strictly divided by content type?
5. Are all numerals in tables and metrics tabular?
6. Does each text tier clear its minimum against the *lightest* surface it sits
   on, not just against `bg`?
7. Are there only two radii and one 4px-based spacing scale?
8. Is the density from row count rather than from tightness?
9. Does every status pill carry a label or glyph, not hue alone?
10. Did anything from §11 appear?

### Interactive artifacts only

11. Are hover, pressed, selected, focus-visible, disabled, loading, and error
    all defined, and do they resolve by the §2 precedence order?
12. Do overlays separate by scrim and hairline, layered against the context that
    opened them rather than a fixed z-index table?
13. Is motion inside the ~150ms ceiling, opacity and colour only, and off under
    `prefers-reduced-motion`?
14. Is every colour referenced through a token name, with no inlined hex?

### Last question, always

Could a reader tell this from default LLM output at a glance? If not, the
restraint has not been applied hard enough.
