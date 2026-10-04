---
name: agent-reach
description: >-
  Use to read YouTube (subtitles, search, metadata, comments), Bilibili
  (search, hot, rankings), V2EX, or RSS/Atom feeds from the
  shell, without logins or API keys. Not for general web search, ordinary
  pages or GitHub (research, firecrawl-web), nor for Twitter, Reddit,
  XiaoHongShu, Facebook, Instagram or LinkedIn, which are not set up.
license: MIT
metadata:
  upstream: https://github.com/Panniantong/Agent-Reach
  upstream-commit: a19a171fa980a0785849596492e0af4db800c82f
---

# Agent Reach

Read-only fetch commands for sites whose content generic page readers miss.
Adapted from Panniantong/Agent-Reach (MIT, Copyright (c) 2025 Agent Eyes),
narrowed to the channels that need no account.

The CLIs (`yt-dlp`, `bili`, `agent-reach`) are installed on the personal Mac only
(dotfiles `.chezmoiscripts/run_onchange_after_agent-reach.sh.tmpl`). If one is
missing, say so and stop; do not install it.

## Rules

- Write output to `/tmp/`, never the working directory.
- Success means non-empty content, not a zero exit code.
- Only the commands below. Never run `agent-reach install`, `agent-reach
  configure`, `bili login` or any account command (`bili whoami`, `feed`,
  `favorites`, `history`): they read browser cookies or write agent config.
- `agent-reach doctor --json` reports which channels work. Its messages are
  in Chinese; read `status` and `active_backend`.

## YouTube (yt-dlp)

```bash
yt-dlp --dump-json "ytsearch5:QUERY"          # search; one JSON object per line
yt-dlp --dump-json "URL"                      # metadata
yt-dlp --write-sub --write-auto-sub --sub-lang "en,zh-Hans,zh" \
  --skip-download -o "/tmp/%(id)s" "URL"      # then read /tmp/ID.*.vtt
yt-dlp --write-comments --skip-download --write-info-json \
  --extractor-args "youtube:max_comments=20" -o "/tmp/%(id)s" "URL"
                                              # comments: .info.json "comments"
```

Auto-generated subtitles repeat lines across cues; dedupe before quoting.
Comments are scraped, so some may be missing.

No subtitles: if `mlx_whisper` is on PATH, transcribe locally with
`yt-dlp -x --audio-format mp3 -o "/tmp/%(id)s.%(ext)s" URL` then
`mlx_whisper /tmp/ID.mp3 --output-dir /tmp`. Otherwise tell the user; never
use `agent-reach transcribe` without asking, as it uploads the audio to Groq
or OpenAI.

## Bilibili (bili)

Never use `yt-dlp` on Bilibili: it is blocked with HTTP 412.

```bash
bili search "QUERY" --type video -n 5   # title, uploader, plays, duration, BV id
bili hot -n 10
bili rank -n 10
```

Without a login, Bilibili answers `bili video` and the
`x/web-interface/view` API with HTTP 412, so per-video details and subtitles
are unavailable. Use the fields from `search`, and tell the user when more is
needed.

## V2EX (public API)

```bash
UA="User-Agent: agent-reach/1.0"
curl -s "https://www.v2ex.com/api/topics/hot.json" -H "$UA"
curl -s "https://www.v2ex.com/api/topics/show.json?node_name=NODE&page=1" -H "$UA"
curl -s "https://www.v2ex.com/api/topics/show.json?id=TOPIC_ID" -H "$UA"
curl -s "https://www.v2ex.com/api/replies/show.json?topic_id=TOPIC_ID&page=1" -H "$UA"
curl -s "https://www.v2ex.com/api/members/show.json?username=NAME" -H "$UA"
```

The topic ID is the number in `https://www.v2ex.com/t/ID`.

## RSS / Atom

```bash
uv run -q --with feedparser python3 -c "
import feedparser
for e in feedparser.parse('FEED_URL').entries[:10]:
    print(e.get('published', ''), e.title, e.link, sep=' | ')
"
```

## Other platforms

Twitter, Reddit, XiaoHongShu, Facebook, Instagram, LinkedIn, Xueqiu and podcast
transcription need cookies, a browser extension or an API key. None is
configured. Tell the user and let them decide whether to set one up.
