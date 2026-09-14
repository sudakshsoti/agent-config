# Handoff: agent-config sprawl reduction, Phase 2 via tickets (2026-09-14)

## Where the work lives

- **agent-config worktree:** `~/dev/agent-config-sprawl`, branch `sprawl/phase-0-2`, pushed to origin. All sprawl work lives here.
  - Don't run `install.sh` from this worktree. Live installs run only from `~/dev/agent-config` (main).
- **agent-config main checkout:** `~/dev/agent-config`. Five unrelated commits are pushed (mattpocock plugins, Pi fleetView, the harness-config-maintenance skill, the skill-lifecycle skill, the README resync).
  - `plans/reduce-agent-config-architecture-sprawl.md` is still untracked there. It's an older copy of the plan; the authoritative copy, with the execution tracker, is on the sprawl branch.
- **dotfiles:** `~/dev/dotfiles`, branch `docs/ownership-contract-followup`, pushed and not merged. It has 3 commits:
  - the modify script no longer writes `tui.status_line`;
  - stale commands/hooks wording is gone;
  - the `AGENTS.md` ownership section points at agent-config.
- **Plan:** `plans/reduce-agent-config-architecture-sprawl.md`, on the branch. The authorised scope is Phases 0–2. Phases 0 and 1 are ticked; Phase 2 is open.
- **Spec:** GitHub issue #33 (`sudakshsoti/agent-config`), plus a "Corrections found while drafting tickets" comment that overrides the body where they differ.
- **Tickets:** #34–#42. They're sub-issues of #33, labelled `ready-for-agent`, with native blocked-by links.

## What changed on `sprawl/phase-0-2`

| Commit | Change |
|---|---|
| `45b9ba64` | Plan and execution tracker |
| `108146db` | `docs/sprawl-baseline/` (Phase 0) |
| `207ac8d7`, `c4a71d0a` | `docs/ownership.md`, `docs/ownership.tsv`, `AGENTS.md` pointer, and the recorded decisions (Phase 1) |
| `d1ecaec6` | `sync.sh` strip also matches `.orca/agent-hooks`; orca removed from `plugins.txt` |
| `f7f4e75c` | `settings.json` synced from live (orca hooks, overrides and `baseline@baseline` removed) |
| `55c99207` | Orphaned `computer-use` skillOverride removed |
| `8ba76991` | mattpocock setup: `docs/agents/*`, `## Agent skills` in `AGENTS.md`, and `to-spec`, `to-tickets`, `triage` added |
| `36ec58a6` | **Ticket #34 done.** `scripts/check.sh` finds every `scripts/test-*` on its own, exit 77 counts as SKIP, the run fails if `git status` changes, new `scripts/test-check.py`, and the footer test SKIPs when deps are missing |
| `9d0f7b8b` | `plugins.txt` mattpocock line adds `implement` |
| this handoff | This file |

## Decisions (all accepted by the user) and why

| # | Decision | Why |
|---|---|---|
| D1 | `install.sh` fills `~/.agents/skills` when Codex, Pi, opencode or OMP is present. Selective install uses the same rule. | Pi reads `~/.agents/skills`, but it was only filled when Codex existed |
| D2 | agent-config owns the Codex `[tui]` status bar; dotfiles fills only `model`, `model_reasoning_effort`, `plan_mode_reasoning_effort`. A key-overlap check is added. | Both repos were writing the same keys |
| D3 | Paseo hooks stay tracked | Used on this machine and the homelab VPS |
| D4 | Orca removed completely: hooks, strip, `plugins.txt`, overrides | No longer used |
| D5 | `baseline@baseline` removed | Retired |
| D6 | `install.sh` stops making host `~/.config/omp` overlay links; `--prune` removes symlinks there whose target resolves into `omp/overlays/`, and nothing else | dotfiles `ompgo`/`ompcodex` are canonical |
| D7 | `~/.claude/commands` and `~/.claude/hooks` removed live (backed up in the session scratchpad) | Unmanaged leftovers |
| D8 | `node_modules/` untracked and gitignored; `check.sh` runs `npm ci` only when it's missing, otherwise visible SKIP | Committed by accident; only the footer test needs it |
| D9 | Worktree guard is Git-based (`git-dir` != `git-common-dir`) unless `--force` | Path matching missed worktrees |
| D10 | Duplicate names on `external` lines that list skills fail `check.sh`. Bare lines (e.g. `emilkowalski/skills`) produce an audit warning only. | Collisions silently shadow skills; allowlists aren't forced |
| D11 | dotfiles follow-up done in this run | Keep the two contracts in step |
| — | Chezmoi collisions are tested on a fixture and detected live by the audit; `docs/ownership.md` rule 5 gets reworded | The hermetic check can't see the live machine |
| — | D1 unit tests are enough; no new before/after fixtures. The D1 note gets reworded (ticket #37). | Avoid fixture churn |
| — | Tickets name surfaces plus key files. Generated artifacts are committed with their source. Docs change in the same ticket as their behaviour. | User instruction |

## Current state

- Nothing is uncommitted on the sprawl branch or in dotfiles. The only uncommitted file is the untracked plan copy on main (see above).
- **Live machine:** I linked `implement`, `tdd` and `code-review` by hand into `~/.claude/skills` and `~/.agents/skills`, pointing at `~/dev/agent-config/vendor/mattpocock-skills/skills/engineering/`. They match what `install.sh` will create after the merge.
- **#34 caveats:**
  - It was built without `/tdd` or `/code-review`.
  - A `test-*` file with an unknown extension is reported as FAIL.
  - CI (`ubuntu-latest`) has no setup-node step, and the footer test needs Node >= 22.19.
  - Nobody confirmed whether shellcheck is installed.
- **Open tickets, in blocking order:**
  1. #35 `node_modules` untrack (blocked by #34, now done)
  2. #36 worktree guard (no blockers)
  3. #37 four-harness skills-root rule (blocked by #36)
  4. #38 overlay link removal and prune (blocked by #36)
  5. #39 drift checks (blocked by #34)
  6. #40 ownership checks (blocked by #34)
  7. #41 local audit (blocked by #39, #40)
  8. #42 runbook and plan ticks (blocked by all)
- **Backups** are in `/private/tmp/claude-501/.../scratchpad/` (`claude-settings.backup-2026-09-14*.json`, `claude-dirs-backup-2026-09-14/`). `/private/tmp` is cleared on reboot, so copy them somewhere durable if you want them.

## Later live apply (user-run, after merges; not for agents)

1. Merge dotfiles `docs/ownership-contract-followup`, then run `chezmoi apply`. Until this happens, the key-overlap check fails.
2. Merge `sprawl/phase-0-2` into agent-config main.
3. Run `npm ci` in `~/dev/agent-config` immediately; the merge deletes the tracked `node_modules/`.
4. From `~/dev/agent-config`, run `./install.sh --prune`. It links to-spec/to-tickets/triage/implement, drops the orca links, sets the Codex bar and prunes the overlay links.

## Rules that still apply

- Never `git add -A`; commit explicit paths.
- No co-author lines.
- Never edit repo `settings.json` directly: edit live, then run `./sync.sh`.
- Never run chezmoi apply/add from agents.
- Don't bypass the Safety Net hook.
- Never run `install.sh` or `sync.sh` against the real HOME in tests.

## Next action

Optionally run `/code-review` on `36ec58a6` against issue #34 first. Then, in `~/dev/agent-config-sprawl`, run `/implement` for issue #35 (then #36, …), using `/clear` between tickets.
