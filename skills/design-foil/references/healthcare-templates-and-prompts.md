# Healthcare templates and challenge prompts

Use alongside the generic templates only for healthcare-routing triggers in
`../SKILL.md`. Adapt the structure to the actual payer, provider, or
payer-provider context. Verify time-sensitive domain claims before publishing.

## Healthcare-specific additions to generic deliverables

### Competitive UX teardown

Add a final section: **Design opportunities for Pop-I / Value Connect**. Tie
each opportunity to a healthcare workflow, quality, risk, or handoff outcome,
not a competitor feature alone.

### Strategy and decision rationale

For registry, cohort, or Text-to-SQL work, state:

- the downstream consumer and handoff;
- how the proposal affects TCOC, quality, intervention speed, trust, or risk;
- whether a registry is a reusable asset or a one-off query;
- whether the default fits the common case without blocking expert users.

## Challenge prompts

### Product and workflow

- “How does this connect to the reduce-TCOC narrative?”
- “Does this treat the registry as a reusable asset or a one-off query?”
- “Which downstream module does this hand off to?”
- “Is this aligned with the design guardrails, or drifting toward standalone
  product thinking?”
- “If a competitor shipped this tomorrow, would it matter? What would?”
- “What is the regulatory tailwind or headwind?”
- “Does this serve multi-market positioning, or accidentally design for one
  segment?”

### Stakeholder and career influence

- “Who needs to see this work for it to matter for your career?”
- “Are you framing this as a design recommendation or a business
  recommendation?”
- “Are you underselling your contribution?”
- “Will this make sense at 8am ET with no prior context?”
- “Is this delivery, influence, or capability building?”
- “What would the Lead Designer version of you do differently?”
- “Should this be solved, delegated, or escalated?”
- “How can this contribution be more visible without being self-promotional?”

## Worked example: registry template priority

Frame the decision as adoption velocity, trust scaffolding, and content
leverage. A template can make the common population-health task fast, give
users a known-good reference before asking them to trust AI-generated SQL, and
provide a reusable demonstration asset. State the trade-off plainly: a custom
SQL editor remains important for power users, but should follow evidence of a
real unmet usage pattern rather than lead the Alpha-to-GA workflow.

## Natural-language prototype prompt

Use this structure with Figma Make or another approved tool:

> Design a [persona]'s flow to [job] in Pop-I. Start from [entry condition].
> Show the Text-to-SQL request, validation/provenance, preview with [key
> distribution or confidence detail], and registry handoff to [downstream
> team]. Default for the common case; give experts a reversible escape hatch.
> Include loading, low-confidence, empty, and validation-failure states. The
> outcome is [TCOC, quality, intervention-speed, or trust measure].
