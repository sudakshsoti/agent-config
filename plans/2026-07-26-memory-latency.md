# Memory read/write latency: get the vault off the interactive path

Written 2026-07-26. Spans two repos: `agent-config` (the `/recall` and `/remember`
commands, the hook, `settings.json`) and `claude-memory` (the ingest conventions).

## The problem, stated precisely

`/remember` takes long enough that it is on its way to becoming something I stop
invoking. That is the failure mode, not the seconds themselves.

Measured on 2026-07-26:

- `tools/lint.py` runs in **31ms**. `wiki/index.md` is **49 lines**. The whole wiki is
  **2,518 lines** across 20 pages. Nothing about the corpus is slow.
- `/remember` reads vault `CLAUDE.md` (92 lines) + `.claude/commands/ingest.md` (123) +
  `wiki/index.md` (49) before it writes a single byte. Roughly **3k tokens of setup**.
- It then generates the raw file, reads the target wiki page, rewrites it, updates
  `index.md`, appends `log.md`, and commits. **Ten to fifteen sequential round trips**,
  several thousand tokens of output, all inline in a session whose context is already
  large. Per the global `CLAUDE.md` measurement, a mid-session token is re-read about
  **33 times**.

So the cost is not the data and not the pipeline. It is running a twelve-turn
read-modify-write inline, in the foreground, against a large context, with no cache
shared with anything.

Note the irony worth recording: PLAN.md item D moved the page template and tag taxonomy
out of the vault `CLAUDE.md` into `ingest.md` so they would load only on demand.
`/remember` invokes ingest every single time, so for this operation D moved the cost
sideways rather than removing it.

## What the field does about this

Checked 2026-07-26. The 2026 literature is unanimous that inline extraction is a bug,
and names our exact risk: doing reconciliation inline "adds latency to every response
for memory the user won't need until much later", a tax that "makes teams skip the write
path entirely". Vendors compete at 0.2 to 0.65s p95 on the read path; full-context
baselines at 9.87s median are treated as the thing to beat.

The four patterns everyone converges on:

1. Async prefetch on read, so retrieval overlaps generation and the cost is hidden
   rather than reduced.
2. Background consolidation on write. Moving heavy inference between queries rather
   than during them cut answer-time compute roughly 5x for the same accuracy.
3. A shared prompt cache between parent and worker, which drops the delegated agent's
   token overhead to near zero.
4. Deadlines and mutual exclusion so the background pass cannot run away or double-write.

Claude Code's own memory system reportedly implements all four: it scans up to 200
memory files, calls Sonnet (~250ms, 256 tokens) to pick the top 5, hides that behind
async prefetch, and runs write extraction in a forked background agent with a 5-turn
deadline and a prompt cache shared with the parent. Inline execution is reserved for an
explicit `/remember`.

Our vault is synchronous on both paths and shares no cache, because it **is** a slash
command. That is the whole delta. (Source is a third-party reverse-engineering of the
client, not Anthropic documentation, and at least part of this build writes memories
inline. Treat the mechanism as well-evidenced, not official. The engineering lesson
holds either way.)

## What this plan does NOT do

Recording these so they do not get relitigated. The vault `PLAN.md` already rejected
embeddings, a graph database, an LLM-arbitrated CRUD pipeline, access-time expiry, and
benchmark-driven tuning, with reasons that still hold. Nothing here reopens them. In
particular: none of this is an argument for a vector store or an MCP memory server.
Those address retrieval quality over a large corpus. We have 2,518 lines and a 31ms
linter.

One caution from the fresh research, hedged appropriately: a July 2026 paper on memory
operator selection finds a budget crossover where retention beats consolidation once
the raw evidence comfortably fits the budget, because the fidelity lost in compressing
outweighs the coverage gained. It is about packing evidence into a context window, not
about wiki maintenance, so the transfer is loose. Hold the direction only: a heavyweight
ingest pipeline is a cost paid now against a retrieval problem we do not have yet.

## Items

