#!/usr/bin/env python3
"""Phase 0 install fixtures: run install.sh against disposable homes only.

The checkout is a `git archive HEAD` export (not a Git work tree), so the
core.hooksPath step is skipped; git and claude are stubbed to exit 93 and log
any call. The environment is cleared so XDG_CONFIG_HOME / PI_CODING_AGENT_DIR
cannot redirect writes outside the temporary HOME.
"""
import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

BASE = Path(__file__).resolve().parent
CHECKOUT = BASE / "checkout"
STUBS = BASE / "bin"
OUT = BASE / "out"
MAIN_VENDOR = Path.home() / "dev/agent-config/vendor"

HARNESS_DIRS = {
    "codex": ".codex",
    "pi": ".pi/agent",
    "omp": ".omp/agent",
    "opencode": ".config/opencode",
}


def tree_snapshot(root):
    entries = {}
    for parent, dirs, files in os.walk(root, followlinks=False):
        for name in sorted(dirs + files):
            p = Path(parent) / name
            rel = str(p.relative_to(root))
            if p.is_symlink():
                entries[rel] = ("link", os.readlink(p))
            elif p.is_dir():
                entries[rel] = ("dir",)
            else:
                entries[rel] = ("file", hashlib.sha256(p.read_bytes()).hexdigest())
    return entries


def normalise(text, home, checkout):
    return text.replace(str(checkout), "<REPO>").replace(str(home), "<HOME>")


def listing(home, checkout):
    lines = []
    for rel, entry in sorted(tree_snapshot(home).items()):
        if entry[0] == "link":
            lines.append(f"link  ~/{rel} -> {normalise(entry[1], home, checkout)}")
        elif entry[0] == "file":
            lines.append(f"file  ~/{rel} sha256={entry[1]}")
        else:
            lines.append(f"dir   ~/{rel}/")
    return lines


def run_case(name, harnesses, args, vendor=False):
    calls = STUBS / "calls.log"
    calls.unlink(missing_ok=True)
    checkout_before = tree_snapshot(CHECKOUT)
    with tempfile.TemporaryDirectory(dir=BASE) as tmp:
        home = Path(tmp) / "home"
        home.mkdir()
        for h in harnesses:
            (home / HARNESS_DIRS[h]).mkdir(parents=True)
        env = {
            "HOME": str(home),
            "PATH": f"{STUBS}:/opt/homebrew/bin:/usr/bin:/bin",
            "LANG": "C.UTF-8",
        }
        result = subprocess.run(
            ["bash", str(CHECKOUT / "install.sh"), *args],
            cwd=home, env=env, text=True, capture_output=True, timeout=120,
        )
        lines = listing(home, CHECKOUT)
        out = normalise(result.stdout + result.stderr, home, CHECKOUT)
    checkout_after = tree_snapshot(CHECKOUT)
    stub_calls = calls.read_text() if calls.exists() else ""
    report = [
        f"# case: {name}",
        f"# pre-created harness dirs: {', '.join(HARNESS_DIRS[h] for h in harnesses) or '(none)'}",
        f"# vendor present: {vendor}",
        f"# command: env -i HOME=<HOME> PATH=<stubs>:/opt/homebrew/bin:/usr/bin:/bin bash <REPO>/install.sh {' '.join(args)}",
        f"# exit: {result.returncode}",
        f"# checkout unchanged: {checkout_before == checkout_after}",
        f"# git/claude stub calls: {stub_calls.strip() or '(none)'}",
        f"# links: {sum(l.startswith('link') for l in lines)}  files: {sum(l.startswith('file') for l in lines)}",
        "",
        "## resulting HOME tree (sorted)",
        *lines,
        "",
        "## install.sh output",
        out.rstrip(),
        "",
    ]
    (OUT / f"{name}.txt").write_text("\n".join(report))
    print(f"{name}: exit={result.returncode} links={sum(l.startswith('link') for l in lines)} "
          f"checkout_unchanged={checkout_before == checkout_after} stub_calls={bool(stub_calls)}")


def set_vendor(present):
    vendor = CHECKOUT / "vendor"
    if vendor.exists():
        shutil.rmtree(vendor)
    if not present:
        return
    ignore = shutil.ignore_patterns(".git")
    vendor.mkdir()
    shutil.copytree(MAIN_VENDOR / "BexTuychiev-firecrawl-claude-code-skill",
                    vendor / "BexTuychiev-firecrawl-claude-code-skill", ignore=ignore, symlinks=True)
    shutil.copytree(MAIN_VENDOR / "emilkowalski-skills", vendor / "emilkowalski-skills",
                    ignore=ignore, symlinks=True)
    src = MAIN_VENDOR / "anthropics-claude-code/plugins/frontend-design/skills"
    shutil.copytree(src, vendor / "anthropics-claude-code/plugins/frontend-design/skills",
                    ignore=ignore, symlinks=True)


def main():
    OUT.mkdir(exist_ok=True)
    full = ["--no-plugins"]
    selective = ["--skills-only=commit,vibe"]
    set_vendor(False)
    run_case("full-none", [], full)
    run_case("full-codex", ["codex"], full)
    run_case("full-pi", ["pi"], full)
    run_case("full-omp", ["omp"], full)
    run_case("full-opencode", ["opencode"], full)
    run_case("full-all", ["codex", "pi", "omp", "opencode"], full)
    run_case("selective-none", [], selective)
    run_case("selective-codex", ["codex"], selective)
    run_case("selective-pi", ["pi"], selective)
    run_case("selective-all", ["codex", "pi", "omp", "opencode"], selective)
    set_vendor(True)
    run_case("full-pi-vendor", ["pi"], full, vendor=True)
    run_case("full-all-vendor", ["codex", "pi", "omp", "opencode"], full, vendor=True)
    set_vendor(False)


if __name__ == "__main__":
    main()
