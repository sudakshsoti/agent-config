---
name: peer-review
description: "Use for a cross-lineage adversarial review of an engineering plan another agent wrote, or when `/peer-review` is requested. Not for your own plan (self-review), frontend code (maintainability-review), or implementation defects (diagnosing-bugs)."
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
model than the one that wrote the plan, so **do not run this prompt inline** —
dispatch the native reviewer role:

- **OMP** — dispatch the `adversary` subagent with the plan file. It pins
  `model: "@adversary"`, which resolves through the `adversary` role in
  `omp/config.yml` to a non-Anthropic model at high effort. The fallback chain
  can end on a Claude model, so report the model that actually ran; if it is a
  Claude model, label the review "same-lineage" rather than cross-lineage.
- **Pi** — dispatch the `reviewer` subagent (read-only, on a second model
  lineage).

On any other surface, run the prompt above in a session that is not on the same
vendor as the plan's author.
