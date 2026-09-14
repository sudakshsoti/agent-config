#!/usr/bin/env python3
"""Regression tests for scripts/check-manifest.py and scripts/manifest.py.

Hermetic: every fixture is a disposable temp directory with its own
plugins.txt and skills/ tree; nothing touches the real checkout.
"""

from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
CHECK = ROOT / "scripts" / "check-manifest.py"

sys.path.insert(0, str(ROOT / "scripts"))
import manifest  # noqa: E402


def make_repo(tmp_path, plugins_text, skill_names=()):
    """Write plugins.txt and empty skills/<name>/SKILL.md fixtures under tmp_path."""
    (tmp_path / "plugins.txt").write_text(plugins_text, encoding="utf-8")
    skills_dir = tmp_path / "skills"
    for name in skill_names:
        skill = skills_dir / name
        skill.mkdir(parents=True)
        (skill / "SKILL.md").write_text(
            f"---\nname: {name}\ndescription: Test skill.\n---\n", encoding="utf-8"
        )
    return tmp_path


def run_check(repo_root):
    result = subprocess.run(
        [sys.executable, str(CHECK), str(repo_root)],
        text=True,
        capture_output=True,
        check=False,
    )
    return result.returncode, result.stdout + result.stderr


class ManifestParserTest(unittest.TestCase):
    def test_parses_bare_and_allowlisted_lines(self):
        entries, errors = manifest.parse_plugins_text(
            "# comment\n"
            "\n"
            "external owner/repo\n"
            "external owner/other:sub skill-a skill-b\n"
        )
        self.assertEqual(errors, [])
        self.assertEqual(len(entries), 2)
        self.assertEqual(entries[0].source, "owner/repo")
        self.assertIsNone(entries[0].subdir)
        self.assertEqual(entries[0].skills, [])
        self.assertEqual(entries[1].source, "owner/other")
        self.assertEqual(entries[1].subdir, "sub")
        self.assertEqual(entries[1].skills, ["skill-a", "skill-b"])

    def test_trailing_comment_is_stripped(self):
        entries, errors = manifest.parse_plugins_text("external owner/repo skill-a  # note\n")
        self.assertEqual(errors, [])
        self.assertEqual(entries[0].skills, ["skill-a"])

    def test_unknown_directive_is_an_error(self):
        _, errors = manifest.parse_plugins_text("plugin owner/repo\n")
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].line_no, 1)

    def test_bad_source_is_an_error(self):
        _, errors = manifest.parse_plugins_text("external not-owner-slash-repo\n")
        self.assertEqual(len(errors), 1)

    def test_missing_file_parses_as_empty(self):
        entries, errors = manifest.parse_plugins_file("/no/such/plugins.txt")
        self.assertEqual((entries, errors), ([], []))


class CheckManifestTest(unittest.TestCase):
    def test_current_tree_passes(self):
        code, output = run_check(ROOT)
        self.assertEqual(code, 0, output)

    def test_malformed_line_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = make_repo(Path(tmp), "external not-owner-slash-repo\n")
            code, output = run_check(repo)
        self.assertEqual(code, 1)
        self.assertIn("not owner/repo", output)

    def test_duplicate_name_on_one_line_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = make_repo(Path(tmp), "external owner/repo dup dup\n")
            code, output = run_check(repo)
        self.assertEqual(code, 1)
        self.assertIn("duplicate external skill name: dup", output)

    def test_duplicate_name_across_two_lines_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = make_repo(
                Path(tmp),
                "external owner/repo-a dup\n"
                "external owner/repo-b dup\n",
            )
            code, output = run_check(repo)
        self.assertEqual(code, 1)
        self.assertIn("duplicate external skill name: dup", output)

    def test_bare_source_is_info_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = make_repo(Path(tmp), "external owner/repo\n")
            code, output = run_check(repo)
        self.assertEqual(code, 0, output)
        self.assertIn("info:", output)
        self.assertIn("bare source", output)

    def test_repo_owned_overlap_is_info_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = make_repo(
                Path(tmp),
                "external owner/repo shared-name\n",
                skill_names=["shared-name"],
            )
            code, output = run_check(repo)
        self.assertEqual(code, 0, output)
        self.assertIn("info:", output)
        self.assertIn("overlaps repo-owned skills/shared-name", output)

    def test_missing_plugins_file_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            (repo / "skills").mkdir()
            code, output = run_check(repo)
        self.assertEqual(code, 0, output)


if __name__ == "__main__":
    unittest.main()
