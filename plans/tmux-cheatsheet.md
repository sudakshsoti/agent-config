# Tmux cheatsheet

## Context

Build a self-contained HTML cheatsheet from `/Users/sudakshsoti/.tmux.conf` for the user's personal tmux workflow. It should make the configured prefix, navigation, session/window/pane actions, copy mode, persistence, and sessionx shortcuts easy to scan, with no external assets or dependencies.

The current tmux setup uses `Ctrl-a` as the prefix, emacs keys, mouse support, mobile-friendly arrow navigation, OSC 52 clipboard forwarding, a bottom Kohra-style status line, and TPM plugins including sessionx, yank, resurrect, and continuum. The checked-in chezmoi template `/Users/sudakshsoti/dev/dotfiles/dot_tmux.conf.tmpl` matches the active config except that it keeps the home directory portable. The repository has existing visual decisions in `design/decisions.md`; current unrelated working-tree changes in `install.sh`, `omp/config.yml`, and `pi/settings.json` must remain untouched.

Settled in design-grill round 1: deliver the file at the repository root as `desktop-tmux-cheatsheet.html`; cover the complete configured workflow while putting daily actions first; use the Kohra terminal direction; and include a tiny shortcut filter.

The machine runs tmux 3.7c and has local mono faces including InputMono Nerd Font Mono, JetBrains Mono, PT Mono, and Menlo. The typography plan should favour recognisable key glyphs, punctuation, and numerals at compact sizes, with a deliberate local fallback stack unless portability requirements call for embedding a font.

## Approach

- Use a single HTML file with inline CSS and only minimal JavaScript if a small interaction materially improves lookup.
- Organise content by task rather than mirroring config order: prefix, everyday navigation, panes, windows, sessions, copy/clipboard, persistence, and status cues.
- Make the prefix explicit in every shortcut so the page works as a quick reference rather than requiring memory of `Ctrl-a`.
- Use a dense, dark terminal-oriented visual system grounded in the existing Kohra cues, while keeping contrast, focus visibility, responsive reflow, printability, and keyboard access intact.
- Use a type-led two-role system: a readable screen sans for explanatory text and a mono face for keys, commands, and status cues; proof real shortcut strings and long labels before finalising sizes and measure.
- Verify every shortcut and configured behaviour against the real config, then render the HTML at narrow and wide widths for a visual pass.

## Files to modify

- `desktop-tmux-cheatsheet.html` — new standalone deliverable (proposed name; confirm if another location/name is preferred).
- `plans/tmux-cheatsheet.md` — this implementation plan.

## Reuse

- Source of truth: `/Users/sudakshsoti/.tmux.conf`.
- Visual constraints: `design/decisions.md`.
- Design guidance: `frontend-design`, `design-typography`, and `design-grill` skill instructions.

## Steps

- [x] Settle audience, scope, output path, and visual direction.
- [ ] Translate the config into a reviewed shortcut/content inventory, separating custom bindings from clearly labelled tmux/plugin defaults where useful.
- [ ] Build the self-contained responsive HTML with inline styles and minimal interaction.
- [ ] Render and inspect the result at 390, 900, and 1440 CSS pixels; fix wrapping, contrast, focus, and print issues.
- [ ] Re-check the final inventory against `/Users/sudakshsoti/.tmux.conf` and run lightweight HTML validation.

## Verification

- Open the file directly in a browser without a network connection.
- Check all displayed shortcuts against `/Users/sudakshsoti/.tmux.conf`, including sessionx's fzf header actions and the status-line mode cues.
- Test responsive layout at 390, 900, and 1440 CSS pixels, keyboard focus, reduced motion, and print preview.
- Confirm no external fonts, scripts, stylesheets, images, or network requests are required.
