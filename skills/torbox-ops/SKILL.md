---
name: torbox-ops
description: |
  Operate the TorBox / rclone / decypharr media plumbing on the homelab. Use this
  skill whenever the symlink chain misbehaves — stale FUSE mount, SSH hangs / commands
  hang, decypharr stalls, torrents stuck "Downloading" at 0 B, broken library
  symlinks, missing imports, or 30-day retention pruning. Triggers on "FUSE",
  "mount is stale", "rclone-torbox", "decypharr", "reconciler", "/mnt/torbox",
  "/mnt/library broken symlinks", "torbox-watchdog", "prune-regrab", "retention",
  or "movie/show won't import". RIGID — FUSE recovery and the retention flow have
  exact orderings; a plain `docker compose restart` makes the FUSE wedge WORSE.
---

# TorBox Ops (Homelab)

TorBox-only topology since 2026-05-15 (RD + zurg decommissioned). The chain:

```
Radarr/Sonarr → decypharr (mock qBittorrent, TorBox-only) → TorBox WebDAV
→ rclone mount /mnt/torbox/__all__/ → symlink in /mnt/library/ → Jellyfin
```

Nothing lands on disk — only symlinks. Pins: decypharr `cy01/blackhole:v2.3`
(never `:latest`), rclone `--vfs-cache-mode minimal`, decypharr `rate_limit: 55/minute`.

## On-box vs remote

If the session is **on the box** (hostname `homelab`, e.g. `/opt/homelab`), you ARE
the host — run everything locally, never `ssh`/`sshpass` into the box IP. If
**remote from the Mac**, prefix with the SSH line from the homelab `CLAUDE.md`.
(Server IP + credentials live in the homelab repo `CLAUDE.md` / `.claude/rules/`.)

## Symptom → action

- SSH connects but commands hang — Stale TorBox FUSE mount → **FUSE recovery**
- Torrent stuck "Downloading" at 0 B — Wedged mount or decypharr stall → **FUSE recovery**, then **reconciler**
- Folder on WebDAV but no library symlink — decypharr never reached `processSymlink()` → **reconciler**
- Broken symlinks in `/mnt/library` — TorBox pruned the item (30-day) → **retention**
- Movie/show won't match (foreign title) — normalisation / not in arr → **reconciler unmatched**

## FUSE recovery — order matters

The torbox-watchdog (`/opt/stacks/torbox-watchdog.sh`, cron `* * * * *`) handles this
automatically: 30s timeout test on `/mnt/torbox/__all__`, 3-strike debounce, scoped to
the `rclone-torbox` container.

**Recovery is stop → `docker rm -f` → unmount-while-down → verify-gone → up. NOT `restart`.**
A plain `docker compose restart` brings the new container up while the dead container's
mount namespace still holds a propagated peer of the FUSE mount, so the new rclone mounts
onto a still-wedged path and crash-loops with `fusermount3: failed to access mountpoint:
Socket not connected`. **`docker rm -f` is required** — a bare `stop` leaves that namespace
(and its FUSE peer) alive, so the host unmount can't stick.

Manual recovery if the watchdog isn't keeping up (mirrors `torbox-watchdog.sh`):

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

## Reconciler — closes the silent-drop gap

`/opt/stacks/torbox-import-reconciler.py` (cron `*/2 * * * *`, source:
`scripts/torbox-import-reconciler.py`) diffs WebDAV folders against existing
`/mnt/library/{movies,shows}` symlinks and ManualImports any orphan. Also runs
cleanup passes (empty-placeholder rmdir, stuck/ghost queue eviction). Run manually
between ticks:

```bash
/opt/stacks/torbox-import-reconciler.py
tail -30 /var/log/torbox-reconciler.log
```

**Unmatched folders** go to `/var/log/torbox-reconciler.unmatched.log`. These are
normally either content not in Sonarr/Radarr or language-variant dubs — they prune
naturally on TorBox's 30-day cycle. Title matching uses Unicode NFD decomposition
(`Cléo`→`cleo`) plus Radarr `originalTitle` / Sonarr `alternateTitles`; if a _known_
film with diacritics is stuck, the NFD fix may have regressed — check `normalize()`.

## 30-Day Retention

TorBox prunes items not _downloaded/streamed_ in 30 days. **Critical: WebDAV reads
are clock-neutral by design — Jellyfin streaming does NOT reset the timer.** Only a
torrent re-add or `/api/torrents/requestdl` counts. Two-stage nightly flow:

1. **Decypharr Repair sweep** (`0 4 * * *`, `auto_repair: false` — detect-only).
2. **Prune-regrab cron** (`/etc/cron.d/torbox-prune-cleanup`, `0 5 * * *`) runs
   `/opt/stacks/torbox-prune-regrab.py`: walks `/mnt/library/{movies,shows}` for
   `xtype -l` broken symlinks, resolves each to a Radarr movie / Sonarr episode,
   deletes the symlink, re-monitors, and fires `MoviesSearch` / `SeasonSearch` /
   `EpisodeSearch`. State: `/var/lib/torbox-prune-regrab/state.json` (24h cooldown,
   3-attempt cap → `high`-priority ntfy on giveup). Log `/var/log/torbox-prune-regrab.log`.

**ToS caveat:** routed through arr search (not decypharr `auto_repair: true`) so each
grab looks user-initiated on the wire. This still violates TorBox's ToS spirit on
automated re-request; 24h dedup + 3-attempt cap bounds it to "normal user" volume.
If TorBox tightens enforcement, flip the cron back to the old `find -delete` line at
`/etc/cron.d/torbox-prune-cleanup.bak`.

## Quick health checks

```bash
find /mnt/library/ -type f \( -iname '*.mkv' -o -iname '*.mp4' \) -size +50M  # should be 0
find /mnt/library/ -xtype l                                                    # broken symlinks
df -h / /mnt/HC_Volume_105268540 && docker system df
```

## Research-first

Decypharr, TorBox, and rclone move fast. Before building a workaround for unexpected
behaviour, search GitHub issues / changelogs first — and ask for exact log output
before proposing a root cause. After a non-trivial fix, write it up in `JOURNAL.md`.
