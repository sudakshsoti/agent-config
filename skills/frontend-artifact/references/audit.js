#!/usr/bin/env node
// audit.js — measure a rendered artifact and check it against the numeric
// thresholds in visual-qa.md. Taste rules that can be measured are measured
// here so the review does not depend on the model's eye alone.
//
//   node audit.js <url-or-file> [--width 390 --height 844] [--compact] [--json]
//
// Requires the `playwright` module. It is resolved from the normal module path,
// then from the shared Pi package tree (~/.pi/agent/npm/node_modules); pass
// NODE_PATH to point elsewhere. The module's bundled Chromium is used; set
// CHROMIUM_PATH to an installed browser executable when that build is absent.
// Nothing is downloaded. Exit code 1 when any check FAILs. WARN never fails.
//
// The page-side function `auditPage` is exported on `module.exports` and on
// `window.__artifactAudit` when this file is loaded in a browser, so the same
// measurements can be taken through `playwright-cli run-code` or a devtools
// console.

'use strict';

// ---------------------------------------------------------------- page side
function auditPage() {
  const BANNED_FAMILIES = ['inter', 'roboto', 'space grotesk', 'instrument serif', 'fraunces', 'playfair display'];
  const GENERIC = ['system-ui', '-apple-system', 'blinkmacsystemfont', 'segoe ui', 'arial', 'helvetica', 'helvetica neue', 'times', 'times new roman', 'sans-serif', 'serif', 'monospace', 'ui-sans-serif', 'ui-serif', 'ui-monospace'];
  const INTERACTIVE = 'button, [role="button"], input, select, textarea, summary, [role="dialog"], dialog, [role="menu"], [role="listbox"], [popover]';
  const EMOJI = /[\u{1F300}-\u{1FAFF}\u{2600}-\u{27BF}\u{1F1E6}-\u{1F1FF}]/u;

  const all = Array.from(document.querySelectorAll('body *'));
  const visible = (el) => {
    const r = el.getBoundingClientRect();
    const cs = getComputedStyle(el);
    return r.width > 0 && r.height > 0 && cs.visibility !== 'hidden' && cs.display !== 'none';
  };
  const firstFamily = (stack) => stack.split(',')[0].trim().replace(/^["']|["']$/g, '');

  // --- colour helpers
  const parseColor = (s) => {
    const m = s && s.match(/rgba?\(([^)]+)\)/);
    if (!m) return null;
    const p = m[1].split(/[\s,\/]+/).filter(Boolean).map(Number);
    return { r: p[0], g: p[1], b: p[2], a: p.length > 3 ? p[3] : 1 };
  };
  const lum = (c) => {
    const f = (v) => { v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); };
    return 0.2126 * f(c.r) + 0.7152 * f(c.g) + 0.0722 * f(c.b);
  };
  const contrast = (a, b) => { const [l1, l2] = [lum(a), lum(b)].sort((x, y) => y - x); return (l1 + 0.05) / (l2 + 0.05); };
  const hueOf = (c) => {
    const r = c.r / 255, g = c.g / 255, b = c.b / 255;
    const max = Math.max(r, g, b), min = Math.min(r, g, b), d = max - min;
    const sat = max === 0 ? 0 : d / max;
    if (d < 0.001) return { hue: null, sat: 0 };
    let h;
    if (max === r) h = ((g - b) / d) % 6; else if (max === g) h = (b - r) / d + 2; else h = (r - g) / d + 4;
    h = Math.round(h * 60); if (h < 0) h += 360;
    return { hue: h, sat };
  };
  const effectiveBackground = (el) => {
    let n = el;
    while (n && n !== document.documentElement) {
      const c = parseColor(getComputedStyle(n).backgroundColor);
      if (c && c.a > 0.99) return c;
      n = n.parentElement;
    }
    const root = parseColor(getComputedStyle(document.documentElement).backgroundColor);
    return root && root.a > 0 ? root : { r: 255, g: 255, b: 255, a: 1 };
  };

  // --- text sample: paragraphs and list items carry the body role
  const textEls = all.filter((el) => /^(P|LI|DD|TD|FIGCAPTION|BLOCKQUOTE)$/.test(el.tagName) && visible(el) && el.textContent.trim().length > 40);
  const sizeCounts = new Map();
  for (const el of textEls) {
    const fs = parseFloat(getComputedStyle(el).fontSize);
    sizeCounts.set(fs, (sizeCounts.get(fs) || 0) + el.textContent.length);
  }
  const bodySize = sizeCounts.size ? [...sizeCounts.entries()].sort((a, b) => b[1] - a[1])[0][0] : null;
  const bodyEls = textEls.filter((el) => parseFloat(getComputedStyle(el).fontSize) === bodySize);
  const bodyEl = bodyEls[0] || null;

  let lineHeightRatio = null, measureCh = null, bodyContrast = null, bodyFamily = null;
  if (bodyEl) {
    const cs = getComputedStyle(bodyEl);
    const lh = parseFloat(cs.lineHeight);
    lineHeightRatio = isNaN(lh) ? null : +(lh / bodySize).toFixed(2);
    bodyFamily = firstFamily(cs.fontFamily);
    const probe = document.createElement('span');
    probe.textContent = '0000000000';
    probe.style.cssText = `position:absolute;visibility:hidden;white-space:nowrap;font:${cs.font};letter-spacing:${cs.letterSpacing}`;
    document.body.appendChild(probe);
    const ch = probe.getBoundingClientRect().width / 10;
    probe.remove();
    const widest = Math.max(...bodyEls.map((el) => el.getBoundingClientRect().width));
    measureCh = ch ? Math.round(widest / ch) : null;
    const fg = parseColor(cs.color);
    if (fg) bodyContrast = +contrast(fg, effectiveBackground(bodyEl)).toFixed(2);
  }

  // --- headings
  const h1 = document.querySelector('h1');
  const h1Size = h1 && visible(h1) ? parseFloat(getComputedStyle(h1).fontSize) : null;
  const headingRatio = h1Size && bodySize ? +(h1Size / bodySize).toFixed(2) : null;

  // --- fonts. document.fonts.check() answers true when no @font-face matched at
  // all, so a stylesheet that never loaded looks fine to it. Measure instead: a
  // family that is really available changes the width of a probe string
  // against every generic fallback.
  const fontAvailable = (fam) => {
    const probe = (stack) => {
      const s = document.createElement('span');
      s.textContent = 'mmmmmmmmmmlli0123WQ';
      s.style.cssText = `position:absolute;visibility:hidden;white-space:nowrap;font-size:48px;font-family:${stack}`;
      document.body.appendChild(s);
      const w = s.getBoundingClientRect().width;
      s.remove();
      return w;
    };
    return ['monospace', 'serif', 'sans-serif'].some((g) => probe(`"${fam}", ${g}`) !== probe(g));
  };
  const declared = new Set();
  const fallbackRendering = new Set();
  const availability = new Map();
  for (const el of all) {
    if (!visible(el) || !el.textContent.trim()) continue;
    const fam = firstFamily(getComputedStyle(el).fontFamily);
    if (!fam) continue;
    declared.add(fam);
    if (GENERIC.includes(fam.toLowerCase())) continue;
    if (!availability.has(fam)) availability.set(fam, fontAvailable(fam));
    if (!availability.get(fam)) fallbackRendering.add(fam);
  }
  const families = [...declared];
  const genericPrimary = families.filter((f) => GENERIC.includes(f.toLowerCase()));
  const banned = families.filter((f) => BANNED_FAMILIES.includes(f.toLowerCase()));
  const failedFonts = [];
  document.fonts.forEach((ff) => { if (ff.status === 'error') failedFonts.push(ff.family); });

  // --- decoration counts
  const radii = new Set();
  let shadowsOnStatic = 0, gradients = 0, gradientText = 0, backdrop = 0, negativeTrackingSmall = 0, uppercaseEls = 0;
  const hues = new Map();
  for (const el of all) {
    if (!visible(el)) continue;
    const cs = getComputedStyle(el);
    const r = cs.borderTopLeftRadius;
    if (r && r !== '0px') radii.add(r);
    if (cs.boxShadow && cs.boxShadow !== 'none' && !el.matches(INTERACTIVE) && !el.closest('[role="dialog"], dialog, [popover]')) shadowsOnStatic++;
    if (/gradient\(/.test(cs.backgroundImage)) {
      gradients++;
      if ((cs.webkitBackgroundClip || cs.backgroundClip) === 'text') gradientText++;
    }
    if (cs.backdropFilter && cs.backdropFilter !== 'none') backdrop++;
    const ls = parseFloat(cs.letterSpacing);
    if (!isNaN(ls) && ls < 0 && parseFloat(cs.fontSize) < 24) negativeTrackingSmall++;
    if (cs.textTransform === 'uppercase' && el.textContent.trim()) uppercaseEls++;
    for (const prop of ['color', 'backgroundColor', 'borderTopColor']) {
      const c = parseColor(cs[prop]);
      if (!c || c.a < 0.5) continue;
      const { hue, sat } = hueOf(c);
      if (hue === null || sat < 0.25) continue;
      const bucket = Math.round(hue / 30) * 30 % 360;
      hues.set(bucket, (hues.get(bucket) || 0) + 1);
    }
  }
  // Hover rules that move things: a lift on hover is a marketing tell.
  let hoverTransforms = 0;
  for (const sheet of Array.from(document.styleSheets)) {
    let rules; try { rules = sheet.cssRules; } catch (e) { continue; }
    for (const rule of Array.from(rules)) {
      if (rule.selectorText && /:hover/.test(rule.selectorText) && rule.style && rule.style.transform && rule.style.transform !== 'none') hoverTransforms++;
    }
  }
  const emojiText = all.some((el) => el.childNodes.length && Array.from(el.childNodes).some((n) => n.nodeType === 3 && EMOJI.test(n.nodeValue)));
  const imagesMissingAlt = Array.from(document.images).filter((img) => !img.hasAttribute('alt')).length;
  const overflowX = document.documentElement.scrollWidth - document.documentElement.clientWidth;

  // --- first useful unit at the top of the page
  const candidates = all.filter((el) => visible(el) && el.matches('p, li, table, figure, form, input, button, dl, pre, canvas, svg, img, [role="list"], [role="table"]') && !el.closest('nav'));
  const firstUseful = candidates.length ? Math.round(Math.min(...candidates.map((el) => el.getBoundingClientRect().top + window.scrollY))) : null;

  return {
    viewport: { width: innerWidth, height: innerHeight },
    fonts: { families, bodyFamily, genericPrimary, banned, fallbackRendering: [...fallbackRendering], failedFonts, loaded: document.fonts.size },
    body: { sizePx: bodySize, lineHeightRatio, measureCh, contrast: bodyContrast },
    headings: { h1Px: h1Size, h1ToBody: headingRatio },
    decoration: { distinctRadii: [...radii], shadowsOnStatic, gradients, gradientText, backdrop, hoverTransforms, negativeTrackingSmall, uppercaseEls, accentHues: [...hues.keys()].sort((a, b) => a - b), emojiText },
    layout: { overflowX, firstUsefulTopPx: firstUseful, imagesMissingAlt },
  };
}

// ---------------------------------------------------------------- checks
function evaluate(m, opts) {
  const out = [];
  const add = (level, name, value, limit) => out.push({ level, name, value, limit });
  const compact = !!opts.compact, display = !!opts.display;
  const wide = m.viewport.width >= 700;
  const { fonts, body, headings, decoration, layout } = m;

  if (fonts.failedFonts.length) add('FAIL', 'webfont failed to load', fonts.failedFonts.join(', '), 'none');
  if (fonts.fallbackRendering.length) add('FAIL', 'declared family rendering a fallback', fonts.fallbackRendering.join(', '), 'none');
  if (fonts.genericPrimary.length) add('FAIL', 'generic or system family used as primary', fonts.genericPrimary.join(', '), 'a named face');
  if (fonts.banned.length) add('FAIL', 'family on the automatic-choice ban list', fonts.banned.join(', '), 'none');
  const named = fonts.families.filter((f) => !fonts.genericPrimary.includes(f));
  add(named.length > 3 ? 'FAIL' : named.length > 2 ? 'WARN' : 'PASS', 'font families in use', named.join(', ') || 'none', '≤ 2, third only for code');

  if (body.sizePx == null) add('WARN', 'body text not found', 'no paragraph or list text over 40 chars', 'body role required');
  else {
    const min = compact ? 14 : 16;
    add(body.sizePx < min || body.sizePx > 20 ? 'FAIL' : 'PASS', 'body size px', body.sizePx, `${min}–20`);
    if (body.lineHeightRatio != null) add(body.lineHeightRatio < 1.3 || body.lineHeightRatio > 1.7 ? 'FAIL' : body.lineHeightRatio < 1.4 || body.lineHeightRatio > 1.6 ? 'WARN' : 'PASS', 'body line-height ratio', body.lineHeightRatio, '1.4–1.6');
    // Measure is a wide-viewport question; a phone bounds it by itself.
    if (body.measureCh != null && !compact && wide) add(body.measureCh > 90 || body.measureCh < 30 ? 'FAIL' : body.measureCh > 75 || body.measureCh < 40 ? 'WARN' : 'PASS', 'widest body measure ch', body.measureCh, '40–75');
    if (body.contrast != null) add(body.contrast < 4.5 ? 'FAIL' : body.contrast < 7 ? 'WARN' : 'PASS', 'body text contrast', body.contrast, '≥ 4.5 (7 preferred)');
  }
  if (headings.h1ToBody != null) {
    const max = compact ? 1.6 : display ? 7 : 3.2;
    add(headings.h1ToBody > max + 0.6 ? 'FAIL' : headings.h1ToBody > max ? 'WARN' : 'PASS', 'h1 to body size ratio', headings.h1ToBody, `≤ ${max}${display ? ' (display)' : ''}`);
  }

  add(decoration.distinctRadii.length > 3 ? 'FAIL' : 'PASS', 'distinct border radii', decoration.distinctRadii.join(' ') || 'none', '≤ 3');
  add(decoration.shadowsOnStatic > 0 ? 'FAIL' : 'PASS', 'shadows on non-interactive elements', decoration.shadowsOnStatic, '0');
  add(decoration.gradientText > 0 ? 'FAIL' : decoration.gradients > 0 ? 'WARN' : 'PASS', 'gradients', `${decoration.gradients} (${decoration.gradientText} on text)`, '0');
  add(decoration.backdrop > 0 ? 'FAIL' : 'PASS', 'backdrop-filter', decoration.backdrop, '0');
  add(decoration.hoverTransforms > 0 ? 'FAIL' : 'PASS', 'hover rules that transform', decoration.hoverTransforms, '0');
  add(decoration.negativeTrackingSmall > 0 ? 'FAIL' : 'PASS', 'negative tracking below 24px', decoration.negativeTrackingSmall, '0');
  add(decoration.uppercaseEls > 12 ? 'WARN' : 'PASS', 'uppercase elements', decoration.uppercaseEls, '≤ 12');
  add(decoration.accentHues.length > 3 ? 'FAIL' : decoration.accentHues.length > 2 ? 'WARN' : 'PASS', 'saturated hue buckets', decoration.accentHues.join('° ') + (decoration.accentHues.length ? '°' : 'none'), '≤ 2 unless data needs more');
  if (decoration.emojiText) add('WARN', 'emoji in text', 'present', 'use SVG or words');

  add(layout.overflowX > 0 ? 'FAIL' : 'PASS', 'horizontal overflow px', layout.overflowX, '0');
  add(layout.imagesMissingAlt > 0 ? 'FAIL' : 'PASS', 'images without alt attribute', layout.imagesMissingAlt, '0');
  if (layout.firstUsefulTopPx != null && m.viewport.width <= 500) {
    const limit = Math.round(m.viewport.height * 0.4);
    add(layout.firstUsefulTopPx > limit ? (compact ? 'FAIL' : 'WARN') : 'PASS', 'first useful unit top px (narrow)', layout.firstUsefulTopPx, `≤ ${limit}`);
  }
  return out;
}

// ---------------------------------------------------------------- node side
async function main() {
  const args = process.argv.slice(2);
  const target = args.find((a) => !a.startsWith('--'));
  if (!target) { console.error('usage: node audit.js <url-or-file> [--width N --height N] [--compact | --display] [--json]'); process.exit(2); }
  const opt = (name, def) => { const i = args.indexOf(name); return i > -1 ? args[i + 1] : def; };
  const width = +opt('--width', 390), height = +opt('--height', 844);
  const compact = args.includes('--compact'), display = args.includes('--display'), json = args.includes('--json');

  let playwright;
  const os = require('os'), path = require('path');
  const candidates = ['playwright', path.join(os.homedir(), '.pi/agent/npm/node_modules/playwright'), path.join(os.homedir(), '.pi/agent/npm/node_modules/playwright-core')];
  for (const c of candidates) { try { playwright = require(c); break; } catch (e) { /* next */ } }
  if (!playwright) { console.error('playwright module not found; set NODE_PATH to a directory containing it'); process.exit(2); }

  const url = /^https?:\/\//.test(target) || target.startsWith('file:') ? target : 'file://' + path.resolve(target);
  // CHROMIUM_PATH points at an already-installed browser when the module's own build is absent.
  const launch = {};
  if (process.env.CHROMIUM_PATH) launch.executablePath = process.env.CHROMIUM_PATH;
  const proxy = process.env.HTTPS_PROXY || process.env.https_proxy;
  if (proxy) launch.proxy = { server: proxy }; // the same proxy curl and npm use
  const browser = await playwright.chromium.launch(launch);
  const page = await browser.newPage({ viewport: { width, height } });
  const consoleErrors = [], failedRequests = [];
  page.on('console', (msg) => { if (msg.type() === 'error') consoleErrors.push(msg.text()); });
  page.on('pageerror', (err) => consoleErrors.push(String(err)));
  page.on('requestfailed', (req) => failedRequests.push(`${req.url()} (${(req.failure() || {}).errorText || 'failed'})`));
  page.on('response', (res) => { if (res.status() >= 400) failedRequests.push(`${res.url()} (HTTP ${res.status()})`); });
  await page.goto(url, { waitUntil: 'networkidle' });
  await page.evaluate(() => document.fonts.ready);
  const metrics = await page.evaluate(auditPage);
  await browser.close();

  metrics.consoleErrors = consoleErrors;
  metrics.failedRequests = failedRequests;
  const checks = evaluate(metrics, { compact, display });
  if (failedRequests.length) checks.push({ level: 'FAIL', name: 'requests that failed', value: failedRequests.join('; '), limit: 'none' });
  const otherErrors = consoleErrors.filter((e) => !/Failed to load resource/.test(e));
  if (otherErrors.length) checks.push({ level: 'FAIL', name: 'console errors', value: otherErrors.join('; '), limit: 'none' });

  if (json) console.log(JSON.stringify({ url, metrics, checks }, null, 2));
  else {
    console.log(`audit ${url} at ${width}×${height}${compact ? ' (compact)' : display ? ' (display)' : ''}`);
    for (const c of checks) console.log(`${c.level.padEnd(4)} ${c.name}: ${c.value} (limit ${c.limit})`);
    const fails = checks.filter((c) => c.level === 'FAIL').length, warns = checks.filter((c) => c.level === 'WARN').length;
    console.log(`${fails} FAIL, ${warns} WARN`);
  }
  process.exit(checks.some((c) => c.level === 'FAIL') ? 1 : 0);
}

if (typeof window !== 'undefined') window.__artifactAudit = auditPage;
if (typeof module !== 'undefined') { module.exports = { auditPage, evaluate }; if (require.main === module) main().catch((e) => { console.error(e); process.exit(2); }); }
