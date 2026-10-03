---
name: vibe
description: "Use for any interface change (tweak, new screen, risky UI/data change) to choose process depth and build-review; not for non-UI work or design critique alone."
---

# Vibe

Vibe is a workflow, not an aesthetic. It decides how much process an interface task needs and holds the build to a rendered, reviewed result. Visual language, tokens and review thresholds come from `design-interface`, `design-visual-system`, `design-typography` and `ux-writing`. Do not duplicate their guidance here.

## 1. Pick the route

1. **Quick tweak.** One component or style area; none of the Builder's quick-tweak escalations (`builder` agent) apply. Inspect the current screen, tokens and nearest comparable pattern, then build without an approval pause unless the request conflicts with a `[stated]` decision (a settled line in `design/decisions.md`, tagged as in `design-grill`).
2. **Shape first.** A new screen, changed workflow, unclear hierarchy or competing direction. If `design/decisions.md` has no settled direction, run `design-grill` in the main session. Then run the Plan role and present the single decision that changes the work. Wait for approval before building. A new standalone page is always this route; use the active design skills directly.
3. **Risky change.** Authentication, persistent data, dependencies, destructive operations, migrations or broad architecture. Run the Plan role, explain the impact and rollback shape, and wait for explicit approval before implementation.

## 2. Roles and the hand-off contract

Three roles. Each agent file defines its own return shape; the next role starts from that, not from the conversation.

- **Plan** returns confirmed decisions, exact files, target viewports, required states, checks to run and unresolved questions.
- **Builder** receives that hand-off or an explicitly bounded quick tweak. See the `builder` agent for its boundary and return.
- **Critic** receives the screenshots, the project-local audit output if one exists and the relevant implementation. Its rules and return shape (prioritised findings, named coverage, `ship` or `fix`) live in the critic agent files (`omp/agents/critic.md`, `pi/agents/Critic.md`) because it runs without loading this skill. Do not restate them in the dispatch.

How the roles run depends on the harness:

| Harness | Plan | Builder | Critic |
| --- | --- | --- | --- |
| Pi | `Plan` subagent | `builder` subagent | `Critic` subagent with images attached |
| OMP | `plan` subagent via `task` | `builder` subagent | `critic` subagent given the absolute screenshot paths to read |

When a role runs in the main session, still write its output in the role's shape before moving on. The Critic must run in a fresh context: a session reviewing its own build approves it. If no image-capable reviewer exists, report "Critic pass unavailable" and do not claim visual quality.

## 3. Rendered or not done

A visual change is not complete until its rendered result has been inspected. If no runnable app, URL, representative state or browser path exists, name the blocker and do not claim visual success. When responsiveness can change, inspect both narrow and wide viewports. Use a project-local audit when one exists.

If the Critic returns `fix`, dispatch the Builder for one focused repair, capture fresh screenshots, re-run the project-local audit if one exists and run the Critic once more. If the second verdict is still `fix`, stop and ask the user.

## 4. Final report

Finish with user-visible changes, screenshot paths, audit results, the Critic's verdict, changed files and any unresolved risk.
