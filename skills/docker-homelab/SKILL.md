---
name: docker-homelab
description: |
  Ground truth for the self-hosted homelab infrastructure. Use this skill whenever
  working in the Homelab Architect project — for server specs, service inventory,
  storage layout, media workflow, network topology, and common operations.
  Always read this before forming opinions on existing infrastructure state.
---

# Docker Homelab — Infrastructure Reference

## Server

<!-- FILL IN: CPU, RAM, storage drives, OS, hostname -->

| Property | Value |
|----------|-------|
| Hostname | |
| OS | |
| CPU | |
| RAM | |
| Boot disk | |
| Data disk(s) | |

## Storage Layout

<!-- FILL IN: mount points, partition scheme, FUSE mounts, cloud storage integrations -->

| Mount | Purpose | Type |
|-------|---------|------|
| /home | | |
| /mnt/... | | |

## Service Inventory

<!-- FILL IN: every running container — service name, image, compose project, exposed port, public URL if any -->

| Service | Image | Compose project | Port | URL |
|---------|-------|-----------------|------|-----|
| | | | | |

## Network

<!-- FILL IN: reverse proxy in use (Nginx/Caddy/Traefik), domain, DNS provider, Cloudflare tunnel y/n -->

- Reverse proxy:
- Domain:
- DNS provider:
- Cloudflare tunnel:
- Internal DNS / split-horizon:

## Media Workflow

<!-- FILL IN: arr stack (Sonarr/Radarr/Prowlarr/etc.), indexer setup, Real-Debrid integration, Jellyfin config, download client -->

- Download client:
- Indexer manager:
- Real-Debrid: connected via
- Media server:
- Library paths:

## Common Operations

<!-- FILL IN: the commands you actually run for routine tasks -->

```
# Restart all services
# Pull latest images
# View logs for a service
# Backup compose + volumes
# Check disk usage
```

## VPS (if applicable)

<!-- FILL IN: provider, region, specs, what's hosted there vs local -->

| Property | Value |
|----------|-------|
| Provider | |
| Region | |
| CPU / RAM | |
| Purpose | |

## Known Issues / Quirks

<!-- FILL IN: anything non-obvious about this setup — e.g. FUSE mount needs remounting after reboot, specific service restart order -->
