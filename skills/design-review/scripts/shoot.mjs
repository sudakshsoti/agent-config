#!/usr/bin/env node
// Screenshot a URL at several widths. Copy into a project on first use.
//   node scripts/shoot.mjs http://127.0.0.1:8000 390 900 1440
// Requires: pnpm add -D playwright && pnpm exec playwright install chromium
//
// Writes PNGs to $CLAUDE_SCRATCHPAD if set, else ./.shots, and prints the paths.

import { mkdirSync } from "node:fs";
import { join, resolve } from "node:path";
import { chromium } from "playwright";

const [url, ...widthArgs] = process.argv.slice(2);

if (!url) {
  console.error("usage: node shoot.mjs <url> [width ...]  (default 390 900 1440)");
  process.exit(1);
}

const widths = (widthArgs.length ? widthArgs : ["390", "900", "1440"]).map(Number);
if (widths.some((w) => !Number.isFinite(w) || w < 200)) {
  console.error("widths must be numbers of at least 200");
  process.exit(1);
}

const outDir = resolve(process.env.CLAUDE_SCRATCHPAD ?? ".shots");
mkdirSync(outDir, { recursive: true });

const browser = await chromium.launch();
const stamp = new Date().toISOString().replace(/[:.]/g, "-").slice(0, 19);

try {
  for (const width of widths) {
    const context = await browser.newContext({
      viewport: { width, height: Math.round(width * 0.75) },
      deviceScaleFactor: 2,
      colorScheme: "dark",
    });
    const page = await context.newPage();
    await page.goto(url, { waitUntil: "networkidle", timeout: 30_000 });
    // Let webfonts settle so the capture shows the real metrics.
    await page.evaluate(() => document.fonts.ready);
    const path = join(outDir, `${stamp}-${width}.png`);
    await page.screenshot({ path, fullPage: true });
    await context.close();
    console.log(path);
  }
} finally {
  await browser.close();
}
