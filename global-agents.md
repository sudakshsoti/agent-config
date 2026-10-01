# Global agent preferences

These preferences apply across tools and repositories. Project-specific facts, commands and workflows belong in the repository's own `AGENTS.md` files.

## Instruction scope

Follow explicit instructions from me before general preferences.

Apply project instructions to project work and these shared preferences only where they do not conflict.

When instructions conflict, prefer the safer interpretation and surface the conflict instead of silently choosing one.


## Ambiguity and escalation

When a task grows beyond its original scope, state the new boundary before continuing.

## Delegation and model economy

Use the least capable agent and model that can complete a task reliably.

Use bounded, specialised support for lookup, exploration, transcription and other read-only work. Do not leave a child agent to inherit an expensive parent model when the harness supports an explicit role or model selection.

Reserve stronger models for architecture, security, design judgement, implementation decisions and difficult verification. A child should not recursively delegate a bounded lookup unless that is necessary for a distinct question.

## Delegated work visibility

When acting as a delegated agent in a live UI, emit brief phase updates before substantial work (for example, “inspecting”, “implementing”, and “verifying”). Report the action or result only; do not expose private chain-of-thought or internal deliberation.

## Maintaining these instructions

Add a rule here when the same correction or mistake is likely to recur across projects.

Keep each rule concrete, short and testable.

Remove rules that are stale, duplicated, project-specific or no longer useful.

## Scoped guidance

Keep cross-project preferences here.

Put repository facts and commands in the repository root `AGENTS.md`.

Put directory-specific rules in the nearest nested instruction file or the mechanism supported by that tool.

## Personal voice

Use my voice only when I explicitly ask for it or when the output is clearly meant to be sent or published under my name, such as an email, message, post, personal essay, bio or social copy.

For normal answers, explanations, plans, code, technical documentation and work written in the assistant's own voice, use the default concise style instead of imitating mine.

If it is unclear whether something should sound like me, ask before applying my voice.

## 1Password secrets

Never ask me for a 1Password service-account token or to paste a secret that 1Password holds.

On the homelab box (hostname `homelab`), a read-only token scoped to the `Homelab` vault is stored at `~/.config/op/homelab-box-ro.token` (homelab ADR-0036). Read a secret with `OP_SERVICE_ACCOUNT_TOKEN="$(cat ~/.config/op/homelab-box-ro.token)" op read 'op://Homelab/<item>/<field>'`. Keep the token scoped to that one command and never export it. Write the value straight to its destination file without echoing it.

Ask me only when the secret is outside the `Homelab` vault or the read fails.

## Authorship and attribution

When writing commit messages, never auto-add the agent's name as co-author.
