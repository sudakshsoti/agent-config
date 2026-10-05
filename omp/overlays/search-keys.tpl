# API keys for omp. Refresh after rotating a key in 1Password:
#   op inject -f -i ~/.config/omp/search-keys.tpl -o ~/.omp/.env && chmod 600 ~/.omp/.env
TAVILY_API_KEY={{ op://Homelab/Tavily - API key/credential }}
EXA_API_KEY={{ op://Homelab/Exa - API key/credential }}
FIRECRAWL_API_KEY={{ op://Homelab/Firecrawl - API key/credential }}
PARALLEL_API_KEY={{ op://Homelab/Parallel Search API Key/credential }}
OPENROUTER_API_KEY={{ op://Homelab/OpenRouter API Key - omp.sh/credential }}
# Jev compaction (claude-compact-openrouter); install.sh copies it into
# ~/.claude/settings.json as OPENROUTER_API_KEY.
JEV_OPENROUTER_API_KEY={{ op://Homelab/OpenRouter API Key - Jev/credential }}
