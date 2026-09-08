---
name: self-review
description: "Use immediately after proposing an engineering plan or when `/self-review` is requested; have the plan-critic identify omissions and revise the plan to address every point. It is the in-lineage review stage; use peer-review for an adversarial review by another model lineage."
user-invocable: true
---

# Self-review

Use the plan-critic subagent to review the plan you just proposed.

Then revise the plan to address every point it raised. For any point you reject,
give a one-line reason. Show what changed, not the whole plan again.

Do not hand this to the cross-lineage reviewer yet; the user runs that separately
— the `peer-review` skill (`/peer-review`), which in omp dispatches the
`adversary` subagent on a non-Anthropic model.
