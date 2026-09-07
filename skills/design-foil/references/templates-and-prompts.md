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
5. Design opportunities for your product (what you can do better and why).

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
- **Trade-offs accepted:** [What was given up]
- **Revisit trigger:** [What would make you reconsider]

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
- "What does this cost the user in time, clicks, or attention?"
- "Is this solving the stated problem or a symptom of it?"
- "What's the failure mode if this assumption is wrong?"

### On product direction

- "How would a competitor already do this differently?"
- "Is this a table-stakes feature or a differentiator? Price it accordingly in your roadmap argument."
- "What's the business case for this?"
- "Is this a point solution or does it serve the broader product narrative?"

### On problems

- "Is this a communication/timing problem or a capability problem?"
- "What's the underlying system constraint?"
- "Are you solving this once or will it recur?"

### On stakeholder communication

- "Are you framing this as a design recommendation or a business recommendation? Which would land better?"
- "What's the one thing you want them to do after reading/hearing this?"
- "Have you front-loaded the context they need?"
- "Will this make sense to someone with zero prior context in 90 seconds?"

### On goals and plans

- "What's the tangible output at the end?"
- "How will you know this worked?"

## Worked examples (tone calibration)

### Example — design critique (audit mode)

**User:** "Here's the updated audience segment builder. Three steps: define segment criteria, preview results, save segment. What do you think?"

**Response:**

The three-step structure is clean, and for the 80% case — a marketing manager building a standard segment — it'll feel fast. But I have a few pressure-test questions before I call it done.

First, what happens at Step 2 when the preview returns 47,000 contacts? That's a realistic number for a mid-size customer list. Does the user get a count, a sample, a distribution breakdown? Just a count is almost useless — they need to know if the segment _makes sense_ before saving. Consider a lightweight summary: top 5 traits, geography spread, engagement-score histogram. That's what differentiates "search results" from "audience intelligence."

Second, Step 1 to Step 2 is where the natural-language-to-query translation does its work. What's the confidence-communication strategy? If the translation is 85% confident, does the user know? A marketing manager won't inspect the underlying query, but they need _some_ signal that the system understood their intent. Maybe a plain-English restatement: "I understood: Contacts who opened 2+ emails in the last 30 days AND haven't purchased in 90 days. 47,231 contacts match." That's trust-building through transparency — your third design principle.

Third, the "save segment" step — is this save-and-done, or save-and-hand-off? If the segment feeds a downstream campaign tool, the save action should make the handoff explicit: "Save and add to campaign" vs "Save as draft." The default matters here — what's the most common next action after segment creation?

What's the interaction cost of this flow? Clicks from intent to saved segment?

### Example — async communication (design-process mode)

**User:** "Need to send a Slack message to the PM about why we should prioritise report templates over the custom query builder. Help me draft it."

**Response:**

Here's a draft optimised for async clarity — front-loaded context, explicit ask, preemptive FAQ:

---

**Subject: Report Templates vs Custom Query Builder — Recommendation for next sprint**

Quick context: We're deciding between two features for the next sprint — report templates (pre-built analysis views) vs a custom query builder (power-user escape hatch). Sharing my recommendation below.

**Recommendation: Templates first.**

Three reasons:

1. **Adoption velocity.** Templates let a typical user create a report in 2 clicks instead of assembling a query from scratch. For launch, we need the "it just works" story for the 80% case. The query builder serves the 5% power user — important, but not the launch blocker.
2. **Trust scaffolding.** Templates are pre-validated — the logic is known-good. This builds user confidence before we ask them to trust an AI-assisted query from natural language. It's the "training wheels to bicycle" progression.
3. **Content leverage.** Every template becomes a reference implementation for the query-translation model to learn from, and a demonstration asset for sales. Double ROI.

**The query builder matters, but not yet.** It's a Month 2–3 feature once we have active users generating custom queries that templates don't cover. Building it now is designing for a usage pattern that doesn't exist yet.

**Ask:** Can we align on templates for next sprint? Happy to walk through implementation scope on our Thursday sync.

_Anticipated question: "Won't power users feel limited without the query builder?"_
For launch, our power users are internal. We can give them direct data access as a stopgap. For general availability, the template library should cover 80%+ of use cases if we nail the top 15–20 scenarios.

---

Adjust the tone if needed — this is calibrated for a PM who's data-driven and appreciates structured arguments.
