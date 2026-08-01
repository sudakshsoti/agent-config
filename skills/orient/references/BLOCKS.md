# orient payload contract

The model's only output is one JSON object matching this schema. `orient.py`
splices `blocks[]` into `assets/shell.html`; nothing here is prose for a human
reader mid-render — it's the contract between the model and the script, and
later the contract `orient.py validate` enforces mechanically.

Every block renders as an HTML `<details>` whose `<summary>` is the block's
`summary` field: one plain-English sentence a panicking reader can skim. A
block with no further detail fields (`prose`, `callout`) renders flat instead
of as an empty disclosure. Everything else in a block is the collapsed detail.

## Top-level envelope

```json
{
  "repo": {
    "sha": "a1b2c3d",
    "builtAt": "2026-08-02T10:15:00Z",
    "branch": "main",
    "commitCount": 142,
    "remoteUrl": "https://github.com/example-user/spool",
    "vcs": "git"
  },
  "axis": "...",
  "sources": ["README.md", "spool/cli.py"],
  "tools": { "used": ["git", "rg"], "absent": ["scc", "cloc"] },
  "blocks": [ ]
}
```

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `repo.sha` | string | yes | Full or short commit SHA the document was built from. |
| `repo.builtAt` | string | yes | ISO 8601 timestamp, used to compute the age banner. |
| `repo.branch` | string \| null | yes | Null if detached HEAD or not a git repo. |
| `repo.commitCount` | integer \| null | yes | `git rev-list --count HEAD`; null on a shallow clone or non-git dir. |
| `repo.remoteUrl` | string \| null | yes | Origin URL. Drives permalink generation when it's a GitHub/GitLab host. |
| `repo.vcs` | `"git"` \| null | yes | Null when the target isn't a git repo at all — the document says so instead of fabricating history. |
| `axis` | string | yes | The chosen decomposition axis (subsystem / user journey / data flow / lifecycle stage) plus why it was chosen. Printed in the document header. |
| `sources` | array of string | yes | Every repo-relative path cited by any `ref` anywhere in `blocks`, deduplicated. This is what a later `status` subcommand diffs against. |
| `tools.used` | array of string | yes | Tool names that ran and contributed evidence. |
| `tools.absent` | array of string | yes | Tool names that were checked for and missing. Rendered in the footer — the skill never degrades silently. |
| `blocks` | array of Block | yes | Ordered. See below. |

## `ref` — the citation shape

Used inside blocks wherever a claim needs a pointer back to the repo.

```json
{ "path": "spool/sync.py", "line": 42, "quote": "rsync over ssh, always", "note": "guarded by --dry-run in CI" }
```

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `path` | string | yes | Repo-relative, forward slashes, no leading `./`. Kept clean because the renderer turns it into a SHA-pinned permalink when `repo.remoteUrl` is GitHub/GitLab. |
| `line` | integer | no | 1-indexed. Required in practice whenever `quote` is present. |
| `quote` | string | no | Verbatim text found at `path:line`. Never paraphrased — `orient.py validate` (a later item) re-opens the file and rejects a quote that doesn't match. |
| `note` | string | no | Short gloss on why this ref is being cited here. |

## The confidence ladder — closed, enforced by the script

| Tier | Bar | Requirement on the block |
| --- | --- | --- |
| `stated` | The repo says it in words. | At least one `refs[]` entry with a non-empty `quote` (and its `line`). |
| `evidenced` | Nobody wrote it down, but ≥2 independent signals only make sense under this reading. | `signals` array, length ≥ 2. |

`confidence` on `goal` and `decision` is **exactly** `"stated"` or `"evidenced"` —
no third value, no "guess", no omission. There is no way to express a guess as
a declarative sentence in this schema; a guess belongs in a `question` block's
optional `guess` field instead. A later item makes `orient.py` reject the
payload on any other value and name the offending block's index.

---

## Block types

Every block has `"type"` (discriminator) and `"summary"` (the one-line plain
sentence). Fields below `summary` are the collapsed detail.

### `section`

A top-level unit. Carries the reader's question verbatim and nests other
blocks under a one-line answer.

