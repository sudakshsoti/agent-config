# Issue Work Order

Updated: 2026-09-14

This is the maintainer's working order for the open GitHub issues in this repository. It is intentionally organized as execution waves rather than issue-number order.

## Recommended order

### 0. Verify the live crash first

- **[#43](https://github.com/sudakshsoti/agent-config/issues/43)** — `pi-claude-bridge`: `prompt-capture: no capture` kills the Pi process.
- Category: `bug`; current state: `needs-triage`.
- Reproduce this in the bridge repository. If confirmed, fix it before the backlog below. If it cannot be reproduced, request logs, versions, and exact invocation details.
- This repository does not contain `pi-claude-bridge`, so verification cannot happen locally.

### 1. Foundation — work in parallel when possible

- **[#34](https://github.com/sudakshsoti/agent-config/issues/34)** — make `scripts/check.sh` discover every `scripts/test-*` and report pass/fail/skip truthfully.
- **[#36](https://github.com/sudakshsoti/agent-config/issues/36)** — refuse installs from linked Git worktrees before any write.

If working serially, start with #34 because it unlocks more of the critical path. #36 can proceed independently.

### 2. Core implementation

After #34:

- **[#39](https://github.com/sudakshsoti/agent-config/issues/39)** — machine-check `plugins.txt`, the skill catalogue, and the `sync.sh` filter.
- **[#40](https://github.com/sudakshsoti/agent-config/issues/40)** — machine-check ownership records, Codex key partitioning, and collision rules.
- **[#35](https://github.com/sudakshsoti/agent-config/issues/35)** — make `node_modules/` an ignored build product and bootstrap it from `check.sh`.

Issues #39 and #40 are the higher-priority path because they unlock #41. #35 may be done alongside them, but changes to `check.sh` should be coordinated.

After #36:

- **[#37](https://github.com/sudakshsoti/agent-config/issues/37)** — use one four-consumer predicate for the shared skills root.
- **[#38](https://github.com/sudakshsoti/agent-config/issues/38)** — retire host OMP overlay links and add narrow `--prune` reclamation.

Issue #38 has a hard dependency on #36 and a soft sequencing recommendation to land after #37, because both modify `install.sh`.

### 3. Audit and closeout

- **[#41](https://github.com/sudakshsoti/agent-config/issues/41)** — add the opt-in, read-only, offline local audit after #39 and #40.
- **[#42](https://github.com/sudakshsoti/agent-config/issues/42)** — close Phase 2 after #34–#41. This includes a user-run live-apply procedure, so it should become `ready-for-human` only when its dependencies are complete.

### 4. Later design and planning work

- **[#44](https://github.com/sudakshsoti/agent-config/issues/44)** — consolidate `self-review` and `peer-review` after Phase 2; it needs scope and caller decisions first.
- **[#45](https://github.com/sudakshsoti/agent-config/issues/45)** — split the remaining architecture-sprawl work into separate Phase 3–6 issues before implementation. Do not treat this umbrella issue as one coding task.

**[#33](https://github.com/sudakshsoti/agent-config/issues/33)** is the parent specification for #34–#42. Track it as the parent; do not pick it up as an independent implementation task.

## Triage labels

| Issues | Category | Current state |
| --- | --- | --- |
| #33 | `enhancement` | `ready-for-agent` (parent/spec only) |
| #34–#41 | `enhancement` | `ready-for-agent` |
| #42 | `enhancement` | `needs-triage` until dependencies complete; then `ready-for-human` |
| #43 | `bug` | `needs-triage` |
| #44–#45 | `enhancement` | `needs-triage` |

`needs-info` and `wontfix` are available for future triage but are not appropriate for the current open issues.

## Tracker metadata

The hard dependency relationships are recorded in GitHub's native `blocked by` metadata. The soft #37 → #38 sequencing remains documented here rather than being encoded as a hard blocker. #34–#42 are children of #33.

The existing issues already cover the fixes identified during review:

- #34 covers the hand-maintained `scripts/check.sh` list.
- #36 covers the path-only linked-worktree guard.
- #38 covers the old host-overlay behavior.

No duplicate issue is needed.

## How to proceed

1. Verify and resolve #43, or move it to `needs-info` with concrete reporter questions.
2. Start #34 and #36 as the first implementation wave.
3. Keep the GitHub `blocked by` relationships up to date as issues close or scope changes.
4. Run the narrow relevant tests after each issue, then run `bash scripts/check.sh` at the Phase 2 closeout.
5. Do not perform the live home/dotfiles apply from an AFK agent; reserve #42 for an explicit human-run session.
6. Re-triage #44 and split #45 after Phase 2 is complete.
