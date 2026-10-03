#!/usr/bin/env python3
"""audit-local.py — opt-in, read-only, offline audit of local install drift.

    python3 scripts/audit-local.py [--repo PATH] [--home PATH] [--dotfiles PATH] [--json]

Compares this checkout's declared install surface (plugins.txt, skills/,
vendor/) against what is actually on disk under --home (default $HOME) and,
for the chezmoi collision check, against a dotfiles checkout (default
$AGENT_CONFIG_DOTFILES_DIR or <home>/dev/dotfiles). It never writes, never
fetches, and never runs chezmoi, npm or any harness — the only subprocesses it
starts are `git ls-files`, `git show` and `git rev-parse`, each run with
GIT_OPTIONAL_LOCKS=0 so a concurrent chezmoi/git process is never blocked or
disturbed.

Findings are categorised `info` or `warn`:

  missing-clone         a declared `external` line in plugins.txt has no
                         vendor/<owner>-<repo> checkout on disk.
  undeclared-checkout   a vendor/<slug> directory exists but no `external`
                         line in plugins.txt declares it.
  non-symlink-entry     an entry in ~/.agents/skills is a real file or
                         directory rather than a symlink.
  dangling-link         a symlink in ~/.agents/skills whose target does not
                         exist.
  foreign-link          a symlink in ~/.agents/skills that resolves outside
                         this repo (and its vendor/ checkouts).
  shadowed-repo         (info) an external skill name that a repo-owned
                         skills/<name> shadows at install time — by design,
                         not a problem.
  shadowed-external     a skill name that more than one external source
                         ships; exactly one wins at install time (an
                         allowlist line naming the skill beats a bare line;
                         among the same kind the earlier plugins.txt line
                         wins) and the finding lists the skill, the winning
                         source and every losing source. Detected by reading
                         each declared source's actual vendor checkout (via
                         its SKILL.md frontmatter `name:`), so bare sources —
                         which import every skill they ship — are covered
                         too. Names a repo-owned skill shadows are reported
                         as shadowed-repo only.
  chezmoi-collision      a dotfiles-tracked path that collides with one of
                         this repo's managed install destinations (see
                         ownership_collisions.py). If the dotfiles checkout is
                         absent, this is a single `info` finding instead.

Exit codes: 0 whenever the audit ran, with or without findings. 2 only when
the audit itself could not run — an invalid --repo path, or plugins.txt
existing but unreadable/undecodable. It never fails just because it found
drift.

Out of scope (by design, not oversight): repairing, pruning or declaring
vendor checkouts; running `chezmoi managed`; anything from the pre-4a7edc49
codex/config.toml partition (removed, no longer a destination) or the
~/.config/omp host-overlay-link surface (decided in #38, wontfix: the folder
holds search-keys.tpl, linked on purpose; those links are an intended
destination, not drift).
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from manifest import parse_plugins_file  # noqa: E402
import ownership_collisions as oc  # noqa: E402

GIT_TIMEOUT_SECONDS = 30


class AuditError(Exception):
    """Raised when the audit itself cannot run (as opposed to finding drift)."""


@dataclass(frozen=True)
class Finding:
    level: str  # "info" | "warn"
    category: str
    message: str

    def to_dict(self):
        return {"level": self.level, "category": self.category, "message": self.message}


# --------------------------------------------------------------------------
# Git — the only subprocesses this script ever starts.
# --------------------------------------------------------------------------


def run_git(args, cwd):
    """Run a read-only git command with locks disabled. Never raises for a
    non-zero exit; the caller decides whether that is fatal or just means
    'nothing to report here'."""
    env = dict(os.environ)
    env["GIT_OPTIONAL_LOCKS"] = "0"
    try:
        return subprocess.run(
            ["git", *args],
            cwd=str(cwd),
            env=env,
            text=True,
            capture_output=True,
            timeout=GIT_TIMEOUT_SECONDS,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        raise AuditError(f"failed to run git {' '.join(args)} in {cwd}: {error}") from error


# --------------------------------------------------------------------------
# install.sh's slug rule and skill-name discovery
# --------------------------------------------------------------------------


def slug_for(source):
    """install.sh: slug="${repo%/*}-${repo#*/}" for a validated owner/repo."""
    owner, repo_name = source.split("/", 1)
    return f"{owner}-{repo_name}"


def skill_frontmatter_name(skill_md_path):
    """Read the frontmatter `name:` from a SKILL.md, or None if absent/unreadable."""
    try:
        text = skill_md_path.read_text(encoding="utf-8")
    except OSError:
        return None
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    for line in lines[1:]:
        stripped = line.strip()
        if stripped == "---":
            break
        if line.startswith("name:"):
            value = line[len("name:") :].strip()
            if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
                value = value[1:-1]
            return value
    return None


def external_source_root(vendor_dir, entry):
    """Mirror install.sh's src_root selection for one plugins.txt entry."""
    if entry.subdir:
        return vendor_dir / entry.subdir
    if (vendor_dir / "skills").is_dir():
        return vendor_dir / "skills"
    return vendor_dir


