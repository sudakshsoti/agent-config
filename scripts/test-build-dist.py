#!/usr/bin/env python3
"""Regression tests for scripts/build-dist.py, the claude.ai skill packager.

Hermetic: every case builds a throwaway git repo holding a copy of the real
build-dist.py and lint-skills.py, never the real skills/ or dist/ trees.
"""

import os
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GIT_ENV = {
    **os.environ,
    "GIT_CONFIG_GLOBAL": os.devnull,
    "GIT_CONFIG_NOSYSTEM": "1",
    "GIT_AUTHOR_NAME": "t",
    "GIT_AUTHOR_EMAIL": "t@example.com",
    "GIT_COMMITTER_NAME": "t",
    "GIT_COMMITTER_EMAIL": "t@example.com",
}

SKILL = """---
name: alpha
description: "Do alpha things when alpha is asked for."
disable-model-invocation: true
license: MIT
---

# Alpha

Body.
"""


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


class BuildDistTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory(prefix="build-dist-test-")
        self.root = Path(self._tmp.name)
        (self.root / "scripts").mkdir()
        for name in ("build-dist.py", "lint-skills.py", "frontmatter.py"):
            shutil.copy2(ROOT / "scripts" / name, self.root / "scripts" / name)
        write(self.root / ".gitignore", ".DS_Store\n")
        write(self.root / "distribution.txt", "# comment\nalpha\n")
        write(self.root / "skills" / "alpha" / "SKILL.md", SKILL)
        write(self.root / "skills" / "alpha" / "references" / "one.md", "one\n")
        write(self.root / "skills" / "alpha" / ".DS_Store", "junk")
        self.git("init", "-q")
        self.git("add", "-A")

    def tearDown(self):
        self._tmp.cleanup()

    def git(self, *args):
        subprocess.run(["git", "-C", str(self.root), *args], check=True, env=GIT_ENV, capture_output=True)

    def build(self, *flags):
        return subprocess.run(
            [sys.executable, str(self.root / "scripts" / "build-dist.py"), str(self.root), *flags],
            capture_output=True,
            text=True,
            env=GIT_ENV,
        )

    def zip_path(self, name="alpha"):
        return self.root / "dist" / (name + ".zip")

    def test_builds_upload_layout_and_strips_rejected_keys(self):
        result = self.build()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        with zipfile.ZipFile(self.zip_path()) as zf:
            self.assertEqual(
                sorted(zf.namelist()), ["alpha/SKILL.md", "alpha/references/one.md"]
            )
            skill = zf.read("alpha/SKILL.md").decode()
        self.assertNotIn("disable-model-invocation", skill)
        self.assertIn("license: MIT", skill)
        self.assertIn("# Alpha", skill)
        # The source is untouched.
        self.assertIn("disable-model-invocation", (self.root / "skills/alpha/SKILL.md").read_text())

    def test_rebuild_is_byte_identical_and_check_passes(self):
        self.build()
        first = self.zip_path().read_bytes()
        self.zip_path().unlink()
        self.build()
        self.assertEqual(first, self.zip_path().read_bytes())
        self.assertEqual(self.build("--check").returncode, 0)

    def test_check_reports_stale_and_unlisted_without_writing(self):
        self.build()
        write(self.root / "skills" / "alpha" / "references" / "one.md", "changed\n")
        write(self.root / "dist" / "gone.zip", "")
        before = self.zip_path().read_bytes()
        result = self.build("--check")
        self.assertEqual(result.returncode, 1)
        self.assertIn("STALE dist/alpha.zip", result.stdout)
        self.assertIn("UNLISTED dist/gone.zip", result.stdout)
        self.assertEqual(before, self.zip_path().read_bytes())

        self.assertEqual(self.build().returncode, 0)
        self.assertFalse((self.root / "dist" / "gone.zip").exists())
        self.assertEqual(self.build("--check").returncode, 0)

    def test_from_index_ignores_unstaged_edits(self):
        write(self.root / "skills" / "alpha" / "references" / "one.md", "unstaged\n")
        self.assertEqual(self.build("--from-index").returncode, 0)
        with zipfile.ZipFile(self.zip_path()) as zf:
            self.assertEqual(zf.read("alpha/references/one.md"), b"one\n")

    def test_invalid_skill_fails_and_writes_nothing(self):
        write(
            self.root / "skills" / "alpha" / "SKILL.md",
            SKILL.replace("Do alpha things", "Do <alpha> things"),
        )
        write(self.root / "skills" / "alpha" / "nested" / "SKILL.md", SKILL)
        result = self.build()
        self.assertEqual(result.returncode, 1)
        self.assertIn("angle bracket", result.stdout)
        self.assertIn("exactly one SKILL.md", result.stdout)
        self.assertFalse(self.zip_path().exists())

    def test_listed_skill_without_files_fails(self):
        write(self.root / "distribution.txt", "alpha\nmissing\n")
        result = self.build()
        self.assertEqual(result.returncode, 1)
        self.assertIn("missing: listed", result.stdout)


if __name__ == "__main__":
    unittest.main()
