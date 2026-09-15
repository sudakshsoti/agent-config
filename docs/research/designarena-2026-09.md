# DesignArena (designarena.ai) — Text-to-HTML boards, read 2026-09-16

Source: https://www.designarena.ai/leaderboard/code (JS-rendered; scraped via headless Chromium accessibility tree on 2026-09-16). Scores are pairwise-preference Elo on single-shot text→HTML generations judged visually by voters. Not agentic: no tools, no repository context, no AGENTS.md, no multi-turn.

Only models routed or candidate in this repo are listed; rank is position in the full board (ties share a rank).

## Overall Frontend (Text-to-HTML), top of board

1. Kimi K3 1388 · 2. Muse Spark 1.3 Max 1373 · 3. GPT-6 Astra (xhigh) 1369 · 4. Muse Spark 1.3 (xhigh) 1365 · 5. GPT-5.6 Sol (xhigh) 1352 · 6. Claude Fable 5.1 1346 · 7. DeepSeek-V4.1-Flash 1341 · 8. Claude Opus 5 1338 · 9. GPT-5.6 Sol (Medium) 1334 · 10. GLM-5.3 1330 · 11. Muse Spark 1.2 1327. GPT-5.6 Terra and GPT-5.6 Luna are outside the top 20. GLM-5.3-Flash not in the top 20.

## Task-specific boards

| Model | General Purpose | Landing Page | Dashboard | Productivity | UI Components |
| --- | --- | --- | --- | --- | --- |
| Muse Spark 1.3 (xhigh) | 3 (1344) | 1 (1376) | 1 (1354) | 3 (1322) | 2 (1390) |
| Muse Spark 1.3 Max | 1 (1354) | 3 (1369) | 2 (1353) | 2 (1333) | 3 (1379) |
| GPT-6 Astra (xhigh) | — | — | — | — | 1 (1402) |
| GPT-5.6 Sol (xhigh) | 21 (1290) | 5 (1346) | 8 (1321) | 1 (1348) | 7 (1343) |
| GPT-5.6 Sol (Medium) | 9 (1313) | 8 (1332) | 8 (1321) | 10 (1298) | 9 (1342) |
| GPT-5.6 Terra | 30 (1271) | 21 (1298) | 13 (1309) | 28 (1273) | 37 (1274) |
| GPT-5.6 Luna | 48 (1242) | 34 (1285) | 18 (1297) | 40 (1255) | 35 (1276) |
| Kimi K3 | 4 (1336) | 2 (1371) | 33 (1273) | 10 (1298) | 4 (1369) |
| DeepSeek-V4.1-Flash | 5 (1330) | 17 (1303) | 17 (1299) | 6 (1308) | 14 (1328) |
| GLM-5.3 (not Flash) | 12 (1308) | 4 (1355) | 31 (1279) | 28 (1273) | 7 (1343) |
| GLM-5.3-Flash | 18 (1297) | 13 (1316) | 40 (1263) | 48 (1245) | 11 (1339) |
| Muse Spark 1.2 | 11 (1311) | 9 (1325) | 4 (1328) | 17 (1294) | 15 (1325) |
| DeepSeek-V4-Flash-0731 | 46 (1243) | 58 (1239) | 63 (1224) | 67 (1216) | 46 (1252) |

"—" = not listed on that board. GPT-6 Astra appears only on UI Components among the boards read; no Astra entry at `low` effort anywhere.

## Reading

- Sol at Medium is within ~10 Elo of Sol at xhigh on four of five boards and ahead on General Purpose; xhigh buys little here.
- Luna and Terra are the two weakest OpenAI entries on every board; Luna is 60–110 Elo below Sol Medium.
- Muse Spark 1.3 leads only at xhigh/Max; no lower-effort Muse entry is listed, so the boards say nothing about Muse at `minimal`/`low`/`high`.
- "Overall Preference vs Speed" chart places Terra and Luna on the fast/low-preference side with the Flash models.

## Limits

Single-shot visual preference on generated HTML. Does not measure tool use, repository grounding, instruction adherence, multi-turn editing or agentic reliability, which dominate harness experience. Voter population and prompt distribution are DesignArena's; Elo across categories is not directly comparable.
