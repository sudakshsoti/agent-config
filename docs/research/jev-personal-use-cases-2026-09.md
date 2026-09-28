# Jev / Laya for personal projects and daily life (2026-09-28)

Builds on `docs/research/jev-context-management-2026-09.md` (Jev identity, quota,
protocol probes — not repeated here) and `docs/research/jev-compaction-effectiveness-2026-09.md`
(coding-agent conclusions: rule enforcement on diffs is the best fit; compaction/pruning/
skill routing are rejected; a per-turn model router is unproven — **not re-litigated**).
All web reads and repo scans done 2026-09-28. Anything not directly observed is tagged
**[INFERENCE]**.

## TL;DR

- **In the user's own ~26 non-employer repos, essentially nothing needs Jev.** Five
  parallel read-only scouts covering finance, homelab/network, mail/RSS/notes, and 18
  misc tool repos found exactly **one plausible-but-marginal in-repo candidate** (the
  Obsidian vault's Inbox→PARA note triage) and one **already-solved-cheaper** candidate
  (finance's merchant-category fallback, which already uses a low-volume LLM call).
  Everything else is deterministic regex/threshold/state-machine code that the repos'
  own authors deliberately kept deterministic — several docs explicitly record fuzzy
  human judgment being *replaced by* a threshold, never the reverse (homelab
  `library-tripwire.py`, `RCA-2026-09-01-swap-load-thrashing.md`).
- **The strongest real opportunities are daily-life, not code-in-repos**: RSS entry
  triage (Miniflux API supports exactly the two/three-state decision Jev is built for —
  §4.2), and an unmatched-sender email classifier layered *behind* the existing
  Sieve/Gmail-filter rules rather than replacing them (§4.1) — both **not yet built**.
- **Laya (`convaiinnovations/laya`, Apache-2.0, HuggingFace) is real, verified, and the
  better default for anything touching finance, health, or personal notes**: it's a
  421M-parameter open-weight model family that speaks the *same* three primitives
  (`choice`/`score`/`noul`) and ships a `laya-serve` HTTP server that exposes the
  identical `POST /v1/systemone` wire shape as TypeSafe Jev, so existing Jev clients
  work by only changing the base URL — self-hosted, $0 per token, nothing leaves the
  machine. Source: https://huggingface.co/convaiinnovations/laya (read 2026-09-28).
- **Every proposed use below states what data would leave the machine.** For anything
  touching `finance`, `vault`, or Proton Mail content, the recommendation is Laya
  self-hosted, not cloud Jev — see the ranked table's Laya column.
- **Nothing here overturns the settled coding-agent conclusions** in the two prior
  notes; this note only extends them to personal-project and daily-life scope.

## 1. Jev and Laya: what's verified (brief; see companion note for depth)

- Jev 1.13: TypeSafe's "System One" model — `choice`/`score`/`noul` questions against
  a `state`, mixed in one call, no text output, 64K context, $0.042/M input tokens,
  free output. Access: OpenCode Zen (`https://opencode.ai/zen/v1/systemone`),
  OpenRouter (`typesafe/jev-1.13`), or TypeSafe direct. Sources:
  https://docs.typesafe.ai/introduction, https://typesafe.ai/blog/introducing-system-one-models-and-jev
  (both read 2026-09-28; the same three primitives — Choice/Score/Noul — are confirmed
  verbatim in the docs page's primitives table).
- **Laya**, verified from its HuggingFace model card (`convaiinnovations/laya`,
  license `apache-2.0`, read 2026-09-28):
  - Non-autoregressive, ModernBERT-large backbone (421M params), ~33–40ms per call on
    a T4 GPU; a `laya-multilingual` checkpoint (322M, mmBERT-base) covers 100+
    languages at 1024–8192 token context; a `laya-typed-decisions` fine-tune scores
    0.766 accuracy on a 2,000-decision benchmark (vs Jev's published 0.727).
  - **Self-hosting, Jev-compatible:** `pip install "laya[serve]"` then `laya-serve`
    exposes `POST /v1/systemone` with the same request/response shape as TypeSafe
    Jev — "existing TypeSafe clients work by changing their base URL." Binds
    `0.0.0.0` with no auth unless `LAYA_API_KEY` is set.
  - Honest limits published by the maintainer: base checkpoints are "near chance"
    zero-shot on the typed-decisions benchmark (0.362) — the competitive 0.766 number
    belongs to a checkpoint *fine-tuned* on that benchmark's own training split, so
    Laya is "a fast base to specialise, not a zero-shot decision engine" without
    fine-tuning on your own labelled decisions. `noul` questions can anchor on their
    own `true:`/`false:` labels rather than the state on the English checkpoint
    (documented bug, GitHub `NandhaKishorM/laya#156`); ships over-confident until you
    fit per-question-type temperature (mean ECE 0.466 → 0.081 after calibration);
    high-cardinality choices (>20 options) favor Jev over default-settings Laya.
  - Independent third-party comparison pages exist (`madewithjev.com`-adjacent
    ecosystem: flowtivity.ai, alphamatch.ai, a Medium "Jev vs Laya" post) but are
    **secondary and not used as evidence here** beyond confirming Laya is a widely
    discussed real project, not vaporware — the HuggingFace card and its linked
    GitHub (`NandhaKishorM/laya`) are the primary sources used for every claim above.
- **Practical consequence for this note**: any use case touching finance data,
  health data, personal notes, or private mail content should default to **local
  Laya**, not cloud Jev/OpenRouter — see the "data leaving machine" column below.

## 2. Method

- Cloned 26 of the user's non-employer, non-clinical repos shallowly to
  `/tmp/jev-scan/` via `gh repo clone --depth 1` (list: finance, finance-dashboard,
  homelab, home-network, proton-sieve-india, drop, vault, obsidian-config,
  claude-memory, repertory, astrology, niimbot-label-generator, hardcopy, md-print,
  brew-guide, pop360, baseline, agmtech, netopt-peer-groups, twin-peaks-companion,
  abstractly, kohra, miniflux-theme, dotfiles, agent-config, workbench, sudaksh-io).
  `home-network` failed to clone in this pass; it was scanned afterwards via `gh api`
  (see §3.2 and Gaps).
  `value-connect`, `optum-news-workflow`, `quality-optimization`, `clinical-reasoning`
  were never cloned or read, per the hard privacy rule.
- Fanned out 5 parallel read-only `scout` subagents grouped by cluster (finance;
  homelab/network; mail/RSS/notes; misc tools ×2), each briefed on Jev's fit
  criteria and the privacy rules (schema/structure/code only for `finance`, `vault`,
  `claude-memory`; never quote data, amounts, account numbers, note prose, or
  credentials). Findings below are their file:line citations, cross-checked by me
  against the raw scout output.
- Deleted `/tmp/jev-scan` after writing this note (see end of session).

## 3. Findings by cluster (existing repos)

### 3.1 Finance (`finance`, `finance-dashboard`)

- `tests/test_txn_kind_emi.py`, `test_merchant_spend.py`, `test_reimbursable_category.py`,
  `test_spend_pace_backtest.py`, `test_spend_pace_projection.py`: SQL-invariant
  regression tests over enum columns (`txn_kind ∈ {purchase, refund, emi_conversion,
  emi_leg}`, `schema.sql:264`) and a ~20-row `categories` lookup table — no
  classification logic to replace, everything is DB CHECK constraints. **Reject.**
- `scripts/finance_brief.py` (71.3KB): the decision layer (pace verdict, insight
  trigger priority `_insight_gate:1507`, emoji/status maps `_emoji:186`) is already
  fully deterministic and separated from the one LLM call in the file
  (`_insight_sentence:1533-1557`, OpenRouter deepseek-v4-flash, ~1×/day, with a
  verbatim-number safety guard `_insight_is_safe:1560` and a template fallback).
  **Reject** — free-text phrasing output, and volume (1/day) is exactly the
  "existing LLM call at low volume" exclusion.
- `workflows/axis-cc-v1.json`, `axis-bank-v1.json`, `icici-cc-v1.json` (n8n Gmail-alert
  ingestion): an OpenRouter deepseek-v4-flash node extracts fields from the alert
  email body into a fixed schema (`merchant, transaction_date, amount, card,
  category, type, source, needs_review, ...`, `icici-cc-v1.json:220`), then a
  SQL `ILIKE`-pattern `merchant_map` table (`schema.sql:92-97`, matched via
  `match_merchant`, `schema.sql:890-897`) assigns the category, falling back to
  `needs_review=true` for a human to fix via `agent_fix_*` functions
  (`schema.sql:215,294`). The `unattributed_spend` view's own code comment
  (`schema.sql:2620`) records that a pattern-match-based review signal was **"tried
  and dropped" as too noisy** — this is the one place a fuzzy classifier's
  documented history exists. **Verdict: marginal.** This is the closest Jev-shaped
  seam in the whole scan (fuzzy merchant text → fixed ~20-category answer set,
  existing `noul`-equivalent safety valve already in place) but it's already solved
  by a cheap LLM call at low volume (low hundreds of alerts/month), so swapping in
  Jev/Laya would be a lateral change, not a structural improvement — worth
  prototyping only if the merchant-map miss rate becomes a real pain point.
- `scripts/import_amazon_orders.py`: two hand-written compiled-regex keyword buckets,
  documented as a deliberate scope guard against an LLM pass (`:136-152`) for a
  one-off import job. **Reject** — occasional volume, deliberately conservative.
- `scripts/check-seed-pii.py` / `test_db_pull_pii_guard.py`: anchored regex over a
  closed `pg_dump --column-inserts` grammar, whose docstring documents two past
  false-positive incidents from an earlier unanchored version. **Reject,
  emphatically** — a PII leak guard is exactly where a 99%-accurate fuzzy
  classifier's silent 1% miss rate is unacceptable.
- `finance-dashboard`: pure aggregation/grouping over already-typed DB columns
  (`lib/aggregate.ts:70,255-300`). **Reject** — nothing to classify.

### 3.2 Homelab / network (`homelab`, `home-network`)

`home-network` (read afterwards via `gh api repos/sudakshsoti/home-network/...`):
documentation plus `scripts/sweep-lan.sh`, `find-switch.sh`, `verify-topology.sh` and
`lib-devices.sh`. Device identification is an exact MAC lookup against
`devices.tsv` (`scripts/sweep-lan.sh:16-22`); there is no alert, camera-event or
log-triage code. No Jev fit: the answer space is a table lookup, not fuzzy text.

Every one of the 8 n8n workflows and 6+ Python/shell scripts audited resolves to a
numeric threshold, regex, or explicit state machine with 2–8 fixed outcomes:
`arr-events-to-ntfy.json` (3-way IF chain), `homelab-stuck-reaper.json` (>30-day
threshold), `homelab-daily-digest.json`, `homelab-watched-pruner.json` (>30-day +
25-item cap), `letterboxd-to-radarr.json` (`typeof id === 'number'` check),
`homelab-cert-probe.json` (an explicit first-match-wins TLS state machine, 8
terminal states), `supabase-keepalive.json` (`status >= 400`),
`scripts/torbox-import-reconciler.py` (2,293 lines of regex/threshold heuristics
that explicitly delegate the one genuinely fuzzy step — release-name-to-show
matching — to Sonarr/Radarr's own production parser, `:816-818`),
`scripts/torbox-prune-regrab.py`, `stacks/library-tripwire.py` (a `DROP_FRACTION`
threshold whose docstring cites the `2026-06-25` incident it was built to replace —
i.e., **it replaced a manual/fuzzy check with a threshold, not the other way
round**), `scripts/platform_check.py`, `stacks/server-watchdog.sh`,
`stacks/torbox-watchdog.sh`, and `cloudflare-worker-email-rss/src/routes/inbound.ts`
(exact sender/domain allowlist, no content classification). The RCA/incident docs
(`RCA-2026-09-01-swap-load-thrashing.md`, `INCIDENT-2026-06-25-sonarr-library-wipe.md`)
confirm the same pattern in prose: incidents get remediated by adding a
deterministic check, never by adding a fuzzy human-judgment step. **Reject across
the board** — this repo's own engineering philosophy already is "replace fuzzy
judgment with a threshold," and destructive actions (reboot, delete, blocklist) make
determinism the correct choice regardless of Jev's existence.
- **One marginal exception:** `n8n-workflows/weather-to-ntfy.json` — every threshold
  and priority is decided deterministically in a Code node (`:98-123`); the *only*
  LLM call in the whole repo is a stylist (OpenRouter deepseek-v4.1-flash,
  `:154-180`) that rephrases pre-selected facts into a notification title/body,
  gated by a fact-checking validator node that falls back to a deterministic
  template on any deviation (`:181-190`). Jev could theoretically own the
  send/no-send + priority + tag decision (already a fixed small set), but the body
  text itself must stay free-form — a partial substitution only, not a new
  capability. **Reject as a structural change**, note as trivia.

### 3.3 Mail / RSS / notes (`proton-sieve-india`, `miniflux-theme`, `vault`, `obsidian-config`, `claude-memory`)

- **`proton-sieve-india`**: ~215 sender-domain wildcard patterns across 13 category
  allow-lists (finance, accounts, wallets, travel, ecommerce, courier, health,
  utilities, government, newsletters, entertainment, education, jobs) plus a
  `List-Unsubscribe`-based promo catch-all (`combined.sieve`, confirmed by direct
  read). Matching is `address :domain :matches "From"` — **exact sender-suffix
  matching, not fuzzy text** — and the README documents new-sender/domain-churn
  handling as a **manual** maintenance task ("Updating After Domain Changes",
  "Adding Your State Electricity Board"). LinkedIn is deliberately excluded as
  "too broad" (`combined.sieve:406`) — an acknowledged case Sieve can't cleanly
  handle. **Verdict: Sieve already solves the fixed-sender case cleanly — reject**
  for wholesale reclassification. The only genuine gap is unknown/new senders that
  land unlabeled in Inbox, and lookalike-phishing domains no allow-list enumerates —
  see §4.1 for why that's a real, separate, buildable use case (not a change to
  this repo).
- **`miniflux-theme`**: pure CSS + an icon-substitution `MutationObserver`
  (`theme.js`, confirmed no entry-filtering logic). **Reject — nothing to
  evaluate.**
- **`vault`** (sensitive, structure only): classic PARA taxonomy (`00 Inbox/`,
  `01 Projects/`, `02 Areas/`, `03 Resources/`, `04 Archive/`) with fixed `type` and
  `status` frontmatter enums defined in `.agents/skills/vault-maintenance/SKILL.md`.
  Inbox→PARA placement is explicitly **prose instructions for manual/agent-judgement
  placement at edit time** — no script routes or tags notes automatically;
  `build-index.py` only regenerates read-only reports. **Verdict: the one
  plausible in-repo candidate** — fixed ~4–5-bucket answer set, genuinely fuzzy
  free-prose input, done repeatedly at capture time. Whether it clears the
  volume/latency bar depends on capture rate (unmeasured **[INFERENCE]**); if
  built, it must run on local Laya, not cloud Jev, given note-content sensitivity.
- **`obsidian-config`**: settings/CSS/stock plugin binaries only, no authored
  logic. **Reject.**
- **`claude-memory`** (sensitive, structure only): a 3-layer wiki (`raw/`, `wiki/`,
  `CLAUDE.md`) with a fixed 5-tag enum (`#project #decision #person #tool
  #concept`) and 7-field frontmatter. Salience ("is this durable / does it still
  matter") is **deliberately kept inside an LLM's contextual judgment** per
  `CLAUDE.md`'s own stated rationale — the repo's mechanical linter
  (`tools/lint.py`, 485 lines) explicitly limits itself to conformance checks
  (frontmatter shape, tag-taxonomy membership, broken links, staleness) precisely
  *because* the authors already decided salience shouldn't be reduced to a
  scoring function. Retrieval has no similarity scoring — it's index-summary
  pre-filtering by design. **Reject** — the repo's design already routes the fuzzy
  judgment to where it belongs (a chat model with reasoning), and mechanical checks
  stay mechanical on purpose.

### 3.4 Misc tools (18 repos: `drop`, `repertory`, `astrology`, `niimbot-label-generator`,
`hardcopy`, `md-print`, `brew-guide`, `pop360`, `baseline`, `agmtech`,
`netopt-peer-groups`, `twin-peaks-companion`, `abstractly`, `kohra`, `dotfiles`,
`agent-config`, `workbench`, `sudaksh-io`)

No repo in this batch has the required combination (fuzzy NL input × fixed small
answer set × real volume/latency pain). Closest seams, all rejected with reasons:

- `repertory/recommend.py:83-127` `parse_genres` — hand-curated alias dict over 26
  fixed genres; regex already clean, dropdown-scale volume.
- `repertory/watchlist.py:21-23` `excludes()` — brittle exact title/year matching;
  personal-diary volume, not painful enough to justify a model call.
- `hardcopy/lib/markdown-to-html.ts` `classifyCaption` — the single genuinely
  fuzzy-prose → fixed-3-choice (`{drop, promote, stop}`) seam found anywhere in the
  misc-tools batch, hand-tuned to ~98% precision on a 44-file personal corpus
  (`handoff/2026-08-10-caption-detection-ladder.md`). Rejected: personal-scale
  corpus, correctness matters more than Jev's latency advantage over a
  multi-second PDF render.
- `pop360/src/lib/t2f-parser.ts` — 39 regex clinical-phrase detectors; closest fit
  by shape, but it's a demo app whose product *is* the free-text reasoning string
  (wrong output type for Jev) with a canned no-match fallback already built in.
- `baseline/skills/baseline/SKILL.md` design-request router — already an LLM call
  with a 50+-probe routing eval harness (`evals/run-routing.mjs`); volume is ~1 per
  design session; no latency/cost pain documented.
- `agent-config/scripts/check-model-routing.py` — pure regex/YAML config
  validation (selector shape, `disabledProviders`, overlay coverage, Pi-unreachable
  providers); machine-generated config input, never fuzzy text. Issue-label triage
  (`docs/agents/triage-labels.md`, 5 fixed labels) is real but single-digit-issue
  volume and needs free-text rationale alongside the label — an LLM call, if any,
  is already the right tool. `ownership_collisions.py`/`audit-local.py` have zero
  fuzzy-matching (`difflib`/`SequenceMatcher`) anywhere.
- `netopt-peer-groups`, `twin-peaks-companion`, `brew-guide`, `agmtech`,
  `abstractly`, `kohra`, `dotfiles`, `workbench`, `sudaksh-io`,
  `niimbot-label-generator`, `md-print`, `astrology`, `drop`: no fuzzy-text
  classification logic present at all (structured-input arithmetic, exact-match
  lookups, static content, or deterministic ephemeris calculation). `drop`'s
  planning doc describes only **manual** user-applied tagging, no automatic
  classification.

## 4. Daily-life integrations (researched from primary docs)

### 4.1 Email (Proton Mail) — buildable, not yet built

- **Sieve is server-side, static, and header-only** — confirmed above (§3.3): it
  cannot call an external API, so Jev/Laya cannot participate in Sieve rule
  evaluation itself. To triage mail with a model, you need client-side access.
- **Proton Bridge is the primary-source-verified path**: "an open-source
  application that allows you to fully integrate your Proton Mail account with
  any program that supports IMAP and SMTP" — a local desktop app that decrypts
  and exposes a **local IMAP/SMTP bridge**, available with a paid Mail plan.
  Source: https://proton.me/support/protonmail-bridge-clients-apple-mail,
  https://proton.me/mail/bridge (both read 2026-09-28). This means: a local
  script (any IMAP library) can poll the Inbox via Bridge, read subject/sender/
  body, and act (apply an IMAP label/flag) — the mechanism proton-sieve-india's
  README implicitly assumes doesn't exist when it says new senders must be added
  to Sieve by hand.
- **Buildable use case**: run a local script (cron or IMAP IDLE) against Proton
  Bridge for mail that lands in Inbox *without* a matching Sieve label (i.e.,
  Sieve's own 15 categories already sorted the other 95%+) — ask Laya (local,
  since bank/broker/health mail is exactly the sensitive category) a `choice`
  over the same ~14 category labels used in `proton-sieve-india` plus a `noul`
  ("does this look like a phishing lookalike of a known bank domain?"), then
  apply the IMAP label via Bridge if confidence clears a threshold, else leave
  unlabeled for manual review — same shape as the existing Sieve categories, but
  covering the unmatched tail Sieve's README admits it can't. **Data leaving
  machine: none**, if Laya is self-hosted alongside Bridge on the same machine.
  Cloud Jev would send sender/subject/body-excerpt to TypeSafe or OpenRouter —
  avoid for financial/health mail. **[INFERENCE]**: volume and IMAP polling
  cadence unmeasured; this is a new build, not a modification of existing code.
- No source repo behind a Jev/Laya "email triage" build was found on
  `madewithjev.com` beyond tweets with no linked GitHub (`/builds/fifty-emails-under-two-seconds`,
  `/builds/500-emails-3-cents`, `/builds/inbox-triage-1500-emails` are all
  Twitter/X posts with "Open on X" as the only link — **no traceable source
  repo**, so these are cited as directional evidence only, not as code to copy.
  Source: https://madewithjev.com/builds/fifty-emails-under-two-seconds (read
  2026-09-28).

### 4.2 RSS (Miniflux) — the cleanest daily-life fit found in this whole research pass

- Verified from the primary Miniflux API reference
  (https://miniflux.app/docs/api.html, read 2026-09-28): entries have exactly
  three states (`status ∈ {read, unread, removed}`) and a separate `starred`
  boolean; both are settable in bulk via `PUT /v1/entries` with `entry_ids` +
  `status`/`starred`, or per-entry via `PUT /v1/entries/{id}/bookmark`. `GET
  /v1/entries` supports filtering by `status`, `starred`, `category_id`, and date
  ranges. **There is no arbitrary per-entry tag field** — only feed-level
  categories exist — so any "smart filing" idea is bounded to the
  read/unread/starred answer space, which happens to be exactly Jev/Laya's shape.
- **Buildable use case**: a script pulls unread entries (`GET
  /v1/entries?status=unread`), asks Jev/Laya a `noul` ("is this worth reading
  given my interests?") or `score` (interest 0–1) per entry from title+summary,
  then bulk-applies `starred=true` to the top scorers and/or marks low-scorers
  `status=read` via `PUT /v1/entries` — replacing the daily manual skim implied
  by the user running a themed Miniflux instance (`miniflux-theme` repo exists
  specifically because they read it regularly). **Data leaving machine**: article
  titles/summaries (public RSS content, not sensitive) — cloud Jev is fine here;
  local Laya works too and is essentially free at this volume. **Verdict: best
  candidate in this whole report** — fixed 2–3-state answer space verified from
  primary docs, genuinely fuzzy input (article titles/summaries), real daily
  volume (dozens of entries), and no existing code to disrupt (it's a net-new
  script, zero migration risk). **[INFERENCE]**: not yet built; volume and
  interest-model design unverified beyond the API's supported operations.

### 4.3 Todoist — deterministic parsing already covers the common case

- Verified from Todoist's own developer docs and help center (filters use a
  query language like `"priority 1"`; Quick Add is a **deterministic** natural-
  language *syntax* parser for dates/projects/labels — `#Project`, `@label`,
  `p1`–`p4`, plus date phrases — not a fuzzy classifier). Sources:
  https://developer.todoist.com/api/v1/ (Filters), community/help documentation
  confirming Quick Add's fixed grammar (read 2026-09-28).
- **Gap Quick Add doesn't cover**: a raw freeform capture with no explicit syntax
  (e.g. a voice-to-text note) gets no project/priority/label at all — it's
  presumably triaged later by hand, consistent with the `gtd` skill present in
  `agent-config/skills/`. A `choice` (project) + `score` (priority) call from
  raw task text is a plausible fit *in principle*, but daily capture volume is
  low (a handful/day), so the savings over a cheap chat-model call are marginal
  — **[INFERENCE]**: plausible, not compelling; task text is not especially
  sensitive, so either cloud Jev or local Laya works, but the case for adopting
  either over "just ask whatever model you're already talking to" is weak at
  this volume.

### 4.4 SMS/UPI transaction categorization

- The user's actual bank/CC ingestion pipeline (finance repo, §3.1) already
  ingests via **Gmail alert emails**, not raw SMS, and already uses a low-volume
  LLM call with a documented history of trying and dropping a pattern-based
  fallback signal. There is no separate SMS pipeline in this account to modify.
  A third-party LinkedIn post (Miklos Toth, non-primary, cited for directional
  cost comparison only) reports Jev costing $0.07/1,000 decisions vs. Claude
  Haiku 4.5's $3.31 for bank-message categorization — consistent with the
  finance repo's own economics, but doesn't change the §3.1 verdict: this is
  already solved cheaply at low volume. **Reject**, same reasoning as §3.1.

### 4.5 Homelab alert triage

- Already covered exhaustively in §3.2: every alert/notification decision found
  is a numeric threshold or explicit state machine, several explicitly built to
  *replace* a manual/fuzzy step. **Reject**, no fuzzy-input decision surface
  exists to hand to a model.

## 5. Ranked table

| # | Use case | Repo / workflow | Current mechanism | Jev primitive | Data leaving machine | Laya-local viable? | Verdict |
|---|---|---|---|---|---|---|---|
| 1 | RSS entry triage (star / mark-read) | Miniflux instance (daily-life; `miniflux-theme` repo evidences active use) — **not yet built** | Manual daily skim of unread entries | `noul`/`score` per entry from title+summary, bulk `PUT /v1/entries` | Public article titles/summaries only | Yes, and cheap at this volume; cloud Jev also fine (low sensitivity) | **Prototype — best candidate found** |
| 2 | Unmatched-sender email classifier (behind Sieve) | `proton-sieve-india` + Proton Bridge — **not yet built** | Sieve exact sender-domain match (~215 patterns); unmatched senders sit unlabeled, manual fix documented in README | `choice` over ~14 existing labels + `noul` (phishing-lookalike confidence gate) | Sender/subject/body excerpt — sensitive (bank/broker/health) | **Yes, required** — self-host Laya alongside Bridge, zero egress | **Prototype, local-only** — genuine gap Sieve's own docs admit |
| 3 | Merchant-category classifier for `merchant_map` misses | `finance` n8n workflows (`axis-cc-v1.json` etc.) | SQL `ILIKE` pattern match + `needs_review` flag; pattern-based signal "tried and dropped" per `schema.sql:2620` | `choice` (~20 categories) + `noul` (`needs_review`) | Merchant/payee text — already leaves machine via existing OpenRouter call | Yes — could swap existing call to local Laya for zero-egress | **Marginal — already solved cheaply**; only worth it to cut egress, not accuracy |
| 4 | Obsidian vault Inbox → PARA note filing | `vault` | Manual/agent-judgement placement at capture time (`vault-maintenance` skill) | `choice` over ~4–5 PARA buckets + `type`/`status` tags | Full note prose — highly sensitive | **Yes, required** | **Prototype cautiously, local-only** — volume/latency pain unmeasured |
| 5 | Todoist raw-capture triage (project + priority) | Daily-life, Todoist API/MCP + `gtd` skill | Quick Add's deterministic syntax parser (no fallback for freeform captures) | `choice` (project) + `score` (priority) | Task text — low sensitivity | Yes, either works | **Plausible, not compelling** — low daily volume |
| 6 | weather-to-ntfy send/priority decision only (not the message body) | `homelab` (`weather-to-ntfy.json`) | Deterministic thresholds already own facts+priority; only the phrasing is delegated to a low-volume flash-model stylist | `choice`/`score` for the decision slot only | n/a (decision slot has no free text) | Yes | **Reject as a structural change** — the part that needs a model needs *text*, which Jev can't emit |

## 6. Rejected and why

- **`proton-sieve-india` wholesale reclassification** — ~215 sender-domain
  patterns already give exact, zero-error routing; the input signal (From-domain)
  is discrete and enumerable, not fuzzy natural language. Reject.
- **Gmail filters (`workbench/knowledge/gmail-filters.xml`)** — same shape as
  Sieve: ~40 exact-sender rules across an 11-label taxonomy (Paper Trail/Banking,
  Insurance, Receipts, Subscriptions, Tax & Investments, Medical; Travel & Stays;
  Dev; Work/UHG Digest; Newsletters; Documents), maintained by hand. Same
  reasoning as Sieve: exact match already works. Reject for the matched majority;
  its unmatched tail is the same opportunity as §4.1, applied to Gmail instead of
  Proton if ever relevant.
- **finance PII-leak guard (`check-seed-pii.py`)** — regex is exact over a closed
  grammar; a silent 1% miss rate on a data-leak guard is unacceptable. Reject.
- **finance `import_amazon_orders.py` categorization** — two conservative regex
  buckets, deliberately scoped away from an LLM pass per its own comments;
  one-off import volume. Reject.
- **All 8 homelab n8n workflows + all homelab scripts** — thresholds, regex, and
  state machines throughout; the repo's own incident docs record *replacing*
  fuzzy judgment with determinism, never the reverse; destructive actions
  (reboot, delete, blocklist) make determinism correct regardless of Jev's
  existence. Reject.
- **`repertory` genre/title matching** — hand-curated alias dicts and exact
  title+year matching at personal-diary volume; brittle but not painful enough.
  Reject.
- **`hardcopy` caption-detection ladder** — the one genuine fuzzy-prose →
  fixed-3-choice seam in the misc-tools batch, but tuned to ~98% precision on a
  44-file personal corpus where correctness matters more than latency. Reject.
- **`pop360` clinical-criteria detector** — regex-based demo app whose product
  *is* the free-text reasoning output; wrong primitive for Jev. Reject.
- **`baseline` design-request router** — already an LLM call with its own 50+
  probe eval harness, at ~1 decision/session; no volume/latency pain. Reject.
- **`agent-config` model-routing config check and issue-label triage** — the
  former is pure regex/YAML validation over machine-generated config (never
  fuzzy text); the latter is single-digit-issue volume and needs free-text
  rationale alongside any label. Reject. Note: the scouts confirmed the two
  "settled" companion research notes exist in this actual checkout even though a
  fresh clone snapshot briefly lacked them — restated here for clarity, not
  re-litigated.
- **`claude-memory` salience/retrieval** — the repo's own design deliberately
  keeps salience judgment inside an LLM's reasoning and keeps mechanical checks
  (in `tools/lint.py`) strictly to conformance, on purpose. Reject.
- **SMS/UPI transaction categorization** — no separate SMS pipeline exists in
  this account (ingestion is via Gmail alerts, already covered under finance);
  same verdict as finance §3.1/§4.4. Reject.
- **Homelab alert triage** — no fuzzy-input decision surface exists anywhere in
  the repo to hand to a model. Reject.
- **12 remaining misc-tools repos** (`niimbot-label-generator`, `md-print`,
  `brew-guide`, `agmtech`, `netopt-peer-groups`, `twin-peaks-companion`,
  `abstractly`, `kohra`, `dotfiles`, `workbench`, `sudaksh-io`, `astrology`,
  `drop`) — no classification/routing/scoring logic of any kind found; either
  static content, structured-input arithmetic, exact-match lookups, or (for
  `astrology`) deterministic ephemeris calculation with the fuzzy layer already
  living in a full chat-model persona (wrong primitive, since it needs free
  prose). Reject, nothing to migrate.

## Gaps

- **`home-network` was not scanned by the scouts** (shallow clone failed). It was
  read afterwards via `gh api` (tree + `scripts/sweep-lan.sh`): LAN sweep plus exact
  MAC→name lookup from `devices.tsv`, with no camera-event or alert logic, so no
  candidate (§3.2). Hikvision/NVR event triage would be net-new work, not an
  existing decision point.
- **Volume/frequency for every "not yet built" daily-life candidate (§4.1, §4.2,
  §5 rows 1, 2, 4) is unmeasured** — I don't have the user's actual unread-entry
  count/day, Inbox-miss rate, or vault capture rate. These are architecturally
  plausible, not benchmarked.
- **Proton Bridge requires a paid Proton Mail plan** ("Bridge is available only
  with a paid plan that includes Proton Mail," proton.me/mail/bridge) —
  whether the user's current plan includes it is unverified here.
- **Laya's zero-shot accuracy without fine-tuning is weak** (0.362 on the
  vendor's own typed-decisions benchmark, per its model card) — any of the
  local-Laya recommendations above (vault, unmatched-sender mail) would likely
  need either the `laya-typed-decisions` fine-tune approach or a small labelled
  set from the user's own data before the accuracy is trustworthy for anything
  that auto-files without human review. Not tested here.
- **No probe of either Jev's or Laya's actual `/v1/systemone` endpoint was
  performed** in this pass (consistent with the companion note: the paid Jev
  endpoint has never been successfully called from this machine). All latency/
  accuracy figures above are vendor- or community-published, not locally
  reproduced.
- **No traceable source repo exists behind any madewithjev.com email-classifier
  or transaction-categorization build** — every relevant entry links only to an
  X/Twitter post, not GitHub, so none could be cited as implementation
  reference (see §4.1).
- **`ai-file-sorter` (the tool in `workbench/cowork/downloads-desktop-sorter-plan.md`,
  https://github.com/hyperfield/ai-file-sorter)** is a real, closely analogous
  "deterministic-first, model-for-the-ambiguous-leftovers" pattern the user has
  already researched for Downloads/Desktop sorting — but it expects an
  OpenAI-compatible `/chat/completions` endpoint, not the SystemOne `/v1/systemone`
  protocol, so Jev/Laya are not a drop-in there without forking the tool to add
  protocol support. Noted as directional validation of the pattern, not a ranked
  candidate, since it isn't the user's own code and wasn't in scope to modify.

## Sources

- https://docs.typesafe.ai/introduction — Jev primitives (Choice/Score/Noul),
  atomic-question guidance (read 2026-09-28).
- https://typesafe.ai/blog/introducing-system-one-models-and-jev — vendor
  announcement, architecture, pricing, use-case table (read 2026-09-28).
- https://huggingface.co/convaiinnovations/laya — Laya model card: license,
  architecture, `laya-serve` Jev-compatible HTTP server, benchmarks vs Jev,
  honest limits section (read 2026-09-28).
- https://miniflux.app/docs/api.html — Entry `status`/`starred` fields, `GET
  /v1/entries` filters, `PUT /v1/entries` bulk update, `PUT
  /v1/entries/{id}/bookmark` (read 2026-09-28).
- https://proton.me/mail/bridge, https://proton.me/support/protonmail-bridge-clients-apple-mail
  — Proton Bridge local IMAP/SMTP access, paid-plan requirement (read
  2026-09-28).
- https://developer.todoist.com/api/v1/ — Filters query syntax; Quick Add
  deterministic parsing confirmed via Todoist help center and third-party
  client docs (read 2026-09-28).
- https://madewithjev.com/jev-use-cases, https://madewithjev.com/jev-multi-agent,
  https://madewithjev.com/jev-with/claude-code — community catalogue, used for
  leads only; every relevant email/transaction-classifier entry traced back to a
  bare X/Twitter post with no source repo (read 2026-09-28).
- https://madewithjev.com/builds/fifty-emails-under-two-seconds — cited as the
  representative example of the untraceable-source-repo problem in §4.1.
- Miklos Toth, LinkedIn post on bank-message categorization cost — secondary,
  cited only for a directional cost figure already consistent with the finance
  repo's own economics, not used as a design source.
- `docs/research/jev-context-management-2026-09.md`,
  `docs/research/jev-compaction-effectiveness-2026-09.md` — this repo's own
  prior, settled Jev research (identity, quota, protocol probes, coding-agent
  conclusions), built on rather than repeated.
- Five parallel `scout` subagent reports (2026-09-28), each reading shallow
  clones under `/tmp/jev-scan/` per the privacy rules in this note's brief:
  `ScoutFinance`, `ScoutHomelabNetwork`, `ScoutMailRssNotes`, `ScoutMiscToolsA`,
  `ScoutMiscToolsB` — full findings folded into §3 above with file:line
  citations; raw transcripts available at `history://JevPersonalUseCases.ScoutFinance`
  etc. within this session.
- `gh repo list sudakshsoti` — repo inventory (read 2026-09-28).
