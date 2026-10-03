---
name: handoff
description: "Use when ending or pausing a session to write a structured handoff of decisions, progress, changes, and next steps for the next session. Not for tracker backlog upkeep (backlog) or personal task capture (gtd)."
disable-model-invocation: true
---

# Handoff

Create structured documents that enable seamless continuity across agent
sessions.

## When to Use

- Ending a work session for the day
- Before taking a break mid-task
- Switching to a different project temporarily
- When you want to capture state for a future session
- Before a context reset you know is coming

## Handoff Process

### Step 1: Ask What Matters

Ask the user:

> "I'll create a handoff document. Is there anything specific you want to make
> sure I capture? (Key decisions, code snippets, context about the problem,
> things you'll forget, etc.)"

### Step 2: Generate Handoff Document

Create a structured document. Fill Current State from the session itself: the
phase, the active task, and the last milestone reached.

```markdown
# Session Handoff: [Brief Description]

**Date:** [YYYY-MM-DD]
**Project:** [project name/path]

## Current State

**Task:** [What we're working on]
**Phase:** [exploration/planning/implementation/debugging/review]
**Progress:** [last milestone reached]

## What We Did

[2-3 sentence summary of the session's work]

## Decisions Made

- **[Decision]** — [Rationale]
- **[Decision]** — [Rationale]

## Code Changes

**Files modified:**

- `path/to/file.ts` — [what and why]
- `path/to/other.ts` — [what and why]

**Key code context:** [Critical snippets or patterns to remember]

## Open Questions

- [ ] [Question needing resolution]
- [ ] [Question needing resolution]

## Blockers / Issues

- [Issue] — [current status]

## Context to Remember

[Important background, constraints, user preferences, domain knowledge - things
that would take time to re-establish]

## Next Steps

1. [ ] [First thing to do next session]
2. [ ] [Second thing]
3. [ ] [Third thing]

## Files to Review on Resume

- `path/to/key/file.ts` — [why it matters]
```

### Step 3: Write the File

Write to: `handoff/[YYYY-MM-DD]-[brief-description].md` under the git root of the
current project, creating `handoff/` if missing. The file stays untracked on
purpose: add `handoff/` to `.git/info/exclude` if it is not already ignored.

Confirm location with user:

> "I'll save this to `handoff/[filename].md`. Want a different
> location?"

## What to Capture

### Always Include

1. **Decisions with reasoning** — The "why" is often more valuable than the
   "what"
2. **Code changes** — File paths, what changed, the intent
3. **Current progress** — Where in the task we stopped
4. **Next steps** — Clear, actionable items to resume with
5. **User context** — Constraints, preferences, domain knowledge they shared

### Include When Relevant

- **Errors encountered** — And how they were (or weren't) resolved
- **Dead ends** — Approaches tried that didn't work (saves re-exploration)
- **Key files** — Files to read to get back up to speed
- **External dependencies** — APIs, services, tools involved

### Skip

- Verbose tool output (file listings, grep results)
- Intermediate reasoning that reached conclusions
- Repeated similar operations
- Information that's obvious from the code

## Format Guidelines

- **Bullet points** — Scannable over narrative
- **File paths** — `src/foo.ts:42` not "that function"
- **Checkboxes for actions** — `- [ ]` for next steps and open questions
- **Specifics** — "Added retry logic to fetchUser()" not "made improvements"

## Quality Check

Before saving, verify:

1. **Could a fresh agent pick up from this?** — Enough context to continue?
2. **Are decisions traceable?** — Clear why things were decided?
3. **Are next steps actionable?** — Know exactly what to do first?
4. **Is code work clear?** — Know which files matter?

## Using a Handoff Document

When starting a new session, the user can:

1. Share the handoff file at session start
2. Say "Resume from this handoff: [paste or path]"
3. Reference it with @ mention if supported

The handoff should let you hit the ground running without lengthy
re-explanation.

## Example Handoff

```markdown
# Session Handoff: Auth System Implementation

**Date:** [YYYY-MM-DD]
**Project:** /path/to/my-api

## Current State

**Task:** Implementing user authentication for the API
**Phase:** Implementation
**Progress:** Basic JWT flow works; refresh tokens not started

## What We Did

Built the core JWT authentication flow including token generation, validation
middleware, and login/logout endpoints. Hit an issue with key rotation that we
resolved by moving to config-based key paths.

## Decisions Made

- **JWT with RS256** — Stateless auth, works with distributed setup
- **Redis for refresh tokens** — Need revocation capability
- **15-min access token expiry** — Balance security/UX for mobile app

## Code Changes

**Files modified:**

- `src/auth/jwt.ts` — Token generation and validation logic
- `src/middleware/auth.ts` — Request authentication middleware
- `src/routes/auth.ts` — Login/logout endpoints
- `config/keys/` — RSA key pair storage

**Key code context:** Token validation uses RS256. Keys loaded from
`config/keys/` based on NODE_ENV.

## Open Questions

- [ ] Automatic vs opt-in refresh token rotation?
- [ ] Rate limit for login attempts? (User mentioned 10k DAU)

## Context to Remember

- Client is a mobile app - tokens need offline capability
- User has 10k daily active users - scale matters
- Using PostgreSQL for user storage
- User prefers explicit error messages over generic ones

## Next Steps

1. [ ] Implement `/auth/refresh` endpoint
2. [ ] Add rate limiting to `/auth/login`
3. [ ] Write tests for token expiry edge cases
4. [ ] Update API docs with auth flow

## Files to Review on Resume

- `src/auth/jwt.ts` — Core token logic
- `src/routes/auth.ts` — Current endpoint implementation
```

## Key Reminders

- Ask what matters to the user before generating
- Decisions need reasoning — capture the "why"
- File paths anchor the work — always include them
- Next steps should be immediately actionable
- Better slightly longer and useful than short and vague
