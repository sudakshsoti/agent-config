---
name: self-review
description: "Use immediately after proposing a non-trivial engineering plan or when `/self-review` is requested; critique your own plan against a fixed checklist and revise it to address every point. Not for trivial single-step plans, code diffs (code-review), an adversarial pass by another model lineage (peer-review), or frontend code (maintainability-review)."
user-invocable: true
---

# Self-review

Critique the plan you just proposed, then revise it, in the current session.

Answer every checklist item against your own plan, or write "none":

1. Unstated assumptions, and what breaks if each is false.
2. Internal inconsistencies: where the plan contradicts itself or a stated
   requirement.
3. Blind spots that genuinely apply: auth, race conditions, migration and
   rollback, error handling, idempotency, tests, data loss, observability.
4. Over-engineering: where it exceeds the problem. Give the simpler version.
5. Verdict: ship / fix / rethink, then the top three changes.

Then revise the plan to address every point. For any point you reject, give a
one-line reason. Show what changed, not the whole plan again.

## Dispatch

If the plan touches more than 5 files or spans several workstreams, dispatch a
subagent with the checklist above and **no model override**, so it stays
in-lineage:

- OMP: a `task` subagent on the session model.
- Pi: the `general-purpose` agent with its default model.

Do not pin a cross-lineage model here.
