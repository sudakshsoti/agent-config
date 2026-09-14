# Maintainability checklist

The eight categories a maintainability review walks. Skip any that don't apply.

## DRY — duplication

- Same _logic_ (not just similar-looking code) repeated in 2+ places instead of extracted
- Copy-pasted components/functions differing only by a parameter — should be one parameterized version
- Repeated API-call / data-fetching logic instead of a shared client / hook / service layer
- Magic numbers or strings repeated across files instead of named constants
- Duplicate validation between frontend and backend that could share a schema (e.g. zod)

## Over-engineering (the AI-assisted smell)

- Abstraction built for a case that only happens once
- A config/plugin system for something with one caller
- Custom caching, memoization, or perf optimization with no evidence it's needed
- Generic/flexible types where a concrete one would be clearer and just as correct
- A new dependency pulled in for something that's 10 lines of hand-rolled code

## Structure and separation of concerns

- Components/functions doing more than one job (fetch + transform + render in one place)
- Business logic buried in JSX/UI instead of a hook or utility
- Files that have quietly grown past a reasonable size for what they do
- Folder/file organization that doesn't match how a human would look for it later

## Naming and readability

- Names describing implementation, not intent (`data2`, `handleClick3`, `tempFlag`)
- Inconsistent casing / naming convention within the same file or module
- Booleans that don't read naturally in an `if` (`if (!status)` where `status` isn't obviously negatable)
- Names that only make sense with tribal knowledge — should be self-evident from the code alone

## Comments

- Comments restating what the code already says (delete — the code should say it)
- Missing comment where a non-obvious _why_ decision was made (keep only this kind)
- Dead / commented-out code left in
- TODOs with no owner or context, dropped and forgotten

## Error handling and edge cases

- Empty or swallowed catch blocks
- Inconsistent handling for structurally similar operations (one API call handles failure, its sibling doesn't)
- Missing loading / error / empty states for UI that fetches data
- Unhandled null/undefined on data from an API or user input

## State management (frontend-specific)

- State lifted to a parent/context when only one component needs it, or kept local when siblings need it too
- Derived values stored in state instead of computed at render time
- Prop drilling three+ levels where context or composition reads cleaner
- Redundant state duplicating what's already derivable from existing state or props

## Dependencies and imports

- Unused imports or variables left after edits
- New dependency added for trivial functionality
- Import cycles or barrel files adding indirection with no real payoff
