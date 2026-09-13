# Reduce agent-configuration architecture sprawl

Status: proposed plan; no implementation started.

## Goal

Reduce the maintenance and reasoning cost of `agent-config` without changing the behavior of Claude, Codex, OMP, Pi, skill delivery, or sandbox bootstrap flows.

The work covers five related concerns:

1. ownership boundaries between `agent-config` and `dotfiles`;
2. skill catalogue, external manifest, ZIP, archive, and vendor lifecycle;
3. duplicated cross-harness policy;
4. plans, handoffs, decisions, runbooks, snapshots, and TODO lifecycle;
5. the repository's verification boundary.

## Why this is worth doing

These are not five equal cleanup projects. The concrete friction is concentrated in a few places:

| Area | Evidence of current friction | Priority |
| --- | --- | --- |
| Ownership | The ownership tables in `agent-config` and `dotfiles` have diverged; some live files have shared writers or special merge rules; full and selective skill installation do not express the same consumer contract. | High |
| Skill lifecycle | The human catalogue can disagree with the committed tree; external declarations and ignored vendor checkouts can drift; duplicate external skill names have ambiguous precedence. | High |
| Cross-harness policy | Routing intent is spread across global instructions, agent definitions, harness configs, overlays, snapshots, and handoffs. Repeated routing changes require reconstructing policy from several formats. | Medium-high |
| Document lifecycle | Current truth, decisions, active plans, historical handoffs, and future manuals are not reliably distinguishable. Some documents describe completed or not-yet-existing behavior as current. | Medium-high |
| Verification | `scripts/check.sh` claims to be comprehensive but omits existing regression tests and does not inspect several drift-prone boundaries. | Medium |

Large file counts, tracked ZIPs, historical snapshots, and archives are not problems by themselves. They become candidates only when ownership, status, or verification is ambiguous.

## Constraints and invariants

All phases must preserve these boundaries unless a separate behavior-change decision is approved:

- Pi remains the daily driver and OMP remains an installed fallback. This plan does not remove either harness.
- Harness-specific capabilities remain different. The plan aligns policy vocabulary; it does not force identical routing behavior.
- Repo-owned, external, plugin, archived, and machine-local skills remain distinct delivery lanes.
- Repo-owned ZIPs remain release artifacts for channels that cannot consume the source tree directly.
- External sources continue to float to their latest upstream revision. Reproducibility changes such as pinning are out of scope.
- Archives and historical configuration snapshots are retained unless a separate retention decision is made.
- Credential-bearing and runtime files remain machine-local. Tracked preference files may continue to merge into live files only through their existing safety contracts.
- `~/.codex/config.toml` keeps its text-preserving merge behavior and top-level TOML placement invariant.
- Pi web-search configuration keeps its credential-safe recursive merge, mode preservation, and idempotence behavior.
- OMP base configuration remains authoritative; overlays remain session-only and non-persistent.
- Global and project-local Pi configuration remain separate scopes.
- Sandbox implementation remains in `dotfiles`; its planning and immutable configuration bundle may remain in `agent-config`.
- No phase silently applies live configuration, updates external repositories, installs plugins, deletes archives, or rewrites user credentials.
- Existing uncommitted work is not absorbed into this effort. Never discard or commit unrelated work on the user's behalf; execute from an isolated worktree or begin only after the user has resolved it.

## Target architecture

The desired end state is not one universal configuration file. It is a small set of explicit contracts:

1. **Ownership contract:** every managed live surface has one source owner, one delivery method, one writeback rule, and one verification owner.
2. **Skill lifecycle contract:** every skill is classifiable as repo-owned, external, plugin-provided, archived, generated, or machine-local, with deterministic collision rules.
3. **Policy contract:** shared role and safety intent is stated once; each harness records only its mapping and justified deviations.
4. **Document lifecycle contract:** readers can distinguish current truth, accepted decisions, active work, operational instructions, and historical evidence.
5. **Verification contract:** the advertised check runs all hermetic repository checks, while machine/network-dependent audits are clearly separate.

## Delivery scope and sequence

`agent-config` is the first implementation scope and will hold the canonical cross-repository ownership contract for agent configuration. `dotfiles` remains authoritative for machine application and receives a separate, explicitly coordinated follow-up only where its local instructions, guards, or tests must change. If the `dotfiles` checkout is unavailable, cross-repository work stops at the accepted contract; the plan must not claim convergence.

The work is delivered as separately approved milestones rather than one architecture branch. Ownership is first because every later phase needs an authoritative source. Existing verification is wired next; ownership-dependent assertions follow only after the Phase 1 contract is accepted. Skill and harness-policy work proceed against those guardrails. Document lifecycle follows after durable decisions exist, avoiding another round of stale documentation.

