# RCA: `prompt-capture: no capture` crash (pi + pi-claude-bridge)

Date: 2026-09-13
Symptom: pi exits via `uncaughtException` from `streamClaudeAgentSdk`:

```text
Error: prompt-capture: no capture for this 12961-char system prompt, and it
embeds none of the 1 known. Claude Code would receive none of this turn's
context files, skills or custom instructions.
    at PromptCaptures.resolveOrDerive
      (pi-claude-bridge/src/prompt-capture.ts:135)
    at streamClaudeAgentSdk (pi-claude-bridge/src/index.ts:1496)
    at .../pi-blackhole/src/om/provider-stream.ts:186
```

## Root cause

The throw is a deliberate fail-closed guard, not a null-pointer. The bridge
records the assembled prompt once per agent in `before_agent_start`
(`pi-claude-bridge/src/index.ts:1960` → `promptCaptures.record`) and resolves
it at provider-stream time (`src/index.ts:1496` →
`promptCaptures.resolveOrDerive`). Resolution succeeds only on an exact key
match or when the live prompt embeds a known prompt verbatim (wrapping is OK).
The crashing turn satisfied neither: a 12961-char prompt against 1 known
capture with zero embedding.

Audited prompt rewriters among installed packages:

- `pi-quiet-activity/index.ts` (`before_agent_start`) returns
  `event.systemPrompt + FINAL_RESPONSE_INSTRUCTION`, but **only when
  `ctx.mode === "tui"` and quiet mode is enabled**. Any turn recorded with the
  suffix and resolved without it (non-TUI path, F9 toggle mid-session) misses
  exactly, and the shorter prompt cannot embed the longer recorded one.
- `@tintinweb/pi-subagents/src/prompts.ts` `buildAgentPrompt()`:
  `"replace"` mode is env header + config prompt with **no parent identity**,
  so it can never embed the parent capture. `"append"` mode embeds the parent
  verbatim and is safe.

Structural aggravator: the bridge shares the provider stream function globally
(`ACTIVE_STREAM_SIMPLE_KEY`, `src/index.ts:151,2061`), so a child's query is
served by the parent's `streamSimple` — but `promptCaptures`
(`src/index.ts:831`) is **per module instance**. The child records into its own
map (if it records at all) while the parent resolves against its own, which
holds only the 1 parent capture.

Ruled out: `pi-blackhole` (pure provider router, no rewrite),
`cc-safety-net` (no `before_agent_start`/`systemPrompt` hook in `dist/pi/`),
`pi-lens`, `pi-mcp-adapter`. The error text's "extension loaded after
claude-bridge" theory does not fit: the only wrapper found
(`pi-quiet-activity`) loads *before* the bridge per `settings.json` order.

Ranked hypotheses: (H1) a `prompt_mode: replace` / isolated subagent ran on a
bridge model; (H2) quiet-activity conditional-wrap skew across turns/modes;
(H3) pi rebuilt the prompt mid-session (tools/skills/context change) with no
re-record; (H4) stale map after `/reload` / resume / fork.

Note: the stack's `pi-blackhole/.../provider-stream.ts:186` has no counterpart
in installed blackhole 0.5.4 source — it is a source-mapped frame from the
bundled dist. Do not chase line 186 literally; re-verify versions on repro.

## Plan

1. **Confirm the hypothesis with the bridge debug log.**
   Run `CLAUDE_BRIDGE_DEBUG=1 pi`, reproduce, and inspect
   `~/.pi/agent/claude-bridge.log`. Compare `record` vs `resolve` lines:
   prompt lengths and `moduleInstanceId` values. Split IDs point to H1/H4;
   same ID with a suffix-sized delta points to H2; same ID with an arbitrary
   delta points to H3.

2. **Confirm the crashing agent's prompt mode.**
   Identify which subagent type was active at the crash and read its
   `prompt_mode`. `replace` confirms H1. Re-run the same task with an
   `append`-mode / clone agent (empty `systemPrompt`); crash disappearing
   confirms H1.

3. **Toggle-test H2.**
   Reproduce with `/quiet-activity off` (or `enabled: false` in
   `~/.pi/agent/extension-data/quiet-activity/config.json`).

4. **Apply immediate workarounds.**
   Run `replace`-mode / isolated subagents on a non-bridge model; keep bridge
   models on the main agent plus `append`-mode agents. Disable
   `pi-quiet-activity` for bridge sessions if H2 is confirmed. Keep the bridge
   last among prompt-touching extensions in `settings.json`.

5. **Harden the bridge (upstream fix, `pi-claude-bridge` repo).**
   Share `PromptCaptures` via a `Symbol.for` global like
   `ACTIVE_STREAM_SIMPLE_KEY` so parent/child instances resolve against one
   map. On resolve-miss, record the live `systemPromptOptions` and continue
   with a loud warning plus `diagDump` instead of an `uncaughtException` that
   kills pi; at minimum downgrade to a failed turn, not a dead process.
   Handle replace-mode explicitly by projecting the turn's own
   skills/context. Correct the error text to enumerate the actual
   `before_agent_start` chain instead of blaming a later extension.

6. **Coordinate subagents (`pi-subagents`).**
   Ensure child sessions either load the bridge (so they record) or route
   replace-mode children off bridge models until the shared-map fix lands;
   document that replace-mode + bridge is unsupported.

## Acceptance criteria

- The H1 repro (replace-mode subagent on a bridge model), the H2 repro (F9
  toggle mid-session), and the `/reload` case all complete with no
  `uncaughtException` and the process stays alive.
- Skills and context files for the live turn are verifiably forwarded to
  Claude Code in each case (debug log shows a resolved or re-recorded
  capture).
- A resolve-miss degrades to a failed turn with a loud warning, never a
  process exit.
