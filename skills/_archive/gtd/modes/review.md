# Weekly Review

Structured as GTD's **Get Clear → Get Current → Get Creative**. Under 10 minutes — move fast, the value is in the habit, not the thoroughness.

## Start

```
find-tasks (projectId: inbox) — inbox count
find-completed-tasks (last 7 days) — wins
find-tasks (filterIdOrName: "Stalled") — stale items
find-tasks (labels: ["waiting"]) — waiting items
find-projects (archivedStatus: active) — project count, for Part 3
find-comments (on the recurring "Weekly Review" task) — last week's stated focus
```

```
Weekly review. ~[N] min based on what's here.

Last 7 days: [X] completed
[Y] in Next Actions, [Z] in inbox, [W] stale

Last week's focus was "[focus]" — how'd that go? [only if a focus was recorded]

Ready?
```

Estimate time: 2 min base + 30s per stale item + 30s per project + 30s per waiting item. Cap at 10 min estimate.

## Get Clear: Inbox to zero (1-2 min)

If inbox isn't already empty, run a fast version of [modes/process.md](process.md) — `now`/`later`/`someday`/`delete` only, no project detection.

## Get Current, Part 1: Wins (1 min)

Show completed items from `find-completed-tasks`. Ask: "Biggest win?"

Acknowledge briefly ("Nice." / "Solid."), move on. Don't dwell.

## Get Current, Part 2: Stuck Items (2-3 min)

**Stale (from the `Stalled` filter — created 14+ days ago, still open):**

If many stale items (8+), offer batch option first:

```
[N] items sitting 14+ days. Want to:
1. Triage one by one
2. Bulk move old ones to Someday (keeps recent)
```

Bulk = batched `update-tasks` moving all matched task IDs to the Someday project.

Otherwise go item by item:

```
[N] stale items:

1. '[item]' ([X] days) — keep/someday/delete?
```

| Response      | Action                  |
| ------------- | ----------------------- |
| `y` or `keep` | Keep as-is              |
| `someday`     | Move to Someday project |
| `delete`      | `delete-object`         |

## Get Current, Part 3: Project Health (1-2 min)

```
find-projects (archivedStatus: active)
get-project-health (per projectId) — health status per project
```

`get-project-health` flags AT_RISK/CRITICAL projects — typically no open next action or a high overdue load. If a project's health data looks missing or stale, `analyze-project-health (projectId)` triggers a fresh assessment (async — it just kicks off the analysis, so re-check with `get-project-health` after, don't expect an immediate result). Skip this part if everything comes back EXCELLENT/ON_TRACK.

```
[N] projects need a next action:

1. '[project]' — next step?
```

User gives next action → `add-tasks` as a sub-task/first task of that project → next project.

If user says "drop it" → archive or delete the project.

## Get Current, Part 4: Waiting Check (1-2 min)

**Waiting items (`@waiting` label), age from `created_at`:**

Skip if none. Otherwise:

```
Waiting on:
• '[item]' — [person] — [X] days
```

For each: "Still waiting? (y/nudge/done)"

| Response | Action                                                                   |
| -------- | ------------------------------------------------------------------------ |
| `y`      | Keep waiting                                                             |
| `nudge`  | `add-tasks` "Follow up with [person] re: [item]" as a normal next action |
| `done`   | `complete-tasks`                                                         |

## Get Creative: Mind Sweep (2 min)

```
Anything floating in your head not captured?
```

`add-tasks` each into Inbox. "Got it." Repeat until "done" or "no." (Every few weeks, if it feels right, widen this to a higher-horizon prompt: "Any projects or goals that need to change — start, stop, or reshape?")

## Close

`complete-tasks` on the recurring "Weekly Review" task (this is what drives next session's days-since-review). Ask for next week's focus, then `add-comments` it on that same task so it surfaces at the next review:

```
Review done.
• [X] completed this week
• [Y] stale triaged
• [Z] projects checked
• [W] waiting reviewed

Focus for next week?
```

Save their answer as a comment. If they don't have one, that's fine — don't push.
