# Global agent preferences

These preferences apply across tools and repositories. Repository facts, commands and workflows belong in the repository's own `AGENTS.md`; directory-specific rules go in the nearest nested instruction file.

## Scope

Order of precedence: my explicit instructions, then the project's `AGENTS.md`, then this file. Apply this file only where it does not conflict with the first two.

When instructions conflict, take the safer option (the less destructive or more reversible one) and tell me about the conflict.

Before touching files outside the request, name them and ask.

## Blockers and decisions

When you stop for a blocker or a decision, open with one plain-English sentence on what happened and one on what you need from me. Identifiers (env vars, flags, paths, test names) come after those two sentences.

## Delegation

Use the least capable agent and model that can do the task reliably. When delegating, load `skill://specialist-delegation`.

When acting as a delegated agent in a live UI, emit a brief phase update before substantial work (inspecting, implementing, verifying). Report actions and results only, not private reasoning.

## Maintaining these instructions

Add a rule here when the same correction or mistake is likely to recur across projects. Keep each rule concrete, short and testable. Remove rules that are stale, duplicated, project-specific or no longer useful.

## Personal voice

Use my voice only when I explicitly ask for it or when the output is clearly meant to be sent or published under my name, such as an email, message, post, personal essay, bio or social copy.

For everything else (answers, explanations, plans, code, technical documentation), use the default concise style. If it is unclear whether something should sound like me, ask before applying my voice.

## 1Password secrets

Never ask me for a 1Password service-account token or to paste a secret that 1Password holds.

On the homelab box (hostname `homelab`), read secrets with `OP_SERVICE_ACCOUNT_TOKEN="$(cat ~/.config/op/homelab-box-ro.token)" op read 'op://Homelab/<item>/<field>'` (read-only token, `Homelab` vault only; homelab ADR-0036). Never export the token or echo the value; write it straight to its destination file.

Ask me only when the secret is outside the `Homelab` vault or the read fails.

## Authorship and attribution

When writing commit messages, never auto-add the agent's name as co-author.
