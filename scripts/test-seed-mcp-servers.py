#!/usr/bin/env python3
"""Regression tests for seed-mcp-servers.py."""

from pathlib import Path
import json
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SEEDER = ROOT / "scripts" / "seed-mcp-servers.py"


def run(mode, source, target):
    with tempfile.TemporaryDirectory() as temporary:
        directory = Path(temporary)
        source_path = directory / "source.json"
        target_path = directory / "target.json"
        source_path.write_text(json.dumps(source), encoding="utf-8")
        if target is not None:
            target_path.write_text(json.dumps(target), encoding="utf-8")
        result = subprocess.run(
            ["python3", str(SEEDER), mode, str(source_path), str(target_path)],
            text=True,
            capture_output=True,
            check=False,
        )
        live = (
            json.loads(target_path.read_text(encoding="utf-8"))
            if target_path.exists()
            else None
        )
        return result, live


HTTP = {"type": "http", "url": "https://example.test/mcp"}


class SeedMcpServersTest(unittest.TestCase):
    def test_merge_adds_missing_servers_and_preserves_unrelated_keys(self):
        result, live = run(
            "merge",
            {"mcpServers": {"new": HTTP}},
            {"mcpServers": {"old": HTTP}, "disabledServers": ["linear"]},
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(set(live["mcpServers"]), {"old", "new"})
        self.assertEqual(live["disabledServers"], ["linear"])

    def test_merge_never_edits_an_existing_server(self):
        tool_edited = {**HTTP, "credentialId": "local-oauth-state"}
        result, live = run(
            "merge", {"mcpServers": {"s": HTTP}}, {"mcpServers": {"s": tool_edited}}
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(live["mcpServers"]["s"], tool_edited)

    def test_merge_creates_the_target_when_absent(self):
        result, live = run("merge", {"mcpServers": {"s": HTTP}}, None)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(live, {"mcpServers": {"s": HTTP}})

    def test_missing_lists_only_absent_servers_as_name_tab_json(self):
        result, _ = run(
            "missing",
            {"mcpServers": {"have": HTTP, "lack": HTTP}},
            {"mcpServers": {"have": HTTP}, "userID": "state-blob"},
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        name, _, payload = result.stdout.strip().partition("\t")
        self.assertEqual(name, "lack")
        self.assertEqual(json.loads(payload), HTTP)

    def test_refuses_a_server_carrying_inline_credentials(self):
        for carrier in ("env", "headers"):
            with self.subTest(carrier=carrier):
                result, live = run(
                    "merge",
                    {"mcpServers": {"s": {**HTTP, carrier: {"K": "sk-live"}}}},
                    None,
                )

                self.assertNotEqual(result.returncode, 0)
                self.assertIn("inline credentials", result.stderr)
                self.assertIsNone(live)

    def test_repo_snapshots_are_seedable(self):
        for snapshot in ("claude", "omp"):
            with self.subTest(snapshot=snapshot):
                result = subprocess.run(
                    [
                        "python3",
                        str(SEEDER),
                        "missing",
                        str(ROOT / "snapshots" / snapshot / "mcp.json"),
                        "/nonexistent/target.json",
                    ],
                    text=True,
                    capture_output=True,
                    check=False,
                )
                self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