### Phase 0 — establish a behavioral baseline

**Purpose:** make “no behavior change” testable before moving responsibility or reducing duplication.

1. Start from a clean committed baseline or isolated worktree and record the exact `agent-config` and `dotfiles` revisions used by the effort.
2. Define the ownership-matrix schema before encoding any assertions. It must capture source, destination, delivery, writeback, state classification, and verifier.
3. Produce a named baseline record attached to the first change. It must contain repository revisions, commands run, test results, the managed-surface inventory, disposable-home fixture outputs, and hashes for committed generated artifacts.
4. Inventory managed surfaces for Claude, Codex, OMP, Pi, shared skill roots, sandbox bundle inputs, and machine-local exclusions.
5. Classify each surface by delivery mechanism: symlink, copy-if-absent, merge, generated artifact, external checkout, plugin installation, or intentionally unmanaged state.
6. Capture current full-install and selective-install outcomes in disposable destinations or existing fixtures; never apply them to the live home directory.
7. Run every existing repository test individually, including tests not currently called by `scripts/check.sh`, and record exact commands and results.
8. Keep unrelated dirty files outside the implementation worktree. Never discard, stash, or commit them as part of this plan.

**Exit criteria:** reviewers have a named, revision-pinned baseline record, a complete surface inventory in the agreed schema, reproducible fixture evidence, and exact current test results.

### Phase 1 — settle ownership between `agent-config` and `dotfiles`

**Purpose:** remove ambiguity about where a change belongs and which repository controls each live path.

1. Build one ownership matrix with, at minimum:
   - live destination;
   - canonical source repository and path;
   - delivery mechanism;
   - authority to write or merge;
   - whether the application can write back through a symlink;
   - credential/runtime-state classification;
   - verification owner.
2. Store the canonical cross-repository matrix in `agent-config`. Replace the duplicated full table in `dotfiles` with the minimum machine-ownership rule plus a reference to the canonical contract. If an offline local copy proves necessary, treat it as a generated or mechanically reconciled view rather than a second hand-edited source.
3. Resolve every currently shared or ambiguous path explicitly, especially:
   - `~/.codex/config.toml`;
   - Pi web-search configuration;
   - `~/.agents/skills`;
   - `~/.omp/agent` and `~/.pi/agent`;
   - Codex prompts and agents;
   - Claude settings snapshot/sync behavior;
   - OMP wrappers and overlays.
4. Specify the intended consumer set for full and selective installation. The observed Codex-gated shared-skill behavior is a compatibility issue, not an automatic cleanup: capture it in before/after disposable-home fixtures and require explicit approval before changing it.
5. Identify every agent-config-managed symlink that could collide with chezmoi ownership. Make collision detection explicit and non-destructive; do not let either tool silently claim the other's path.
6. Keep cross-repository sandbox sequencing explicit: `agent-config` owns the portable configuration bundle and planning; `dotfiles` owns launchers, aliases, machine application, and live sandbox operations.
7. Update repository instructions only after the ownership matrix is accepted, then verify that both repositories describe the same contract.

**Exit criteria:** every committed managed surface has one unambiguous owner and delivery rule; any intentional full/selective-install difference is named and fixture-tested; shared-writer paths retain their tested merge semantics; `dotfiles` either references the accepted canonical contract or has a mechanically reconciled view.

### Phase 2 — make the verification boundary truthful

**Purpose:** create guardrails before consolidating catalogues and policy.

1. Define two verification tiers:
   - **hermetic repository checks**, safe for `scripts/check.sh` and CI;
   - **local environment audits**, which may inspect installed symlinks, ignored vendor checkouts, or tool availability but must not mutate them.
2. Bring all existing hermetic regression tests under the advertised entry point, including the operational-footer and subagent-statusline tests.
3. After Phase 1 approval, add coverage for the accepted ownership contract and for intentional full/selective-install equivalence using disposable homes. Do not encode unresolved ownership choices in tests.
4. Add static checks for skill-manifest shape, repo-owned catalogue consistency, distribution ZIP consistency, and collision reporting.
5. Add an opt-in, path-limited, non-networked, read-only local audit for declared versus present vendor checkouts and installed skill links. Missing clones, undeclared checkouts, non-symlink entries, and shadowed names should be reported distinctly. This audit must never repair state and is not a completion blocker.
6. Limit document checks to structured metadata, resolvable local references, and unique identifiers. Represent future-only operations with explicit metadata rather than fragile prose scanning.
7. Keep `scripts/check.sh` exhaustive within the hermetic tier. If a check cannot run in CI without credentials, network access, or a live home directory, list it separately rather than weakening the main check.
8. Ensure one failing check does not prevent the remaining checks from reporting, preserving the current aggregate-result behavior.

