# TODO

## prompt-capture crash (pi + pi-claude-bridge)

See `plans/pi-claude-bridge-prompt-capture-rca.md`.

- [ ] Confirm the hypothesis via `CLAUDE_BRIDGE_DEBUG=1` log (record vs resolve lengths, `moduleInstanceId` split) and repro tests (replace-mode subagent, `/quiet-activity off`, `/reload`).
- [ ] Apply workarounds: replace-mode / isolated subagents on non-bridge models; bridge models on main + append-mode agents.
- [ ] Upstream bridge fix: shared `PromptCaptures` via `Symbol.for`, graceful miss (failed turn, not process exit), replace-mode projection, corrected error text.
- [ ] Subagent coordination: child sessions load the bridge or route replace-mode children off bridge models.

## Next: automatically reconcile the Docker Sandbox bundle

- [ ] Update `agent-sandbox run` so every `pi` or `omp` launch compares committed `HEAD` in canonical `~/dev/agent-config` with the installed bundle's `VERSION` and rebuilds the immutable bundle only when it is stale.
- [ ] Handle commits, pulls, rebases, and branch switches without relying on Git push hooks.
- [ ] If selected bundle paths are dirty, keep using the last valid bundle and print a clear warning rather than packaging uncommitted state.
- [ ] Preserve the existing per-sandbox digest check so already-created sandboxes install the refreshed bundle automatically on their next `pi` or `omp` launch.
- [ ] Do not auto-apply dotfiles; keep `chezmoi diff` plus targeted `chezmoi apply` as an explicit operation.
- [ ] When `sbx` or the launcher is unavailable, fail clearly and point to `pi-host` / `omp-host`; never silently fall back to host execution.
- [ ] Add regression tests for unchanged, stale, dirty, missing-Docker, existing-sandbox, and new-sandbox paths.
