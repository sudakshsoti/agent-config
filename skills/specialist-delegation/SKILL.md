---
name: specialist-delegation
description: "Use in Pi when deciding whether to delegate work, selecting specialist subagents, or preparing and verifying a worker handoff. Owns individual dispatches; use workstreams for dependencies, edit ownership, and integration across multiple implementation streams."
compatibility: "Pi with the Agent subagent tool; check the live tool schema and available agent roles."
---

# Pi specialist delegation

Delegate a bounded outcome, not responsibility for understanding the task. This
skill is Pi-specific even though it is distributed through the shared skills
root. If Pi's Agent tool is unavailable, work directly or report the limitation;
do not invent an API or install another coordinator.

## Decide before dispatching

Use a specialist when it supplies expertise, independent review, parallel work,
or useful context isolation that exceeds the cost of briefing and checking it.
State the choice in one clause: “Explore will map the dependency because the
entry point is unknown; I will decide the implementation.”

Stay in the main session when the target is already known and a direct read or
search answers the question, the edit is trivial, the handoff would repeat most
of the work, or the task cannot be separated from unresolved requirements. Do
not delegate merely to use more agents, duplicate a running investigation, or
ask a child to recursively delegate a bounded lookup.

For multiple implementation streams with dependencies or shared edit risks,
load [pi-workstreams](../pi-workstreams/SKILL.md) first. Independent lookups do
not need a workflow graph.

## Select by role, permission, and judgment

Inspect the currently available roles and tool schema. In this repository,
`pi/agents/*.md` and `pi/model-ladder.md` own routing; these are agent-config
source paths, not paths to assume in the target project. In an installed
session, inspect available role definitions (normally `~/.pi/agent/agents/`)
and the live tool schema. Do not copy model IDs into packets as permanent
policy. Project role overrides may differ. Use the least
expensive capable role, not an unspecified child inheriting the parent model.

| Work | Starting role | Boundary |
| --- | --- | --- |
| One bounded path, reference, or fact lookup | `scout` | Read-only; return a conclusion with locations. |
| Unknown code paths, existing patterns, dependencies | `Explore` | Read-only discovery; parent synthesizes the change. |
| Public/disposable source lookup | `public-scout` | Never private code, user data, unreleased designs, or credentials. |
| Primary-source investigation and cited report | `research` | Follow the research skill; reserve its report path as a write. |
| Precise low-risk fix, test, mechanical refactor | `code-worker` | Parent has already made design decisions; exact scope and checks. |
| Approved interface implementation | `builder` | Follow vibe and relevant design skills, including rendered evidence. |
| UX implementation plan | `Plan` | Read-only planning, not a generic backend architect. |
| Supplied interface screenshots | `Critic` | Read-only visual review, not engineering peer review. |
| Adversarial plan/diff review | `reviewer` | Read-only; preserve the second-lineage requirement for peer review. |
| Broader reasoning or implementation outside these contracts | `general-purpose` | Explicit scope; use only when a narrower specialist is insufficient. |
| Approved multi-part coordination | `workflow` | Check its child-role restrictions; see pi-workstreams. |

Escalate judgment-heavy or security-sensitive work rather than forcing it into
`code-worker`. If overriding model or thinking, follow the current ladder and
explain why; never bypass a role's privacy or tool restrictions. The research
skill specifically retains its named role's model and reasoning defaults.
If a suitable role is unavailable, do the work directly or surface the gap.

## Give a self-contained packet

A new child has no reliable memory of this conversation. Include:

```text
Goal and why it matters:
Repository / working directory and applicable instructions:
Mode: read-only investigation OR implementation (explicitly say which).
Known evidence: paths, symbols, decisions, and approaches already ruled out.
Task: exact question OR exact approved changes and acceptance criteria.
Ownership: allowed write paths; forbidden/shared paths; other active workers.
Inputs: required upstream output and its verified revision, if any.
Checks: relevant formatter, diagnostics, tests, and proof to return.
Stop if: facts contradict the packet, scope must expand, a decision is missing,
         privacy/permissions are uncertain, or verification repeatedly fails.
Return: conclusion, evidence locations, changed files, commands and results,
        unresolved gaps, and integration artifact/branch when applicable.
Git: no staging, commit, push, reset, or cleanup unless explicitly authorized.
Delegation: do not spawn further workers for this bounded task.
```

For discovery, give the question and needed context, not a long speculative
search recipe. For implementation, first inspect the relevant evidence and
choose the change yourself. “Based on your findings, fix it” is not a packet.
Read-only reviewers must not make repairs. Give writers enough context to read
before editing, not permission to redesign adjacent code.

## Launch and coordinate

- Use `Agent` with the exact `subagent_type`, a short description, and the
  packet. Inspect the live schema rather than assuming optional tools exist.
- Set `run_in_background: true` when other useful work can continue. Use false
  only when the very next action depends on the result and there is nothing
  else useful to do. Defaults vary across installations; be explicit.
- Dispatch independent parallel calls in one message. Keep fan-out small enough
  to review the returns. Never parallelize dependent or overlapping writes.
- Record the returned ID and assigned scope. Continue different work while a
  background child runs; do not poll, sleep, or invent its likely result.
- On completion notification, use `get_subagent_result` if the preview is
  insufficient. Use `steer_subagent` for a running child, or the `Agent` tool's
  `resume` argument with its ID after it finishes, when correcting the same
  bounded task (if supported by the live schema). A new child needs a fresh
  packet. Do not launch a replacement writer while the first may still write.

## Synthesize and verify

A return is a claim, not proof of completion. Inspect the actual diff or artifact
against the packet, check for unauthorized changes, and validate material
claims against the supplied evidence. Run the narrow relevant checks on the
result being accepted; passing worker-local tests does not establish that
integrated changes pass. Do not repeat the entire discovery exercise merely
to demonstrate oversight.

On missing evidence, request it. On a failed approach, identify the failed
assumption before a bounded retry; repeated failure means escalation or a
blocker, not an endless agent loop. Resolve contradictory findings yourself
against the source, or ask the user when a requirement is genuinely undecided.
Report what was verified and what remains uncertain, not merely “agent done.”

## Fit into normal work

- Normal implementation, debugging, and TDD still own their engineering loop;
  delegation changes who performs a slice, not its acceptance criteria.
- `vibe` owns UI planning/build/visual review. Keep its role contracts and proof.
- `self-review` owns the in-lineage plan check; `peer-review` owns adversarial
  cross-lineage plan review. Use `code-review` for its standards/spec diff review.
- `execute-plan` owns hands-off execution of a supplied checklist, including its
  checkpoint policy. This skill supplies Pi routing, not a second execution
  loop. Follow its Pi verification exception rather than the general
  no-reinspection shortcut.
- `handoff` creates session-continuity documents; a worker packet is not a
  request to create one.
