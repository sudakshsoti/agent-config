/**
 * model-roles — OMP-style model roles and fallback chains for Pi.
 *
 * Each role in `<agent dir>/model-roles.json` (repo: pi/model-roles.json) is
 * registered as a virtual model `role/<name>`, so `/model`, Ctrl+P
 * (`enabledModels`), `--model`, Plannotator phases and settings can all select
 * a role by name. Pi asks the router for a physical model before every request
 * (docs/virtual-models.md), and the router walks the role's fallback chain:
 *
 *   - `user` / `direct`: the first usable model, primary first. A model is
 *     usable when it has credentials and is not cooling down.
 *   - `continuation`: stay on the model that answered last, so the prompt cache
 *     and thinking signatures survive, unless it has since been benched.
 *   - `retry` (Pi's own retry of transient errors: 429, overload, 5xx):
 *     stay on the failed model until it has failed `failuresBeforeFallback`
 *     times in a row, then bench it and move down the chain.
 *
 * Pi does not retry quota, billing or auth errors, so the router never sees
 * them. `agent_before_settle` covers that gap: when a role's run ends in an
 * error, it benches the model that failed, omits the failed reply from context
 * (the same `context_edit` Pi's own retry uses) and asks for one continuation,
 * which routes to the next usable model. At most `maxFallbacksPerPrompt` per
 * prompt, so an outage across every rung cannot loop.
 *
 * Unlike setModel()-based fallback packages, routing never changes the
 * selection, so a fallback is never saved as the new default model. Physical
 * model selections (`/model xai/...`) are left alone.
 *
 * Chains are keyed by physical `provider/model`, modelled on omp/config.yml
 * `retry.fallbackChains`; scripts/check-model-routing.py validates their shape
 * and resolves role targets for reachability.
 */
import { existsSync, readFileSync } from "node:fs";
import { join } from "node:path";
import type { ExtensionAPI, ExtensionContext } from "@earendil-works/pi-coding-agent";
import { getAgentDir } from "@earendil-works/pi-coding-agent";

type Level = "off" | "minimal" | "low" | "medium" | "high" | "xhigh" | "max";
const LEVELS: Level[] = ["off", "minimal", "low", "medium", "high", "xhigh", "max"];
const PROVIDER = "role";
const SELECTOR = /^([a-z0-9][a-z0-9-]*)\/(.+?)(?::(off|minimal|low|medium|high|xhigh|max))?$/;
const CONTEXT_OVERFLOW = /context|too long|too many tokens|maximum.*tokens/i;

interface Config {
	roles: Record<string, string>;
	chains: Record<string, string[]>;
	cooldownMinutes: number;
	failuresBeforeFallback: number;
	maxFallbacksPerPrompt: number;
}

interface Rung {
	provider: string;
	id: string;
	level?: Level;
}

// biome-ignore lint/suspicious/noExplicitAny: Pi's Model type is generic over its API.
type AnyModel = any;

const configPath = () => join(getAgentDir(), "model-roles.json");

function loadConfig(): Config {
	const path = configPath();
	if (!existsSync(path)) throw new Error(`model-roles: ${path} is missing`);
	const raw = JSON.parse(readFileSync(path, "utf-8"));
	return {
		roles: raw.roles ?? {},
		chains: raw.chains ?? {},
		cooldownMinutes: raw.cooldownMinutes ?? 15,
		failuresBeforeFallback: raw.failuresBeforeFallback ?? 2,
		maxFallbacksPerPrompt: raw.maxFallbacksPerPrompt ?? 4,
	};
}

function parse(selector: string): Rung | undefined {
	const match = SELECTOR.exec(selector.trim());
	if (!match) return undefined;
	return { provider: match[1], id: match[2], level: match[3] as Level | undefined };
}

const keyOf = (model: { provider: string; id?: string; model?: string }) => `${model.provider}/${model.id ?? model.model}`;

