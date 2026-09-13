# Ownership contract: agent-config and dotfiles

Status: **accepted contract** (Phase 1 of `plans/reduce-agent-config-architecture-sprawl.md`, agent-config side, 2026-09-14). This is the canonical cross-repository ownership record for agent configuration. It replaces the full table formerly in `AGENTS.md`. The dotfiles copy is replaced in a separate follow-up (see [dotfiles follow-up](#dotfiles-follow-up)).

Recorded against agent-config `8019ca14` (branch `sprawl/phase-0-2`) and dotfiles `bb3d28fa` (read-only). Phase 1 records **current behaviour as the contract**. Where the only fix would change behaviour, the entry is marked *deferred — needs approval* with the proposed change; nothing here changes install, sync, merge or harness behaviour.

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
| `deferred` | `no`, or `yes: <what needs approval or which later phase>` |

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
| S16 `~/.codex/config.toml` | Two independent mergers, no enforced order. The per-key partition is [below](#codexconfigtoml-key-partition). `tui.status_line` is enforced by both with different values, and the last applier wins | **Yes:** choose one owner for `tui.status_line` |
| S40 Pi web-search config | Shared writer by design. `apply-web-search-config.py` pushes only non-credential repo keys (credential-shaped keys are rejected) into `$PI_CODING_AGENT_DIR/web-search.json`, else `$XDG_CONFIG_HOME/pi/web-search.json`, else both `~/.pi/web-search.json` and `~/.pi/agent/web-search.json`. pi-web-access owns credentials and unmanaged keys | No |
| S03/S04/S31/S42 `~/.agents/skills` | agent-config owns the links. opencode and Pi read the root and have no links of their own. Full and selective installs gate the root differently ([install consumer sets](#install-consumer-sets)) | **Yes:** gate alignment |
| S02 external skill collisions | Repo-owned `skills/<name>` wins. Among external sources, the later `plugins.txt` line replaces the earlier link (last declared wins). An absent `vendor/<slug>` is skipped with a warning (`stablyai/orca` today) | **Yes:** Phase 3 |
| `~/.omp/agent`, `~/.pi/agent` directories | Neither repository creates or owns these directories: the harness installer does, and `install.sh` only acts when they exist. agent-config owns the per-file links listed in S19–S24 and S32–S39. Everything else inside (S27, S41) is tool or machine state. dotfiles has no source under either | No |
| S17/S18 Codex agents and prompts | agent-config. Symlinked per file when `~/.codex` exists, so machine-local files survive. Role declarations reach Codex through the `[agents]` keys merged in S16. Absent from the dotfiles table; recorded here | No |
| S07 Claude settings snapshot | Live file authoritative (writeback class 3). The paseo and orca hook commands are in the snapshot because `sync.sh` does not filter them, so a fresh-machine bootstrap installs them. `baseline@baseline` is `false` in `enabledPlugins`, consistent with the commented-out `marketplace`/`plugin` lines in `plugins.txt` that say to flip it back when re-enabling. It is a disabled plugin, not drift | **Yes (hooks only):** add paseo/orca patterns to the `sync.sh` filter if they are machine state |
| S13 statusline absolute path | Fixed-path reference, not a delivered link. It requires the canonical checkout at `~/dev/agent-config`, the same requirement as the `install.sh` links and dotfiles `agent-sandbox`'s `AGENT_CONFIG_ROOT`. `sync.sh` rewrites the live `$HOME` back to a literal `$HOME` | No |
| S25 OMP overlays | agent-config owns `omp/overlays/*`. Full install links them into host `~/.config/omp` whether or not `~/.omp/agent` exists. The only tracked consumer is the sandbox guest copy at `/home/agent/.config/omp`, used by dotfiles `ompgo`/`ompcodex` via `agent-sandbox run omp --config …`. No host `~/.local/bin/omp-{go,codex}-overlay` is tracked in dotfiles, so the `install.sh` comments naming them are stale | **Yes:** gate or drop the host links; correct the comments |
| S26 `~/.config/omp/.active-overlay` | Machine-local runtime state with no tracked writer in either repository. Per-file overlay links never touch it | No |
| S49 OMP wrappers | dotfiles owns `ompgo`/`ompcodex` and the `agent-*` functions in `dot_zshrc.tmpl`, `agent-sandbox`, `omp-update-daily` and the LaunchAgent. They read overlays but never write agent-config files | No |
| S21 `omp/keybindings.yml` | agent-config; symlinked when `~/.omp/agent` exists. Missing from both old tables; recorded here. Not in the sandbox bundle manifest | No |
| S14 `~/.claude/commands/`, `hooks/` | Owned by neither. agent-config has no `commands/` or `hooks/` source. `install.sh --prune` only removes dangling links there that point into the checkout, which is harmless legacy. The dotfiles table row, `.chezmoiignore` comment and `install.sh` step-9 comment that attribute them to agent-config are stale | No (dotfiles wording follow-up) |
| S43 `.pi/subagents.json` | agent-config project-scope preference. It is not delivered to HOME and not in the sandbox bundle. pi-subagents' `/agents` menu writes it in place when cwd is the checkout (writeback class 2). The global scope stays `pi/subagents.json` (S35). The dirty copy in the main checkout is the user's work and is not absorbed | No |
| S45 committed `node_modules/` | agent-config generated artifact from `package.json`/`package-lock.json` (`pi-token-speed`, which brings `@earendil-works/pi-tui`). Not delivered, but `pi/extensions/operational-footer/index.js` imports `@earendil-works/pi-tui` and `scripts/test-operational-footer.mjs` requires it from this tree. Pi probably resolves it through the extension symlink's real path, but that is unverified. The implied regeneration rule is `npm install` against the committed lockfile, with the lockfile change in the same commit | **Yes:** keeping it committed is a retention decision |
| S44 `core.hooksPath` | [Recorded hazard](#full-install-writes-shared-git-config) | **Yes** |
| S48 sandbox guest destinations | Inventoried from `sandbox/bootstrap/install.sh` ([sandbox split](#sandbox-split)) | No |
| S51 undeclared vendor checkouts | Runtime cache owned by neither repository. Not inspected; the declared-versus-present audit is Phase 2/3 | **Yes:** Phase 3 |

### `~/.codex/config.toml` key partition

Both mergers preserve every key they do not name. Neither symlinks the file, because Codex rewrites it from its TUI and it may hold machine-local credentials.

| Key | Writer | Rule |
| --- | --- | --- |
| top-level `model`, `model_reasoning_effort`, `plan_mode_reasoning_effort` | dotfiles `dot_codex/modify_private_config.toml` (on every `chezmoi apply`) | Supplied only if absent, placed before the first table header; an existing value is passed through |
| `tui.status_line` | **both**: dotfiles (7-entry list) and agent-config `codex/config.toml` (10-entry list) | Each overwrites on its own run; last applier wins |
| `tui.status_line_use_colors` | agent-config `scripts/apply-codex-config.py` (full `install.sh` when `~/.codex` exists) | Enforced |
| `skills.max_context_tokens` | agent-config | Enforced |
| `agents.enabled`, `agents.default_subagent_model`, `agents.default_subagent_reasoning_effort`, `agents.max_concurrent_threads_per_session` | agent-config | Enforced |
| `agents.docs_researcher.description`, `agents.docs_researcher.config_file` | agent-config | Enforced |
| everything else (`[plugins.*]`, MCP, projects, credentials, desktop state) | Codex / machine | Never written by either repository |

Ordering: nothing sequences `chezmoi apply` and `install.sh`. Both are idempotent for their own keys. `apply-codex-config.py` manages tables only; it appends a missing table at the end and never writes top-level keys, so it cannot misplace the dotfiles top-level defaults.

*Deferred — needs approval:* give `tui.status_line` one owner. The proposal is agent-config, which already enforces `tui.status_line_use_colors` in the same table; remove `write_status_line` from the dotfiles modify script. The alternative is dotfiles, with the key removed from `codex/config.toml`. Either option changes the effective footer on one side.

## Install consumer sets

The currently observed contract, from the Phase 0 fixtures in [`sprawl-baseline/fixtures/`](sprawl-baseline/fixtures/):

| Mode | `~/.claude/skills` | `~/.agents/skills` populated when | External skills | Everything else |
| --- | --- | --- | --- | --- |
| Full (`./install.sh`) | always | `~/.codex` exists (only) | both roots, when `vendor/<slug>` exists | per-harness links, merges, settings copy, overlays, plugins, `core.hooksPath` |
| Selective (`--skills-only=…`) | named repo skills | `~/.codex` **or** `~/.pi/agent` exists | never | nothing |

**Known compatibility issue.** On a Pi-only or opencode-only machine, a full install delivers no shared skills and a selective install does. See the `full-pi`/`full-pi-vendor` fixtures (`~/.agents/skills`: 0) against `selective-pi` (2). `install.sh` states the gap is deliberate ("Preserve the normal install's Codex-only shared-root detection").

*Deferred — needs approval:* make the full-install gate `~/.codex` **or** `~/.pi/agent` (optionally `~/.config/opencode`). Before and after, capture `full-pi`, `full-opencode` and `full-pi-vendor` fixtures, and confirm no duplicate discovery (Pi already reads `~/.agents/skills` and has no `~/.pi/agent/skills` links). Phase 2 may encode today's difference as a fixture test; it must not encode the proposed change until approved.

### Full install writes shared git config

A full install runs `git -C "$REPO" config core.hooksPath .githooks` whenever the checkout is a Git work tree. From a linked worktree this writes the common `.git/config` shared with the main checkout. The ephemeral-worktree guard (`*/.git/worktrees/*`, `*/worktrees/*`) does not match sibling worktrees such as `~/dev/agent-config-sprawl`. The value is relative and identical for every checkout, but it is still a write outside HOME made from a worktree. It is the only such write apart from `vendor/` clones. Do not run `install.sh` from a worktree.

*Deferred — needs approval:* skip the write when `git rev-parse --git-dir` differs from `--git-common-dir`, or when `core.hooksPath` already equals `.githooks`.

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

*Deferred (dotfiles follow-up; no behaviour change while no source exists):* add preventive ignore gates for `.claude/skills`, `.claude/agents`, `.claude/claude-powerline.json`, `.agents`, `.codex/AGENTS.md`, `.codex/agents`, `.codex/prompts`, `.omp/agent`, `.config/opencode/AGENTS.md`, `.pi/agent` and `.pi/web-search.json`.

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

## Deferred behaviour changes (need approval)

1. S16: one owner for `tui.status_line` (proposal: agent-config).
2. S03/S04/S31/S42: full-install `~/.agents/skills` gate aligned with selective install.
3. S44: skip the `core.hooksPath` write from linked worktrees.
4. S07: decide whether paseo/orca hooks are machine state (`sync.sh` filter).
5. S25: gate or drop host `~/.config/omp` overlay links; fix stale `install.sh` comments.
6. S45: retention of the committed npm tree.
7. S02/S51: external collision rule and vendor audit (Phase 3).
8. dotfiles: preventive `.chezmoiignore` gates and the stale `commands/`/`hooks/` wording (follow-up below).

## Instruction conflict: "change both copies together"

Before this change, agent-config `AGENTS.md` said the ownership table "is duplicated in both repos; change both copies together", and dotfiles `AGENTS.md` says the same. Phase 1 changes the agent-config copy only, because dotfiles is out of scope for this run. **Until the dotfiles follow-up lands, the two repositories knowingly disagree**: dotfiles still carries its older full table (including the stale `commands/` and `hooks/` claims, and missing Codex prompts/agents and OMP `keybindings.yml`). Where they differ, this contract wins. Phase 1's exit criterion ("`dotfiles` either references the accepted canonical contract or has a mechanically reconciled view") is **not met** until the follow-up is applied.

## dotfiles follow-up

This is proposed text only; it has not been applied. Replace the whole `## Which repo owns what` section of `~/dev/dotfiles/AGENTS.md` (the heading through the two trap bullets, ending before `## Secrets`) with:

```markdown
## Which repo owns what

One rule settles almost every case: **`~/dev/agent-config` owns what the agent knows and how it behaves; `~/dev/dotfiles` owns the machine it runs on.** Secrets are always dotfiles (1Password + age), never agent-config.

The canonical per-path contract is `docs/ownership.md` (rows in `docs/ownership.tsv`) in `~/dev/agent-config`. Change ownership there first; do not copy its table here.

This repo's side of that contract:

- chezmoi targets: `~/.claude/plugins/claude-hud/config.json` (the one dotfiles path under `~/.claude/`); `~/.config/opencode/opencode.jsonc` (the modify script owns only `$schema`, `lsp` and `permission`); `~/.zshrc` including `ompgo`/`ompcodex`/`pis`/`omps`/`agent-*`; `~/.local/bin/agent-sandbox`, `omp-update-daily` and LaunchAgents; `.gitconfig`, Brewfile, fonts, terminal and editor config.
- shared writer: `~/.codex/config.toml`. `dot_codex/modify_private_config.toml` supplies top-level `model`, `model_reasoning_effort` and `plan_mode_reasoning_effort` only if absent and enforces `tui.status_line`; agent-config's `install.sh` enforces the keys in its `codex/config.toml`. `tui.status_line` is currently written by both — see the contract before changing either.
- sandbox: this repo owns launchers, aliases, machine application and live sandbox operations; agent-config owns the configuration bundle that `agent-sandbox prepare` builds.
- nothing else under `~/.claude/`, `~/.agents/`, `~/.codex/`, `~/.omp/`, `~/.pi/` or `~/.config/omp/` belongs to this repo.

Two traps:

- **Never let chezmoi claim a path agent-config symlinks.** One blind `chezmoi apply` replaces a live symlink with a stale regular file and the edits silently stop reaching the agent. `.chezmoiignore` gates `.claude/CLAUDE.md`, `.claude/settings.json` and `.config/omp`; never `chezmoi add` anything under the agent-config paths listed in the contract.
- **Never edit agent-config's `settings.json` directly.** It is a snapshot that `./sync.sh` overwrites wholesale from `~/.claude/settings.json`. Change the live file, then sync.
```

The same follow-up should also correct two stale comments in dotfiles:

- In `.chezmoiignore`, change "alongside the skills/agents/commands/hooks symlinks" to "alongside the skills and agents symlinks".
- In the `.claude/settings.json` gate comment, change "CLAUDE.md, skills, agents, commands and hooks" to "CLAUDE.md, skills and agents".
- In `install.sh` step 9, change "CLAUDE.md, skills, agents, commands, hooks, or settings.json" to "CLAUDE.md, skills, agents or settings.json".

Optionally, it can add the preventive ignore gates listed under [chezmoi collision inventory](#chezmoi-collision-inventory). The follow-up should also run dotfiles `tests/test-agent-sandbox.py` and confirm that both `AGENTS.md` files point at this contract.
