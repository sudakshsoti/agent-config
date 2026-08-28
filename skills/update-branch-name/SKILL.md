---
name: update-branch-name
description: |
  Rename the current git branch to fit a naming convention — a semantic
  prefix (feat/fix/chore/docs/...) plus a kebab-case slug — and keep the
  remote, any open PR, and local tracking in sync. Use when the user types
  /update-branch-name or says "rename this branch", "fix the branch name",
  "this branch needs a prefix", or gives a specific new branch name. Refuses
  to touch main/master, and prefers GitHub's server-side rename so an open
  PR isn't orphaned.
user-invocable: true
disable-model-invocation: true
---

# Update Branch Name

Rename the current branch to fit a naming convention, without the damage a
naive rename does: `git branch -m` plus a manual remote push-and-delete
orphans any open PR — GitHub closes a PR when it sees its head branch
disappear — and leaves other clones or worktrees tracking a branch that no
longer exists.

## 1. Know where you are

- `git branch --show-current`. If it's `main`/`master` (or the repo's default
  branch), refuse — this is for feature branches. Offer to create one
  instead.
- `git worktree list --porcelain`. If another worktree has this branch
  checked out, `git branch -m` will fail outright — say so up front rather
  than letting git's own error stand in for an explanation.

## 2. Land on the new name

Default convention — semantic prefix + kebab-case slug, Conventional-Commits
style:

`feat/ fix/ chore/ docs/ refactor/ test/ perf/ build/ ci/` + `short-kebab-slug`

- If the user gave an exact name, validate it (below) and use it as-is.
- If they gave a description instead of a name ("rename it to something
  about the auth fix"), infer the type from what the branch actually
  contains — `git log <base>..HEAD --oneline`, `git diff --stat` — and
  slugify the rest.
- If the repo already has a visible convention — other branch names, or the
  user states one (`username/description`, `TICKET-123-description`) — match
  that instead of imposing Conventional Commits on a repo that doesn't use
  it.
- If the computed new name equals the current name, say so and stop; nothing
  to do.

**Valid git ref name:** lowercase, hyphens not underscores or spaces, no
`..`, `~`, `^`, `:`, `?`, `*`, `[`, no leading/trailing `/` or `.`, no `@{`,
doesn't end in `.lock`. Reject and re-derive rather than silently mangling a
name that fails this.

## 3. Check what's at stake before touching the remote

- `git status -sb` (or `git rev-parse --abbrev-ref <branch>@{u}` — errors if
  there's no upstream) — has this branch ever been pushed? If not, this is a
  same-machine-only rename: go to 4a, nothing else applies.
- If it has an upstream: `gh pr view <old-name> --json number,url 2>/dev/null`
  — is there an open PR? This decides the path in step 4.

Renaming a pushed branch touches shared state — confirm the new name with the
user before running step 4b or 4c.

## 4a. Local-only rename (never pushed)

```bash
git branch -m <old> <new>
```

Nothing else references the old name. Done.

## 4b. Pushed, `gh` available, GitHub remote

Prefer GitHub's server-side rename endpoint over a manual push+delete — it
moves the branch and re-points any open PR and branch-protection rule in one
step, with no window where the remote has neither name:

```bash
gh api -X POST "repos/{owner}/{repo}/branches/<old>/rename" -f new_name=<new>
git branch -m <old> <new>
git fetch origin --prune
git branch --set-upstream-to=origin/<new> <new>
```

`{owner}/{repo}` — leave literal; `gh api` fills these in from the current
repo context. If `<old>` contains `/`, pass it through as-is; `gh api`
handles the path encoding.

## 4c. Pushed, no `gh` / not a GitHub remote

More caution needed here, since nothing auto-repoints a PR:

- **Open PR exists:** stop and explain — a manual rename (push new, delete
  old) will close that PR the moment GitHub sees the old branch vanish.
  Offer to rename locally only and let the user push the new branch under a
  fresh PR when ready, or proceed only on explicit confirmation that losing
  the PR link is acceptable.
- **No open PR:**
  ```bash
  git branch -m <old> <new>
  git push -u origin <new>
  git push origin --delete <old>
  ```

## 5. Report

State the old and new name, whether the remote and any PR moved with it, and
flag what the tool can't reach: other clones or worktrees still tracking
`<old>` need their own `git fetch --prune` plus `git branch -m` (or a fresh
checkout) to catch up.
