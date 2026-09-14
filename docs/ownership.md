# Ownership contract: agent-config and dotfiles

Status: **accepted contract** (Phase 1 of `plans/reduce-agent-config-architecture-sprawl.md`, agent-config side, 2026-09-14). This is the canonical cross-repository ownership record for agent configuration. It replaces the full table formerly in `AGENTS.md`. The dotfiles copy is replaced on dotfiles branch `docs/ownership-contract-followup` (`a8e23ee`, `89b17d5`, `9460927`; not merged) (see [dotfiles follow-up](#dotfiles-follow-up)).

Recorded against agent-config `8019ca14` (branch `sprawl/phase-0-2`) and dotfiles `bb3d28fa` (read-only). Phase 1 records **current behaviour as the contract**. Where the only fix would change behaviour, the entry is marked *deferred — needs approval* with the proposed change; nothing here changes install, sync, merge or harness behaviour. On 2026-09-14 the user decided every deferred item; the [decisions](#decisions-2026-09-14) section records each one and where it is implemented.

## The rule

`~/dev/agent-config` owns what the agent knows and how it behaves. `~/dev/dotfiles` owns the machine it runs on. Secrets are always dotfiles (1Password + age), never agent-config. Credential-bearing and runtime files belong to neither and stay machine-local.

## Where the rows live

[`ownership.tsv`](ownership.tsv) is the row-level source of truth: one row per managed surface, 53 rows. This document states the rules and resolutions and refers to rows by id. Do not copy the rows into another hand-edited table.

`ownership.tsv` is derived from the Phase 0 baseline [`sprawl-baseline/surfaces.tsv`](sprawl-baseline/surfaces.tsv), which stays unchanged as historical evidence. Ids `S01`–`S52` keep their baseline meaning, and `S53` is new. Compared with the baseline schema:

| Column | Meaning |
| --- | --- |
| `id`, `harness`, `live_destination`, `source_repo`, `source_path`, `delivery`, `writes_through_symlink`, `state_class`, `verifier`, `condition` | As defined in the [baseline schema](sprawl-baseline/README.md#ownership-matrix-schema) |
| `write_authority` | The baseline's `writeback_authority`, renamed: who may write or merge the live path |
| `verification_owner` | The repository whose check is responsible for the row: `agent-config`, `dotfiles`, `both: …` or `none` |
| `resolution` | The Phase 1 contract for the row. It replaces the baseline `status` column, and no row is left `ambiguous` |
| `deferred` | `no` (with the decision and where it is implemented, when one was needed), or `yes: <what is still open or which later phase>` |

Every row has exactly one source owner. The two shared-writer rows (S16, S40) have **one owner per key**, and the key partition is recorded below.

## Writeback classes

Each row's `write_authority` falls into one of these classes:

1. **Repository edit.** A symlinked file that no tool rewrites (for example `global-agents.md` and `claude-powerline.json`). Change it in agent-config and it is live.
2. **Tool writes through a symlink.** The tool rewrites the linked file and the write lands in the checkout: OMP `config.yml`, Pi `settings.json`/`subagents.json`, and the project-scope `.pi/subagents.json` in place. Review with `git diff` before committing. OMP drops comments, so rationale lives in `docs/`.
3. **Live file authoritative, pulled back.** `~/.claude/settings.json` only (S07). `install.sh` copies it if absent, and `./sync.sh` sanitises it and pulls it back. Never edit the tracked snapshot directly.
4. **Merge of owned keys.** The repository enforces only its keys, and the tool or machine keeps everything else: `~/.codex/config.toml` (S16) and pi-web-access `web-search.json` (S40).
5. **Machine-local.** Never tracked, never linked: S08, S26, S27, S41, S50 and the credential halves of S16/S40.

## Surfaces by owner

- **agent-config (symlinks):** S01, S03, S06, S09, S10, S15, S17–S24, S25, S29, S32–S39.
- **agent-config (other):** S05 migration removal, S07 copy-if-absent snapshot, S12 plugin declarations, S13 fixed-path statusline reference, S28/S52 historical, S43 project scope, S44 git config, S45–S47 generated artifacts, S48 sandbox guest copies.
- **external, declared by agent-config:** S02, S04.
- **shared writers:** S16 (dotfiles + agent-config, per key), S40 (agent-config preferences + machine credentials).
- **dotfiles:** S11, S30, S49, S53.
- **neither (machine-local or intentionally unmanaged):** S08, S14, S26, S27, S31, S41, S42, S50, S51.

## Resolutions

The ambiguous surfaces from Phase 0 plus the list in plan step 3:

| Surface | Resolution (current behaviour is the contract) | Deferred? |
| --- | --- | --- |
| S16 `~/.codex/config.toml` | Two mergers with disjoint keys. The per-key partition is [below](#codexconfigtoml-key-partition). agent-config owns `tui.status_line` (D2) | No: decided 2026-09-14; dotfiles side on its follow-up branch; key-overlap check in Phase 2 |
| S40 Pi web-search config | Shared writer by design. `apply-web-search-config.py` pushes only non-credential repo keys (credential-shaped keys are rejected) into `$PI_CODING_AGENT_DIR/web-search.json`, else `$XDG_CONFIG_HOME/pi/web-search.json`, else both `~/.pi/web-search.json` and `~/.pi/agent/web-search.json`. pi-web-access owns credentials and unmanaged keys | No |
| S03/S04/S31/S42 `~/.agents/skills` | agent-config owns the links. opencode and Pi read the root and have no links of their own. Full and selective installs currently gate the root differently; D1 aligns them ([install consumer sets](#install-consumer-sets)) | No: decided 2026-09-14 (D1); implemented in Phase 2 |
| S02 external skill collisions | Repo-owned `skills/<name>` wins. Among external sources, the later `plugins.txt` line replaces the earlier link (last declared wins). An absent `vendor/<slug>` is skipped with a warning. `stablyai/orca` was removed from `plugins.txt` (D4). A name declared by more than one external source fails `check.sh` (D10) | No: decided 2026-09-14 (D10); implemented in Phase 2. Vendor audit stays Phase 3 |
| `~/.omp/agent`, `~/.pi/agent` directories | Neither repository creates or owns these directories: the harness installer does, and `install.sh` only acts when they exist. agent-config owns the per-file links listed in S19–S24 and S32–S39. Everything else inside (S27, S41) is tool or machine state. dotfiles has no source under either | No |
| S17/S18 Codex agents and prompts | agent-config. Symlinked per file when `~/.codex` exists, so machine-local files survive. Role declarations reach Codex through the `[agents]` keys merged in S16. Absent from the dotfiles table; recorded here | No |
| S07 Claude settings snapshot | Live file authoritative (writeback class 3). Paseo hooks stay tracked on purpose: they are no-ops without `PASEO_TERMINAL_ID` (D3). Orca wrapper hooks and the orca `skillOverrides` are removed, and the `sync.sh` filter now also strips `.orca/agent-hooks` (D4). `baseline@baseline` is retired and removed from `enabledPlugins` (D5) | No: decided 2026-09-14; applied on `sprawl/phase-0-2` |
| S13 statusline absolute path | Fixed-path reference, not a delivered link. It requires the canonical checkout at `~/dev/agent-config`, the same requirement as the `install.sh` links and dotfiles `agent-sandbox`'s `AGENT_CONFIG_ROOT`. `sync.sh` rewrites the live `$HOME` back to a literal `$HOME` | No |
| S25 OMP overlays | agent-config owns `omp/overlays/*`. Full install links them into host `~/.config/omp` whether or not `~/.omp/agent` exists. The only tracked consumer is the sandbox guest copy at `/home/agent/.config/omp`, used by dotfiles `ompgo`/`ompcodex` via `agent-sandbox run omp --config …`. No host `~/.local/bin/omp-{go,codex}-overlay` is tracked in dotfiles, so the `install.sh` comments naming them are stale. D6: `install.sh` stops the host links, and the dotfiles functions are canonical | No: decided 2026-09-14 (D6); implemented in Phase 2 |
| S26 `~/.config/omp/.active-overlay` | Machine-local runtime state with no tracked writer in either repository. Per-file overlay links never touch it | No |
| S49 OMP wrappers | dotfiles owns `ompgo`/`ompcodex` and the `agent-*` functions in `dot_zshrc.tmpl`, `agent-sandbox`, `omp-update-daily` and the LaunchAgent. They read overlays but never write agent-config files | No |
| S21 `omp/keybindings.yml` | agent-config; symlinked when `~/.omp/agent` exists. Missing from both old tables; recorded here. Not in the sandbox bundle manifest | No |
| S14 `~/.claude/commands/`, `hooks/` | Owned by neither. agent-config has no `commands/` or `hooks/` source. `install.sh --prune` only removes dangling links there that point into the checkout, which is harmless legacy. The stale dotfiles wording is corrected on its follow-up branch (`89b17d5`). D7: the leftover live directories were backed up and removed on 2026-09-14 | No |
| S43 `.pi/subagents.json` | agent-config project-scope preference. It is not delivered to HOME and not in the sandbox bundle. pi-subagents' `/agents` menu writes it in place when cwd is the checkout (writeback class 2). The global scope stays `pi/subagents.json` (S35). The dirty copy in the main checkout is the user's work and is not absorbed | No |
| S45 committed `node_modules/` | agent-config generated artifact from `package.json`/`package-lock.json` (`pi-token-speed`, which brings `@earendil-works/pi-tui`). Not delivered, but `pi/extensions/operational-footer/index.js` imports `@earendil-works/pi-tui` and `scripts/test-operational-footer.mjs` requires it from this tree. Pi probably resolves it through the extension symlink's real path, but that is unverified. D8: `node_modules/` becomes untracked and gitignored, `package.json` and `package-lock.json` stay tracked, and `check.sh` runs `npm ci` only when `node_modules/` is missing | No: decided 2026-09-14 (D8); implemented in Phase 2 |
| S44 `core.hooksPath` | [Recorded hazard](#full-install-writes-shared-git-config); D9 makes the worktree guard git-based | No: decided 2026-09-14 (D9); implemented in Phase 2 |
| S48 sandbox guest destinations | Inventoried from `sandbox/bootstrap/install.sh` ([sandbox split](#sandbox-split)) | No |
| S51 undeclared vendor checkouts | Runtime cache owned by neither repository. `mattpocock/skills` is now declared. `charleswiltgen-axiom`, `coreyhaines31-marketingskills` and `ehmo-platform-design-skills` remain present but undeclared; the declared-versus-present audit is Phase 3 | **Yes:** Phase 3 |

### `~/.codex/config.toml` key partition

Both mergers preserve every key they do not name. Neither symlinks the file, because Codex rewrites it from its TUI and it may hold machine-local credentials.

| Key | Writer | Rule |
| --- | --- | --- |
| top-level `model`, `model_reasoning_effort`, `plan_mode_reasoning_effort` | dotfiles `dot_codex/modify_private_config.toml` (on every `chezmoi apply`) | Supplied only if absent, placed before the first table header; an existing value is passed through |
| `tui.status_line` | agent-config `codex/config.toml` (D2) | Enforced. The dotfiles modify script no longer writes it (`a8e23ee`) |
| `tui.status_line_use_colors` | agent-config `scripts/apply-codex-config.py` (full `install.sh` when `~/.codex` exists) | Enforced |
| `skills.max_context_tokens` | agent-config | Enforced |
| `agents.enabled`, `agents.default_subagent_model`, `agents.default_subagent_reasoning_effort`, `agents.max_concurrent_threads_per_session` | agent-config | Enforced |
| `agents.docs_researcher.description`, `agents.docs_researcher.config_file` | agent-config | Enforced |
| everything else (`[plugins.*]`, MCP, projects, credentials, desktop state) | Codex / machine | Never written by either repository |

Ordering: nothing sequences `chezmoi apply` and `install.sh`. With D2 the key sets are disjoint, so order does not matter; both are idempotent for their own keys. `apply-codex-config.py` manages tables only; it appends a missing table at the end and never writes top-level keys, so it cannot misplace the dotfiles top-level defaults.

*Decided 2026-09-14 (D2):* agent-config owns `tui.status_line`, `tui.status_line_use_colors`, `[skills]` and `[agents*]`; dotfiles fills only the three top-level defaults if absent. The dotfiles side is on dotfiles branch `docs/ownership-contract-followup` (`a8e23ee`, `89b17d5`, `9460927`; not merged). Phase 2 adds a check that the two key sets do not overlap. Remaining gap: the live Codex status bar only changes to the agent-config list on the next agent-config install.

## Install consumer sets

The contract observed at the recorded revision, from the Phase 0 fixtures in [`sprawl-baseline/fixtures/`](sprawl-baseline/fixtures/):

| Mode | `~/.claude/skills` | `~/.agents/skills` populated when | External skills | Everything else |
| --- | --- | --- | --- | --- |
| Full (`./install.sh`) | always | `~/.codex` exists (only) | both roots, when `vendor/<slug>` exists | per-harness links, merges, settings copy, overlays, plugins, `core.hooksPath` |
| Selective (`--skills-only=…`) | named repo skills | `~/.codex` **or** `~/.pi/agent` exists | never | nothing |

**Known compatibility issue.** On a Pi-only or opencode-only machine, a full install delivers no shared skills and a selective install does. See the `full-pi`/`full-pi-vendor` fixtures (`~/.agents/skills`: 0) against `selective-pi` (2). `install.sh` states the gap is deliberate ("Preserve the normal install's Codex-only shared-root detection").

*Decided 2026-09-14 (D1):* `install.sh` populates `~/.agents/skills` when any of Codex, Pi, opencode or OMP is present, matching selective install. Implemented in Phase 2, with before/after `full-pi`, `full-opencode` and `full-pi-vendor` fixtures and a check for duplicate discovery (Pi already reads `~/.agents/skills` and has no `~/.pi/agent/skills` links).

### Full install writes shared git config

A full install runs `git -C "$REPO" config core.hooksPath .githooks` whenever the checkout is a Git work tree. From a linked worktree this writes the common `.git/config` shared with the main checkout. The ephemeral-worktree guard (`*/.git/worktrees/*`, `*/worktrees/*`) does not match sibling worktrees such as `~/dev/agent-config-sprawl`. The value is relative and identical for every checkout, but it is still a write outside HOME made from a worktree. It is the only such write apart from `vendor/` clones. Do not run `install.sh` from a worktree.

*Decided 2026-09-14 (D9):* the `install.sh` worktree guard becomes git-based and refuses when `git rev-parse --git-dir` differs from `--git-common-dir`, so a linked worktree never reaches the write. Implemented in Phase 2.

## chezmoi collision inventory

Every live path agent-config writes, cross-checked against dotfiles `bb3d28fa` source targets (decoded chezmoi names) and `.chezmoiignore`:

| agent-config destination | Rows | Delivery | dotfiles source targeting it | `.chezmoiignore` gate |
| --- | --- | --- | --- | --- |
| `~/.claude/CLAUDE.md` | S10 | symlink | none | **yes** (`.claude/CLAUDE.md`) |
| `~/.claude/settings.json` | S07 | copy-if-absent | none | **yes** (`.claude/settings.json`) |
| `~/.config/omp/{codex-only-overlay.yml,go-overlay.yml,search-keys.tpl}` | S25 | symlink per file | none | **yes** (`.config/omp`) |
| `~/.claude/skills/<name>/` | S01, S02 | symlink | none | no |
| `~/.claude/agents/*.md` | S06 | symlink per file | none | no |
| `~/.claude/claude-powerline.json` | S09 | symlink | none | no |
| `~/.agents/skills/<name>/` | S03, S04 | symlink | none | no |
| `~/.codex/AGENTS.md`, `~/.codex/agents/*.toml`, `~/.codex/prompts/*.md` | S15, S17, S18 | symlink | none | no |
| `~/.omp/agent/{AGENTS.md,config.yml,keybindings.yml,lsp.yml}`, `themes/*.json`, `agents/*.md` | S19–S24 | symlink | none | no |
| `~/.config/opencode/AGENTS.md` | S29 | symlink | none (sibling `opencode.jsonc` is dotfiles `modify_`, S30) | no |
| `~/.pi/agent/{AGENTS.md,settings.json,pi-fff.json,subagents.json}`, `prompts/*.md`, `themes/*.json`, `extensions/<name>/{index.js,index.ts,theme.json}`, `agents/*.md` | S32–S39 | symlink | none | no |
| `~/.codex/config.toml` | S16 | merge | `dot_codex/modify_private_config.toml` | n/a: intentional shared writer; neither side symlinks |
| `~/.pi/web-search.json`, `~/.pi/agent/web-search.json` | S40 | merge | none | no |

dotfiles targets under agent-config roots that do not collide: `~/.claude/plugins/claude-hud/config.json` (S11) and `~/.config/opencode/opencode.jsonc` (S30).

**Result at the recorded revisions: no active collision.** Three destinations are gated. The rest are safe only because dotfiles has no source for them, so a `chezmoi add`/`re-add` of one of them would create a claim silently.

*Still deferred (dotfiles; not part of its follow-up branch; no behaviour change while no source exists):* add preventive ignore gates for `.claude/skills`, `.claude/agents`, `.claude/claude-powerline.json`, `.agents`, `.codex/AGENTS.md`, `.codex/agents`, `.codex/prompts`, `.omp/agent`, `.config/opencode/AGENTS.md`, `.pi/agent` and `.pi/web-search.json`.

### Non-destructive detection rule

The implementation belongs to Phase 2. The specification:

1. **Inputs.** Rows in `docs/ownership.tsv` with `source_repo` beginning `agent-config` or `external` and a concrete home `live_destination`. A dotfiles revision's `git ls-files`, from a fixture or a read-only checkout. dotfiles `.chezmoiignore`.
2. **Decode chezmoi source names to targets.** Per path component, repeatedly strip the attribute prefixes `private_`, `readonly_`, `empty_`, `executable_`, `create_`, `modify_`, `remove_`, `symlink_`, `encrypted_`, `exact_`, `external_`, `once_`, `onchange_`, `run_`, `before_` and `after_`. Map `dot_` to `.` and strip the `.tmpl` and `.age` suffixes. Skip source entries whose first component starts with `.`, which chezmoi ignores, including `.chezmoiscripts`.
3. **Collision.** A decoded target equals an agent-config destination, or is an ancestor or descendant of a directory-level link (`~/.claude/skills/<name>/`, `~/.agents/skills/<name>/`). A `symlink_` source whose target points into `~/dev/agent-config` is also a claim. Only rows listed as intentional shared writers are exempt (S16 `~/.codex/config.toml` via `modify_`).
4. **Ignore gates.** Evaluate `.chezmoiignore` conservatively: treat lines inside template conditionals as possibly inactive. A gated destination with a matching source is still reported, because the gate hides it only on some machines.
5. **Severity.** A collision fails the hermetic check (run against a pinned dotfiles fixture). An ungated but unclaimed destination is informational. A three-gate regression (removal of `.claude/CLAUDE.md`, `.claude/settings.json` or `.config/omp`) fails.
6. **Never mutate.** No `chezmoi apply`, `add`, `re-add`, `forget` or `init`, no edits to either tree, and no automatic ignore entries. An optional local-audit tier may run `chezmoi managed` read-only, path-limited to the destinations above, and report only.

## Sandbox split

- **agent-config owns** the portable configuration bundle and its planning. That covers `sandbox/bootstrap/{manifest.txt,install.sh}`, `scripts/build-agent-sandbox-bundle.sh` (a `git archive HEAD` snapshot with `SHA256SUMS` and marker), its test, and the committed payload named by the manifest.
- **dotfiles owns** launchers, aliases, machine application and live sandbox operations: `~/.local/bin/agent-sandbox` (`prepare`, `run`, `shell`, `reset`, ports, checkpoints, doctor), the `pis`/`omps`/`ompgo`/`ompcodex`/`agent-*` shell functions, pinned binary versions inside the guest, and `tests/test-agent-sandbox.py`.
- **Sequencing:** `agent-sandbox prepare` in dotfiles requires the canonical agent-config checkout at `~/dev/agent-config` with clean bundle paths, invokes the agent-config builder, then copies the bundle into the guest and runs its installer. A bundle change lands and is committed in agent-config first. A launcher change lands in dotfiles and consumes whatever bundle `prepare` builds.
- **Guest destinations (S48)**, installed as marker-guarded copies (`.agent-config-sandbox-managed`), never symlinks:
  - `~/.pi/agent/{AGENTS.md, settings.json, subagents.json}`, `prompts/`, `themes/`, `extensions/`, `agents/`
  - `~/.omp/agent/{AGENTS.md, config.yml, lsp.yml}`, `themes/`
  - `~/.agents/skills/<repo-skill>/`
  - `~/.config/omp/<overlay>`
  - **Not carried:** OMP `keybindings.yml`, `pi-fff.json`, pi web-search config, Codex and Claude config, external skills, `node_modules/`.

## Decisions (2026-09-14)

Every behaviour change deferred by Phase 1 was decided by the user on 2026-09-14:

| # | Rows | Decision | Where implemented |
| --- | --- | --- | --- |
| D1 | S03, S04, S31, S42 | `install.sh` populates `~/.agents/skills` when any of Codex, Pi, opencode or OMP is present, matching selective install | Phase 2 |
| D2 | S16 | dotfiles fills only `model`, `model_reasoning_effort` and `plan_mode_reasoning_effort` if absent; agent-config owns `[tui].status_line`, `status_line_use_colors`, `[skills]` and `[agents*]` | dotfiles `a8e23ee`, `89b17d5`, `9460927` (branch, not merged); key-overlap check in Phase 2 |
| D3 | S07 | Paseo hooks stay tracked in `settings.json`; they are env-gated no-ops elsewhere | No change needed |
| D4 | S02, S07 | Orca retired: its wrapper hooks are removed from `settings.json` and the `sync.sh` filter strips `.orca/agent-hooks`; `external stablyai/orca` is removed from `plugins.txt` along with the orca `skillOverrides` | `sprawl/phase-0-2` |
| D5 | S07 | `baseline@baseline` is retired and removed from `enabledPlugins` | Live settings, then `sync.sh` on `sprawl/phase-0-2` |
| D6 | S25, S49 | `install.sh` stops creating host `~/.config/omp` overlay links; dotfiles `ompgo`/`ompcodex` are canonical | Phase 2 |
| D7 | S14 | `~/.claude/commands` and `~/.claude/hooks` stay unmanaged; the leftover live directories are backed up and deleted | Live, 2026-09-14 |
| D8 | S45 | `node_modules/` becomes untracked and gitignored; `check.sh` runs `npm ci` only if it is missing | Phase 2 |
| D9 | S44 | The `install.sh` worktree guard becomes git-based (`--git-dir` differs from `--git-common-dir`) | Phase 2 |
| D10 | S02 | A skill name declared by more than one external source fails `check.sh` | Phase 2 |
| D11 | — | The dotfiles follow-up is done in this run | dotfiles branch `docs/ownership-contract-followup` |

Unchanged by these decisions: `.pi/subagents.json` stays tracked (S43), and the fixed statusline path stays (S13).

Still open: the preventive dotfiles `.chezmoiignore` gates ([collision inventory](#chezmoi-collision-inventory)) and the Phase 3 vendor audit (S51).

## Instruction conflict: "change both copies together"

Before this change, agent-config `AGENTS.md` said the ownership table "is duplicated in both repos; change both copies together", and dotfiles `AGENTS.md` says the same. Phase 1 changed the agent-config copy first. The dotfiles copy is now replaced on dotfiles branch `docs/ownership-contract-followup` (`a8e23ee`, `89b17d5`, `9460927`; not merged): its `AGENTS.md` keeps only this repository's side and points at this contract, and the stale `commands/` and `hooks/` claims are gone. **Until that branch merges, dotfiles `main` still carries the older full table.** Where they differ, this contract wins. Phase 1's exit criterion ("`dotfiles` either references the accepted canonical contract or has a mechanically reconciled view") is met on the branch and not yet on dotfiles `main`.

## dotfiles follow-up

Applied on dotfiles branch `docs/ownership-contract-followup` (`a8e23ee`, `89b17d5`, `9460927`; not merged):

- `a8e23ee` — `dot_codex/modify_private_config.toml` stops enforcing `tui.status_line`; it only supplies the three top-level model defaults when absent and passes every other line through (D2).
- `89b17d5` — drops the stale `commands/`/`hooks/` ownership claims from `.chezmoiignore`, `README.md` and `install.sh`.
- `9460927` — replaces the full ownership table in dotfiles `AGENTS.md` with that repository's side of the contract and a pointer to this document.

Remaining gaps:

- The branch is not merged into dotfiles `main`.
- The live Codex status bar only picks up the agent-config `tui.status_line` list on the next agent-config install; until then it keeps whichever list was applied last.
- The optional preventive ignore gates listed under [chezmoi collision inventory](#chezmoi-collision-inventory) were not added.
