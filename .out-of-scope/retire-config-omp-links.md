# Retiring the `~/.config/omp` links

The installer keeps linking `omp/overlays/*` into `~/.config/omp`, file by
file. This is not slated for removal.

## Why this is out of scope

The request was to stop delivering OMP **model-role overlays** to the host:
per-session YAML files that `ompgo` and `ompcodex` loaded to switch OMP onto
a different model set. Those overlays and their wrapper commands have since
been removed. The only file left in `omp/overlays/` is `search-keys.tpl`,
the 1Password template that `op inject` turns into `~/.omp/.env` (OMP's
web-search and OpenRouter keys, plus the Jev key the installer copies into
Claude's settings).

Every reference to that template uses the fixed path
`~/.config/omp/search-keys.tpl`: the refresh command written inside the
template itself, the installer's reminder when `~/.omp/.env` is missing, the
setup notes in `AGENTS.md` and the homelab instructions. The dotfiles repo
also ignores `.config/omp` so chezmoi never claims it. Moving the template
would mean changing all of those across two repositories and gaining nothing
in return, so the link stays.

Leftover links to the removed overlay files point at files that no longer
exist. `./install.sh --prune` already removes broken links like these.

## Prior requests

- #38: "Host ~/.config/omp overlay links retired, with a narrow --prune reclamation"
