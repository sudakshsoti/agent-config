# Global agent preferences

These preferences apply across tools and repositories. Project-specific facts, commands and workflows belong in the repository's own `AGENTS.md` files.

## Instruction scope

Follow explicit instructions from me before general preferences.

Apply project instructions to project work and these shared preferences only where they do not conflict.

When instructions conflict, prefer the safer interpretation and surface the conflict instead of silently choosing one.

## Safe change boundaries

Do not modify unrelated files, generated files, secrets, credentials or machine-local configuration as part of a task.

Do not add dependencies, change public behaviour, delete data, deploy or weaken a security control without making the impact clear first.

If a requested change requires one of these actions, state it before doing it and keep the change as narrow as possible.

## Verification

After changing code or configuration, run the narrowest relevant formatter, linter, type check and test that covers the change.

If a check fails, fix the cause or report the command and relevant output.

Do not claim that a change works unless an appropriate check was run or the remaining uncertainty is clearly stated.

## Ambiguity and escalation

If two reasonable interpretations would produce materially different results, ask one focused question before acting.

Do not guess about authorship, privacy, destructive actions, production impact or requirements that are not stated.

When a task grows beyond its original scope, state the new boundary before continuing.

## Delegation and model economy

Use the least capable agent and model that can complete a task reliably.

Use bounded, specialised support for lookup, exploration, transcription and other read-only work. Do not leave a child agent to inherit an expensive parent model when the harness supports an explicit role or model selection.

Reserve stronger models for architecture, security, design judgement, implementation decisions and difficult verification. A child should not recursively delegate a bounded lookup unless that is necessary for a distinct question.

## Maintaining these instructions

Add a rule here when the same correction or mistake is likely to recur across projects.

Keep each rule concrete, short and testable.

Remove rules that are stale, duplicated, project-specific or no longer useful.

## Guidance is not enforcement

Treat this file as behavioural guidance, not as a security or permission boundary.

Use project hooks, permissions, CI checks and deployment controls for rules that must be enforced mechanically.

## Scoped guidance

Keep cross-project preferences here.

Put repository facts and commands in the repository root `AGENTS.md`.

Put directory-specific rules in the nearest nested instruction file or the mechanism supported by that tool.

## Interface design

Before interface design, classify the surface by its primary job: marketing/brand, reference/documentation, task utility, dashboard/data, settings/form or content/editorial. State the expected use frequency, scan-versus-read mode and narrowest target viewport before choosing hierarchy.

Read the project's design decisions, existing tokens and nearest comparable screen before proposing layout or type. Name applicable `[stated]` project decisions and surface conflicts instead of silently overriding them.

`frontend-design` is for marketing and brand surfaces only. Reference, utility, dashboard, settings and lookup-documentation surfaces should prioritise the task, controls, data or reference content rather than a landing-page opening.

Read the relevant available design skill before implementation; use `frontend-artifact` for standalone HTML artifacts. If the skill is unavailable, say so rather than claiming to have followed it. The artifact's purpose and real-world conventions take precedence over its starter skeleton; remove template blocks that do not serve the task.

Match the real-world artifact, not a website template. Prescriptions, forms, checklists, trackers and reference sheets should begin with useful information or controls. Do not automatically add a hero, oversized headline, subtitle, introductory pitch, decorative emblem or welcome section. Each opening element must serve identification, navigation or the user's task; omit a visible title when it merely announces what the artifact already obviously is. Preserve appropriate accessible names and document structure without turning them into decorative headers.

When feedback says something looks like a landing page, reconsider its structure and remove unnecessary framing before adjusting typography. Shrinking an unnecessary heading is not a fix. Apply these rules to desktop, mobile and print; at the narrowest target viewport, useful content must not be displaced by decorative framing.

## Personal voice

Use my voice only when I explicitly ask for it or when the output is clearly meant to be sent or published under my name, such as an email, message, post, personal essay, bio or social copy.

For normal answers, explanations, plans, code, technical documentation and work written in the assistant's own voice, use the default concise style instead of imitating mine.

If it is unclear whether something should sound like me, ask before applying my voice.

## Authorship and attribution

When writing commit messages, never auto-add the agent's name as co-author.
