# Technical field guide reference

Primary reference: a Distill section with a figure that answers the paragraph above it. Two companion crops show an interactive figure with its controls (Sam Rose) and a chapter opening with centred illustrations and captions (The Book of Shaders).

All three were user-supplied full-page captures from Chrome at 2× device pixel ratio, 1683 CSS px wide, cropped to a 1200 CSS px band and downscaled to CSS pixels on 2026-09-14. Values below were measured from the crops and are approximate.

## 1. Section with figure (primary)

- Page title: Exploring Bayesian Optimization — Distill
- Source: https://distill.pub/2020/bayesian-optimization/
- Image: [reference.png](reference.png)
- Captured: 2026-09-14
- Band: the "Active Learning" heading through the first figure and the paragraph after it.

| Relationship | Value in the reference |
| --- | --- |
| Body size and leading | about 17px sans, line-height about 1.7 (29px pitch); paragraphs separated by about 17px |
| Prose measure | 700px from x=490 to x=1192, about 85ch, centred on the page |
| Section heading | about 34px sans weight 600, ratio 2.0 to body, with a 1px light rule 19px below it and 32px between the rule and the prose |
| Figure width | 1057px from x=312 to x=1369, wider than the prose by about 178px on each side, still centred on the prose column |
| Figure anatomy | two 227px-tall plots with a 13px title above each, an arrow between them, and a legend in a 1px-bordered box at the right edge; axis labels at 10px |
| Figure spacing | about 55px between the last prose line and the plot titles; about 50px between the caption and the next paragraph |
| Caption | about 13px mid grey at line-height 1.7, set to the figure's width rather than the prose measure; it names what each mark means |
| Reference marks | superscript numbers in one small blue, the only accent in the prose |
| Colour | white ground, near-black text; inside the figure each colour means one series (purple truth, black prediction, grey uncertainty, red last point) and the meaning holds across every figure in the article |

## 2. Interactive figure with controls (Sam Rose)

- Page title: Bloom Filters — samwho.dev
- Source: https://samwho.dev/bloom-filters/
- Image: [reference-interactive.png](reference-interactive.png)
- Captured: 2026-09-14
- Band: the add/check/clear figure, the paragraph and dialogue after it, and the start of the "False-positive rates" section.

| Relationship | Value in the reference |
| --- | --- |
| Body size and leading | about 18px sans, line-height about 1.55 (28px pitch) |
| Prose measure | 740px from x=468 to x=1207, about 80ch, centred |
| Controls | one 38px-tall row: a 412px text input, then three 96–116px buttons 5px apart (green add, blue check, orange clear), white labels, about 4px radius; the row spans the prose measure exactly |
| Interactive field | 32 circles at 42px with a 4px gap, 16 per row, two rows 20px apart, starting 24px below the controls; unset bits pale yellow (#F7E2B2), set bits saturated orange |
| Colour as vocabulary | the word "bits" in the prose is bold in the bit colour; each hash function name has its own colour that matches the table and the figure |
| Dialogue callout | an 88px panel in light grey-blue (#ECEFF4) with about 12px radius and a speech tail, a character drawing 100px wide to its left; used to voice the reader's objection before answering it |
| Section heading | about 30px serif weight 600 preceded by a small orange "#" anchor mark; about 55px above and 26px below |
| Chart | y-axis percentage labels at 14px, a light grid, chart width about 90% of the prose measure |
| Colour | white ground, near-black text; green, blue and orange only on the three actions; yellow and orange only on bits |

## 3. Chapter opening with centred illustrations (The Book of Shaders)

- Page title: Getting started — The Book of Shaders
- Source: https://thebookofshaders.com/01/
- Image: [reference-chapter.png](reference-chapter.png)
- Captured: 2026-09-14
- Band: the chapter title, first subheading, two paragraphs and two illustrations with captions.

| Relationship | Value in the reference |
| --- | --- |
| Body size and leading | about 18px serif, line-height about 1.5 (27px pitch) |
| Prose measure | 792px from x=442 to x=1234, about 95ch |
| Title stack | chapter title about 44px italic serif, subheading about 32px italic serif, ratio 2.4 and 1.8 to body; 22px between them and 15px from subheading to prose |
| Figure | 517px wide, centred on the prose column (centre x=841 against a prose centre of x=838), 257px tall |
| Figure spacing | 22px between the last prose line and the figure; 31px between the caption and the next paragraph |
| Caption | about 13px italic serif, right-aligned to the figure's right edge, line-height 1.6; credits the source and date |
| Chrome | a 1px rule under a one-line header; nothing else on the canvas |
| Colour | white ground, black text; the only colour is the magenta arrow inside one illustration, which carries meaning (before and after) |

## Borrow

A section heading with a rule and prose directly beneath; a figure wider than the prose but centred on it, with its caption set to the figure's width; a caption that names what every mark means; colours inside figures that mean the same part in every figure; one row of controls exactly the prose width, the primary action first; an interactive field with a fixed cell size and gap; key terms in the prose set in the colour of the thing they name; a small anchor mark on section headings; centred illustrations narrower than the prose with a right-aligned italic caption.

## Do not borrow

Distill's masthead, author block and DOI line; the 85–95ch measures without their tall leading; Sam Rose's character drawings, dialogue voice and playful palette as page decoration; The Book of Shaders' italic display serif as a brand; illustrations, plots and code from the sources; a control row with no figure state to change. The field guide makes its subject legible before decoration.