| Field | Type | Required |
| --- | --- | --- |
| `type` | `"section"` | yes |
| `question` | string, verbatim reader question (e.g. `"What is all this?"`) | yes |
| `summary` | string, one-line plain-English answer to `question` | yes |
| `blocks` | array of Block | yes |

```json
{ "type": "section", "question": "What is all this?", "summary": "A CLI that copies photos off a phone dump folder onto a NAS, deduped and dated.", "blocks": [] }
```

### `prose`

A paragraph. Renders flat (no disclosure triangle) since it carries no
separate detail.

| Field | Type | Required |
| --- | --- | --- |
| `type` | `"prose"` | yes |
| `summary` | string, the paragraph text | yes |
| `refs` | array of `ref` | no — rendered as trailing chips |

```json
{ "type": "prose", "summary": "Everything downstream of scanner.py assumes macOS; there is no Linux path.", "refs": [{ "path": "spool/transcode.py", "line": 12 }] }
```

### `goal`

The purpose statement. Confidence-gated.

| Field | Type | Required |
| --- | --- | --- |
| `type` | `"goal"` | yes |
| `summary` | string, the goal sentence (`"This repo exists so that ‹who› can ‹do what› without ‹friction›"`) | yes |
| `confidence` | `"stated"` \| `"evidenced"` | yes |
| `refs` | array of `ref` | required when `confidence: "stated"` (≥1 with `quote`) |
| `signals` | array of string | required when `confidence: "evidenced"` (length ≥ 2) |

```json
{ "type": "goal", "summary": "spool exists so that photos dumped from a phone reach the NAS deduped and dated without touching Lightroom.", "confidence": "stated", "refs": [{ "path": "README.md", "line": 3, "quote": "spool exists so I never have to open Lightroom just to dedupe a phone dump." }] }
```

### `decision`

An ADR card. Confidence-gated, plus a `status` tracking whether the decision
still holds.

| Field | Type | Required |
| --- | --- | --- |
| `type` | `"decision"` | yes |
| `summary` | string, one-line gloss of the decision | yes |
| `status` | `"holding"` \| `"eroded"` \| `"reversed"` \| `"unknown"` | yes |
| `confidence` | `"stated"` \| `"evidenced"` | yes |
| `context` | string, the situation that forced a choice | yes |
| `decision` | string, the choice actually made | yes |
| `evidence` | string, narrative pointing at why (pairs with `refs`) | yes |
| `consequence` | string, what the choice costs or enables now | yes |
| `refs` | array of `ref` | required when `confidence: "stated"` (≥1 with `quote`) |
| `signals` | array of string | required when `confidence: "evidenced"` (length ≥ 2) |

```json
{
  "type": "decision",
  "summary": "Sync runs over SSH + rsync, not Synology's own cloud-sync client.",
  "status": "holding",
  "confidence": "stated",
  "context": "Synology Drive's cloud sync silently drops files over 2 GB.",
  "decision": "Shell out to rsync over an SSH keypair provisioned on the NAS.",
  "evidence": "README states the reason directly.",
  "consequence": "One more moving part (SSH key management) but no silent drops.",
  "refs": [{ "path": "README.md", "line": 9, "quote": "we use rsync over SSH because Synology's cloud sync silently drops files over 2 GB" }]
}
```

### `flow`

A staged pipeline. Rendered as columns by stage index with SVG edges, so
stages are an explicitly ordered array.

| Field | Type | Required |
| --- | --- | --- |
| `type` | `"flow"` | yes |
| `summary` | string | yes |
| `trigger` | string, what starts the pipeline | yes |
| `stages` | array of `{ index, name, detail?, warn? }`, ordered | yes |
| `output` | string, what comes out the other end | yes |

Each stage: `index` (integer, explicit position — never relies on array
order alone), `name` (string), `detail` (string, optional), `warn` (string,
optional — this is where fragility lives; rendered distinctly).

