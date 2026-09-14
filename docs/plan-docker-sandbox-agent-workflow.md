# Plan: low-friction sandboxed Pi and OMP workflow

Date: 2026-09-13
Status: Final plan after self-review and cross-lineage adversarial review

## Recommendation

Adopt Docker Sandboxes for Pi, OMP, development commands, and agent-controlled browser automation, but do not immediately hide it behind a large custom process manager.

Pilot two workflows first:

1. **Shared direct lane:** one persistent `agent-dev` sandbox mounts `~/dev` read-write. It preserves `cd repo && pi|omp`, including trusted Git worktrees, but can inspect or destroy every repository under `~/dev`.
2. **Dedicated clone lane:** one sandbox gets a private clone of one repository. It cannot modify host source directly, but requires explicit import/export for uncommitted work.

The shared lane is the provisional recommendation because adherence is the priority, but it becomes the default only if the security contract tests pass and a two-session comparison confirms clone mode is too disruptive.

After the pilot, add thin fail-closed wrappers so daily use remains:

```bash
cd ~/dev/my-project
pi
# or
omp
```

Keep `pi-host` and `omp-host` as explicit escape hatches. Never fall back to them automatically.

## Security objective

A Pi/OMP mistake must not erase or modify the host outside explicitly mounted development paths.

Required controls:

- tested backup and restore before mounting `~/dev`;
- no host `$HOME`, `/Users`, `/Volumes`, device nodes, Docker socket, personal browser profile, or complete auth directory mounted;
- SSH-agent forwarding explicitly disabled and verified, because Docker Sandboxes enables it by default when `SSH_AUTH_SOCK` is present;
- no host-side stdio MCP servers or MCP gateway processes reachable from sandboxed agents;
- no repository-defined sandbox environment/lifecycle file allowed to run host commands;
- Pi and OMP catastrophe policies active inside the VM to protect writable repositories;
- credentials sandbox-scoped and destination-bound wherever possible;
- no silent host execution on any error;
- managed bootstrap content copied from a host-controlled installed bundle outside `~/dev`, not executed from a writable repository.

## Accepted limits

- The shared sandbox can inspect or destroy all of `~/dev`.
- Pre-existing hard links can cross the apparent workspace boundary. A host audit must reject any `~/dev` inode whose link count exceeds the number of links found under `~/dev`; a separate filesystem/volume is the stronger future fix.
- Any plaintext secret required by sandboxed application code is readable by the agent and same-user sandbox processes while active.
- Unrestricted outbound networking permits source and accessible-secret exfiltration.
- Sandbox processes may be able to write the host clipboard. Disable this if supported; otherwise never paste unreviewed sandbox-authored clipboard content into a host shell.
- Source, hooks, package scripts, or build files modified through a direct mount can later execute with host permissions if the user runs them on the host.
- A compromised persistent shared sandbox can alter global packages, caches, background processes, and the writable `agent-config` source checkout. It cannot alter the installed bootstrap bundle outside `~/dev`, but source changes still require review before the host bundle is refreshed.
- Deleting a sandbox destroys VM-only sessions, caches, credentials, and files.
- Docker Sandboxes and custom-secret/kit interfaces are early access and may change.

## System shape

```text
macOS host
├── tested Time Machine/other backup
├── host policy + audit log
├── installed bootstrap bundle outside ~/dev
├── ~/dev ─────────────────────────────────┐
├── normal Chrome                          │ optional shared RW mount
├── 1Password desktop/CLI                  │
├── sbx host credential proxy              │
├── pi-host / omp-host                     │
└── thin pi/omp/ompgo/ompcodex shims        │
       │                                    ▼
       ├── agent-dev (trusted/direct)
       │   ├── Pi + OMP + catastrophe guards
       │   ├── development servers
       │   └── isolated Playwright Chromium
       │
       └── agent-<repo>-<hash> (clone)
           ├── one private repository clone
           ├── sanitized agent configuration
           └── project-scoped network/credentials
```

