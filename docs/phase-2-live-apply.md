# Phase 2 live-apply runbook

Status: prepared for a human-run session (#42). Nothing here has been run
against a real HOME. An agent must not run these steps.

Phase 2 was reconciled with the OMP/Pi narrowing (`4a7edc49`). That removed
several surfaces the original steps assumed: `sync.sh`, `codex/config.toml`,
the sandbox bundle, and the `docs/ownership.{md,tsv}` contract, which never
reached `main`. The old steps L1 (dotfiles `docs/ownership-contract-followup`
merge for the Codex key partition) and L4 (removing host `~/.config/omp`
overlay links) are therefore dropped. L4 returns only if #38 is decided in
favour of retiring the host overlays.

## Preconditions

- **P1 — backups.** Record the current state outside both repositories:

  ```bash
  out=~/agent-config-preapply-$(date +%Y%m%d-%H%M%S).txt
  for d in ~/.agents/skills ~/.omp/agent ~/.config/omp ~/.pi/agent \
    ~/.claude ~/.claude/skills ~/.codex ~/.config/opencode; do
    echo "== $d"; ls -la "$d"
  done >"$out" 2>&1
  ```

- **P2 — merged code.** The Phase 2 PR is merged to `main`, and the canonical
  checkout `~/dev/agent-config` is on `main`, clean and up to date
  (`git -C ~/dev/agent-config status --short` prints nothing).
- **P3 — harnesses idle.** No OMP or Pi session is running, because both write
  through the links being refreshed.
- **P4 — retired-harness links you still use.** `--prune` (L5) also runs
  the retired-harness cleanup from `4a7edc49`. It removes every symlink into
  this checkout at `~/.claude/CLAUDE.md`, `~/.claude/claude-powerline.json`,
  `~/.claude/skills/*`, `~/.claude/agents/*`, `~/.codex/AGENTS.md`,
  `~/.codex/agents/*`, `~/.codex/prompts/*` and
  `~/.config/opencode/AGENTS.md`. On 2026-09-14 these links were live on this
  machine, including `~/.claude/CLAUDE.md` and dozens of `~/.claude/skills`
  entries that Claude Code still loads. If Claude Code, Codex or OpenCode
  should keep them, skip L5 or move those links out of the way first. Only
  dotfiles or a hand-made link should own them after the cull.

## Steps

Each step names its verification and rollback. Stop at the first failed
verification.

| Step | Action | Verify | Roll back |
| --- | --- | --- | --- |
| L1 | `git -C ~/dev/agent-config pull --ff-only` | `git -C ~/dev/agent-config log --oneline -1` shows the merge | `git -C ~/dev/agent-config reset --hard <previous sha>` |
| L2 | `cd ~/dev/agent-config && bash scripts/check.sh` (the first run bootstraps the ignored `node_modules/` with `npm ci`) | `0 failed`; `test-operational-footer.mjs` is `ok`; `git status --short` is empty | `rm -rf node_modules` (ignored build product) |
| L3 | `python3 scripts/audit-local.py >~/agent-config-audit-before.txt; echo exit=$?` | `exit=0`; read the findings (expected on 2026-09-14: `dangling-link` for six retired skills and `undeclared-checkout` for three vendor clones) | none, because the audit is read-only |
| L4 | `./install.sh` | `linked=… skipped=0`; `~/.agents/skills` entries are all symlinks | re-link from P1, or check out the previous sha and re-run `./install.sh` |
| L5 | `./install.sh --prune` (read P4 first) | `pruned=` covers the L3 `dangling-link` findings plus the retired-harness links from P4; a second `--prune` prunes 0 | use P1 to recreate any retired-harness link you still need with `ln -s`; links to deleted skills need no rollback |
| L6 | Restart OMP and Pi | Both start; the skill list shows each skill once | restore from P1 |

Order: L2 before L4 so a failing check stops the apply before any link
changes. L3 before L5 so prune output can be compared with an independent
read-only report.

## Post-apply check (AT22)

```bash
cd ~/dev/agent-config
python3 scripts/audit-local.py; echo exit=$?
for d in ~/.agents/skills/*/; do [ -L "${d%/}" ] || echo "${d%/}"; done
git status --short
```

Expect `exit=0` with no `dangling-link`, `non-symlink-entry` or
`chezmoi-collision` findings; no non-symlink output; a clean tree.
`undeclared-checkout` findings are informational: vendor clones are never
deleted automatically.

## Out of scope

- Deleting undeclared `vendor/` checkouts.
- Any dotfiles merge or `chezmoi apply`.
- Retiring host overlay links (#38, on hold).
