#!/usr/bin/env node
// Tests for the Pi catastrophe guard extension.
//
// The extension is ESM written as .js; Node detects the module syntax and
// imports it directly (the repo package.json has no "type" field).

import assert from "node:assert/strict";
import {
  mkdirSync,
  mkdtempSync,
  realpathSync,
  rmSync,
  symlinkSync,
  writeFileSync,
} from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";

const modulePath = new URL(
  "../pi/extensions/catastrophe-guard/index.js",
  import.meta.url,
);
const guard = await import(modulePath.href);

const failures = [];
let passed = 0;

async function test(name, fn) {
  try {
    await fn();
    passed += 1;
  } catch (error) {
    failures.push({ name, error });
  }
}

// ---------------------------------------------------------------------------
// Target extraction
// ---------------------------------------------------------------------------

await test("extractWriteTarget reads write and edit input.path", () => {
  assert.equal(
    guard.extractWriteTarget({ toolName: "write", input: { path: "a.txt" } }),
    "a.txt",
  );
  assert.equal(
    guard.extractWriteTarget({ toolName: "edit", input: { path: "/tmp/a.txt" } }),
    "/tmp/a.txt",
  );
});

await test("extractWriteTarget ignores other tools and empty paths", () => {
  assert.equal(
    guard.extractWriteTarget({ toolName: "bash", input: { command: "true" } }),
    null,
  );
  assert.equal(
    guard.extractWriteTarget({ toolName: "write", input: { path: "" } }),
    null,
  );
  assert.equal(guard.extractWriteTarget(null), null);
});

// ---------------------------------------------------------------------------
// Containment
// ---------------------------------------------------------------------------

const base = mkdtempSync(path.join(tmpdir(), "catastrophe-guard-"));
const cwd = path.join(base, "cwd");
const evil = path.join(base, "cwd-evil");
const outside = path.join(base, "outside");
mkdirSync(cwd);
mkdirSync(evil);
mkdirSync(outside);
writeFileSync(path.join(cwd, "file.txt"), "x\n");
writeFileSync(path.join(evil, "file.txt"), "x\n");
symlinkSync(outside, path.join(cwd, "link"));
symlinkSync(cwd, path.join(base, "cwd-link"));

await test("exact cwd and paths inside are allowed", () => {
  assert.equal(guard.checkWriteTarget(cwd, cwd), null);
  assert.equal(guard.checkWriteTarget(cwd, "file.txt"), null);
  assert.equal(guard.checkWriteTarget(cwd, "a/b/c.txt"), null);
});

await test("a sibling with a shared prefix is not inside", () => {
  const decision = guard.checkWriteTarget(cwd, path.join(evil, "file.txt"));
  assert.ok(decision, "expected cwd-evil to be rejected");
  assert.equal(decision.block, true);
  assert.equal(decision.terminate, true);
});

await test("`..` escaping the tree is rejected", () => {
  const decision = guard.checkWriteTarget(cwd, "../outside/new.txt");
  assert.ok(decision, "expected ../outside to be rejected");
  assert.equal(decision.terminate, true);
});

await test("nonexistent nested paths inside the tree are allowed", () => {
  assert.equal(guard.checkWriteTarget(cwd, "deep/er/still/missing.txt"), null);
});

await test("a symlink out of the tree is resolved and rejected", () => {
  const decision = guard.checkWriteTarget(cwd, "link/escaped.txt");
  assert.ok(decision, "expected symlinked escape to be rejected");
  assert.equal(decision.terminate, true);
});

await test("a symlinked cwd still admits its real contents", () => {
  assert.equal(
    guard.checkWriteTarget(path.join(base, "cwd-link"), "file.txt"),
    null,
  );
});

