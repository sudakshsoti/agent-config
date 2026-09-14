# Complete the agent-config sprawl audit through Phase 2

Status: proposed execution plan
Owner repository: `agent-config`
Execution worktree: `~/dev/agent-config-sprawl`
Execution branch: `sprawl/phase-0-2`
Parent specification: GitHub issue #33
Implementation tickets: GitHub issues #35–#42
Last reconciled with repository state: 2026-09-14

## Goal

Finish the already-authorised Phase 2 work from
`plans/reduce-agent-config-architecture-sprawl.md`: make the repository's
verification boundary truthful without changing harness behavior beyond the
accepted D1, D6, D8, D9, and D10 decisions.

This plan is deliberately shaped for the vendored `implement` skill. Execute
one numbered slice per fresh `/implement` invocation. Each slice has one
outcome, a fixed spec source, a TDD seam, focused checks, a full-suite gate, and
one reviewable commit.

Phases 3–6 are not part of this plan. They remain separate approval gates after
Phase 2 is merged and its live-apply runbook is available.

## Authority and current-state corrections

Acceptance criteria remain governed by the approved sources:

1. the user's current instruction;
2. issue #33, with its "Corrections found while drafting tickets" comment
   overriding the older body where they differ;
3. the ticket issue for the active slice;
4. `plans/reduce-agent-config-architecture-sprawl.md` for invariants;
5. `handoff/2026-09-14-sprawl-phase-2-tickets.md` as historical context.

This plan controls sequencing and records the evidence-backed state corrections
below. It does not override an approved behavior or acceptance criterion. Stop
for a decision if a state correction would require such an override.

The following ticket and handoff assumptions are now stale:

- Dotfiles commits `a8e23ee`, `89b17d5`, and `9460927` are already on dotfiles
  `main`. Ticket #40 must expect Codex key reconciliation against current
  dotfiles `main` to pass, not fail.
- `docs/ownership.md` and `AGENTS.md` on the sprawl branch still describe the
  dotfiles follow-up as unmerged and `tui.status_line` as written by both
  repositories. Correct those statements in Slices 6 and 8.
- Live-apply step L1 no longer needs to merge the dotfiles branch. The runbook
  should verify that the commits are present and make any targeted `chezmoi
  apply` an explicit user action.
- Do not rely on the dated `/private/tmp` backups named in issue #33. The
  runbook must require fresh durable pre-apply snapshots if those files no
  longer exist.
- Ticket #35's `Blocked by: #1` is a typo. It was blocked by #34, whose code is
  present in commit `36ec58a6`.
- Issue #33 A4 and ticket #35 intentionally permit a cold `check.sh` run to
  prepare its pinned npm dependency. Treat that preparation as an explicit
  parent-spec exception to the broader "hermetic checks" wording: a
  materialized checkout runs hermetically, missing npm produces a truthful
  SKIP, and a cold checkout may need registry access for `npm ci`.

## Non-negotiable boundaries

- Never run `install.sh`, `sync.sh`, `chezmoi apply`, or a live configuration
  merger against the real home from this worktree.
- Never edit credentials, runtime state, or machine-local auth/session files.
- Never absorb the unrelated modified VS Code settings file currently present
  in `~/dev/dotfiles`.
- Do not change Pi/OMP routing, provider behavior, FleetView, sandbox task mode,
  plugin selection, dependencies, or lockfiles.
- Do not regenerate the historical files under `docs/sprawl-baseline/fixtures/`.
- Do not use `git add -A`. Stage only paths named by the active slice.
- Do not push, force-push, merge either repository, apply dotfiles, or close
  issues unless the user asks separately.
- Preserve the current dotfiles/agent-config ownership boundary.

## `/implement` execution contract

Before every slice:

1. Start from a clean `sprawl/phase-0-2` worktree and confirm the preceding
   slice is committed.
2. Record `BASE=$(git rev-parse HEAD)`.
3. Invoke `/implement` with only this plan section and the named GitHub issue as
   the spec. Use `/clear` between slices.
