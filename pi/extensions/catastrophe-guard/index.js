// Catastrophe guard for Pi.
//
// Pi runs tools with the permissions of the user who launched it, so the only
// enforcement point available is a global `tool_call` extension. This one:
//
//   * refuses write/edit targets that resolve outside the canonical cwd
//     (symlinks and `..` are resolved before the comparison);
//   * hard-denies obvious host/home/device catastrophes so the agent cannot
//     retry a spelling variant after a block;
//   * asks only for destructive operations that stay inside the working tree
//     (generic recursive rm, `git reset --hard`, `git clean`, force push), and
//     blocks them outright when there is no UI to confirm through.
//
// This is an accident guard, not a security sandbox: string matching can be
// bypassed by generated scripts or unlisted interpreters. See
// docs/guardrails-pi-omp-catastrophic-actions.md.

import { existsSync, realpathSync } from "node:fs";
import { homedir } from "node:os";
import path from "node:path";

const PROTECTED_DIRS = ["/Users", "/Volumes", "/dev"];

const SHELL_SEPARATOR = /(?:&&|\|\||[;&|\n])/;
const ENV_ASSIGNMENT = /^[A-Za-z_][A-Za-z0-9_]*=/;
const COMMAND_WRAPPERS = new Set([
  "command",
  "env",
  "nice",
  "nohup",
  "time",
  "exec",
]);

function stripQuotes(token) {
  if (typeof token !== "string" || token.length < 2) return token;
  const first = token[0];
  const last = token.at(-1);
  if ((first === '"' && last === '"') || (first === "'" && last === "'")) {
    return token.slice(1, -1);
  }
  return token;
}

function tokenize(segment) {
  return segment.match(/"[^"]*"|'[^']*'|[^\s]+/g) ?? [];
}

function commandName(token) {
  return path.posix.basename(stripQuotes(token) ?? "");
}

function segments(command) {
  return (
    String(command ?? "")
      // `\<newline>` is a line continuation: the shell joins the lines, so
      // treating them as separate segments would hide the arguments that follow.
      .replace(/\\\r?\n/g, " ")
      .split(SHELL_SEPARATOR)
      .map((segment) => segment.trim())
      .filter(Boolean)
  );
}

// Locate the actual command inside a pipeline segment, skipping leading
// `FOO=bar` assignments and thin wrappers such as `command`/`env`/`nice`.
// Assignments may follow a wrapper (`env FOO=bar rm ...`), so repeat until
// neither prefix rule applies.
function resolveCommand(tokens) {
  let index = 0;
  let advanced = true;
  while (advanced && index < tokens.length) {
    advanced = false;
    while (
      index < tokens.length &&
      ENV_ASSIGNMENT.test(stripQuotes(tokens[index]))
    ) {
      index += 1;
      advanced = true;
    }
    while (
      index < tokens.length &&
      COMMAND_WRAPPERS.has(commandName(tokens[index]))
    ) {
      index += 1;
      advanced = true;
      while (
        index < tokens.length &&
        stripQuotes(tokens[index]).startsWith("-")
      ) {
        index += 1;
      }
    }
  }
  if (index >= tokens.length) return null;
  return { index, name: commandName(tokens[index]) };
}

function hasRecursiveFlag(tokens) {
  return tokens.some((token) => {
    const value = stripQuotes(token);
    if (value === "--recursive") return true;
    if (!value.startsWith("-") || value === "-" || value.startsWith("--"))
      return false;
    return /[rR]/.test(value.slice(1));
  });
}

function positionalArguments(tokens) {
  return tokens
    .filter((token) => {
      const value = stripQuotes(token);
      return !(value.startsWith("-") && value !== "-");
    })
    .map(stripQuotes);
}

// `find` path arguments are everything before the first expression term.
function findPaths(tokens) {
  const paths = [];
  for (const token of tokens) {
    const value = stripQuotes(token);
    if (value.startsWith("-") || value === "!" || value === "(") break;
    paths.push(value);
  }
  return paths;
}

