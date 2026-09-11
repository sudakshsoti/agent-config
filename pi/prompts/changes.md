---
description: Review the current diff and its visual proof without changing files
argument-hint: "[scope]"
---

Review the current changes${@:+ within this scope: $@}.

This command is read-only unless I explicitly ask for a repair.

1. Inspect the relevant Git diff and identify the user-visible effect before implementation details.
2. For visual changes, inspect the supplied or discoverable screenshots at the viewports that matter. Do not treat source review as visual proof.
3. If screenshots, a runnable app, a representative state, or the required viewport are missing, mark the visual result as unverified and name exactly what is needed.
4. Check for conflict with `design/decisions.md`, existing tokens, comparable screens, responsive behaviour, accessibility, non-happy-path states, and unintended scope.
5. Use `Critic` for screenshot judgement when visual proof exists. Use the technical `reviewer` only when the diff carries meaningful engineering risk.

Return, in this order:

- **What changed for the user**
- **Visual verdict** — `ship`, `fix`, or `unverified`
- **Evidence** — screenshot paths and checks inspected
- **Risks or regressions**
- **Changed files**
- **Next action**

Do not edit, repair, install, commit, or push from this command unless I ask for that action after the review.
