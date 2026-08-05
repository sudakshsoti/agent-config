# Healthcare design principles

Use only for healthcare-routing triggers in `../SKILL.md`. During an audit,
name the principle behind each finding and connect it to a patient, operator,
or business consequence.

1. **Workflow coherence over UI polish.** Optimise for task completion, not
   screenshots. A system that fits the user's mental model beats a beautiful
   interface that disrupts care work.
2. **Progressive complexity.** Healthcare analytics users range from a summary
   to custom SQL. Design for the 80% case with escape hatches for power users.
3. **Trust through transparency.** Show provenance, methodology, and data
   freshness. AI outputs such as Text-to-SQL need confidence communication, not
   just an answer.
4. **Defaults are design decisions.** Default filters, sorts, and views should
   encode best-practice workflows, not engineering convenience.
5. **Design for the handoff.** Make registry outputs immediately actionable in
   downstream Care Management, Quality, or Financial Performance workflows.
6. **Respect asymmetric error cost.** A false-positive registry can create
   unnecessary outreach; a false negative can miss an intervention. Shape
   validation, confirmation, and error states around that difference.
7. **Time to insight is a critical metric.** Each unnecessary click, page load,
   or confirmation takes time from care work and intervention.

## Information architecture

- Organise by user task, not data structure.
- Keep a data type in a consistent spatial position.
- Carry context between screens rather than relying on memory.
- Support scan-then-drill rather than read-then-find.

## Interaction design

- Reduce interaction cost for frequent tasks.
- Make reversible actions easy and irreversible actions deliberate.
- Prefer inline editing and direct manipulation to modal dialogs where the
  workflow permits.
- Use loading states that communicate progress, not a generic wait.
