# Design evals

Three fixed briefs. The point is not to score a screen, it is to find out whether a
rule in `interface-composition` or `slop.md` actually changes a render. A rule that
does not is an adjective and should be cut rather than reworded.

## How to run

1. Fresh session, no design skills invoked. Paste the brief. Screenshot at 390 /
   900 / 1440. Keep the PNGs as the baseline.
2. Fresh session. `/design`, then the same brief. Screenshot the same three widths.
3. Diff the two by eye against the P0 list in `SKILL.md`. Count P0 findings in
   each. If the count did not drop, the rules did not bind.

Record the P0 counts and the date under Results. Do not tune the briefs to make the
skills look good; change the briefs only when they stop exercising a rule.

## Brief 1 — dense listing

> Build a screen listing tonight's five recommended films. Each has a title, year,
> runtime, language, genres, a one-line blurb, and ratings from Letterboxd, Rotten
> Tomatoes, Metacritic and IMDb, some of them missing. The user marks each one
> watched, already seen, or not interested, and can give it a rating.

Exercises: pattern selection (cards vs table), repetition audit, action hierarchy,
`items x actions`, shared axis, container arithmetic.

## Brief 2 — form

> Build the filter panel for that app. Genre multi-select, decade range, minimum
> rating per source, runtime ceiling, a toggle for films already in the watchlist,
> and a toggle for films with no poster. It opens over the listing.

Exercises: control density, one primary action, label repetition, overlay layering,
390px behaviour, focus order.

## Brief 3 — empty and error

> The programme has not been generated yet. Then: generation failed because the
> ratings API is over quota. Then: generation is running and streaming progress.

Exercises: states occupying the populated region, no layout shift on swap, error
copy that names cause and fix, status carried by more than hue.

## Results

| Date | Brief | Baseline P0 | With skills P0 | Note |
|---|---|---|---|---|
| | | | | |
