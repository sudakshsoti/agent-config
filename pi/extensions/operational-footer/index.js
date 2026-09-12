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
  const insideHome =
    fromHome === "" || (fromHome !== ".." && !fromHome.startsWith(`..${sep}`));
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
  if (!right) return truncateToWidth(left, width, "");

  const fittedRight = truncateToWidth(right, width, "");
  const leftWidth = Math.max(1, width - visibleWidth(fittedRight) - 1);
  const fittedLeft = truncateToWidth(left, leftWidth, "");
  const gap = Math.max(
    1,
    width - visibleWidth(fittedLeft) - visibleWidth(fittedRight),
  );
  return truncateToWidth(
    `${fittedLeft}${" ".repeat(gap)}${fittedRight}`,
    width,
    "",
  );
}

function plain(value) {
  return (value || "").replace(ANSI_PATTERN, "").trim();
}

function truncateMiddle(value, width) {
  if (visibleWidth(value) <= width) return value;
  if (width <= 1) return value.slice(0, width);

  const remaining = width - 1;
  const head = Math.ceil(remaining / 2);
  const tail = Math.floor(remaining / 2);
  return `${value.slice(0, head)}…${tail > 0 ? value.slice(-tail) : ""}`;
}

function joinSegments(segments, separator) {
  return segments.filter(Boolean).join(separator);
}

function packSegments(segments, width, separator) {
  const packed = [];
  for (const segment of segments) {
    const candidate = joinSegments([...packed, segment], separator);
    if (visibleWidth(candidate) <= width) packed.push(segment);
  }
  return packed;
}

function formatLspAlert(value, width, theme) {
  const text = plain(value);
  const failedPart = text.match(/LSP Failed:\s*(.+?)(?:\s+·|$)/i)?.[1];
  if (!failedPart) return undefined;

  const names = failedPart
    .split(",")
    .map((name) => name.trim())
    .filter(Boolean);
  if (names.length === 0) return undefined;

  const limit = width < 96 ? 1 : 2;
  const shown = names.slice(0, limit).join(", ");
  const remainder = names.length > limit ? ` +${names.length - limit}` : "";
  const label = width < 96 ? "LSP !" : "LSP failed:";
  const alert = `${label} ${shown}${remainder}`;
  return theme.fg("error", alert);
}

function formatMcpAlert(value, authValue, width, theme) {
  const text = plain(value);
  const authText = plain(authValue);
  if (!text && !authText) return undefined;

  if (
    authText ||
    /needs auth|authentication required|auth required|authenticating/i.test(
      text,
    )
  ) {
    return theme.fg("warning", width < 96 ? "MCP auth" : "MCP authentication");
  }

  if (!/failed|error|unavailable|disconnected|connection lost/i.test(text)) {
    return undefined;
  }

  const server = text.match(
    /failed to (?:connect|initialize)(?: to)?\s+([^(:\s]+)/i,
  )?.[1];
  const label = width < 96 ? "MCP !" : "MCP failed:";
  return theme.fg("error", `${label}${server ? ` ${server}` : ""}`);
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
            cost: {
              input: 0,
              output: 0,
              cacheRead: 0,
              cacheWrite: 0,
              total: 0,
            },
          };
          let cacheHit;

          for (const entry of ctx.sessionManager.getEntries()) {
            if (
              entry.type === "message" &&
              entry.message.role === "assistant"
            ) {
              const messageUsage = entry.message.usage;
              addUsage(usage, messageUsage);
              const prompt =
                messageUsage.input +
                messageUsage.cacheRead +
                messageUsage.cacheWrite;
              cacheHit =
                prompt > 0
                  ? (messageUsage.cacheRead / prompt) * 100
                  : undefined;
            } else if (
              entry.type === "message" &&
              entry.message.role === "toolResult"
            ) {
              addUsage(usage, entry.message.usage);
            } else if (
              entry.type === "branch_summary" ||
              entry.type === "compaction"
            ) {
              addUsage(usage, entry.usage);
            }
          }

          const statuses = footerData.getExtensionStatuses();
          const speed = plain(statuses.get("tokenSpeed")).replace(
            /^⚡\s*TPS:\s*/i,
            "",
          );
          const lspAlert = formatLspAlert(
            statuses.get("pi-lens-lsp"),
            width,
            theme,
          );
          const mcpAlert = formatMcpAlert(
            statuses.get("mcp"),
            statuses.get("mcp-auth"),
            width,
            theme,
          );
          const extras = [...statuses.entries()]
            .filter(
              ([key, value]) =>
                ![
                  "tokenSpeed",
                  "pi-lens-lsp",
                  "mcp",
                  "mcp-auth",
                  "kohra-thinking",
                ].includes(key) && plain(value),
            )
            .map(([, value]) => plain(value));

          const branch = footerData.getGitBranch();
          const location = `${compactPath(ctx.cwd)}${branch ? ` (${branch})` : ""}`;
          const model = ctx.model?.id || "no model";
          const thinking = ctx.thinkingLevel || "off";
          const state = `${model} ${theme.fg("dim", "·")} ${thinking}`;
          const locationWidth = Math.max(1, width - visibleWidth(state) - 1);
          const context = ctx.getContextUsage();
          const contextText =
            context?.percent == null
              ? `context ? / ${formatCount(context?.contextWindow || ctx.model?.contextWindow || 0)}`
              : `context ${context.percent.toFixed(1)}% / ${formatCount(context.contextWindow)}`;

          const separator = theme.fg("dim", " · ");
          const health = [lspAlert, mcpAlert].filter(Boolean);
          const segments = [
            theme.fg("text", contextText),
            ...health,
            ...extras.map((value) => theme.fg("dim", value)),
            health.length === 0 && speed && speed !== "--"
              ? theme.fg("dim", speed)
              : undefined,
          ].filter(Boolean);
          const accounting = [
            cacheHit === undefined
              ? undefined
              : `cache ${cacheHit.toFixed(1)}%`,
            usage.input ? `↑${formatCount(usage.input)}` : undefined,
            usage.output ? `↓${formatCount(usage.output)}` : undefined,
            usage.cacheRead ? `R${formatCount(usage.cacheRead)}` : undefined,
            usage.cost.total ? `$${usage.cost.total.toFixed(3)}` : undefined,
          ]
            .filter(Boolean)
            .join(" ");

          const accountingText = accounting
            ? theme.fg("dim", accounting)
            : undefined;
          const right = health.length === 0 ? accountingText : undefined;
          const availableWidth = right
            ? Math.max(1, width - visibleWidth(right) - visibleWidth(separator))
            : width;
          const packed = packSegments(segments, availableWidth, separator);

          const rowOne = fit(
            theme.fg("muted", truncateMiddle(location, locationWidth)),
            state,
            width,
          );
          const rowTwo = fit(joinSegments(packed, separator), right, width);

          return [rowOne, rowTwo];
        },
      };
    });
  });
}
