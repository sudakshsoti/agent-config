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
    "pi/verbosity.json",
    "pi/pi-fff.json",
    "pi/keybindings.json",
    "pi/subagents.json",
    "pi/prompts/vibe.md",
    "pi/themes/kohra.json",
    "pi/agents/scout.md",
    "pi/extensions/operational-footer/index.js",
)

# A pre-commit hook exports these; an inherited GIT_DIR would redirect
# rev-parse (and therefore the linked-worktree guard) at the outer repository
# instead of the disposable checkout.
GIT_REPO_SELECTOR_VARS = ("GIT_DIR", "GIT_INDEX_FILE", "GIT_WORK_TREE")


def seed_repo(destination):
    """Populate a disposable checkout with everything install.sh links."""
    destination.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(ROOT / "install.sh", destination / "install.sh")
    for name in ("alpha", "beta", "gamma"):
        skill = destination / "skills" / name
        skill.mkdir(parents=True)
        (skill / "SKILL.md").write_text(
            f"---\nname: {name}\ndescription: Test skill.\n---\n",
            encoding="utf-8",
        )
    (destination / "global-agents.md").write_text("shared\n", encoding="utf-8")
    for relative in OMP_FILES + PI_FILES:
        path = destination / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("fixture\n", encoding="utf-8")
    # A plain install must never fetch this source.
    (destination / "plugins.txt").write_text(
        "external example/should-never-fetch\n", encoding="utf-8"
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


class DisposableInstallCase(unittest.TestCase):
    """Shared install.sh runner over a disposable HOME.

    The environment always drops the Git variables a pre-commit hook exports,
    and keeps Git from reading the operator's global/system config. Unless
    real_git is set, a PATH stub stands in for Git so that an accidental fetch
    or repository config write fails loudly instead of reaching the network.
    """

    # Supplied by each subclass's setUp: the disposable HOME, the checkout
    # under test, and the directory holding the stub git used when real_git is
    # false.
    test_home: Path
    repo: Path
    bin: Path

    def install_environment(self, real_git):
        environment = dict(os.environ)
        environment["HOME"] = str(self.test_home)
        for name in GIT_REPO_SELECTOR_VARS:
            environment.pop(name, None)
        environment["GIT_CONFIG_NOSYSTEM"] = "1"
        environment["GIT_CONFIG_GLOBAL"] = os.devnull
        if not real_git:
            environment["PATH"] = str(self.bin) + os.pathsep + environment["PATH"]
        return environment

    def install(self, *arguments, repo=None, real_git=False):
        checkout = repo or self.repo
        return subprocess.run(
            ["bash", str(checkout / "install.sh"), *arguments],
            cwd=checkout,
            env=self.install_environment(real_git),
            text=True,
            capture_output=True,
            timeout=10,
            check=False,
        )


class InstallerTest(DisposableInstallCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)
        self.repo = self.directory / "checkout"
        seed_repo(self.repo)
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
        for present in ("omp", "pi", "both"):
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

    def test_no_consumer_creates_no_shared_root(self):
        # With none of ~/.codex, ~/.pi/agent, ~/.config/opencode or
        # ~/.omp/agent present, both selective and full installs must create
        # no ~/.agents at all — not even an empty skills/ directory — while
        # still exiting 0 and saying so.
        remove_tree(self.test_home)
        self.test_home.mkdir()
        selective = self.install("--skills-only=alpha")
        self.assertEqual(selective.returncode, 0, selective.stdout + selective.stderr)
        self.assertFalse((self.test_home / ".agents").exists())
        self.assertIn("no shared-skill-root consumer", selective.stdout)

        full = self.install("--no-external")
        self.assertEqual(full.returncode, 0, full.stdout + full.stderr)
        self.assertFalse((self.test_home / ".agents").exists())
        self.assertIn("no shared-skill-root consumer", full.stdout)

    # Every consumer set that shared_root_consumers_present checks, mapped to
    # the home-relative directories that make it true. "none" and "all" are
    # the extremes; the other four isolate one consumer at a time.
    CONSUMER_SETS = {
        "none": (),
        "codex": (".codex",),
        "pi": (".pi/agent",),
        "opencode": (".config/opencode",),
        "omp": (".omp/agent",),
        "all": (".codex", ".pi/agent", ".config/opencode", ".omp/agent"),
    }

    def _reset_home_for_consumers(self, relatives):
        remove_tree(self.test_home)
        self.test_home.mkdir()
        for relative in relatives:
            (self.test_home / relative).mkdir(parents=True)

    def test_consumer_matrix_agrees_across_modes(self):
        # Stub external source so full installs exercise S04 (externals follow
        # the same gate) alongside the repo-owned skills every mode links.
        vendor_skill = self.repo / "vendor/example-skills/skills/ext-one"
        vendor_skill.mkdir(parents=True)
        (vendor_skill / "SKILL.md").write_text(
            "---\nname: ext-one\ndescription: External stub.\n---\n",
            encoding="utf-8",
        )
        (self.repo / "plugins.txt").write_text(
            "external example/skills ext-one\n", encoding="utf-8"
        )

        for name, relatives in self.CONSUMER_SETS.items():
            with self.subTest(consumer_set=name):
                # Selective mode: repo-owned names only (external skills are
                # never selectable through --skills-only).
                self._reset_home_for_consumers(relatives)
                selective = self.install("--skills-only=alpha,beta,gamma")
                self.assertEqual(
                    selective.returncode, 0, selective.stdout + selective.stderr
                )
                selective_links = links_under(self.test_home / ".agents")

                # Full mode: repo-owned names plus the stubbed external.
                self._reset_home_for_consumers(relatives)
                full = self.install("--no-external")
                self.assertEqual(full.returncode, 0, full.stdout + full.stderr)
                full_links = links_under(self.test_home / ".agents")

                if name == "none":
                    self.assertEqual(selective_links, {})
                    self.assertEqual(full_links, {})
                    self.assertFalse((self.test_home / ".agents").exists())
                else:
                    self.assertEqual(
                        selective_links,
                        {
                            f"skills/{skill}": str(self.repo / "skills" / skill)
                            for skill in ("alpha", "beta", "gamma")
                        },
                    )
                    expected_full = dict(selective_links)
                    expected_full["skills/ext-one"] = str(vendor_skill)
                    self.assertEqual(full_links, expected_full)

                # ~/.pi/agent/skills must never exist, and this repo must never
                # write Codex or OpenCode config, in any consumer set or mode.
                for relative in relatives:
                    if relative == ".pi/agent":
                        self.assertFalse(
                            (self.test_home / ".pi/agent/skills").exists()
                        )
                    if relative == ".codex":
                        self.assertEqual(
                            list((self.test_home / ".codex").iterdir()), []
                        )
                    if relative == ".config/opencode":
                        self.assertEqual(
                            list((self.test_home / ".config/opencode").iterdir()), []
                        )

    def test_prune_under_pi_only_covers_the_shared_root(self):
        self._reset_home_for_consumers((".pi/agent",))
        result = self.install("--skills-only=alpha")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        shared = self.test_home / ".agents/skills"
        self.assertTrue((shared / "alpha").is_symlink())
        (shared / "ghost").symlink_to(self.repo / "skills/deleted-skill")

        pruned = self.install("--no-external", "--prune")
        self.assertEqual(pruned.returncode, 0, pruned.stdout + pruned.stderr)
        self.assertFalse((shared / "ghost").is_symlink())
        # The repo-owned skills relinked by the full install survive.
        for skill in ("alpha", "beta", "gamma"):
            self.assertTrue((shared / skill).is_symlink())
        self.assertFalse((self.test_home / ".pi/agent/skills").exists())

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


class LinkedWorktreeTest(DisposableInstallCase):
    """Refusal for a real `git worktree add` tree, and primary-checkout success.

    The linked worktree lives at <tmp>/linked-checkout — deliberately not
    matching install.sh's */worktrees/* path patterns — so only the structural
    rev-parse guard can refuse it. Nothing here reaches the network: every run
    passes --no-external or --skills-only.
    """

    def setUp(self):
        if shutil.which("git") is None:
            self.skipTest("git is required for the linked-worktree fixture")
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)
        self.primary = self.directory / "primary-checkout"
        seed_repo(self.primary)
        self.test_home = self.directory / "home"
        self.test_home.mkdir()
        for relative in (".omp/agent", ".pi/agent"):
            (self.test_home / relative).mkdir(parents=True)

        self.git("init", "-q", cwd=self.primary)
        self.git("add", "-A", cwd=self.primary)
        self.git(
            "-c", "user.name=Installer Test",
            "-c", "user.email=installer@example.com",
            "-c", "commit.gpgsign=false",
            "commit", "-qm", "fixture",
            cwd=self.primary,
        )
        self.linked = self.directory / "linked-checkout"
        self.git(
            "worktree", "add", "-q", "-b", "feature", str(self.linked),
            cwd=self.primary,
        )
        self.common_dir = Path(
            self.git(
                "rev-parse", "--path-format=absolute", "--git-common-dir",
                cwd=self.linked,
            ).stdout.strip()
        )
        # Only the structural guard can fire: neither path matches the patterns
        # that the pre-existing path guard rejects.
        for path in (self.primary, self.linked):
            self.assertNotIn("/worktrees/", str(path))
        self.assertNotEqual(
            self.git(
                "rev-parse", "--path-format=absolute", "--git-dir", cwd=self.linked
            ).stdout.strip(),
            str(self.common_dir),
        )

    def git(self, *arguments, cwd):
        """Run real Git in the fixture, never the PATH stub."""
        result = subprocess.run(
            ["git", "-C", str(cwd), *arguments],
            env=self.install_environment(real_git=True),
            text=True,
            capture_output=True,
            timeout=30,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        return result

    def assert_worktree_refused_without_changes(self, *arguments):
        home_before = snapshot(self.test_home)
        config_before = (self.common_dir / "config").read_bytes()
        result = self.install(*arguments, repo=self.linked, real_git=True)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("linked worktree", result.stdout + result.stderr)
        self.assertEqual(snapshot(self.test_home), home_before, "HOME changed")
        self.assertEqual(
            (self.common_dir / "config").read_bytes(),
            config_before,
            "the shared .git/config changed",
        )
        return result

    def test_full_selective_and_prune_refusals_change_nothing(self):
        home_before = snapshot(self.test_home)
        config_before = (self.common_dir / "config").read_bytes()
        for arguments in (
            ("--no-external",),
            ("--skills-only=alpha",),
            ("--no-external", "--prune"),
        ):
            with self.subTest(arguments=arguments):
                self.assert_worktree_refused_without_changes(*arguments)
        # Byte-identical across the whole sequence, not merely run by run.
        self.assertEqual(snapshot(self.test_home), home_before)
        self.assertEqual((self.common_dir / "config").read_bytes(), config_before)

    def test_force_installs_from_a_linked_worktree(self):
        result = self.install(
            "--skills-only=alpha", "--force", repo=self.linked, real_git=True
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("linked worktree", result.stdout)
        self.assertEqual(
            (self.test_home / ".agents/skills/alpha").resolve(),
            (self.linked / "skills/alpha").resolve(),
        )

    def test_primary_checkout_writes_core_hooks_path(self):
        result = self.install("--no-external", repo=self.primary, real_git=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        hooks = self.git(
            "config", "--local", "--get", "core.hooksPath", cwd=self.primary
        )
        self.assertEqual(hooks.stdout.strip(), ".githooks")


if __name__ == "__main__":
    unittest.main()
