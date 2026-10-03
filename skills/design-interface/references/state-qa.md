# State QA

A deliberate-failure protocol for the states most happy-path testing never exercises.

## The protocol

Go offline mid-session, not just at load. Log out mid-session, not just before it starts. Exhaust the quota or hit the rate limit deliberately. Each of these is a state a real user reaches without warning; testing only from a fresh, authenticated, under-quota session never exercises them.

## Gotcha

The source's claim that most products fail this protocol within 60 seconds is recorded here as an assertion, not a measurement — no baseline project has timed it. Do not cite the 60-second figure as if it were tested; cite the protocol.
