#!/usr/bin/env python3
"""Regression tests for the pi web-search preference merger."""

from pathlib import Path
import json
import os
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
MERGER = ROOT / "scripts" / "apply-json-config.py"
TRACKED_CONFIG = ROOT / "pi" / "web-search.json"


class ApplyWebSearchConfigTest(unittest.TestCase):
    def run_merger(self, source, target):
        """Run the merger in a scratch directory; return (returncode, target text)."""
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            source_path = directory / "source.json"
            target_path = directory / "target.json"
            if source is not None:
                source_path.write_text(source, encoding="utf-8")
            if target is not None:
                target_path.write_text(target, encoding="utf-8")

            result = subprocess.run(
                ["python3", str(MERGER), str(source_path), str(target_path)],
                text=True,
                capture_output=True,
                check=False,
            )
            text = target_path.read_text(encoding="utf-8") if target_path.exists() else ""
            return result, text

    def merge(self, source, target):
        result, text = self.run_merger(source, target)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return text

    def parse(self, text):
        """Parse merged output, failing the test rather than raising on bad JSON."""
        try:
            return json.loads(text)
        except json.JSONDecodeError as error:
            self.fail(f"merger produced invalid JSON: {error}\n{text}")

    def test_pushes_workflow_into_existing_config(self):
        merged = self.parse(self.merge(
            '{"workflow": "auto-summary"}\n',
            '{"provider": "all"}\n',
        ))

        self.assertEqual(merged["workflow"], "auto-summary")

    def test_preserves_unmanaged_machine_local_keys(self):
        merged = self.parse(self.merge(
            '{"workflow": "auto-summary"}\n',
            '{"curatorTimeoutSeconds": 20, "autoOpenBrowser": false}\n',
        ))

        self.assertEqual(merged["curatorTimeoutSeconds"], 20)
        self.assertIs(merged["autoOpenBrowser"], False)

    def test_creates_missing_config(self):
        merged = self.parse(self.merge('{"workflow": "auto-summary"}\n', None))

        self.assertEqual(merged, {"workflow": "auto-summary"})

    def test_source_wins_over_conflicting_target_key(self):
        merged = self.parse(self.merge(
            '{"workflow": "auto-summary", "provider": "auto"}\n',
            '{"workflow": "summary-review", "provider": "brave"}\n',
        ))

        self.assertEqual(merged["workflow"], "auto-summary")
        self.assertEqual(merged["provider"], "auto")

    def test_merges_nested_objects_instead_of_replacing_them(self):
        merged = self.parse(self.merge(
            '{"ssrf": {"allowRanges": ["198.18.0.0/15"]}}\n',
            '{"ssrf": {"trustEnvProxy": false, "allowRanges": []}}\n',
        ))

        self.assertEqual(merged["ssrf"]["allowRanges"], ["198.18.0.0/15"])
        self.assertIs(merged["ssrf"]["trustEnvProxy"], False)

    def test_is_idempotent_and_leaves_mtime_untouched(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            source_path = directory / "source.json"
            target_path = directory / "target.json"
            source_path.write_text('{"workflow": "auto-summary"}\n', encoding="utf-8")
            target_path.write_text('{"workflow": "auto-summary"}\n', encoding="utf-8")
            os.utime(target_path, (1_000_000, 1_000_000))

            result = subprocess.run(
                ["python3", str(MERGER), str(source_path), str(target_path)],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(target_path.stat().st_mtime, 1_000_000)

    def test_preserves_existing_file_mode(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            source_path = directory / "source.json"
            target_path = directory / "target.json"
            source_path.write_text('{"workflow": "auto-summary"}\n', encoding="utf-8")
            target_path.write_text('{"provider": "all"}\n', encoding="utf-8")
            target_path.chmod(0o644)

            result = subprocess.run(
                ["python3", str(MERGER), str(source_path), str(target_path)],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(target_path.stat().st_mode & 0o777, 0o644)

    def test_defaults_to_owner_only_mode_when_creating(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            source_path = directory / "source.json"
            target_path = directory / "target.json"
            source_path.write_text('{"workflow": "auto-summary"}\n', encoding="utf-8")

            result = subprocess.run(
                ["python3", str(MERGER), str(source_path), str(target_path)],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(target_path.stat().st_mode & 0o777, 0o600)

    def test_repo_config_contains_only_managed_non_secret_preferences(self):
        try:
            source = TRACKED_CONFIG.read_text(encoding="utf-8")
        except OSError as error:
            self.fail(f"cannot read tracked config: {error}")
        config = self.parse(source)
        self.assertEqual(set(config), {"provider", "summaryModel", "workflow"})

        result, _ = self.run_merger(source, '{}\n')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_rejects_credential_keys_in_the_tracked_file(self):
        result, _ = self.run_merger(
            '{"braveApiKey": "sk-live-should-not-be-committed"}\n',
            '{"provider": "all"}\n',
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("credential-shaped key", result.stderr)

    def test_rejects_nested_credential_keys(self):
        result, _ = self.run_merger(
            '{"searchRouting": {"exaToken": "x"}}\n',
            None,
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("searchRouting.exaToken", result.stderr)

    def run_with_env(self, dotenv, target, *specs):
        """Merge an empty source into target with --env-from specs; return (result, parsed target)."""
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            source_path = directory / "source.json"
            target_path = directory / "target.json"
            dotenv_path = directory / ".env"
            source_path.write_text("{}\n", encoding="utf-8")
            target_path.write_text(target, encoding="utf-8")
            if dotenv is not None:
                dotenv_path.write_text(dotenv, encoding="utf-8")
            args = ["--env-from", f"{dotenv_path}:{specs[0]}"] if specs else []
            result = subprocess.run(
                ["python3", str(MERGER), str(source_path), str(target_path), *args],
                text=True,
                capture_output=True,
                check=False,
            )
            return result, self.parse(target_path.read_text(encoding="utf-8"))

    def test_env_from_copies_the_named_secret_and_keeps_other_env(self):
        result, merged = self.run_with_env(
            "# comment\nOTHER=nope\nOPENROUTER_API_KEY='sk-or-live'\n",
            '{"env": {"KEEP": "1"}, "hooks": {"x": []}}\n',
            "OPENROUTER_API_KEY",
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            merged["env"], {"KEEP": "1", "OPENROUTER_API_KEY": "sk-or-live"}
        )
        self.assertEqual(merged["hooks"], {"x": []})

    def test_env_from_missing_name_warns_and_keeps_the_existing_value(self):
        result, merged = self.run_with_env(
            "OTHER=1\n",
            '{"env": {"OPENROUTER_API_KEY": "already-there"}}\n',
            "OPENROUTER_API_KEY",
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("OPENROUTER_API_KEY not found", result.stderr)
        self.assertEqual(merged["env"]["OPENROUTER_API_KEY"], "already-there")

    def test_env_from_missing_file_warns_instead_of_failing(self):
        result, merged = self.run_with_env(None, '{"model": "opus"}\n', "OPENROUTER_API_KEY")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("not found", result.stderr)
        self.assertEqual(merged, {"model": "opus"})

    def test_claude_settings_is_credential_free_and_merges_cleanly(self):
        source = (ROOT / "claude" / "settings.json").read_text(encoding="utf-8")
        config = self.parse(source)

        self.assertNotIn("hooks", config)  # herdr owns the SessionStart hook
        self.assertNotIn("OPENROUTER_API_KEY", config.get("env", {}))
        result, _ = self.run_merger(source, '{"hooks": {"SessionStart": []}}\n')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_reports_invalid_target_json_without_a_traceback(self):
        result, text = self.run_merger('{"workflow": "auto-summary"}\n', "{ not json\n")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("invalid JSON", result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        self.assertEqual(text, "{ not json\n")  # left untouched

    def test_reports_missing_source_without_a_traceback(self):
        result, _ = self.run_merger(None, '{"provider": "all"}\n')

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("missing source config", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_rejects_non_object_source(self):
        result, _ = self.run_merger('["workflow"]\n', '{"provider": "all"}\n')

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("expected a JSON object", result.stderr)


if __name__ == "__main__":
    unittest.main()
