# Fix the stale Pi footer label

## Root cause

The footer change in `cfb58774` is correct, but Pi never loaded that file.

Pi discovers the global extension at `~/.pi/agent/extensions/operational-footer/index.js`.
That path resolves to `~/dev/agent-config/pi/extensions/operational-footer/index.js`, not to the active temporary worktree.
The canonical checkout's local `feat/ux-pi-flow-infographic` branch diverged from its remote before `cfb58774`, so its working file still contains the fallback `"build"` value and `mode.toUpperCase()` rendering.
The current `fix/pi-footer-live-source` worktree is based on `origin/main`, which also predates the fix.

A fresh import of the installed extension reproduces `BUILD · gpt-5.6-sol · high`.
Rendering the file stored in `cfb58774` produces `gpt-5.6-sol · high` without `BUILD`.
This rules out Pi's module cache as the primary cause.
After the installed file changes, an existing Pi process will still need `/reload` or a restart because auto-discovered extensions are loaded at startup and reload.

## Plan

1. **Create a standalone fix on `fix/pi-footer-live-source`.**
   Inspect all of `cfb58774` before reuse; it also changes `pi/model-ladder.md`, so do not cherry-pick it as an opaque unit.
   Apply the three functional footer changes to this clean branch: remove the retired status lookup, remove that key from the extras exclusion, and render only model plus thinking level.

2. **Add a footer render regression test.**
   Add `scripts/test-operational-footer.mjs` using the minimal Pi context and footer-data stubs from the RCA probe.
   Supply model and thinking values as test inputs, assert that those exact values render, and assert that no mode segment such as `BUILD` or `PLAN` renders.
   Accept an optional source path so the same test can exercise the tracked extension and Pi's installed extension.

3. **Integrate only the standalone fix into the canonical checkout.**
   Before changing `~/dev/agent-config`, record its branch, `HEAD`, full status, and SHA-256 hashes of `.pi/subagents.json` and `ux-first-pi-configuration-plan.html`.
   Confirm that the footer file is not modified there, then cherry-pick the reviewed standalone fix commit onto the current local branch.
   Do not reset, rebase, merge the divergent remote feature branch, switch branches, or overwrite either uncommitted file as part of this repair.

4. **Verify delivery, then reload.**
   Resolve `~/.pi/agent/extensions/operational-footer/index.js` with `realpath` and require the expected canonical-checkout path.
   Compare that installed file with the fixed tracked footer by content hash, then run the render test against the resolved installed path.
   Re-check the canonical branch, unrelated file hashes, and pre-existing status entries; only the intended committed files may differ.
   Run `/reload` or restart Pi, then inspect a wide TUI screenshot as supporting visual evidence.

5. **Document the worktree boundary.**
   Update `pi/model-ladder.md` to say that linked configuration is live only from the canonical checkout targeted by `~/.pi/agent`.
   State that commits made in another worktree do not reach the running Pi installation until integrated into that checkout.

## Acceptance criteria

- The render test fails on the current installed extension with `stale BUILD label is rendered`.
- The same test passes on the fixed branch and on the resolved installed path after integration.
- The installed footer's content hash matches the reviewed fixed footer.
- The canonical checkout's two unrelated file hashes and pre-existing status entries remain unchanged.
- A fresh Pi TUI screenshot contains no `BUILD` or `PLAN` prefix as supporting evidence.