await test("isWithin uses exact or separator containment", () => {
  assert.equal(guard.isWithin("/a/b", "/a/b"), true);
  assert.equal(guard.isWithin("/a/b", "/a/b/c"), true);
  assert.equal(guard.isWithin("/a/b", "/a/b-extra"), false);
  assert.equal(guard.isWithin("/a/b", "/a"), false);
});

await test("canonicalizePath appends missing components", () => {
  const canonical = guard.canonicalizePath("missing/deep.txt", cwd);
  // macOS exposes /var through /private/var; compare canonicalized paths.
  assert.equal(
    canonical,
    path.join(realpathSync(cwd), "missing", "deep.txt"),
  );
});

// ---------------------------------------------------------------------------
// Bash classification
// ---------------------------------------------------------------------------

const denyCases = [
  "sudo ls",
  "sudo rm -rf /",
  "rm -rf /",
  "rm -rf /*",
  "rm -rf /Users/me",
  "rm -r /Users",
  "rm -rf /Volumes/Backup",
  "rm -rf ~/Documents",
  "rm -rf /dev/disk2",
  "find / -delete",
  "find /Users/me -name '*.log' -delete",
  "find /Volumes/Backup -delete",
  "mkfs.ext4 /dev/disk2",
  "dd if=/dev/zero of=/dev/disk2 bs=1m",
  "dd of=/dev/rdisk0",
  "diskutil eraseDisk JHFS+ Empty /dev/disk2",
  "diskutil partitionDisk /dev/disk2 1 GPT",
  "chmod -R 777 /",
  "chown -R me /Users/me",
];

const promptCases = [
  "rm -rf node_modules",
  "rm -r build",
  "rm -fr ./dist",
  "rm --recursive ./dist",
  "git reset --hard HEAD~1",
  "git clean -fd",
  "git clean -xdf",
  "git push --force origin main",
  "git push -f",
  "git push origin main --force-with-lease",
];


for (const command of denyCases) {
  await test(`deny: ${command}`, () => {
    const result = guard.classifyBash(command);
    assert.equal(result.verdict, "deny", `expected deny, got ${result.verdict}`);
    assert.ok(result.reason, "expected a reason");
  });
}

for (const command of promptCases) {
  await test(`prompt: ${command}`, () => {
    const result = guard.classifyBash(command);
    assert.equal(result.verdict, "prompt", `expected prompt, got ${result.verdict}`);
    assert.ok(result.reason, "expected a reason");
  });
}

const genuinelyAllowed = [
  "rm file.txt",
  "rm -f build.log",
  "npm test",
  "npm install",
  "ls -la",
  "git status",
  "git push origin main",
  "git commit -m 'x'",
  "git reset HEAD~1",
  "git stash",
  "echo sudo is just text",
  "grep -rn sudo src",
  "mkdir -p a/b",
  "python3 script.py",
  "node scripts/check.sh",
  "find . -name '*.js'",
  "cat file.txt",
  "chmod 644 file.txt",
  "npm run build && npm test",
];

for (const command of genuinelyAllowed) {
  await test(`allow: ${command}`, () => {
    const result = guard.classifyBash(command);
    assert.equal(result.verdict, "allow", `expected allow, got ${result.verdict}`);
  });
}

await test("quoted mentions of destructive commands are allowed", () => {
  const quoted = [
    'grep -rn "mkfs.ext4" docs/',
    'echo "dd if=/dev/zero of=/dev/disk2"',
    'echo "diskutil eraseDisk JHFS+ Empty /dev/disk2"',
    'echo "rm -rf /"',
    'git commit -m "git reset --hard"',
    'git log --grep="git clean -fd"',
  ];
  for (const command of quoted) {
    const result = guard.classifyBash(command);
    assert.equal(
      result.verdict,
      "allow",
      `expected allow for ${command}, got ${result.verdict}`,
    );
  }
});

await test("rm -rf on $HOME and ${HOME} is denied", () => {
  assert.equal(guard.classifyBash("rm -rf $HOME").verdict, "deny");
  assert.equal(guard.classifyBash("rm -rf ${HOME}").verdict, "deny");
});

