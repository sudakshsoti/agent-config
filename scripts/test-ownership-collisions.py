#!/usr/bin/env python3
"""Hermetic tests for scripts/ownership_collisions.py.

Runs entirely against the committed synthetic fixture in
scripts/fixtures/ownership-collisions/ (a fake `git ls-files` listing and a
fake `.chezmoiignore`, both modeled on the real ~/dev/dotfiles shapes but
independent of them). Never reads ~/dev/dotfiles, never runs chezmoi, and
writes nothing into this checkout.
"""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import ownership_collisions as oc  # noqa: E402

FIXTURES = ROOT / "scripts" / "fixtures" / "ownership-collisions"

# The one symlink_ entry in the fixture "points" at this path in its source
# content (what a real chezmoi symlink_ file's contents would hold) —
# supplied out of band from the ls-files listing, the same way a real
# collector would pair `git ls-files` with `git show` on each symlink_ blob.
SYMLINK_SOURCE = "symlink_dot_local/private_bin/omp-go-overlay"
SYMLINK_TARGET_CONTENT = "/Users/example/dev/agent-config/omp/overlays/go-overlay.yml"

GATED_CLAIM_SOURCE = "dot_config/private_omp/executable_search-keys.tpl"


def load_source_paths():
    text = (FIXTURES / "ls-files.txt").read_text(encoding="utf-8")
    return [line for line in text.splitlines() if line.strip()]


def load_chezmoiignore():
    return (FIXTURES / "chezmoiignore").read_text(encoding="utf-8")


class OwnershipCollisionsTest(unittest.TestCase):
    def setUp(self):
        self.source_paths = load_source_paths()
        self.chezmoiignore = load_chezmoiignore()
        self.symlink_targets = {SYMLINK_SOURCE: SYMLINK_TARGET_CONTENT}

    def collisions_by_source(self, chezmoiignore=None):
        collisions = oc.find_collisions(
            self.source_paths,
            self.chezmoiignore if chezmoiignore is None else chezmoiignore,
            self.symlink_targets,
        )
        return {c.source_path: c for c in collisions}

    # -- no collision -----------------------------------------------------

    def test_no_collision_for_an_unrelated_dotfile(self):
        by_source = self.collisions_by_source()
        self.assertNotIn("dot_config/starship.toml", by_source)

    def test_dot_leading_source_entries_are_skipped(self):
        # .chezmoiignore itself is in the fixture's ls-files listing; chezmoi
        # never manages dot-leading source entries, so it must decode to
        # nothing and never appear as a collision.
        self.assertIsNone(oc.decode_source_path(".chezmoiignore"))
        by_source = self.collisions_by_source()
        self.assertNotIn(".chezmoiignore", by_source)

    # -- direct claim -------------------------------------------------------

    def test_direct_claim_on_an_exact_managed_file(self):
        by_source = self.collisions_by_source()
        collision = by_source["dot_omp/private_agent/create_config.yml"]
        self.assertEqual(collision.target, ".omp/agent/config.yml")
        self.assertFalse(collision.gated)

    # -- claim under the skills root -----------------------------------------

    def test_claim_under_the_skills_root(self):
        by_source = self.collisions_by_source()
        collision = by_source["dot_agents/private_skills/exact_myskill/dot_config"]
        self.assertEqual(collision.target, ".agents/skills/myskill/.config")
        self.assertIn("skills", collision.reason)

    # -- symlink_ claim -------------------------------------------------------

    def test_symlink_entry_pointing_into_agent_config_is_a_claim(self):
        by_source = self.collisions_by_source()
        collision = by_source[SYMLINK_SOURCE]
        self.assertIn("agent-config", collision.reason)

    def test_symlink_entry_without_a_known_target_is_not_a_claim(self):
        # Without symlink_targets, the module cannot see where the symlink_
        # points, so its own decoded path (.local/bin/omp-go-overlay, which
        # matches no managed destination) determines the outcome: no claim.
        collisions = oc.find_collisions(self.source_paths, self.chezmoiignore)
        by_source = {c.source_path: c for c in collisions}
        self.assertNotIn(SYMLINK_SOURCE, by_source)

    # -- gated-but-claimed path is not reported --------------------------------

    def test_gated_but_claimed_path_is_not_reported(self):
        # dot_config/private_omp/executable_search-keys.tpl decodes to
        # .config/omp/search-keys.tpl, which claims the OMP overlays
        # destination -- but the fixture .chezmoiignore has an unconditional
        # ".config/omp" line, so chezmoi will never manage it on any machine.
        by_source = self.collisions_by_source()
        self.assertNotIn(GATED_CLAIM_SOURCE, by_source)

    def test_conditionally_gated_claim_is_still_reported(self):
        # A gate inside a {{ if }} block might be inactive on this machine,
        # so it must not suppress the report -- only annotate it "gated".
        chezmoiignore = (
            '{{ if ne .chezmoi.os "darwin" -}}\n'
            ".config/omp\n"
            "{{ end -}}\n"
        )
        by_source = self.collisions_by_source(chezmoiignore=chezmoiignore)
        collision = by_source[GATED_CLAIM_SOURCE]
        self.assertTrue(collision.gated)

    # -- regression: removing the .config/omp gate reintroduces the collision --

    def test_removing_the_config_omp_gate_reintroduces_the_collision(self):
        ungated_chezmoiignore = "\n".join(
            line
            for line in self.chezmoiignore.splitlines()
            if line.strip() != ".config/omp"
        )
        self.assertNotIn(".config/omp", ungated_chezmoiignore.splitlines())

        by_source = self.collisions_by_source(chezmoiignore=ungated_chezmoiignore)
        self.assertIn(GATED_CLAIM_SOURCE, by_source)
        self.assertFalse(by_source[GATED_CLAIM_SOURCE].gated)

    # -- exempt shared writer: pi/web-search.json merge ------------------------

    def test_pi_web_search_merge_is_exempt_not_a_collision(self):
        self.assertIsNone(oc.classify_target(".pi/web-search.json"))
        self.assertIsNone(oc.classify_target(".pi/agent/web-search.json"))

    # -- decoder unit coverage ---------------------------------------------

    def test_decoder_strips_stacked_attribute_prefixes_and_suffixes(self):
        self.assertEqual(
            oc.decode_source_path("run_once_after_dot_myscript.sh.tmpl"),
            ".myscript.sh",
        )
        self.assertEqual(
            oc.decode_source_path("private_dot_ssh/encrypted_id_ed25519.age"),
            ".ssh/id_ed25519",
        )

    def test_decoder_leaves_unmanaged_extensions_alone(self):
        # A non-tmpl, non-age suffix is not chezmoi syntax and must survive.
        self.assertEqual(
            oc.decode_source_path("dot_config/omp/search-keys.tpl"),
            ".config/omp/search-keys.tpl",
        )


if __name__ == "__main__":
    unittest.main()
