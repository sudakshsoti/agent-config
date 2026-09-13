# Sprawl baseline — Phase 0

Status: historical evidence. Recorded 2026-09-14 for
`plans/reduce-agent-config-architecture-sprawl.md`, Phase 0. It describes the
repository as it stood at the revisions below. It is not current truth once
later phases land.

## Revisions

| Repository | Revision | Notes |
| --- | --- | --- |
| agent-config base | `fc15a3a462d543398af61fecee18265a5af89cce` | `docs: add repository sprawl audit plan` |
| agent-config branch head (inventoried tree) | `f7cf2536cc82fe060cb0b675ee04edeeb0b241fb` | `sprawl/phase-0-2`, worktree `~/dev/agent-config-sprawl`; adds only the plan tracker |
| dotfiles (read-only) | `bb3d28fa28e68898a6eea7f30bf59ab1a67123dd` | `git -C ~/dev/dotfiles rev-parse HEAD` |

Environment: macOS 26.6.2 (Darwin 25.6.0), Python 3.14.7, Node v24.14.0,
`/bin/bash` 3.2.57, jq 1.7.1-apple, Info-ZIP 3.0.

The main checkout (`~/dev/agent-config`) had unrelated uncommitted work
(`.pi/subagents.json`, `pi/subagents.json`, `plugins.txt`, `skills/README.md`,
untracked skills and ZIPs). It was not read for the inventory, modified, stashed
or committed. The only thing read from it was `vendor/`, for the vendor fixture
variant.

## Ownership-matrix schema

Every managed surface is one row in [`surfaces.tsv`](surfaces.tsv), with these
fields:

| Field | Meaning |
| --- | --- |
| `id` | Stable row id (`Snn`) for later phases to reference |
| `harness` | claude, codex, omp, opencode, pi, shared, sandbox, dotfiles, repo, distribution |
| `live_destination` | Path the tool reads, or `(not delivered)` |
| `source_repo` | agent-config, dotfiles, external, shared, neither |
| `source_path` | Canonical source path in that repository |
| `delivery` | One of: symlink, copy-if-absent, merge, generated artifact, external checkout, plugin installation, unmanaged. Qualifiers such as "per file" are allowed |
| `writeback_authority` | Who may write or merge the live file |
| `writes_through_symlink` | Whether a tool write lands in the source repository |
| `state_class` | credential, runtime, preference, generated or historical |
| `verifier` | Check that currently covers it (script, fixture or none) |
| `condition` | Gate under which install.sh delivers it |
| `status` | `settled`, or `ambiguous: <reason>` for Phase 1 to resolve |

Sources read: `install.sh`, `sync.sh`, `scripts/apply-codex-config.py`,
`scripts/apply-web-search-config.py`, `scripts/build-agent-sandbox-bundle.sh`,
`sandbox/bootstrap/manifest.txt`, `plugins.txt`, `settings.json`, `AGENTS.md`
and `.githooks/pre-commit` in agent-config. From dotfiles (read-only):
`AGENTS.md` ownership table, `.chezmoiignore`, `dot_codex/modify_private_config.toml`,
`dot_config/opencode/modify_opencode.jsonc`, `dot_zshrc.tmpl` and
`private_dot_local/bin/executable_agent-sandbox`.

## Surface inventory summary

52 rows across all harnesses. Rendered by delivery:

| Delivery | Rows |
| --- | --- |
| symlink | S01, S03, S06, S09, S10, S15, S17–S25, S29, S32–S39 |
| external checkout + symlink | S02, S04 |
| copy-if-absent (+ sync.sh pull-back) | S07 |
| merge | S16 (two writers), S30 (dotfiles), S40 |
| generated artifact | S45, S46, S47 |
| plugin installation | S12 |
| chezmoi apply (dotfiles-owned) | S11, S49 |
| copy by bundle installer | S48 |
| migration removal | S05 |
| git config write (outside HOME) | S44 |
| fixed-path reference, not installed | S13 |
| unmanaged / not delivered | S08, S14, S26–S28, S31, S41–S43, S50–S52 |