await test("backslash-newline does not hide a protected rm", () => {
  assert.equal(guard.classifyBash("rm -rf \\\n/").verdict, "deny");
});

await test("an env-assignment prefix does not hide a protected rm", () => {
  assert.equal(guard.classifyBash("env FOO=bar rm -rf /").verdict, "deny");
});

await test("deny wins over prompt for protected recursive rm", () => {
  assert.equal(guard.classifyBash("rm -rf /Users/me/proj").verdict, "deny");
});

await test("empty and whitespace commands are allowed", () => {
  assert.equal(guard.classifyBash("").verdict, "allow");
  assert.equal(guard.classifyBash("   ").verdict, "allow");
});

// ---------------------------------------------------------------------------
// Handler behavior: UI confirm, decline, non-UI
// ---------------------------------------------------------------------------

function bashEvent(command) {
  return { toolName: "bash", toolCallId: "t1", input: { command } };
}

await test("non-UI blocks a confirmation operation without terminating", async () => {
  const result = await guard.handleToolCall(bashEvent("git reset --hard"), {
    cwd,
    hasUI: false,
  });
  assert.ok(result, "expected a block");
  assert.equal(result.block, true);
  assert.notEqual(result.terminate, true);
});

await test("UI confirm accepts a confirmation operation", async () => {
  let calls = 0;
  const result = await guard.handleToolCall(bashEvent("git clean -fd"), {
    cwd,
    hasUI: true,
    ui: {
      confirm: async () => {
        calls += 1;
        return true;
      },
      notify: () => {},
    },
  });
  assert.equal(result, undefined);
  assert.equal(calls, 1);
});

await test("UI decline blocks without forcing termination", async () => {
  const result = await guard.handleToolCall(bashEvent("git clean -fd"), {
    cwd,
    hasUI: true,
    ui: { confirm: async () => false, notify: () => {} },
  });
  assert.ok(result, "expected a block");
  assert.equal(result.block, true);
  assert.notEqual(result.terminate, true);
});

await test("hard deny terminates and never prompts", async () => {
  let calls = 0;
  const result = await guard.handleToolCall(bashEvent("sudo rm -rf /"), {
    cwd,
    hasUI: true,
    ui: {
      confirm: async () => {
        calls += 1;
        return true;
      },
      notify: () => {},
    },
  });
  assert.ok(result, "expected a block");
  assert.equal(result.terminate, true);
  assert.equal(calls, 0);
});

await test("allowed bash returns undefined", async () => {
  const result = await guard.handleToolCall(bashEvent("npm test"), { cwd });
  assert.equal(result, undefined);
});

await test("write inside cwd is allowed, outside terminates", async () => {
  const inside = await guard.handleToolCall(
    { toolName: "write", input: { path: "file.txt" } },
    { cwd, hasUI: false },
  );
  assert.equal(inside, undefined);

  const outsideResult = await guard.handleToolCall(
    { toolName: "edit", input: { path: path.join(evil, "file.txt") } },
    { cwd, hasUI: false },
  );
  assert.ok(outsideResult, "expected a block");
  assert.equal(outsideResult.terminate, true);
});

await test("default export registers a tool_call handler", () => {
  const handlers = [];
  guard.default({ on: (name, handler) => handlers.push([name, handler]) });
  assert.equal(handlers.length, 1);
  assert.equal(handlers[0][0], "tool_call");
  assert.equal(typeof handlers[0][1], "function");
});

rmSync(base, { recursive: true, force: true });

for (const { name, error } of failures) {
  process.stderr.write(`FAIL ${name}\n`);
  process.stderr.write(`     ${error.message}\n`);
}
process.stdout.write(
  `catastrophe-guard: ${passed} passed, ${failures.length} failed\n`,
);
process.exitCode = failures.length === 0 ? 0 : 1;
