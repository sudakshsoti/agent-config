# snapshots/

Machine-local harness config, **copied** into this repo rather than symlinked.

Everything else here is linked, so the repo *is* the live file and there is no
sync step. Two surfaces cannot work that way, and each is a copy for its own
reason:

- **`omp/mcp.json`** — README.md's "Secrets policy" calls `~/.omp/agent/mcp.json`
  a live leak path with no guard. OMP writes that file itself; if `omp/` held a
  symlink to it, an `omp mcp add` for a server with an inline `env` API key
  would write a real credential straight into a git working tree. A copy breaks
  that path: nothing OMP writes reaches the tree on its own.
- **`claude/mcp.json`** — Claude Code keeps its user-scope `mcpServers` *inside*
  `~/.claude.json`, a ~70KB state blob that also holds `userID`, `machineID`,
  `oauthAccount` and a feature-flag cache. There is nothing to link; only the
  `mcpServers` object is extracted.

`install.sh` runs the other direction on a fresh machine: it adds the servers a
snapshot names that the live config lacks (`scripts/seed-mcp-servers.py`, and
`claude mcp add-json` for Claude Code) and never edits an existing one, so OAuth
state and tool-side edits survive. A server carrying `env` or `headers` is
refused on both ends. The Claude statusline scripts and theme used to be
snapshotted here; they now live in `claude/` and are linked.

The cost of a copy is drift. Refresh after changing any of these by hand or
through a TUI:

```bash
./scripts/snapshot-machine-config.sh           # refresh from live
./scripts/snapshot-machine-config.sh --check   # report drift, exit 1 if any
```

That script scans every file before writing it and **refuses** anything
credential-shaped, leaving the previous snapshot in place. Failing closed is the
point: copying instead of linking is only worth doing if a secret can never
ride along.

## What the statusline is

`claude/settings.json` (merged into `~/.claude/settings.json` by `install.sh`)
wires `claude/statusline.sh` and `claude/subagent-statusline.sh` up.

`statusline.sh` is a wrapper around the `claude-powerline` npm package (a
runtime dependency, installed separately). It exists because claude-powerline
renders the context token count with a bare `toLocaleString()`, which takes the
system locale — on an en-IN machine 170000 comes out as `1,70,000`, lakh
grouping, correct for rupees and unreadable as a token budget. There is no
config key for the format and no locale that yields `170k`, so the wrapper
rewrites the rendered output and fails open on every path.

`claude-powerline.json` is the theme it renders through: minimal style,
transparent backgrounds, and only the model, git, context and thinking segments
enabled.