### Marked ambiguous (for Phase 1)

- **S03/S04/S31 shared skill root:** full install populates `~/.agents/skills` only when `~/.codex` exists; selective install does so when `~/.codex` or `~/.pi/agent` exists. Pi and opencode read this root.
- **S02 external skills:** no precedence rule for duplicate names across external sources. `stablyai/orca` is declared but absent from local `vendor/`.
- **S07 Claude settings snapshot:** tracked `settings.json` contains paseo and orca hook commands that `sync.sh` does not filter. `enabledPlugins` includes `baseline@baseline`, which is not in `plugins.txt`.
- **S13 statusline scripts:** `settings.json` references `$HOME/dev/agent-config/scripts/*.sh` by fixed path. They are not delivered links.
- **S14 `~/.claude/commands/` and `hooks/`:** the dotfiles table assigns them to agent-config. agent-config has no source for them, but `--prune` still scans them.
- **S16 `~/.codex/config.toml`:** two mergers (the dotfiles chezmoi modify script and `apply-codex-config.py`), with no recorded key partition or ordering.
- **S21 `~/.omp/agent/keybindings.yml`:** linked by install.sh but missing from both ownership tables.
- **S25/S26 OMP overlays:** linked even when `~/.omp/agent` is absent. install.sh comments name `~/.local/bin/omp-{go,codex}-overlay` consumers, which are not tracked in dotfiles. The dotfiles `ompgo`/`ompcodex` now run OMP inside `agent-sandbox` with guest paths.
- **S43 project-scope `.pi/subagents.json`:** a tracked file that the tool itself writes.
- **S45 committed npm tree:** `node_modules/` (13,865 files), `package.json` and `package-lock.json` have no documented regeneration rule. `test-operational-footer.mjs` depends on it.
- **S48 sandbox guest destinations:** not inventoried in detail.
- **S51 undeclared vendor checkouts** in the main checkout. They may correspond to its uncommitted `plugins.txt`.

Ownership-table drift observed (input to Phase 1, not resolved here):

- dotfiles lists `commands/` and `hooks/` and an `ompgo`/`ompcodex` row. agent-config does not.
- agent-config lists Codex/Pi prompts, `pi-web-access` merge wording and the `opencode.jsonc` grouping differently.
- Both tables omit OMP `keybindings.yml`.

## Install fixtures

Command: `python3 docs/sprawl-baseline/fixtures/run_fixtures.py`, run from a
scratchpad copy. The copied script uses sibling `checkout/`, `bin/` and `out/`
directories.

Method:

- The checkout is `git archive HEAD` extracted to a scratch directory. It is not a Git work tree, so install.sh skips its `core.hooksPath` write.
- `git` and `claude` are replaced by stubs that exit 93 and log every call.
- The environment is cleared (`HOME`, `PATH`, `LANG` only), so `XDG_CONFIG_HOME` and `PI_CODING_AGENT_DIR` cannot redirect writes.
- Each case uses a fresh temporary `HOME`.
- Full install uses `--no-plugins`. Selective install uses `--skills-only=commit,vibe`.
- The vendor variants copy the three declared, locally present vendor sources from the main checkout, without `.git`.

Safety review before running:

