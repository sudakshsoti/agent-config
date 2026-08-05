#!/usr/bin/env python3
"""Regression tests for the Codex TOML configuration merger."""

from pathlib import Path
import subprocess
import tempfile
import tomllib
import unittest


ROOT = Path(__file__).resolve().parents[1]
MERGER = ROOT / "scripts" / "apply-codex-config.py"


class ApplyCodexConfigTest(unittest.TestCase):
    def merge(self, source: str, target: str) -> str:
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            source_path = directory / "source.toml"
            target_path = directory / "target.toml"
            source_path.write_text(source, encoding="utf-8")
            target_path.write_text(target, encoding="utf-8")

            result = subprocess.run(
                ["python3", str(MERGER), str(source_path), str(target_path)],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            return target_path.read_text(encoding="utf-8")

    def test_replaces_multiline_array_without_corrupting_toml(self):
        merged = self.merge(
            "[tui]\nstatus_line = [\"new\"]\n",
            "# retained comment\n[tui]\nstatus_line = [\n  \"old\",\n  \"legacy\",\n]\n\n[unmanaged]\nvalue = true\n",
        )

        self.assertEqual(tomllib.loads(merged)["tui"]["status_line"], ["new"])
        self.assertIn("# retained comment", merged)
        self.assertIn("[unmanaged]\nvalue = true", merged)
        self.assertNotIn("legacy", merged)

    def test_replaces_existing_single_line_assignment(self):
        merged = self.merge(
            "[tui]\nstatus_line = [\"new\"]\n",
            "[tui]\nstatus_line = [\"old\"]\n",
        )

        self.assertEqual(tomllib.loads(merged)["tui"]["status_line"], ["new"])


if __name__ == "__main__":
    unittest.main()
