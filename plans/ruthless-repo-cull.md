# Ruthlessly cull agent-config

Status: proposed; shared understanding confirmed; no cleanup implemented.

This is a temporary execution plan. Delete this file in the final cleanup commit after every phase and deferred-work handoff is complete.

## Goal

Reduce `agent-config` to the smallest coherent repository that supports **OMP and Pi** without preserving stale harness integrations, generated distributions, machine-local metadata, retired content, or completed planning evidence.

The cull optimizes maintenance burden, navigability, conceptual simplicity, and tracked size equally. When they conflict, prefer the simpler model.

## Measurable outcome

The current tracked tree has 14,154 files. Of those, 13,865 are under `node_modules/`, 40 are generated ZIPs, 20 are retired skill files under `archive/`, and 5 are IDE metadata.

The target is:

- fewer than 250 tracked files, subject to the final merged skill contents;
- no tracked dependency installation, generated skill packages, retired archive, or IDE project state;
- one shared skill root for OMP and Pi: `~/.agents/skills`;
- no standalone Claude, Codex, or OpenCode installation/configuration surface;
- clean-install and explicit-upgrade-prune fixtures for OMP and Pi;
- one current operational story in `README.md` and `AGENTS.md`;
- all retained hermetic checks passing.

This plan does **not** rewrite Git history, so old objects remain recoverable and clone history does not immediately shrink. The current tree and future commits become smaller.

## Confirmed decisions

### Retained architecture

- OMP and Pi remain first-class.
- Shared skills are source-only and are linked once into `~/.agents/skills`.
- OMP and Pi keep their own thin agents, prompts, themes, extensions, settings, routing, and justified differences.
- Retiring standalone Codex and OpenCode harnesses does **not** retire `openai-codex` or `opencode-go` model providers used inside OMP/Pi. Retain OMP overlays such as `omp/overlays/codex-only-overlay.yml` and `omp/overlays/go-overlay.yml`.
- Clean installs and upgrades must work. Upgrade cleanup is explicit through `./install.sh --prune`.
- External skill repositories may remain broad imports when the source is trusted and focused.

### Retained content

- Retain `package.json`, `package-lock.json`, and `pi-token-speed`; `pi/settings.json` consumes the package.
- Retain `skills/frontend-artifact/screenshots/`; the images are runtime reference inputs, not generated debris.
- Retain `design/decisions.md` and `tests/design-intent-cases.md` as current contracts.
- Retain the full explicitly whitelisted design, engineering, writing, personal, productivity, niche-domain, and interviewing skill portfolios except for the removals and merge below.
- Retain all interviewing variants because they are considered crucial.
- Retain `handoff` and skill-discovery/setup helpers.

### Approved removals and consolidation

- Remove standalone Claude, Codex, and OpenCode harness support completely.
- Remove tracked `node_modules/` and ignore it; local installations may be reconstructed with `npm ci`.
- Remove tracked `dist/*.zip` and the ZIP build/check contract.
- Remove `archive/`, `.idea/`, and dated OMP configuration snapshots.
- Remove the sandbox bootstrap, builder, and tests for now. A future sandbox experiment must earn its way back.
- Remove the repo-owned `commit`, `push`, `pr`, `merge`, and `update-branch-name` skills.
- Delete redundant Claude-format `agents/plan-critic.md`; update retained review skills to dispatch native OMP/Pi reviewer roles without consolidating those skills in this effort.
- Merge `n8n-deploy` into `homelab-deploy`; `homelab-deploy` remains the canonical name.
- Include the five pre-existing worktree deletions as intentional cleanup.
- Delete dated acceptance record `tests/frontend-artifact-validation.md`.
- Transfer still-relevant dotfiles-owned work into issues, then delete its copies from this repository.

### Deferred work

Review-skill consolidation is not part of this cull. After this plan is approved, create a separate GitHub issue proposing:

- merge `peer-review` and `self-review` into one plan-review capability;
- keep external `code-review` as the diff/branch review lane;
- fold `maintainability-review` guidance into the appropriate design or code lane;
- preserve native OMP/Pi reviewer dispatch and update all callers.

Do not implement that issue in this plan.

## Safety boundaries

