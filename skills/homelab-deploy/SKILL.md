---
name: homelab-deploy
description: |
  Deploy a change to the homelab box (Hetzner / Docker / /opt/stacks) correctly and
  safely. Use this skill whenever shipping a change to the server — editing
  docker-compose, the Caddyfile, a watchdog script, decypharr config, or any
  /opt/stacks file, restarting the stack, adding a subdomain, or "pushing this to the
  box / server / homelab". Triggers on "deploy to the box", "ship this to the server",
  "apply on /opt/stacks", "restart the stack", "sync-stacks", "make deploy",
  "add a subdomain", or editing any file under stacks/ in the repo. RIGID — the order
  matters and two mechanisms (bare `up -d rclone-torbox`, n8n import) silently break
  things; follow the steps exactly.
---

# Homelab Deploy

The deploy ritual for the homelab. Server `/opt/stacks/` is the source of truth for the
running stack; the repo `stacks/` directory is a point-in-time **mirror** captured by
`make sync-stacks`. This skill is the checklist that turns deploy from a memory test
into steps — and routes the two footgun cases to specialized skills.

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

| Change type                                        | Mechanism                                                                                                                            |
| -------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| Generic stack edit (compose, Caddy, env, watchdog) | `cd /opt/stacks && docker compose up -d`                                                                                             |
| **rclone-torbox / FUSE config**                    | **STOP — use the `torbox-ops` skill** (watchdog teardown under flock). NEVER a bare `docker compose up -d rclone-torbox`.            |
| **n8n workflow**                                   | **STOP — use the `n8n-deploy` skill** or `make deploy WORKFLOW=…`. NEVER `n8n import:workflow` / `update:workflow` / the API.        |
| Env-var change on a container                      | `docker compose up -d <svc>` — a **recreate**, not `restart` (restart does NOT pick up env changes).                                 |
| New subdomain                                      | DNS A record → server, add to `/opt/stacks/Caddyfile`, then `docker exec stacks-caddy-1 caddy reload --config /etc/caddy/Caddyfile`. |
| Caddy Dockerfile change                            | `cd /opt/stacks && docker compose build caddy && docker compose up -d caddy`.                                                        |

### The two landmines (say them out loud before deploying)

- **`docker compose up -d rclone-torbox` wedges the rshared FUSE peer** → crash-loop
  `fusermount3: ... Socket not connected`. The only safe recreate is the watchdog
  teardown (stop → `docker rm -f` → `fusermount -uz` → poll `/proc/mounts` → up).
  Delegate to **torbox-ops**.
- **n8n `import:workflow` / `update:workflow` / API PUT silently clobber the DB** via the
  in-memory cache. The only reliable path is the stopped-n8n sqlite3 dance. Delegate to
  **n8n-deploy**.

## Capture drift back into git

After any **live server edit**, run from the repo on the Mac:

```bash
make sync-stacks
```

It rsyncs `/opt/stacks/` → repo `stacks/` (excludes `.env`, runtime state, backups).
`git diff` is then your review surface. Skip this only if the edit was made in the repo
and pushed out, never edited live.

## Stop. Leave the tree dirty.

**NEVER `git commit` or `git push` until the user explicitly asks** — even after a fully
verified change. Make the edits, deploy, run sync-stacks, leave the working tree dirty
for review. When the user asks to commit: push to a **new branch and open a PR into
`main`** — never commit directly to `main`.

## Verify before declaring done

A deploy is not "done" until it's confirmed live (evidence, not assertion):

```bash
cd /opt/stacks && docker compose ps          # target container Up + healthy
docker compose logs --tail=30 <svc>          # no crash-loop
```

For a web service, hit the endpoint (from the Mac/client, not the Hetzner IP — Cloudflare
Bot-Fight 403s the datacenter IP for proxied vhosts). If something regressed, treat it as
an incident → use the **homelab-triage** skill and write up non-trivial fixes in
`JOURNAL.md`.

## Research-first

Decypharr, TorBox, n8n, rclone move fast. Before building a workaround for unexpected
behaviour, search GitHub issues / changelogs first.
