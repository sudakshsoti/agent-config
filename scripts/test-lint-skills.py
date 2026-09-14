#!/usr/bin/env python3
"""Regression tests for scripts/lint-skills.py's catalogue count check.

Focused on the "The list below covers the N repo-owned skills" sentence in
skills/README.md — lint_catalogue also checks bullets-vs-directories, but that
half already has coverage via the real tree passing under check.sh; this file
adds the stated-count half, which had none.

Hermetic: everything runs against an in-memory string plus a `dirnames` set,
never against the real skills/README.md or skills/ tree.
"""

import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]

spec = importlib.util.spec_from_file_location("lint_skills", ROOT / "scripts" / "lint-skills.py")
lint_skills = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lint_skills)


def readme_text(sentence):
    return (
        "# Skills library\n\n"
        "## Convention\n\n"
        f"{sentence}\n\n"
        "- `alpha` — Alpha skill.\n"
        "- `beta` — Beta skill.\n"
    )


class StatedCountTest(unittest.TestCase):
    def lint(self, sentence, dirnames, tmp_path):
        skills_dir = tmp_path / "skills"
        skills_dir.mkdir()
        (skills_dir / "README.md").write_text(readme_text(sentence), encoding="utf-8")
        return lint_skills.lint_catalogue(str(skills_dir), dirnames)

    def test_matching_count_passes(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            fails, _ = self.lint(
                "The list below covers the 2 repo-owned skills.",
                ["alpha", "beta"],
                Path(tmp),
            )
        self.assertEqual(fails, [])

    def test_stale_count_fails(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            fails, _ = self.lint(
                "The list below covers the 3 repo-owned skills.",
                ["alpha", "beta"],
                Path(tmp),
            )
        self.assertTrue(
            any("states 3 repo-owned skills but 2 exist" in f for f in fails),
            fails,
        )

    def test_missing_sentence_fails(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            fails, _ = self.lint(
                "This README has no count sentence at all.",
                ["alpha", "beta"],
                Path(tmp),
            )
        self.assertTrue(
            any("no 'covers the N repo-owned skills' sentence" in f for f in fails),
            fails,
        )

    def test_bullet_mismatch_still_reported_alongside_count(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            fails, _ = self.lint(
                "The list below covers the 2 repo-owned skills.",
                ["alpha", "gamma"],
                Path(tmp),
            )
        self.assertTrue(any("gamma" in f for f in fails), fails)
        self.assertTrue(any("beta" in f for f in fails), fails)


if __name__ == "__main__":
    unittest.main()