- Use phased, coherent commits so every deletion is recoverable through Git.
- Do not rewrite history, delete remote branches, deploy, or mutate credentials.
- Do not run installation or prune tests against the real home directory; use disposable `HOME` fixtures.
- `--prune` may remove symlinks that point into this repository and copies carrying an unambiguous managed marker. It must refuse or warn on unmarked real files and directories.
- Do not delete or rewrite live `~/.claude/settings.json`, `~/.codex/config.toml`, credentials, sessions, databases, or other unmanaged machine state.
- Preserve unrelated worktree changes. Earlier inspection reported an `AGENTS.md` edit, while the latest `git status --short` did not; re-check immediately before execution and treat any new diff as user-owned.
- Keep machine-local `omp/config.yml.lock` and ignored `vendor/` out of commits.
- Do not hand-edit generated or external content before deleting its contract.

## Execution phases

Each phase should be a separate commit and stop/go gate. Run the phase-specific checks before committing and inspect `git status --short` immediately afterward because the pre-commit hook can modify files.

### Phase 0 — establish the exact baseline and hand off deferred work

**Purpose:** prevent the cull from absorbing unrelated changes or losing active work.

1. Record `git status --short`, the current commit, and `git ls-files | wc -l`.
2. Confirm the only intended pre-existing deletions are:
   - `ux-first-pi-configuration-plan.html`;
   - `plans/fix-stale-pi-footer.md`;
   - `plans/frontend-artifact.md`;
   - `plans/pi-claude-bridge-prompt-capture-rca.md`;
   - `plans/scalable-agent-sandbox-tasks.md`.
3. If any other path is dirty, preserve it outside cleanup commits or stop for review. Never restore or overwrite it automatically.
4. Create the deferred review-consolidation GitHub issue described above.
5. In `~/dev/dotfiles`, create or update issue(s) for still-relevant sandbox/clone-mode work currently described by:
   - `TODO.md`;
   - `plans/scalable-agent-sandbox-user-manual.md`;
   - `handoff/2026-09-14-docker-clone-mode-decision.md`.
6. Copy only actionable requirements and acceptance criteria into issues; do not move historical prose wholesale.
7. Capture the issue URLs in the cleanup commit message or pull-request description, not in a permanent archive file.

**Gate:** the baseline is explicit, unrelated work is protected, and pending work has an owner outside files scheduled for deletion.

### Phase 1 — remove bulk, generated debris, and local metadata

**Purpose:** remove the highest-confidence clutter without changing retained OMP/Pi behavior.

1. Add `node_modules/` to `.gitignore` and remove all 13,865 files from Git tracking. Do not require deleting the local installation.
2. Delete:
   - `dist/`;
   - `scripts/build-zip.sh`;
   - `scripts/check-zips.py`;
   - `archive/`;
   - `.idea/`;
   - `omp/config.2026-08-30.yml`;
   - `omp/config.2026-09-03.yml`;
   - `tests/frontend-artifact-validation.md`.
3. Remove ZIP checks from `scripts/check.sh` and `.githooks/pre-commit` if present.
4. Update `scripts/lint-skills.py` so it validates source skill names, frontmatter, descriptions, and catalogue consistency without requiring ZIPs.
5. Rewrite source-delivery references in:
   - `skills/README.md`;
   - `skills/skill-lifecycle/SKILL.md`;
   - `skills/harness-config-maintenance/SKILL.md`;
   - any retained skill found by `git grep -nE 'dist/|build-zip|check-zips|\.zip' -- skills scripts README.md AGENTS.md`.
6. Preserve `skills/frontend-artifact/screenshots/` and verify every referenced `reference.png` still exists.

**Checks:**

```bash
npm ci
python3 scripts/lint-skills.py
git grep -nE 'build-zip|check-zips|dist/[^ ]+\.zip' -- ':!plans/ruthless-repo-cull.md' || true
git ls-files node_modules dist archive .idea
git diff --check
git status --short
```

**Gate:** the listed generated/local paths produce no tracked output, npm installation is reproducible, and source-skill lint passes.

### Phase 2 — retire standalone Claude, Codex, and OpenCode surfaces

**Purpose:** collapse the repository from a multi-harness compatibility matrix to OMP/Pi plus shared skills.

1. Delete standalone harness sources:
   - `CLAUDE.md`;
   - `agents/`;
   - `codex/`;
   - `settings.json`;
   - `sync.sh`;
   - `claude-powerline.json`.
2. Delete Claude/Codex-only scripts and tests:
   - `scripts/apply-codex-config.py`;
   - `scripts/test-apply-codex-config.py`;
   - `scripts/statusline.sh`;
   - `scripts/subagent-statusline.sh`;
   - `scripts/test-subagent-statusline.sh`.
