# Tmux cheatsheet

## Context

Build a self-contained HTML cheatsheet from `/Users/sudakshsoti/.tmux.conf` for the user's personal tmux workflow. It should make the configured prefix, navigation, session/window/pane actions, copy mode, persistence, and sessionx shortcuts easy to scan, with no external assets or dependencies.

The current tmux setup uses `Ctrl-a` as the prefix, emacs keys, mouse support, mobile-friendly arrow navigation, OSC 52 clipboard forwarding, a bottom Kohra-style status line, and TPM plugins including sessionx, yank, resurrect, and continuum. The checked-in chezmoi template `/Users/sudakshsoti/dev/dotfiles/dot_tmux.conf.tmpl` matches the active config except that it keeps the home directory portable. Local plugin documentation confirms the configured sessionx actions, tmux-yank copy keys, tmux-resurrect save/restore keys, and continuum's automatic restore behaviour. The repository has existing visual decisions in `design/decisions.md`; current unrelated working-tree changes in `install.sh`, `omp/config.yml`, and `pi/settings.json` must remain untouched.

Settled in design-grill rounds 1–3: deliver the file at the repository root as `desktop-tmux-cheatsheet.html`; cover the complete configured workflow while putting daily actions first; include a small, clearly labelled tmux-defaults section; use the Kohra terminal direction; use balanced density; organise wide screens as a slim index rail plus content; include a live, unobtrusive shortcut filter; and make the typography portable across machines.

The machine runs tmux 3.7c and has local mono faces including InputMono Nerd Font Mono, JetBrains Mono, PT Mono, and Menlo. The supplied font library also contains `CommitMono VariableFont.woff2` (about 88 KB) and `AtkinsonHyperlegibleNext-VariableFont_wght.ttf` (about 112 KB); their accompanying metadata/licence files identify SIL Open Font License 1.1. Use these as the portable pair: Commit Mono for key sequences and Atkinson Hyperlegible Next for explanatory text. The typography plan should favour recognisable key glyphs, punctuation, and numerals at compact sizes.

## Approach

- Use a single HTML file with inline CSS and only minimal JavaScript if a small interaction materially improves lookup.
- Organise content by task rather than mirroring config order: prefix, everyday navigation, panes, windows, sessions, copy/clipboard, persistence, and status cues. On wide screens, keep a slim index rail for the live filter and section links; let the main column carry the reading order.
- Make the prefix explicit in every shortcut so the page works as a quick reference rather than requiring memory of `Ctrl-a`.
- Mark shortcuts by source: custom config bindings, sessionx bindings, tmux-yank/resurrect plugin bindings, and useful tmux defaults, so inherited behaviour is not mistaken for a custom mapping.
- Use a balanced, dark terminal-oriented visual system grounded in the existing Kohra cues, while keeping contrast, focus visibility, responsive reflow, printability, and keyboard access intact.
- Use a type-led two-role system: a readable screen sans for explanatory text and an embedded mono face for keys, commands, and status cues; proof real shortcut strings and long labels before finalising sizes and measure.
- Keep the font payload limited to the two inspected variable files: Commit Mono's WOFF2 for key sequences and Atkinson Hyperlegible Next's TTF for prose, with explicit fallback stacks if either embedded face cannot load.
- Verify every shortcut and configured behaviour against the real config, then render the HTML at narrow and wide widths for a visual pass.

## Content inventory

The inventory is based on the active config and a `tmux -f ~/.tmux.conf list-keys -T prefix` check on tmux 3.7c.

- **Start here:** `Ctrl-a` is the prefix; `Ctrl-a Ctrl-a` sends a literal `Ctrl-a`; `Ctrl-a r` reloads; `Ctrl-a b` toggles the status bar.
- **Everyday navigation:** repeatable `Ctrl-a` + arrow keys select panes; `Ctrl-a Space` returns to the last window; `Ctrl-a L` returns to the last session/client; mouse support remains available.
- **Panes:** `Ctrl-a c` opens a window in the current directory; `Ctrl-a "` splits vertically in the current directory; `Ctrl-a %` splits horizontally in the current directory; the tmux default `Ctrl-a z` toggles zoom.
- **Windows:** `Ctrl-a w` opens the current-session tree; the small defaults strip can include next/previous window, detach, and direct window numbers without hiding the custom mappings.
- **Sessions:** `Ctrl-a o` opens sessionx with zoxide and `~/dev` subdirectories as custom session paths; the sessionx command bar documents Enter, Alt-Backspace, Ctrl-r, Ctrl-w, Ctrl-t, Ctrl-e, Ctrl-f, Ctrl-b, Ctrl-u/Ctrl-d, and Escape. Its useful inherited actions such as Ctrl-p/Ctrl-n and `?` preview toggle will be labelled as sessionx defaults.
- **Copy and clipboard:** tmux-yank provides `Ctrl-a y` for the current command line and `Ctrl-a Y` for the pane working directory; copy mode is entered with the tmux default `Ctrl-a [`; `y`, `Y`, and mouse selection are documented from the installed plugin. OSC 52 forwarding and `copy-pipe-and-cancel` explain why the copy action exits copy mode.
- **Persistence:** tmux-resurrect provides `Ctrl-a Ctrl-s` save and `Ctrl-a Ctrl-r` restore; continuum auto-restores at tmux server start and saves in the background; pane contents are captured. The `Ctrl-a r` reload shortcut is kept visibly separate from `Ctrl-a Ctrl-r` restore.
- **Plugin maintenance:** TPM's `Ctrl-a I` installs and `Ctrl-a U` updates plugins. The page can name the installed plugin set without turning plugin configuration into a shortcut table.
- **Status cues:** decode the bottom strip: blue active-window dot, amber activity dot, `PREFIX` while the prefix is pending, `COPY` in copy mode, session name otherwise, optional git status at 80+ columns, and blue clock.

