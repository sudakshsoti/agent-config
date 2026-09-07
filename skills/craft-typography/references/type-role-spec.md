# Type role specification

The completeness contract for a project's type system: every text role on the surface specified across the same seven fields, so a gap is visible as an empty cell rather than a role nobody thought about.

## The table

| Role | Family and cut | Axes/features | Size/leading | Tracking | Measure/alignment | Purpose |
| --- | --- | --- | --- | --- | --- | --- |
|  |  |  |  |  |  |  |

- **Family and cut** — which face, and which weight/width/italic cut of it, not just the family name.
- **Axes/features** — which variable axes or OpenType features this role turns on, from the set the font file actually carries (`../references/font-file-inspection.md`).
- **Size/leading** — the resolved size and line-height at this role's rendered context, from `design/tokens.css`.
- **Tracking** — explicit, especially at display sizes where the body default reads loose or tight.
- **Measure/alignment** — the reading measure this role is expected to sit inside, and its text alignment.
- **Purpose** — the job this role does on the surface (a heading level, a caption, a numeral-heavy stat), so a role can be told apart from a merely different size of the same job.

Faces and cuts come from `design/decisions.md`; numbers come from `design/tokens.css`. The table itself specifies nothing new — it is a check that every text role in use has a row, and every cell in that row is filled or explicitly deferred to an open question.

## What an unfilled cell means

An unfilled cell is a question for the direction, not a value to invent while filling in the table. The table's job is completeness, not authorship: it exists to make an unanswered question visible as a gap, not to license guessing at plausible-looking numbers to close the gap.

This table does not replace `critique`'s own report — `critique` judges whether the built surface matches what this table says; this table is what "what was specified" refers to when there is one.

## Sources

- `archive/skills/typography-craft/SKILL.md` @ `201bd7ed9072269c1081a0e4d2315868b84649e4`.

## Gotcha

Agents read the table as licence to invent sizes and tracking the direction never settled — an unfilled cell is a question for the direction, or for the reply where there is no direction file, not a value to choose to make the table look complete.
