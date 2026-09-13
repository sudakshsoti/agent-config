# TODO

## Next: automatically reconcile the Docker Sandbox bundle

- [ ] Update `agent-sandbox run` so every `pi` or `omp` launch compares committed `HEAD` in canonical `~/dev/agent-config` with the installed bundle's `VERSION` and rebuilds the immutable bundle only when it is stale.
- [ ] Handle commits, pulls, rebases, and branch switches without relying on Git push hooks.
- [ ] If selected bundle paths are dirty, keep using the last valid bundle and print a clear warning rather than packaging uncommitted state.
- [ ] Preserve the existing per-sandbox digest check so already-created sandboxes install the refreshed bundle automatically on their next `pi` or `omp` launch.
- [ ] Do not auto-apply dotfiles; keep `chezmoi diff` plus targeted `chezmoi apply` as an explicit operation.
- [ ] When `sbx` or the launcher is unavailable, fail clearly and point to `pi-host` / `omp-host`; never silently fall back to host execution.
- [ ] Add regression tests for unchanged, stale, dirty, missing-Docker, existing-sandbox, and new-sandbox paths.
