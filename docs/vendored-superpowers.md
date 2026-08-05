# Vendored superpowers skills

Thirteen skills under `skills/` come from the **superpowers** plugin by Jesse
Vincent, vendored from `superpowers@claude-plugins-official` at version 6.2.0:

`brainstorming`, `dispatching-parallel-agents`, `executing-plans`,
`finishing-a-development-branch`, `receiving-code-review`,
`requesting-code-review`, `subagent-driven-development`,
`systematic-debugging`, `test-driven-development`, `using-git-worktrees`,
`verification-before-completion`, `writing-plans`, `writing-skills`.

Upstream: <https://github.com/obra/superpowers>

## Why they are copied rather than installed

The plugin ships a `SessionStart` hook (matcher `startup|clear|compact`) that
injects the whole `using-superpowers` skill body — 481 words, about 650 tokens —
into every session, and again after every `/clear`. On this machine a token
added to context is re-read about 29 times, so that is roughly 19K tokens per
session before any work happens, and the `/clear`-at-every-task-boundary rule in
`global-CLAUDE.md` makes it fire more often, not less.

Claude Code has no way to disable a single hook from a plugin. `settings.json`
has `skillOverrides` for individual skills but no `hookOverrides`; the only
switch is `disableAllHooks`, which would also kill `trim-tool-output.py`,
`context-budget.py` and the `Grep|Glob` discovery gate. Disabling the plugin and
copying the skills without its `hooks/` directory is the only way to keep the
skills and drop the injection.

`using-superpowers` itself is deliberately **not** vendored. It exists to nag
Claude into checking for skills, which is what the hook was injecting; the skill
list is already in context on every request without it.

## What this costs

Skill updates no longer arrive automatically. To refresh:

```bash
git clone --depth 1 https://github.com/obra/superpowers /tmp/superpowers
# diff, then copy the skills listed above, excluding hooks/
rm -rf /tmp/superpowers
```

After copying, rewrite any `superpowers:<name>` cross-references to the bare
`<name>` — the plugin namespace no longer resolves — and rebuild the zips with
`./scripts/build-zip.sh <name>`.

## Licence

MIT, Copyright (c) 2025 Jesse Vincent. The full text ships upstream at
<https://github.com/obra/superpowers/blob/main/LICENSE>; a copy is kept beside
this note at `vendored-superpowers-LICENSE`.
