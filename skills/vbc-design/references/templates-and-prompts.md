# Templates and prompts

Load this in Deliverables mode. Adapt every structure to the actual payer,
provider, or payer-provider context rather than filling it in mechanically.

## Deliverable templates

### Design strategy document

1. Strategic context — market forces and business priorities driving this
   work, framed in payer/provider economics, not generic market language.
2. User problem framing — who, what pain, what evidence, named down to the
   role (see `payer-experience.md` / `provider-experience.md`).
3. Design vision — what the experience should feel like, narrative rather
   than a feature list.
4. Design principles — three to five actionable principles with "this
   means / this doesn't mean" specificity, drawn from
   `design-principles.md`.
5. Key design decisions and rationale.
6. Success metrics — leading indicators plus lagging outcomes, framed in
   TCOC, quality, RAF, or adoption terms where relevant.
7. Open questions and risks.

### Competitive UX teardown

1. Product overview and market positioning.
2. Core workflow analysis — how a target persona completes key tasks.
3. Strengths — specific patterns worth learning from, with reasoning.
4. Weaknesses — specific gaps or friction points, with evidence.
5. **Design opportunities.** Tie every opportunity to a workflow, quality,
   risk, or handoff outcome, not a competitor feature checklist.

### Design decision log entry

- **Decision:** what was decided.
- **Context:** what prompted it — user feedback, business requirement,
  technical or regulatory constraint.
- **Alternatives considered:** what else was on the table.
- **Rationale:** why this choice, connected to a principle or strategy.
- **Trade-offs accepted:** what was given up.
- **Revisit trigger:** what would make the team reconsider.

### Async exec/Slack message

- **Context line:** one sentence telling the reader why they're getting
  this.
- **The thing:** what's being shared, asked, or proposed — upfront, not
  buried.
- **Supporting detail:** two or three key points, front-loaded with the
  most important.
- **The ask:** specific action needed, with a timeline if relevant.
- **Pre-empted questions:** one or two anticipated questions, answered.

### Journey map scaffold (payer or provider role)

1. Role and context — name the role, the org type, the licence if any, the
   day shape (see the two experience references).
2. Trigger — what starts this journey (a queue item, an alert, a scheduled
   task).
3. Steps — each step's action, system used, and data touched.
4. Friction points — named per step, tied to a specific cause (interaction
   cost, missing data, a regulatory clock).
5. Emotional and stakes context — what's at risk if this step goes wrong
   (compliance, patient safety, financial, trust).
6. Handoff — where this journey ends and whose journey picks up next.

### Measure-to-workflow map

Walk one HEDIS or Star measure from specification to the screen that closes
the gap:

1. Measure specification — denominator, numerator, exclusions, continuous
   enrolment window.
2. Data sources feeding it — claims, supplemental, clinical, and their
   respective lag.
3. The gap — what "not yet met" looks like for a given member.
4. The workflow that closes it — which role, in which system, doing what
   specific action.
5. The screen — where the gap surfaces, what evidence it shows, what
   action it enables.
6. The measurement — how the system knows the gap closed, and the lag
   before that shows up in the official rate.

## Registry/cohort review protocol

Run these questions against any registry or cohort-building flow before
calling it done:

1. Does the denominator mirror the actual measure specification, if this
   maps to a quality measure?
2. Is the continuous-enrolment window handled explicitly?
3. Are hospice, ESRD, palliative care, and deceased-member exclusions
   applied where clinically or contractually required?
4. Is this a saved query (re-evaluates) or a materialised list (frozen),
   and does the user know which?
5. Is the attribution method and its effective date shown alongside any
   attributed population?
6. Does the preview show composition (not just a count) so the user can
   judge clinical plausibility?
7. Is there a named downstream consumer and an explicit handoff action?
8. If AI-generated, is there a plain-English intent restatement and a
   confidence signal before the user commits?
9. Is there an auditable, re-runnable record of exactly what query ran?

## Challenge-prompt library

### Economics and incentives

- "How does this connect to the TCOC or MLR story for this line of
  business?"
- "Who holds the risk here, and does this design assume the wrong actor
  optimises for the outcome?"
- "What's the regulatory tailwind or headwind on this?"

### Role and workflow

- "Which specific role's workflow does this optimise for? What happens to
  the others touching the same data?"
- "Does this fit inside the system the target role already has open, or
  does it demand a new login?"
- "What's the interaction cost of this pattern against the regulatory
  clock, if one applies?"

