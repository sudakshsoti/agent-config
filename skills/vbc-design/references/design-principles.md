# Design principles

Load this in Audit mode. Name the specific principle behind each finding and
connect it to a patient, operator, or business consequence — never a
generic verdict.

## The fourteen principles

1. **Workflow coherence over UI polish.** A system that fits the user's
   mental model with mediocre visuals beats a beautiful interface that
   disrupts care work. Optimise for task completion, not screenshots.
2. **Progressive complexity.** Healthcare analytics users range from "show
   me the summary" to "let me write custom SQL." Design for the 80% case
   with escape hatches for power users; never force everyone through the
   power-user path.
3. **Trust through transparency.** Show provenance, methodology, and data
   freshness. AI outputs such as Text-to-SQL need confidence communication,
   not just an answer.
4. **Defaults are design decisions.** Default filters, sorts, and views
   should encode best-practice workflows, not engineering convenience.
5. **Design for the handoff.** Make registry outputs immediately actionable
   in downstream Care Management, Quality, or Financial Performance
   workflows — every output is someone else's input.
6. **Respect asymmetric error cost.** A false-positive registry entry
   creates unnecessary outreach; a false negative can mean a missed
   intervention. Shape validation, confirmation, and error states around
   that difference, not around a single uniform error treatment.
7. **Time to insight is a critical metric.** Every unnecessary click, page
   load, or confirmation takes time directly from care work or
   intervention.
8. **Show the as-of.** Every count, rate, or list needs a visible
   data-through date and, where relevant, a completeness caveat — an
   undated number reads as more current than it is.
9. **The list is a promise.** A stale or already-closed item on a gap or
   outreach list costs credibility for the whole product, not just that
   one row — a user who catches one wrong entry stops trusting the rest.
10. **Design for the person who will be audited.** Provenance,
    reproducibility, and an auditable trail of exactly what ran are user
    features in this domain, not backend logging — the person defending a
    number in a RADV or NCQA audit is a real user of that trail.
11. **Fit the host workflow.** Living inside the EHR or inside the queue the
    user already works from beats a beautiful separate destination; a new
    login is an adoption tax that kills usage regardless of the tool's
    merits.
12. **PHI is not a footnote.** Minimum-necessary access and consent
    restrictions are a layout and defaults constraint, decided at design
    time, not a compliance review bolted on at the end.
13. **Regulatory clocks are part of the interaction budget.** A turnaround
    requirement or an appeal timeframe is a hard constraint on how many
    clicks a workflow can afford, not a note in a requirements doc.
14. **Denial and outreach wording carries legal and emotional weight.** Flag
    it explicitly and route the actual copy to `ux-writing` — don't let
    default component text stand in for reviewed member-facing language.

## Information architecture

- Organise by user task, not data structure.
- Keep a data type in a consistent spatial position across screens.
- Carry context between screens rather than relying on memory.
- Support scan-then-drill rather than read-then-find.

## Interaction design

- Reduce interaction cost for frequent tasks.
- Make reversible actions easy and irreversible actions deliberate.
- Prefer inline editing and direct manipulation to modal dialogs where the
  workflow permits.
- Use loading states that communicate progress, not a generic wait.

## Audit checklist

Twelve questions to run against any healthcare screen, one per underlying
principle, phrased as questions the auditor asks:

1. Does every count or rate on this screen carry a visible as-of date?
2. If this is an AI-generated result, is there a confidence signal, not
   just an answer?
3. Do the default filter, sort, and view encode a best-practice workflow,
   or just whatever was easiest to build?
4. If this feeds a downstream team or system, is the handoff explicit and
   immediately actionable, or does it dead-end here?
5. Does the error/confirmation treatment differ for a costly false positive
   versus a costly false negative, or is every error handled the same way?
6. Could a user tell, at a glance, whether an item on this list is already
   resolved?
7. If a claim or coding suggestion appears here, is there a visible
   evidence trail behind it?
8. Does this workflow live inside a system the target role already has
   open, or does it demand a separate login?
9. Does the default view expose more PHI than the stated task requires for
   this role?
10. If a regulated turnaround clock applies, is it visible and is the
    escape path (escalation, expedite) reachable in one or two steps?
11. Is any member- or provider-facing wording here reviewed language, or is
    it a placeholder that needs to route through `ux-writing`?
12. Could the person who built this defend every number on it in an audit,
    using only what's shown on screen?
