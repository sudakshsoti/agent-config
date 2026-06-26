---
name: explain-this
description:
  Explain Claude's plan, current action, or finished work in plain English, then
  teach the one concept behind it. Use when the user asks "what are you doing",
  "what did you do", "explain that", "what does that mean", "in simple terms",
  "wait, why", or types /explain-this — and proactively after presenting a plan
  or finishing a chunk of work the user may not follow. Built for a
  design/product person learning the engineering side: teaches code/infra
  concepts with everyday analogies, and skips design concepts they already know.
user-invocable: true
---

# Explain This

Translate-and-teach. When asked (or after a meaty step), explain what you're
planning, doing, or just did — first in one plain-English line, then an optional
layer that teaches the one concept behind it. The reader is learning the
engineering side; leave them with a word and an intuition they keep.

## The contract

Two layers. The TL;DR is always there. The deeper layer is offered, never forced.

```
**In short:** <one sentence, zero jargon — what's happening and why it matters to
you. Tense follows the moment: "I'm about to…" / "I'm…" / "I just…">

Going deeper (optional):
- **The idea — `<concept>`:** the real term, defined plainly, so the word sticks.
- **Like…** one everyday analogy (mail, kitchens, traffic) that makes it click.
- **Why it matters / watch for:** the tradeoff, or the thing that could bite —
  why this over the alternative.
```

Example:

> **In short:** I'm moving the data fetch off the main path so the page stays
> clickable while it loads instead of freezing.
>
> Going deeper (optional):
> - **The idea — `async`:** code that kicks off slow work and keeps going
>   instead of standing still waiting for the result.
> - **Like…** ordering at a counter and getting a buzzer — you sit down and do
>   other things until it buzzes, instead of standing at the till.
> - **Why it matters:** the screen never locks up; the catch is errors can get
>   silently dropped unless we deliberately catch them — which is the next thing
>   I'll wire in.

More worked examples across coding, homelab, automation, and infra:
[references/examples.md](references/examples.md).

## Rules

- **Lead with the jargon-free TL;DR.** If a technical term has to appear, it gets
  defined in the deeper layer — never assumed.
- **Teach the technical, skip the familiar.** Explain code / infra / engineering
  concepts. Do **not** explain design, product, UX, or healthcare concepts — the
  reader owns those; treat them as shared vocabulary.
- **One concept per explanation.** Name it as a reusable term so vocabulary
  compounds over sessions. Don't stack three concepts at once.
- **Analogies stay everyday.** Kitchens, mail, traffic — universal. Not Figma,
  value-based care, or clinical references.
- **Scale to the moment.** A tiny action gets just the TL;DR, no deeper layer. A
  real plan or a finished feature earns both layers. Never pad.
- **Any of three tenses:** an upcoming *plan*, a *current* action, or *finished*
  work. Adjust the TL;DR's tense; the shape stays the same.
- **Plain markdown, not `<details>`.** The terminal may not collapse HTML, so the
  skippable layer is just the `Going deeper (optional):` heading.

## Common mistakes

- A TL;DR that still leaks jargon ("I'm memoizing the selector") — rewrite it as
  what it *does* for the reader, push the term down into `The idea`.
- Explaining something the reader already knows (a design pattern, a care
  workflow). That's not teaching, it's noise — cut it.
- Three concepts crammed in. Pick the one that matters most here; the rest can
  come when they next appear.
- A domain-specific analogy that only lands if you already know the domain. If
  the analogy needs its own explanation, it's the wrong analogy.
