#!/usr/bin/env python3
"""Anti-drift check: every symlink a real `install.sh` run creates must fall
under scripts/ownership_collisions.py's MANAGED_DESTINATIONS.

This is the guard against the two definitions silently diverging: if
install.sh grows a new destination (or one of PI_FILES/OMP_FILES/overlay
support here changes) without a matching update to MANAGED_DESTINATIONS, the
chezmoi collision rule would quietly stop covering it. Hermetic: runs against
a disposable COPY of the repo and a disposable HOME, exactly like
scripts/test-install-selected-skills.py (its helpers are reused verbatim
rather than re-implemented) -- never the operator's real $HOME, never
install.sh in this checkout.
"""

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

# Reuse the existing disposable-HOME installer harness rather than
# reimplementing the linked-worktree guard, the git-selector-variable
# stripping, or the seeded fixture checkout.
sys.path.insert(0, str(ROOT / "scripts"))
import importlib.util

_spec = importlib.util.spec_from_file_location(
    "test_install_selected_skills", ROOT / "scripts" / "test-install-selected-skills.py"
)
if _spec is None or _spec.loader is None:
    raise RuntimeError("could not load test-install-selected-skills.py")
_install_test_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_install_test_module)

import ownership_collisions as oc  # noqa: E402


def target_is_managed(path):
    """True if a HOME-relative symlink path falls under a managed destination."""
    if path in oc.EXEMPT_SHARED_WRITERS:
        return True
    return oc.classify_target(path) is not None


class InstallOutputStaysWithinManagedDestinationsTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)
        self.repo = self.directory / "checkout"
        _install_test_module.seed_repo(self.repo)
        self.test_home = self.directory / "home"
        self.test_home.mkdir()
        for relative in (".omp/agent", ".pi/agent"):
            (self.test_home / relative).mkdir(parents=True)
        self.bin = self.directory / "bin"
        self.bin.mkdir()
        stub = self.bin / "git"
        stub.write_text("#!/bin/sh\nexit 93\n", encoding="utf-8")
        stub.chmod(0o755)

        self.case = _install_test_module.DisposableInstallCase()
        self.case.test_home = self.test_home
        self.case.repo = self.repo
        self.case.bin = self.bin

    def test_every_symlink_created_falls_under_a_managed_destination(self):
        result = self.case.install("--no-external")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

        links = _install_test_module.links_under(self.test_home)
        self.assertTrue(links, "install created no symlinks -- fixture is broken")

        unmanaged = {path: target for path, target in links.items() if not target_is_managed(path)}
        self.assertEqual(
            unmanaged,
            {},
            "install.sh created symlinks outside scripts/ownership_collisions.py's "
            "MANAGED_DESTINATIONS -- update MANAGED_DESTINATIONS to match install.sh",
        )

    def test_every_declared_managed_destination_is_reachable_by_a_real_link(self):
        # The inverse check: every *file-level* managed destination this
        # fixture seeds should actually appear, so MANAGED_DESTINATIONS isn't
        # silently ahead of install.sh either (a stale entry install.sh no
        # longer writes). The skills tree is checked separately since its
        # names are dynamic.
        result = self.case.install("--no-external")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        links = set(_install_test_module.links_under(self.test_home))

        expected_files = [
            ".omp/agent/AGENTS.md",
            ".omp/agent/config.yml",
            ".omp/agent/keybindings.yml",
            ".omp/agent/lsp.yml",
            ".omp/agent/themes/kohra.json",
            ".omp/agent/agents/adversary.md",
            ".config/omp/go-overlay.yml",
            ".pi/agent/AGENTS.md",
            ".pi/agent/settings.json",
            ".pi/agent/verbosity.json",
            ".pi/agent/pi-fff.json",
            ".pi/agent/keybindings.json",
            ".pi/agent/subagents.json",
            ".pi/agent/prompts/vibe.md",
            ".pi/agent/themes/kohra.json",
            ".pi/agent/agents/scout.md",
            ".pi/agent/extensions/operational-footer/index.js",
        ]
        missing = [path for path in expected_files if path not in links]
        self.assertEqual(missing, [], "install.sh no longer writes a destination this fixture expects")
        for path in expected_files:
            self.assertTrue(
                target_is_managed(path),
                f"{path} is installed but not covered by MANAGED_DESTINATIONS",
            )
        self.assertTrue(any(path.startswith(".agents/skills/") for path in links))


if __name__ == "__main__":
    unittest.main()
