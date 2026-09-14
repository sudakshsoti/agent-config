# Minimum low-friction guardrails for Pi and OMP

Date: 2026-09-13

Scope: prevent accidental destruction of the host, home directory, mounted volumes, or valuable Git state without prompting on routine reads, edits, tests, and builds.

## Recommendation

Use three layers:

1. **Recovery:** configure a real backup. Guardrails can fail.
2. **Near-zero-friction accident guard:** enforce a small catastrophe deny-list and prevent direct file writes outside the working tree.
3. **OS containment for unattended or untrusted work:** run the agent with only the working tree writable.

Do not use instructions in `AGENTS.md` as the safety boundary. They guide the model but do not enforce anything.

## Current machine/config audit

- `omp/config.yml` sets `tools.approvalMode: yolo` and `bashInterceptor.enabled: false`.
- `pi/settings.json` has no approval or sandbox facility; Pi does not provide one as a setting.
- `tmutil destinationinfo` reports `No destinations configured`, and `tmutil listlocalsnapshots /` lists no snapshots.
- Pi is 0.85.1; OMP is 18.1.19; the host is macOS.

The missing backup is the most consequential gap. A deny-list is not a substitute for recoverability.

## Pi

### What Pi actually provides

Pi runs tools with the permissions of the user who launched it. It has no built-in sandbox or approval system. Project trust only controls whether project-local settings, packages, skills, and extensions load; it does not restrict subsequent tool calls.

Enforcement must therefore come from either:

- a global `tool_call` extension, or
- an operating-system/container/VM boundary.

Sources: installed Pi `docs/security.md` ("Project Trust", "No Built-in Sandbox"), `docs/extensions.md` (`tool_call` can block), and `docs/containerization.md`.

### Minimum practical Pi extension

Install a global extension under `~/.pi/agent/extensions/` that:

- blocks `write` and `edit` targets outside the canonical current working tree (resolve `..` and symlinks before comparison);
- hard-blocks commands targeting `/`, the home directory, `/Users`, `/Volumes`, or raw devices with recursive deletion, recursive ownership/mode changes, formatting, wiping, or mass deletion;
- asks only for destructive operations inside the working tree, such as generic recursive `rm`, `git reset --hard`, `git clean`, and force-push;
- blocks by default when there is no UI (`pi -p`, JSON mode);
- returns `{ block: true, terminate: true }` for hard-denied calls so the agent does not simply retry a spelling variant.

Pi ships `examples/extensions/permission-gate.ts` and `protected-paths.ts` as starting points. The former demonstrates confirmation before dangerous Bash commands; the latter demonstrates blocking file writes. A production version should canonicalize paths rather than use substring matching.

`bash` tool calls and direct `write`/`edit` calls must both be covered. Gating only `rm -rf` still permits the agent to damage files directly through the file tools.

## OMP

### Verified approval behavior

OMP 18.1.19 exposes:

- `tools.approvalMode: always-ask | write | yolo`
- `tools.approval.<tool>: allow | prompt | deny`
- ordered `bash.patterns` entries with `{ match, approval }`; matching is whole-command glob matching and only `*` is special
- extension/hook interception

The mode semantics, from `omp config get tools.approvalMode` and the installed binary, are:

- `always-ask`: reads run automatically; write and execution tools prompt.
- `write`: reads **and file edits/writes** run automatically; execution tools such as Bash/eval/browser/task prompt.
- `yolo`: all tiers run automatically, except explicit per-tool or Bash-pattern `prompt`/`deny` rules.

Therefore `write` mode is safer but prompts for every test/build command. It does not constrain file writes to the workspace. It is not the best default for someone who explicitly wants low friction.

The binary contains a built-in list of critical Bash command shapes, but under `yolo` a critical result without an explicit policy resolves to allow. Do not assume `yolo` retains those prompts.

### Minimum low-friction OMP policy

Keep routine tools automatic, but add explicit policies that survive `yolo`:

```yaml
tools:
  approvalMode: yolo
  approval:
    eval: deny

bash:
  patterns:
    # Hard host/volume/device boundaries. Put deny rules first: rules are ordered.
    - { match: "sudo *", approval: deny }
    - { match: "rm *-r* /", approval: deny }
    - { match: "rm *-r* /Users/*", approval: deny }
    - { match: "rm *-r* /Volumes/*", approval: deny }
    - { match: "rm *-r* ~*", approval: deny }
    - { match: "find / *-delete*", approval: deny }
    - { match: "find /Users/* -delete*", approval: deny }
    - { match: "find /Volumes/* -delete*", approval: deny }
    - { match: "mkfs*", approval: deny }
    - { match: "dd *of=/dev/*", approval: deny }
    - { match: "diskutil erase*", approval: deny }
    - { match: "diskutil partition*", approval: deny }
    - { match: "chmod *-R* /*", approval: deny }
    - { match: "chown *-R* /*", approval: deny }

    # Prompt only for destructive workspace/Git operations.
    - { match: "rm *-r*", approval: prompt }
    - { match: "git reset --hard*", approval: prompt }
    - { match: "git clean *", approval: prompt }
    - { match: "git push *--force*", approval: prompt }
```

This is intentionally short and broad. `rm` with no recursive option remains automatic; routine tests/builds remain automatic; recursive removal and destructive Git operations are the main prompts.

`tools.approval.eval: deny` closes OMP's documented route in which the eval tool can spawn a shell and bypass `bash.patterns`. It does **not** stop Bash from running a generated script whose destructive contents are not visible in the Bash tool's command string.

`bashInterceptor.enabled` may reduce unnecessary shell usage by redirecting `cat`, `grep`, in-place `sed`, and output redirection to dedicated tools. It is an ergonomics feature, not a security boundary, so enabling it is optional.

Sources: installed `omp --help`; `omp config get tools.approval --json`; `omp config get tools.approvalMode --json`; `omp config get bash.patterns --json`; and installed binary implementation of Bash policy resolution and critical patterns.

## What deny-lists cannot guarantee

String matching can be bypassed accidentally or deliberately through:

- a generated script followed by `bash script.sh`;
- Python, Node, Perl, Ruby, or another interpreter deleting files;
- aliases, variables, command substitution, unusual quoting, or an unlisted utility;
- a custom extension or MCP tool that writes files without using the standard Bash/write/edit tools.

For that reason, a hook is a strong accident guard, not a security sandbox.

## Hard boundary without routine prompts

For unattended sessions, unfamiliar repositories, or a categorical guarantee that the host/home cannot be erased, run the entire Pi or OMP process inside an OS/container/VM boundary with:

- only the current repository writable;
- host home, `/Users`, `/Volumes`, and device nodes unavailable or read-only;
- credentials mounted read-only or brokered;
- no host Docker socket;
- no passwordless privilege escalation.

Pi documents Docker, Docker Sandboxes, OpenShell, and Gondolin in installed `docs/containerization.md`. The same whole-process containment principle applies to OMP. A writable repository can still be deleted inside the sandbox, so keep it in Git and back it up.

## Minimum required, in order

1. **Configure Time Machine or another tested backup now.** This machine currently has no Time Machine destination or local snapshots.
2. **Add one global catastrophe guard to each harness.** Pi needs a `tool_call` extension; OMP can use `bash.patterns` plus `tools.approval.eval: deny`.
3. **Use whole-process containment for unattended/untrusted work.** This is the only robust way to make host deletion impossible without approving every command.

Changing OMP from `yolo` to `write` is a valid simpler alternative if prompting for every Bash/eval call is acceptable. `always-ask` is unnecessary for this goal and would be substantially more intrusive.