export default function modelRoles(pi: ExtensionAPI) {
	let registry: AnyModel;
	let ui: ExtensionContext["ui"] | undefined;
	const benchedUntil = new Map<string, number>();
	const failures = new Map<string, number>();
	let fallbacksThisPrompt = 0;

	const notify = (message: string, type: "info" | "warning" | "error" = "warning") => {
		try {
			ui?.notify(message, type);
		} catch {
			// UI not available (print mode); the transcript still records the routed model.
		}
	};

	const isBenched = (key: string) => (benchedUntil.get(key) ?? 0) > Date.now();

	function bench(key: string, why: string, config: Config) {
		benchedUntil.set(key, Date.now() + config.cooldownMinutes * 60_000);
		failures.delete(key);
		notify(`model-roles: ${key} benched for ${config.cooldownMinutes} min (${why.slice(0, 120)})`);
	}

	function usable(model: AnyModel | undefined): boolean {
		return Boolean(model) && !isBenched(keyOf(model)) && registry?.hasConfiguredAuth(model) === true;
	}

	/** Primary first, then its chain, then each rung's own chain (OMP resolves chains by exact model). */
	function candidates(role: string, level: Level, config: Config): { model: AnyModel; level: Level }[] {
		const primary = parse(config.roles[role] ?? "");
		if (!primary) throw new Error(`model-roles: role ${role} has no valid selector`);
		const out: { model: AnyModel; level: Level }[] = [];
		const seen = new Set<string>();
		const add = (rung: Rung, fallbackLevel: Level) => {
			const key = `${rung.provider}/${rung.id}`;
			if (seen.has(key)) return;
			seen.add(key);
			const model = registry?.find(rung.provider, rung.id);
			if (model) out.push({ model, level: rung.level ?? fallbackLevel });
		};
		add({ ...primary, level: level }, level);
		const queue = [`${primary.provider}/${primary.id}`];
		for (let i = 0; i < queue.length && i < 8; i++) {
			for (const selector of config.chains[queue[i]] ?? []) {
				const rung = parse(selector);
				if (!rung) continue;
				add(rung, level);
				queue.push(`${rung.provider}/${rung.id}`);
			}
		}
		return out;
	}

	function firstUsable(role: string, level: Level, config: Config) {
		const found = candidates(role, level, config).find((c) => usable(c.model));
		if (!found) {
			throw new Error(
				`model-roles: no usable model for role/${role} (no credentials, or every rung benched; /roles reset clears the bench)`,
			);
		}
		return found;
	}

	let config: Config;
	try {
		config = loadConfig();
	} catch (error) {
		console.error(String(error));
		return;
	}

	for (const [role, selector] of Object.entries(config.roles)) {
		const primary = parse(selector);
		pi.registerVirtualModel({
			provider: PROVIDER,
			id: role,
			name: `${role} (${primary ? primary.id : "invalid"})`,
			thinkingLevels: LEVELS,
			route(request, ctx?: { modelRegistry?: AnyModel }) {
				registry = ctx?.modelRegistry ?? registry;
				const live = loadConfig();
				const level = (request.thinkingLevel as Level) ?? primary?.level ?? "medium";

				if (request.reason === "continuation" && request.previous && usable(request.previous.model)) {
					return { model: request.previous.model, thinkingLevel: request.previous.thinkingLevel ?? level };
				}

				if (request.reason === "retry" && request.failed) {
					const key = keyOf(request.failed.model);
					const count = (failures.get(key) ?? 0) + 1;
					failures.set(key, count);
					const message = request.failed.message?.errorMessage ?? "error";
					if (CONTEXT_OVERFLOW.test(message) || (count < live.failuresBeforeFallback && usable(request.failed.model))) {
						return { model: request.failed.model, thinkingLevel: request.failed.thinkingLevel ?? level };
					}
					bench(key, message, live);
				}

				const chosen = firstUsable(role, level, live);
				const primaryKey = primary ? `${primary.provider}/${primary.id}` : "";
				if (request.reason !== "direct" && keyOf(chosen.model) !== primaryKey) {
					notify(`role/${role} → ${keyOf(chosen.model)}:${chosen.level}`, "info");
				}
				return { model: chosen.model, thinkingLevel: chosen.level };
			},
		});
	}

	pi.on("session_start", async (_event, ctx) => {
		registry = ctx.modelRegistry;
		ui = ctx.ui;
	});

	pi.on("before_agent_start", async () => {
		fallbacksThisPrompt = 0;
	});

	pi.on("message_end", async (event) => {
		const message = event.message as AnyModel;
		if (message?.role === "assistant" && message.stopReason !== "error" && message.provider) {
			failures.delete(keyOf(message));
		}
	});

	// Quota, billing and auth errors are not retried by Pi, so route() never sees them.
	pi.on("agent_before_settle", async (event, ctx) => {
		if (event.outcome !== "error" || ctx.model?.provider !== PROVIDER) return;
		const live = loadConfig();
		if (fallbacksThisPrompt >= live.maxFallbacksPerPrompt) return;

		for (let i = event.context.contextEntries.length - 1; i >= 0; i--) {
			const entry = event.context.contextEntries[i];
			const failed = [...entry.messages]
				.reverse()
				.find((m: AnyModel) => m.role === "assistant" && m.stopReason === "error") as AnyModel;
			if (!failed) continue;
			const why = failed.errorMessage ?? "error";
			if (CONTEXT_OVERFLOW.test(why)) return;
			bench(keyOf(failed), why, live);
			try {
				firstUsable(ctx.model.id, (ctx.thinkingLevel as Level) ?? "medium", live);
			} catch (error) {
				notify(String(error), "error");
				return;
			}
			fallbacksThisPrompt++;
			return {
				entries: [{ type: "context_edit" as const, targetId: entry.sourceEntry.id, replacement: null }],
				continue: true,
			};
		}
	});

	pi.registerCommand("roles", {
		description: "Show model roles and their fallback state; `/roles reset` clears benched models",
		handler: async (args, ctx) => {
			registry = ctx.modelRegistry;
			if (args?.trim() === "reset") {
				benchedUntil.clear();
				failures.clear();
				ctx.ui.notify("model-roles: bench cleared", "info");
				return;
			}
			const live = loadConfig();
			const lines = Object.keys(live.roles).map((role) => {
				const chain = candidates(role, parse(live.roles[role])?.level ?? "medium", live)
					.map((c) => {
						const key = keyOf(c.model);
						const mark = isBenched(key) ? " (benched)" : registry.hasConfiguredAuth(c.model) ? "" : " (no auth)";
						return `${key}:${c.level}${mark}`;
					})
					.join(" → ");
				return `${role}: ${chain}`;
			});
			ctx.ui.notify(lines.join("\n"), "info");
		},
	});
}