**Exit criteria:** `scripts/check.sh` accurately represents all hermetic checks; optional local-state audits are discoverable, non-mutating, and non-blocking; accepted ownership and installation contracts are regression-tested.

### Phase 3 — close the skill lifecycle

**Purpose:** make skill inventory deterministic without collapsing intentionally different delivery lanes.

1. Define the lifecycle states and source of truth for:
   - active repo-owned skills;
   - archived repo-owned skills;
   - external allowlisted skills;
   - Claude-only marketplace plugins;
   - generated ZIPs;
   - ignored vendor checkouts;
   - machine-local runtime/cache state.
2. Define authoritative catalogue metadata before changing the README. Active names and counts come from checked repository inputs; descriptions and rationale remain hand-authored. State whether any rendered catalogue is committed, and require a check that regenerated fields match while preserving hand-authored fields.
3. Preserve the existing first-party invariant: every active repo-owned skill passes lint and has exactly one matching current ZIP; archived and external skills do not acquire ZIP requirements.
4. Validate external declarations without changing their floating-version semantics:
   - source path and allowlisted skill names are structurally valid;
   - duplicate names across external sources are detected;
   - repo-owned shadowing remains deterministic and documented;
   - missing optional local checkouts are distinguished from invalid declarations.
5. Treat same-name external collisions as blocking diagnostics first. Do not introduce or change precedence until the current effective winner is captured in fixtures and an explicit compatibility decision approves the rule.
6. Treat ignored `vendor/` as a cache of declared sources, not as an additional catalogue. The local audit should identify undeclared checkouts and declared-but-absent sources without deleting or fetching anything.
7. Define archive entry and restoration criteria. Preserve provenance and ensure archived names cannot be mistaken for active catalogue entries.
8. Keep release artifact generation reproducible from committed repo-owned skill sources and verify that dirty or untracked skill work is never represented as a committed release baseline.

**Exit criteria:** committed skill inputs are mechanically consistent; external declarations are statically valid; optional local vendor drift is reported with explicit severity; collisions block installation or remain unchanged under an approved, fixture-tested compatibility rule.

### Phase 4 — separate shared policy from harness mechanisms

**Purpose:** reduce routing and instruction duplication while preserving harness-specific behavior.

1. Establish a stable vocabulary for roles and concerns such as main execution, planning, workflow coordination, bounded discovery, routine implementation, adversarial review, architecture/security escalation, fallback, and quota policy.
2. Classify existing statements as one of:
   - shared behavioral or safety invariant;
   - shared routing intent;
   - harness-specific mechanism;
   - machine-local preference;
   - historical rationale.
3. Choose one durable policy source for shared routing intent. Keep model identifiers, file formats, provider restrictions, and unsupported capabilities in per-harness mappings.
4. Map each harness explicitly:
   - Claude plugins, settings, agents, and prompts;
   - Codex defaults, agents, and prompt delivery;
   - OMP authoritative config, roles, fallbacks, and session overlays;
   - Pi default model, per-agent frontmatter, subagent scopes, and lack of OMP-style automatic role/fallback machinery.
5. Record justified deviations rather than normalizing them away. In particular:
   - retain OMP as fallback;
   - retain provider-isolated OMP overlays;
   - retain Pi global versus project-local scopes;
   - retain explicit model overrides where Pi cannot encode an OMP policy.
6. Review `AGENTS.md`, `CLAUDE.md`, and `global-agents.md` as distinct surfaces. Consolidate only clauses that are truly shared; keep harness bootstrap or precedence instructions local to the file that consumes them.
7. Mark dated OMP snapshots and migration handoffs as provenance rather than active policy. Active configuration must be identifiable without date archaeology.
8. Define a small normalized policy representation for verification: role, model/provider, scope, fallback behavior, and documented exceptions. Compare this representation rather than prose or raw configuration formats.
9. Extend verification only where the normalized policy marks equivalence as intended. Tests must not reject documented harness-specific differences.

**Exit criteria:** a reader can understand routing and safety intent from one policy view, then see each harness's mapping and exceptions; normalized before/after fixtures show that no model/provider, role, scope, or fallback behavior changed unintentionally.

### Phase 5 — establish a document lifecycle

**Purpose:** make repository documentation navigable as current truth rather than an undifferentiated chronology.

