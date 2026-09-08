# Pi subagent observability

**Research date:** 2026-09-08 (September 2026)

## Answer

**Yes, Pi can show a Claude Code-style live roster and detailed child views, but not in Pi core alone.** This checkout already has the strongest same-TUI option installed: `@tintinweb/pi-subagents@0.16.1`. Its FleetView shows `main` plus running subagents, and Enter opens a live, auto-updating conversation viewer. Its widget shows live activity, tool counts, tokens, context use and elapsed time. Source: [pi-subagents README](https://github.com/tintinweb/pi-subagents#readme), local package `/Users/sudakshsoti/.pi/agent/npm/node_modules/@tintinweb/pi-subagents/README.md`.

**This checkout currently has FleetView disabled.** `/Users/sudakshsoti/dev/agent-config/pi/subagents.json` contains `{ "fleetView": false }`; the package README documents the toggle at `/agents → Settings → Fleet view`. `widgetMode` is not set, so the package default is its background-agent widget. Source: local `pi/subagents.json`; local package README.

## Comparison

### 1. Pi core

Pi core provides session persistence and navigation (`/resume`, `/tree`, `/fork`, `/clone`), JSONL session files, and a `SessionManager` API. It also provides extension APIs for lifecycle events, custom tools, widgets, overlays and custom renderers. Sources: [sessions docs](https://pi.dev/docs/latest/sessions), [session-format docs](https://pi.dev/docs/latest/session-format), [extensions docs](https://pi.dev/docs/latest/extensions).

The official subagent implementation is still an **example extension**. It starts separate `pi --mode json -p --no-session` processes, parses JSON events, and uses `onUpdate` for progress; it is not a core all-children dashboard or attach/follow UI. Source: [official subagent example](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/examples/extensions/subagent/index.ts). Pi issue [#552](https://github.com/badlogic/pi-mono/issues/552) describes extracting this into a reusable library and lists full observability as a design goal; the current official example remains the reference implementation.

**Possible now:** build a custom roster/dashboard using the extension event and UI APIs. **Not built in:** a cross-process “show every running child and switch into it” screen.

### 2. Installed `@tintinweb/pi-subagents`

This is the closest match to Claude Code inside one Pi TUI:

- FleetView lists `main` and top-level running/queued/recently-finished agents; arrow keys select and Enter opens a live conversation overlay.
- The overlay auto-follows new content, can be scrolled, can steer a running agent, and can stop it.
- The widget shows live tool activity, token totals, context percentage and elapsed time.
- Background agents support queueing, completion notifications, `get_subagent_result`, `steer_subagent`, session resume, JSONL `.output` transcripts, lifecycle events and cross-extension RPC.

Sources: [README](https://github.com/tintinweb/pi-subagents#readme), [changelog](https://github.com/tintinweb/pi-subagents/blob/master/CHANGELOG.md), local `/Users/sudakshsoti/.pi/agent/npm/node_modules/@tintinweb/pi-subagents/src/ui/fleet-list.ts` and `src/index.ts`.

Important limits: FleetView shows only top-level agents; nested children are intentionally hidden from the top-level UI and lifecycle events. Queued agents without a child session are hidden until they start. Only a bounded number of rows render at once, with an overflow count. Default `.output` transcripts live under the OS temp directory, are owner-only and cleared on reboot; `persist_session` is separate and must be enabled for normal Pi session files. Sources: [README nested-agent and transcript sections](https://github.com/tintinweb/pi-subagents#nested-subagents), [README UI section](https://github.com/tintinweb/pi-subagents#ui), local package README.

### 3. tmux / multiplexing

[`pi-tmux-subagents`](https://github.com/masta-g3/pi-tmux-subagents) launches real tmux-backed Pi child sessions. Its `tmux_subagent` tool supports `list`, `get`, `status`, `send`, `wait`, `stop` and attach/follow workflows; children can remain alive for inspection when auto-stop is disabled. This gives each child its own actual Pi UI, at the cost of tmux process/session management. Source: [README](https://github.com/masta-g3/pi-tmux-subagents#readme).

[`pi-command-center`](https://github.com/DanGreinke/pi-command-center) adds a `/cc` full-screen dashboard across tmux panes/windows, auto-refreshing state files, card navigation and Enter-to-jump-to-pane. Its optional supervisor Pi session can list agents, inspect details and send messages through per-workspace inboxes. Source: [README](https://github.com/DanGreinke/pi-command-center#readme).

### 4. Other community approaches

- [`pi-dashboard-subagents`](https://github.com/BlackBeltTechnology/pi-dashboard-subagents) emits every child tool call, reasoning step, text event and error as a structured timeline for `pi-agent-dashboard`. It is foreground-only, in-memory, with no background spawning, `get_subagent_result` or `steer_subagent`. Source: [README](https://github.com/BlackBeltTechnology/pi-dashboard-subagents#readme).
- [`pi-shadow-git`](https://github.com/EmZod/pi-subagent-with-logging) combines per-agent git checkpoints, JSONL audit logs and a `/mc` Mission Control TUI with status, turns, tool calls and errors for many agents. Its workflow expects separate workspaces and environment variables such as `PI_WORKSPACE_ROOT` and `PI_AGENT_NAME`; it is an orchestration/logging system rather than a drop-in viewer for `pi-subagents` records. Source: [README](https://github.com/EmZod/pi-subagent-with-logging#readme).
- [`Mazzy Command Center`](https://github.com/mazurovn/Mazzy-Command-Center) is a larger project-local orchestrator with an authenticated localhost web dashboard, live SSE updates, durable tasks and an evolving own subagent engine. It is source-available under PolyForm Noncommercial, so check the licence before commercial use. Source: [README](https://github.com/mazurovn/Mazzy-Command-Center#readme).

## Practical conclusion

For this setup, **enable FleetView in `pi/subagents.json` or `/agents → Settings → Fleet view`** to get the requested same-terminal experience; no custom code is needed. Use `persist_session` when post-reboot inspection matters. Use `pi-tmux-subagents` or `pi-command-center` when children must be independent panes/processes or visible across multiple Pi instances. A single aggregate dashboard for arbitrary Pi processes, richer historical retention, or visible nested-agent trees still needs an extension/community dashboard or custom integration.
