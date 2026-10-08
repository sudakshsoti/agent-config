# Frontend artifact guidance

- [stated] Keep frontend-artifact separate from Vibe: Vibe is a workflow, not an aesthetic. Do not change Vibe in this task. — User, 2026-09-11.
- [stated] Include all eight languages from the handoff in v1. — User selected “All eight directions”, 2026-09-11.
- [stated] If no language is named, recommend a direction and wait for confirmation before building. — User selected “Recommend, then confirm”, 2026-09-11.
- [stated] Naming or confirming a language approves its documented visual defaults; ask again only for important uncovered decisions or conflicts. — User selected “Yes, approve defaults”, 2026-09-11.
- [stated] Language defaults govern visual choices only; preserve content, requested features, the surface's job, accessibility and applicable project decisions. — Approved plan, 2026-09-12.
- [stated] Start with one inspected, annotated screenshot per language; expand later rather than requiring a full reference library now. — User selected “Curated starter set”, 2026-09-11.
- [stated] Validate the same latency content as technical-field-guide and visual-essay, plus a personal-software research-list utility, in both Codex and Pi. Five other languages receive profile and reference review only in v1. — User selected “Small comparison set” and approved plan, 2026-09-12.
- [stated] Use semantic HTML, plain CSS and minimal JavaScript for new standalone artifacts; respect an existing project's stack. Reuse the existing design skills and shared installation. — Approved plan, 2026-09-12.
- [stated] Render and inspect at 390 px and 1440 px minimum, allow two correction passes and report unresolved failures. — Approved plan, 2026-09-12.
- [stated] Each language ships a starter skeleton with real tokens and a validated Google Fonts pairing; standalone artifacts may load fonts from Google Fonts because a single file cannot self-host. — User, 2026-09-12.
- [stated] Measurable taste rules are enforced by `references/audit.js` with the thresholds in `visual-qa.md`; a FAIL is fixed before screenshots. — User, 2026-09-12.
- [stated] The critic pass runs in a fresh process with the screenshots, the reference image and the audit output, and returns the fixed structure in `critic-prompt.md`. — User, 2026-09-12.
- [stated] Vibe moves from a Pi-only prompt to `skills/vibe`, visible to every harness, with harness-specific role dispatch; `pi/prompts/vibe.md` and `codex/prompts/vibe.md` are thin wrappers. This supersedes the 2026-09-11 "do not change Vibe" scope, which applied to that task only. — User, 2026-09-12.

# cmux sidebar and tab chrome

- [stated] The sidebar's density register is 11 rows fully visible at 437pt of list height. — User, 2026-09-19.
- [stated] A workspace row carries title and git branch only. — User, 2026-09-19.
- [stated] The last notification body is removed from the row; the spinner and unread badge carry agent state. — User, 2026-09-19.
- [stated] The pull-request line is removed from the row. — User, 2026-09-19.
- [stated] The listening-ports line is removed from the row. — User, 2026-09-19.
- [stated] The sidebar ground is flat, opaque Flexoki base-900 `#282726`, not macOS vibrancy grey. — User, 2026-09-19.
- [stated] The selected row is a filled band in Flexoki base-800 `#403E3C`; a rounded pill is accepted. — User, 2026-09-19.
- [stated] Workspace hues are the eight Flexoki 850s, used as text backgrounds. — User, 2026-09-19.
- [stated] The unread badge is Flexoki orange `#DA702C`, on the leading edge; the loading spinner is trailing. — User, 2026-09-19.
- [stated] Sidebar type is 13pt; the surface tab bar stays at 12pt. — User, 2026-09-19.
- [stated] Workspace titles do not wrap; they truncate to one line. — User, 2026-09-19.
- [stated] Unnamed workspace titles show the last path segment only. — User, 2026-09-19.
- [stated] The app appearance is pinned to dark rather than following the system. — User, 2026-09-19.
- [stated] Workspace naming uses cmux AI auto-naming with the naming agent pinned to `opencode`, so titles bill flat-rate Go rather than the Claude plan. — User, 2026-09-19.
- [stated] `title` is removed from Ghostty's `shell-integration-features` so the shell does not write the running command into the row. — User, 2026-09-19.
- [stated] The pane divider is Flexoki base-850 `#343331`, replacing the inherited cool blue-grey. — User, 2026-09-19.
- [stated] Rows keep their position: `reorderOnNotification` is off, because spatial memory is the fastest way back to a session. — User, 2026-09-19.

# OMP composer shape

