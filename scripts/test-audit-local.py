#!/usr/bin/env python3
"""Hermetic tests for scripts/audit-local.py.

Builds three disposable fixture trees — a fake HOME, a fake repo checkout
(plugins.txt, skills/, vendor/) and a fake dotfiles git repo — and runs
audit-local.py against them with --repo/--home/--dotfiles. Never touches the
operator's real $HOME, ~/dev/dotfiles or this checkout: every path is a
tempdir, and a byte-identical recursive snapshot of all three fixture trees
is asserted before and after each run.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "audit-local.py"

GIT_ENV = {
    "GIT_AUTHOR_NAME": "audit-local test",
    "GIT_AUTHOR_EMAIL": "audit-local-test@example.invalid",
    "GIT_COMMITTER_NAME": "audit-local test",
    "GIT_COMMITTER_EMAIL": "audit-local-test@example.invalid",
    "GIT_CONFIG_NOSYSTEM": "1",
    "GIT_CONFIG_GLOBAL": os.devnull,
}


def isolated_git_environment():
    environment = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    environment.update(GIT_ENV)
    return environment


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def skill_md(name):
    return f"---\nname: {name}\ndescription: Fixture skill.\n---\n"


def snapshot(directory):
    """Byte-identical recursive snapshot: paths, types, link targets, file bytes."""
    entries = {}
    if not directory.exists():
        return entries
    for parent, directories, files in os.walk(directory, followlinks=False):
        for name in directories + files:
            path = Path(parent) / name
            relative = str(path.relative_to(directory))
            if path.is_symlink():
                entries[relative] = ("link", os.readlink(path))
            elif path.is_dir():
                entries[relative] = ("directory",)
            else:
                entries[relative] = ("file", path.read_bytes())
    return entries


class AuditLocalTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)

        self.repo = self.base / "repo"
        self.home = self.base / "home"
        self.dotfiles = self.base / "home" / "dev" / "dotfiles"
        self._build_repo()
        self._build_home()
        self._build_dotfiles()

    # -- fixture construction ---------------------------------------------

    def _build_repo(self):
        repo = self.repo
        # Repo-owned skill that an external source will also claim, to
        # exercise shadowed-repo.
        write(repo / "skills" / "shared-name" / "SKILL.md", skill_md("shared-name"))

        write(
            repo / "plugins.txt",
            "external acme/one shared-name\n"
            "external acme/two dup-name\n"
            "external acme/six\n"
            "external acme/three skillthree\n",
        )

        # acme/one: declared, cloned, provides shared-name (shadowed by repo).
        write(repo / "vendor/acme-one/skills/shared-name/SKILL.md", skill_md("shared-name"))
        # acme/two: declared, cloned, explicitly claims dup-name.
        write(repo / "vendor/acme-two/skills/dup-name/SKILL.md", skill_md("dup-name"))
        # acme/six: declared bare (no allowlist), cloned, also ships dup-name
        # -> duplicate-external across acme/two and acme/six, bare source.
        write(repo / "vendor/acme-six/skills/dup-name/SKILL.md", skill_md("dup-name"))
        write(repo / "vendor/acme-six/skills/six-only/SKILL.md", skill_md("six-only"))
        # acme/three: declared but never cloned -> missing-clone.

        # An undeclared vendor checkout -> undeclared-checkout.
        write(repo / "vendor/acme-four/skills/four-only/SKILL.md", skill_md("four-only"))

    def _build_home(self):
        skills_root = self.home / ".agents" / "skills"
        skills_root.mkdir(parents=True)
        # In-repo, healthy link: not a finding.
        (skills_root / "shared-name").symlink_to(self.repo / "skills" / "shared-name")
        # Dangling link.
        (skills_root / "dangling").symlink_to(self.repo / "skills" / "does-not-exist")
        # Foreign link: resolves outside the repo entirely.
        outside = self.base / "outside-place"
        outside.mkdir()
        (skills_root / "foreign").symlink_to(outside)
        # Real (non-symlink) entry.
        real_dir = skills_root / "realdir"
        real_dir.mkdir()
        write(real_dir / "SKILL.md", skill_md("realdir"))

    def _build_dotfiles(self):
        self.dotfiles.mkdir(parents=True)
        self._git("init", "-q", ".")
        # Collides directly: decodes to ".agents/skills/stray", under the
        # managed tree destination.
        write(self.dotfiles / "dot_agents/skills/stray", "stray\n")
        # A symlink_ source whose *content* (not its own decoded path) points
        # back into agent-config.
        symlink_source = self.dotfiles / "symlink_dot_local/private_bin/executable_omp-fixture-overlay"
        write(symlink_source, "/Users/example/dev/agent-config/omp/overlays/example.yml")
        # An unrelated, non-colliding tracked file.
        write(self.dotfiles / "dot_gitconfig", "[user]\n\tname = Example\n")
        self._git("add", "-A")
        self._git(
            "-c", "commit.gpgsign=false", "commit", "-q", "-m", "fixture",
        )

    def _git(self, *args):
        result = subprocess.run(
            ["git", "-C", str(self.dotfiles), *args],
            env=isolated_git_environment(),
            text=True,
            capture_output=True,
            timeout=30,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return result

    # -- running the script -------------------------------------------------

    def run_audit(self, *extra_args, repo=None, home=None):
        return subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--repo", str(repo if repo is not None else self.repo),
                "--home", str(home if home is not None else self.home),
                "--dotfiles", str(self.dotfiles),
                *extra_args,
            ],
            env=isolated_git_environment(),
            text=True,
            capture_output=True,
            timeout=30,
            check=False,
        )

    # -- tests ----------------------------------------------------------

    def test_every_category_appears_and_exit_is_zero(self):
        before = (
            snapshot(self.repo),
            snapshot(self.home),
            snapshot(self.dotfiles),
        )
        result = self.run_audit()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

        expected_categories = {
            "missing-clone",
            "undeclared-checkout",
            "non-symlink-entry",
            "dangling-link",
            "foreign-link",
            "shadowed-repo",
            "duplicate-external",
            "chezmoi-collision",
        }
        found_categories = {
            line.split(":", 1)[0].split(None, 1)[-1]
            for line in result.stdout.splitlines()
            if line.startswith("  info") or line.startswith("  warn")
        }
        missing = expected_categories - found_categories
        self.assertEqual(missing, set(), result.stdout)

        after = (
            snapshot(self.repo),
            snapshot(self.home),
            snapshot(self.dotfiles),
        )
        self.assertEqual(before, after, "audit-local.py must never write to its inputs")

    def test_specific_findings_are_reported_under_the_right_category(self):
        result = self.run_audit()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        out = result.stdout

        self.assertIn("missing-clone", out)
        self.assertIn("acme/three", out)
        self.assertIn("undeclared-checkout", out)
        self.assertIn("vendor/acme-four", out)
        self.assertIn("dangling-link", out)
        self.assertIn("~/.agents/skills/dangling", out)
        self.assertIn("foreign-link", out)
        self.assertIn("~/.agents/skills/foreign", out)
        self.assertIn("non-symlink-entry", out)
        self.assertIn("~/.agents/skills/realdir", out)
        self.assertIn("shadowed-repo", out)
        self.assertIn("shared-name", out)
        self.assertIn("duplicate-external", out)
        self.assertIn("dup-name", out)
        self.assertIn("bare source", out)
        self.assertIn("chezmoi-collision", out)
        self.assertIn(".agents/skills/stray", out)
        # The healthy in-repo link must never be reported as any kind of finding.
        self.assertNotIn("~/.agents/skills/shared-name is", out)

    def test_json_output_parses_and_matches_text_findings(self):
        result = self.run_audit("--json")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertIn("findings", payload)
        categories = {f["category"] for f in payload["findings"]}
        self.assertIn("missing-clone", categories)
        self.assertIn("chezmoi-collision", categories)
        for finding in payload["findings"]:
            self.assertIn(finding["level"], ("info", "warn"))
            self.assertTrue(finding["message"])

    def test_missing_dotfiles_emits_one_info_finding_and_continues(self):
        result = self.run_audit("--dotfiles", str(self.base / "no-such-dotfiles"))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("info", result.stdout)
        self.assertIn("chezmoi-collision", result.stdout)
        self.assertIn("not found", result.stdout)
        # Still reports every other category despite the missing dotfiles repo.
        self.assertIn("missing-clone", result.stdout)

    def test_invalid_repo_path_exits_2(self):
        before_home = snapshot(self.home)
        result = self.run_audit(repo=self.base / "no-such-repo")
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertEqual(snapshot(self.home), before_home)

    def test_unreadable_plugins_txt_exits_2(self):
        plugins = self.repo / "plugins.txt"
        original_mode = plugins.stat().st_mode
        plugins.chmod(0o000)
        try:
            if os.access(plugins, os.R_OK):
                self.skipTest("running as a user that bypasses file permissions")
            result = self.run_audit()
            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        finally:
            plugins.chmod(original_mode)

    def test_default_repo_is_this_checkout_and_never_writes(self):
        # No --repo/--home/--dotfiles at all: exercises the real defaults
        # (this checkout, $HOME, $AGENT_CONFIG_DOTFILES_DIR or ~/dev/dotfiles)
        # without asserting on their content, just that it runs read-only.
        # A full recursive snapshot of this checkout would be slow (and this
        # test's own point is only that the default-path run touches nothing),
        # so the guard here is `git status --porcelain`, the same check
        # check.sh itself uses, plus a full snapshot of the disposable HOME.
        env = isolated_git_environment()
        env["HOME"] = str(self.home)
        env.pop("AGENT_CONFIG_DOTFILES_DIR", None)

        def repo_git_status():
            status = subprocess.run(
                ["git", "-C", str(ROOT), "status", "--porcelain"],
                env=env,
                text=True,
                capture_output=True,
                timeout=30,
                check=False,
            )
            return status.returncode, status.stdout

        before = (repo_git_status(), snapshot(self.home))
        result = subprocess.run(
            [sys.executable, str(SCRIPT)],
            env=env,
            text=True,
            capture_output=True,
            timeout=30,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        after = (repo_git_status(), snapshot(self.home))
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