- install.sh writes only under `$HOME`, with two exceptions: `git -C $REPO config core.hooksPath` (skipped here) and `$REPO/vendor` clones (skipped with `--no-plugins`).
- The worktree guard matches `*/.git/worktrees/*` and `*/worktrees/*`. Neither `~/dev/agent-config-sprawl` nor the scratch copy matches.
- Every case reported `checkout unchanged: True`. The only stub call was `git -C <REPO> rev-parse --git-dir` (full install's hooks-path probe). Nothing invoked the network or `claude`.

Outputs, normalised to `<HOME>`, `<REPO>` and `<STUBS>`, are in [`fixtures/`](fixtures/):

| Case | Pre-created dirs | Vendor | Exit | Links | Files | `~/.claude/skills` | `~/.agents/skills` |
| --- | --- | --- | --- | --- | --- | --- | --- |
| full-none | none | no | 0 | 44 | 1 | 38 | 0 |
| full-codex | `.codex` | no | 0 | 85 | 2 | 38 | 38 |
| full-pi | `.pi/agent` | no | 0 | 67 | 3 | 38 | **0** |
| full-omp | `.omp/agent` | no | 0 | 51 | 1 | 38 | 0 |
| full-opencode | `.config/opencode` | no | 0 | 45 | 1 | 38 | 0 |
| full-all | all four | no | 0 | 116 | 4 | 38 | 38 |
| full-pi-vendor | `.pi/agent` | yes | 0 | 81 | 3 | 52 | **0** |
| full-all-vendor | all four | yes | 0 | 144 | 4 | 52 | 52 |
| selective-none | none | no | 0 | 2 | 0 | 2 | 0 |
| selective-codex | `.codex` | no | 0 | 4 | 0 | 2 | 2 |
| selective-pi | `.pi/agent` | no | 0 | 4 | 0 | 2 | **2** |
| selective-all | all four | no | 0 | 4 | 0 | 2 | 2 |

Observed behaviour, recorded as-is and not changed:

- **Codex-gated shared root:** a full install with Pi but no `~/.codex` delivers no skills to `~/.agents/skills`, so Pi receives none from install.sh. A selective install with Pi only does populate `~/.agents/skills`. Full and selective installs therefore disagree for Pi-only (and opencode-only) machines.
- Selective install touches only `~/.claude/skills` and optionally `~/.agents/skills`. It does not copy `settings.json`, link `CLAUDE.md`/agents/overlays, merge configs, touch externals or run git.
- Full install links `~/.config/omp/*` overlays even with no harness present (full-none).
- Full install always copies `~/.claude/settings.json` (sha256 `74fb2f45…`, identical to tracked) and links `CLAUDE.md`, `claude-powerline.json` and `agents/plan-critic.md`.
- With `.pi/agent`, both `~/.pi/web-search.json` and `~/.pi/agent/web-search.json` are created (sha256 `228941dd…`).
- With `.codex`, `~/.codex/config.toml` is created by merge (sha256 `d5311a04…`).
- Without vendor, every `external` line prints `SKIP … vendor/<slug> is absent`. With vendor, 14 external skills are linked (`external=3` sources) and `stablyai/orca` is skipped. No repo-owned name shadowed an external one.

## Test results

Each command was run individually from the worktree root. `check.sh` was also
run once as an aggregate.

| Command | Exit | Summary line | In `check.sh` | In pre-commit |
| --- | --- | --- | --- | --- |
| `python3 scripts/lint-skills.py <repo>` | 0 | `38 passed, 0 failed, 1 warnings (not fatal)` (WARN macos-design-guidelines body 37356 bytes) | yes | yes |
| `python3 scripts/check-zips.py <repo>` | 0 | `38 active, 0 stale, 0 missing, 0 orphan` | yes | yes |
| `python3 scripts/test-apply-codex-config.py` | 0 | `Ran 2 tests … OK` | yes | no |
| `python3 scripts/test-apply-web-search-config.py` | 0 | `Ran 14 tests … OK` | yes | yes |
| `python3 scripts/test-build-agent-sandbox-bundle.py` | 0 | `Ran 16 tests in 137.306s OK` | yes | no |
| `python3 scripts/test-design-instructions.py` | 0 | `design instruction contract: ok` | yes | yes |
| `python3 scripts/test-install-selected-skills.py` | 0 | `Ran 8 tests … OK` | yes | no |
| `python3 scripts/test-omp-catastrophe-policy.py` | 0 | `Ran 5 tests … OK` | yes | no |
| `node scripts/test-catastrophe-guard.mjs` | 0 | `catastrophe-guard: 71 passed, 0 failed` (plus Node MODULE_TYPELESS_PACKAGE_JSON warning) | yes | no |
| `node scripts/test-operational-footer.mjs` | 0 | no output (bare `assert` script; silent pass) | **no** | no |
| `bash scripts/test-subagent-statusline.sh` | 0 | `8 passed, 0 failed` | **no** | no |
| `bash scripts/check.sh` | 0 | `9 passed, 0 failed` | — | — |

Not invoked by `check.sh`: `test-operational-footer.mjs` and
`test-subagent-statusline.sh`. `build-zip.sh`, `statusline.sh` and
`subagent-statusline.sh` are not tests. dotfiles' `tests/test-agent-sandbox.py`
was not run because dotfiles is read-only for this phase.

## Committed generated artifacts

`git ls-files dist` (sha256):

```
f611db0f306ce35140b189969444452bcaba0702719f672e61f1193665a3c482  dist/backlog.zip
06049191180a4298617e202c6f70f1a33bf62f2b89df7f49ed339ff0246435c8  dist/clinical-reasoning.zip
e53ed4accd444a295eb0afcfdc60c69a836835309dd24b6d33fda082f5fee5d5  dist/codebase-memory.zip
add7a8b9338330343a00d493d2ae198b524b3944510584509309de61d34b3f4f  dist/commit.zip
bc8e12a5be8f6ab5dae626af0a2b0c77520fa29f53c8fe99e5417278b2a1f74e  dist/design-grill.zip
fc1f464c3454257b0d107cf69b7ec144a50cf4cc1f907e64dc6e55cc2a307691  dist/design-interface.zip
018a4621094da0e60c7d4f05ca0afd4b0549b9d20d8d0edac235b6068db31748  dist/design-strategy.zip
43f380e87377e01bcfc55c4fefb1243c523f2ba51b12e6ccb61bae0eab2c625e  dist/design-typography.zip
0c199e5bbdbbaf8dc7d7842a5f61207baaa9448a7038ab9eef14461440a51bae  dist/design-visual-system.zip
0870d6f6fc9372cbd75506ea3222d4c5ba68ca2510d3255d683fb3c771528d35  dist/diagnosing-bugs.zip
583ee7dc19bf32bce39ad3cd3de4ef575c0367a30e912916c5b42f3f094c969c  dist/execute-plan.zip
ba2209e37558407ca66a6e6b41fe72826d78af781834489676a87620e4995a57  dist/find-skills.zip
a81533add3f567f0567fb579f4d7da1326df0c380cda342256227365ad35d874  dist/frontend-artifact.zip
75ed7b1d6a9db2fd7891d588578b3425f1c6f4ad0cb38e7494b36dfeb98c5020  dist/geopolitics.zip
9607668d57e46e276ce61340749336847793724856413e848f4dc8d097aa5cf8  dist/grilling.zip
b168a7b5573903ba72c97fe24f5d0728004a88ae02d7f50d2bf221f100f1d666  dist/gtd.zip
26222c77373b292d62f88730bd32e0d57417c199df305a1fe0d38f9259db8d0a  dist/handoff.zip
f1d9c48ec046ab7c7d0422ee8063c73fab05d2c4426bfe7262b9abb724385ddf  dist/homelab-deploy.zip
6ae86825b5b32f255da9900901a17f53a452478de5a83268d0eb7c97b76c0905  dist/humanizer.zip
ce7c3525f4e2309bd34c2a19703795869c6a9ad4d8a231a701ce28ff3d15cf0e  dist/macos-design-guidelines.zip
c4e5dbbfce823b15aa89c0a8cff9061a4400121f88fd2b0a3c2adc21bd987187  dist/maintainability-review.zip
90d7e65c315eb796af5b0a292708903e2bd2870cfb85868c8c54d5217f9273a8  dist/merge.zip
b650beb547a940c91548cb77eb3702cbe56df0721a6f22ee42130755cc73848c  dist/n8n-deploy.zip
f0175a9f2b535d6075094329f632dd2eb2c51f0deb51f525f1512169c9c3dcf3  dist/obsidian-markdown.zip
5df13ac9cce9e1ba95a505fe85fa0db65313fec5dfba74ab2c28210f49d5a27a  dist/peer-review.zip
8cd95489d2d6338b0f7642e8c7d26ede2dd4ded6c59a009cc2d23724a64ff9f6  dist/pr.zip
2325e9814245b3415de404b2660c6f9041d96cde49e42be04c2371528d8765ab  dist/push.zip
408d9fa048176288858fbb00b9b244111bebf3e2693fb18abdc2cdf42781338c  dist/research.zip
06d9e0f2a4dcb0fdb172c627e1b193af42c7a7e90bd49445a9c32f9e147e9116  dist/rights-counsel.zip
1f81dee1355b089c70476abf9bb40aa49b6c73eac2039ed2032905a10bb38bb6  dist/self-review.zip
4b24f1edc6b3a59ff06c02f5efafc1d87c88abb0c8b29df7ba3005fec2fd6876  dist/shopping-research.zip
02332ce58460552342ab22148d19a44e7cbffb3163c0dbf60eaebebfa7788e8e  dist/strategy-counsel.zip
99c91dceb18679b943ea115ce00bf309beb6debb4107d048b8deeeeed729c8f3  dist/update-branch-name.zip
9cdf3b5b23c526d202611b5cfa63f200bcad810428762a580b65367bd955395b  dist/ux-writing.zip
83fe65b62aa0861e919cd8ce4da263fcdb6c6e07c8727f06cb53880b29f523fa  dist/vbc-design.zip
a21d70ab6a68280535525551bdfed33f118570b35b4515307bca74a787ace71a  dist/vedic-astrology.zip
b089e3e5d7ff0d11879909741feafc60015963881c1bb2f6f5a989783238d3db  dist/vibe.zip
9b3433e3e28f44162fca18cc956dcd100b7430af1b7b7c6411333d6e93a6946c  dist/writing-editor.zip
```

Other committed generated or snapshot content:

```
74fb2f453f85b0d135222e695c5fd78e3df8de84bc19b455b9e5f7348574cbc3  settings.json            (sync.sh snapshot of live file)
b1acfe86aabfc50cc21bcf568ccb9555a39716f75da1f72ec833523c802d4ea4  package.json
eb76b39acb3ae0774e1451f0d54aee7025f3d06759f87994f9398a65335c01bf  package-lock.json
41bf24db2754122cc4fa0906afff69ec2927c7e6f8c30a974b41d5171f2b8d35  omp/config.2026-08-30.yml (historical snapshot)
1bd2435bab4080af344ab6410369c4eb90b1ddcc23191fadf17a9765371934e5  omp/config.2026-09-03.yml (historical snapshot)
git tree 6ddee9dfbd9b7a2f5f58124ec65c405b324e0480  node_modules/ (13,865 files)
git tree 2190f94dfbc9d98e4ff1be46555683870fa196b0  sandbox/bootstrap/
git tree a6e0cee6efb763692013e061e69281665f64f98d  skills/ (ZIP sources)
git tree 6df9c66a3906e8baa195a464e5a983ee1891e2b6  archive/ (20 files)
```

Vendor revisions used by the vendor fixtures (main checkout, floating, read-only):
`BexTuychiev-firecrawl-claude-code-skill cc33c614`, `emilkowalski-skills d23d7f88`,
`anthropics-claude-code b5932767`.

## Commands run

```sh
git -C ~/dev/agent-config-sprawl rev-parse HEAD            # f7cf2536…
git -C ~/dev/agent-config-sprawl merge-base HEAD fc15a3a4  # fc15a3a4…
git -C ~/dev/dotfiles rev-parse HEAD                       # bb3d28fa…
git ls-files dist | xargs shasum -a 256
git rev-parse HEAD:node_modules HEAD:archive HEAD:sandbox/bootstrap HEAD:skills
# each test listed in the table above, individually, then:
bash scripts/check.sh
# fixtures (from scratchpad):
git -C ~/dev/agent-config-sprawl archive HEAD | tar -x -C <scratch>/checkout
python3 <scratch>/run_fixtures.py
```
