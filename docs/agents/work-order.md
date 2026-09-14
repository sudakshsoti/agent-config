# Issue Work Order

Updated: 2026-09-14

This is the maintainer's working order for the open GitHub issues in this repository. It is organized by what is still blocking, not by issue number.

## Remaining order

### 1. Maintainer decisions

- **[#38](https://github.com/sudakshsoti/agent-config/issues/38)** — retire host OMP overlay links and add narrow `--prune` reclamation. On hold: the cull plan behind `4a7edc49` keeps the host OMP overlays. Decide which direction wins before any `install.sh` change.
- **[#40](https://github.com/sudakshsoti/agent-config/issues/40)** — the chezmoi collision check merged in #50. The `ownership.tsv` integrity and Codex key-partition half is not applicable after the cull: `docs/ownership.{md,tsv}` never reached `main`, and the Codex config was removed. Decide whether to close that half as superseded.

### 2. Human-run closeout

- **[#42](https://github.com/sudakshsoti/agent-config/issues/42)** — close Phase 2 with the live apply in [`docs/phase-2-live-apply.md`](../phase-2-live-apply.md). Mark it `ready-for-human` once #38 and #40 are decided. Read precondition P4 first: `./install.sh --prune` also removes retired-harness links such as `~/.claude/CLAUDE.md` and `~/.claude/skills/*`.

### 3. Later design and planning work

- **[#44](https://github.com/sudakshsoti/agent-config/issues/44)** — consolidate `self-review` and `peer-review` after Phase 2; it needs scope and caller decisions first.
- **[#45](https://github.com/sudakshsoti/agent-config/issues/45)** — split the remaining architecture-sprawl work into separate Phase 3–6 issues before implementation. Do not treat this umbrella issue as one coding task. Follow-up notes from Phase 2 are recorded on the issue.

**[#33](https://github.com/sudakshsoti/agent-config/issues/33)** is the parent specification for #34–#42. Track it as the parent; do not pick it up as an independent implementation task.

## Status

| Issue | State | Notes |
| --- | --- | --- |
| #33 | open | parent spec only |
| #34, #36 | closed, completed | PR #49 |
| #35, #37, #39, #41 | closed, completed | PR #50; superseded parts (the `sync.sh` filter and the ownership-contract doc updates) are noted on each issue |
| #40 | open, partly implemented | collision check in PR #50; contract half awaits a decision |
| #38 | open, on hold | conflicts with the cull plan's retained host overlays |
| #42 | open | runbook prepared; live apply not run |
| #43, #46–#48 | closed, not planned | `pi-claude-bridge` lives outside this repository |
| #44, #45 | open, `needs-triage` | re-triage after Phase 2 |

## Tracker metadata

The hard dependency relationships are recorded in GitHub's native `blocked by` metadata. #34–#42 are children of #33.

## How to proceed

1. Decide #38 and #40's contract half.
2. Keep the GitHub `blocked by` relationships up to date as issues close or scope changes.
3. Do not perform the live home/dotfiles apply from an AFK agent; reserve #42 for an explicit human-run session.
4. Re-triage #44 and split #45 after Phase 2 is complete.
