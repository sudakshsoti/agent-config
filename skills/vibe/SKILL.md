---
name: vibe
description: "Route an interface change through the lightest safe build-and-review flow: quick tweak, shape first, or risky change. Plan, build and critique roles run as subagents where the harness has them and sequentially otherwise, with a fresh-context critic on screenshots. Use for any UI task; invoke frontend-artifact for a standalone page."
---

# Vibe

Vibe is a workflow, not an aesthetic. It decides how much process an interface task needs and holds the build to a rendered, reviewed result. Visual language, tokens and review thresholds come from `frontend-artifact` for a standalone page and from `design-interface`, `design-visual-system`, `design-typography` and `ux-writing` inside a product. Do not duplicate their guidance here.

## 1. Pick the route

1. **Quick tweak.** One component or style area; no dependency, architecture, authentication, navigation, data-model, migration, persistence or new visual-direction change. Inspect the current screen, tokens and nearest comparable pattern, then build without an approval pause unless the request conflicts with a `[stated]` decision.
2. **Shape first.** A new screen, changed workflow, unclear hierarchy or competing direction. If `design/decisions.md` has no settled direction, run `design-grill` in the main session. Then run the Plan role and present the single decision that changes the work. Wait for approval before building. A new standalone page is always this route, and its language selection follows `frontend-artifact`'s gate.
3. **Risky change.** Authentication, persistent data, dependencies, destructive operations, migrations or broad architecture. Run the Plan role, explain the impact and rollback shape, and wait for explicit approval before implementation.

## 2. Roles and the hand-off contract

Three roles. Each returns a fixed shape so the next can start without re-reading the conversation.

- **Plan** returns confirmed decisions, exact files, target viewports, required states, checks to run and unresolved questions.
- **Builder** receives that hand-off or an explicitly bounded quick tweak. It returns the checks run, `audit.txt` when the page is standalone, and absolute screenshot paths for every visual change.
- **Critic** receives the screenshots, the audit output and the relevant implementation, and returns the structure in `frontend-artifact/references/critic-prompt.md`: differences from the reference, feature check, generic tells, first useful unit, and exactly `ship` or `fix` with at most five prioritised changes.

How the roles run depends on the harness:

| Harness | Plan | Builder | Critic |
| --- | --- | --- | --- |
| Pi | `Plan` subagent in the foreground | `builder` subagent | `Critic` subagent with images attached |
| OMP | `plan` subagent via `task` | `builder` subagent | `critic` subagent given the absolute screenshot paths to read |

When a role runs in the main session, still write its output in the role's shape before moving on. The Critic must run in a fresh context: a session reviewing its own build approves it. If no image-capable reviewer exists, report "Critic pass unavailable" and do not claim visual quality.

## 3. Rendered or not done

A visual change is not complete until its rendered result has been inspected. If no runnable app, URL, representative state or browser path exists, name the blocker and do not claim visual success. When responsiveness can change, inspect both narrow and wide viewports. For a standalone page, run `frontend-artifact/references/audit.js` before capturing and paste its output to the Critic.

If the Critic returns `fix`, dispatch the Builder for one focused repair, capture fresh screenshots, re-run the audit and run the Critic once more. If the second verdict is still `fix`, stop and ask the user.

## 4. Boundaries

Do not install dependencies or change product direction without approval. Follow the repository's existing verification, commit and push policy. Finish with user-visible changes, screenshot paths, audit results, the Critic's verdict, changed files and any unresolved risk.
