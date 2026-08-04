---
name: discovery-first
description: >-
  When the request is vague, subjective or exploratory, switch to planning and
  discovery before problem-solving. Use when the ask is open-ended ("make this
  better", "clean this up", "what should we do about X"), states a symptom
  rather than a change ("this feels slow", "users get confused here"), is a
  judgement call about quality or taste, or names a goal without naming the
  edit. Inspect the relevant context, restate the likely underlying problem,
  name the unknowns, offer two or three directions with a recommendation, then
  implement. Skip it when the instruction already names the change, or the
  change is small, obvious and reversible.
user-invocable: true
---

# Discovery First

One shift: when the user does not yet know what they want, plan and discover
before solving. Read the relevant context, say what you think the real problem
is, recommend a direction — then write code.

This is a light pass, not a workshop. It should read like a colleague thinking
out loud for a minute. No spec, no phases, no approval gate.

## Recognise the trigger

Enter discovery mode when the request is any of:

- **Open-ended** — "make this nicer", "clean this up", "what should we do here".
- **A symptom, not a change** — "this feels slow", "people miss the save button".
- **Subjective** — quality, taste, naming, tone, "is this any good".
- **Exploratory** — "could we…", "I'm thinking about…", "is X worth doing".
- **A goal with no named edit** — the outcome is stated, the change is not.

Stay in normal mode when the instruction names the change, or the change is
small, obvious and reversible. A discovery pass on a clear request is the
failure mode to avoid — it reads as stalling.

## The pass

First open the files, components or flows the request actually touches. Framing
that isn't grounded in the code is guessing.

Then write, in the user's language — behaviour and outcomes, not internals:

```
**What I think you're after:** <one or two sentences restating the underlying
problem as you now understand it.>

**Unknowns:** <up to 3 things that would change the answer, each with the
assumption you'll run with if it goes unanswered.>

**Directions:**
1. **<name>** — what it does, what it costs.
2. **<name>** — what it does, what it costs.

**I'd go with <n>,** because <reason>.

<At most 1-2 questions, and only if a different answer produces a different
solution. Otherwise: "Say the word and I'll start on <n>.">
```

Then start. You don't need certainty, a spec, or a written plan — just enough
clarity that the first edit is unlikely to be thrown away.

## Rules

- **Look before you frame.** Restating a problem you haven't inspected is noise.
- **Recommend, never hand over a blind menu.** Two or three directions, each
  with its cost, and always a pick.
- **Only ask what changes the answer.** If both answers lead to the same code,
  don't ask — state the assumption and move.
- **Speak in product terms.** What the user sees and does. Implementation detail
  belongs in the trade-off line, not the framing.
- **Don't edit ahead of the direction.** Reading is free; refactors are not.
- **Move on.** Once the direction is clear, implement. Don't reopen the framing.

## Common mistakes

- A questionnaire. Five questions up front is a survey — pick the one that
  actually forks the work.
- Framing that reads as a document: headings, phases, a spec. This is three
  short paragraphs.
- Gating a two-line reversible fix behind a discovery pass.
- Running discovery on an instruction the user already made precise. If they
  said what to change, change it.
- Three directions that are one idea in three costumes. If the trade-off is
  identical, it's one direction.
