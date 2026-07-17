---
name: pr
description: |
  Open a GitHub pull request with the gh CLI. Use when the user types /pr or says
  "open a PR", "raise a pull request", "create a PR", "PR this". Makes sure the
  work is committed and the branch is pushed, derives the title from the branch's
  commits, and writes a why-first body (Summary / Changes / Test plan, plus linked
  issues) in the user's voice — no AI-attribution footer. Supports draft PRs.
user-invocable: true
---

# PR

Open the pull request the user would open. Return the URL when done.

## 1. Preflight

- **Committed?** If the tree is dirty, stop and run `/commit` first (or ask).
- **Not on the base branch.** Never open a PR from `main`/`master`. If the user
  is on the default branch, create a feature branch off it first, then continue.
- **Pushed?** If the branch has no upstream, push it (`git push -u origin <branch>`)
  — same guard rails as `/push`.
- **Base branch** = the repo default (`main` unless it's clearly otherwise).

## 2. Title

Derive it from the branch's commits (`git log <base>..HEAD --oneline`), in the
same house style as commits — `scope: imperative summary`, no emoji. A
single-commit branch reuses that commit's subject verbatim.

## 3. Body

Prose first, in the user's voice. Fill only the sections that carry weight:

```markdown
## Summary

1–3 sentences: what this does and, mainly, why.

## Changes

- concrete change one
- concrete change two

## Test plan

- [ ] how it was verified

Closes #123 ← only if an issue is actually referenced
```

Do **not** add any "Generated with Claude Code" / AI-attribution footer.

## 4. Create

```bash
gh pr create --base <base> --head <branch> \
  --title "scope: summary" \
  --body "$(cat <<'EOF'
## Summary
…
EOF
)"
```

Add `--draft` when the user asks for a draft. Print the returned PR URL. To land
it later, the user runs `/merge`.
