---
name: self-review
description: "Use immediately after proposing an engineering plan or when `/self-review` is requested; critique your own plan against a fixed checklist and revise it to address every point. It is the in-lineage review stage; use peer-review for an adversarial review by another model lineage."
user-invocable: true
---

# Self-review

Critique the plan you just proposed, then revise it. This is the **in-lineage**
pass: it is allowed to be the same model and the same context, and its job is to
catch what you can catch yourself before anyone else reads the plan.

Work the checklist against your own plan:

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

Run the checklist in the current session. That is the point of this stage — a
fresh context would duplicate `peer-review`.

If the plan is large enough to want a second reader, dispatch a subagent with the
checklist above and **no model override**, so it stays in-lineage:

- OMP: a `task` subagent on the session model.
- Pi: the `general-purpose` agent with its default model.

Do not pin a cross-lineage model here. Reviewing a plan on a different vendor is
the separate `peer-review` skill (`/peer-review`).
