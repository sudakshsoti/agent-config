# Fonts

**Blacklist only, no whitelist.** Anything not banned is available; the
operator adds to the blacklist over time.

## Banned

Poppins, Montserrat, Raleway, Lato, Open Sans, Nunito, Quicksand, Playfair
Display, Oswald, Bebas Neue, Comfortaa, Josefin Sans, Roboto, Space Grotesk,
Manrope, DM Sans, DM Serif, Instrument Sans, Instrument Serif, Fraunces.

## Inter is body and UI only, never display

Inter at 72px in a hero is the loudest "an agent made this" signal.

## Known-good free faces

Newsreader, Literata, Source Serif 4, Geist, Geist Mono, IBM Plex Sans /
Serif / Mono, JetBrains Mono, Schibsted Grotesk, Bricolage Grotesque, Libre
Caslon Text, Hanken Grotesk, Fira Sans / Code / Mono. Not a whitelist, a
shortlist.

## Licensed set is this-machine-only

For print or eyes-only artifacts. Anything public defaults to free faces.
The question, asked once in Phase 0: *"Free fonts (safe to share) or your
licensed set (this machine only)?"*

## Inventory

Held as `woff2` under `homelab/stacks/static/fonts`: Söhne (Buch, Kräftig,
Halbfett), National 2 (regular, italic, medium, bold, bold-italic), Berkeley
Mono (regular, bold), plus free Literata, Newsreader, Inter, JetBrains Mono.

Desktop only, no `woff2`: Mallory, Tiempos Text, Halyard, Atkinson
Hyperlegible Next.

**Not present in any form**, despite `frontend-craft` having listed them:
Mercury, Whitney, Archer, Verlag, Knockout, Gotham, Domaine, Harriet.

## Delivery

Two Latin-subset faces are roughly 100KB after base64 and the file stays
self-contained, which is the preferred route for anything shareable. Until
that is built, an example or a private artifact may link Google Fonts and
take the `check.py` WARN.
