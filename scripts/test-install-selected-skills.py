#!/usr/bin/env python3
"""Exercise installation without using the operator's home directory.

Two things are checked here that nothing else can: that a clean install writes
only the OMP, Pi and shared-skill destinations, and that --prune removes what
this repo owns while leaving everything else — especially unmarked real files
at retired harness paths — exactly as it found it.
"""

import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]

OMP_FILES = (
    "omp/config.yml",
    "omp/keybindings.yml",
    "omp/lsp.yml",
    "omp/agents/adversary.md",
    "omp/themes/kohra.json",
    "omp/overlays/go-overlay.yml",
)
PI_FILES = (
    "pi/settings.json",
    "pi/pi-fff.json",
    "pi/keybindings.json",
    "pi/subagents.json",
    "pi/prompts/vibe.md",
    "pi/themes/kohra.json",
    "pi/agents/scout.md",
    "pi/extensions/operational-footer/index.js",
)


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


def links_under(directory):
    """Map of home-relative path -> link target for every symlink under a root."""
    found = {}
    for parent, directories, files in os.walk(directory, followlinks=False):
        for name in directories + files:
            path = Path(parent) / name
            if path.is_symlink():
                found[str(path.relative_to(directory))] = os.readlink(path)
    return found


class InstallerTest(unittest.TestCase):
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
        (self.repo / "global-agents.md").write_text("shared\n", encoding="utf-8")
        for relative in OMP_FILES + PI_FILES:
            path = self.repo / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("fixture\n", encoding="utf-8")
        # A plain install must never fetch this source.
        (self.repo / "plugins.txt").write_text(
            "external example/should-never-fetch\n", encoding="utf-8"
        )
        self.test_home = self.directory / "home"
        self.test_home.mkdir()
        for relative in (".omp/agent", ".pi/agent"):
            (self.test_home / relative).mkdir(parents=True)
        # Catch accidental external fetches and local Git config changes without
        # allowing either command to reach the network or real repository.
        self.bin = self.directory / "bin"
        self.bin.mkdir()
        stub = self.bin / "git"
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

    def assert_no_retired_harness_paths(self):
        for relative in (".claude", ".codex", ".config/opencode"):
            self.assertFalse(
                (self.test_home / relative).exists(),
                f"install created a retired harness path: {relative}",
            )

    def test_clean_install_writes_only_omp_pi_and_shared_skill_destinations(self):
        result = self.install("--no-external")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assert_no_retired_harness_paths()

        expected = {
            f".agents/skills/{name}": str(self.repo / "skills" / name)
            for name in ("alpha", "beta", "gamma")
        }
        expected[".omp/agent/AGENTS.md"] = str(self.repo / "global-agents.md")
        expected[".pi/agent/AGENTS.md"] = str(self.repo / "global-agents.md")
        expected[".omp/agent/config.yml"] = str(self.repo / "omp/config.yml")
        expected[".omp/agent/keybindings.yml"] = str(self.repo / "omp/keybindings.yml")
        expected[".omp/agent/lsp.yml"] = str(self.repo / "omp/lsp.yml")
        expected[".omp/agent/agents/adversary.md"] = str(self.repo / "omp/agents/adversary.md")
        expected[".omp/agent/themes/kohra.json"] = str(self.repo / "omp/themes/kohra.json")
        expected[".config/omp/go-overlay.yml"] = str(self.repo / "omp/overlays/go-overlay.yml")
        for relative in PI_FILES:
            expected[f".pi/agent/{relative[len('pi/') :]}"] = str(self.repo / relative)

        self.assertEqual(links_under(self.test_home), expected)

    def test_selective_and_full_install_agree_on_the_shared_root(self):
        selected = self.install("--skills-only=alpha,beta,gamma")
        self.assertEqual(selected.returncode, 0, selected.stdout + selected.stderr)
        selective_links = {
            path: target
            for path, target in links_under(self.test_home).items()
            if path.startswith(".agents/skills/")
        }
        self.assert_no_retired_harness_paths()
        # Selective mode configures nothing else.
        self.assertFalse((self.test_home / ".omp/agent/config.yml").exists())
        self.assertFalse((self.test_home / ".pi/agent/settings.json").exists())

        remove_tree(self.test_home)
        self.test_home.mkdir()
        for relative in (".omp/agent", ".pi/agent"):
            (self.test_home / relative).mkdir(parents=True)
        full = self.install("--no-external")
        self.assertEqual(full.returncode, 0, full.stdout + full.stderr)
        full_links = {
            path: target
            for path, target in links_under(self.test_home).items()
            if path.startswith(".agents/skills/")
        }
        self.assertEqual(selective_links, full_links)

    def test_shared_root_is_filled_without_creating_harness_config(self):
        for present in ("omp", "pi", "both", "neither"):
            with self.subTest(present=present):
                remove_tree(self.test_home)
                self.test_home.mkdir()
                if present in ("omp", "both"):
                    (self.test_home / ".omp/agent").mkdir(parents=True)
                if present in ("pi", "both"):
                    (self.test_home / ".pi/agent").mkdir(parents=True)
                result = self.install("--skills-only=alpha")
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertEqual(
                    links_under(self.test_home / ".agents"),
                    {"skills/alpha": str(self.repo / "skills" / "alpha")},
                )
                self.assert_no_retired_harness_paths()
                self.assertFalse((self.test_home / ".pi/agent/settings.json").exists())
                self.assertFalse((self.test_home / ".omp/agent/config.yml").exists())

    def test_only_selected_links_change_and_repeated_run_is_safe(self):
        result = self.install("--skills-only=alpha,beta")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(
            links_under(self.test_home),
            {
                f".agents/skills/{name}": str(self.repo / "skills" / name)
                for name in ("alpha", "beta")
            },
        )
        after_first = snapshot(self.directory)

        result = self.install("--skills-only=alpha,beta", "--no-external")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(snapshot(self.directory), after_first)

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
                target.parent.mkdir(parents=True, exist_ok=True)
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

    def test_marked_directory_is_reclaimed_on_full_install(self):
        target = self.test_home / ".agents/skills/beta"
        target.mkdir(parents=True)
        (target / ".agent-config-managed").touch()
        (target / "stale-copy.md").write_text("old\n", encoding="utf-8")
        result = self.install("--no-external")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue(target.is_symlink())
        self.assertEqual(os.readlink(target), str(self.repo / "skills" / "beta"))

    def test_unmarked_directory_is_preserved_with_a_warning(self):
        target = self.test_home / ".agents/skills/beta"
        target.mkdir(parents=True)
        (target / "hand-installed.md").write_text("keep\n", encoding="utf-8")
        result = self.install("--no-external")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("unmanaged directory", result.stdout)
        self.assertFalse(target.is_symlink())
        self.assertEqual((target / "hand-installed.md").read_text(), "keep\n")

    def test_source_directory_without_skill_file_changes_nothing(self):
        (self.repo / "skills/unfinished").mkdir()
        self.assert_refused_without_changes("--skills-only=alpha,unfinished")

    def test_blocked_root_refuses_before_creating_links(self):
        shared = self.test_home / ".agents/skills"
        shared.parent.mkdir(parents=True, exist_ok=True)
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

    def test_prune_removes_retired_repo_links_and_preserves_real_files(self):
        home = self.test_home
        # The retired harness sources still exist on disk here, so every symlink
        # below resolves. That matters: prune must remove a link because of
        # *where it points*, not because its target happens to be missing. A
        # dangling fixture link would pass through the weaker dangling-link path
        # and prove nothing about retired-harness cleanup.
        for relative in ("agents/plan-critic.md", "codex/prompts/vibe.md"):
            retired = self.repo / relative
            retired.parent.mkdir(parents=True, exist_ok=True)
            retired.write_text("retired source\n", encoding="utf-8")
        for relative in (".claude/skills", ".codex/agents", ".codex/prompts",
                         ".config/opencode", ".claude/agents"):
            (home / relative).mkdir(parents=True, exist_ok=True)
        # Ours: symlinks pointing into this checkout.
        (home / ".claude/CLAUDE.md").symlink_to(self.repo / "global-agents.md")
        (home / ".claude/claude-powerline.json").write_text("{}\n", encoding="utf-8")
        (home / ".claude/skills/alpha").symlink_to(self.repo / "skills/alpha")
        (home / ".claude/agents/plan-critic.md").symlink_to(self.repo / "agents/plan-critic.md")
        (home / ".codex/AGENTS.md").symlink_to(self.repo / "global-agents.md")
        (home / ".codex/prompts/vibe.md").symlink_to(self.repo / "codex/prompts/vibe.md")
        (home / ".config/opencode/AGENTS.md").symlink_to(self.repo / "global-agents.md")
        # A copy the retired mirror left behind, carrying our marker.
        marked = home / ".codex/skills/legacy"
        marked.mkdir(parents=True)
        (marked / ".agent-config-managed").touch()
        # Not ours: a hand-made link elsewhere, real files, and a real directory.
        (home / ".claude/skills/local").symlink_to("/somewhere/else")
        (home / ".claude/settings.json").write_text("mine\n", encoding="utf-8")
        keep = home / ".claude/skills/handmade"
        keep.mkdir()
        (keep / "mine.md").write_text("mine\n", encoding="utf-8")

        result = self.install("--no-external", "--prune")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

        # Every retired link below resolved before the prune, so removal must
        # come from the retired-harness rule rather than the dangling sweep.
        self.assertIn("retired harness link", result.stdout)
        self.assertNotIn("(dangling)", result.stdout)

        for relative in (".claude/CLAUDE.md", ".claude/skills/alpha",
                         ".claude/agents/plan-critic.md", ".codex/AGENTS.md",
                         ".codex/prompts/vibe.md", ".config/opencode/AGENTS.md",
                         ".codex/skills/legacy"):
            self.assertFalse(
                (home / relative).is_symlink() or (home / relative).exists(),
                f"prune left a repo-owned entry behind: {relative}",
            )
        # An unmarked real file at a retired single-file destination is preserved
        # and reported rather than deleted.
        self.assertEqual(
            (home / ".claude/claude-powerline.json").read_text(), "{}\n"
        )
        self.assertIn("left alone", result.stdout)
        self.assertEqual((home / ".claude/settings.json").read_text(), "mine\n")
        self.assertEqual((keep / "mine.md").read_text(), "mine\n")
        self.assertEqual(
            os.readlink(home / ".claude/skills/local"), "/somewhere/else"
        )
        # The shared root was still populated by the same run.
        self.assertTrue((home / ".agents/skills/alpha").is_symlink())

    def test_prune_removes_undeclared_shared_links_and_is_idempotent(self):
        result = self.install("--skills-only=alpha")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        shared = self.test_home / ".agents/skills"
        (shared / "ghost").symlink_to(self.repo / "skills/deleted-skill")
        (shared / "handmade").mkdir()

        first = self.install("--no-external", "--prune")
        self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
        self.assertFalse((shared / "ghost").is_symlink())
        self.assertTrue((shared / "handmade").is_dir())
        after_first = snapshot(self.directory)

        second = self.install("--no-external", "--prune")
        self.assertEqual(second.returncode, 0, second.stdout + second.stderr)
        self.assertEqual(snapshot(self.directory), after_first)

    def test_external_sources_link_by_frontmatter_name_and_honor_allowlist(self):
        # vendor/ is pre-populated, and --no-external suppresses the fetch, so
        # the linking path runs without touching the network or the git stub.
        vendor_skills = self.repo / "vendor/example-skills/skills"
        for dirname, declared in (("odd-directory", "renamed-skill"), ("other", "spare-skill")):
            skill = vendor_skills / dirname
            skill.mkdir(parents=True)
            (skill / "SKILL.md").write_text(
                f"---\nname: {declared}\ndescription: External.\n---\n",
                encoding="utf-8",
            )
        # A repo-owned skill of the same name must win the collision.
        ours = self.repo / "skills/renamed-skill"
        ours.mkdir()
        (ours / "SKILL.md").write_text(
            "---\nname: renamed-skill\ndescription: Ours.\n---\n", encoding="utf-8"
        )
        (self.repo / "plugins.txt").write_text(
            "external example/skills renamed-skill spare-skill\n", encoding="utf-8"
        )

        result = self.install("--no-external")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        links = links_under(self.test_home / ".agents")
        # Linked under its declared name, not its directory name.
        self.assertEqual(
            links["skills/spare-skill"], str(vendor_skills / "other")
        )
        # The repo-owned copy wins, and the external one is reported as shadowed.
        self.assertEqual(links["skills/renamed-skill"], str(ours))
        self.assertIn("shadowed by this repo's skills/renamed-skill", result.stdout)
        self.assertNotIn("skills/odd-directory", links)

    def test_external_allowlist_excludes_unnamed_skills(self):
        vendor_skills = self.repo / "vendor/example-skills/skills"
        for name in ("wanted", "unwanted"):
            skill = vendor_skills / name
            skill.mkdir(parents=True)
            (skill / "SKILL.md").write_text(
                f"---\nname: {name}\ndescription: External.\n---\n", encoding="utf-8"
            )
        (self.repo / "plugins.txt").write_text(
            "external example/skills wanted\n", encoding="utf-8"
        )

        result = self.install("--no-external")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        links = links_under(self.test_home / ".agents")
        self.assertEqual(links["skills/wanted"], str(vendor_skills / "wanted"))
        self.assertNotIn("skills/unwanted", links)

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
