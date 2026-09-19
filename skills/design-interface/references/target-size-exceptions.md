# Target size: the AA exceptions and the spacing math

WCAG 2.2 SC 2.5.8 Target Size (Minimum, Level AA) sets a 24×24 CSS-pixel floor for pointer targets. SC 2.5.5 Target Size (Enhanced, Level AAA) sets 44×44. A target under 24×24 is not automatically a failure against SC 2.5.8: check each of the five named exceptions before reporting it.

## The five AA exceptions (SC 2.5.8)

- **Spacing.** The target is smaller than 24×24 but positioned so that a 24px-diameter circle centred on the target's bounding box does not intersect the equivalent circle of any adjacent target. Worked example: two 20px targets each get a 24px circle (2px of radius beyond each edge); the circles stay clear of each other once the targets are 4px apart edge to edge. Shrink the gap below 4px and the circles overlap, and the exception no longer applies.
- **Equivalent.** The same function is available through another target on the same page that does meet the minimum, for example an undersized inline icon button duplicated by a full-size control elsewhere in the same flow.
- **Inline.** The target sits within a sentence or block of text, such as a link inside a paragraph, where the target size is a product of the line height and surrounding text rather than a discrete control.
- **User Agent Control.** The size of the target is determined by the user agent and not modified by the author, for example a native `<input type="checkbox">` rendered at the browser's default size with no custom sizing applied.
- **Essential.** A specific size is essential to the information being conveyed, for example a map at a scale where enlarging every point would misrepresent the data.

## Mechanics: where the enlarging pseudo-element goes

When a visible control must stay smaller than the target floor, grow the hit area with a pseudo-element on the wrapping `<label>` or `<button>`, never on the `<input>` itself. Replaced elements (`<input>`, `<img>`, `<video>`) do not reliably render `::before`/`::after` content across browsers, so a pseudo-element placed on the input is silently dropped rather than merely mis-positioned.

```css
.checkbox-label {
  position: relative;
}
.checkbox-label::after {
  content: "";
  position: absolute;
  inset: 50% auto auto 50%;
  transform: translate(-50%, -50%);
  width: 24px;
  height: 24px;
}
```

Two enlarged hit areas must not overlap; where they would, shrink the pseudo-element to the largest size that clears the neighbour rather than removing it.
