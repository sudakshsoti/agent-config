# The Closed List

One file. It answers *what is alive right now* so that question is decided once rather
than re-argued every morning. Orient and Triage read it; only Mode 3 writes it.

## Where it lives

Discovered, not hard-coded — the operator's setup decides:

- A notes vault (Obsidian PARA and similar): an Areas-level note, e.g.
  `02 Areas/ClosedList.md`. Best default when one exists — it sits beside the project notes
  the operator already reads.
- A repo: `ClosedList.md` at the root, or wherever a `CLAUDE.md`/`AGENTS.md` points.
- **No filesystem** (claude.ai, a hosted assistant): a Linear document or a Notion page.
  If neither is available, ask the operator to keep the ledger themselves and paste it at
  the start of a session — degraded, but it still beats guessing.

Record the resolved path the first time and reuse it. Two ledgers is worse than none.

## Format

```markdown
# Closed List — Q<N> <year> · <name> (<quarter-start> → <quarter-end>)

## Live
Capped at the job + 3. Each carries a finish condition and a consequence.

| Commitment | Finish condition | Who's harmed if it slips | Next move |
|---|---|---|---|
| The job | (ongoing) | employer, income | — |
| AGM Motors site | Design signed off + handed to build | Paid client, invoice waits | Homepage layout |
| Dori branding | Identity system delivered | Promised, external | Logo lockups |
| Finance system | Ledger trusted, one dashboard | Only me — but money | Reconcile Q2 |

## Floor
Non-negotiable, cheap, only hurts when missed. Never traded against Live work.
- Meds, morning + night
- Timesheet, weekly
- Any payment or renewal with a real date

## Dormant
Not failure — the reason the three above are real. Each gets a resurface date.
| Project | Why not now | Resurface |
|---|---|---|
| Twin Peaks Case File | Pure fun, zero consequence | Nov 2026 |
| Tokenmaxxing | Interesting, not load-bearing | Next season |

## Failing at
Written down, so it is a decision rather than guilt.
- Homelab beyond keeping it running
- Reading the tooling backlog
- Any new side project, however good

## Notes
One or two lines on what this season is *for*.
```

## Capacity rules

- **Live = the job + 3.** The job is not one of the three; it is the ground the three sit
  on. Three is a ceiling, not a target — two is a better season than four.
- **Consequence ranks, interest does not.** Paid, promised, or load-bearing for another
  person outranks personally interesting. This rule exists specifically because interest
  wins in the moment and consequence wins in the accounting, so the ledger has to hold the
  line the operator's attention will not.
- **A finish condition is mandatory.** "Work on X" is not a commitment; it is a mood.
  Anything with no answer to *what has to be true for this to be done* goes Dormant.
- **Dormant has a date.** Without one it reads as abandonment and the operator will keep
  it Live out of loyalty. With one it reads as scheduled, and it lets go cleanly.
- **The Floor is not a slot.** It sits outside the three entirely.
- **Tag the quarter, everywhere it's filterable.** Every Live commitment and every
  Dormant item's resurface point should carry a matching quarter label wherever the
  underlying system supports one — `quarter/qN-YYYY` in Obsidian, `qN-YYYY` in Todoist,
  `QN YYYY` in Linear. Moving something to the next quarter under overcommitment is then
  a one-field edit — swap the label — not a rewrite.

## The cull procedure

1. **Sweep.** Every system, plus the uncaptured question. Count what you find.
2. **Show the count first.** "Eleven Linear projects, two freelance clients, a job, and
   nine open household items" is the argument. Let it sit before proposing anything.
3. **Sort into three buckets** — has a finish condition and a consequence / has a finish
   condition but no consequence / neither.
4. **Fill Live from bucket one**, consequence-ranked, up to three. If bucket one holds
   more than three, that is the real conversation: something with a genuine counterparty
   has to be renegotiated or delayed, and the honest move is to say which and help draft
   the message.
5. **Everything else is Dormant**, each with a resurface date and one line of why not now.
6. **Draft the "failing at" list** from what the operator keeps flinching about.
7. **Read it back**, then write on approval.

## Revising mid-season

Cheaper than a full cull and far more common — a new client, a deadline moving, energy
dropping. Change one row, keep the cap. A swap is a swap: something leaves Live for
something to enter. If the operator wants a fourth Live commitment, the answer is which of
the three is going Dormant, asked as a question rather than argued as a position.

Reconvene the full procedure when the review-by date passes, **when the calendar quarter
turns over**, the season's purpose has changed, or the ledger has stopped matching what
the operator actually does — that last one is the real signal, and it shows up as Orient
repeatedly recommending work that is not in the ledger.
