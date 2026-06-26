# Worked examples

A bank of `explain-this` explanations across the surfaces Claude works on. Each
follows the contract: jargon-free **In short**, then a skippable `Going deeper`
layer naming one concept with an everyday analogy. Use these to calibrate tone —
not as scripts to copy.

---

## Coding — caching a result

> **In short:** I'm saving the result of a slow calculation so we don't redo it
> every time the screen redraws.
>
> Going deeper (optional):
> - **The idea — `caching`:** keeping the answer to expensive work nearby so you
>   can reuse it instead of recomputing.
> - **Like…** writing a phone number on a sticky note instead of looking it up
>   in the directory every single time.
> - **Why it matters:** much faster, but the sticky note can go stale — if the
>   underlying data changes we have to remember to throw the note away.

## Coding — an API request

> **In short:** I'm asking another service for the data we need and waiting for
> it to answer before I show the page.
>
> Going deeper (optional):
> - **The idea — `API call`:** a structured request to another program — you ask
>   a specific question in an agreed format, it sends back an answer.
> - **Like…** ordering from a menu: you don't go into the kitchen, you give the
>   waiter a known order and food comes back.
> - **Why it matters:** if their kitchen is slow or closed, our page has to
>   handle the wait or the no-show gracefully rather than just hanging.

## Homelab — recovering a stuck mount

> **In short:** I'm restarting the storage connection in a specific order,
> because a plain restart would wedge it harder.
>
> Going deeper (optional):
> - **The idea — `FUSE mount`:** a folder that's really a live window into remote
>   storage, not files actually sitting on the disk.
> - **Like…** a TV showing a live camera feed — yank the cable mid-frame and it
>   freezes; you have to reconnect in order, not just hit the power button.

## Automation — an n8n workflow on a schedule

> **In short:** I'm setting this little automation to run by itself every morning
> instead of you triggering it.
>
> Going deeper (optional):
> - **The idea — `cron schedule`:** a clock-based rule that says "run this at
>   exactly these times" without anyone pressing go.
> - **Like…** a programmable coffee maker set for 7am — it just happens, you
>   don't get up to start it.
> - **Why it matters:** reliable and hands-off, but if it fails at 7am nobody's
>   watching, so it needs to shout (a notification) when something breaks.

## Infra — putting work in a queue

> **In short:** Instead of doing every job the instant it arrives, I'm lining
> them up so the system handles them steadily without getting overwhelmed.
>
> Going deeper (optional):
> - **The idea — `queue`:** a waiting line for tasks — they get added at the
>   back and worked off the front, one or a few at a time.
> - **Like…** a single-file line at a coffee counter: orders don't get lost in a
>   stampede, they're served in order at a pace the barista can keep up with.
> - **Why it matters:** smooths out spikes so nothing crashes under load; the
>   tradeoff is a job might wait a moment before it's picked up.

## Git — branching before a change

> **In short:** I'm making a private copy of the project to work in, so nothing I
> try can break the version that's currently working.
>
> Going deeper (optional):
> - **The idea — `branch`:** a parallel line of work split off from the main one,
>   that you can merge back in once it's proven good.
> - **Like…** drafting an essay in a separate document instead of editing the
>   published one live — you only paste it back when you're happy.
> - **Why it matters:** experiments stay safe and reversible; the main version is
>   never at risk while the work is in progress.