3. Retain Pi's `scripts/test-operational-footer.mjs`; it tests `pi/extensions/operational-footer/index.js` and is not a Claude statusline test.
4. Remove every `marketplace` and `plugin` declaration from `plugins.txt`. Retain external declarations and rewrite their comments for OMP/Pi delivery through `~/.agents/skills`.
5. Rewrite `install.sh` around three destinations only:
   - shared skills: `~/.agents/skills`;
   - OMP configuration: `~/.omp/agent` and its established overlay destinations;
   - Pi configuration: `~/.pi/agent`.
6. Delete installer variables, branches, merges, prompts, agents, settings, plugin commands, and permissive-posture checks for `~/.claude`, `~/.codex`, and `~/.config/opencode`.
7. Preserve external checkout behavior in ignored `vendor/`, including deterministic repo-owned name precedence.
8. Make `--skills-only=name,...` install only named repo-owned skills into `~/.agents/skills`, without unrelated harness writes or external fetches.
9. Rewrite `--prune` to:
   - prune dangling or no-longer-declared managed links in `~/.agents/skills`, OMP, and Pi;
   - remove retired Claude/Codex/OpenCode symlinks only when they point into this repository;
   - remove copied files only when an existing marker proves agent-config ownership;
   - warn and leave unmarked real files/directories untouched;
   - remain idempotent.
10. Rewrite `README.md` and reconcile `AGENTS.md` to describe OMP/Pi only, shared-skill ownership, externals, source-only delivery, prune safety, and machine-local secret boundaries.
11. Retain `global-agents.md`; it is harness-neutral. Link it only to OMP and Pi destinations.
12. Rewrite retained skill prose that names Claude/Codex/OpenCode mechanisms. Do not remove provider IDs such as `openai-codex/*` or `opencode-go/*` from OMP/Pi routing.
13. Update `skills/self-review/SKILL.md` and `skills/peer-review/SKILL.md` to invoke the native OMP/Pi critic/reviewer role instead of deleted `agents/plan-critic.md`. Do not merge the skills here.
14. Delete `scripts/test-apply-codex-config.py` from `scripts/check.sh`; retain Pi web-search, OMP policy, Pi extension, and other retained checks.

**Fixture checks:**

```bash
tmp_home="$(mktemp -d)"
mkdir -p "$tmp_home/.omp/agent" "$tmp_home/.pi/agent"
HOME="$tmp_home" ./install.sh
HOME="$tmp_home" ./install.sh --prune
HOME="$tmp_home" ./install.sh --prune
find "$tmp_home/.agents" "$tmp_home/.omp" "$tmp_home/.pi" -maxdepth 4 -type l -print
rm -rf "$tmp_home"
```

Add targeted fixtures before considering the phase complete:

- clean install produces only OMP/Pi/shared-skill destinations;
- a simulated old repo-pointing Claude/Codex/OpenCode symlink is removed by `--prune`;
- an unmarked real file at a retired destination is preserved with a warning;
- repeated prune is a no-op;
- selective installation and full installation agree on the shared skill destination.

**Gate:** no standalone retired-harness path is installed or documented, retained provider routing is unchanged, and destructive prune cases are covered.

### Phase 3 — remove the sandbox experiment from this repository

**Purpose:** stop carrying an implementation whose owner and survival are not yet settled.

1. After Phase 0 transfers actionable work, delete:
   - `sandbox/`;
   - `scripts/build-agent-sandbox-bundle.sh`;
   - `scripts/test-build-agent-sandbox-bundle.py`.
2. Remove the sandbox test from `scripts/check.sh`.
3. Remove sandbox bundle/install claims from `README.md`, `AGENTS.md`, `TODO.md`, plans, handoffs, and retained skills.
4. Do not add replacement launchers, bundles, manifests, or compatibility stubs. The dotfiles issue is the only forward pointer.

**Checks:**

```bash
git grep -nE 'sandbox/bootstrap|build-agent-sandbox-bundle' -- ':!plans/ruthless-repo-cull.md' || true
git ls-files sandbox
git diff --check
git status --short
```

**Gate:** no tracked bootstrap or repository check depends on the retired experiment.

### Phase 4 — simplify the retained skill catalogue

**Purpose:** remove explicitly rejected workflow skills and consolidate only the approved deployment pair.

1. Delete repo-owned skills:
   - `skills/commit/`;
   - `skills/push/`;
   - `skills/pr/`;
   - `skills/merge/`;
   - `skills/update-branch-name/`.
