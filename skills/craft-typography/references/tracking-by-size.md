# Tracking by size

Calibration behind the existing rule "tracking at display sizes must not be left at the body default." The rule stays as the rule; this table is the starting calibration, not a substitute for checking a real specimen.

## Size-to-tracking table

| Size | Tracking |
|---|---|
| 10–12px | +0.5px to +1px (open up tiny text) |
| 14–16px (body) | 0 (default) |
| 20–28px | -0.01em to -0.02em (slight tighten) |
| 32–48px (headings) | -0.02em to -0.04em |
| 64px+ (display) | -0.04em to -0.06em |

Larger sizes need negative tracking because a typeface's default spacing is calibrated for body sizes.

## Cross-check against Apple's flat display value

Apple's published guidance uses a flat -0.02em tracking value across its display sizes. That value sits comfortably inside this file's 32–48px band above, but it under-tightens against the 64px+ row, which calls for -0.04em to -0.06em — roughly half the negative tracking Apple's flat number provides. Tracking stays size-specific: a single flat value applied across all display sizes is exactly the failure this table exists to prevent. Do not import -0.02em as a substitute for the 64px+ row.

## Uppercase tracking and word count

Uppercase reads harder than mixed case because every letter is the same height. Two conditions make it acceptable: a short phrase (under four words) at any size, or a small size (roughly 10–12px) paired with wide tracking (+0.05em to +0.1em) — the eyebrow-label/badge case. Uppercase body prose or anything a user needs to skim is outside both conditions.

## Sources

- Robert Bringhurst, The Elements of Typographic Style (line length, tracking).
- `skills/design-engineering/references/typography/line-length-tracking.md` @ `81805dc89d40889639a95502bfb578a098266dc8`.

## Gotcha

Agents apply the display-size tracking values to body text, or leave uppercase labels at the body default tracking — either direction costs legibility for no visual gain. The table's rows are per size band; do not interpolate a "close enough" row for a size that falls between two of them without checking the specimen.
