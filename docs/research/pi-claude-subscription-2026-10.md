# Pi + Claude subscription via `@gotgenes/pi-anthropic-auth` (2026-10-02)

Pi could not reach Claude at all between 2026-09-16 and 2026-10-02; the OAuth
credential was removed after Anthropic began rejecting third-party harnesses
(`earendil-works/pi#3372`). This note records how that block actually works,
the extension that routes around it, what it costs, and the boundary this repo
enforces around it. Supersedes the "Pi has no Claude path" half of
`harness-provider-access-2026-09.md`; the OpenRouter half still stands.

## The block is prompt classification, not authentication

The 400 is not an auth failure. The token is accepted; Anthropic classifies the
**request** server-side and routes it to the account's extra-usage bucket.

`earendil-works/pi#6888` (2026-07-20, closed no-action) bisected it. Pi's default
system prompt contains one line enumerating its own docs:

```
- When asked about: extensions (docs/extensions.md), themes (docs/themes.md),
  skills (docs/skills.md), ... pi packages (docs/packages.md)
```

A fuzzy classifier keys on that dense combination, not on any single token:

- No single item trips it; the combination does.
- Renaming `skills` → `widgets` and `pi packages` → `zz packages` passes.
- A filler block of identical length passes, so it is content, not size.
- Binary search on a prefix: 2231 chars succeeds 3/3, 2232 fails 3/3.

Replacing the prompt with a minimal `SYSTEM.md` made the **identical token** bill
to the plan, proven by response headers:

```
anthropic-ratelimit-unified-status: allowed
anthropic-ratelimit-unified-5h-utilization: 0.14
```

So plan billing is reachable in principle. That is why a plugin can address
this at all: the fix is prompt shaping, not credential forgery.

## What the extension does

`@gotgenes/pi-anthropic-auth` (gotgenes/pi-anthropic-auth, MIT, 318★) re-registers
the built-in `anthropic` provider behind a thin `streamSimple` wrapper:

1. Prepends an `x-anthropic-billing-header` system block (Claude Code version +
   hash suffix), matching what Claude Code itself sends.
2. Rewrites Pi's XML-sectioned system prompt: drops the `docs` section and
   replaces the preamble with a minimal neutral prompt.
3. Reconciles the advertised `cc_version` with Pi's own `claude-cli` user-agent.
4. Retries once at the named floor when Anthropic returns
   `claude_code_version_too_old`.

Non-Anthropic providers and plain API-key Anthropic requests pass through
untouched; it activates only on an `sk-ant-oat` OAuth token.

Its own measured table (2026-09-21, pi 0.86.1, `claude-opus-5`, 28 KB prompt):

| request | result |
| --- | --- |
| pi prompt, no billing header | 400 `You're out of extra usage.` |
| same prompt + billing header | 200 |
| sanitized prompt, still no header | 400 |
| minimal prompt + billing header | 200 |

Note this **contradicts** `pi#6888`, which found the prompt alone decisive. Both
are consistent if the header is necessary but not sufficient: #6888 used a fully
minimal prompt while the extension keeps a real project prompt.

## What is actually confirmed

