---
name: update-branch-name
description: "Rename a feature branch to a valid convention while preserving remote tracking, pull-request continuity, worktree alignment, and protection for default branches."
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
- `git worktree list --porcelain`. Note whether this branch sits in a linked
  worktree, and whether that worktree's directory name encodes the old branch
  name — step 5 handles both. Renaming a branch that is checked out in
  *another* worktree is fine: git rewrites that worktree's HEAD for you. It
  does not fail, so don't refuse on those grounds.

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

## 5. Bring the worktree directory with it

Git never renames a worktree's directory when you rename its branch, and
nothing else does either — a worktree manager such as herdr derives the
directory name once, at creation, then leaves it alone. So
`~/.../worktree-green-valley-f1bb` keeps its old name while the branch inside
it is now `chore/film-data-model`. Nothing breaks. It just reads wrong from
then on.

Only do this when the directory name actually encodes the old branch name. If
the user named the directory themselves (`~/work/scratch`), leave it.

Two rules make it safe:

- **Rename the branch first, then move the directory.** The reverse leaves you
  with a dead shell *and* a rollback to do if the branch rename then fails.
- **Run the move from outside the worktree being moved.** The main worktree is
  never the one moving, and it's the first entry of `worktree list`:

```bash
MAIN=$(git worktree list --porcelain | head -1 | cut -d' ' -f2)
git -C "$MAIN" worktree move <old-dir> <new-dir>
```

Build `<new-dir>` by swapping only the slug inside the existing basename,
keeping whatever convention is already there (`worktree-<slug>`,
`<repo>-<slug>`, or a bare `<slug>`). Flatten `/` to `-`, because a slash
would nest a directory instead of naming one: `chore/film-data-model` →
`worktree-chore-film-data-model`.

**Run it from inside the worktree and it exits 1 after having succeeded.** The
directory and git's registry are both already updated, but git's final step
resolves the now-dangling cwd and prints
`error: working directory does not exist: <old-dir>`. Do not read that as a
failure and do not retry — the retry fails for real, since the old path is
genuinely gone by then. Run `git worktree list` before concluding anything.

Never `mv` a worktree directory. Its `.git` file holds an absolute path, so
`mv` severs the link while `git worktree move` updates both sides. If someone
already ran the `mv`, `git worktree repair <new-dir>` relinks it.

## 6. Report

State the old and new name, whether the remote and any PR moved with it, and
whether the worktree directory moved too. Then flag what the tool cannot
reach:

- **Every shell sitting in the old directory, including your own.** A process
  cannot change its parent's working directory, so those shells are now in a
  dangling one and every command there fails until someone runs
  `cd <new-dir>`. Print the exact `cd` line. This is the one piece that cannot
  be automated away.
- Editors, terminal tabs and workspace managers opened at the old path need
  reopening at the new one.
- Other clones or worktrees still tracking `<old>` need their own
  `git fetch --prune` plus `git branch -m`, or a fresh checkout.
