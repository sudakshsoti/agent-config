---
name: n8n-deploy
description: |
  Edit or deploy self-hosted n8n workflows without clobbering the DB — nodes,
  schedules, active state, Code nodes. RIGID: never import:workflow,
  update:workflow, or API node writes; all three silently corrupt state.
disable-model-invocation: true
---

# n8n Workflow Deploy (Homelab)

Self-hosted n8n at `n8n.sudaksh.com`. SQLite DB in the `stacks_n8n-data` volume.
Workflow JSONs are version-controlled at `n8n-workflows/` in the homelab repo.

## The One Rule

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

## Decision: which path?

- **One-off single-field tweak** (rename a node, flip a value) → use the **n8n UI**.
  UI saves go through the normal path and don't fight the cache.
- **Editing an existing workflow from a JSON** (the usual case) → **sqlite3 UPDATE path** below.
- **Deploying a brand-new workflow** → **INSERT path** below (UPDATE path + `shared_workflow` row).

`scripts/deploy-n8n-workflow.sh <workflow-file>` in the homelab repo automates the
full UPDATE dance — prefer it over hand-running the steps. Reach for the manual
steps when debugging or when the script doesn't cover the case (e.g. INSERT).

## UPDATE path (edit existing workflow)

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

## INSERT path (new workflow)

Do the UPDATE-path INSERT into `workflow_entity`, **plus**:

- Insert a row into `shared_workflow (workflowId, projectId, role)` with
  `projectId='1Ki3qX8BssdekLUq'`, `role='workflow:owner'`. Without it the n8n API
  returns 404 even though the `workflow_entity` row exists.
- Set `active=1` **via sqlite** — `active` is read-only on the API PUT, and
  `POST /{id}/activate` returns 404 on n8n 2.16.x.

## Gotchas (bake these into every workflow)

- **Cron strings are IST.** The container runs `GENERIC_TIMEZONE=Asia/Kolkata`.
  Schedule cron expressions in IST, not UTC.
- **`executeOnce: true`** on aggregation/notification (fan-in) nodes. Omitting it
  once caused a 900-duplicate fan-out.
- **Transfer files with `docker cp`**, not a bind mount — host `/tmp` is not mounted.
- **Code-node built-ins are allowlisted** via `NODE_FUNCTION_ALLOW_BUILTIN` on the
  n8n container (currently `fs,tls`). Adding another built-in requires editing
  `/opt/stacks/docker-compose.yml` then `docker compose up -d n8n` — a **recreate**
  (`up -d`), not a `restart`; a restart does NOT pick up env changes.
- **Notifications** from workflows POST to docker-internal `http://ntfy:80/<topic>`
  (topics `soti-homelab-ops` / `soti-homelab-arrs`), basic auth `n8n:<password>`
  (credentials in the homelab repo `.claude/rules/api-keys.md`).
  ntfy Title must be ASCII-only; bodies are plain UTF-8 (no markdown — Android shows
  raw asterisks). Use colon-separated labels for emphasis.

## After deploying

1. Re-read `workflow_entity.nodes` to confirm the change persisted.
2. If it has a schedule, sanity-check the next-run time accounts for IST.
3. Run the changed node in isolation before declaring done (check timezone shifts,
   empty arrays, parallel-branch timing).
4. Per homelab convention: commit + push only when the user asks, then offer a
   continuation prompt.