Ordered by dependency. A is the felt pain and unblocks C. B is independent. D is
separate cleanup that can happen any time.

### A. Fork the `/remember` write path

`commands/remember.md` currently runs all five steps inline. Change it so the main
session does nothing but dispatch: an `Agent` call with `subagent_type: "fork"` does
steps 2 through 5 (timestamp, raw file, INGEST, commit) and reports back.

A fork is the right primitive here specifically because it **inherits the full
conversation context**, so there is no distil-then-hand-off step to write and no risk of
the distillation losing what made the material worth keeping. It runs in the background,
and its tool output never enters the parent context.

The trade to accept knowingly: a fork always runs on the parent model, so this is Opus
tokens against a shared cache rather than Sonnet tokens against a cold one. For a
twelve-turn file-shuffling job with a large parent context, the shared cache wins. If
that turns out wrong, the fallback is distil-inline-then-dispatch to a Sonnet
`general-purpose` agent, which is strictly cheaper per token and strictly worse at
knowing what to keep.

- [ ] Rewrite `commands/remember.md` so the parent dispatches a fork and reports only
      the fork's confirmation line.
- [ ] Keep the vault's INGEST procedure as the fork's instructions by reference, not by
      inlining it into the command. The 123-line `ingest.md` should load in the fork's
      context, never the parent's.
- [ ] Give the fork an explicit bound: if it cannot finish INGEST, it must still leave
      the `raw/` file written and say so. A half-ingested vault is recoverable; a lost
      raw file is not.

**Acceptance.** Invoke `/remember` on a real session. The raw file exists, the wiki page
is created or updated, `index.md` and `log.md` are updated, and the vault has a commit.
The parent session's context grows by roughly the confirmation line only, not by twelve
turns of tool output. Verify by inspecting the transcript, not by asking the model.

### B. Grep-first `/recall`

`commands/recall.md` routes every lookup through `CLAUDE.md` + `index.md` summaries and
then opens whole pages of 130 to 180 lines when the task needs one section.

- [ ] Rewrite step 1 to grep `wiki/` for the task's terms first, and read only the pages
      that hit.
- [ ] Keep `index.md` as the fallback for when grep returns nothing, which is exactly
      the case where a summary-level scan is the right tool.
- [ ] Preserve the existing prohibitions verbatim: never bulk-read `wiki/`, never read
      `raw/` during recall.

At 20 pages grep is instant, so this is a read-volume fix rather than a search-speed
fix. It composes with C: typed observations make a grep hit land on the fact instead of
the page.

**Acceptance.** A recall on a known topic (say `hermes`) reads at most two files before
answering, and the answer is no worse than today's. A recall on a topic the vault has
never seen still says so rather than guessing.

### C. Typed observations in INGEST (vault `PLAN.md` item F)

- [ ] Add the `- [decision] chose X over Y because Z` observation form to the page
      template in `claude-memory/.claude/commands/ingest.md`.
- [ ] Document the convention in the vault `CLAUDE.md` in one line, not a section. That
      file is the always-resident one and the IFScale finding about instruction density
      applies to every line added to it.
- [ ] Decide whether `tools/lint.py` should check observation syntax. Default is no: an
      unenforced convention is better than a check that fires on every legacy page.

**Acceptance.** A page ingested after this change carries typed observations, `lint.py`
still exits clean on the existing wiki, and grepping for a decision term lands on the
observation line rather than only on the page title.

### D. SessionEnd consolidation hook (vault `PLAN.md` item G)

The endgame. A and B move the work off your critical path; only this removes the wait
entirely, because the work happens when nobody is watching. It is also the enforcement
point that stops `~/.claude/projects/*/memory/` refilling with unprovenanced copies
(see E).

Constraints from this repo's own `CLAUDE.md`, which are not negotiable: a hook must
never block a prompt, must exit 0 and print nothing on error, and must be bounded in
time. `hooks/context-budget.py` is the working model to copy, and
`scripts/test-ctx-flag.sh` is the precedent for how an intentionally silent thing gets
tested.

