# rclone-torbox: the only safe recreate

Read this when the change touches rclone-torbox or its FUSE config.

**NEVER a bare `docker compose up -d rclone-torbox`.** It wedges the rshared FUSE peer
and the container crash-loops with `fusermount3: ... Socket not connected`. The only safe
recreate is the watchdog teardown (stop → `docker rm -f` → `fusermount -uz` → poll
`/proc/mounts` → up).

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
