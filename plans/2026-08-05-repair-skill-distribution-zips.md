# Repair Skill Distribution Zips Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Restore the GitHub Actions `check` workflow by making the committed `dist/*.zip` artefacts exactly match the active skill catalogue.

**Architecture:** Keep `skills/` as the source of truth and treat `dist/` as committed generated output for Claude.ai and API uploads. Rebuild only active skills whose source changed or whose archive is missing, remove archives for skills moved under `skills/_archive/`, then use the existing zip-integrity gate and full repository check as verification.

**Tech Stack:** Bash, Python 3, Info-ZIP `zip`, GitHub Actions

## Global Constraints

- Do not edit anything under `skills/_archive/`; those files preserve retired skill source.
- Do not hand-edit zip contents; generate them with `scripts/build-zip.sh`.
- Do not change `scripts/check-zips.py`; its failure accurately identifies source/artifact drift.
- Do not push, merge, or open a pull request without explicit instruction.

---

### [x] Task 1: Synchronise committed skill distribution artefacts

**Files:**
- Regenerate: `dist/design-foil.zip`
- Regenerate: `dist/frontend-craft.zip`
- Regenerate: `dist/html-doc.zip`
- Create: `dist/motion-craft.zip`
- Create: `dist/motion-review.zip`
- Regenerate: `dist/prototype.zip`
- Delete: `dist/animation-vocabulary.zip`
- Delete: `dist/apple-design.zip`
- Delete: `dist/emil-design-eng.zip`
- Delete: `dist/find-animation-opportunities.zip`
- Delete: `dist/improve-animations.zip`
- Delete: `dist/review-animations.zip`
- Delete: `dist/value-connect.zip`

**Interfaces:**
- Consumes: active skill directories detected by `scripts/check-zips.py` as direct children of `skills/` containing `SKILL.md`
- Produces: one matching `dist/<skill>.zip` per active skill and no zip for any skill under `skills/_archive/`

- [x] **Step 1: Reproduce the failing integrity gate**

Run:

```bash
python3 scripts/check-zips.py .
```

Expected: exit 1 with `26 active, 4 stale, 2 missing, 7 orphan`.

- [x] **Step 2: Rebuild changed and newly active skill archives**

Run:

```bash
./scripts/build-zip.sh \
  design-foil \
  frontend-craft \
  html-doc \
  motion-craft \
  motion-review \
  prototype
```

Expected: six `built: dist/<name>.zip` lines and exit 0.

- [x] **Step 3: Remove archives whose skills were retired**

Run:

```bash
git rm \
  dist/animation-vocabulary.zip \
  dist/apple-design.zip \
  dist/emil-design-eng.zip \
  dist/find-animation-opportunities.zip \
  dist/improve-animations.zip \
  dist/review-animations.zip \
  dist/value-connect.zip
```

Expected: Git stages deletion of exactly the seven orphaned archives.

- [x] **Step 4: Verify the focused integrity gate passes**

Run:

```bash
python3 scripts/check-zips.py .
```

Expected: exit 0 with `26 active, 0 stale, 0 missing, 0 orphan`.

- [x] **Step 5: Verify the complete CI-equivalent check**

Run:

```bash
./scripts/check.sh
```

Expected: exit 0 and the final `check.sh` summary reports every check passed.

- [x] **Step 6: Review and commit only the distribution repair**

Run:

```bash
git status --short
git diff --stat
git add \
  dist/design-foil.zip \
  dist/frontend-craft.zip \
  dist/html-doc.zip \
  dist/motion-craft.zip \
  dist/motion-review.zip \
  dist/prototype.zip
git commit -m "skills: sync distribution archives"
```

Expected: the commit contains six rebuilt/created archives and seven deleted orphan archives, with no source or configuration changes.

## Self-review

- The plan addresses every item emitted by the failing `check-zips.py` run.
- The focused check proves exact source/archive parity; the full check mirrors `.github/workflows/check.yml` via `scripts/check.sh`.
- No workaround weakens the CI gate, and no unrelated skill source is changed.
