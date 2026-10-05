---
name: specialist-delegation
description: "Use in Pi, OMP or Claude Code when deciding whether to delegate work, selecting specialist subagents, or preparing and verifying a worker handoff. Not for dependencies, edit ownership, or integration across multiple implementation streams (workstreams)."
compatibility: "Pi or Claude Code with the Agent tool, or OMP with the task tool; check the live tool schema and available agent roles."
---

# Specialist delegation

Delegate a bounded outcome, not responsibility for understanding the task. This
skill covers Pi (the `Agent` tool), OMP (the `task` tool) and Claude Code (its
own `Agent` tool). If no delegation tool is available, work directly or report the limitation; do not
invent an API or install another coordinator.

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
load `workstreams` (`skill://workstreams`, [on disk](../workstreams/SKILL.md)) first. Independent lookups do
not need a workflow graph.

## Select by role, permission, and judgment

Inspect the currently available roles and tool schema. In this repository,
Pi routing lives in `pi/agents/*.md` and `pi/model-ladder.md`; OMP mirrors that
ladder in `omp/agents/*.md` plus `task.agentModelOverrides` in `omp/config.yml`,
which takes precedence over agent frontmatter; Claude Code agents are
`claude/agents/*.md`. These are agent-config source paths, not paths to assume
in the target project. In an installed session, inspect available role
definitions (normally `~/.pi/agent/agents/` or `~/.omp/agent/agents/` plus
OMP's bundled agents; Claude Code lists its agents, including built-ins, in
the `Agent` tool description) and the live tool schema. Do not copy model IDs
into packets as permanent policy. Project role overrides may differ. Use the
least expensive capable role, not an unspecified child inheriting the parent
model.
In Claude Code, `scout`, `code-worker` and `builder` carry their own models;
for a built-in, name the `model` the table gives, because an omitted one
inherits the parent's. Where those three are not installed (a work machine
without `--claude-agents`), use `Explore` + `haiku` for `scout` and
`general-purpose` + `sonnet` for the other two.

| Work | Pi role | OMP agent | Claude Code | Boundary |
| --- | --- | --- | --- | --- |
| One bounded path, reference, or fact lookup | `scout` | `scout` | `scout` | Read-only; return a conclusion with locations. |
| Unknown code paths, existing patterns, dependencies | `Explore` | `scout` | `Explore` | Read-only discovery; parent synthesizes the change. |
| Public/disposable source lookup | `public-scout` | `scout` | `scout` | Never private code, user data, unreleased designs, or credentials. |
| Primary-source investigation and cited report | `research` | `research` | `general-purpose` | Follow the research skill; reserve its report path as a write. |
| Precise low-risk fix, test, mechanical refactor | `code-worker` | `code-worker` | `code-worker` | Parent has already made design decisions; exact scope and checks. |
| Strictly mechanical update or data collection | `code-worker` | `sonic` | `general-purpose` + `haiku` | No judgement; exact instructions. |
| Approved interface implementation | `builder` | `builder` | `builder` | Follow vibe and relevant design skills, including rendered evidence. |
| UX implementation plan | `Plan` | `plan` | `Plan` | Read-only planning, not a generic backend architect. |
| Supplied interface screenshots | `Critic` | `critic` | `general-purpose`, read-only packet | Read-only visual review, not engineering peer review. |
| Adversarial plan/diff review | `reviewer` | `adversary` | none: every child is Claude; run `peer-review` from Pi or OMP | Read-only; preserve the second-lineage requirement for peer review. |
| Structured review of recent code changes | `reviewer` | `reviewer` | none: use `code-review` | OMP's bundled `/review` contract; keep its output shape. |
| Broader reasoning or implementation outside these contracts | `general-purpose` | `task` | `general-purpose` | Explicit scope; use only when a narrower specialist is insufficient. |
| Approved multi-part coordination | `workflow` | `workflow` | `Workflow`, only on the user's explicit opt-in | Check its child-role restrictions; see workstreams. |

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

- **Pi:** use `Agent` with the exact `subagent_type`, a short description, and
  the packet. **Claude Code:** the same `Agent` call, plus `model` for a
  built-in; continue a
  finished child with `SendMessage` to its ID. **OMP:** use `task` with the exact `agent`, the shared packet in
  `context`, and one `tasks` entry per assignment (`isolated` requests a
  worktree when enabled). Inspect the live schema rather than assuming optional
  tools exist.
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
  checkpoint policy. This skill supplies harness routing, not a second
  execution loop. Follow its delegation verification rule rather than the
  general no-reinspection shortcut.
- `handoff` creates session-continuity documents; a worker packet is not a
  request to create one.