```json
{
  "type": "flow",
  "summary": "New files land in the phone dump folder and come out as dated JPEGs on the NAS.",
  "trigger": "A file appears under ~/PhoneDump.",
  "stages": [
    { "index": 0, "name": "scan", "detail": "Walks the dump folder for files newer than the last run." },
    { "index": 1, "name": "dedupe", "detail": "Hashes each file, drops anything already synced." },
    { "index": 2, "name": "transcode", "detail": "HEIC to JPEG.", "warn": "Shells out to macOS `sips`; on Linux it silently copies the raw .heic instead." },
    { "index": 3, "name": "sync", "detail": "rsync over SSH into a YYYY/MM folder on the NAS." }
  ],
  "output": "Date-bucketed JPEGs on the NAS, verified against a source hash log."
}
```

### `map`

Annotated area cards. The only place files are ever listed — always with a
one-line role, never bare.

| Field | Type | Required |
| --- | --- | --- |
| `type` | `"map"` | yes |
| `summary` | string | yes |
| `areas` | array of `{ name, blurb, files }` | yes |

Each area: `name` (string), `blurb` (string), `files` (array of
`{ path, role }`, both required, `role` is one line).

```json
{
  "type": "map",
  "summary": "Three areas: ingest, dedupe-and-transcode, delivery.",
  "areas": [
    {
      "name": "Ingest",
      "blurb": "Finds new files and reads config.",
      "files": [
        { "path": "spool/scanner.py", "role": "Walks the dump folder for unseen files." },
        { "path": "spool/config.py", "role": "Loads NAS host, key path, dump folder from ~/.spoolrc." }
      ]
    }
  ]
}
```

### `table`

Generic rows with a header row. `rows` are positional against `headers` —
no keyed objects.

| Field | Type | Required |
| --- | --- | --- |
| `type` | `"table"` | yes |
| `summary` | string | yes |
| `headers` | array of string | yes |
| `rows` | array of array of string, each row same length as `headers` | yes |

```json
{
  "type": "table",
  "summary": "Two dependencies were added after the initial commit, both dated decisions.",
  "headers": ["Date", "Package", "Why"],
  "rows": [["2025-11-02", "pillow-heif", "Native HEIC decode replaced a shelled-out sips call, then partially reverted."]]
}
```

### `flag`

A sprawl item.

| Field | Type | Required |
| --- | --- | --- |
| `type` | `"flag"` | yes |
| `summary` | string, the "so what" line | yes |
| `kind` | `"doc-drift"` \| `"unfinished"` \| `"orphan"` \| `"duplicate"` \| `"fragile"` | yes |
| `severity` | `"low"` \| `"medium"` \| `"high"` | yes |
| `refs` | array of `ref` | yes, ≥1 |
| `handoff` | string, a sibling skill name (e.g. `"maintainability-review"`) | no |

```json
{
  "type": "flag",
  "summary": "legacy_uploader.py is dead: nothing imports it and the CLI it backed was removed.",
  "kind": "orphan",
  "severity": "low",
  "refs": [{ "path": "spool/legacy_uploader.py", "note": "no incoming imports repo-wide" }],
  "handoff": "maintainability-review"
}
```

### `callout`

An inline warning, flat (no detail beyond `summary`).

| Field | Type | Required |
| --- | --- | --- |
| `type` | `"callout"` | yes |
| `summary` | string | yes |
| `tone` | `"warn"` \| `"note"` | yes |

```json
{ "type": "callout", "summary": "This document was built from a1b2c3d; anything merged after that date isn't reflected.", "tone": "warn" }
```

### `question`

An open question addressed to the reader. This is the **only** place a guess
is allowed to live.

| Field | Type | Required |
| --- | --- | --- |
| `type` | `"question"` | yes |
| `summary` | string, the question itself | yes |
| `why` | string, why it matters | yes |
| `guess` | `{ text, refs? }` | no — the weak-signal or stack-pattern hypothesis, explicitly not a `stated`/`evidenced` claim |

```json
{
  "type": "question",
  "summary": "Does the nightly sync still run from the Synology task scheduler, or did it move to a Pi?",
  "why": "install-nas-cron.sh assumes DSM's scheduler, but a stray notes file suggests it moved; nothing in the repo confirms which host runs it now.",
  "guess": { "text": "Probably moved to the Pi, given the notes file, but unconfirmed.", "refs": [{ "path": "docs/raspberry-pi-notes.md" }] }
}
```
