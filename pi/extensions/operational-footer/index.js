import { truncateToWidth, visibleWidth } from "@earendil-works/pi-tui";
import { relative, resolve, sep } from "node:path";

const ANSI_PATTERN = /\x1b\[[0-9;]*m/g;

function formatCount(count) {
  if (count < 1_000) return `${count}`;
  if (count < 10_000) return `${(count / 1_000).toFixed(1)}k`;
  if (count < 1_000_000) return `${Math.round(count / 1_000)}k`;
  if (count < 10_000_000) return `${(count / 1_000_000).toFixed(1)}M`;
  return `${Math.round(count / 1_000_000)}M`;
}

function compactPath(cwd) {
  const home = process.env.HOME;
  if (!home) return cwd;
  const fromHome = relative(resolve(home), resolve(cwd));
  const insideHome = fromHome === "" || (fromHome !== ".." && !fromHome.startsWith(`..${sep}`));
  return insideHome ? (fromHome ? `~${sep}${fromHome}` : "~") : cwd;
}

function addUsage(total, usage) {
  if (!usage) return;
  total.input += usage.input || 0;
  total.output += usage.output || 0;
  total.cacheRead += usage.cacheRead || 0;
  total.cacheWrite += usage.cacheWrite || 0;
  total.reasoning += usage.reasoning || 0;
  total.totalTokens += usage.totalTokens || 0;
  total.cost.input += usage.cost?.input || 0;
  total.cost.output += usage.cost?.output || 0;
  total.cost.cacheRead += usage.cost?.cacheRead || 0;
  total.cost.cacheWrite += usage.cost?.cacheWrite || 0;
  total.cost.total += usage.cost?.total || 0;
}

function fit(left, right, width) {
  const gap = Math.max(2, width - visibleWidth(left) - visibleWidth(right));
  return truncateToWidth(`${left}${" ".repeat(gap)}${right}`, width, "");
}

function plain(value) {
  return (value || "").replace(ANSI_PATTERN, "").trim();
}

export default function operationalFooter(pi) {
  pi.on("session_start", (_event, ctx) => {
    ctx.ui.setFooter((tui, theme, footerData) => {
      const unsubscribe = footerData.onBranchChange(() => tui.requestRender());

      return {
        dispose: unsubscribe,
        invalidate() {},
        render(width) {
          const usage = {
            input: 0,
            output: 0,
            cacheRead: 0,
            cacheWrite: 0,
            reasoning: 0,
            totalTokens: 0,
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0, total: 0 },
          };
          let cacheHit;

          for (const entry of ctx.sessionManager.getEntries()) {
            if (entry.type === "message" && entry.message.role === "assistant") {
              const messageUsage = entry.message.usage;
              addUsage(usage, messageUsage);
              const prompt = messageUsage.input + messageUsage.cacheRead + messageUsage.cacheWrite;
              cacheHit = prompt > 0 ? (messageUsage.cacheRead / prompt) * 100 : undefined;
            } else if (entry.type === "message" && entry.message.role === "toolResult") {
              addUsage(usage, entry.message.usage);
            } else if (entry.type === "branch_summary" || entry.type === "compaction") {
              addUsage(usage, entry.usage);
            }
          }

          const statuses = footerData.getExtensionStatuses();
          const mode = plain(statuses.get("pi-plan-build-mode")) || "build";
          const speed = plain(statuses.get("tokenSpeed")).replace(/^⚡\s*TPS:\s*/i, "");
          const lsp = plain(statuses.get("pi-lens-lsp"));
          const extras = [...statuses.entries()]
            .filter(([key, value]) => !["pi-plan-build-mode", "tokenSpeed", "pi-lens-lsp", "kohra-thinking"].includes(key) && plain(value))
            .map(([, value]) => plain(value));

          const branch = footerData.getGitBranch();
          const location = `${compactPath(ctx.cwd)}${branch ? ` (${branch})` : ""}`;
          const model = ctx.model?.id || "no model";
          const thinking = ctx.thinkingLevel || "off";
          const context = ctx.getContextUsage();
          const contextText = context?.percent == null
            ? `context ? / ${formatCount(context?.contextWindow || ctx.model?.contextWindow || 0)}`
            : `context ${context.percent.toFixed(1)}% / ${formatCount(context.contextWindow)}`;

          const operational = [contextText, speed && speed !== "--" ? speed : undefined, lsp && lsp !== "LSP Inactive" ? lsp : undefined, ...extras]
            .filter(Boolean)
            .join(theme.fg("dim", " · "));
          const accounting = [
            cacheHit === undefined ? undefined : `cache ${cacheHit.toFixed(1)}%`,
            usage.input ? `↑${formatCount(usage.input)}` : undefined,
            usage.output ? `↓${formatCount(usage.output)}` : undefined,
            usage.cacheRead ? `R${formatCount(usage.cacheRead)}` : undefined,
            usage.cost.total ? `$${usage.cost.total.toFixed(3)}` : undefined,
          ].filter(Boolean).join(" ");

          const state = `${theme.bold(mode.toUpperCase())} ${theme.fg("dim", "·")} ${model} ${theme.fg("dim", "·")} ${thinking}`;
          const rowOne = fit(theme.fg("muted", location), state, width);
          const rowTwo = fit(theme.fg("text", operational), theme.fg("dim", accounting), width);

          if (width >= 96) return [rowOne, rowTwo];
          return [truncateToWidth(rowOne, width, ""), truncateToWidth(operational, width, ""), truncateToWidth(theme.fg("dim", accounting), width, "")];
        },
      };
    });
  });
}
