#!/usr/bin/env node
// Screenshot a URL at several widths, in one or both colour schemes.
// Copy into a project on first use; it must resolve the project's playwright.
//   node scripts/shoot.mjs http://127.0.0.1:5173 390 900 1440 --theme both
// Requires: pnpm add -D playwright && pnpm exec playwright install chromium
//
// --theme dark|light|both (default both). Writes PNGs to $CLAUDE_SCRATCHPAD if
// set, else ./.shots, named <stamp>-<width>-<scheme>.png, and prints the paths.

import { mkdirSync } from "node:fs";
import { join, resolve } from "node:path";

const args = process.argv.slice(2);
const themeIdx = args.indexOf("--theme");
let theme = "both";
if (themeIdx !== -1) {
  theme = args[themeIdx + 1] ?? "";
  args.splice(themeIdx, 2);
}
if (!["dark", "light", "both"].includes(theme)) {
  console.error("--theme must be dark, light or both");
  process.exit(1);
}
const schemes = theme === "both" ? ["light", "dark"] : [theme];

const [url, ...widthArgs] = args;

if (!url) {
  console.error(
    "usage: node shoot.mjs <url> [width ...] [--theme dark|light|both]  (default 390 900 1440, both)",
  );
  process.exit(1);
}

const widths = (widthArgs.length ? widthArgs : ["390", "900", "1440"]).map(Number);
if (widths.some((w) => !Number.isFinite(w) || w < 200)) {
  console.error("widths must be numbers of at least 200");
  process.exit(1);
}

let chromium;
try {
  ({ chromium } = await import("playwright"));
} catch {
  console.error(
    "BLOCKED: playwright is not installed in this project.\n" +
      "  fix: pnpm add -D playwright && pnpm exec playwright install chromium",
  );
  process.exit(2);
}

const outDir = resolve(process.env.CLAUDE_SCRATCHPAD ?? ".shots");
mkdirSync(outDir, { recursive: true });

const browser = await chromium.launch();
const stamp = new Date().toISOString().replace(/[:.]/g, "-").slice(0, 19);

try {
  for (const width of widths) {
    for (const colorScheme of schemes) {
      const context = await browser.newContext({
        viewport: { width, height: Math.round(width * 0.75) },
        deviceScaleFactor: 2,
        colorScheme,
      });
      const page = await context.newPage();
      try {
        await page.goto(url, { waitUntil: "networkidle", timeout: 30_000 });
      } catch (err) {
        console.error(
          `BLOCKED: could not load ${url} (${err.message.split("\n")[0]}).\n` +
            "  fix: start the dev server and pass its real port",
        );
        process.exit(3);
      }
      // Let webfonts settle so the capture shows the real metrics.
      await page.evaluate(() => document.fonts.ready);
      const path = join(outDir, `${stamp}-${width}-${colorScheme}.png`);
      await page.screenshot({ path, fullPage: true });
      await context.close();
      console.log(path);
    }
  }
} finally {
  await browser.close();
}
