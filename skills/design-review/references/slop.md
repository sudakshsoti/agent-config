# Anti-slop list for visual work

The list of record. `frontend-craft`, `nightjar` and `brand-studio` each carried a
partial copy; this is the one that binds. Prose slop is `humanizer`'s territory and
is not duplicated here.

A negation list moves the model off one default and onto the next. So each entry
names the replacement move, not just the ban. Swapping `bg-purple-600` for
`bg-emerald-700` is not a fix, it is a different unexamined default.

---

## P1a — colour

| Tell | Replacement move |
|---|---|
| Purple-to-blue, blue-to-violet, purple-to-pink gradient | One flat brand colour derived from the subject, plus one accent. Name where the colour comes from. |
| Gradient on heading text (`bg-clip-text text-transparent`) | Weight, size or width carries the emphasis. |
| Untouched shadcn `zinc` / `slate` / `neutral` defaults | Override `--primary`, `--radius` and `--ring` before the first component. Test: could someone tell your Card from the shadcn docs Card in a screenshot? |
| Tailwind `blue-600` as the button colour | The project's `--primary`. If there isn't one, that's the first thing to define. |
| Pure `#000000` or `#ffffff` as a base surface | A neutral dark or light grey. Three surface steps, roughly 8 points apart. |
| A second accent hue | One accent. Status colours are not accents. |
| Status carried by hue alone | Every status pill carries a label or glyph. |

## P1b — type

| Tell | Replacement move |
|---|---|
| Inter, Roboto, Arial, Helvetica everywhere | A pairing chosen for the subject. State the reason in one line. |
| The tasteful defaults: Space Grotesk, Instrument Serif, Fraunces, Playfair Display | Same rule. These read as considered and are now as automatic as Inter. |
| A system stack shipped as the final answer | Acceptable only when stated as a constraint. Otherwise self-host an OFL variable face. |
| No display face at all, one family at four sizes | Two roles minimum: a characterful display used with restraint, a clean body face. |
| Proportional numerals in tables and metrics | `tnum`, always, wherever figures align. |
| Centred body text at paragraph length | Ranged left. Measure 60 to 75 characters. |

## P1c — surface and shape

| Tell | Replacement move |
|---|---|
| `rounded-2xl shadow-lg` on every surface | Containers earn an edge by fill step or hairline. Two radii in the system, not one applied everywhere. |
| Glassmorphism, neumorphism, glows | A hairline and a fill step. |
| Drop shadows where nothing is elevated | Shadow means elevation. Nothing else. |
| Rounded card with a coloured left border | The label says what it is. |
| Full-pill (999px) radii on cards or rows | Pills are for pills. |
| Zebra-striped tables, vertical table rules | Row hover and horizontal hairlines. |

## P1d — layout and content

| Tell | Replacement move |
|---|---|
| Centred hero plus three feature cards | Composition follows the content. See `interface-composition`. |
| Three-column icon-in-a-circle feature grid | Same. |
| Decorative numbered markers (01 / 02 / 03) | Number only where order carries information the reader needs. |
| Emoji as icons, bullets or status | A drawn icon set, or a word. |
| Decorative stat blocks with invented numbers | Real data or no block. |
| Three-item lists purely for rhythm | The number of items the content has. |
| Filler copy: seamlessly, effortlessly, powerful, beautiful, elevate, unlock, supercharge | Say what it does. See `ux-writing`. |
| `fade-in-up` on everything on scroll | One orchestrated moment, or none. Motion under 150ms, opacity and colour only, off under `prefers-reduced-motion`. |

---

## The question that outranks the table

Could a reader tell this from default LLM output at a glance?

A screen can pass every row above and still fail this, because passing a negation
list only proves you avoided the last defaults, not that you made a choice. The
positive test is the reference anchor: name the real product or printed artifact
whose design language this follows, and check the render against it.