## Daily workflow

### Trusted direct work

```bash
cd ~/dev/my-project
pi
omp
ompgo
ompcodex
```

The shim canonicalizes the current path, verifies it is under an explicitly approved root, starts or reattaches with native `sbx` commands, maps the current subdirectory, and executes the requested binary with the original argument array and terminal attached.

### Unfamiliar or sensitive work

```bash
agent-run --clone pi
```

Clone mode is mandatory for unfamiliar repositories and preferred whenever host write-through is unnecessary. Worktree state that is not present in the repository must be imported explicitly; changes must be exported/fetched explicitly.

### Host helpers

```bash
agent-shell
agent-status
agent-port 3000
agent-port --remove 3000
agent-stop
agent-reset          # typed sandbox-name confirmation
pi-host
omp-host
```

Direct binary paths, `command pi`, `command omp`, and scripts with hard-coded paths remain possible bypasses. Document and audit them; shell shims are an adherence mechanism, not a security boundary.

## Host policy

Keep the first version host-only and small:

- a list of canonical roots approved for the shared direct lane;
- all other repositories use clone mode or are refused;
- no repository-controlled marker in the MVP;
- every approval, port mapping, credential binding/revocation, reset, and attempted host fallback is appended to a host audit log outside `~/dev`.

Policy and log writes use host locking plus atomic replace. Lane decisions cannot change while a command is active; a change applies on the next launch.

Do not build a six-state custom lifecycle manager initially. Let `sbx` own create/start/stop/attach concurrency. Add custom locks or state only if the contract spike demonstrates a real race that `sbx` does not handle.

## Web development

Human testing uses normal host Chrome. The server runs inside the VM and binds to `0.0.0.0`; a separate host terminal publishes it with `agent-port`.

The contract spike must prove the published host socket is loopback-only (`127.0.0.1`). If `sbx` cannot guarantee this, use a loopback-only forwarder/firewall rule or refuse publication by default.

No repository file may publish a port automatically. `agent-status` lists mappings and associated sandbox processes. Test HMR/WebSockets, frontend plus API ports, OAuth callbacks, collisions, removal, and a VM/proxy failure during a running server.

Agent-driven browser work uses Playwright Chromium inside the VM. A sandbox-specific agent configuration disables host computer/browser relay integrations. Pi's Playwright installation must use its working hoisted CLI and `--browser=chromium`. Store screenshots/traces in one documented gitignored artifact directory and provide cleanup.

Never expose the personal Chrome profile or 1Password browser extension.

## Credentials and 1Password

Use these paths in order:

1. **Proxy-managed destination-bound secret.** Resolve on the host, including through `op read`; expose only an `sbx` placeholder inside the VM; substitute only on approved hosts.
2. **Narrow plaintext development secret.** If the application itself needs the value, inject only non-production fields into one process. Accept that the agent can inspect them.
3. **Read-only 1Password service account.** Use only in a dedicated sandbox and limit it to one project vault. Assume the agent can read and exfiltrate every accessible item.

Rules:

- always use sandbox scope; `sbx secret set` is global by default, so an unscoped command is rejected by the helper;
- never put a real secret in argv, shell history, temporary files, the repository, image, or persistent global sandbox environment;
- disable tracing around host `op read` pipelines;
- keep only references/approvals in managed dotfiles; live values stay in the host keychain/runtime state;
- test redirects and logs so destination binding cannot leak a substituted value;
- never use broad `sbx reset` as credential revocation because it removes all stored secrets and sandbox state;
- provide targeted `agent-secrets list` and `agent-secrets revoke` operations;
- never mount/sign into the personal 1Password vault or copy complete Pi/OMP auth stores.

