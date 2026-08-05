# Themes

`assets/base.html` ships with the `manuscript` theme active. A theme is one `:root` swap and
nothing else: every rule below reads a token, so no literal colour, font or measure survives
to fight it.

To apply one, in the generated file replace the whole `:root { ... }` block with the theme's
light block, replace the whole `@media (prefers-color-scheme: dark)` block with its dark
block, and rename `theme:` in the comment above them. Leave `@media print` and everything
below it untouched. A theme that seems to need an edit below `:root` is a bug in
`base.html`, not something to patch per document.

## console

For reference sheets, checklists, command references and comparison notes: dense, scannable,
mono labels, wide column.

```css
:root {
  color-scheme: light dark;

  --paper:       #fbfbfc;
  --ink:         #1b1f27;
  --muted:       #5a616e;
  --rule:        #e0e2e8;
  --fill:        #f0f1f5;
  --accent:      #0b5fd0;
  --accent-soft: #e6edf9;

  --font-body: ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  --font-ui:   ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  --font-mono: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;

  --measure: 76ch;
  --wide:    82rem;
  --leading: 1.5;

  --text-base: 1rem;
  --text-h1:   1.75rem;
  --text-h2:   1.25rem;
  --text-h3:   1rem;

  --s1: 0.25rem;
  --s2: 0.5rem;
  --s3: 0.75rem;
  --s4: 1rem;
  --s5: 1.75rem;
  --s6: 2.75rem;

  --radius: 4px;
}
```

```css
@media (prefers-color-scheme: dark) {
  :root {
    --paper:       #14171c;
    --ink:         #e2e5ec;
    --muted:       #98a0af;
    --rule:        #272c35;
    --fill:        #1c2028;
    --accent:      #7fb0f2;
    --accent-soft: #1d2634;
  }
}
```

Contrast: `#1b1f27` on `#fbfbfc` is **15.97:1**; `#e2e5ec` on `#14171c` is **14.24:1**. Muted
clears at 6.03:1 and 6.83:1, the link accent at 5.70:1 and 8.04:1. All past AA's 4.5:1.

`#0b5fd0` matches `skills/orient/assets/shell.html`, so HTML from this repo stays coherent.
Pointing `--font-ui` at the mono stack is what makes headings, meta, tables and labels mono
while body prose stays sans.

## report

For briefs, findings, recommendations and status notes: sans throughout, cool paper, tighter
section rhythm than manuscript.

```css
:root {
  color-scheme: light dark;

  --paper:       #f7f8fa;
  --ink:         #1c2420;
  --muted:       #5c665f;
  --rule:        #dfe3e0;
  --fill:        #eef0ee;
  --accent:      #2f6b4c;
  --accent-soft: #e4ede8;

  --font-body: ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  --font-ui:   ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  --font-mono: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;

  --measure: 72ch;
  --wide:    78rem;
  --leading: 1.6;

  --text-base: 1.125rem;
  --text-h1:   2rem;
  --text-h2:   1.4rem;
  --text-h3:   1.08rem;

  --s1: 0.25rem;
  --s2: 0.5rem;
  --s3: 0.75rem;
  --s4: 1.125rem;
  --s5: 1.75rem;
  --s6: 2.5rem;

  --radius: 5px;
}
```

```css
@media (prefers-color-scheme: dark) {
  :root {
    --paper:       #161a18;
    --ink:         #e2e8e4;
    --muted:       #98a49c;
    --rule:        #2a312d;
    --fill:        #1d2320;
    --accent:      #7fbf9c;
    --accent-soft: #1e2a24;
  }
}
```

Contrast: `#1c2420` on `#f7f8fa` is **14.94:1**; `#e2e8e4` on `#161a18` is **14.14:1**. Muted
clears at 5.61:1 and 6.80:1, the accent at 5.94:1 and 8.23:1.

Smaller `--s5` and `--s6` give the denser section rhythm. A slightly larger `--text-base`
than manuscript's `1.0625rem` carries the brief's read-once-at-arm's-length feel; `console`
goes the other way at `1rem` because a reference sheet is scanned, not read.

## Adding a theme

Define the complete token set, in the order above, in both a light `:root` and a dark
`@media (prefers-color-scheme: dark)` override; a partial set leaves manuscript values
showing through. One accent hue, no gradients, neutrals tinted toward it, never pure `#000`
or `#fff` in either mode. Compute body-on-paper contrast in both modes, clear 4.5:1, record
the number beside the block. System stacks only, no webfonts. Change nothing below `:root`.
