---
name: peer-review
description: "Use when an engineering plan needs an adversarial, cross-lineage review of assumptions, blind spots, over-engineering, alternatives, and ship/fix/rethink risk. It reviews another agent’s plan; use self-review for the in-lineage pass and diagnosing-bugs for implementation defects."
user-invocable: true
---

# Peer-review

Adversarially review the engineering plan in scope — the plan just proposed in
this session, or the text the user pasted / pointed you at. It was written by
another agent (ideally a different model). You did not write it and owe it no
loyalty. Find what it missed. Do not praise or restate it.

1. Unstated assumptions, and what breaks if each is false.
2. Blind spots that genuinely apply: auth, race conditions, migration and
   rollback safety, error handling, tests, data loss.
3. Over-engineering. Give the simpler version.
4. Steelman one different approach. When does it win?
5. Verdict: ship / fix / rethink, then the top three changes.

Terse. No filler. Specific, with file/line references where they apply. If a
section has nothing real, write "none".

---

This is the cross-lineage pass. Its value comes from being run by a _different_
model than the one that wrote the plan.

In omp, do not run this prompt yourself — dispatch the `adversary` subagent with
the plan file. It pins `model: "@adversary"`, which resolves through the
`adversary` role in `omp/config.yml` to GPT-5.6 Sol at high effort, and whose
fallback chain contains no Anthropic model. Running it inline would review a
Claude plan with Claude.

On any other surface, run the prompt above in a session that is not on the same
vendor as the plan's author.

The in-house equivalent — Claude reviewing its own plan via the `plan-critic`
subagent — is the separate `self-review` skill, and is deliberately in-lineage.