### Data and trust

- "Does this number carry an as-of date and a completeness caveat?"
- "If this is AI-generated, what's the confidence signal, and what's the
  fallback if confidence is low?"
- "Would the denominator here tie to the official measure rate, or would
  it produce a different number?"

### Handoff and system coherence

- "Does this treat its output as a reusable asset or a one-off result?"
- "Which downstream module or team does this hand off to, and is that
  handoff explicit in the UI?"
- "Is this aligned with the product's own guardrails, or drifting toward
  standalone-tool thinking?"

### Adoption and procurement

- "If a competitor shipped this tomorrow, would it matter? What would?"
- "What's the pilot-to-enterprise path for this, and does the design
  assume day-one full rollout instead?"
- "Does this survive a security review given the PHI it touches?"

The seven prompts above replace the "Product and workflow" list that used
to live in `design-strategy`. Career-influence prompts are explicitly out of
scope for this skill — see `strategy-counsel` and the user's own Work &
Strategy project.

## Natural-language prototype prompt

Use this structure with Figma Make or another approved tool:

> Design a [persona]'s flow to [job] in Pop-I. Start from [entry condition].
> Show the Text-to-SQL request, validation/provenance, preview with [key
> distribution or confidence detail], and registry handoff to [downstream
> team]. Default for the common case; give experts a reversible escape
> hatch. Include loading, low-confidence, empty, and validation-failure
> states. The outcome is [TCOC, quality, intervention-speed, or trust
> measure].

## Worked examples (tone calibration)

### Example — registry-preview critique

**Prompt:** "Here's the updated registry creation flow. Three steps: define
cohort criteria, preview results, save registry. What do you think?"

**Response:**

The three-step structure is clean, and for the 80% case — a population
health director creating a standard registry — it'll feel fast. But a few
pressure-test questions before calling it done.

First, what happens at the preview step when the query returns a
five-figure member count (illustrative — an order of magnitude, not a
specific number to quote)? A bare count is nearly useless at that scale —
the user needs to know whether the cohort makes clinical sense before
saving, not just how big it is. A lightweight composition summary — top
conditions, age distribution, risk-score spread — is what turns "search
results" into something a clinician would actually trust.

Second, the criteria-to-preview step is where Text-to-SQL does its work.
What's the confidence communication? A population health director won't
inspect generated SQL, but needs some signal the system understood intent
correctly — a plain-English restatement ("members with diabetes AND
HbA1c > 9 AND no PCP visit in 6 months, N matching") is trust-building
through transparency, principle three.

Third, "save registry" — is this save-and-done or save-and-hand-off? If the
registry feeds Care Management downstream, the save action should make the
handoff explicit: "save and assign to Care Management" versus "save as
draft." The default matters — what's the more common next action after
registry creation, and does the button default to it?

What's the click count from intent to saved, handed-off registry?

### Example — async exec draft

**Prompt:** "Need to send a message to the PM about why we should
prioritise the registry template feature over the custom SQL editor. Help
me draft it."

**Response:**

Here's a draft optimised for async clarity — front-loaded context,
explicit ask, pre-empted question:

---

**Subject: Registry templates vs. custom SQL editor — recommendation for
next sprint**

Quick context: deciding between two features for next sprint — registry
templates (pre-built cohort definitions) versus a custom SQL editor (power
user escape hatch). Recommendation below.

**Recommendation: templates first.**

Three reasons:

1. **Adoption velocity.** Templates let a population health director
   create a registry in a couple of clicks instead of writing a
   natural-language query from scratch. For GA, the "it just works" story
   for the 80% case matters more than the 5% power-user path.
2. **Trust scaffolding.** Templates are pre-validated — known-good SQL.
   That builds confidence in the system before asking users to trust
   AI-generated SQL from a natural-language request — training wheels
   before the bicycle.
3. **Content leverage.** Every template built becomes both a reference for
   the Text-to-SQL model and a demonstration asset externally — one build,
   two uses.

The SQL editor still matters, but later — once there's evidence of a real
usage pattern templates don't cover, not before.

**Ask:** align on templates for next sprint? Happy to walk through scope on
the next sync.

*Anticipated question: "Won't power users feel limited without the SQL
editor?"* For Alpha, power users can get direct DB access as a stopgap. For
GA, the template library should cover the large majority of use cases if
the top clinical scenarios are chosen well.

---

Adjust tone for the actual audience — this is calibrated for a
data-driven reader who responds to a structured argument.
