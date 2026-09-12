---
name: research
description: "Use when a question needs investigation against high-trust primary sources, official documentation, specifications, or first-party APIs, with findings captured in a cited Markdown file. It delegates research and records evidence; use firecrawl-web for Firecrawl retrieval without the repository write-up."
---

Spin up the harness's **named research role** in the background to do the research, so you keep working while it reads. Do not use an unnamed or generic child. In Pi, use `subagent_type: research`; in Codex, use `agent_type: docs_researcher`. Keep the child in the background and do not override the role's model or reasoning level: each harness has a deliberate lower-cost research route.

Its job:

1. Investigate the question against **primary sources** (official docs, source code, specs, first-party APIs), not a secondary write-up of them. Follow every claim back to the source that owns it.
2. Write the findings to a single Markdown file, citing each claim's source.
3. Save it where the repo already keeps such notes; match the existing convention, and if there is none, put it somewhere sensible and say where.
