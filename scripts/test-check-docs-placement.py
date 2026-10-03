#!/usr/bin/env python3
"""Regression tests for scripts/check-docs-placement.py.

Hermetic: every fixture is a throwaway git repo; nothing touches the checkout.
"""

from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
CHECK = ROOT / "scripts" / "check-docs-placement.py"


def make_repo(files, untracked=()):
    """Create a git repo with `files` tracked and `untracked` left unstaged."""
    tmp = tempfile.TemporaryDirectory()
    repo = Path(tmp.name)
    subprocess.run(["git", "init", "-q", str(repo)], check=True)
    for group, tracked in ((files, True), (untracked, False)):
        for rel, text in dict(group).items():
            path = repo / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
            if tracked:
                subprocess.run(["git", "-C", str(repo), "add", rel], check=True)
    return tmp, repo


def run_check(repo):
    result = subprocess.run(
        [sys.executable, str(CHECK), str(repo)],
        text=True,
        capture_output=True,
        check=False,
    )
    return result.returncode, result.stdout + result.stderr


class DocsPlacementTest(unittest.TestCase):
    def check(self, files, untracked=()):
        tmp, repo = make_repo(files, untracked)
        self.addCleanup(tmp.cleanup)
        return run_check(repo)

    def test_valid_layout_passes(self):
        code, out = self.check(
            {
                "plans/a.md": "Status: planned\n\n# A\n",
                "plans/b.md": "Status: active\n",
                "docs/research/note.md": "# no status needed\n",
                "docs/agents/domain.md": "# no status needed\n",
                "docs/research/page.html": "<html>",
                "README.md": "# readme\n",
            },
            untracked={"plans/autosaved.md": "# OMP autosave, no status\n"},
        )
        self.assertEqual(code, 0, out)
        self.assertIn("0 failed", out)

    def test_plan_without_status_line_fails(self):
        code, out = self.check({"plans/a.md": "# A\n\nStatus: planned\n"})
        self.assertEqual(code, 1, out)
        self.assertIn("plans/a.md", out)
        self.assertIn("Status: planned", out)
        self.assertIn("Status: active", out)

    def test_empty_plan_fails(self):
        code, out = self.check({"plans/a.md": ""})
        self.assertEqual(code, 1, out)
        self.assertIn("plans/a.md", out)

    def test_unknown_status_fails(self):
        code, out = self.check({"plans/a.md": "Status: someday\n"})
        self.assertEqual(code, 1, out)
        self.assertIn("plans/a.md", out)

    def test_done_status_fails_and_says_delete(self):
        code, out = self.check({"plans/a.md": "Status: done\n"})
        self.assertEqual(code, 1, out)
        self.assertIn("plans/a.md", out)
        self.assertIn("delete", out)

    def test_status_with_trailing_text_fails(self):
        code, out = self.check({"plans/a.md": "Status: planned (soon)\n"})
        self.assertEqual(code, 1, out)

    def test_md_directly_under_docs_fails(self):
        code, out = self.check({"docs/runbook.md": "# runbook\n"})
        self.assertEqual(code, 1, out)
        self.assertIn("docs/runbook.md", out)
        self.assertIn("plans/", out)

    def test_md_in_other_docs_subdir_fails(self):
        code, out = self.check({"docs/misc/plan.md": "# plan\n"})
        self.assertEqual(code, 1, out)
        self.assertIn("docs/misc/plan.md", out)

    def test_untracked_misplaced_md_is_ignored(self):
        code, out = self.check(
            {"README.md": "# readme\n"}, untracked={"docs/runbook.md": "# x\n"}
        )
        self.assertEqual(code, 0, out)

    def test_nested_plan_is_checked(self):
        code, out = self.check({"plans/sub/a.md": "# A\n"})
        self.assertEqual(code, 1, out)
        self.assertIn("plans/sub/a.md", out)


if __name__ == "__main__":
    unittest.main()
