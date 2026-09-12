#!/usr/bin/env node

import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { createRequire } from "node:module";
import { resolve } from "node:path";
import vm from "node:vm";

const require = createRequire(import.meta.url);
const tui = require("@earendil-works/pi-tui");
const sourcePath = resolve(
  process.argv[2] ??
    new URL("../pi/extensions/operational-footer/index.js", import.meta.url)
      .pathname,
);
const source = await readFile(sourcePath, "utf8");
const transformed = source
  .replace(
    'import { truncateToWidth, visibleWidth } from "@earendil-works/pi-tui";\n',
    "const { truncateToWidth, visibleWidth } = tui;\n",
  )
  .replace(
    'import { relative, resolve, sep } from "node:path";\n',
    "const { relative, resolve, sep } = path;\n",
  )
  .replace("export default function", "function")
  .concat("\nmodule.exports = operationalFooter;\n");
const module = { exports: {} };
vm.runInNewContext(transformed, {
  console,
  module,
  path: require("node:path"),
  process,
  tui,
});
const operationalFooter = module.exports;

const ANSI_PATTERN = /\x1b\[[0-9;]*m/g;
const stripAnsi = (value) => value.replace(ANSI_PATTERN, "");
const theme = {
  fg: (_color, value) => `\u001b[38;5;245m${value}\u001b[0m`,
};

function renderFooter({
  width = 120,
  statuses = new Map(),
  entries = [],
  cwd = "/Users/me/project",
} = {}) {
  let footer;
  const ctx = {
    cwd,
    model: { id: "gpt-5.6-luna", contextWindow: 272_000 },
    thinkingLevel: "high",
    sessionManager: { getEntries: () => entries },
    getContextUsage: () => ({ percent: 42.1, contextWindow: 272_000 }),
    ui: {
      setFooter: (factory) => {
        footer = factory({ requestRender() {} }, theme, {
          getGitBranch: () => "feature/footer",
          getExtensionStatuses: () => statuses,
          onBranchChange: () => () => {},
        });
      },
    },
  };

  operationalFooter({
    on(event, handler) {
      assert.equal(event, "session_start");
      handler({}, ctx);
    },
  });

  assert(footer, "footer should be registered");
  const lines = footer.render(width);
  assert.equal(lines.length, 2, `expected two rows, got ${lines.length}`);
  for (const line of lines) {
    assert(
      tui.visibleWidth(line) <= width,
      `footer line exceeds ${width} columns: ${stripAnsi(line)}`,
    );
  }
  return lines.map(stripAnsi);
}

const healthy = renderFooter({
  statuses: new Map([
    ["pi-lens-lsp", "LSP Active: typescript, eslint"],
    ["mcp", "🔌 MCP: 3 servers enabled (1 disabled)"],
    ["tokenSpeed", "⚡ TPS: 42.0"],
  ]),
});
assert.match(healthy[0], /gpt-5\.6-luna · high/);
assert.match(healthy[1], /context 42\.1% \/ 272k/);
assert.doesNotMatch(healthy[1], /LSP|MCP|TPS|🔌/);

const degradedWide = renderFooter({
  statuses: new Map([
    ["pi-lens-lsp", "LSP Active: typescript · LSP Failed: yaml, eslint, json"],
    ["mcp", "🔌 MCP: 3 servers enabled (1 disabled)"],
  ]),
  entries: [
    {
      type: "message",
      message: {
        role: "assistant",
        usage: {
          input: 12_000,
          output: 4_000,
          cacheRead: 0,
          cacheWrite: 0,
          reasoning: 0,
          totalTokens: 16_000,
          cost: {
            input: 0,
            output: 0,
            cacheRead: 0,
            cacheWrite: 0,
            total: 0.12,
          },
        },
      },
    },
  ],
});
assert.match(degradedWide[1], /LSP failed: yaml, eslint \+1/);
assert.doesNotMatch(degradedWide[1], /MCP|cache|↑|↓|\$/);

const degradedNarrow = renderFooter({
  width: 80,
  statuses: new Map([
    ["pi-lens-lsp", "LSP Failed: yaml, eslint, json"],
    ["mcp", "MCP: Failed to connect to github"],
  ]),
});
assert.match(degradedNarrow[1], /LSP ! yaml \+2/);
assert.match(degradedNarrow[1], /MCP ! github/);

const auth = renderFooter({
  statuses: new Map([["mcp-auth", "Authenticating github..."]]),
});
assert.match(auth[1], /MCP authentication/);

const longPath = renderFooter({
  width: 80,
  cwd: "/Users/me/worktrees/a-very-long-project-name-with-many-segments",
});
assert.match(longPath[0], /…/);
assert.match(longPath[0], /feature\/footer/);