// Expand `~`, ignore relative paths, and normalize lexically without touching
// the filesystem (the target may not exist yet).
export function normalizeShellPath(raw) {
  const unquoted = stripQuotes(String(raw ?? ""));
  if (!unquoted) return null;
  const home = homedir();
  let expanded = unquoted;
  if (expanded === "~" || expanded.startsWith("~/")) {
    expanded = home + expanded.slice(1);
  } else if (expanded === "$HOME" || expanded.startsWith("$HOME/")) {
    expanded = home + expanded.slice("$HOME".length);
  } else if (expanded === "${HOME}" || expanded.startsWith("${HOME}/")) {
    expanded = home + expanded.slice("${HOME}".length);
  }
  if (!path.isAbsolute(expanded)) return null;
  return path.posix.normalize(expanded);
}

export function isProtectedRoot(normalized) {
  if (!normalized) return false;
  if (normalized === "/" || normalized === "/*") return true;
  const roots = [...PROTECTED_DIRS, homedir()];
  return roots.some(
    (root) => normalized === root || normalized.startsWith(`${root}/`),
  );
}

function hardDenyReason(command) {
  for (const segment of segments(command)) {
    const tokens = tokenize(segment);
    const resolved = resolveCommand(tokens);
    if (!resolved) continue;
    const { index, name } = resolved;
    const rest = tokens.slice(index + 1);

    if (name === "sudo") return "sudo is not permitted";

    if (name === "rm" && hasRecursiveFlag(rest)) {
      const targets = positionalArguments(rest);
      if (
        targets.some((target) => isProtectedRoot(normalizeShellPath(target)))
      ) {
        return "recursive rm on a protected root ('/', /Users, /Volumes, ~, /dev)";
      }
    }

    if (name === "find") {
      const deletes = rest.some((token) => stripQuotes(token) === "-delete");
      const paths = findPaths(rest);
      if (
        deletes &&
        paths.some((target) => isProtectedRoot(normalizeShellPath(target)))
      ) {
        return "find -delete on a protected root ('/', /Users, /Volumes, ~, /dev)";
      }
    }

    if ((name === "chmod" || name === "chown") && hasRecursiveFlag(rest)) {
      const targets = positionalArguments(rest);
      if (
        targets.some((target) => isProtectedRoot(normalizeShellPath(target)))
      ) {
        return `recursive ${name} on a protected root ('/', /Users, /Volumes, ~, /dev)`;
      }
    }

    // These are matched per resolved command rather than against the raw
    // string: `grep -rn mkfs docs/` mentions the command but runs none of it.
    if (name === "mkfs" || name.startsWith("mkfs.")) {
      return "mkfs formats a filesystem";
    }

    if (
      name === "dd" &&
      rest.some((token) => /^of=\/dev\//.test(stripQuotes(token)))
    ) {
      return "dd writing to a raw device";
    }

    if (
      name === "diskutil" &&
      /^(erase|partition)/.test(stripQuotes(rest[0]) ?? "")
    ) {
      return "diskutil erase/partition";
    }
  }

  return null;
}

function confirmationReason(command) {
  for (const segment of segments(command)) {
    const tokens = tokenize(segment);
    const resolved = resolveCommand(tokens);
    if (!resolved) continue;
    const { index, name } = resolved;
    const rest = tokens.slice(index + 1);

    if (name === "rm" && hasRecursiveFlag(rest)) {
      return "recursive rm deletes a whole tree";
    }

    if (name === "git") {
      const subcommand = stripQuotes(rest[0]);
      if (
        subcommand === "reset" &&
        rest.some((token) => stripQuotes(token) === "--hard")
      ) {
        return "git reset --hard discards working-tree changes";
      }
      if (subcommand === "clean") {
        return "git clean removes untracked files";
      }
      if (
        subcommand === "push" &&
        rest.some((token) => {
          const value = stripQuotes(token);
          return value === "-f" || value.startsWith("--force");
        })
      ) {
        return "force push rewrites remote history";
      }
    }
  }

  return null;
}

// classifyBash returns "deny" for host/device catastrophes, "prompt" for
// destructive operations that stay inside the working tree, and "allow"
// everywhere else (tests, installs, routine inspection, nonrecursive rm).
export function classifyBash(command) {
  const raw = String(command ?? "");
  if (!raw.trim()) return { verdict: "allow", reason: null };

  const deny = hardDenyReason(raw);
  if (deny) return { verdict: "deny", reason: deny };

  const prompt = confirmationReason(raw);
  if (prompt) return { verdict: "prompt", reason: prompt };

  return { verdict: "allow", reason: null };
}

// Resolve a path against cwd, replacing every existing ancestor with its
// realpath and re-appending the components that do not exist yet. This makes
// `..` and symlinks collapse before containment is checked.
export function canonicalizePath(target, cwd = process.cwd()) {
  const absolute = path.resolve(cwd, target);
  const missing = [];
  let current = absolute;
  while (!existsSync(current)) {
    const parent = path.dirname(current);
    if (parent === current) break;
    missing.unshift(path.basename(current));
    current = parent;
  }
  let real;
  try {
    real = realpathSync(current);
  } catch {
    real = current;
  }
  return missing.length ? path.join(real, ...missing) : real;
}

// Exact-or-separator containment: `/a/b-extra` is not inside `/a/b`.
export function isWithin(root, target) {
  const resolvedRoot = path.resolve(root);
  const resolvedTarget = path.resolve(target);
  if (resolvedTarget === resolvedRoot) return true;
  const prefix = resolvedRoot.endsWith(path.sep)
    ? resolvedRoot
    : resolvedRoot + path.sep;
  return resolvedTarget.startsWith(prefix);
}

export function extractWriteTarget(event) {
  if (!event || (event.toolName !== "write" && event.toolName !== "edit")) {
    return null;
  }
  const value = event?.input?.path;
  return typeof value === "string" && value.length > 0 ? value : null;
}

// Returns null when the write stays inside cwd, otherwise a blocking result.
export function checkWriteTarget(cwd, target) {
  const canonicalCwd = canonicalizePath(cwd, cwd);
  const canonicalTarget = canonicalizePath(target, cwd);
  if (isWithin(canonicalCwd, canonicalTarget)) return null;
  return {
    block: true,
    reason: `Refusing to write outside the working tree: ${target} resolves to ${canonicalTarget}, outside ${canonicalCwd}`,
    terminate: true,
  };
}

export async function handleToolCall(event, ctx) {
  if (!event || !ctx) return undefined;
  const cwd = typeof ctx.cwd === "string" && ctx.cwd ? ctx.cwd : process.cwd();

  if (event.toolName === "write" || event.toolName === "edit") {
    const target = extractWriteTarget(event);
    if (!target) return undefined;
    const decision = checkWriteTarget(cwd, target);
    if (!decision) return undefined;
    ctx.ui?.notify?.(decision.reason, "warning");
    return decision;
  }

  if (event.toolName === "bash") {
    const command = event?.input?.command;
    const { verdict, reason } = classifyBash(command);

    if (verdict === "deny") {
      return {
        block: true,
        reason: `Catastrophe guard: ${reason}`,
        terminate: true,
      };
    }

    if (verdict === "prompt") {
      const detail = `Catastrophe guard: ${reason}\n\n${command}`;
      if (!ctx.hasUI) {
        return {
          block: true,
          reason: `${detail}\n\nBlocked: no UI is available to confirm.`,
        };
      }
      const approved = await ctx.ui.confirm(
        "Confirm destructive command",
        detail,
      );
      if (!approved) return { block: true, reason: "Blocked by user" };
    }
  }

  return undefined;
}

export default function catastropheGuard(pi) {
  pi.on("tool_call", handleToolCall);
}
