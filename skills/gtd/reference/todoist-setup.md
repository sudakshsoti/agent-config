# Todoist GTD Setup

**This skill adapts to your Todoist — it does not impose a taxonomy.** At session start, *map the existing structure* and build every filter query from what's actually there. Only create missing pieces, and match the conventions already in use. The default tables below describe a *recommended* fresh-account layout — they are not an assumption to force onto an account that already organizes things differently. Read once per session before the first Todoist write.

## Map existing structure first (before any create)

Run before First-Run Setup, before building filters, before any metric read:

```
get-overview
find-projects (archivedStatus: active)
find-labels
```

For each GTD concept, detect whether it exists as a **project**, a **label**, or **neither**, and record the query token to use:

| GTD concept | Look for | Token if PROJECT | Token if LABEL |
|---|---|---|---|
| Waiting For | project "Waiting For" **or** label "waiting" | `##Waiting For` | `@waiting` |
| Someday/Maybe | project "Someday / Maybe" or "Someday" **or** a someday label | `##Someday / Maybe` | `@someday` |
| Parking projects | any holding-pen project (e.g. "Watchlist Inbox") | `##Watchlist Inbox` (one token per project) | — |
| Audit Log | project named per `AUDIT_LOG_PROJECT` (default "Audit Log") | — | — |
| Contexts | labels (whatever the user actually uses) | — | `@Calls`, `@Work`, … |

**Rule:** if a concept already exists as a project, do NOT also create a label for it (and vice versa). E.g. if "Waiting For" is already a project, use `##Waiting For` everywhere and never create an `@waiting` label. Match what's there.

From the detected tokens, define the variables the filter templates use:

- `WAITING` = the Waiting For token (`##Waiting For` or `@waiting`)
- `SOMEDAY` = the Someday token (`##Someday / Maybe` or `@someday`)
- `PARKING` = the extensible exclusion list = Someday project + every user-designated parking project (Watchlist Inbox, etc.). See below.
- `QUICK` = the user's short-task / low-effort context label (e.g. `@10 Min`, or `@quick` on a default account)

## Parking projects (holding pens)

A **parking project** is any project whose tasks must be excluded from *every* active-task view — Next Actions, Stalled, inbox counts, coach candidates, overdue health. It's a named, extensible list, not a single hardcoded "Someday":

- Always includes the Someday/Maybe project.
- Includes any user-designated parking project — e.g. **Watchlist Inbox**, a media parking lot that would otherwise flood Next Actions with dozens of non-actionable items.
- The user can name more at any time; treat `PARKING` as configurable and append each as `& !##<project name>` to active-task filters.