def discover_external_names(src_root, entry):
    """Names an entry actually provides: its explicit allowlist, or every
    SKILL.md frontmatter name under src_root for a bare source."""
    if entry.skills:
        return list(entry.skills)
    names = []
    if (src_root / "SKILL.md").is_file():
        names.append(skill_frontmatter_name(src_root / "SKILL.md") or src_root.name)
    elif src_root.is_dir():
        for child in sorted(src_root.iterdir()):
            if (child / "SKILL.md").is_file():
                names.append(skill_frontmatter_name(child / "SKILL.md") or child.name)
    return names


# --------------------------------------------------------------------------
# Categories
# --------------------------------------------------------------------------


def audit_vendor_checkouts(repo, entries, findings):
    vendor_root = repo / "vendor"
    declared_slugs = {}
    for entry in entries:
        declared_slugs.setdefault(slug_for(entry.source), entry)

    for slug, entry in sorted(declared_slugs.items()):
        if not (vendor_root / slug).is_dir():
            findings.append(
                Finding(
                    "warn",
                    "missing-clone",
                    f"external {entry.source} (plugins.txt:{entry.line_no}) has no "
                    f"vendor/{slug} checkout",
                )
            )

    if vendor_root.is_dir():
        for child in sorted(vendor_root.iterdir()):
            if child.is_dir() and child.name not in declared_slugs:
                findings.append(
                    Finding(
                        "warn",
                        "undeclared-checkout",
                        f"vendor/{child.name} exists but is not declared by any "
                        "'external' line in plugins.txt",
                    )
                )


def audit_shared_skills_root(repo, home, findings):
    skills_root = home / ".agents" / "skills"
    if not skills_root.is_dir():
        return
    repo_resolved = repo.resolve()
    for entry in sorted(skills_root.iterdir(), key=lambda p: p.name):
        name = entry.name
        if entry.is_symlink():
            if not entry.exists():
                try:
                    target = os.readlink(entry)
                except OSError:
                    target = "?"
                findings.append(
                    Finding(
                        "warn",
                        "dangling-link",
                        f"~/.agents/skills/{name} is a dangling symlink -> {target}",
                    )
                )
                continue
            resolved = entry.resolve()
            try:
                resolved.relative_to(repo_resolved)
            except ValueError:
                findings.append(
                    Finding(
                        "warn",
                        "foreign-link",
                        f"~/.agents/skills/{name} -> {resolved} resolves outside this "
                        "repo (and its vendor/ checkouts)",
                    )
                )
        else:
            kind = "directory" if entry.is_dir() else "file"
            findings.append(
                Finding(
                    "warn",
                    "non-symlink-entry",
                    f"~/.agents/skills/{name} is a real {kind}, not a symlink",
                )
            )


def audit_external_name_collisions(repo, entries, findings):
    repo_owned = set()
    skills_dir = repo / "skills"
    if skills_dir.is_dir():
        for child in sorted(skills_dir.iterdir()):
            if (child / "SKILL.md").is_file():
                repo_owned.add(child.name)

    # name -> list of (source label, line_no, is_bare)
    providers = {}
    for entry in entries:
        vendor_dir = repo / "vendor" / slug_for(entry.source)
        if not vendor_dir.is_dir():
            continue  # already reported as missing-clone
        src_root = external_source_root(vendor_dir, entry)
        is_bare = not entry.skills
        for name in discover_external_names(src_root, entry):
            providers.setdefault(name, []).append((entry.source, entry.line_no, is_bare))

    for name, sources in sorted(providers.items()):
        if name in repo_owned:
            labels = ", ".join(f"{source} (plugins.txt:{line_no})" for source, line_no, _ in sources)
            findings.append(
                Finding(
                    "info",
                    "shadowed-repo",
                    f"external skill '{name}' from {labels} is shadowed by repo-owned "
                    f"skills/{name} (repo-owned always wins at install time)",
                )
            )
        if len(sources) > 1 and name not in repo_owned:
            # Mirror install.sh: explicit allowlist beats bare, earlier line
            # beats later within a kind (sources are already in file order).
            winner = next((src for src in sources if not src[2]), sources[0])
            losers = [src for src in sources if src is not winner]
            label = lambda src: f"{src[0]} (plugins.txt:{src[1]})"  # noqa: E731
            findings.append(
                Finding(
                    "warn",
                    "shadowed-external",
                    f"skill '{name}': {label(winner)} wins; shadowed: "
                    f"{', '.join(label(src) for src in losers)}",
                )
            )


