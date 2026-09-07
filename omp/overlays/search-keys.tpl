# API keys for omp. Refresh after rotating a key in 1Password:
#   op inject -f -i ~/.config/omp/search-keys.tpl -o ~/.omp/.env && chmod 600 ~/.omp/.env
TAVILY_API_KEY={{ op://Homelab/Tavily - API key/credential }}
EXA_API_KEY={{ op://Homelab/Exa - API key/credential }}
FIRECRAWL_API_KEY={{ op://Homelab/Firecrawl - API key/credential }}
OPENROUTER_API_KEY={{ op://Homelab/OpenRouter API Key - omp.sh/credential }}
