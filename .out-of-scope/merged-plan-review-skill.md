# Merged plan-review skill

This repo keeps plan review as two separate skills, `self-review` and
`peer-review`, and does not merge them into one plan-review capability.
`maintainability-review` stays a separate, explicitly invoked review of
frontend code.

## Why this is out of scope

The two skills differ in a way that matters more than their shared subject.
Each one answers a different question:

- `self-review` is the in-lineage pass. The agent that wrote a plan critiques
  it against a fixed checklist and then revises it. It is quick, runs in the
  same context and needs no other model.
- `peer-review` is the cross-lineage pass. A hostile reviewer on a different
  model family (the `adversary` agent routed to GLM, not Claude) reviews
  another agent's plan. It reports the model that actually ran and labels a
  Claude fallback as same-lineage, because a second lineage is the point.

A merged skill would have to choose between these modes at runtime. That
choice would either stay hidden (and the cross-lineage guarantee would quietly
weaken), or it would come back as a mode switch, which is just the two skills
again behind one name. The 2026-10-04 skill audit went the other way: it
sharpened `peer-review`'s lineage reporting and added "not for X, use Y"
boundaries between overlapping skills (#79), which makes it clear which one
to pick.

`maintainability-review` is a different kind of review again: it reviews
code, not plans, and runs only when invoked. Folding it into a plan-review
skill would mix up the two kinds of review.

## Prior requests

- #44: "Consolidate plan-review skills: merge self-review and peer-review"