## Design plan

**Typographic thesis:** a personal terminal reference should feel like a calm instrument panel: stable mono key shapes and numerals make sequences recognisable at a glance, while a restrained reading face keeps explanations from becoming code noise.

**Palette:** charcoal foundation `#141719`; message surface `#1b1e20`; tool/index surface `#202427`; fog text `#d7d9d8`; mist focus blue `#78accf`; amber status `#d2a56d`. Use teal and violet only for small source/status distinctions, not large fills.

**Type:** embed the inspected Commit Mono variable font for keys, commands, labels, and the filter; use the inspected Atkinson Hyperlegible Next variable font for explanatory prose, each with a compatible fallback. Keep the title modest rather than oversized, set shortcut rows in a readable mono size, and use sentence case throughout. Proof `Ctrl-a Ctrl-r`, `Alt-Backspace`, `Ctrl-u/Ctrl-d`, and the longest sessionx descriptions at 390px.

**Layout:** a slim index rail sits beside a single main reading column on wide screens; the rail contains the title, filter, and anchored section links, then moves above the content on narrow screens. Shortcut groups use ruled rows with an action, key sequence, and concise note instead of identical cards.

```text
┌──────────────────────┬──────────────────────────────────────────┐
│ Tmux                 │ Ctrl-a is the prefix                     │
│ [ filter shortcuts ] │ Everyday                                 │
│                      │  Action             Keys       Note       │
│ Everyday             │  Reload config      Ctrl-a r    ...       │
│ Panes                │  Last window        Ctrl-a Space ...      │
│ Windows              │ Panes                                    │
│ Sessions             │  ...                                      │
│ Copy & clipboard     │                                            │
│ Persistence          │                                            │
└──────────────────────┴──────────────────────────────────────────┘
```

**Principles:** let the prefix be the memorable visual anchor; preserve terminal-like hierarchy through alignment and rules; reserve colour for focus, mode, activity, and source; keep the filter helpful but visually quiet; make every interactive state keyboard-visible and usable without JavaScript failure.

## Files to modify

- `desktop-tmux-cheatsheet.html` — new standalone deliverable at the repository root.
- `plans/tmux-cheatsheet.md` — this implementation plan.
- `design/decisions.md` — settled design-grill decisions for this deliverable.

## Reuse

- Source of truth: `/Users/sudakshsoti/.tmux.conf`.
- Visual constraints: `design/decisions.md`.
- Design guidance: `frontend-design`, `design-typography`, and `design-grill` skill instructions.
- Font evidence: supplied `CommitMono-SudakshV143/license.txt` and `Atkinson_Hyperlegible_Next/OFL.txt`, both identifying SIL Open Font License 1.1; supplied WOFF2/TTF files are 88 KB and 112 KB respectively.

## Steps

- [x] Settle audience, scope, output path, and visual direction.
- [x] Settle density, page structure, filter behaviour, and font portability.
- [x] Translate the config into a reviewed shortcut/content inventory, separating custom bindings from clearly labelled tmux/plugin defaults where useful. Include the sessionx fzf command bar, `prefix + Ctrl-s`/`Ctrl-r` persistence actions, and tmux-yank's `prefix + y`/`Y` plus copy-mode actions.
- [x] Confirm the embedded font candidate and final visual tokens: Commit Mono for keys, Atkinson Hyperlegible Next for prose, using the existing Kohra palette.
- [x] Build the self-contained responsive HTML with inline styles and minimal interaction.
- [x] Render and inspect the result at 390, 900, and 1440 CSS pixels; skipped at the user's request for manual inspection.
- [x] Re-check the final inventory against `/Users/sudakshsoti/.tmux.conf` and run lightweight HTML validation.

## Verification

- Open the file directly in a browser without a network connection.
- Check all displayed shortcuts against `/Users/sudakshsoti/.tmux.conf`, including sessionx's fzf header actions and the status-line mode cues.
- Manual inspection remains for responsive layout at 390, 900, and 1440 CSS pixels; static checks cover keyboard focus selectors, reduced-motion rules, and print styles.
- Confirm no external fonts, scripts, stylesheets, images, or network requests are required.
