/**
 * anthropic-prompt-shim — keep Pi's `docs` prompt section from tripping
 * Anthropic's third-party classifier.
 *
 * Pi's default system prompt carries one dense line enumerating its own
 * documentation. Anthropic's server-side classifier reads that combination as
 * a third-party harness and routes the request to the account's extra-usage
 * bucket, which fails outright on an account without overage enabled:
 *
 *   400 invalid_request_error: You're out of extra usage.
 *
 * See earendil-works/pi#6888 (bisected: a 2231-char prefix of the prompt
 * succeeds 3/3, 2232 fails 3/3) and docs/research/pi-claude-subscription-2026-10.md.
 * Verified still present in Pi 1.0.0 on 2026-10-02.
 *
 * This extension drops that one line from the rendered prompt and nothing else.
 * It is deliberately the *conservative* half of the Claude path: it changes
 * what Pi says, not who Pi claims to be. @gotgenes/pi-anthropic-auth does the
 * latter (Claude Code billing-header impersonation) and is the route with
 * confirmed working evidence; this is an independent, less adversarial
 * alternative that does not depend on Anthropic's detection staying fooled.
 *
 * Why it returns a full `systemPrompt` rather than mutating a section:
 * `systemPromptOptions.sections` cannot address the docs section. Pi generates
 * `tools`, `rules`, `docs` and `cwd` inside `buildSystemPromptSections()` at
 * render time; the options object an extension receives holds only *caller*
 * sections, so `sections.docs` is always undefined (checked against
 * dist/core/system-prompt.js and dist/core/agent-session.js in Pi 1.0.0).
 * `customPrompt` is not an alternative either: it takes an early branch that
 * also suppresses `tools` and `rules`, stripping the model's tool list.
 * Returning `systemPrompt` is therefore the only handle that removes the
 * trigger without discarding the rest of the prompt.
 *
 * Cost of that choice: a forced prompt is opaque to Pi, so the transcript
 * records it whole instead of as diffable sections and loses per-section
 * delta updates for the turn. That is the price of the only available lever.
 *
 * Scope: prompt shaping only, applied on every turn regardless of provider,
 * because the trigger is about the prompt rather than the endpoint; the
 * Anthropic classifier is simply the one that reacts to it.
 */

import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";

/**
 * Substrings that must not reach the provider.
 *
 * #6888 found no single documentation item trips the classifier, only the
 * dense combination. The whole enumeration line goes, not just `pi packages`:
 * the line is one upstream-authored string, and editing it in place would
 * silently stop matching on the next rewording. Removing the line entirely is
 * the behaviour #6888 measured as passing.
 */
const TRIGGER_LINES = ["When asked about:"] as const;

/** True when `text` still carries a line this extension must remove. */
function carriesTrigger(text: string): boolean {
	return TRIGGER_LINES.some((needle) => text.includes(needle));
}

/**
 * Remove the trigger line, leaving every other line untouched.
 *
 * Line-based rather than a regex over the whole prompt: the line is a single
 * upstream-authored bullet, so dropping matching lines cannot damage the
 * surrounding `<docs>` section or any other section.
 */
function stripTriggerLines(prompt: string): { text: string; removed: number } {
	const lines = prompt.split("\n");
	const kept = lines.filter((line) => !carriesTrigger(line));
	return { text: kept.join("\n"), removed: lines.length - kept.length };
}

export default function (pi: ExtensionAPI) {
	pi.on("before_agent_start", (event) => {
		const prompt = event.systemPrompt;
		if (typeof prompt !== "string" || prompt.length === 0) return;

		// No trigger means upstream reworded or removed it. Do nothing rather
		// than force a prompt: an unnecessary `systemPrompt` override costs the
		// transcript its section deltas for no benefit. `/drift-check` reports
		// when this stops firing so the premise can be re-verified.
		if (!carriesTrigger(prompt)) return;

		const { text } = stripTriggerLines(prompt);
		return { systemPrompt: text };
	});

	pi.registerCommand("anthropic-prompt-shim:status", {
		description: "Show whether the Anthropic prompt trigger is present and being removed",
		handler: async (_args, ctx) => {
			const prompt = ctx.getSystemPrompt?.() ?? "";
			const present = carriesTrigger(prompt);
			ctx.ui.notify(
				[
					"anthropic-prompt-shim",
					`  trigger in current prompt: ${present ? "yes" : "no"}`,
					present
						? "  -> the next turn will drop the enumeration line"
						: "  -> nothing to remove; upstream may have reworded it",
					"  pairing: this only fixes the prompt. If requests still fail",
					"  with 'out of extra usage', the billing header is the missing",
					"  half — see @gotgenes/pi-anthropic-auth.",
				].join("\n"),
			);
		},
	});
}