4. Write or extend the focused regression test first and prove that it fails
   for the intended reason before changing production code, unless the slice is
   documentation-only.
5. Run the focused test after each small implementation step. Use `bash -n`,
   `python3 -m py_compile`, Node syntax/test execution, and LSP diagnostics as
   applicable; this repository has no single cross-language typecheck.
6. Run `git diff --check`, then `bash scripts/check.sh` once after the focused
   checks pass. It must leave `git status --porcelain` unchanged.
7. Stage only the slice's files and make a checkpoint commit. The `code-review`
   skill reviews committed `HEAD`, so run `/code-review "$BASE"` against the
   ticket after this checkpoint.
8. Fix every accepted finding, rerun the focused checks, `git diff --check`, and
   the full suite, then amend the checkpoint. Run `/code-review "$BASE"` again.
   Repeat the fix/check/amend/re-review loop until both review axes are clean or
   every rejected finding has a written reason.
9. Inspect `git status --short` after every commit/amend because the pre-commit
   hook may format the working tree. Related formatter output must be staged,
   retested, amended, and re-reviewed; preserve or revert unrelated output.

Suggested invocation:

```text
/implement

Implement only Slice <N> from
plans/complete-sprawl-phase-2.md in the current worktree. GitHub issue #<NN> is
the slice specification; issue #33 and its correction comment supply the
parent acceptance criteria. Follow the plan's current-state corrections and
/implement execution contract. Do not broaden scope, touch live configuration,
push, or close issues.
```

## Preparation gate — reconcile before implementation

This is branch preparation, not an `/implement` slice.

1. Confirm `~/dev/agent-config-sprawl` is clean except for this plan while it is
   under review. Commit the approved plan separately before rebasing, or keep a
   copy outside the worktree and restore it afterward.
2. Fetch `origin`, record `PRE_REBASE_TIP=$(git rev-parse HEAD)` and
   `PRE_REBASE_BASE=$(git merge-base origin/main HEAD)`, and verify the remote
   feature branch has not advanced.
3. Rebase `sprawl/phase-0-2` onto `origin/main` before ticket #35. Because the
   branch is published, record that a later push will require
   `--force-with-lease`; do not push during preparation without explicit user
   approval.
4. Resolve the known conflicts deliberately:
   - keep the sprawl branch's authoritative
     `plans/reduce-agent-config-architecture-sprawl.md`, including its execution
     tracker, while incorporating any newer main wording that does not weaken
     it;
   - accept main's deletion of the five retired 2026-09-08/13 handoffs; do not
     resurrect them;
   - preserve main's Pi observational-memory, keybindings, and settings changes;
   - preserve main's `.idea/` additions without staging them in later slices;
   - retain the branch's ownership baseline, ownership contract, Orca cleanup,
     and ticket #34 implementation.
5. Inspect `git range-diff "$PRE_REBASE_BASE..$PRE_REBASE_TIP"
   "origin/main..HEAD"`, then run `git diff --check`,
   `python3 scripts/test-check.py`, and
   `bash scripts/check.sh`. If integration requires more than mechanical
   preservation of the two sides, stop. Specify the repair as a separate
   `/implement` slice with its own regression test, review, and commit before
   #35; never hide behavior changes in conflict resolution.
6. Review the existing #34 implementation. Prefer a disposable review worktree
   checked out at the rebased equivalent of commit `36ec58a6`, then run
   `/code-review HEAD^` against issue #34. If it finds a blocking defect, add a
   narrowly specified remediation slice before #35; do not fold unrelated
   cleanup into another ticket.

Exit gate: the rebased branch is clean, #34's behavior is accepted, all current
checks pass or have an explicitly documented environment SKIP, and the
following commands confirm ticket #35's pre-state:

```bash
git ls-files node_modules | wc -l    # expected: 13865 before #35
git check-ignore node_modules        # expected: no match before #35
```

## Slice 1 — make `node_modules` a local build product (#35)

