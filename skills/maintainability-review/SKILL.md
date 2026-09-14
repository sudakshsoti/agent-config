---
name: maintainability-review
description: "Review AI-generated frontend code for human maintainability across duplication, abstractions, naming, structure, silent failures, and cross-session drift."
user-invocable: true
disable-model-invocation: true
---

# Maintainability Review

AI-written code tends to work on the first pass and still be a liability six months later: duplicated logic, abstractions built for a case that happens once, patterns that drift between files written in different sessions. This skill catches that class of problem — not bugs, not security holes, just human maintainability.

## Pick a mode first

Detect from context; if genuinely ambiguous, ask.

| Situation                                               | Mode               |
| ------------------------------------------------------- | ------------------ |
| Reviewing a change just made, or before committing      | **diff** (default) |
| Periodic check-in on a repo you actively work in        | **audit**          |
| Haven't opened this repo in weeks, unsure how bad it is | **triage**         |

Cues: just wrote code → diff; "how's the codebase doing" → audit; "haven't touched this in a while" → triage.

## Before flagging anything (all modes)

- **Read for intent first.** Understand what the code is trying to do before deciding whether _how_ it does it is a problem.
- **Cross-check the repo before calling something duplication.** Grep for similar existing logic (function names, sibling utility files, component patterns) before saying "extract this". If a match exists elsewhere → flag as cross-file duplication and name the other location. If not → only flag duplication _within_ the current scope.
- **Check consistency with local conventions.** New code that works but doesn't match the surrounding error-handling or naming style is itself a maintainability cost.
- Run the checklist in `references/checklist.md` (DRY, over-engineering, structure, naming, comments, error handling, state, dependencies). Skip sections that don't apply. Don't manufacture findings to look thorough — a clean review gets a short report.

## Modes

### diff (default)

Review only what changed or the files named, not the whole repo. Scope it with `git diff --name-only` (uncommitted), `git diff --name-only <base>..HEAD` (a branch), or `git status --short` (pre-commit). If the change touches 15+ files, say so and offer to focus on the riskiest few first. Report with the severity format below.

### audit

Whole-repo health check; assume the repo is mostly fine and you're hunting drift, not doing first-time triage.

1. Get the file list; skip generated/vendor code (`node_modules`, `dist`, `build`, lockfiles, `*.gen.*`).
2. Look for **architectural drift across files**, not per-file nits: 2–3 different ways of doing the same thing (multiple date formatters, multiple API-call patterns, multiple state approaches for similar problems). This is the failure mode unique to code written across many sessions — each file looks fine, the whole has no consistent pattern.
3. Spot-check naming, folder structure, and whether newer files follow older established patterns.
4. Check for dead code and unused exports repo-wide.

Report as a short narrative + severity list organized **by theme** ("3 different toast patterns in use"), not by file — the value is the pattern, not any single instance.

### triage

For a repo weeks without review. The first pass is a **map of where the damage is concentrated**, not a line-by-line dump.

1. Build a hotspot list before reading in detail:
   `git log --format=format: --name-only --since="90 days ago" | sort | uniq -c | sort -rg | head -30`
   (widen the window to match the gap). Often-edited files are where debt compounds; barely-touched ones are lower priority even if messy.
2. Skim the top 10–15 hotspots against the checklist at lighter depth — a severity tag per file, not every issue in each.
3. Separately, one repo-wide pass for architectural drift (same as audit step 2) — it compounds silently and won't show in a hotspot list.
4. Report as a triage table:

   | File                | Change freq    | Severity | Core issue (one line)                                |
   | ------------------- | -------------- | -------- | ---------------------------------------------------- |
   | `src/api/orders.ts` | 34 commits/90d | 🔴       | 3 duplicate fetch patterns, no shared error handling |

   Follow with a short "start here" — the top 2–3 rows. Offer to go deeper on any file after the user sees the map, rather than front-loading full detail on all 15.

## Do not report

- Anything a linter/formatter/type-checker already catches (assume CI handles it).
- Style preferences with no maintainability cost (arrow vs `function` keyword, tabs vs spaces).
- Test-only code or fixtures that intentionally break production conventions.
- One-off scripts explicitly framed as throwaway.
- Anything flagged as an intentional tradeoff in a comment or commit message — note it, don't re-litigate.

If everything found is a nit, lead with "No blocking issues" rather than padding.

## Severity format

For **diff mode**, group findings by severity, `file:line` where possible, each with a one-line fix direction. (audit and triage use the by-theme and table formats specified above.)

- **🔴 Blocking** — will actively cause pain for the next person (duplicated business logic, no error handling on a flow that needs it, one component doing three unrelated jobs).
- **🟡 Worth fixing** — real cost, not urgent (naming that needs a second read, a helper that should be extracted, minor over-engineering).
- **🟢 Nit** — small, safe to skip under time pressure.

Close with a one-line verdict: would this survive a new engineer opening it cold in six months — **yes / mostly / no** — and why.

## References

- `references/checklist.md` — the eight-category maintainability checklist. Load when running any mode.
