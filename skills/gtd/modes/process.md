# Inbox Processing

## Start

```
find-tasks (projectId: inbox)
```

**Empty:** "Inbox clear." → end

**Has items:** Jump straight in. Show count in first item:

```
1/5: 'Call dentist'
Actionable? (now/later/someday/delete)
```

No preamble. No "Let's process your inbox!" Just the first item.

## The Clarify Tree

For anything not obviously simple, run the canonical GTD clarify question set silently, then ask only what's needed:

1. **Actionable?**
   - No, and never will be → `delete`
   - No, but maybe later → `someday` (moves to Someday project)
   - No, but useful reference → tell the user to save it elsewhere (Todoist isn't a reference filer); delete from Todoist
2. **Yes, actionable. Under 2 minutes?** → do it now, then `complete-tasks`. Don't file a 2-minute task — that's slower than just doing it.
3. **Yes, takes longer. One step or many?**
   - One step → next action: set label(s) + priority (+ `dueString`/`deadlineDate` if genuinely date-bound), move out of Inbox.
   - Many steps → it's a project. Ask for the ONE next action, create it as a **sub-task** of this item (so the project always has a visible next action — no separate "orphan project" check needed later), then decide whether the parent stays a flat task with sub-tasks or gets promoted to its own Todoist project.
4. **Someone else should do it?** → `delegate`, see below.

## Per-Item Flow

**Simple items:**

```
1/5: 'Call dentist'
Actionable? (now/later/someday/delete)

→ "later"
```

Move it, show next item immediately.

**Looks like a project** (multi-step, vague, or big):

```
2/5: 'Plan vacation'
Sounds like a project. What's ONE next action?

→ "research flights"

Got it. Keep 'Plan vacation' as a project with that as the first step? (y/n)
```

On "y": `add-tasks` "Plan vacation" (as a project or parent task), then `add-tasks` "research flights" as its sub-task (`parentId`).

**Has a due date or time clue** ("dentist appointment Tuesday"):

```
3/5: 'Dentist appointment Tuesday'
When? (I'll set the due date)

→ "tuesday 2pm"
```

`update-tasks` with `dueString: "tuesday 2pm"`, move to Next Actions (remove from Inbox project via `projectId` update, drop any inbox-only state).

**Under 2 minutes:**

```
4/5: 'Reply to Sarah — one line'
That's a 2-min task. Doing it now, or file it?

→ "now"
```

On "now": walk them through it, then `complete-tasks`. On anything else, file normally.

## Response Mapping

| User Says                               | Action                                                                          |
| --------------------------------------- | ------------------------------------------------------------------------------- |
| `now`                                   | Set priority `p1`, keep/set `dueString: today`, move out of Inbox               |
| `later`                                 | Move out of Inbox (no date unless date-bound), leave in the Next Actions filter |
| `later home`                            | Same as `later` + add `@home` label                                             |
| `someday`                               | `update-tasks` project → Someday                                                |
| `delete`                                | `delete-object` (task)                                                          |
| `skip`                                  | Next item                                                                       |
| `stop`                                  | End session                                                                     |
| `home` / `office` / `errands` / `calls` | Add matching `@context` label, move to Next Actions                             |
| `delegate [person]`                     | Add `@waiting` label + a comment naming who, move out of Inbox                  |

**Context shortcut:** Any context word combined with a disposition adds the label. "later office" = move out of Inbox + `@office` label.

**Delegate shortcut:** "delegate sarah" = `@waiting` label + `add-comments` "waiting on: Sarah".

## Error Handling

If an MCP call fails mid-session:

1. Retry once
2. If still fails: "Todoist not responding. Check the connection and try again?"
3. Don't lose track of position — remember where you were (Todoist state itself isn't lost; only your position in the walkthrough is)

## Session End

```
Done. 5 processed:
• 3 → Next Actions
• 1 → Someday
• 1 deleted

Anything else?
```