**Outcome:** no `node_modules/` path is tracked; `.gitignore` owns the exclusion;
`check.sh` bootstraps with `npm ci --ignore-scripts --no-audit --no-fund` only
when `@earendil-works/pi-tui` is absent, and reports dependency-based SKIPs
truthfully.

**TDD seam:** extend `scripts/test-check.py` first with npm-missing,
node-missing, first-bootstrap, and no-second-bootstrap fixtures. Mark
`scripts/test-operational-footer.mjs` with `// check.sh: requires-npm`.

**Production/docs:** `.gitignore`, `scripts/check.sh`,
`scripts/test-operational-footer.mjs`, `docs/ownership.md` S45,
`docs/ownership.tsv` S45, and index-only removal of tracked `node_modules/`.
Keep `package.json` and `package-lock.json` byte-identical.

**Focused gate:** issue #35's commands plus:

```bash
python3 scripts/test-check.py
git ls-files node_modules | wc -l       # 0
git check-ignore node_modules           # node_modules
git diff --exit-code -- package.json package-lock.json
```

**Commit:** `build: make node_modules a local product (#35)`

## Slice 2 — refuse linked-worktree installs before writes (#36)

**Outcome:** full, selective, and prune installs refuse linked Git worktrees
before writing HOME or shared Git config; `--force` and primary checkouts retain
existing behavior; Git detection failure falls back to the path guard.

**TDD seam:** first add the reusable consumer-set, full-install, real-Git
worktree, and common-`.git/config` snapshot helpers to
`scripts/test-install-selected-skills.py`; then add red refusal/override cases.
Clear inherited `GIT_DIR`, `GIT_INDEX_FILE`, and `GIT_WORK_TREE` in fixtures.

**Production/docs:** `install.sh`, `AGENTS.md`, `docs/ownership.md` D9/S44,
and `docs/ownership.tsv` S44 only.

**Focused gate:** `python3 scripts/test-install-selected-skills.py`, `bash -n
install.sh`, and issue #36's Apple/Homebrew Git spot checks where both binaries
are available.

**Commit:** `install: refuse linked worktrees before writes (#36)`

## Slice 3 — use one shared-skill consumer predicate (#37)

**Depends on:** Slice 2.

**Outcome:** one `shared_root_consumers_present` predicate covers Codex, Pi,
opencode, and OMP for full install, selective install, external links, and
prune. No mode creates `~/.pi/agent/skills`.

**TDD seam:** add the consumer-set × install-mode matrix, external vendor stub,
none case, Pi-only prune, and no-Pi-private-root assertions to
`scripts/test-install-selected-skills.py` before changing `install.sh`.

**Production/docs:** `install.sh`, `AGENTS.md`, `docs/ownership.md` D1 and
install-consumer table, and `docs/ownership.tsv` S03/S04/S31/S42. Do not
regenerate Phase 0 fixtures.

**Focused gate:** `python3 scripts/test-install-selected-skills.py`, `bash -n
install.sh`, and the Pi-only/opencode-only/OMP-only disposable-home checks from
issue #37.

**Commit:** `install: unify shared skill consumers (#37)`

## Slice 4 — retire host OMP overlay links safely (#38)

**Depends on:** Slice 2; execute after Slice 3 to avoid editing the same
installer/test hunks twice.

**Outcome:** full install creates no host `~/.config/omp` overlays; without
`--prune` it reports matching leftovers; with `--prune` it removes only symlinks
resolving into this repository's `omp/overlays/`. Foreign links, regular files,
`.active-overlay`, and the directory survive. Sandbox-bundle delivery remains
unchanged.

**TDD seam:** add no-create, non-prune note, and narrow-prune fixtures to
`scripts/test-install-selected-skills.py` before deleting installer step 3i.

**Production/docs:** `install.sh`, `AGENTS.md`, `docs/ownership.md` D6/S25,
and `docs/ownership.tsv` S25/S26. Do not change the bundle manifest or overlay
contents.

**Focused gate:** issue #38's installer tests plus:

```bash
python3 scripts/test-install-selected-skills.py
python3 scripts/test-build-agent-sandbox-bundle.py
grep -n 'omp/overlays/' sandbox/bootstrap/manifest.txt
bash -n install.sh
```

