---
name: homelab-triage
description: |
  Diagnose a homelab problem systematically and leave a paper trail. Use this skill
  whenever something on the box is broken, slow, or behaving oddly — a service is down
  or unhealthy, the box is unreachable, disk is full, containers are OOM-restarting,
  swap/load is thrashing, a stream won't play, or you're about to debug a recurring
  issue. Triggers on "the box is down", "X is unhealthy / keeps restarting",
  "out of disk", "everything is slow", "what's wrong with the server", "why did it
  reboot", "OOM", "write an RCA", "incident", or any homelab debugging. Points symptom
  → the right rules file and scaffolds a `/remember` entry for the incident. RIGID
  first-look order; recall prior history before theorizing, `/remember` it after.
---

# Homelab Triage

Systematic incident response for the homelab. The discipline: **read history first, run a
fixed first-look sweep, map the symptom to the owning subsystem, get exact log output
before naming a root cause, then leave a paper trail.** Don't patch symptoms — find the
root cause (see systematic-debugging).

## Step 0 — read history first

Before theorizing, invoke `/recall` (or read `~/dev/claude-memory` directly — `wiki/index.md`
is the entry point) for prior occurrences — most "new" incidents have a documented cause and
fix. This is non-negotiable for _recurring_ symptoms. (`JOURNAL.md` and `RCA-*.md` were
retired 2026-07-27 — all incident/decision history now lives in this vault, not the repo.)

## Step 1 — first-look sweep (fixed order)

On the box (or over Tailscale SSH — see homelab-deploy for the on-box vs remote rule):

```bash
df -h / /mnt/HC_Volume_105268540        # root disk fills fast — known issue
docker system df                         # image/volume/log bloat
docker compose -f /opt/stacks/docker-compose.yml ps   # any container not Up/healthy?
free -m && uptime                        # swap thrash + load (gate is load >8 on 8 cores)
timeout 30 ls /mnt/torbox/__all__/ >/dev/null && echo "FUSE ok" || echo "FUSE WEDGED"
tail -40 /var/log/server-watchdog.log    # reboots, disk prunes, daemon restarts
```

Ask for the **exact error / log output** before proposing a root cause. Run the failing
thing in isolation before declaring a fix (check timezone shifts, empty arrays,
parallel-branch timing).

## Step 2 — map symptom → owning subsystem

- SSH hangs / commands hang / `Transport endpoint not connected` / mount stale → **torbox-ops skill** (FUSE recovery)
- Torrent stuck "Downloading" 0 B / folder won't import → **torbox-ops skill** (reconciler)
- Container OOM-killed / restarting → `.claude/rules/memory-management.md` (mem caps + host slices)
- n8n workflow broken / not firing → **n8n-deploy skill** + `.claude/rules/architecture.md` (n8n)
- Stream stutters / won't play remotely → `.claude/rules/networking.md` (Cloudflare proxy vs grey-cloud, BBR)
- DNS / Caddy / TLS / cert → `.claude/rules/networking.md` (Caddy + Cloudflare)
- Hermes agent / Discord / cron / MCP → `.claude/rules/architecture-hermes.md`
- Box rebooted on its own → server-watchdog (Tier 1) or Cloudflare Worker (Tier 2) — `.claude/rules/architecture.md`

## Step 3 — respect the escalation chain

Recovery is layered; don't fight an automated layer that's already acting:

```
Container down → Autoheal → FUSE stale → torbox-watchdog
→ Docker/system failure → server-watchdog reboot (≤2 / 6h)
→ OS frozen → Cloudflare Worker → Hetzner API hard reset (≤2 / 24h)
```

Check whether a watchdog is mid-recovery (`/var/log/torbox-watchdog.log`,
`server-watchdog.log`) before manually intervening — a manual `restart` during a FUSE
teardown makes the wedge worse.

## Step 4 — leave a paper trail

- **Recurring or non-trivial fix** → invoke `/remember` so the incident gets distilled and
  ingested into `~/dev/claude-memory` (what broke, root cause, fix, how verified) — this
  replaces the old `JOURNAL.md` append.
- **Significant incident with a real root-cause investigation** → still worth writing up in
  the same shape the old `RCA-*.md` files used, but hand it to `/remember` as the source
  material rather than a new repo file:

  ```markdown
  # <one-line title>, YYYY-MM-DD

  ## Symptom — what was observed, when, blast radius

  ## Timeline — UTC timestamps of detection → recovery

  ## Root cause — the actual mechanism (not the proximate symptom)

  ## Fix — what changed, with command/diff

  ## Verification — the command/output proving it's resolved

  ## Prevention — guardrail/watchdog/cap added so it can't silently recur
  ```

- If the fix changed anything under `/opt/stacks`, capture it with `make sync-stacks`
  (see homelab-deploy), then commit it on a branch. Push only when asked.

## Notes

- Notifications land in ntfy (`soti-homelab-ops`); a `high`/`urgent` ping there is often
  the first signal — check the phone.
- Debug Cloudflare-proxied endpoints from the **Mac/client**, not the Hetzner host
  (Bot-Fight Mode 403s the datacenter IP).
