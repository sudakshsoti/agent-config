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
