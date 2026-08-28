# Value Connect context

Load this whenever the conversation is actually about this product. Facts
current as of 2026-08 — confirm product phase before relying on it if this
file is stale.

## What it is

Value Connect is a suite at Optum Insight (UnitedHealth Group). Population
Interventions (Pop-I) is an AI-enabled module inside that suite — a module
in a suite, not a standalone product, and every design decision should be
checked against that framing.

Pop-I's job: identify impactable patient cohorts, build registries, and hand
them downstream to Care Management, Quality, and Financial Performance.
Flagship capability: Text-to-SQL — natural language to validated SQL to
registry creation — extended to member-list filtering as well.

Adjacent named surfaces inside the broader suite — **names only, no invented
behaviour**: Care Extension, Contract Performance, Network Optimization, EHR
Integrations, Quality Opt, SDoH, Risk Accuracy. These are names, not
specifications — do not describe their behaviour as though it's known;
say so explicitly if a conversation assumes otherwise.

Phase: Alpha to GA, with a React UI migration in progress.

## Guardrails

- Every output is someone else's input — design for the handoff, always.
- A registry is a reusable operational asset, not a one-off query result —
  treat "save" as creating something that persists and gets reused, not as
  closing a search.
- Name the downstream consumer for every flow under discussion.
- Watch for drift toward standalone-product thinking — a feature that only
  makes sense in isolation, disconnected from the suite and the downstream
  handoff, is a signal to push back.

## Recurring personas

Population health director, care manager, analytics users spanning
summary-only to custom-SQL fluency, and CFO/CMO-level audiences for
executive-facing output. See `payer-experience.md` and
`provider-experience.md` for the full role detail behind these.

## The canonical worked flow

Define cohort criteria, preview results, save registry.

The preview problem: a bare count is nearly useless at five-figure cohort
sizes — the user needs to judge whether the cohort makes clinical sense, not
just how big it is. Show composition: top conditions, age distribution, risk
score spread (order-of-magnitude framing, not implementation-specific).
Pair this with intent restatement in plain English before the user commits.

Save-and-assign versus save-as-draft is a defaults decision, not a
throwaway button choice — it determines whether the default action creates
an explicit downstream handoff or leaves the registry sitting unassigned.

## Competitor set

Innovaccer, Arcadia, Cedar Gate, Lightbeam, Clarify, Inovalon, Cotiviti.
Frame every observation as a design opportunity for Pop-I / Value Connect,
not a feature checklist, and verify current competitor product claims by
search before asserting them — this list moves.

## Prototyping constraint

The available tools are Figma Make and Copilot Enterprise. Prototype by
natural-language specification: describe the user, the job, state
transitions, data, rules, failure cases, and the success signal — offer
prompts and experiments before proposing traditional code. See
`templates-and-prompts.md` for the structure.

## Closing note

Stakeholder names, org chart, reporting lines, OKRs, working hours, and
career state are deliberately absent from this skill and must not be added
here — that context lives in the user's own Work & Strategy project, kept
separate on purpose.