def audit_chezmoi_collisions(dotfiles, findings):
    if not dotfiles.is_dir():
        findings.append(
            Finding(
                "info",
                "chezmoi-collision",
                f"dotfiles checkout not found at {dotfiles} — skipping chezmoi-collision checks",
            )
        )
        return

    is_repo = run_git(["rev-parse", "--is-inside-work-tree"], cwd=dotfiles)
    if is_repo.returncode != 0:
        findings.append(
            Finding(
                "info",
                "chezmoi-collision",
                f"{dotfiles} is not a git repository — skipping chezmoi-collision checks",
            )
        )
        return

    ls_files = run_git(["ls-files"], cwd=dotfiles)
    if ls_files.returncode != 0:
        findings.append(
            Finding(
                "info",
                "chezmoi-collision",
                f"'git ls-files' failed in {dotfiles} — skipping chezmoi-collision checks",
            )
        )
        return
    source_paths = [line for line in ls_files.stdout.splitlines() if line.strip()]

    ignore_result = run_git(["show", "HEAD:.chezmoiignore"], cwd=dotfiles)
    chezmoiignore_text = ignore_result.stdout if ignore_result.returncode == 0 else ""

    symlink_targets = {}
    for source_path in source_paths:
        if oc.is_symlink_source(source_path):
            shown = run_git(["show", f"HEAD:{source_path}"], cwd=dotfiles)
            if shown.returncode == 0:
                symlink_targets[source_path] = shown.stdout.strip()

    collisions = oc.find_collisions(source_paths, chezmoiignore_text, symlink_targets)
    for collision in collisions:
        gated_note = " (only inside a conditional .chezmoiignore block)" if collision.gated else ""
        findings.append(
            Finding(
                "warn",
                "chezmoi-collision",
                f"dotfiles:{collision.source_path} -> ~/{collision.target} {collision.reason}{gated_note}",
            )
        )


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------


def parse_args(argv):
    parser = argparse.ArgumentParser(
        description="Opt-in, read-only, offline audit of local install drift."
    )
    parser.add_argument("--repo", default=None, help="repo checkout to audit (default: this script's checkout)")
    parser.add_argument("--home", default=None, help="home directory to inspect (default: $HOME)")
    parser.add_argument("--dotfiles", default=None, help="dotfiles checkout for the chezmoi check")
    parser.add_argument("--json", action="store_true", help="emit findings as JSON instead of text")
    return parser.parse_args(argv)


def resolve_paths(args):
    repo = Path(args.repo).expanduser() if args.repo else SCRIPT_DIR.parent
    if not repo.is_dir():
        raise AuditError(f"--repo path is not a directory: {repo}")

    home = Path(args.home).expanduser() if args.home else Path(os.environ.get("HOME", str(Path.home())))

    if args.dotfiles:
        dotfiles = Path(args.dotfiles).expanduser()
    else:
        env_dotfiles = os.environ.get("AGENT_CONFIG_DOTFILES_DIR")
        dotfiles = Path(env_dotfiles).expanduser() if env_dotfiles else home / "dev" / "dotfiles"

    return repo, home, dotfiles


def load_entries(repo):
    plugins_path = repo / "plugins.txt"
    try:
        entries, errors = parse_plugins_file(str(plugins_path))
    except OSError as error:
        raise AuditError(f"could not read {plugins_path}: {error}") from error
    except UnicodeDecodeError as error:
        raise AuditError(f"could not decode {plugins_path}: {error}") from error
    return entries, errors


def run_audit(repo, home, dotfiles):
    findings = []

    entries, errors = load_entries(repo)
    for error in errors:
        findings.append(
            Finding("warn", "missing-clone", f"plugins.txt:{error.line_no}: {error.message} (skipped)")
        )

    audit_vendor_checkouts(repo, entries, findings)
    audit_shared_skills_root(repo, home, findings)
    audit_external_name_collisions(repo, entries, findings)
    audit_chezmoi_collisions(dotfiles, findings)

    return findings


def print_text_report(repo, home, dotfiles, findings):
    print("agent-config local audit")
    print(f"  repo:     {repo}")
    print(f"  home:     {home}")
    print(f"  dotfiles: {dotfiles}")
    print()
    if not findings:
        print("no findings")
    else:
        by_category = {}
        for finding in findings:
            by_category.setdefault(finding.category, []).append(finding)
        for category in sorted(by_category):
            for finding in by_category[category]:
                print(f"  {finding.level:<4}  {category}: {finding.message}")
    print()
    info_count = sum(1 for f in findings if f.level == "info")
    warn_count = sum(1 for f in findings if f.level == "warn")
    print(f"{info_count} info, {warn_count} warn")


def main(argv):
    args = parse_args(argv)
    try:
        repo, home, dotfiles = resolve_paths(args)
        findings = run_audit(repo, home, dotfiles)
    except AuditError as error:
        print(f"audit-local.py: {error}", file=sys.stderr)
        return 2

    if args.json:
        payload = {
            "repo": str(repo),
            "home": str(home),
            "dotfiles": str(dotfiles),
            "findings": [f.to_dict() for f in findings],
        }
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print_text_report(repo, home, dotfiles, findings)

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
