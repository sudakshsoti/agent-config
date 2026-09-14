---
name: homelab-deploy
description: "Deploy the homelab's Docker and Caddy stack and its self-hosted n8n workflows using guarded procedures for remote access, synchronisation, restarts, rclone, torbox and n8n."
disable-model-invocation: true
---

# Homelab Deploy

The deploy ritual for the homelab. Server `/opt/stacks/` is the source of truth for the
running stack; the repo `stacks/` directory is a point-in-time **mirror** captured by
`make sync-stacks`. This skill turns deploy from a memory test into steps, and handles
the three footguns explicitly: the rclone-torbox recreate, the n8n sqlite3 dance, and
committing the verified change.

## Pick the mode first

| The change is… | Mode |
| --- | --- |
| a generic stack edit (compose, Caddy, env, watchdog) | [Mode A](#mode-a-stack-change) |
| an rclone-torbox / FUSE config change | [Mode A](#mode-a-stack-change) → the safe recreate |
| an n8n workflow edit or new workflow | [Mode B](#mode-b-n8n-workflow-deploy) |

State the mode out loud before you run anything. Both modes share the pre-flight,
commit and verification rules below; read those once and apply them to whichever
mode you picked.

## Pre-flight (both modes)

**`git pull` first** — homelab convention; never start on a stale tree.

**On-box vs remote.** If the session is **on the box** (hostname `homelab`, cwd like
`/opt/homelab`) you ARE the host — run every command locally, never `ssh` into it.
If **remote from the Mac**, the Mac must be **Tailscale-connected** (public SSH is
closed — UFW allows port 22 only on `tailscale0`). SSH is key auth via the 1Password
agent: `ssh root@homelab` (MagicDNS) or `ssh root@100.113.191.93`. A Touch-ID prompt
may pop. Server IP + creds live in the homelab repo `CLAUDE.md` / `.claude/rules/`.

**`restart` is not `up -d`.** An env-var change needs a **recreate**
(`docker compose up -d <svc>`); a `restart` does NOT pick up env changes.

## Mode A: stack change

### Pick the mechanism by change type

**Do NOT reflexively `docker compose up -d` for everything.** Match the change:

- Generic stack edit (compose, Caddy, env, watchdog) → `cd /opt/stacks && docker compose up -d`
- **rclone-torbox / FUSE config** → **STOP — follow [rclone-torbox: the only safe recreate](#rclone-torbox-the-only-safe-recreate)** below (watchdog teardown). NEVER a bare `docker compose up -d rclone-torbox`.
- **n8n workflow** → **STOP — switch to [Mode B](#mode-b-n8n-workflow-deploy)**. NEVER `n8n import:workflow` / `update:workflow` / the API.
- Env-var change on a container → `docker compose up -d <svc>` — a **recreate**, not `restart`.
- New subdomain → DNS A record → server, add to `/opt/stacks/Caddyfile`, then `docker exec stacks-caddy-1 caddy reload --config /etc/caddy/Caddyfile`.
- Caddy Dockerfile change → `cd /opt/stacks && docker compose build caddy && docker compose up -d caddy`.

### The two landmines (say them out loud before deploying)

- **`docker compose up -d rclone-torbox` wedges the rshared FUSE peer** → crash-loop
  `fusermount3: ... Socket not connected`. The only safe recreate is the watchdog
  teardown (stop → `docker rm -f` → `fusermount -uz` → poll `/proc/mounts` → up).
  Procedure is inlined below.
- **n8n `import:workflow` / `update:workflow` / API PUT silently clobber the DB** via the
  in-memory cache. The only reliable path is the stopped-n8n sqlite3 dance — see
  [Mode B](#mode-b-n8n-workflow-deploy).

### rclone-torbox: the only safe recreate

The torbox-watchdog (`/opt/stacks/torbox-watchdog.sh`, cron `* * * * *`) normally handles
this: 30s timeout test on `/mnt/torbox/__all__`, 3-strike debounce, scoped to the
`rclone-torbox` container. Deploy by hand only when the watchdog isn't keeping up.

**Recovery is stop → `docker rm -f` → unmount-while-down → verify-gone → up. NOT `restart`.**
A plain `docker compose restart` brings the new container up while the dead container's
mount namespace still holds a propagated peer of the FUSE mount, so the new rclone mounts
onto a still-wedged path and crash-loops with `fusermount3: failed to access mountpoint:
Socket not connected`. **`docker rm -f` is required** — a bare `stop` leaves that namespace
(and its FUSE peer) alive, so the host unmount can't stick.

```bash
cd /opt/stacks/torbox
docker compose stop rclone-torbox
docker rm -f rclone-torbox          # destroy the namespace so the FUSE peer releases
fusermount -uz /mnt/torbox; umount -l /mnt/torbox 2>/dev/null
# verify against /proc/mounts — `mountpoint -q` lies after a lazy unmount (host view
# detaches immediately while the kernel endpoint is still wedged)
for i in $(seq 10); do grep -q /mnt/torbox /proc/mounts || break; fusermount -uz /mnt/torbox; sleep 1; done
grep -q /mnt/torbox /proc/mounts && echo "STILL WEDGED — investigate before up"
docker compose up -d rclone-torbox
```

Then force a fresh listing so newly-grabbed folders reappear:

```bash
docker exec rclone-torbox wget -qO- --post-data='recursive=false' http://localhost:5573/vfs/refresh
```

Anything beyond this recreate — the import reconciler, 30-day TorBox retention and
prune-regrab, decypharr stalls, broken `/mnt/library` symlinks, health checks — is in the
archived `skills/_archive/torbox-ops/SKILL.md`, deleted from this repo but recoverable
from Git history:

```bash
git -C ~/dev/agent-config show fafe8c11^:skills/_archive/torbox-ops/SKILL.md
```

Do NOT try to invoke `torbox-ops` as a skill; it no longer loads.

## Mode B: n8n workflow deploy

Self-hosted n8n at `n8n.sudaksh.com`. SQLite DB in the `stacks_n8n-data` volume.
Workflow JSONs are version-controlled at `n8n-workflows/` in the homelab repo.

### The one rule

**NEVER use `n8n import:workflow` or `n8n update:workflow`, and NEVER PUT the
`nodes`/`connections` via the public API to edit an existing workflow.** All three
silently clobber the DB via n8n's in-memory cache. `update:workflow` even warns
"Changes will not take effect if n8n is running" — but even done correctly,
"Publishing workflow … with current version" republishes from a version-history
snapshot that overwrites your fresh import.

**The official n8n docs (and Context7) will steer you to `import:workflow` and the REST
`PUT /workflows/{id}` — those are right for multi-main/queue deployments and WRONG for this
single-main SQLite box.** "It's the documented command" is not a reason to use it here.

The only reliable path is a **direct sqlite3 UPDATE while n8n is stopped**.

### Decision: which path?

- **One-off single-field tweak** (rename a node, flip a value) → use the **n8n UI**.
  UI saves go through the normal path and don't fight the cache.
- **Editing an existing workflow from a JSON** (the usual case) → **UPDATE path** below.
- **Deploying a brand-new workflow** → **INSERT path** below (UPDATE path + `shared_workflow` row).

`scripts/deploy-n8n-workflow.sh <workflow-file>` in the homelab repo automates the
full UPDATE dance — prefer it over hand-running the steps. Reach for the manual
steps when debugging or when the script doesn't cover the case (e.g. INSERT).

### UPDATE path (edit existing workflow)

DB on host: `/mnt/HC_Volume_105268540/docker/volumes/stacks_n8n-data/_data/database.sqlite`

1. **Stop n8n** so the cache can't overwrite you:

   ```bash
   cd /opt/stacks && docker compose stop n8n
   ```

2. **UPDATE both tables.** Triggers register from `activeVersionId → workflow_history`,
   so updating only `workflow_entity` leaves a stale active version that re-clobbers
   on start. Set `nodes`, `connections`, `updatedAt` on **both** `workflow_entity`
   AND `workflow_history`. **Leave `active` alone** here (toggle it separately, below).
   Use `python3` + `sqlite3` (host `/tmp` is not mounted into the container, so edit
   the host DB file directly).
3. **Start n8n:**

   ```bash
   cd /opt/stacks && docker compose start n8n
   ```

4. **Verify** by re-reading `workflow_entity.nodes` after start — confirm your change
   survived the cache.

Full annotated procedure lives in the homelab repo: `.claude/rules/architecture.md`
("n8n" section).

### INSERT path (new workflow)

Do the UPDATE-path INSERT into `workflow_entity`, **plus**:

- Insert a row into `shared_workflow (workflowId, projectId, role)` with
  `projectId='1Ki3qX8BssdekLUq'`, `role='workflow:owner'`. Without it the n8n API
  returns 404 even though the `workflow_entity` row exists.
- Set `active=1` **via sqlite** — `active` is read-only on the API PUT, and
  `POST /{id}/activate` returns 404 on n8n 2.16.x.

### n8n gotchas (bake these into every workflow)

- **Cron strings are IST.** The container runs `GENERIC_TIMEZONE=Asia/Kolkata`.
  Schedule cron expressions in IST, not UTC.
- **`executeOnce: true`** on aggregation/notification (fan-in) nodes. Omitting it
  once caused a 900-duplicate fan-out.
- **Transfer files with `docker cp`**, not a bind mount — host `/tmp` is not mounted.
- **Code-node built-ins are allowlisted** via `NODE_FUNCTION_ALLOW_BUILTIN` on the
  n8n container (currently `fs,tls`). Adding another built-in requires editing
  `/opt/stacks/docker-compose.yml` then `docker compose up -d n8n` — a **recreate**
  (`up -d`), not a `restart`.
- **Notifications** from workflows POST to docker-internal `http://ntfy:80/<topic>`
  (topics `soti-homelab-ops` / `soti-homelab-arrs`), basic auth `n8n:<password>`
  (credentials in the homelab repo `.claude/rules/api-keys.md`).
  ntfy Title must be ASCII-only; bodies are plain UTF-8 (no markdown — Android shows
  raw asterisks). Use colon-separated labels for emphasis.

### n8n verification

1. Re-read `workflow_entity.nodes` to confirm the change persisted.
2. If it has a schedule, sanity-check the next-run time accounts for IST.
3. Run the changed node in isolation before declaring done (check timezone shifts,
   empty arrays, parallel-branch timing).

## Capture drift back into git

After any **live server edit**, run from the repo on the Mac:

```bash
make sync-stacks
```

It rsyncs `/opt/stacks/` → repo `stacks/` (excludes `.env`, runtime state, backups).
`git diff` is then your review surface. Skip this only if the edit was made in the repo
and pushed out, never edited live.

## Commit the verified change

Once the deploy is verified live and `make sync-stacks` has captured the drift, **commit
it** — one commit per completed step, not one batched commit at the end.

**Never commit directly to `main`** — branch first, then commit there. **Push or open a
PR only when the user explicitly asks**; commits accumulate locally until then.

(This repo used to require leaving the tree dirty and never committing until asked. That
override was dropped 2026-07-23 in favour of the global always-commit habit.)

## Verify before declaring done

A deploy is not "done" until it's confirmed live (evidence, not assertion):

```bash
cd /opt/stacks && docker compose ps          # target container Up + healthy
docker compose logs --tail=30 <svc>          # no crash-loop
```

For a web service, hit the endpoint (from the Mac/client, not the Hetzner IP — Cloudflare
Bot-Fight 403s the datacenter IP for proxied vhosts). If something regressed, treat it as
an incident: roll back or fix forward before moving on, and `/remember` non-trivial fixes
into `~/dev/claude-memory`. The old triage runbook (symptom → subsystem walkthroughs) is
the archived, deleted `skills/_archive/homelab-triage/SKILL.md`, recoverable with:

```bash
git -C ~/dev/agent-config show fafe8c11^:skills/_archive/homelab-triage/SKILL.md
```

## Research-first

Decypharr, TorBox, n8n, rclone move fast. Before building a workaround for unexpected
behaviour, search GitHub issues / changelogs first.
