# Fonts for standalone artifacts

A single HTML file cannot carry self-hosted font files, so `design-typography`'s self-hosting rule is relaxed here: a standalone artifact may load fonts from Google Fonts with one `<link>`. Every family below is OFL-licensed. Each `<link>` was fetched and returned 200 on 2026-09-12; copy it as written, because a wrong axis range returns an error page and the browser silently falls back.

Rules that still hold:

- Two families at most. A third is allowed only as a mono for code, identifiers or values.
- Never Inter, Roboto, Space Grotesk, Instrument Serif, Fraunces or Playfair Display. They read as automatic.
- Never ship a system stack as the answer. `audit.js` fails a page whose primary family is generic or is rendering a fallback.
- Declare a metric-compatible fallback after the webfont so a slow load does not reflow badly: Georgia for a serif, `"Helvetica Neue", Arial` for a sans, `ui-monospace, Menlo` for a mono.
- Turn on `font-optical-sizing: auto` only for a family listed with an `opsz` axis.

Pairings are listed with the language they suit first; a pairing may be borrowed by a neighbouring language when the content calls for it. The skeleton for each language already carries the first pairing.

## technical-field-guide

1. **Source Serif 4** (opsz, wght) for reading + **IBM Plex Mono** for identifiers. The skeleton default.
   `<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Source+Serif+4:ital,opsz,wght@0,8..60,400..700;1,8..60,400&family=IBM+Plex+Mono:wght@400;500&display=swap">`
2. **Literata** (opsz, wght) + **JetBrains Mono**. Warmer, more bookish.
   `<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Literata:ital,opsz,wght@0,7..72,400..700;1,7..72,400&family=JetBrains+Mono:wght@400..500&display=swap">`
3. **Source Sans 3** for reading + **Source Serif 4** for headings, when a sans reading face fits the audience better.
   `<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Source+Sans+3:wght@400..700&family=Source+Serif+4:opsz,wght@8..60,400..700&display=swap">`

## personal-software

1. **Geist** + **Geist Mono**. One family carries the tool. The skeleton default.
   `<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Geist:wght@400..700&family=Geist+Mono:wght@400..500&display=swap">`
2. **Atkinson Hyperlegible Next**, single family, when legibility at small sizes matters most.
   `<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible+Next:wght@400..700&display=swap">`
3. **Hanken Grotesk**, single family, slightly warmer.
   `<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Hanken+Grotesk:wght@400..700&display=swap">`

## precision-software

1. **IBM Plex Sans** + **IBM Plex Mono**. Distinct small forms, tabular figures. The skeleton default.
   `<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap">`
2. **Geist** + **Geist Mono**, cooler and tighter.
   `<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Geist:wght@400..700&family=Geist+Mono:wght@400..500&display=swap">`
3. **Figtree**, single family, for a friendlier working surface.
   `<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Figtree:wght@400..700&display=swap">`

## editorial-modernist

1. **Newsreader** (opsz, wght) for display and body + **Public Sans** for meta and captions. The skeleton default.
   `<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,400..700;1,6..72,400&family=Public+Sans:wght@400..700&display=swap">`
2. **Source Serif 4** + **Source Sans 3**. Steadier, less display character.
   `<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Source+Sans+3:wght@400..700&family=Source+Serif+4:opsz,wght@8..60,400..700&display=swap">`
3. **Lora** + **Work Sans**, when the subject is warmer or more informal.
   `<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Work+Sans:wght@400..600&family=Lora:ital,wght@0,400..700;1,400&display=swap">`

## swiss-graphic

1. **Archivo** (wdth, wght), single family; the width axis gives display and text different proportions. The skeleton default.
   `<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,400..800&display=swap">`
2. **Instrument Sans** (wdth, wght), single family, slightly narrower.
   `<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Instrument+Sans:wdth,wght@75..100,400..700&display=swap">`
3. **Schibsted Grotesk** or **Familjen Grotesk**, single family, for a more Scandinavian neutrality.
   `<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Schibsted+Grotesk:wght@400..700&display=swap">`
   `<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Familjen+Grotesk:wght@400..700&display=swap">`

## visual-essay

1. **Crimson Pro** for prose + **Public Sans** for labels, annotations and controls. The skeleton default. Crimson Pro runs small; keep body at 20px.
   `<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Crimson+Pro:ital,wght@0,400..700;1,400&family=Public+Sans:wght@400..700&display=swap">`
2. **Source Serif 4** + **Source Sans 3**, when the essay is more report than narrative.
   `<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Source+Sans+3:wght@400..700&family=Source+Serif+4:opsz,wght@8..60,400..700&display=swap">`
3. **Literata** + **Hanken Grotesk**.
   `<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Literata:ital,opsz,wght@0,7..72,400..700;1,7..72,400&family=Hanken+Grotesk:wght@400..700&display=swap">`

## industrial-instrument

1. **Chivo** + **Chivo Mono**. A neutral grotesk with a matched mono for values. The skeleton default.
   `<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Chivo:wght@400..800&family=Chivo+Mono:wght@400..600&display=swap">`
2. **Barlow** + **Barlow Condensed**, when labels need a condensed cut beside wide readouts.
   `<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Barlow:wght@400;500;600&family=Barlow+Condensed:wght@500;600&display=swap">`
3. **IBM Plex Sans Condensed** + **IBM Plex Mono**, for denser panels.
   `<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Condensed:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap">`

## quiet-catalogue

1. **Spectral** for titles and descriptions + **Karla** for metadata and controls. The skeleton default.
   `<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Spectral:ital,wght@0,400;0,600;1,400&family=Karla:wght@400..700&display=swap">`
2. **EB Garamond** + **Libre Franklin**, for older or more scholarly material.
   `<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=EB+Garamond:ital,wght@0,400..700;1,400&family=Libre+Franklin:wght@400..600&display=swap">`
3. **Newsreader** + **Archivo**, for a catalogue with strong titles.
   `<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,400..700;1,6..72,400&family=Archivo:wdth,wght@62..125,400..800&display=swap">`

## Verifying a pairing you add

Fetch the `<link>` URL with `curl -s -o /dev/null -w "%{http_code}"` and a browser user agent; it must return 200. Then run `audit.js`, which fails when the declared family renders a fallback. Record the date checked beside the new entry.
