# FFGrep tool-display fix plan

Date: 2026-09-14
Status: diagnosis confirmed, fix not implemented
Scope: `pi-tool-display` custom overrides cannot hide `ffgrep` output; recommend FFF-owned display control

## 1. User symptom

With `pi-tool-display@0.5.0` configured as:

```json
{
  "customToolOverrides": {
    "ffgrep": {
      "enabled": true,
      "kind": "generic",
      "outputMode": "hidden"
    }
  }
}
```

`ffgrep` from `@ff-labs/pi-fff@0.10.6` still rendered its full collapsed preview.
Built-in `bash` displayed `output hidden`, proving display configuration loaded.

A later screenshot showed the same split:

- `ffgrep /Pour over/ ...` expanded with many result lines
- `$ git status --short` collapsed as `output hidden`

The user has since intentionally removed `pi-tool-display`,
`pi-verbosity-control`, and `pi-quiet-activity` from tracked
`pi/settings.json`. Those removals remain local working-tree changes and are
not part of this plan commit.

## 2. Reproduction

A deterministic regression test was added only in a disposable upstream clone:

```text
/var/folders/1_/3rj5g_1x4_7dz5g28_v6ym540000gn/T/tmp.wCrd4eRB8l/upstream/tests/custom-tool-overrides.test.ts
```

Test name:

```text
custom override decorates a tool registered through a different Pi extension API
```

It models two distinct Pi `ExtensionAPI` objects:

1. Display extension registers lifecycle handlers through its own API.
2. FFF-like extension registers `ffgrep` through another API.
3. FFF's `renderResult` retains its original visible renderer.
4. Display configuration requests hidden output.

Result:

```text
Expected: ""
Actual:   "VISIBLE RESULT THAT SHOULD BE HIDDEN"
```

Command:

```bash
./node_modules/.bin/tsx --test \
  --test-name-pattern='different Pi extension API' \
  tests/custom-tool-overrides.test.ts
```

Existing upstream coverage missed this because its late-registration test
registers the late tool through the same mocked API object as
`pi-tool-display`.

## 3. Confirmed root cause

Pi 0.85.1 creates a separate `ExtensionAPI` object for every extension:

- `.../@earendil-works/pi-coding-agent/dist/core/extensions/loader.js`
- `registerTool` stores the supplied definition in the calling extension's registry.
- `pi-tool-display` wraps only its own `pi.registerTool`.
- It therefore cannot intercept `pi.registerTool` calls made by `pi-fff`.
- Its fallback, `pi.getAllTools()`, returns metadata copies without
  `renderCall`/`renderResult`.
- Mutating those lookup results cannot replace FFF's actual renderer.
- Package order and `/reload` cannot merge separate API objects.

The hypothesis that turned out correct is:

> Cross-extension renderer replacement through per-extension `registerTool`
> wrapping plus `getAllTools()` metadata mutation cannot reach another
> extension's live tool definition.

## 4. Rejected alternatives

- Mutating `getAllTools()` results.
- Wrapping only `pi-tool-display`'s own `pi.registerTool`.
- Changing package order or relying on `/reload`.
- Stripping `tool_result` content:
  - would also remove information from model context;
  - is not a UI-only fix.
- Editing installed files under `~/.pi/agent/npm/node_modules`.
- Importing across independently installed Pi package roots.
- Reimplementing FFF search execution in a cosmetic wrapper.
- Private Pi registry/prototype patching.
- Replacing FFF entirely with slower built-in `grep`/`find`.

## 5. Recommended immediate solution

Add UI-only display control to an FFF fork.

### 5.1 Fork source

Fork:

```text
@ff-labs/pi-fff@0.10.6
```

Pin it by exact npm version or commit-pinned Git URL.

### 5.2 Configuration

Add a TUI-only setting, for example:

```json
{
  "resultDisplay": "hidden"
}
```

Use it for:

- `ffgrep`
- `fffind`
- optional `fff-multi-grep`

### 5.3 Rendering change

Change only `renderResult`:

```ts
renderResult(result, options, theme, context) {
  if (config.resultDisplay === "hidden") {
    return new Text("", 0, 0);
  }

  return renderTextResult(result, options, theme, context, 15);
}
```

