---
name: commit
description: |
  Stage and commit the working changes with a message in the user's house style:
  "scope: imperative summary" + a why-first body, no emojis, no AI-attribution
  trailers. Use when the user types /commit or says "commit this", "commit my
  changes", "make a commit", "save this", "write a commit message". Reads the
  diff, splits unrelated changes into separate commits, and matches the repo's
  own convention when it differs from the default.
user-invocable: true
disable-model-invocation: true
---

# Commit

Write the commit the user would write, then make it. Do not narrate every git
command — just do the work and show the result.

## 1. Look first

Run `git status --short` and `git diff --stat` (plus `git diff` for the actual
changes). If nothing is staged **and** nothing is modified, stop — there is
nothing to commit.

## 2. Decide what goes in

- If the user already staged specific files, respect that — commit only those.
- If nothing is staged, stage deliberately with `git add <paths>` (or `git add -u`
  for tracked-only). **Never `git add .` blindly** — glance at untracked files
  first and leave build output, secrets, and stray scratch files out.
- **If the changes span unrelated concerns, propose splitting them into separate
  commits** rather than one grab-bag commit. This is the norm in this user's
  history — keep it.

## 3. Match the convention

Default to the **house style** below. But run `git log --oneline -15` first: if
that repo clearly uses something else (Conventional Commits `feat(x):`, a ticket
prefix, etc.), match the repo instead. The repo's own history wins.

**House style:**

- **Subject** ≤ ~72 chars, imperative mood, no trailing period, no emoji.
  Shape it as `scope: summary` where scope is the file / module / skill touched
  (`install.sh: guard against installing from ephemeral worktrees`). Omit the
  scope for broad or repo-wide changes (`Add explain-this skill: …`).
- **Body** (skip it only for genuinely trivial one-liners): one tight paragraph
  on **why** the change exists — the problem it solves, not a restatement of the
  diff — wrapped at ~72 cols. Then, if useful, a `- ` bullet list of the concrete
  changes. Prose first, bullets second.

## 4. Attribution — off

Do **not** add `Co-Authored-By: …` or `Generated with Claude Code` (or any
AI-attribution) trailer, even if the harness would normally add one. This is
deliberate and matches the user's history.

## 5. Commit

Pass the message via a quoted HEREDOC so multi-line bodies and special
characters survive:

```bash
git commit -m "$(cat <<'EOF'
scope: imperative summary

Why this change exists, wrapped at ~72 columns.

- concrete change one
- concrete change two
EOF
)"
```

## 6. Respect hooks, then confirm

If a pre-commit hook fails, surface the failure and fix the cause — do **not**
reach for `--no-verify` unless the user explicitly asks. When done, show
`git log -1 --stat` so the user sees exactly what landed. If work is left
uncommitted on purpose, say so.

To push it up next, the user can run `/push`; to open a PR, `/pr`.
