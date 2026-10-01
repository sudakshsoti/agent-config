#!/usr/bin/env python3
"""Fixture tests for plugin-pin.py."""

from pathlib import Path
import json
import subprocess
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parent / "plugin-pin.py"
PIN = "a" * 40
OTHER = "b" * 40
ID = "demo@market"


def run(content):
    with tempfile.TemporaryDirectory() as temporary:
        path = Path(temporary) / "installed_plugins.json"
        if content is not None:
            path.write_text(
                content if isinstance(content, str) else json.dumps(content),
                encoding="utf-8",
            )
        result = subprocess.run(
            ["python3", str(SCRIPT), str(path), ID, PIN],
            text=True,
            capture_output=True,
            check=False,
        )
    assert result.returncode == 0, result.stderr
    return result.stdout


def registry(sha):
    return {"plugins": {ID: [{"gitCommitSha": sha}]}}


class PluginPinTest(unittest.TestCase):
    def test_at_pin_is_silent(self):
        self.assertEqual(run(registry(PIN)), "")

    def test_other_commit_warns_with_both_short_shas(self):
        out = run(registry(OTHER))
        self.assertIn("bbbbbbbb", out)
        self.assertIn("aaaaaaaa", out)

    def test_not_installed_is_silent(self):
        self.assertEqual(run({"plugins": {}}), "")
        self.assertEqual(run({"plugins": {ID: []}}), "")

    def test_unreadable_registry_warns(self):
        for content in ("{not json", None, [], {"plugins": []}, {"other": 1},
                        {"plugins": {ID: [{}]}}, {"plugins": {ID: ["x"]}},
                        {"plugins": {ID: [{"gitCommitSha": 5}]}}):
            with self.subTest(content=content):
                self.assertIn("cannot read", run(content))


if __name__ == "__main__":
    unittest.main()