**Commit:** `install: retire host OMP overlay links (#38)`

## Slice 5 — detect manifest, catalogue, and sync-filter drift (#39)

**Outcome:** hermetic checks reject malformed manifests, explicit external-name
collisions, catalogue name/count drift, and unsafe `sync.sh` sanitization drift.
Bare external sources and repo-owned overlaps remain informational.

**TDD seams:** create fixture tests first for each independent checker:

- `scripts/test-check-manifest.py` for `scripts/manifest.py` and
  `scripts/check-manifest.py`;
- `scripts/test-check-catalogue.py` for `scripts/check-catalogue.py`;
- `scripts/test-sync-settings.py` for the existing `sync.sh` behavior.

Then add the two static checkers to `scripts/check.sh`. Do not change `sync.sh`
behavior or plugin precedence. Update `skills/README.md` only if the new checker
proves the committed catalogue is already inconsistent.

**Docs:** verifier fields for S01/S02/S07/S12 in `docs/ownership.tsv`.

**Focused gate:** every command in issue #39, plus `python3 -m py_compile` for
the new Python files and `bash -n sync.sh scripts/check.sh`.

**Commit:** `check: detect manifest and catalogue drift (#39)`

## Slice 6 — machine-check the ownership contract (#40)

Keep ticket #40 in one `/implement` invocation and one commit so its
`/code-review` compares against the complete issue rather than reporting a
planned second half as missing. Use two internal red-green seams.

**Outcome A — contract and key partition:** `check-ownership.py` validates the
14-column ownership contract, IDs, and agent-config source paths; an authored
dotfiles-key TSV proves the Codex key sets are disjoint; generic environments
may return 77 only when dotfiles is unavailable.

**Outcome B — collision rules:** an importable `ownership_collisions.py`
decodes chezmoi paths and checks collision rules against a committed synthetic
fixture. It does not run chezmoi or inspect the live home.

**Current correction:** remove the obsolete expected-failure assertion against
dotfiles `main@bb3d28f`. Pin local acceptance to a clean temporary dotfiles
worktree at commit `52768cf`, which contains `a8e23ee`, `89b17d5`, and
`9460927`; reconciliation there must pass. Update stale `docs/ownership.md`
text that calls the follow-up unmerged. The unavailable-dotfiles SKIP remains a
portable test case but does not satisfy this plan's local completion gate.

**TDD seams:** first create `scripts/test-check-ownership.py` and
`scripts/test-codex-key-partition.py`, then their production checker/key TSV.
After that seam is green, create the collision fixture and
`scripts/test-ownership-collisions.py`, then implement
`scripts/ownership_collisions.py`.

**Production/docs:** `scripts/check-ownership.py`,
`docs/ownership-codex-keys.tsv`, `scripts/ownership_collisions.py`, its fixture,
all three tests, `scripts/check.sh`, `docs/ownership.md` key-partition/D2/rule-5
text, and `docs/ownership.tsv` S16. Do not edit dotfiles or `.chezmoiignore`.

**Focused gate:** all commands in issue #40, corrected to expect the pinned
worktree to pass; Python compile checks; and an explicit 77/SKIP test for the
unavailable-dotfiles path.

**Commit:** `check: machine-check the ownership contract (#40)`

## Slice 7 — add the opt-in local drift audit (#41)

**Depends on:** Slices 5 and 6. Confirm the import names
`scripts/manifest.py` and `scripts/ownership_collisions.py` before starting.

**Outcome:** `scripts/audit-local.py [--repo] [--home] [--dotfiles] [--json]`
reports every category in issue #41, exits 0 when findings exist, exits 2 only
when the audit cannot run, and never mutates or fetches anything. `check.sh`
discovers its hermetic test but never runs the audit itself.

**TDD seam:** build `scripts/test-audit-local.py` around temporary Git repos and
a fixture HOME. Assert every category, JSON shape, subprocess allowlist, and a
byte-identical recursive snapshot before/after.

