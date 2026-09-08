---
name: homelab-deploy
description: "Deploy and update the homelab's Docker and Caddy stack using guarded procedures for remote access, synchronisation, restarts, rclone, and n8n."
disable-model-invocation: true
---

# Homelab Deploy

The deploy ritual for the homelab. Server `/opt/stacks/` is the source of truth for the
running stack; the repo `stacks/` directory is a point-in-time **mirror** captured by
`make sync-stacks`. This skill is the checklist that turns deploy from a memory test
into steps — and handles the two footgun cases explicitly (rclone-torbox inline below,
n8n via the `n8n-deploy` skill).

## Before anything: pull + locate yourself

1. **`git pull` first** (homelab convention — never start on a stale tree).
2. **On-box vs remote.** If the session is **on the box** (hostname `homelab`, cwd like
   `/opt/homelab`) you ARE the host — run every command locally, never `ssh` into it.
   If **remote from the Mac**, the Mac must be **Tailscale-connected** (public SSH is
   closed — UFW allows port 22 only on `tailscale0`). SSH is key auth via the 1Password
   agent: `ssh root@homelab` (MagicDNS) or `ssh root@100.113.191.93`. A Touch-ID prompt
   may pop. Server IP + creds live in the homelab repo `CLAUDE.md` / `.claude/rules/`.

## Pick the deploy mechanism by change type

**Do NOT reflexively `docker compose up -d` for everything.** Match the change:

- Generic stack edit (compose, Caddy, env, watchdog) → `cd /opt/stacks && docker compose up -d`
- **rclone-torbox / FUSE config** → **STOP — follow [rclone-torbox: the only safe recreate](#rclone-torbox-the-only-safe-recreate) below** (watchdog teardown). NEVER a bare `docker compose up -d rclone-torbox`.
- **n8n workflow** → **STOP — use the `n8n-deploy` skill** or `make deploy WORKFLOW=…`. NEVER `n8n import:workflow` / `update:workflow` / the API.
- Env-var change on a container → `docker compose up -d <svc>` — a **recreate**, not `restart` (restart does NOT pick up env changes).
- New subdomain → DNS A record → server, add to `/opt/stacks/Caddyfile`, then `docker exec stacks-caddy-1 caddy reload --config /etc/caddy/Caddyfile`.
- Caddy Dockerfile change → `cd /opt/stacks && docker compose build caddy && docker compose up -d caddy`.

### The two landmines (say them out loud before deploying)

- **`docker compose up -d rclone-torbox` wedges the rshared FUSE peer** → crash-loop
  `fusermount3: ... Socket not connected`. The only safe recreate is the watchdog
  teardown (stop → `docker rm -f` → `fusermount -uz` → poll `/proc/mounts` → up).
  Procedure is inlined below — see
  [rclone-torbox: the only safe recreate](#rclone-torbox-the-only-safe-recreate).
- **n8n `import:workflow` / `update:workflow` / API PUT silently clobber the DB** via the
  in-memory cache. The only reliable path is the stopped-n8n sqlite3 dance. Delegate to
  **n8n-deploy**.

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
prune-regrab, decypharr stalls, broken `/mnt/library` symlinks, health checks — is in
`skills/_archive/torbox-ops/SKILL.md` in the agent-config repo. **That file is archived
and no longer loads as a skill**, so read it from disk; do not try to invoke `torbox-ops`.

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
`skills/_archive/homelab-triage/SKILL.md` in the agent-config repo — **archived, no longer
loads as a skill**, so read the file rather than invoking it.

## Research-first

Decypharr, TorBox, n8n, rclone move fast. Before building a workaround for unexpected
behaviour, search GitHub issues / changelogs first.
