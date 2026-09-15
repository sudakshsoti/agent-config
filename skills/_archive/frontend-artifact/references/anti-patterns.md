# Anti-patterns

These are the habits that make a generated page read as generated. Each one is either measured by `audit.js` (marked **audit**) or checked by eye in the critic pass (marked **eye**). Treat every hit as a defect to fix, not a style choice to defend.

## Type

- **audit** A system stack, or a family that failed to load, as the primary face.
- **audit** Inter, Roboto, Space Grotesk, Instrument Serif, Fraunces or Playfair Display.
- **audit** More than two families, or a third that is not a mono used for code or values.
- **audit** Negative letter-spacing on anything under 24px.
- **audit** A page heading more than 3.2 times the body size on a reading page, or more than 1.6 times on a utility. Swiss display pages may go to 7 with `--display`.
- **audit** Body text under 16px on a reading page, under 14px on a utility, or over 20px anywhere.
- **audit** More than twelve uppercase elements. Uppercase is for a few proofed labels.
- **eye** Every heading in the same weight and colour as the body, distinguished only by size.
- **eye** A monospace face on headings, navigation or prose because the subject is technical.

## Colour and surfaces

- **audit** Gradient text. Gradient backgrounds of any kind get a warning; a purple-to-blue one is always wrong.
- **audit** `backdrop-filter`, glass panels, frosted cards.
- **audit** A box-shadow on anything that is not a control, a dialog or a popover.
- **audit** More than two saturated hue families on the page, unless data series need them.
- **audit** More than three distinct border-radius values.
- **eye** A border and a shadow on the same box.
- **eye** A rounded card around every section, or a card grid used because the content came in threes.
- **eye** Pill badges, chips and status tags on things that have no status.
- **eye** A coloured left border on every block. One callout may earn it.
- **eye** Cream, brown and a serif as the whole editorial idea. Dark mode as the whole precision idea.

## Layout

- **audit** Horizontal overflow at 390px.
- **audit** On a utility, the first useful unit below 40% of the phone viewport.
- **eye** A hero: a centred title, a sentence of positioning and a button before any content.
- **eye** A three-column feature grid with an icon, a bold label and two lines of copy.
- **eye** Everything centred. Reading pages align left; a centred title over left-aligned prose is not a decision.
- **eye** A single 1200px centred container with no other layout idea.
- **eye** Uniform spacing between every element. Space should change where the content changes.
- **eye** A section divider, eyebrow label or numbered marker that encodes nothing.

## Motion and interaction

- **audit** A `:hover` rule that transforms the element (lift, scale, tilt).
- **eye** Entrance animations, scroll-triggered reveals, parallax, a typing effect.
- **eye** A hover-only affordance with no keyboard or touch equivalent.
- **eye** A control that exists to look interactive rather than to answer a question in the brief.

## Content

- **audit** Emoji in text (warning). Use an SVG or a word.
- **audit** An image without an `alt` attribute.
- **eye** Emoji or icon-font glyphs as icons.
- **eye** Lorem ipsum, "Lorem Corp", "John Doe", invented statistics, a fake testimonial.
- **eye** Copy that says seamless, effortless, powerful, beautiful, elevate, unlock, supercharge, or ✨.
- **eye** A page that is longer than its content: sections added to make it look complete.
- **eye** "Made with" footers, social icon rows and newsletter boxes on a document or tool.

## The three-question test

Before the critic pass, answer these for the page:

1. Which element would a template not have produced? If nothing, the page is generic.
2. Which decoration could be removed without losing information? Remove it.
3. What does the accent colour mean? If it means "brand", it means nothing.
