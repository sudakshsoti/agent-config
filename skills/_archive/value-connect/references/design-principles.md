# Design principles

Apply these when auditing or generating enterprise healthcare design work. In an audit, name which principle a finding maps to.

## Enterprise healthcare UX principles

1. **Workflow coherence over UI polish.** A system that fits the user's mental model with mediocre visuals beats a beautiful interface that disrupts workflow. Optimise for task completion, not screenshots.
2. **Progressive complexity.** Healthcare analytics users range from "show me the summary" to "let me write custom SQL." Design for the 80% case; provide escape hatches for power users. Never force everyone through the power-user path.
3. **Trust through transparency.** Every number can be questioned. Show provenance, methodology, and data freshness. AI-generated outputs (like Text-to-SQL) need confidence indicators, not just results.
4. **Defaults are design decisions.** The default filter, sort, view shape 90% of user behaviour. Choose defaults that encode best-practice workflows, not engineering convenience.
5. **Design for the handoff.** No tool exists in isolation. Every output becomes someone else's input. Design registry outputs to be immediately actionable in Care Management; design summaries that can drop into a board presentation.
6. **Error cost awareness.** A false positive in a registry means unnecessary outreach (cost + annoyance). A false negative means a missed intervention (potential harm). Design error states, validation, and confirmation patterns with this asymmetry in mind.
7. **Time-to-insight as the critical metric.** The value of an analytics tool is how quickly the user goes from question to actionable insight. Every click, page load, and unnecessary confirmation dialog is time stolen from patient care.

## Information architecture

- Organise by user task, not by data structure.
- Use consistent spatial relationships (same data type, same screen position).
- Reduce reliance on memory across screens — carry context forward.
- Design for scan-then-drill, not read-then-find.

## Interaction design

- Reduce interaction cost relentlessly — fewer clicks for frequent tasks.
- Make reversible actions easy, irreversible actions deliberate.
- Prefer inline editing and direct manipulation over modal dialogs.
- Design loading states that communicate progress, not just "please wait."
