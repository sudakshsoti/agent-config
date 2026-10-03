# Cross-review of skill-audit.md (2026-10-04)

Reviewed report: `~/.omp/agent/sessions/-.herdr-worktrees-agent-config-worktree-brave-harbor-4d20/2026-10-03T18-57-49-646Z_01a10321-324e-75fd-9595-95b53d9d87c9/local/skill-audit.md`
Repo: worktree-lucky-valley-ac3c @ 543d7272 (same HEAD as the audit, clean tree).
Reviewers: 4 × `adversary` (GLM 5.3 Flash, second lineage), each verifying cited file:line evidence.
Full outputs: `agent://AdvTopLevel`, `agent://AdvDetailsA`, `agent://AdvDetailsB`, `agent://AdvDetailsC`.

## Verdict

The audit holds up. Most findings were confirmed, and no high-severity finding was wrong. Before acting on it:
- Re-scope two Top-10 fixes (#5 and #10), because as written they would cause harm.
- Re-rank the Top 10.
- Apply about 8 corrected detail fixes instead of the audit's literal wording.

|Range|Findings|Confirmed|Objections|
|---|---|---|---|
|Top-level (§1–5)|Top 10 + §3/§4|38 claims|10|
|Details A (backlog → handoff)|91|81|10 (1 wrong, 9 overstated)|
|Details B (harness-config → specialist-delegation)|88|74|14|
|Details C (strategy-counsel → writing-editor)|48|45|12|

The summary arithmetic checks out: 11 high, 109 medium, 113 low, 233 total; 35 tighten, 1 rewrite, 1 keep.

## Top-10 amendments

1. **#5, hand-offs to flagged skills: the "tell the user to run /ux-writing" fix is harmful.**
   - Verified in this OMP session: `read skill://ux-writing/SKILL.md` returns the full file even though it has `disable-model-invocation: true`. The flag only removes the skill from the routing list.
   - The OMP hand-offs therefore work. Rewording them as prompts to the user would break that.
   - On claude.ai, `build-dist.py` strips the flag, so the hand-off is fine there too.
   - The remaining risk is Claude Code local [UNVERIFIED]. Limit any fix to that surface.
2. **#10, shared voice block: the "state it once in global-agents.md" option is harmful.**
   - `clinical-reasoning`, `design-strategy`, `design-visual-system` and `vbc-design` all ship to claude.ai.
   - `global-agents.md` is linked only into OMP and Pi, and is never packaged.
   - Moving the rules out of the skills would strip them from every claude.ai copy.
   - Fix: deduplicate within each file only. If you want a single source, it has to be a distributed skill.
3. **Ranking.** #1 (peer-review's false claim about the fallback chain) is real: `omp/config.yml:55-58` ends the chain in `anthropic/claude-sonnet-5-5:medium`. But it only matters when both Go rungs fail, and the fix is one line.
   - #3 (the vibe Critic contract) breaks every UI review loop, and #2 (find-skills uses the banned `npx skills add`) is an outright ban violation.
   - Suggested order: #3, #2, #7, #6, #1, #4, #8, #5, #10, #9.
   - #9 (progressive disclosure across 7 files) is a project, not a fix. Split it or rank it last.
4. **#4 file count is 7, not 6.** It also misattributes the Haiku evidence: the fallback-rung proof is `omp/config.yml:51,53`, not AGENTS.md.
5. **#3 wording.** `audit.txt` is conditional (vibe:21, "when the page is standalone"). The dead instruction is the unconditional "re-run the audit" (vibe:45), plus the mismatch with the critic return shape. The fix (move rules and return shape into `omp/agents/critic.md` and `pi/agents/Critic.md`) is cheap, since vibe is only 49 lines.

## Internal contradictions in the audit

- **Co-author rule.** §4 says "prefer the commit-push skill" and §3 says keep it global. Keep it global: commit-push is flagged, so commits made without the skill would lose the rule. Strike §4's branch.
- **ux-writing Reporting section.** The medium/size fix moves it to `references/`, while the low/actionability fix moves it to the top. Keep it in the main file, since it is the only completion criterion, and move only Formatting & Style.
- **Pointer convention.** For strategy-counsel the audit says drop the inline links and keep the References section. For ux-writing it says the opposite. writing-for-agents favours point-of-use pointers, so keep the inline ones.

## Wrong findings (drop or correct)

|Skill|Audit claim|Evidence against|
|---|---|---|
|design-typography|font ban list duplicated in design-visual-system:165-167|zero grep hits in dvs; the copies are in `_archive/frontend-artifact` only. Duplication of the OFL/system-stack rule still stands|
|humanizer|"Do not apply §14 as a ban" contradicts patterns.md §14|patterns.md:138 already carries the "unless the writer's sample uses them" exception|
|overnight-run|deepseek override "pinned by check-model-routing.py"|no deepseek/mimo in that script; model-ladder says "DeepSeek V4.1 Flash has no agent pin"|
|self-review (§5 row)|Pi default model not in-lineage|Pi main and `general-purpose` both run muse-spark-1.3-contributor|
|specialist-delegation|OMP bundled agents unconfirmed|AGENTS.md routing gotcha names them|
|specialist-delegation|"be explicit" names no setting|same bullet names `run_in_background: true`|

## Harmful fixes (apply the corrected version)

|Skill|Audit fix|Correction|
|---|---|---|
|homelab-deploy|state restart-vs-recreate once in Pre-flight|keep rclone "NOT restart" + FUSE rationale inline; only the env-var rule moves|
|humanizer|delete false-positive bullets as detection-only|they govern what a rewrite keeps; move to references, don't delete|
|workstreams|cut coordinator paragraph to one line|keep "do not bypass its allowlist or edit configuration to expand its authority" verbatim|
|writing-editor|delete Opening template from mode-playbooks.md|also rewrite SKILL.md's pointer to it, or it dangles|
|vibe|delete "escalation thresholds" phrase|design-interface has `## Escalation triggers`, explicitly owned for vibe; rename, don't delete|
|specialist-delegation|move role table + Launch to ROLES.md/LAUNCH.md|both used on every dispatch; trim the repo-path caveat and "Fit into normal work" instead|

## Overstated (downgrade severity)

- backlog: the L/weekend vs 5–8 band "contradiction" is consistent (L=5 sits inside 5–8). Only the `XL`=8 mapping is dead data. Downgrade medium → low.
- clinical-reasoning: "no hedging" is scoped to disclaimers by its own gloss. Downgrade medium → low.
- design-grill: the "Skill tool" wording is documented as intentional (plugins.txt:73-75). Downgrade medium → low.
- design-interface: the rule count is ~38, not ~50 (high stands). The blur/submit "contradiction" is already reconciled; keep only the disabled-state reword.
- design-visual-system: the surface classes *are* defined; what's missing is a classify-first step. The menu-vs-gating "contradiction" isn't one.
- geopolitics, rights-counsel, overnight-run, homelab-deploy, codebase-memory, vedic-astrology, maintainability-review: one low "contradiction" each that the files already reconcile.
- ux-writing: the 40–60 chars vs 8–14 words limits use different units. The real contradiction is reading level (7th vs 7th–8th vs 9th–10th).
- rights-counsel (Next tier): tax is in and out of scope; RERA is only in scope. Drop the RERA half.
- strategy-counsel (§5 row): the "career scope conflicts with vbc-design routing" claim is unsupported; vbc-design:115 routes to it consistently.
- workstreams: the "read the active role" mitigation is already in the file (:50, :58–59). Downgrade to a nit.

## Missed by the audit

- handoff `README.md:105-106` links to a non-existent `compaction-hook` skill. The H1 is `# Session Handoff Skill`, the same H1/name mismatch class the audit flagged elsewhere.
- clinical-reasoning: RNTCP also appears in `references/clinical-framework.md:26`. The audit's fix would leave it stale.
- vbc-design:109 routes non-healthcare design to `design-strategy`. The natural target is `design-interface`/`design-visual-system`.
- ux-writing: "active voice 85% of the time" vs "active voice (unless passive is clearer)".
- harness-config-maintenance: the ownership-table row "one link serves both harnesses" omits the `~/.claude/skills` second link. Fix it together with that finding.
- maintainability-review: the description says "frontend code", but the modes and checklist are whole-repo and language-agnostic.
- homelab-deploy: hard-coded `git -C ~/dev/agent-config show fafe8c11^:…` paths and commit pins.
- §3 1Password: the safe target is the homelab repo's AGENTS.md, not flagged `homelab-deploy`.

## Confirmed strongest items (act first)

vibe Critic contract · find-skills `npx` ban · skill-lifecycle Install section · ux-writing case contradiction · the 7 dangling refs · peer-review chain claim · merge squash vs stacked PRs.