Waiting For is excluded from active-task/no-date views too (a delegated item isn't a next action), so the practical exclusion set for "what's actionable right now" is `PARKING` **plus** `WAITING`.

## Structure (default recommendation)

For a fresh account. On an existing account, detect first (above) and adapt — several of these can be a project *or* a label:

| GTD concept | Todoist structure |
|---|---|
| Inbox | Native Todoist Inbox project |
| Next Actions | **Filter**, not a project — see below |
| Waiting For | Project `##Waiting For` **or** label `@waiting` — detect which; don't create both |
| Someday/Maybe | Project (`##Someday / Maybe` / `##Someday`) **or** label — detect which |
| Parking projects | User's holding-pen projects (e.g. `##Watchlist Inbox`) — excluded from all active views |
| Projects (multi-step outcomes) | Todoist project (big) or a parent task with sub-tasks (small). First sub-task/task = the next action. |
| Context | Label — use the user's actual context labels (e.g. `@Calls`, `@Work`, `@Health`, `@Errands`, `@Online`, `@Computer`, `@Deep-Work`, `@10 Min`). On a bare account the defaults are `@home`, `@office`, `@errands`, `@calls`, `@computer`, `@online`. |
| Energy/time | Label: a short-task label (`@10 Min` / `@quick`), plus `@Deep-Work` / `@low_energy` |
| Today's focus | Priority `p1` and/or `dueString: today` |
| Hard deadline | `deadlineDate` (ISO `YYYY-MM-DD`) — separate from due date |
| Review cadence | Recurring task **"Weekly Review"**, `dueString: "every Sunday"` |
| Audit trail | Project `AUDIT_LOG_PROJECT` (default "Audit Log") of dated review summaries — see below |

## First-run / gap-fill checklist

Detect first (map step above), then create **only what's missing**, matching existing convention. Never build parallel structure alongside what the user already has. Show the user what's about to be created before creating it; skip anything that already exists.

1. **Contexts** (`find-labels`, then `add-labels` for any the user wants): reuse the user's existing context labels — don't rename them to the defaults.
2. **Waiting For:** if neither a project nor a label exists, create the user's preferred form (default: label `waiting`). If a "Waiting For" project already exists, use it — do NOT also add an `@waiting` label.
3. **Someday/Maybe:** same — reuse the existing project/label; create only if absent.
4. **Parking projects:** identify them (Someday + any the user designates). Don't auto-create beyond Someday.
5. **Filters** (`find-filters`, then `add-filters` for any missing) — build the query from the detected tokens (next section). After creating each, sanity-check with one `find-tasks (filterIdOrName: ...)`; if Todoist rejects the syntax, adjust and retry rather than leaving a broken filter.
6. **Recurring review task** (`find-tasks (searchText: "Weekly Review")`, then `add-tasks` if missing): content `"Weekly Review"`, `dueString: "every Sunday"`.
7. **Audit Log:** detect `AUDIT_LOG_PROJECT`; if missing, **offer** to create it (don't assume).

## Filter queries (build from detected structure)

Templates — substitute the detected tokens, and append one `& !##<name>` per parking project:

```
Next Actions: !#Inbox & !{WAITING} & !{SOMEDAY} & {!##<each parking project>} & (no date | today | overdue)
Waiting For:  {WAITING}
Quick Wins:   {QUICK} & !{WAITING} & !{SOMEDAY} & (no date | today | overdue)
Stalled:      (no date) & !{SOMEDAY} & {!##<each parking project>} & !{WAITING}
```

**Worked example — project-based setup** (Waiting For, Someday / Maybe, and Watchlist Inbox are all *projects*; short-task label is `@10 Min`). These are copy-pasteable into `find-tasks (filterIdOrName)` / `add-filters`:

```
Next Actions: !#Inbox & !##Waiting For & !##Someday / Maybe & !##Watchlist Inbox & (no date | today | overdue)
Waiting For:  ##Waiting For
Quick Wins:   @10 Min & !##Waiting For & !##Someday / Maybe & !##Watchlist Inbox & (no date | today | overdue)
Stalled:      (no date) & !##Someday / Maybe & !##Watchlist Inbox & !##Waiting For
```

## Staleness signal

**`created before: -N days` is the wrong primary stall metric.** Created-date says nothing about whether a task is dropped when tasks are deliberately dated far ahead — it flags future-dated parked items (insurance renewals dated years out, vaccine schedules, Q4 cancellations) as false positives. On a real account it returned ~62 items, almost all correctly parked.

Staleness is now: **actionable tasks with NO due date, sitting outside parking projects** — genuinely untriaged/dropped work. This is the `Stalled` filter above:

```
(no date) & !##Someday / Maybe & !##Watchlist Inbox & !##Waiting For
```

(Substitute your own `SOMEDAY` / parking / `WAITING` tokens.) On the same account this returned ~8, of which most were genuinely dropped — real signal.

Todoist still has **no true last-modified field**, so there's no perfect "last touched" measure. `created before: -N days` can still be a *secondary* curiosity, but never the headline stall number. `analyze-project-health` / `get-project-health` remain the better signal for whether a *project* (vs a task) is stalled.

## Overdue health signal

Overdue is not automatically rot. Most overdue is just "didn't get to it yesterday." Bucket it before treating any of it as a health concern:

- **Overdue today/yesterday** → noise. Ignore — not-yet-done, not stalled.
- **Overdue 7+ days (one-off)** → real. This is the only bucket to surface as a health concern.
- **Recurring, rolled forward** → expected. A recurring med/chore reminder that rolled is NOT a stalled task. Flag it separately (or not at all); never count it toward overdue health.

Queries:

```
Real overdue (one-off, outside parking):  overdue & !recurring & !##Waiting For & !##Someday / Maybe & !##Watchlist Inbox
Recurring rolled (ignore for health):     overdue & recurring
```

From the real-overdue result set, bucket by due date: due ≥ yesterday → noise; due ≤ 7 days ago → surface. (If your Todoist accepts relative offsets in `due before:`, the 7+ bucket is directly `due before: -7 days & !recurring & !##Waiting For & !##Someday / Maybe & !##Watchlist Inbox`.)

## Audit Log convention

`AUDIT_LOG_PROJECT` (default `"Audit Log"`, configurable — change it if the user names the project differently). It holds one dated entry per review so each review has a baseline to compare against instead of starting cold.

- **Detect** at session start (map step). If it doesn't exist, **offer** to create it — don't assume, and don't silently skip the baseline.
- **Review START:** read the most recent entry — the newest dated task in `AUDIT_LOG_PROJECT`, plus its description/comment — as a baseline: completion counts, avoidance areas, task-hygiene numbers. Compare this review against it ("last review you had 12 stale, now 8"). If there are no entries, say "no prior baseline" once and move on.
- **Review END:** write a new dated summary — `add-tasks` a task named with today's date (e.g. `"2026-07-12 review"`) into `AUDIT_LOG_PROJECT`, with the numbers in the description or an `add-comments` comment: completed this week, stale triaged, projects checked, waiting reviewed, notable avoidance areas.

## MCP tool gotchas

- **Priority strings, not numbers:** `p1`–`p4`, where `p1` is highest urgency and `p4` is the default/lowest. This is the inverse of Apple Reminders' old 0/1/5/9 scheme — don't port that mental model over.
- **`dueString` vs `dueDate` vs `deadlineDate`:** `dueString` takes natural language ("tomorrow", "every monday", "next week") and is preferred for anything with recurrence or a time. `dueDate` is a specific floating `YYYY-MM-DD` with no parsing. `deadlineDate` (ISO) is the separate hard-deadline field — never conflate it with the due date.
- **Reschedule vs. update for recurring tasks:** use `reschedule-tasks` to move a recurring task's next occurrence — it preserves the recurrence rule. `update-tasks` with a new `dueString` can silently destroy the recurrence and turn a repeating task into a one-off. Only use `update-tasks` on a recurring task when you intend to change the rule itself.
- **`complete-tasks` on a recurring task rolls it forward** rather than closing it permanently — this is what the weekly review relies on to reset days-since-review, and why a rolled-forward recurring task shows as overdue without being stalled.
- **Labels are referenced by name**, not ID, in every tool that takes a `labels` array.
- **`duration`/`durationUnit`** must be supplied together (`minute` or `day`).
- **No per-task "last modified" field.** Don't approximate staleness with `created before: -N days` as the primary signal (it flags deliberately future-dated items — see Staleness signal above). Use the no-date-outside-parking `Stalled` filter for task staleness, and `analyze-project-health`/`get-project-health` for whether a *project* is stalled.
- **Batch, don't loop:** `add-tasks`, `update-tasks`, `complete-tasks` all accept arrays — pass every item in one call instead of one call per task.
- **`get-overview`** is the cheap orientation call (project/today/upcoming structure in one shot) — prefer it over several `find-*` calls when you just need the lay of the land, and lead the map-structure step with it.
