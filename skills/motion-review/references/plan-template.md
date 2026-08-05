# Motion implementation plan template

Every plan written by `motion-review audit` follows this structure. The
executor may have zero context from the review, so the plan must contain every
necessary detail. Do not refer to “the audit above” or an earlier discussion.

```markdown
# NNN — <Short imperative title>

- **Status**: TODO
- **Commit**: <output of `git rev-parse --short HEAD` when this plan was written>
- **Severity**: HIGH | MEDIUM | LOW
- **Category**: <audit category>
- **Estimated scope**: <n files, rough size>

## Problem

What is wrong, where, and why it affects the product's feel. Cite each location
as `path/to/file.tsx:123` and include the current code verbatim:

```css
/* src/components/dropdown.css:14 — current */
.dropdown { transition: all 400ms ease-in; }
```

## Target

State the exact end result. Spell out curves, durations, spring configuration
and media queries. Never say only “use a nicer easing”.

```css
/* target */
.dropdown {
  transition: transform 200ms var(--ease-out), opacity 200ms var(--ease-out);
  transform-origin: var(--transform-origin);
}
```

## Repo conventions to follow

State how this codebase already handles tokens, file placement and props. Give
one correct `file:line` exemplar for the executor to follow.

## Steps

1. <One concrete edit per step: file, change, and resulting code.>
2. …

## Boundaries

- Do not touch <out-of-scope files or components>.
- Do not change markup or structure unless a step explicitly says otherwise.
- Do not add dependencies.
- If the code has drifted from the commit stamp, stop and report instead of
  improvising.

## Verification

- **Mechanical**: <exact typecheck, lint and build commands, with expected result>.
- **Feel check**: run <interaction> and confirm:
  - <observable interaction result>;
  - <interruption or retargeting result>;
  - in DevTools at 10% playback, <timing/origin detail>;
  - with reduced motion enabled, movement is reduced while essential feedback
    remains.
- **Done when**: <machine- or eye-checkable completion criteria>.
```

## Notes for the plan author

- Create one plan per finding unless the findings share every file and the same
  fix pattern.
- Pull exact values from the shared motion standards and existing project tokens;
  do not approximate from memory.
- A feel check is required. Motion can be mechanically correct and still feel
  wrong.
- Update `plans/README.md` with the plan number, title, severity, status,
  recommended execution order and dependencies.
