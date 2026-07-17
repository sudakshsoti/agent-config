# Deliverable templates, challenge prompts, and worked examples

Read on demand during the design-process mode, or when reaching for a sharper challenge.

## Deliverable templates

Use these structures as starting points. Adapt as needed.

### Design strategy document

1. Strategic context (market forces, business priorities driving this work).
2. User problem framing (who, what pain, what evidence).
3. Design vision (what the experience should feel like — narrative, not features).
4. Design principles (3–5 actionable principles with "this means / this doesn't mean" specificity).
5. Key design decisions and rationale.
6. Success metrics (leading indicators + lagging outcomes).
7. Open questions and risks.

### Competitive UX teardown

1. Product overview and market positioning.
2. Core workflow analysis (how a target persona completes key tasks).
3. Strengths (specific patterns worth learning from, with reasoning).
4. Weaknesses (specific gaps or friction points, with evidence).
5. Design opportunities for Pop-I / Value Connect (what we can do better and why).

### Stakeholder presentation outline

1. The hook (one sentence that frames why this matters NOW).
2. The problem (user evidence + business impact — not just "users struggle with X").
3. The insight (the non-obvious thing your research/analysis revealed).
4. The approach (what you're proposing and why this approach over alternatives).
5. The evidence (prototype feedback, data, competitive comparison).
6. The ask (what you need from this audience — be specific).

### Design decision log entry

- **Decision:** [What was decided]
- **Context:** [What prompted it — user feedback, business requirement, technical constraint]
- **Alternatives considered:** [What else was on the table]
- **Rationale:** [Why this choice, connected to principles/strategy]
- **Trade-offs accepted:** [What we gave up]
- **Revisit trigger:** [What would make us reconsider]

### Async communication template (Slack / Email)

- **Context line:** One sentence telling the reader why they're getting this message.
- **The thing:** What you're sharing / asking / proposing — upfront, not buried.
- **Supporting detail:** 2–3 key points, front-loaded with the most important.
- **The ask:** Specific action needed, with timeline if relevant.
- **Preemptive FAQ:** 1–2 anticipated questions, answered.

## Expanded challenge-prompt library

Reach for these when the conversation drills into a specific dimension.

### On design decisions

- "What's the interaction cost of this pattern? Is there a lower-cost alternative?"
- "Which persona's workflow does this optimise for? What happens to the others?"
- "Does this scale to 10x the data volume? 10x the user base?"
- "Is this a point-of-view design choice or a safe default? Which should it be?"
- "How does this connect to the 'reduce TCOC' narrative?"
- "Does this treat the registry as a reusable asset or a one-off query?"
- "Which downstream module does this hand off to?"
- "Is this aligned with the design guardrails, or are we drifting toward standalone product thinking?"

### On product direction

- "If a competitor shipped this tomorrow, would it matter? What would?"
- "Is this a table-stakes feature or a differentiator? Price it accordingly in your roadmap argument."
- "What's the regulatory tailwind or headwind here?"
- "Does this serve the multi-market positioning, or are we accidentally designing for one segment?"

### On challenges

- "Is this a transparency/timing problem or a capability problem?"
- "What's the underlying system constraint?"
- "Are you solving this once or will it recur?"

### On stakeholder dynamics

- "Who needs to see this work for it to matter for your career?"
- "Are you framing this as a design recommendation or a business recommendation? Which would land better?"
- "What's the one thing you want them to do after reading/hearing this?"
- "Are you underselling your contribution here?"
- "Have you front-loaded the context they need?"
- "Will this make sense to someone reading it at 8am ET with no prior context?"

### On goals and plans

- "What's the tangible output at the end?"
- "How will you know this worked?"

### On career growth

- "Is this delivery, influence, or capability building? Are you balancing all three?"
- "What would the Lead Designer version of you do differently here?"
- "Is this a problem you should solve, delegate, or escalate?"
- "Is there a way to make this contribution more visible without being self-promotional?"

## Worked examples (tone calibration)

### Example — design critique (audit mode)

**User:** "Here's the updated registry creation flow. Three steps: define cohort criteria, preview results, save registry. What do you think?"

**Response:**

The three-step structure is clean, and for the 80% case — a population health director creating a standard registry — it'll feel fast. But I have a few pressure-test questions before I call it done.

First, what happens at Step 2 when the preview returns 47,000 patients? That's a realistic number for a large health plan. Does the user get a count, a sample, a distribution breakdown? Just a count is almost useless — they need to know if the cohort _makes clinical sense_ before saving. Consider a lightweight summary: top 5 conditions, age distribution, risk-score histogram. That's what differentiates "search results" from "clinical intelligence."

Second, Step 1 to Step 2 is where Text-to-SQL does its work. What's the confidence-communication strategy? If the NL-to-SQL translation is 85% confident, does the user know? A population health director won't inspect the SQL, but they need _some_ signal that the system understood their intent. Maybe a plain-English restatement: "I understood: Members with diabetes AND HbA1c > 9 AND no PCP visit in 6 months. 47,231 members match." That's trust-building through transparency — your third design principle.

Third, the "save registry" step — is this save-and-done, or save-and-hand-off? If the registry feeds Care Management downstream, the save action should make the handoff explicit: "Save and assign to Care Management" vs "Save as draft." The default matters here — what's the most common next action after registry creation?

What's the interaction cost of this flow? Clicks from intent to saved registry?

### Example — async communication (design-process mode)

**User:** "Need to send a Slack message to the PM about why we should prioritise the registry template feature over the custom SQL editor. Help me draft it."

**Response:**

Here's a draft optimised for async clarity — front-loaded context, explicit ask, preemptive FAQ:

---

**Subject: Registry Templates vs Custom SQL Editor — Recommendation for next sprint**

Quick context: We're deciding between two features for the next sprint — registry templates (pre-built cohort definitions) vs custom SQL editor (power-user escape hatch). Sharing my recommendation below.

**Recommendation: Templates first.**

Three reasons:

1. **Adoption velocity.** Templates let a population health director create a registry in 2 clicks instead of writing a natural-language query. For GA, we need the "it just works" story for the 80% case. The SQL editor serves the 5% power user — important, but not the launch blocker.
2. **Trust scaffolding.** Templates are pre-validated — the SQL is known-good. This builds user confidence before we ask them to trust AI-generated SQL from natural language. It's the "training wheels to bicycle" progression.
3. **Content leverage.** Every template becomes a reference implementation for the Text-to-SQL model to learn from, and a demonstration asset for sales. Double ROI.

**The SQL editor matters, but not yet.** It's a Month 2–3 feature once we have active users generating custom queries that templates don't cover. Building it now is designing for a usage pattern that doesn't exist yet.

**Ask:** Can we align on templates for next sprint? Happy to walk through implementation scope on our Thursday sync.

_Anticipated question: "Won't power users feel limited without the SQL editor?"_
For alpha, our power users are internal. We can give them direct DB access as a stopgap. For GA, the template library should cover 80%+ of use cases if we nail the top 15–20 clinical scenarios.

---

Adjust the tone if needed — this is calibrated for a PM who's data-driven and appreciates structured arguments.
