# Phase 1 — deterministic evidence

A fixed command menu, run before any model interpretation happens. Every
command below carries an explicit output cap and a measured rough token cost
(bytes ÷ 4). Run the menu as written — don't improvise a substitute command
because it "should" work; if a tool is absent, take its **named fallback**,
not silence. Every command that ran and every command whose tool was absent
both get recorded into the payload's `tools.used` / `tools.absent` (see
`BLOCKS.md`'s top-level envelope) and rendered in `shell.html`'s footer. A
document that used `scc` looks different from one that fell back to the
extension histogram, and the reader is told which one they're looking at —
that difference is never allowed to disappear silently.

## Tool inventory

`command -v <tool>` each one **on the machine actually running `/orient`**
before trusting this table — it is a snapshot of one machine on one date,
not a promise. Measured 2026-08-02 on the author's Mac:

| Tool | Role here | Status (this machine) |
| --- | --- | --- |
| `git` | primary evidence source for everything below | present |
| `rg` | non-git-repo fallback for the file listing | present |
| `gh` | optional stamp enrichment (platform-stated language/description) | present |
| `jq` | current-state manifest snapshot (pairs with dependency archaeology) | present |
| `node` | not invoked by this file | present |
| `python3` | intent-corpus body filter | present |
| `scc` | language-mix enrichment (`--format json` only) | **absent** |
| `tokei` | same role as `scc`, alternative implementation | **absent** |
| `cloc` | same role as `scc`, alternative implementation | **absent** |
| `graphviz`/`dot` | not used — `flow`/`map` are hand-rolled in `shell.html` (see `BLOCKS.md`) | **absent** |
| `pydeps` | not used, same reason | **absent** |
| `code2flow` | not used, same reason | **absent** |

Net effect: the git-native path below is **primary**, not a fallback-of-last-resort.
`scc`/`tokei`/`cloc` are enrichment only, and on this machine none of them ran —
the extension histogram is the language-mix evidence that actually shipped.
`graphviz`/`pydeps`/`code2flow` need no fallback; nothing in this skill calls them.

---

## 1. Stamp

Fills `payload.repo`. Six tiny commands, ~25 tokens total.

```bash
git rev-parse --is-inside-work-tree   # exit 128 + "not a git repository" on stderr => repo.vcs: null, skip the rest of this file
git rev-parse HEAD                    # repo.sha
git rev-parse --abbrev-ref HEAD       # repo.branch ("HEAD" back means detached)
git rev-list --count HEAD             # repo.commitCount; nonzero exit on a shallow clone => null
git remote get-url origin             # repo.remoteUrl; nonzero exit (no remote configured) => null
date -u +%Y-%m-%dT%H:%M:%SZ           # repo.builtAt
```

Optional enrichment, ~40 tokens, only when `gh` is present and authenticated
(`gh auth status`). Gives a platform-stated language and description as a
cross-check against the extension histogram below — a repo GitHub calls
"Shell" while the histogram says mostly `.py` is itself a signal.

```bash
gh repo view --json description,primaryLanguage,isPrivate,defaultBranchRef -q '.'
```

Nonzero exit (no `gh`, unauthenticated, no remote, offline) — skip it. The
stamp still has everything it needs from `git`.

## 2. Intent corpus

Subjects, capped at 300 commits and a 12,000-byte backstop (≈3,000 tokens,
usually far less — 300 short subject lines rarely get close):

```bash
git log --format='%s' -n 300 | head -c 12000
```

Bodies, but only the ones worth reading: a one-line body is noise (most
commits don't need one), a multi-line body is where the author explains
themselves. Filter for length > 1 line, then a 20,000-byte hard cap
(≈5,000 tokens) as a backstop against a repo that writes long bodies for
nearly every commit — this filter alone doesn't bound the output, the cap
does:

```bash
git log --format='%h%n%s%n%b%n---' -n 200 | python3 -c "
import sys
recs = sys.stdin.read().split('\n---\n')
for r in recs:
    r = r.strip('\n')
    if not r.strip():
        continue
    lines = r.split('\n')
    if len(lines) < 2:
        continue
    body = lines[2:]
    while body and not body[-1].strip():
        body.pop()
    if len(body) > 1:
        print('\n'.join(lines[:2] + body))
        print('---')
" 2>/dev/null | head -c 20000
```

(`2>/dev/null` is load-bearing, not decoration: when the cap actually binds,
`head` closes the pipe early and Python logs a `BrokenPipeError` to stderr on
exit — harmless, but noise this file's own cap-testing surfaced on a real
repo. Silencing it keeps only the 20,000 bytes of evidence in context.)

Measured on this repo: 107 commits in the last 200 have a multi-line body
(house style writes why-first bodies), which saturates the 20,000-byte cap.
Expect this cap to bind on any repo with verbose commit discipline — that's
the intended behavior, not a bug to raise the cap for.

## 3. Dependency archaeology

Every dependency added or removed is a dated decision, so this reads history
(`git log -p`), not current state. One command, all manifest kinds at once,
`-U0` to drop unchanged context lines, vendor/build directories excluded so
a repo that accidentally committed `node_modules` doesn't blow the cap (this
happened while testing this file, on a real repo — the naive glob
`*/package.json` alone pulled in 60+ vendored `package.json` files and a
241,694-byte diff), and an 8,000-byte hard cap (≈2,000 tokens) as backstop:

```bash
git log -p -U0 --format='%h %ad %s' --date=short -- \
  package.json '*/package.json' \
  pyproject.toml '*/pyproject.toml' \
  requirements.txt '*/requirements.txt' \
  Cargo.toml '*/Cargo.toml' \
  go.mod '*/go.mod' \
  Gemfile '*/Gemfile' \
  pom.xml '*/pom.xml' \
  ':(exclude)**/node_modules/**' ':(exclude)**/vendor/**' \
  ':(exclude)**/dist/**' ':(exclude)**/target/**' ':(exclude)**/.venv/**' \
  | head -c 8000
```

Lockfiles (`package-lock.json`, `*.lock`, `Cargo.lock`) are deliberately
excluded — auto-generated, and the diff is transitive-dependency noise, not
an authored decision.

Pairs with a current-state snapshot for whichever manifest kind is actually
present, so archaeology (what changed) and state (what's true now) don't
have to be reconciled by eye. For a JSON manifest, `jq` picks the fields
that matter and skips the rest (~250 tokens); for anything else, the file is
small enough to read whole:

```bash
test -f package.json && jq -r '{name, description, dependencies, devDependencies} | to_entries[] | "\(.key): \(.value)"' package.json
```

If no manifest of any kind exists, both commands above produce empty output
on a normal exit — that's the correct, silent answer for a repo with no
tracked third-party dependencies (this repo is one), not a failure.

## 4. Language mix (the `scc` enrichment, and its fallback)

If `scc` is present:

```bash
scc --format json
```

**Never `scc --by-file`** — per-file output runs 12,000–16,000 tokens of
noise for a modest repo, and per-file granularity belongs to
`maintainability-review triage`, not here.

`scc` was absent on the test machine, so the language mix shipped as the
extension histogram instead — tracked files only, git-native, no scc/tokei/cloc
required. Capped at 30 lines (a repo with more than 30 distinct extensions is
itself worth a `flag`, not a longer table): ~25 tokens measured on this repo.

```bash
git ls-files | grep -oE '\.[A-Za-z0-9_]+$' | sort | uniq -c | sort -rn | head -30
```

`git ls-files` needs a git repo. If `repo.vcs` came back null in step 1,
substitute `rg --files` (respects `.gitignore` the same way); if `rg` is
also absent, `find . -type f -name '*.*'` is the last fallback, uglier but
functionally identical for this purpose:

```bash
rg --files | grep -oE '\.[A-Za-z0-9_]+$' | sort | uniq -c | sort -rn | head -30
```

`tokei`/`cloc` play the identical enrichment role `scc` does; if either is
present instead, use its own JSON/machine-readable flag and skip the
extension histogram. Never run more than one language-mix tool — they answer
the same question.

## 5. First-seen-per-file

When each tracked file first entered history — `--diff-filter=A` restricts
the log to add-events only. Newest-first (default git order), capped at 150
lines (≈800 tokens measured on this repo; scales with repo size, which is
exactly why the cap exists):

```bash
git log --diff-filter=A --format='%h %ad' --date=short --name-only | head -150
```

This is provenance evidence ("when did this area of the repo start
existing"), not a churn count — it says nothing about how often a file
changed after it first appeared. That's section 6, and only at directory
granularity.

## 6. Effort distribution — directory granularity only

Where commits touched, collapsed to the top-level path segment
(`cut -d/ -f1`). Capped at 30 rows (~100 tokens measured on this repo):

```bash
git log --format='' --name-only | grep -v '^$' | cut -d/ -f1 | sort | uniq -c | sort -rn | head -30
```

**Per-file churn is explicitly out of scope for this file.** That level of
detail is `maintainability-review triage`'s job, not Phase 1's — this
command answers "which area of the repo has absorbed the work," not "which
file." Do not narrow the `cut` field or add a `--name-only` per-file variant
here; if a later phase needs file-level churn, it hands off to that skill
instead of reimplementing it in `/orient`.

---

## Absence rule, restated

Every command above either ran and produced evidence, or its tool was
absent and a named fallback ran instead — there is no third outcome. Roll
both lists into `tools.used` / `tools.absent` in the payload envelope
(`BLOCKS.md`), and `shell.html` renders both in the footer unconditionally.
A reader comparing two `/orient` runs of the same repo, one with `scc`
installed and one without, should be able to tell which is which from the
footer alone, without diffing the bodies.

Measured total for this repo's actual Phase 1 run, every cap included where
it bound: ≈7,500 tokens (dominated by the commit-body corpus hitting its
20,000-byte cap, a consequence of this repo's own verbose commit style —
most repos will land well under this).
