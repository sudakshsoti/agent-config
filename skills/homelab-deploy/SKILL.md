---
name: homelab-deploy
description: "Deploy the homelab's Docker and Caddy stack and its self-hosted n8n workflows using guarded procedures for remote access, synchronisation, restarts, rclone, torbox and n8n."
disable-model-invocation: true
---

# Homelab Deploy

The deploy ritual for the homelab. Server `/opt/stacks/` is the source of truth for the
running stack; the repo `stacks/` directory is a point-in-time **mirror** captured by
`make sync-stacks`. This skill turns deploy from a memory test into steps. Every
repo-relative path below (`scripts/`, `make`, `.claude/rules/`, `CLAUDE.md`,
`n8n-workflows/`) is in the homelab repo.

## Pick the mode first

Write the chosen mode and the command you will run before running anything.

| The change is… | Mode |
| --- | --- |
| a generic stack edit (compose, Caddy, env, watchdog) | [Mode A](#mode-a-stack-change) |
| an rclone-torbox / FUSE config change | **STOP** — read [references/rclone-torbox.md](references/rclone-torbox.md) before touching it; NEVER a bare `docker compose up -d rclone-torbox` (it wedges the FUSE mount; the safe recreate is a watchdog-style teardown: stop → `docker rm -f` → unmount → verify → up, **NOT `restart`**) |
| an n8n workflow edit or new workflow | **STOP** — read [references/n8n.md](references/n8n.md) before touching it; NEVER `n8n import:workflow` / `update:workflow` / the API (they silently clobber the DB; the only path is a sqlite3 UPDATE with n8n stopped) |

All modes share the pre-flight, sync, commit and verification rules below.

## Pre-flight (all modes)

**`git pull` first** — homelab convention; never start on a stale tree.

**On-box vs remote.** If the session is **on the box** (hostname `homelab`, cwd like
`/opt/homelab`) you ARE the host — run every command locally, never `ssh` into it.
If **remote from the Mac**, the Mac must be **Tailscale-connected** (public SSH is
closed — UFW allows port 22 only on `tailscale0`). SSH is key auth via the 1Password
agent: `ssh root@homelab` (MagicDNS). A Touch-ID prompt may pop. Server address and
creds live in the homelab repo `CLAUDE.md` / `.claude/rules/`.

**`restart` is not `up -d`.** An env-var change needs a **recreate**
(`docker compose up -d <svc>`); a `restart` does NOT pick up env changes.

## Mode A: stack change

**Do NOT reflexively `docker compose up -d` for everything.** Match the change:

- Generic stack edit (compose, Caddy, env, watchdog) → `cd /opt/stacks && docker compose up -d`
- Env-var change on a container → `docker compose up -d <svc>` (recreate, per Pre-flight).
- New subdomain → DNS A record → server, add to `/opt/stacks/Caddyfile`, then `docker exec stacks-caddy-1 caddy reload --config /etc/caddy/Caddyfile`.
- Caddy Dockerfile change → `cd /opt/stacks && docker compose build caddy && docker compose up -d caddy`.
- rclone-torbox or n8n → not Mode A; use the table above.

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

## Verify before declaring done

A deploy is not "done" until it's confirmed live (evidence, not assertion):

```bash
cd /opt/stacks && docker compose ps          # target container Up + healthy
docker compose logs --tail=30 <svc>          # no crash-loop
```

For a web service, hit the endpoint (from the Mac/client, not the Hetzner IP — Cloudflare
Bot-Fight 403s the datacenter IP for proxied vhosts). If something regressed, treat it as
an incident: roll back or fix forward before moving on. The old triage runbook (symptom → subsystem walkthroughs) is
the archived, deleted `skills/_archive/homelab-triage/SKILL.md`, recoverable with:

```bash
git -C ~/dev/agent-config show fafe8c11^:skills/_archive/homelab-triage/SKILL.md
```
