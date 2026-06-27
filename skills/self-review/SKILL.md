---
name: self-review
description: Self-review the engineering plan you just proposed via the plan-critic subagent, then revise it to address every point. Use right after proposing a plan in plan mode, or when the user types /self-review. Stage 1 of the two-stage plan-review pipeline — the cheap in-house filter before the cross-lineage `rev` pass.
user-invocable: true
---

# Self-review

Use the plan-critic subagent to review the plan you just proposed.

Then revise the plan to address every point it raised. For any point you reject,
give a one-line reason. Show what changed, not the whole plan again.

Do not hand this to the cross-lineage reviewer yet; the user runs that separately
— the `peer-review` skill (`/peer-review`, also available in Codex/Gemini) or the
`rev` / `rev-hard` terminal aliases.
