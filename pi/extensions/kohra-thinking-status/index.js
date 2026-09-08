const LEVELS = {
  off: { label: "off", colour: "#828689" },
  minimal: { label: "min", colour: "#9A9EA1" },
  low: { label: "low", colour: "#78ACCF" },
  medium: { label: "med", colour: "#70B4A2" },
  high: { label: "high", colour: "#D598C0" },
  xhigh: { label: "xhigh", colour: "#D2A56D" },
  max: { label: "max", colour: "#E19796" },
};

function setThinkingStatus(ctx, level) {
  const item = LEVELS[level] ?? LEVELS.off;
  const hex = item.colour.slice(1);
  const red = Number.parseInt(hex.slice(0, 2), 16);
  const green = Number.parseInt(hex.slice(2, 4), 16);
  const blue = Number.parseInt(hex.slice(4, 6), 16);
  ctx.ui.setStatus(
    "kohra-thinking",
    `\u001b[38;2;${red};${green};${blue}mthink:${item.label}\u001b[0m`,
  );
}

export default function (pi) {
  pi.on("session_start", (_event, ctx) => {
    setThinkingStatus(ctx, ctx.thinkingLevel);
  });

  pi.on("thinking_level_select", (event, ctx) => {
    setThinkingStatus(ctx, event.level);
  });

  pi.on("session_shutdown", (_event, ctx) => {
    ctx.ui.setStatus("kohra-thinking", undefined);
  });
}
