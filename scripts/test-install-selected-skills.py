#!/usr/bin/env python3
"""Exercise selective installation without using the operator's home directory."""

import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


def remove_tree(path):
    """Remove test state and report cleanup failures as assertion failures."""
    try:
        shutil.rmtree(path)
    except OSError as error:
        raise AssertionError(f"failed to remove test directory {path}: {error}") from error


def snapshot(directory):
    """Record contents and link targets without following installed skill links."""
    entries = {}
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


class SelectedSkillsInstallTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)
        self.repo = self.directory / "checkout"
        self.repo.mkdir()
        shutil.copyfile(ROOT / "install.sh", self.repo / "install.sh")
        for name in ("alpha", "beta", "gamma"):
            skill = self.repo / "skills" / name
            skill.mkdir(parents=True)
            (skill / "SKILL.md").write_text(
                f"---\nname: {name}\ndescription: Test skill.\n---\n",
                encoding="utf-8",
            )
        # A selective run must never fetch this source or configure these tools.
        (self.repo / "plugins.txt").write_text(
            "external example/should-never-fetch\n", encoding="utf-8"
        )
        self.test_home = self.directory / "home"
        self.test_home.mkdir()
        for relative in (
            ".claude/settings.json",
            ".codex/config.toml",
            ".omp/agent/config.yml",
            ".pi/agent/settings.json",
            ".config/opencode/opencode.jsonc",
            ".codex/skills/legacy/.agent-config-managed",
        ):
            path = self.test_home / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("keep this exact content\n", encoding="utf-8")
        for relative in (".claude/skills", ".agents/skills"):
            skills = self.test_home / relative
            skills.mkdir(parents=True)
            (skills / "unrelated").symlink_to("/missing/unrelated")
        # Catch accidental external fetches and local Git config changes without
        # allowing either command to reach the network or real repository.
        self.bin = self.directory / "bin"
        self.bin.mkdir()
        for command in ("git", "claude"):
            stub = self.bin / command
            stub.write_text("#!/bin/sh\nexit 93\n", encoding="utf-8")
            stub.chmod(0o755)

    def install(self, *arguments, repo=None):
        checkout = repo or self.repo
        environment = dict(os.environ)
        environment["HOME"] = str(self.test_home)
        environment["PATH"] = str(self.bin) + os.pathsep + environment["PATH"]
        return subprocess.run(
            ["bash", str(checkout / "install.sh"), *arguments],
            cwd=checkout,
            env=environment,
            text=True,
            capture_output=True,
            timeout=10,
            check=False,
        )

    def assert_refused_without_changes(self, *arguments, repo=None):
        before = snapshot(self.directory)
        result = self.install(*arguments, repo=repo)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(snapshot(self.directory), before)
        return result

    def test_only_selected_links_change_and_repeated_run_is_safe(self):
        for relative in (".claude/skills/alpha", ".agents/skills/alpha"):
            (self.test_home / relative).symlink_to("/missing/old-alpha")
        before = snapshot(self.directory)
        result = self.install("--skills-only=alpha,beta")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        expected = dict(before)
        for root in (".claude/skills", ".agents/skills"):
            for name in ("alpha", "beta"):
                expected[f"home/{root}/{name}"] = (
                    "link",
                    str(self.repo / "skills" / name),
                )
        self.assertEqual(snapshot(self.directory), expected)
        result = self.install("--skills-only=alpha,beta", "--no-plugins")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(snapshot(self.directory), expected)

    def test_shared_root_supports_codex_or_pi_without_creating_agent_config(self):
        for present in ("codex", "pi", "neither"):
            with self.subTest(present=present):
                remove_tree(self.test_home)
                self.test_home.mkdir()
                if present == "codex":
                    (self.test_home / ".codex").mkdir()
                elif present == "pi":
                    (self.test_home / ".pi/agent").mkdir(parents=True)
                result = self.install("--skills-only=alpha")
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertTrue((self.test_home / ".claude/skills/alpha").is_symlink())
                shared = self.test_home / ".agents/skills/alpha"
                self.assertEqual(shared.is_symlink(), present != "neither")
                self.assertFalse((self.test_home / ".claude/agents").exists())
                self.assertFalse((self.test_home / ".claude/settings.json").exists())
                self.assertFalse((self.test_home / ".pi/agent/settings.json").exists())
                self.assertFalse((self.test_home / ".codex/config.toml").exists())

    def test_invalid_names_and_lists_change_nothing(self):
        for names in (
            "", "alpha,", ",alpha", "alpha,,beta", "alpha,missing",
            "alpha,../beta", "alpha,/tmp/beta", "alpha,beta/SKILL.md",
            "alpha, beta", "alpha\nbeta", "alpha,-beta", "alpha,external",
        ):
            with self.subTest(names=names):
                if names.endswith("external"):
                    (self.repo / "skills/external").symlink_to(self.repo / "skills/beta")
                self.assert_refused_without_changes(f"--skills-only={names}")

    def test_real_file_or_directory_refuses_before_any_link_changes(self):
        for kind in ("file", "directory", "marked-directory"):
            with self.subTest(kind=kind):
                target = self.test_home / ".agents/skills/beta"
                if kind == "file":
                    target.write_text("keep me", encoding="utf-8")
                else:
                    target.mkdir()
                    if kind == "marked-directory":
                        (target / ".agent-config-managed").touch()
                self.assert_refused_without_changes("--skills-only=alpha,beta")
                if target.is_dir():
                    remove_tree(target)
                else:
                    target.unlink()

    def test_source_directory_without_skill_file_changes_nothing(self):
        (self.repo / "skills/unfinished").mkdir()
        self.assert_refused_without_changes("--skills-only=alpha,unfinished")

    def test_blocked_root_refuses_before_changing_other_root(self):
        shared = self.test_home / ".agents/skills"
        remove_tree(shared)
        for kind in ("file", "dangling-link"):
            with self.subTest(kind=kind):
                if kind == "file":
                    shared.write_text("keep me", encoding="utf-8")
                else:
                    shared.symlink_to("/missing/skills")
                self.assert_refused_without_changes("--skills-only=alpha,beta")
                shared.unlink()

    def test_prune_and_duplicate_mode_flags_are_rejected(self):
        self.assert_refused_without_changes("--skills-only=alpha", "--prune")
        self.assert_refused_without_changes(
            "--skills-only=alpha", "--skills-only=beta"
        )

    def test_ephemeral_worktree_requires_explicit_force(self):
        ephemeral = self.directory / "worktrees/temporary-checkout"
        shutil.copytree(self.repo, ephemeral)
        result = self.assert_refused_without_changes(
            "--skills-only=alpha", repo=ephemeral
        )
        self.assertIn("ephemeral worktree", result.stdout)
        result = self.install("--skills-only=alpha", "--force", repo=ephemeral)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(
            (self.test_home / ".agents/skills/alpha").resolve(),
            (ephemeral / "skills/alpha").resolve(),
        )


if __name__ == "__main__":
    unittest.main()
