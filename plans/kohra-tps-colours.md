# Plan: align TPS colours with Kohra

## Direction

Make token speed feel native to the existing Kohra footer by replacing the extension’s saturated red, orange, green, and cyan defaults with Kohra’s muted semantic status colours. Keep the current speed thresholds, status text, icon, and footer position unchanged.

## Colour mapping

| TPS tier | Meaning | Kohra token | Hex |
| --- | --- | --- | --- |
| Slow | Poor throughput | `red` / error | `#E19796` |
| Medium | Acceptable, worth noticing | `amber` / warning | `#D2A56D` |
| Fast | Healthy throughput | `green` / success | `#A4B776` |
| Blazing | Exceptional throughput | `teal` | `#70B4A2` |

Teal is preferable to mist blue for the top tier because mist blue already means focus, links, path, and selection. This keeps TPS as a performance signal rather than another navigation accent.

## Implementation

- Add a `tokenSpeed` block to `pi/settings.json` with the four Kohra hex values.
- Leave `selfColorize: true` on the Powerline custom item so the extension’s tier colour reaches the footer.
- Do not modify package source under `node_modules`; settings remain stable across package updates.
- Validate the JSON and restart Pi to visually confirm all four configured colours are accepted.

## Files

- Modify `pi/settings.json` only.

## Acceptance checks

- TPS no longer uses neon `#ff4444`, `#ffaa00`, `#00ff88`, or `#44ddff`.
- Slow, medium, fast, and blazing values use the corresponding Kohra palette colours above.
- The TPS item remains visible in the current Powerline layout.
- No other footer segment colours or TPS behaviour change.
