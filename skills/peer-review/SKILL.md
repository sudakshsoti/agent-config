---
name: peer-review
description: Adversarially review an engineering plan (or design, approach, RFC) written by another agent — the cross-lineage hostile pass. Use when the user types /peer-review, says "rev this", "peer review this plan", "red-team this", "poke holes in this", "review this plan from another model", or pastes a plan and asks what it missed. Returns assumptions, blind spots, over-engineering, a steelmanned alternative, and a ship/fix/rethink verdict. Surface-agnostic — runs in Codex, Gemini, or Claude. Stage 2 of the two-stage plan-review pipeline — the cross-lineage counterpart to the in-house self-review.
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

This is the cross-lineage pass. Its value comes from being run by a *different*
model than the one that wrote the plan — run it in Codex or Gemini on a plan
Claude proposed, or vice versa. The in-house equivalent (Claude reviewing its
own plan via a subagent) is the separate `self-review` skill; the terminal
`rev` / `rev-hard` aliases are the clipboard-piped version of this same prompt.
