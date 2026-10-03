#!/usr/bin/env python3
"""Exercise installation without using the operator's home directory.

Two things are checked here that nothing else can: that a clean install writes
only the OMP, Pi and shared-skill destinations, and that --prune removes what
this repo owns while leaving everything else — especially unmarked real files
at retired harness paths — exactly as it found it.
"""

import json
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

CLAUDE_FILES = (
    "claude/statusline.sh",
    "claude/subagent-statusline.sh",
    "claude/claude-powerline.json",
)

# A pre-commit hook exports these; an inherited GIT_DIR would redirect
# rev-parse (and therefore the linked-worktree guard) at the outer repository
# instead of the disposable checkout.
GIT_REPO_SELECTOR_VARS = ("GIT_DIR", "GIT_INDEX_FILE", "GIT_WORK_TREE")
# install.sh honors these to place pi-web-access config outside HOME; an
# inherited value (CI runners set XDG_CONFIG_HOME) would send writes to the
# real machine instead of the disposable HOME.
CONFIG_DIR_OVERRIDE_VARS = ("XDG_CONFIG_HOME", "PI_CODING_AGENT_DIR")


def seed_repo(destination):
    """Populate a disposable checkout with everything install.sh links."""
    destination.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(ROOT / "install.sh", destination / "install.sh")
    # The Claude and MCP steps shell out to repo helpers.
    (destination / "scripts").mkdir(exist_ok=True)
    for helper in ("apply-json-config.py", "seed-mcp-servers.py"):
        shutil.copyfile(ROOT / "scripts" / helper, destination / "scripts" / helper)
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
    for relative in CLAUDE_FILES:
        path = destination / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("fixture\n", encoding="utf-8")
    (destination / "claude/settings.json").write_text(
        '{"theme": "dark"}\n', encoding="utf-8"
    )
    (destination / "herdr").mkdir()
    (destination / "herdr/config.toml").write_text("fixture\n", encoding="utf-8")
    (destination / "herdr/plugins.txt").write_text("example/plugin v1\n", encoding="utf-8")
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

    The environment always drops the Git variables a pre-commit hook exports
    and the config-dir overrides that would redirect writes out of the
    disposable HOME, and keeps Git from reading the operator's global/system
    config. Unless
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
        for name in GIT_REPO_SELECTOR_VARS + CONFIG_DIR_OVERRIDE_VARS:
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

    def test_herdr_config_links_only_when_herdr_dir_exists_and_never_installs_plugins_offline(self):
        herdr_stub = self.bin / "herdr"
        called = self.directory / "herdr-called"
        herdr_stub.write_text(
            f"#!/bin/sh\ncase \"$*\" in *install*) touch '{called}' ;; esac\nexit 1\n",
            encoding="utf-8",
        )
        herdr_stub.chmod(0o755)

        result = self.install("--no-external")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("SKIP herdr", result.stdout)
        self.assertFalse((self.test_home / ".config/herdr").exists())

        (self.test_home / ".config/herdr").mkdir(parents=True)
        result = self.install("--no-external")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(
            links_under(self.test_home)[".config/herdr/config.toml"],
            str(self.repo / "herdr/config.toml"),
        )
        self.assertFalse(called.exists(), "--no-external must not run herdr plugin install")

    def test_work_machine_skips_herdr_config(self):
        (self.test_home / ".config/herdr").mkdir(parents=True)
        self.stub_chezmoi_machine("work")
        result = self.install("--no-external")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertNotIn(".config/herdr/config.toml", links_under(self.test_home))

    def stub_chezmoi_machine(self, machine):
        stub = self.bin / "chezmoi"
        stub.write_text(
            f"#!/bin/sh\nprintf '%s' '{{\"machine\": \"{machine}\"}}'\n",
            encoding="utf-8",
        )
        stub.chmod(0o755)

    def test_work_machine_links_skills_but_no_omp_or_pi_config(self):
        self.stub_chezmoi_machine("work")
        result = self.install("--no-external")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("SKIP omp + pi + claude config", result.stdout)
        self.assert_no_retired_harness_paths()

        expected = {
            f".agents/skills/{name}": str(self.repo / "skills" / name)
            for name in ("alpha", "beta", "gamma")
        }
        self.assertEqual(links_under(self.test_home), expected)

    def test_personal_machine_still_links_omp_and_pi_config(self):
        self.stub_chezmoi_machine("personal")
        result = self.install("--no-external")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertNotIn("SKIP omp + pi + claude config", result.stdout)
        links = links_under(self.test_home)
        self.assertEqual(links[".omp/agent/config.yml"], str(self.repo / "omp/config.yml"))
        self.assertEqual(links[".pi/agent/settings.json"], str(self.repo / "pi/settings.json"))

    def test_claude_config_is_linked_and_settings_merged_without_losing_local_keys(self):
        claude = self.test_home / ".claude"
        claude.mkdir()
        (claude / "settings.json").write_text(
            '{"hooks": {"SessionStart": []}, "theme": "light"}\n', encoding="utf-8"
        )
        # A byte-identical real copy (what a hand-copied statusline looks like)
        # is adopted; a differing one is left alone and reported.
        (claude / "statusline.sh").write_text("fixture\n", encoding="utf-8")
        (claude / "subagent-statusline.sh").write_text("hand edited\n", encoding="utf-8")

        result = self.install("--no-external")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

        self.assertEqual(
            os.readlink(claude / "statusline.sh"), str(self.repo / "claude/statusline.sh")
        )
        self.assertEqual(
            os.readlink(claude / "claude-powerline.json"),
            str(self.repo / "claude/claude-powerline.json"),
        )
        self.assertFalse((claude / "subagent-statusline.sh").is_symlink())
        self.assertEqual(
            (claude / "subagent-statusline.sh").read_text(), "hand edited\n"
        )
        self.assertFalse((claude / "settings.json").is_symlink())
        settings = json.loads((claude / "settings.json").read_text())
        self.assertEqual(settings["theme"], "dark")  # repo-owned key wins
        self.assertEqual(settings["hooks"], {"SessionStart": []})  # herdr's survives

    def test_claude_settings_receive_the_key_from_omp_dotenv_not_the_repo(self):
        (self.test_home / ".claude").mkdir()
        (self.test_home / ".omp").mkdir(exist_ok=True)
        (self.test_home / ".omp/.env").write_text(
            "OPENROUTER_API_KEY=sk-or-omp\nJEV_OPENROUTER_API_KEY=sk-or-from-1password\n",
            encoding="utf-8",
        )

        result = self.install("--no-external")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

        settings = json.loads((self.test_home / ".claude/settings.json").read_text())
        self.assertEqual(settings["env"]["OPENROUTER_API_KEY"], "sk-or-from-1password")
        self.assertNotIn("sk-or-from-1password", (self.repo / "claude/settings.json").read_text())

    def test_unparseable_claude_settings_do_not_abort_the_install(self):
        claude = self.test_home / ".claude"
        claude.mkdir()
        (claude / "settings.json").write_text("{ not json\n", encoding="utf-8")

        result = self.install("--no-external")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("not merged", result.stdout)
        self.assertEqual((claude / "settings.json").read_text(), "{ not json\n")
        self.assertTrue((self.test_home / ".agents/skills/alpha").is_symlink())

    def test_unparseable_pi_web_search_does_not_abort_the_install(self):
        (self.repo / "pi/web-search.json").write_text(
            '{"provider": "exa"}\n', encoding="utf-8"
        )
        invalid = self.test_home / ".pi/web-search.json"
        invalid.write_text("{ not json\n", encoding="utf-8")

        result = self.install("--no-external")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("pi/web-search.json not merged", result.stdout)
        self.assertEqual(invalid.read_text(), "{ not json\n")
        self.assertTrue((self.test_home / ".agents/skills/alpha").is_symlink())

    def test_work_machine_leaves_claude_config_alone_but_links_claude_skills(self):
        self.stub_chezmoi_machine("work")
        claude = self.test_home / ".claude"
        claude.mkdir()

        result = self.install("--no-external")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

        self.assertFalse((claude / "settings.json").exists())
        self.assertFalse((claude / "statusline.sh").exists())
        self.assertTrue((claude / "skills/alpha").is_symlink())

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

    def test_claude_skills_root_is_filled_only_when_claude_exists(self):
        # Claude Code does not read ~/.agents/skills, so it gets its own link
        # per declared skill -- but only when ~/.claude is already there. The
        # installer must never create the directory itself.
        no_claude = self.install("--no-external")
        self.assertEqual(no_claude.returncode, 0, no_claude.stdout + no_claude.stderr)
        self.assertFalse((self.test_home / ".claude").exists())

        (self.test_home / ".claude").mkdir()
        with_claude = self.install("--no-external")
        self.assertEqual(
            with_claude.returncode, 0, with_claude.stdout + with_claude.stderr
        )
        claude_skills = self.test_home / ".claude/skills"
        for name in ("alpha", "beta", "gamma"):
            self.assertEqual(
                os.readlink(claude_skills / name), str(self.repo / "skills" / name)
            )
        # Both roots carry the same set: one link each, never one root only.
        self.assertEqual(
            sorted(p.name for p in claude_skills.iterdir()),
            sorted(p.name for p in (self.test_home / ".agents/skills").iterdir()),
        )

    def test_claude_skills_root_is_filled_without_a_shared_root_consumer(self):
        # ~/.claude alone is enough: the two destinations gate independently,
        # so a Claude-only machine still gets a complete set and no ~/.agents.
        remove_tree(self.test_home)
        self.test_home.mkdir()
        (self.test_home / ".claude").mkdir()
        result = self.install("--no-external")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertFalse((self.test_home / ".agents").exists())
        for name in ("alpha", "beta", "gamma"):
            self.assertEqual(
                os.readlink(self.test_home / ".claude/skills" / name),
                str(self.repo / "skills" / name),
            )

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
        (home / ".claude/CLAUDE.md").write_text("mine\n", encoding="utf-8")
        (home / ".claude/skills/alpha").symlink_to(self.repo / "skills/alpha")
        (home / ".claude/agents/plan-critic.md").symlink_to(self.repo / "agents/plan-critic.md")
        (home / ".codex/AGENTS.md").symlink_to(self.repo / "global-agents.md")
        (home / ".codex/prompts/vibe.md").symlink_to(self.repo / "codex/prompts/vibe.md")
        (home / ".config/opencode/AGENTS.md").symlink_to(self.repo / "global-agents.md")
        # A copy the retired mirror left behind, carrying our marker.
        marked = home / ".codex/skills/legacy"
        marked.mkdir(parents=True)
        (marked / ".agent-config-managed").touch()
        # Stale: a repo-owned skill link this repo no longer declares. It lives
        # in the live ~/.claude/skills root, so it is pruned by the
        # not-declared rule rather than the retired-harness one.
        (home / ".claude/skills/ghost").symlink_to(self.repo / "skills/deleted-skill")
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

        for relative in (".claude/agents/plan-critic.md", ".codex/AGENTS.md",
                         ".codex/prompts/vibe.md", ".config/opencode/AGENTS.md",
                         ".codex/skills/legacy"):
            self.assertFalse(
                (home / relative).is_symlink() or (home / relative).exists(),
                f"prune left a repo-owned entry behind: {relative}",
            )
        # An unmarked real file at a retired single-file destination is preserved
        # and reported rather than deleted.
        self.assertEqual((home / ".claude/CLAUDE.md").read_text(), "mine\n")
        self.assertIn("left alone", result.stdout)
        self.assertEqual((home / ".claude/settings.json").read_text(), "mine\n")
        self.assertEqual((keep / "mine.md").read_text(), "mine\n")
        self.assertEqual(
            os.readlink(home / ".claude/skills/local"), "/somewhere/else"
        )
        # ~/.claude/skills is a live destination, not a retired one: a declared
        # skill is (re)linked there by the same run that prunes the retired
        # surfaces, and an undeclared repo-owned link is pruned instead.
        self.assertEqual(
            os.readlink(home / ".claude/skills/alpha"),
            str(self.repo / "skills/alpha"),
        )
        self.assertFalse((home / ".claude/skills/ghost").is_symlink())
        # The shared root was still populated by the same run.
        self.assertTrue((home / ".agents/skills/alpha").is_symlink())

    def test_prune_removes_dangling_config_links_and_keeps_real_files(self):
        first = self.install("--no-external")
        self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
        home = self.test_home
        (self.repo / "omp/lsp.yml").unlink()
        (home / ".omp/agent/stray.yml").write_text("mine\n", encoding="utf-8")
        self.assertTrue((home / ".omp/agent/lsp.yml").is_symlink())
        self.assertFalse((home / ".omp/agent/lsp.yml").exists())

        result = self.install("--no-external", "--prune")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertFalse((home / ".omp/agent/lsp.yml").is_symlink())
        self.assertEqual((home / ".omp/agent/stray.yml").read_text(), "mine\n")
        self.assertTrue((home / ".omp/agent/config.yml").is_symlink())

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

    def vendor_skill(self, slug, dirname, name="x"):
        skill = self.repo / "vendor" / slug / "skills" / dirname
        skill.mkdir(parents=True)
        (skill / "SKILL.md").write_text(
            f"---\nname: {name}\ndescription: External.\n---\n", encoding="utf-8"
        )
        return skill

    def fresh_collide(self, manifest):
        remove_tree(self.repo / "vendor")
        remove_tree(self.test_home / ".agents")
        return self.collide(manifest)

    def collide(self, manifest, repo_owned=False):
        """Install a manifest whose sources all ship skill `x`; return (links, result)."""
        shipped = {
            "a/one": self.vendor_skill("a-one", "x"),
            "b/two": self.vendor_skill("b-two", "x"),
        }
        if repo_owned:
            ours = self.repo / "skills/x"
            ours.mkdir()
            (ours / "SKILL.md").write_text(
                "---\nname: x\ndescription: Ours.\n---\n", encoding="utf-8"
            )
            shipped["ours"] = ours
        (self.repo / "plugins.txt").write_text(manifest, encoding="utf-8")
        result = self.install("--no-external")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        shared = links_under(self.test_home / ".agents")["skills/x"]
        return shared, shipped, result

    def test_collision_bare_vs_bare_last_declared_wins(self):
        winner, shipped, _ = self.collide("external a/one\nexternal b/two\n")
        self.assertEqual(winner, str(shipped["b/two"]))
        winner, shipped, _ = self.fresh_collide("external b/two\nexternal a/one\n")
        self.assertEqual(winner, str(shipped["a/one"]))

    def test_collision_explicit_beats_bare_in_either_order(self):
        winner, shipped, _ = self.collide("external a/one x\nexternal b/two\n")
        self.assertEqual(winner, str(shipped["a/one"]))
        winner, shipped, _ = self.fresh_collide("external b/two\nexternal a/one x\n")
        self.assertEqual(winner, str(shipped["a/one"]))

    def test_collision_explicit_vs_explicit_last_declared_wins(self):
        # check-manifest.py rejects this statically; the installer still resolves it.
        winner, shipped, _ = self.collide("external a/one x\nexternal b/two x\n")
        self.assertEqual(winner, str(shipped["b/two"]))

    def test_collision_repo_owned_beats_every_external(self):
        winner, shipped, result = self.collide(
            "external a/one x\nexternal b/two\n", repo_owned=True
        )
        self.assertEqual(winner, str(shipped["ours"]))
        self.assertIn("shadowed by this repo's skills/x", result.stdout)

    def test_collision_is_the_same_in_the_claude_skills_root(self):
        (self.test_home / ".claude").mkdir()
        winner, shipped, _ = self.collide("external b/two\nexternal a/one x\n")
        claude = links_under(self.test_home / ".claude")["skills/x"]
        self.assertEqual(claude, winner)
        self.assertEqual(winner, str(shipped["a/one"]))

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
