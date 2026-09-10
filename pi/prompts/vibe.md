---
description: Route interface work through the lightest safe build and screenshot-review flow
argument-hint: "<change>"
---

Complete this interface task: $@

Use the lightest safe route:

1. **Quick tweak** — one component or style area; no dependency, architecture, authentication, navigation, data-model, migration, persistence, or new visual-direction change. Inspect the current screen, tokens, and nearest comparable pattern; then build without an approval pause unless the request conflicts with a `[stated]` decision.
2. **Shape first** — a new screen, changed workflow, unclear hierarchy, or competing direction. If `design/decisions.md` has no settled direction, run `design-grill` in the main session. Then run `Plan` in the foreground and present the single decision that changes the work. Wait for approval before `Builder`.
3. **Risky change** — authentication, persistent data, dependencies, destructive operations, migrations, or broad architecture. Run `Plan`, explain the impact and rollback shape, and wait for explicit approval before implementation.

For interface work, classify the surface and use the relevant existing skills: `design-strategy`, `design-interface`, `design-visual-system`, `design-typography`, or `ux-writing`. Do not duplicate their guidance.

Use this hand-off contract:

- `Plan` returns confirmed decisions, exact files, target viewports, required states, checks, and unresolved questions.
- `Builder` receives that hand-off or an explicitly bounded quick tweak. It returns checks run and absolute screenshot paths for every visual change.
- `Critic` receives screenshots plus the relevant implementation and returns exactly `ship` or `fix`.

A visual change is not complete until its rendered result has been inspected. If no runnable app, URL, representative state, or browser path exists, name the blocker and do not claim visual success. When responsiveness can change, inspect both narrow and wide viewports.

If `Critic` returns `fix`, dispatch `Builder` for one focused repair, capture fresh screenshots, and run `Critic` once more. If the second verdict is still `fix`, stop and ask the user.

Do not install dependencies or change product direction without approval. Follow the repository's existing verification, commit, and push policy. Finish with user-visible changes, screenshot paths, changed files, and any unresolved risk.