2. Remove their catalogue entries, cross-skill references, installer assumptions, and any OMP ignored-skill entries.
3. Merge `skills/n8n-deploy/` into `skills/homelab-deploy/`:
   - keep `homelab-deploy` as the name and directory;
   - preserve shared deployment safety once;
   - make general Caddy/Docker and n8n workflows explicit modes/sections;
   - delete `skills/n8n-deploy/` and update all callers.
4. Keep all interviewing variants, including repo-owned `grilling` and `design-grill` and the external document-backed variant.
5. Keep `find-skills`, external setup/ask helpers, `handoff`, the full selected design stack, broad engineering toolkit, and full personal/niche cluster.
6. Do not perform review-skill consolidation; only repair references broken by deleting `agents/plan-critic.md`.
7. Reconcile `skills/README.md` against the actual source directories.

**Checks:**

```bash
python3 scripts/lint-skills.py
git grep -nE 'skills/(commit|push|pr|merge|update-branch-name|n8n-deploy)' -- ':!plans/ruthless-repo-cull.md' || true
git diff --check
git status --short
```

**Gate:** the source catalogue has no orphan references, the deployment merge preserves both approved workflows, and no other whitelisted skill was removed.

### Phase 5 — finish the document cull

**Purpose:** leave only current operating guidance and durable contracts.

1. Commit the five accepted pre-existing deletions, repairing the stale `TODO.md` reference to the deleted Pi/Claude bridge RCA before removing `TODO.md` itself.
2. After their active requirements are implemented or transferred, delete:
   - `TODO.md`;
   - `plans/reduce-agent-config-architecture-sprawl.md`;
   - `plans/scalable-agent-sandbox-user-manual.md`;
   - `docs/repo-sprawl-audit-plan.md`;
   - `handoff/2026-09-14-docker-clone-mode-decision.md`.
3. Keep:
   - `design/decisions.md`;
   - `tests/design-intent-cases.md`.
4. Ensure retained README, AGENTS, design decisions, tests, skill docs, OMP docs, and Pi docs describe only current behavior. Git is the archive; do not add tombstones or a legacy directory.
5. Delete this plan file only in the final closeout commit, after all of its checks and issue handoffs are complete.

**Gate:** every remaining prose file is current operational guidance, a durable decision, or an active executable/acceptance contract.

### Phase 6 — repository-wide verification and closeout

Run proactive diagnostics on changed source files before shell tests, then run the full retained suite.

```bash
./scripts/check.sh
npm ci
git diff --check
git status --short
git ls-files | wc -l
git ls-files node_modules dist archive .idea sandbox codex agents
git grep -nE '~/.claude|~/.codex|~/.config/opencode|claude plugin|check-zips|build-zip' -- \
  ':!plans/ruthless-repo-cull.md' || true
```

Also verify manually:

- OMP base config, overlays, agents, themes, keybindings, LSP settings, provider IDs, roles, and fallback chains are unchanged except for removed standalone-harness prose.
- Pi settings, extensions, agents, prompts, themes, keybindings, web-search merge safety, and `pi-token-speed` remain functional.
- `~/.agents/skills` contains each retained repo-owned/external skill once after a disposable clean install.
- `./install.sh --prune` does not mutate unmarked real files or credential-bearing state.
- no tracked path is generated by `npm ci` or by running the retained checks.
- the tracked file count is below the target or every excess file has a named current purpose.
- each phase is independently revertible.

After final verification:

1. record the commands and results in the final commit or pull-request description;
2. confirm the review-consolidation and dotfiles issue URLs are accessible;
3. delete `plans/ruthless-repo-cull.md`;
4. rerun `./scripts/check.sh` and `git diff --check`;
5. inspect `git status --short` after the final commit for hook-created changes.

## Planned commit sequence

1. `chore: remove generated and local repository clutter`
2. `refactor: narrow installation to omp and pi`
3. `chore: remove the sandbox bootstrap experiment`
4. `refactor: simplify the retained skill catalogue`
5. `docs: remove superseded repository work records`
6. `chore: close out repository cull`

Do not add agent co-author attribution.

## Completion criteria

The cull is complete only when:

- all phase gates pass;
- OMP and Pi clean-install and upgrade-prune fixtures pass from disposable homes;
- no standalone Claude, Codex, or OpenCode harness surface remains;
- model providers used by OMP/Pi remain intact;
- all generated, archived, IDE-local, sandbox, and rejected skill paths are untracked;
- every remaining file has current OMP/Pi, shared-skill, verification, or durable-decision value;
- deferred work exists as issues rather than stale repository documents;
- the temporary culling plan itself has been deleted;
- the working tree is clean except for explicitly identified user-owned changes.
