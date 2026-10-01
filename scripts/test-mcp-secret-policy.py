#!/usr/bin/env python3
"""Tests for the shared MCP secret-refusal policy (snapshot and seed)."""

from pathlib import Path
import json
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SERVER_WITH_ENV = {"type": "stdio", "command": "x", "env": {"API_KEY": "sk-live-123"}}


class McpSecretPolicyTest(unittest.TestCase):
    def test_env_server_refused_by_snapshot_and_seed(self):
        document = {"mcpServers": {"leaky": SERVER_WITH_ENV}}
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "mcp.json"
            source.write_text(json.dumps(document), encoding="utf-8")

            scan = subprocess.run(
                ["python3", str(SCRIPTS / "mcp_secret_policy.py"), str(source)],
                text=True, capture_output=True, check=False,
            )
            seed = subprocess.run(
                ["python3", str(SCRIPTS / "seed-mcp-servers.py"), "merge",
                 str(source), str(Path(temporary) / "target.json")],
                text=True, capture_output=True, check=False,
            )
        self.assertEqual(scan.returncode, 0, "snapshot scan must flag the file")
        self.assertIn("mcpServers.leaky.env", scan.stdout)
        self.assertNotEqual(seed.returncode, 0)
        self.assertIn("env", seed.stderr)

    def test_clean_server_and_empty_env_pass_shared_policy(self):
        document = {"mcpServers": {"ok": {"type": "http", "url": "https://e.test", "env": {}}}}
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "mcp.json"
            source.write_text(json.dumps(document), encoding="utf-8")
            scan = subprocess.run(
                ["python3", str(SCRIPTS / "mcp_secret_policy.py"), str(source)],
                text=True, capture_output=True, check=False,
            )
        self.assertEqual(scan.returncode, 1)

    def test_snapshot_flags_secret_field_outside_mcp_servers(self):
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "x.json"
            source.write_text(json.dumps({"a": {"token": "abc"}, "env": "segment"}), encoding="utf-8")
            scan = subprocess.run(
                ["python3", str(SCRIPTS / "mcp_secret_policy.py"), str(source)],
                text=True, capture_output=True, check=False,
            )
        self.assertEqual(scan.stdout.split(), ["a.token"])


if __name__ == "__main__":
    unittest.main()