| Date | Evidence | Status |
| --- | --- | --- |
| 2026-09-21 | Measured table above, `pi-anthropic-auth` #70 / PR #71 | Maintainer-run |
| 2026-09-24 | Live repro, pi 0.87.1, `claude-haiku-4-5`: 400 without config → 200 with | Maintainer-run |
| 2026-09-29 | Live, pi 0.99.1: `claude-haiku-4-5` and `claude-sonnet-5-5` answered with no version-recovery retry (#81) | **Newest explicit confirmation** |
| 2026-10-02 | This repo: pi upgraded to 1.0.0, extension 3.4.2 installed, registered in `pi settings` | **Loaded, not yet exercised** |

Everything confirming success is from the extension's own maintainer. The
strongest *independent* signals are incidental in-use reports, not success
claims: `pi-anthropic-auth` #80 (2026-09-25, Team seat) and
`earendil-works/pi#10074` (2026-09-26).

**Not verified anywhere:** whether its traffic bills plan limits rather than
extra usage. The extension never asserts plan billing. The only plan-billing
header evidence (`anthropic-ratelimit-unified-5h-utilization`) comes from #6888
using a *different* workaround. Treat "subscription quota" as the plugin's
claim, not an established fact.

## This repo's state

Pi was upgraded 0.85.1 → 1.0.0 and `@gotgenes/pi-anthropic-auth@3.4.2` installed
on 2026-10-02. The extension requires ≥0.86.0, so the 2.x line was not an option.

**It cannot work yet.** `~/.pi/agent/auth.json` contains only `opencode-go`; the
`anthropic` OAuth credential was removed on 2026-09-16. A probe confirms it:

```
$ pi -p --no-session --no-tools --model anthropic/claude-haiku-4-5 "..."
No API key found for anthropic.
```

The extension loads and `/login anthropic` is the only remaining step. That is
an interactive browser flow and is per-box, like every other login in this repo.

## Two independent halves

The route has two separately-failing parts. Keeping them apart is what makes
the whole thing debuggable, and it is why this repo runs both.

| Half | Provider | Does what | Failure mode |
| --- | --- | --- | --- |
| Prompt trigger | `pi/extensions/anthropic-prompt-shim/` (repo-owned) | drops the one enumeration line from the rendered prompt | silently no-ops if upstream rewords the line |
| Billing header | `@gotgenes/pi-anthropic-auth` | supplies Claude Code's billing header | needs Pi ≥ 0.86.0 and an OAuth credential |

`pi#6888` and the extension disagree about which half dominates: #6888 found a
minimal prompt decisive with no header, while the extension measured a
sanitized prompt *still* returning 400 without the header. Both hold if the
header is necessary but not sufficient — #6888 used a fully minimal prompt,
the extension keeps a real project prompt. Either way, removing the trigger is
strictly correct and costs nothing.

### Why the prompt shim returns a full `systemPrompt`

The obvious implementation — mutate `systemPromptOptions.sections.docs` — does
not work, and fails silently. Verified against Pi 1.0.0's own source:

- `sections` on the options object holds only *caller-supplied* sections.
- `tools`, `rules`, `docs` and `cwd` are generated inside
  `buildSystemPromptSections()` at render time (`dist/core/system-prompt.js`),
  and `normalizeBuildSystemPromptOptions()` never populates them.
- So `sections.docs` is always `undefined`, and a handler keyed on it returns
  early forever while looking correct.
- `customPrompt` is not a substitute: it takes an early branch that also
  suppresses `tools` and `rules`, stripping the model's tool list.

Returning `systemPrompt` is the only lever that removes the trigger without
discarding the rest of the prompt. The cost is real and accepted: a forced
prompt is opaque to Pi, so that turn's transcript records it whole and loses
per-section delta updates.

## Verifying after an update

```
./scripts/check-claude-path.py
```

Reports Pi version against the shim's `>=0.86.0` floor, whether the package is
installed, whether an OAuth credential exists, whether the installed Pi still
builds the trigger line, whether the shim's trigger list is still in step, and
whether any Pi agent pins Claude while a prerequisite is unmet. Exits 0 with
findings: a missing credential is normal on a fresh box and must not fail
another machine's build.

Both failure modes are exercised, not assumed: the check was run against a stub
Pi whose prompt omits the trigger (reports the no-op) and with the package
absent (reports the unmet prerequisite).

## This repo's routing decision

`builder` is pinned to `anthropic/claude-opus-5-5` at `thinking: high`. That is
the single deliberate Claude consumer: it is the UI implementer, the role where
Claude's frontend judgement beats Muse Spark, and where the fragile route earns
its keep. `high` rather than `xhigh` because Claude thinking is the scarce plan
resource and `xhigh` is reserved in OMP for explicit escalation.

Everything else stays on OpenCode Go. The full ladder is unchanged.

## The boundary this repo enforces


The extension impersonates Claude Code. Anthropic's
[legal page](https://code.claude.com/docs/en/legal-and-compliance) says OAuth
"is intended exclusively for purchasers of … subscription plans and is designed
to support ordinary use of Claude Code and other native Anthropic applications,"
and reserves the right to enforce "without prior notice." A single user running
their own subscription is not squarely addressed by the "on behalf of their
users" clause, but Pi is plainly not a native Anthropic application.

It has also broken repeatedly on Pi prompt changes: the 0.86.0 XML restructure
(`pi-anthropic-auth` #67/#68), a user extension killed by the same change
(`earendil-works/pi#9838`), and a 0.79.8 lazy-registration clobber (#28).

So the pin is **explicit and revocable, never structural**:

- An explicit `model: anthropic/...` in `pi/agents/*.md` is allowed **only while
  the package is installed**. `scripts/check-model-routing.py` reads the live
  `packages[]` and enforces this.
- `anthropic` is **always** rejected as Pi `defaultProvider`, as an
  `enabledModels` cycle entry, and as `web-search.json` `summaryModel`, shim or
  not — it must never become the face of the harness or a silent fallback.
- OMP remains the Claude harness on the subscription proper; Pi stays the
  flat-rate harness by default.

## Alternatives considered

| Option | Verdict |
| --- | --- |
| `pi-claude-bridge` | Hosts Claude Code via Agent SDK. Anthropic's Agent SDK article says that draws plan limits, and a contributor measured `overage-status: rejected` — the **stronger billing story**. Rejected: this repo already removed it (issues #43, #46–#48) after a `prompt-capture` throw killed the Pi process, and that bug is still open upstream (#144). Also #151 double-loads `AGENTS.md`, ~7k tokens per turn. |
| `leohenon/pi-anthropic-oauth` | 102★, full provider replacement. No confirmed-working report found. Unverified. |
| `@cortexkit/pi-anthropic-auth` | 1.3k downloads/mo, adds relay proxying and quota management. Not evaluated. |
| Extra usage credits | The supported path. Metered at API rates, not plan limits. |
| Live OpenRouter key | Dead key answers HTTP 401 "User not found"; a new key bills per token. |

`pi-claude-bridge` is worth reconsidering if plan billing must be *proven*
rather than assumed, but it needs the #144 crash fixed upstream first.

## Re-check before trusting this

- Run `/anthropic-auth:status` in Pi to confirm the extension loaded and which
  account the login belongs to; `/anthropic-auth:status --account` adds email
  and org.
- Prove plan billing, don't assume it: watch for
  `anthropic-ratelimit-unified-overage-in-use` in responses after real use.
- Re-verify after every Pi upgrade. A prompt-structure change is what broke this
  twice already, and the extension's drift tests only guard the pi version it
  was built against.