1. Begin with four reader-facing states: current truth, accepted decisions, active work, and history. Treat runbooks, RCAs, handoffs, and snapshots as formats within those states rather than designing a larger taxonomy first.
2. Require minimal structured metadata: state, owner repository, last verified date or revision, and superseding link when applicable. Future-only manuals or commands must carry an explicit planned marker.
3. Create one small current-state index that points to authoritative ownership, policy, active work, operational instructions, and accepted decisions. It should link rather than duplicate their contents.
4. Promote load-bearing decisions currently buried in handoffs into durable decision records, including Pi/OMP status, model-ladder intent, sandbox containment and ownership, and credential-safe shared-writer boundaries.
5. Reclassify existing plans and handoffs without rewriting their historical claims. Add status or supersession context so completed footer work and old branch/worktree details cannot be mistaken for current instructions.
6. Keep planned commands out of the operational index until implemented and verified.
7. Convert `TODO.md` into a short index of actionable open work linked to its owning plan, RCA, repository, or decision. Do not duplicate full implementation plans in TODO entries.
8. Defer physical archival or deletion rules. For this effort, status and supersession links are sufficient; preserve paths, links, and Git history.
9. Mark historical OMP snapshots as provenance and link them from policy history rather than leaving their status implicit.

**Exit criteria:** current truth, accepted decisions, active work, and history are visibly distinct; TODOs have owners and durable context; structured metadata prevents planned operations from appearing as current.

### Phase 6 — convergence and final behavior audit

**Purpose:** prove that the consolidation reduced ambiguity without changing operation.

1. Run the full hermetic verification suite in each changed repository.
2. Optionally run the path-limited local environment audit and classify findings as expected drift, stale state, or defects; do not auto-repair them or make clean local state a release condition.
3. Compare full and selective install fixtures against the Phase 0 baseline.
4. Compare normalized Claude, Codex, OMP, and Pi policy mappings against the baseline, allowing only approved and documented differences.
5. Verify repo-owned skill ZIPs from committed sources and confirm external/plugin/archive lane semantics remain unchanged.
6. Verify all live-configuration merger tests, including credential rejection, permissions, idempotence, preservation of unmanaged keys, and TOML placement.
7. Review cross-repository references and run the ownership reconciliation check from both changed checkouts.
8. Produce a short closeout record listing accepted decisions, intentionally retained duplication, deferred behavior changes, and non-blocking local drift.

**Exit criteria:** all hermetic checks pass in changed repositories; fixture hashes and normalized policy mappings match the baseline except for approved differences; no live machine configuration was changed; remaining duplication and optional local drift are explicitly classified.

## Change slices and review gates

Keep implementation reviewable and reversible. Each numbered slice requires separate approval and may use a separate branch; do not combine all phases into one branch or commit.

1. **Baseline and ownership decision** — inventory plus accepted boundary; no configuration moves.
2. **Verification truthfulness** — wire existing tests and add contract checks before structural consolidation.
3. **Skill lifecycle** — catalogue and manifest integrity, then optional local diagnostics.
4. **Shared policy model** — establish vocabulary and mappings before reducing duplicated prose.
5. **Document lifecycle** — classify and index existing material after the new decisions are stable.
6. **Convergence** — final cross-repository and behavior-preservation evidence.

At each gate:

- review the diff for behavior-affecting configuration changes;
- run the narrowest relevant checks, then the full hermetic suite;
- keep generated artifacts in the same slice as their authoritative source change;
- stop if effective configuration differs unexpectedly;
- do not apply live configuration as part of validation.

## Explicitly deferred questions

These may be worthwhile later but require separate decisions:

- **Behavior:** removing OMP, changing FleetView, changing routing/fallbacks, merging Pi scopes, replacing delivery mechanisms, auto-applying live configuration, or changing sandbox task mode.
- **Reproducibility:** pinning floating external skill repositories.
- **Retention:** deleting historical snapshots, archives, plans, or ZIP distribution artifacts.

## Completion criteria

The architecture-sprawl effort is complete when:

- every committed managed surface has one recorded source owner, delivery method, writeback rule, and verifier;
- a reconciliation check covers any ownership facts intentionally repeated across `agent-config` and `dotfiles`;
- committed skill inputs are mechanically checked, while optional local/external drift is reported without blocking hermetic verification;
- shared routing intent is stated once with normalized harness mappings and explicit deviations;
- current truth, decisions, active work, TODOs, and history are distinguishable through structured status and links;
- `scripts/check.sh` runs every hermetic repository check it claims to represent;
- baseline fixtures cover installation, routing, skill delivery, mergers, and sandbox bundle boundaries;
- every behavior difference requires explicit approval, and every retained duplication is named and justified.

## Execution progress

Authorised scope for this run (2026-09-14): Phases 0–2 on branch `sprawl/phase-0-2`. The user accepted the Phase 1 ownership matrix in advance for this run. `dotfiles` changes remain a separate follow-up.

- [ ] Phase 0 — behavioural baseline recorded
- [ ] Phase 1 — ownership matrix and instructions (agent-config side)
- [ ] Phase 2 — truthful verification boundary