Model authentication is a gate, not a later enhancement. Current Pi/OMP use OpenAI Codex OAuth and OpenCode Go credentials; the contributed Pi kit's Anthropic support does not prove these flows work. If Codex OAuth cannot be brokered, prefer a separately limited API credential. Sandbox-local subscription OAuth requires explicit user acceptance and must not be silently selected.

SSH-agent forwarding stays disabled. If later enabled for a dedicated sandbox, document that any process there can request SSH authentication or signatures even though private keys are not copied.

## MCP boundary

Before either agent runs, inventory every configured MCP server and classify it:

- **in-VM stdio:** permitted after its executable/configuration is installed in the VM;
- **remote HTTP:** permitted only with explicit destination and credential policy;
- **host stdio/gateway:** disabled for sandboxed Pi/OMP because it executes outside the VM with host privileges and bypasses the filesystem boundary;
- **unknown:** disabled.

Copy only sanitized definitions. Recreate MCP credentials through the same sandbox-scoped credential process. A gate test must prove a sandboxed agent cannot invoke a host-side stdio MCP server or reach host files through MCP.

## Implementation plan

### Phase 0 — Recovery

1. Configure Time Machine or equivalent versioned backup for `~/dev`.
2. Restore an untracked fixture and a disposable deleted repository.
3. Inventory unpushed branches, stashes, ignored databases, `.env` files, and local-only state.
4. Push valuable branches and move irreplaceable non-source data to backed-up storage.

Gate: both restore drills pass and remaining unrecoverable state is listed.

### Phase 1 — Disposable Docker Sandboxes contract spike

Pin and record the tested `sbx` CLI/daemon pair. Use a disposable fixture—not `~/dev`—to verify:

- create/start/stop/run/exec/remove and concurrent attach behavior;
- guest workspace path, per-command cwd, persistence, and deletion semantics;
- TTY, resize, SIGINT/SIGTERM/SIGTSTP, EOF, piped/closed stdin, and mid-command VM/proxy failure;
- orphan process behavior after failed `exec`;
- port add/remove, loopback binding, HMR, WebSockets, callbacks, and collisions;
- secret scoping, redirects, logs, rotation, revocation, and recreation requirements;
- host/LAN/metadata reachability and available network controls;
- SSH forwarding disabled in host configuration, daemon restarted, no `SSH_AUTH_SOCK` in the VM, and failed signature request;
- hard-link boundary behavior plus a host audit for external links;
- UID/modes, executable bits, symlinks, file locks, watchers, case-only renames, xattrs where relevant, and arm64 dependencies;
- clipboard behavior and whether it can be disabled;
- repository-provided environment/lifecycle plans disabled or unable to run host commands.

Gate: containment results and exact commands are recorded. Any unexplained external hard link, host MCP execution, SSH forwarding, non-loopback port, or host lifecycle-command path blocks mounting `~/dev`.

Before an `sbx` upgrade, rerun this suite. If the daemon updates independently of the CLI, treat the pair as unverified and keep wrappers fail-closed until the suite passes.

### Phase 2 — Authentication and MCP spike

Build a Pi/OMP compatibility matrix:

| Item | Record |
| --- | --- |
| Provider and endpoint | exact hosts |
| Mechanism | API key or OAuth |
| Proxy support | yes/no, verified |
| VM-visible material | placeholder/token/file |
| Renewal | expiry and refresh behavior |
| Revocation | exact targeted command |
| Unattended behavior | fail-closed result |

Run one minimal real request from both Pi and OMP for every required provider without mounting complete host auth stores.

Inventory Pi and OMP MCP configuration. Disable host stdio/gateway routes and prove one in-VM stdio and one approved remote HTTP route behave as expected, if needed.

Gate: both agents authenticate and no tool path escapes through MCP.

### Phase 3 — Install trusted bootstrap and catastrophe guards

Ownership:

- **dotfiles:** `sbx` installation/version gate, host shims/helpers, shared-root allowlist, audit log location, port policy, SSH-forwarding-off setting, and encrypted 1Password references;
- **agent-config:** sandbox Pi/OMP overlay, catastrophe policies, sanitized configuration manifest, and idempotent bootstrap source;
- **neither:** auth, sessions, caches, databases, live `sbx` credentials, and generated runtime state;
- **application repository:** no sandbox policy in the MVP.

If ownership-table entries change, update both owner repositories.

Package reviewed bootstrap content into a host-controlled installed location outside `~/dev`. Record its version and digest. Sandbox creation copies that immutable installed snapshot; it never executes bootstrap from a writable checkout. Refresh requires an explicit host operation after source review.

Bootstrap includes:

- pinned Node 24, Pi, OMP, Git, ripgrep, build tools, and Playwright Chromium;
- Pi global `tool_call` catastrophe guard;
- OMP `bash.patterns` and `tools.approval.eval: deny` from the guardrails report;
- sandbox overlay disabling host computer/browser relay integrations;
- sanitized Pi/OMP settings, skills, prompts, themes, and in-VM MCP definitions;
- atomic bootstrap completion marker with version/digest.

Gate: a recreated sandbox reaches the same verified state from the installed bundle.

### Phase 4 — Compare clone and shared pilots

Run the same representative task for two working sessions in each lane:

- edit and test a Node project;
- inspect Git diff/status;
- start a development server and use host Chrome;
- run one Playwright screenshot test;
- stop/restart and continue;
- export/recover work;
- exercise one worktree in the shared lane.

Decision:

- choose clone mode by default if commit/import/export friction is acceptable;
- choose shared direct mode if clone friction is likely to reduce adherence and all Phase 1 gates pass;
- do not choose shared mode merely because it was the initial idea.

### Phase 5 — Add thin default shims

Implement one launcher used by `pi`, `omp`, `ompgo`, and `ompcodex`.

MVP responsibilities only:

1. canonicalize and separator-check cwd against the host shared-root allowlist;
2. select shared or explicit clone lane;
3. call native `sbx` create/run/exec operations without unsafe shell interpolation;
4. preserve arguments, cwd, exit status, TTY, signals, and stdin mode;
5. preserve OMP overlay arguments;
6. append the host audit event;
7. fail clearly with no host fallback.

Do not add a custom state machine, repository marker parser, or custom kit yet.

Unit-test with a fake `sbx` binary:

- argv with spaces, quotes, metacharacters, Unicode, and newlines;
- nested/symlinked cwd, path-prefix confusion (`~/developer`), case differences, worktrees, and submodules;
- TTY/non-TTY, signals, EOF, piped and closed stdin;
- `omp -p` with closed stdin;
- `ompgo`/`ompcodex` overlay preservation;
- every failure path and zero host fallback.

Use Python subprocess timeouts on macOS, not GNU `timeout`. Keep destructive/port/persistence checks in a separate disposable real-`sbx` smoke suite.

Rollback:

1. disable only the shims;
2. restore all aliases/overlay commands;
3. refresh shell command hashing;
4. verify `type -a pi omp ompgo ompcodex` and host auth;
5. retain or explicitly remove sandbox state.

### Phase 6 — Add sensitive-project credentials only when needed

1. Create a dedicated clone sandbox.
2. Apply narrow egress rules where supported; otherwise label it filesystem/process isolation, not exfiltration protection.
3. Register only sandbox-scoped destination-bound secrets.
4. For plaintext application secrets, inject only into the target process and document visibility.
5. For a service account, create immutable least-privilege project-vault access and record expiry/revocation.
6. Test locked 1Password, unavailable biometrics, expiry, offline host, redirect, and revocation behavior.

Gate: project A cannot use project B's credential binding or vault, and revocation does not destroy unrelated state.

### Phase 7 — Optional hardening after one week

Add only when evidence justifies it:

- a pinned custom image/kit if bootstrap or browser setup is materially slow;
- narrow egress rules for stable projects;
- periodic clean rebuild/export checklist;
- host warnings for unpushed commits, stashes, and untracked files before reset;
- a richer host registry only if more than a direct allowlist and explicit clone flag are actually needed;
- a separate APFS development volume to remove cross-boundary hard-link risk.

## State migration

| State | Treatment |
| --- | --- |
| Tracked Pi/OMP settings, skills, prompts, themes | Sanitized bootstrap snapshot |
| Pi/OMP auth | Recreate through verified proxy/limited local flow; never copy directories wholesale |
| Pi sessions/packages | Start fresh or export reviewed non-secret state |
| OMP sessions/database | Start fresh unless a reviewed export exists |
| MCP definitions | In-VM/remote-only sanitized copy; host stdio disabled |
| MCP credentials | Re-provision as sandbox-scoped secrets |
| Pi web-search settings | Preferences only; credentials separate |
| Git name/email | Explicit VM config |
| Git credentials/signing/SSH | Destination-bound HTTPS preferred; SSH forwarding off |
| Shell environment | Small allowlist, no wholesale import |
| Browser state | Fresh isolated Chromium profile |
| Caches/dependencies | Rebuild; persistent but disposable |
| Live `sbx` secrets | Host keychain/runtime only, untracked |

## Reset safety

`agent-reset` shows the exact sandbox, lane, mounted host paths, processes, ports, credential bindings, bootstrap version, and VM-only state that will disappear. It requires typing the sandbox name.

It removes only the named sandbox. It must not call broad `sbx reset`. Targeted credential revocation is a separate explicit step. First test deletion against a disposable mounted fixture; never imply sandbox removal restores or deletes mounted host files.

## Exit criteria

The system becomes default only when:

- backup and restore drills pass;
- the pinned CLI/daemon contract suite passes;
- SSH forwarding, host MCP execution, host lifecycle commands, and non-loopback publication are absent;
- hard-link audit reports no external link target;
- both Pi and OMP authentication work without complete host auth mounts;
- catastrophe policies are active inside the VM;
- the clone/shared pilot records which lane actually preserves adherence;
- all launch variants route through thin shims with no silent fallback;
- host Chrome and isolated Chromium both work;
- a clean sandbox is reproducible from the installed bootstrap bundle;
- wrapper rollback and targeted credential revocation are exercised.

## Review disposition

Adopted from the adversarial review:

- explicitly disable Docker Sandboxes' default SSH-agent forwarding;
- add hard-link boundary testing/auditing;
- forbid host-side MCP execution;
- reject repository-controlled host lifecycle plans;
- make all credentials explicitly sandbox-scoped;
- add policy/audit concurrency, update-drift, mid-command failure, clipboard, and targeted-revocation handling;
- simplify the launcher and compare clone mode against the shared lane before choosing the default;
- protect bootstrap integrity with an installed host snapshot outside `~/dev`.

Not adopted:

- **Clone mode immediately as the unconditional default:** the user's stated adherence concern and worktree-heavy workflow make that premature; the side-by-side pilot now makes it earn or lose the default based on observed friction.
- **No host policy at all:** a minimal host direct-root allowlist is retained because native `sbx` lifecycle does not decide which repositories are trusted for a broad direct mount.

## References

- Docker Sandboxes: <https://docs.docker.com/ai/sandboxes/>
- Workspace isolation: <https://docs.docker.com/ai/sandboxes/security/isolation/#workspace-isolation>
- Credential management: <https://docs.docker.com/ai/sandboxes/configuration/credentials/>
- Kits and schema status: <https://docs.docker.com/ai/sandboxes/customize/kits/>
- 1Password CLI secrets: <https://developer.1password.com/docs/cli/secrets-scripts>
- 1Password service accounts: <https://developer.1password.com/docs/service-accounts/get-started>
- Local catastrophe analysis: [`guardrails-pi-omp-catastrophic-actions.md`](guardrails-pi-omp-catastrophic-actions.md)