Preserve:

- complete `execute()` output;
- full tool-result `content` and `details`;
- FFF indexing, cursors, frecency, and performance;
- visible tool-call/progress headers;
- default preview behavior when hidden mode is off.

### 5.4 FFF fork files

1. `packages/pi-fff/src/config.ts`
   - Add and validate the display setting.
2. `packages/pi-fff/pi-fff.schema.json`
   - Add enum/default.
   - Document it as presentation-only.
3. `packages/pi-fff/src/index.ts`
   - Apply hidden rendering in the relevant `renderResult` functions.
   - Do not alter execution or returned content.
4. `packages/pi-fff/test/config.test.ts`
   - Default behavior.
   - Valid hidden value.
   - Invalid-value rejection.
5. Rendering tests
   - Settled rendering produces no result rows.
   - Original text and details remain intact.
   - Non-hidden behavior is unchanged.
   - Cover all exposed FFF tool names.

## 6. Agent-config integration

### 6.1 Package

In tracked `pi/settings.json`, replace:

```json
"npm:@ff-labs/pi-fff"
```

with the pinned fork package.

### 6.2 Configuration

Update tracked `pi/pi-fff.json`, for example:

```json
{
  "$schema": "https://raw.githubusercontent.com/dmtrKovalenko/fff/main/packages/pi-fff/pi-fff.schema.json",
  "enableHomeDirScanning": false,
  "resultDisplay": "hidden"
}
```

If the fork changes the schema URL, update `$schema` accordingly.

### 6.3 Installer

No functional `install.sh` change is expected:

- `pi/settings.json` is already linked.
- `pi/pi-fff.json` is already linked.
- Update comments only if they name obsolete behavior.

### 6.4 Test coverage

Retain or extend coverage proving both managed files install from this repository:

```bash
python3 scripts/test-install-selected-skills.py
```

## 7. Verification

### 7.1 FFF fork

```bash
cd <fff-fork>/packages/pi-fff
bun test
bun run typecheck
```

### 7.2 Agent-config

```bash
cd /Users/sudakshsoti/dev/agent-config
python3 -m json.tool pi/settings.json >/dev/null
python3 -m json.tool pi/pi-fff.json >/dev/null
bash -n install.sh
python3 scripts/test-install-selected-skills.py
./scripts/check.sh
git diff --check
git status --short
```

### 7.3 Pi behavior

Verify at 80, 120, and 160 columns:

- FFF call/progress header remains visible.
- Settled FFF result body occupies no output lines.
- Expanded mode remains hidden if matching display semantics.
- Session/tool result still contains complete matches and details.
- The next model turn can retrieve or use the full result.

## 8. Migration

1. Publish or tag the narrow FFF fork.
2. Update `pi/settings.json` to the pinned fork.
3. Add the new display key to `pi/pi-fff.json`.
4. Run:

```bash
./install.sh --no-external
```

1. Restart Pi.
2. Perform the TUI and session proof above.
3. Keep intentionally removed noisy extensions disabled unless separately approved.

## 9. Rollback

1. Restore:

```json
"npm:@ff-labs/pi-fff"
```

1. Remove the fork-specific display key.
2. Rerun the installer.
3. Restart Pi.

No FFF database or session migration is expected.

## 10. Systemic upstream options

### Option A: Pi core renderer registry

Propose a supported API such as:

```ts
registerToolRenderer(name, renderers)
```

This is the best general platform fix but is not suitable as the immediate dependency.

### Option B: Cooperative display API

Enhance `pi-tool-display` with an explicit configured-tool API, for example:

```ts
decorateConfiguredTool(tool, {
  kind: "generic",
  overrideExistingRenderers: true
})
```

It should:

- resolve `customToolOverrides[tool.name]`;
- generate generic call/result renderers from that entry;
- preserve execution, parameters, preparation, results, and model context;
- support producer-first and display-first load orders.

Because independently installed Pi packages have separate module roots, FFF
cannot import `pi-tool-display` directly. Either extract the dependency-free
Symbol protocol into a tiny shared package or ship a compatible shim inside
FFF. Do not bundle the full display extension merely for its helper.