- [stated] `composer.shape` is `rule`, not `rail`: Collie (the Herdr phone client) only detects OMP's `box`, `rule` and `pi` composers, and refuses every phone reply on an unrecognised one ("The agent's input box isn't on screen"). `rule` is the closest supported look to `rail`. Revisit only if Collie gains `rail` support. — User, 2026-10-02.

# Skill audit follow-up

- [stated] The `opencode-go/glm-5.3-flash` fallback chain becomes `mimo-v2.6-pro:high` → `deepseek-v4.1-flash:max` → `openrouter/deepseek/deepseek-v4.1-flash:high` → `anthropic/claude-sonnet-5-5:medium`. All three Go rungs share one provider, so OpenRouter DeepSeek keeps review cross-lineage through a Go outage; Sonnet stays last so scout, smol and commit traffic still runs if Go and OpenRouter are both down. OpenRouter per-token billing (the `omp.sh` key) during a Go outage is accepted. — User, 2026-10-04.
- [stated] `peer-review` reports the model that actually ran and labels a Claude fallback "same-lineage", instead of claiming the chain holds no Anthropic model. — User, 2026-10-04.
- [stated] `find-skills` is retired to `skills/_archive/`; adding skills goes through `skill-lifecycle` and `plugins.txt`. — User, 2026-10-04.
- [stated] `ux-writing` capitalisation: sentence case by default; native apps follow platform convention (e.g. Title Case for macOS menus and buttons). — User, 2026-10-04.
- [stated] The Indian English / INR / Indian-numbering line is removed from `design-strategy`, `design-visual-system`, `vbc-design` and `clinical-reasoning`, because most products are American. It is replaced by "Match the product's market locale for spelling, currency and number format" (the user's locale in `clinical-reasoning`). "No disclaimers" and "address the user as you" stay, deduplicated within each file. — User, 2026-10-04.
- [stated] `clinical-reasoning` keeps its Indian clinical content (guideline hierarchy, brand examples, NCR references); only the voice line changes. — User, 2026-10-04.

# Claude Code delegation

- [stated] `specialist-delegation` covers Claude Code alongside Pi and OMP. Adversarial review has no Claude Code route, because every subagent there is Claude; it goes to `peer-review` in Pi or OMP. — User approved plan, 2026-10-06.
- [stated] Claude Code gets three repo-owned agents in `claude/agents/`: `scout` on Haiku, `code-worker` and `builder` on Sonnet at medium effort. Reviewer, research, plan and critic stay on built-ins plus skills until there is evidence they need more. — User approved plan, 2026-10-06.
- [stated] The work machine gets the agents only with `--claude-agents`: tokens are tightest there, and the agents run only Claude inside Claude Code, so no new vendor sees work code. The rest of the work gate is unchanged. — User, 2026-10-06.
- [inferred] `builder` loads the design skills on demand with the Skill tool instead of preloading them, so a launch does not pay for skills a small tweak never reads.

# OMP model routing

Moved from `AGENTS.md` on 2026-10-06; the live routing table stays there.

- Routing rationale (2026-09-16, `docs/research/*-2026-09.md`): the ladder ran
  on `openai-codex` until that subscription was dropped over frontend quality —
  Luna sits at DesignArena rank 48 overall (1242), the weakest routed model on
  every board. Claude Opus 5 is rank 8 (1338), above GPT-5.6 Sol medium (1334),
  and it wins DesignArena UI Components outright (#5, 1361, ahead of Fable 5.1
  at #12), so it takes `default` and the roles that *decide* or *judge* visual
  work (`plan`, `designer`, `vision`, `critic`). Claude
  Fable 5.1 is rank 6 overall and #2 on LMArena WebDev, but on Max-class plans
  Fable burns regular weekly limits at roughly double rate and is capped at 50%
  of them before it needs usage credits — on Pro-class plans it is
  credits-only from the first message. So Fable stays manual `/model`
  escalation, never a role pin. Sonnet 5 ($2/$10, AA index 38 vs Opus 5's 51)
  carries `task`, `workflow` and `builder`: `builder` implements a plan that
  `plan`/`designer` already fixed, so Sonnet 5's weaker from-scratch design
  standing (DesignArena task boards ranks 22-37) costs little. It ran at
  `high` effort until 2026-09-28, when it dropped to `medium` (user decision)
  alongside `task` and `workflow`. Haiku
  4.5 is no longer pinned to a role: per-turn housekeeping (`smol`, `tiny`,
  `commit`) went to GLM 5.3 Flash, and `code-worker`/`sonic` to Muse Spark 1.3
  Contributor (AA 48 vs DeepSeek V4.1 Flash's 40 and Sonnet 5's 38), because
  pre-decided work belongs on the cheapest adequate quota. Haiku stays a
  fallback rung only. `scout` stays on GLM: it is the highest-frequency agent
  and Go's flat rate absorbs discovery without touching either subscription.
  DeepSeek V4.1 Flash's $60 Go cap is a promo ending 2026-09-20 (then $15,
  i.e. $3 per 5 hours), which is why `code-worker` left it on 2026-09-18; it
  remains the second rung under Muse and the manual throttle fallback.
  Anthropic publishes no per-model weekly message counts, so subscription
  burn rate per role is not predictable from primary docs.
  The Opus rung moved from `claude-opus-5` to `claude-opus-5-5` on 2026-09-23
  (user request, successor swap only): same provider, same 1M/128K limits and
  the same low/medium/high/xhigh/max effort set per `omp models`, and
  `anthropic/claude-opus-5-5` answered a retry-disabled `omp -p` probe. The
  benchmark figures above are the 2026-09-16 Opus 5 evidence and have not been
  re-measured for 5.5; the role split they justify is unchanged.
  The `opencode-go/glm-5.3-flash` fallback chain gained
  `opencode-go/mimo-v2.6-pro:high` as its first rung on 2026-10-02 (user
  decision), ahead of `deepseek-v4.1-flash:max`. Artificial Analysis v4.3.2
  per-benchmark data: hallucination rate GLM-5.3-Flash 27.6%, MiMo-V2.6-Pro
  40.6%, MiMo-V2.6-Flash 54.4%, DeepSeek V4.1 Flash (max) 96.5%; Terminal-Bench
  4.0 34.8 / 32.8 / 22.7 / 26.8. Review roles therefore fall back to the
  lower-hallucination model, not DeepSeek. MiMo-V2.6-Pro's Go cap is $15/month,
  so DeepSeek stays as the next rung. Chains match by exact model, so scout,
  smol and commit traffic also lands on MiMo-Pro `:high` during a GLM outage.
  No role was moved to MiMo: Pro's +4 index lead over GLM comes mostly from
  HLE/CritPt, the Terminal-Bench gap is within noise, and Pro hallucinates more.
  The same chain gained `openrouter/deepseek/deepseek-v4.1-flash:high` between
  `deepseek-v4.1-flash:max` and the Sonnet rung on 2026-10-04 (user decision):
  all three Go rungs share one provider, so the OpenRouter rung keeps review
  cross-lineage through a Go outage, and OpenRouter per-token billing (the
  `omp.sh` key) during that outage is accepted. The model answered a
  retry-disabled probe; Sonnet stays last so scout, smol and commit traffic
  still runs if Go and OpenRouter are both down.

# Pi Jev compaction

- [stated] Pi uses `@alexlikevibe/pi-jev@0.2.1` for context compaction, over the TypeSafe transport, with the key from 1Password item `Mail - TypeSafe API key` (Homelab vault). Routing stays off: it activates only when `routing.cheap` or `routing.strong` is set, and none is. — User, 2026-10-06.
- [inferred] This reverses the 2026-09-28 "do not install" verdict (`docs/research/jev-compaction-effectiveness-2026-09.md`) for Pi only. That verdict rested on OMP's `shake` and `snapcompact`, which Pi lacks; Pi's only built-in path is a model-written summary. The caveats stand: Jev prunes tool output and cannot summarise, each compaction costs one prompt-cache miss, and tool output (repository source included) reaches TypeSafe, so the key is read on the personal Mac only.
- [stated] The key is never written to a file: dotfiles' `pi()` wrapper reads it at launch and hands it to that one process as `TYPESAFE_API_KEY`. A failed read leaves Pi on its normal compaction. `JEVC_DISABLED=1 pi` bypasses Jev. — User, 2026-10-06.

# Pi Claude default

- [stated] Pi defaults to Claude: `role/default` and `role/task` resolve to Sonnet 5.5 and `role/plan`/`role/slow` to Opus 5.5 through `pi/model-roles.json`, and Sonnet is a rung in the GLM fallback chain. — User, 2026-10-09.
- [stated] This overrides the earlier rule that the `@gotgenes/pi-anthropic-auth` impersonation route must never be Pi's default or a fallback. The ToS risk (Anthropic's legal page prohibits impersonating Claude Code) and the breakage risk (it broke twice on Pi prompt changes) are accepted. — User, 2026-10-09.
- [inferred] `check-model-routing.py` now resolves `role/*` through `pi/model-roles.json` and allows `anthropic/*` anywhere in Pi only while the package is in `pi/settings.json` `packages[]`, so dropping the package still fails every Claude route loudly. Without `/login anthropic` the Claude rungs have no credentials and the role chains fall through to OpenCode Go.
