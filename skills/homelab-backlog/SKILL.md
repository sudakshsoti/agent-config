---
name: homelab-backlog
description: |
  File a homelab / finance backlog item the right way — GitHub issue + Project #2 fields
  + Linear mirror, without dropping a field. Use this skill whenever capturing new work:
  "track this", "open an issue for…", "add to the backlog", "file this as a TODO",
  "make a ticket", "we should do X later", "add this to the project", or when writing /
  linking an implementation plan under plans/. Also use to move an item's Stage or apply
  the `planned` label. Triggers on backlog, issue, ticket, Project #2, Linear, area:/type:
  labels, Priority/Stage/Effort/Risk, or `planned`. RIGID taxonomy — GitHub is the source
  of truth, Linear is a mirror; every item needs the full label + field set.
---

# Homelab Backlog

Backlog lives in **GitHub Project #2 — "Homelab + Finance Backlog"**
(<https://github.com/users/sudakshsoti/projects/2>) plus the **`sudakshsoti/homelab`**
repo Issues. There is no `TODO.md` (retired). **GitHub is the source of truth; Linear
(team Sudaksh/SUD, Homelab project) is a parallel mirror.** Use the `gh` CLI (installed).

## New item — the full ritual (don't drop a field)

1. **Open the issue** on `sudakshsoti/homelab` with a clear title + body (what / why /
   acceptance). `gh issue create -R sudakshsoti/homelab -t "…" -b "…" -l area:…,type:…`
2. **Labels — both axes are required:**
   - `area:*` — the subsystem (e.g. `area:media`, `area:n8n`, `area:networking`,
     `area:security`, `area:finance`, `area:hermes`). Check existing labels first:
     `gh label list -R sudakshsoti/homelab`.
   - `type:*` — the kind of work (e.g. `type:bug`, `type:feature`, `type:chore`,
     `type:docs`).
3. **Add to Project #2** and set ALL four fields (commands below):
   - **Priority** — `P1`–`P4`
   - **Stage** — `Inbox → Next → Doing → Blocked → Done` (new items usually `Inbox`)
   - **Effort** — `15 min` / `1 hour` / `Half day` / `Weekend`
   - **Risk** — `Low` / `Medium` / `High` (blast radius if it goes wrong)
4. **Mirror to Linear** (team Sudaksh/SUD, Homelab project) — parallel copy, GitHub stays
   authoritative. Carry the same `area:`/`type:` taxonomy and the needs-plan↔`planned`
   convention.

## Setting Project #2 fields via `gh` (the fiddly part)

Project node id `PVT_kwHOALeJyM4BbSxl`. Add the issue to the board, then set each
single-select field by **option id** (not name):
```bash
# 1. add the issue — prints the item id (PVTI_…)
gh project item-add 2 --owner sudakshsoti --url <issue-url>

# 2. set a field — repeat for Priority / Stage / Effort / Risk
gh project item-edit --project-id PVT_kwHOALeJyM4BbSxl --id <item-id> \
  --field-id <field-id> --single-select-option-id <option-id>
```
Field/option ids are stable; re-fetch with `gh project field-list 2 --owner sudakshsoti --format json`.
Every field-id below shares the prefix `PVTSSF_lAHOALeJyM4BbSxlzhWEQ` (suffix shown):

| Field | field-id suffix | options (name → option-id) |
|---|---|---|
| Priority | `p8` | P1 `85bb5703` · P2 `46b96fb0` · P3 `3d17073b` · P4 `fd734b23` |
| Stage | `qA` | Inbox `25bfe0c3` · Next `a50264d2` · Doing `6a0ac291` · Blocked `00296d09` · Done `7ca4f776` |
| Effort | `qE` | 15 min `7cdd5f4e` · 1 hour `76e338e2` · Half day `cb9df4a6` · Weekend `f9702213` |
| Risk | `q8` | Low `a065482b` · Medium `818fcbee` · High `00810014` |

## `planned` is a label, NOT a Stage

`planned` means **"Claude has written an implementation plan for this issue"** — it's
orthogonal to Stage/Priority (an item can be Inbox-and-unplanned, P1-and-planned, any
combination). Apply `planned` whenever you write or link a `plans/` doc.

## Implementation plans

Detailed specs live in the homelab repo at **`plans/YYYY-MM-DD-<topic>.md`** (e.g.
`plans/2026-06-26-finance-db-resilience.md`). When you write one:
1. Create `plans/YYYY-MM-DD-<topic>.md`.
2. Link it from the issue (comment or body).
3. Apply the `planned` label to the issue (and the Linear mirror).

## Quick reference

| Action | How |
|---|---|
| List existing labels | `gh label list -R sudakshsoti/homelab` |
| Create issue w/ labels | `gh issue create -R sudakshsoti/homelab -t … -b … -l area:x,type:y` |
| View the project board | <https://github.com/users/sudakshsoti/projects/2> |
| Move an item's Stage | edit the Project #2 Stage field (mirror in Linear) |
| Mark plan written | add `planned` label + link the `plans/` doc |

## Don't

- Don't create a `TODO.md` or scatter TODOs in code comments — they're invisible to the
  backlog. Capture every "we should…" as a Project #2 issue.
- Don't open an issue without **both** `area:` and `type:` labels.
- Don't set `planned` as a Stage — it's a label.
- Don't treat Linear as authoritative — sync direction is GitHub → Linear.
