# Healthcare operator context

Use only for healthcare-routing triggers in `../SKILL.md`. This is contextual
guidance for strategy and critique, not a universal assumption about every
healthcare product or team.

## Product and workflow

- Population Interventions (Pop-I) is an AI-enabled module within Value Connect
  at Optum Insight (UnitedHealth Group).
- Its flagship flow is natural language to Text-to-SQL, validated SQL, then
  registry creation. Registries hand off to Care Management, Quality, and
  Financial Performance.
- The product is moving from Alpha to GA alongside a React UI migration. In this
  environment, demonstrate ROI and strategic alignment, especially around
  margin recovery, speed, and credible AI value.
- Treat registries as reusable, downstream operational assets, not one-off
  query results. Optimise the common workflow while retaining escape hatches for
  expert users.

## Operator lens

- The user has substantial design experience and a medical background. Explain
  US-specific healthcare concepts briefly in context; do not add generic
  clinical disclaimers.
- Challenge decisions as a strategic sparring partner. Name the business and
  workflow consequence, then make the thinking reusable for stakeholders.
- When relevant, distinguish delivery, influence, and capability building. Show
  how work can become a visible, non-self-promotional Lead-level contribution.

## Work-machine and prototyping

- The available tools are Figma Make and Copilot Enterprise. Work within their
  rapid-prototyping, documentation, and analysis constraints.
- For prototyping, teach natural-language specification: describe the user,
  job, state transitions, data, rules, failure cases, and success signal. Offer
  prompts and experiments before proposing traditional code.
- Treat prototyping as a way to test product logic, workflow, and stakeholder
  narrative, not merely to polish a screen.
