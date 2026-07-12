# Todoist GTD Setup

The recommended structure this skill operates on, how to create it, and the Todoist MCP tool gotchas that matter for GTD flows. Read once per session before the first Todoist write, or whenever first-run setup runs.

## Structure

| GTD concept | Todoist structure |
|---|---|
| Inbox | Native Todoist Inbox project |
| Next Actions | **Filter**, not a project — see below |
| Waiting For | `@waiting` label |
| Someday/Maybe | **Someday** project |
| Projects (multi-step outcomes) | Todoist project (big) or a parent task with sub-tasks (small). First sub-task/task = the next action. |
| Context | Label: `@home`, `@office`, `@errands`, `@calls`, `@computer`, `@online` |
| Energy/time | Label: `@quick` (<15 min), `@deep`, `@low_energy` |
| Today's focus | Priority `p1` and/or `dueString: today` |
| Hard deadline | `deadlineDate` (ISO `YYYY-MM-DD`) — separate from due date |
| Review cadence | Recurring task **"Weekly Review"**, `dueString: "every Sunday"` |

## First-run auto-create checklist

Check before creating (idempotent — never duplicate):

1. **Labels** (`find-labels`, then `add-labels` for any missing): `home`, `office`, `errands`, `calls`, `computer`, `online`, `waiting`, `quick`, `deep`, `low_energy`.
2. **Someday project** (`find-projects`, then `add-projects` if missing): name `Someday`.
3. **Filters** (`find-filters`, then `add-filters` for any missing):
   - `Next Actions` → query: `!#Inbox & !@waiting & !##Someday & (no date | today | overdue)`
   - `Waiting For` → query: `@waiting`
   - `Quick Wins` → query: `@quick & !@waiting & (no date | today | overdue)`
   - `Stalled` → query: `created before: -14 days & !@waiting & !##Someday`
   After creating each filter, sanity-check it with one `find-tasks (filterIdOrName: ...)` call — if Todoist rejects the query syntax, adjust and retry rather than leaving a broken filter in place.
4. **Recurring review task** (`find-tasks (searchText: "Weekly Review")`, then `add-tasks` if missing): content `"Weekly Review"`, `dueString: "every Sunday"`.

Show the user what's about to be created before creating it; skip anything that already exists.

## MCP tool gotchas

- **Priority strings, not numbers:** `p1`–`p4`, where `p1` is highest urgency and `p4` is the default/lowest. This is the inverse of Apple Reminders' old 0/1/5/9 scheme — don't port that mental model over.
- **`dueString` vs `dueDate` vs `deadlineDate`:** `dueString` takes natural language ("tomorrow", "every monday", "next week") and is preferred for anything with recurrence or a time. `dueDate` is a specific floating `YYYY-MM-DD` with no parsing. `deadlineDate` (ISO) is the separate hard-deadline field — never conflate it with the due date.
- **Reschedule vs. update for recurring tasks:** use `reschedule-tasks` to move a recurring task's next occurrence — it preserves the recurrence rule. `update-tasks` with a new `dueString` can silently destroy the recurrence and turn a repeating task into a one-off. Only use `update-tasks` on a recurring task when you intend to change the rule itself.
- **`complete-tasks` on a recurring task rolls it forward** rather than closing it permanently — this is what the weekly review relies on to reset days-since-review.
- **Labels are referenced by name**, not ID, in every tool that takes a `labels` array.
- **`duration`/`durationUnit`** must be supplied together (`minute` or `day`).
- **No per-task "last modified" field.** Staleness is approximated with `created before: -N days` in a filter, not a true last-touched timestamp. `analyze-project-health`/`get-project-health` are the better signal for whether a *project* is stalled.
- **Batch, don't loop:** `add-tasks`, `update-tasks`, `complete-tasks` all accept arrays — pass every item in one call instead of one call per task.
- **`get-overview`** is the cheap orientation call (project/today/upcoming structure in one shot) — prefer it over several `find-*` calls when you just need the lay of the land.
