# Font-file inspection

What to read from the binary before asserting a family's capability. A specimen page shows what someone chose to render, not what the file can do — the file is the only source for that.

## Tables to read

- **`fvar`** — the variable axes the file actually carries, each with a tag, a minimum, a default and a maximum. The five registered axis tags are `wght`, `wdth`, `opsz`, `ital` and `slnt`; anything else is foundry-custom and has no cross-font meaning — its behaviour is defined only by this file.
- **`STAT`** — named instances (the points along an axis a foundry has given a name, such as "SemiBold" on `wght`) and how those names relate to each other for style linking.
- **`avar`** — the axis-value remapping table. Without it, a stop labelled 500 on `wght` is not guaranteed to look like weight 500 on another variable font; `avar` is what makes an axis value mean something specific inside this file.
- **`name`** — the family and subfamily name records, and which ones a browser will actually select for `font-family` and `font-style`/`font-weight` matching.
- **`GSUB`/`GPOS`** — the OpenType feature tags the file implements (`liga`, `kern`, `ss01`, `smcp`, and so on) and, for `GPOS`, the positioning data that makes those features render correctly rather than merely being present as tags.
- **Coverage** — the Unicode codepoints the `cmap` table maps to a glyph, checked against every script the content requires.

## Commands

- `fonttools ttx -l <file>` lists every table in the file.
- `fonttools ttx -t fvar -t GSUB -t GPOS -o - <file>` dumps those three tables to stdout without writing a file.
- `fc-query <file>` gives a faster summary of family, style and charset coverage where the full table dump is not needed.

## Sources

- `archive/skills/typography-craft/SKILL.md` @ `201bd7ed9072269c1081a0e4d2315868b84649e4`.
- The OpenType specification, `fvar`, `STAT`, `avar`, `name`, `GSUB` and `GPOS` tables (Microsoft/Adobe/OpenType.org).

## Gotcha

Agents treat a codepoint list as proof the script renders — coverage is not shaping, and a font can carry every Devanagari codepoint in `cmap` and still compose conjuncts wrongly because its `GSUB`/`GPOS` rules for that script are incomplete. Confirming a script "renders" requires shaping real conjunct sequences from that script, not just checking each codepoint is present.
