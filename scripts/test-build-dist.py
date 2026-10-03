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

def skill_md(name):
    return """---
name: %s
description: "Do %s things when %s is asked for."
disable-model-invocation: true
license: MIT
---

# %s

Body.
""" % (name, name, name, name.capitalize())


SKILL = skill_md("alpha")


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


class BuildDistTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory(prefix="build-dist-test-")
        self.root = Path(self._tmp.name)
        (self.root / "scripts").mkdir()
        for name in ("build-dist.py", "lint-skills.py", "frontmatter.py", "manifest.py"):
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

    def plugin_line(self, line):
        path = self.root / "plugins.txt"
        write(path, (path.read_text(encoding="utf-8") if path.exists() else "") + line + "\n")

    def vendor_file(self, clone, relpath, text):
        write(self.root / "vendor" / clone / relpath, text)

    def vendor_manifest(self, *names):
        write(self.root / "distribution-vendor.txt", "".join(n + "\n" for n in names))

    def vendor_zip(self, name):
        return self.root / "dist" / "vendor" / (name + ".zip")

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

    def test_vendor_packages_listed_skills_from_plugin_checkouts(self):
        self.plugin_line("external acme/pack")
        self.vendor_file("acme-pack", "skills/beta/SKILL.md", skill_md("beta"))
        self.vendor_file("acme-pack", "skills/beta/references/one.md", "one\n")
        self.vendor_file("acme-pack", "skills/beta/.DS_Store", "junk")
        self.vendor_manifest("beta")
        result = self.build()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("build-dist: 1 vendored zip(s) up to date", result.stdout)
        with zipfile.ZipFile(self.vendor_zip("beta")) as zf:
            self.assertEqual(sorted(zf.namelist()), ["beta/SKILL.md", "beta/references/one.md"])
            self.assertNotIn("disable-model-invocation", zf.read("beta/SKILL.md").decode())
        self.assertIn("disable-model-invocation", (self.root / "vendor/acme-pack/skills/beta/SKILL.md").read_text())
        self.assertTrue(self.zip_path().exists())

    def test_vendor_resolves_subdir_allowlist_and_frontmatter_name(self):
        self.plugin_line("external acme/mono:packs gamma")
        self.vendor_file("acme-mono", "packs/thing/SKILL.md", skill_md("gamma"))
        self.vendor_manifest("gamma")
        result = self.build()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue(self.vendor_zip("gamma").exists())
        self.assertFalse(self.vendor_zip("thing").exists())

    def test_unavailable_vendor_names_fail_and_write_no_zips(self):
        self.plugin_line("external acme/mono:packs gamma hidden")
        self.vendor_file("acme-mono", "packs/thing/SKILL.md", skill_md("gamma"))
        self.vendor_file("acme-mono", "packs/delta/SKILL.md", skill_md("delta"))
        self.vendor_file("acme-mono", "packs/other/SKILL.md", skill_md("hidden"))
        write(self.root / "skills" / "hidden" / "SKILL.md", skill_md("hidden"))
        self.vendor_manifest("gamma", "delta", "hidden")
        result = self.build()
        self.assertEqual(result.returncode, 1)
        self.assertIn("delta: not found in vendor/ (run ./install.sh to fetch it)", result.stdout)
        self.assertIn("hidden: a repo-owned skills/hidden shadows the vendored copy", result.stdout)
        self.assertIn("2 vendored problem(s); no vendored zips written", result.stdout)
        self.assertFalse((self.root / "dist" / "vendor").exists())

    def test_vendor_symlink_is_a_reported_problem(self):
        self.plugin_line("external acme/pack")
        self.vendor_file("acme-pack", "skills/beta/SKILL.md", skill_md("beta"))
        os.symlink("/etc/hosts", self.root / "vendor" / "acme-pack" / "skills" / "beta" / "link.md")
        self.vendor_manifest("beta")
        result = self.build()
        self.assertEqual(result.returncode, 1)
        self.assertIn("is a symlink; claude.ai zips cannot carry links", result.stdout)
        self.assertFalse(self.vendor_zip("beta").exists())

    def test_vendor_validation_failure_leaves_existing_zips_alone(self):
        self.plugin_line("external acme/pack")
        self.vendor_file("acme-pack", "skills/beta/SKILL.md", skill_md("beta"))
        self.vendor_manifest("beta")
        self.assertEqual(self.build().returncode, 0)
        before = self.vendor_zip("beta").read_bytes()
        self.vendor_file(
            "acme-pack", "skills/beta/SKILL.md", skill_md("beta").replace("Do beta things", "Do <beta> things")
        )
        self.vendor_file("acme-pack", "skills/beta/references/two.md", "two\n")
        result = self.build()
        self.assertEqual(result.returncode, 1)
        self.assertIn("beta: description contains an angle bracket", result.stdout)
        self.assertEqual(before, self.vendor_zip("beta").read_bytes())

    def test_vendor_rebuilds_stale_and_removes_unlisted(self):
        self.plugin_line("external acme/pack")
        self.vendor_file("acme-pack", "skills/beta/SKILL.md", skill_md("beta"))
        self.vendor_manifest("beta")
        self.assertEqual(self.build().returncode, 0)
        first = self.vendor_zip("beta").read_bytes()
        write(self.root / "dist" / "vendor" / "gone.zip", "")
        result = self.build()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("removed dist/vendor/gone.zip", result.stdout)
        self.assertEqual(first, self.vendor_zip("beta").read_bytes())
        self.vendor_file("acme-pack", "skills/beta/references/two.md", "two\n")
        result = self.build()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        with zipfile.ZipFile(self.vendor_zip("beta")) as zf:
            self.assertIn("beta/references/two.md", zf.namelist())

    def test_vendor_manifest_errors_name_their_own_file(self):
        write(self.root / "distribution-vendor.txt", "beta\nBeta!\n")
        result = self.build()
        self.assertEqual(result.returncode, 1)
        self.assertIn("distribution-vendor.txt:2: 'Beta!' is not a skill name", result.stdout)

    def test_vendor_zips_are_not_part_of_check_or_from_index(self):
        self.plugin_line("external acme/pack")
        self.vendor_file("acme-pack", "skills/beta/SKILL.md", skill_md("beta"))
        self.vendor_manifest("beta")
        self.assertEqual(self.build().returncode, 0)
        shutil.rmtree(self.root / "dist" / "vendor")
        self.assertEqual(self.build("--check").returncode, 0)
        self.assertFalse((self.root / "dist" / "vendor").exists())
        self.assertEqual(self.build("--from-index").returncode, 0)
        self.assertFalse((self.root / "dist" / "vendor").exists())


if __name__ == "__main__":
    unittest.main()