- [ ] Write `hooks/memory-consolidate.py`. It fires on `SessionEnd`, decides whether the
      session produced anything durable, and if so runs the A path.
- [ ] Wire it in `settings.json` and mirror the change with `sync.sh` conventions.
- [ ] Make it commit separately, so the consolidation diff is reviewable on its own.
- [ ] Add mutual exclusion, so two sessions ending together cannot double-write.
- [ ] Extend `scripts/test-ctx-flag.sh` or add a sibling test. The failure mode of a
      silent hook is that it looks exactly like a quiet one, which is the specific trap
      this repo already documents.

**Acceptance.** Ending a session with durable material produces a vault commit without
any wait in the session itself. Ending a session with nothing durable produces no commit
and no output. A deliberately broken hook still exits 0 and blocks nothing, proven by a
test rather than by reasoning.

### E. Reconcile the harness memory store against the vault

Found 2026-07-26 while diagnosing the above. Claude Code's own file-based memory has
written **30 files across 12 project directories** under `~/.claude/projects/*/memory/`.
Three collide directly with vault content:

- `-Users-sudakshsoti-dev-vault/memory/dori-100-crore-ambition.md` and
  `dori-treat-as-new-brand.md` against `wiki/dori-new-brand-reset.md`, committed the
  same day
- `-Users-sudakshsoti-dev-homelab/memory/hermes-primary-codex.md` against
  `raw/2026-07-23-hermes-codex-primary-and-cron-inventory.md`
- `-Users-sudakshsoti/memory/home-network-topology.md` against `wiki/home-network.md`

Those files carry no `sources:`, no `valid_from`, no supersession rule and no lint pass.
They are the failure mode the vault's whole design exists to prevent, running
unsupervised in a directory nobody reads. This also answers open question 3 in the vault
`PLAN.md` the bad way: the vault is not consulted from other directories, so the harness
store filled the gap with unprovenanced copies.

- [ ] Decide which store is authoritative for which fact type. Working proposal: the
      vault owns durable knowledge; the harness store owns nothing that outlives a
      session.
- [ ] Reconcile the 30 files once. Most are one-line preferences that belong in the
      vault or in `global-CLAUDE.md`. A few are real wiki content and should be ingested
      properly, with provenance.
- [ ] Record the decision in the vault so it does not get made differently next month.

**Acceptance.** No fact exists in both stores with different content. The Dori
collision in particular is resolved in favour of one page.

## Sequencing

A, then B, then C, then D. E can run in parallel with any of them and is the only item
that touches data rather than mechanism.

Stop after A and B if the pain is gone. D is the correct endgame but it is also the only
item that can break a session start, and the value of a hook you have to debug at 2am is
negative.

## Baseline to capture before starting

Do this first, or none of the acceptance criteria above are checkable:

- [x] Time one `/remember` end to end, and count its tool round trips from the
      transcript. Already captured above under "The problem, stated precisely":
      ten to fifteen sequential round trips, ~3k tokens of setup, measured
      2026-07-26.

Re-run the same measurement after A. If the round-trip count in the parent does not drop
to roughly one, A did not do what it claims.

## Sources

- HarrisonSec, Claude Code memory deep dive: https://harrisonsec.com/blog/claude-code-memory-first-principles-tradeoffs/
- Zylos, memory consolidation in long-running agents: https://zylos.ai/research/2026-04-20-memory-consolidation-ai-agents/
- Supermemory, latency budgets for memory retrieval: https://blog.supermemory.ai/latency-budgets-memory-retrieval/
- Hindsight, the consolidation problem: https://hindsight.vectorize.io/blog/2026/05/21/agent-memory-consolidation
- Retain or Consolidate? Budget-dependent operator selection (arXiv 2607.17545): https://arxiv.org/html/2607.17545v2
- Zep on Mem0's benchmark claims: https://blog.getzep.com/lies-damn-lies-statistics-is-mem0-really-sota-in-agent-memory/
- Prior art in this house: `~/dev/claude-memory/PLAN.md` items F and G