**Production/docs:** `scripts/audit-local.py`, `scripts/test-audit-local.py`,
`AGENTS.md` command pointer, `docs/ownership.md`, and `docs/ownership.tsv` S51.
Reuse the parsers from Slices 5 and 6; do not duplicate them.

**Focused gate:** issue #41's hermetic and read-only commands. Treat actual
machine findings as observations, never as changes to repair in this slice.

**Commit:** `audit: report local agent-config drift (#41)`

## Slice 8 — close Phase 2 in documentation (#42)

**Depends on:** every prior slice.

**Outcome:** a current, ordered, user-run live-apply runbook exists; ownership
implementation/status fields and the parent plan say Phase 2 is complete; the
aggregate suite passes.

**Documentation-only seam:** validate every command and link against the final
branch. Prefer `docs/phase-2-live-apply.md` so operational steps are not buried
inside the ownership contract; link it from `docs/ownership.md`.

The runbook must:

- retain P1–P3 and L1–L6 concepts from issue #33 but update L1 to verify the
  already-merged dotfiles follow-up;
- make a targeted `chezmoi apply` an explicit user action, never an agent step;
- require fresh durable snapshots rather than assume `/private/tmp` backups
  survived;
- explain why canonical `npm ci` immediately follows the future agent-config
  merge;
- include verification and rollback for every live step;
- state that none of the live steps were performed by this implementation.

**Other docs:** update D1/D6/D8/D9/D10 status in `docs/ownership.md`, correct the
shared-writer summary in `AGENTS.md`, set the parent plan status accurately, and
tick only Phase 2. Do not mark Phases 3–6 complete.

**Focused/final gate:** issue #42's commands, Markdown diagnostics/link checks,
then:

```bash
python3 scripts/test-install-selected-skills.py
bash scripts/check.sh
git diff --check
git status --short
```

The full run must report zero failures; environment-dependent checks may SKIP
only with the documented reason.

**Commit:** `docs: close architecture sprawl Phase 2 (#42)`

## Final review and handoff

After Slice 8:

1. Build a disposable review worktree from `origin/main`, squash the feature
   branch into one temporary commit whose only issue reference is #33, and run
   `/code-review origin/main` there. This prevents the review skill from
   selecting one of #35–#42 merely because it appears in a slice commit. The
   temporary review commit/worktree is never pushed or merged.
2. Apply accepted findings to the real feature branch through a narrowly scoped
   `/implement` remediation slice, with focused regression coverage,
   `git diff --check`, the full suite, and its own commit. Do not amend unrelated
   historical slice commits.
3. Rebuild the disposable squash from the corrected branch and rerun both
   review axes. Repeat until clean or every rejected finding has a written
   reason.
4. Confirm the branch contains no credential/runtime files and no changes from
   the dirty dotfiles settings file. Re-run Codex-key reconciliation against a
   clean dotfiles worktree pinned at `52768cf`; unlike generic CI, final local
   completion may not substitute the unavailable-dotfiles SKIP.
5. Record exact check counts, SKIPs, retained intentional duplication, and any
   deferred Phase 3–6 work in a short closeout handoff.
6. Stop. Pushing, opening/merging a PR, running the live-apply runbook, and
   beginning Phase 3 all require separate user direction.

## Completion criteria

Phase 2 is ready for merge when:

- tickets #35–#42 are represented by reviewed local commits;
- every `scripts/test-*` is run or truthfully SKIPped by `scripts/check.sh`;
- `node_modules/` is ignored and reproducible without a lockfile change;
- linked-worktree installs fail before writes;
- shared-skill consumer behavior and OMP overlay pruning match the accepted
  ownership contract;
- manifest, catalogue, sync-filter, ownership, Codex-key, and collision drift
  are checked hermetically;
- the optional local audit is read-only and non-blocking;
- the current dotfiles contract reconciles cleanly;
- the runbook documents, but does not execute, live migration and rollback;
- `bash scripts/check.sh` finishes with zero failures and leaves the tree
  unchanged;
- Phase 3–6 work remains explicitly pending.
