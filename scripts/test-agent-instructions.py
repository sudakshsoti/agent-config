#!/usr/bin/env python3
"""Behaviour tests for cohort instruction validation and wrapper repair."""

import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / "scripts" / "check-agent-instructions.py"
REPAIR = ROOT / "scripts" / "repair-agent-instructions.py"


class InstructionToolsTest(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)
        self.manifest = self.root / "manifest.json"

    def tearDown(self):
        self.tempdir.cleanup()

    def write_manifest(self, scopes=None):
        data = {"repositories": [{"path": "repo", "scopes": scopes or ["."]}]}
        self.manifest.write_text(json.dumps(data), encoding="utf-8")

    def write_deferred_manifest(self):
        data = {"repositories": [{
            "path": "repo", "scopes": ["."],
            "deferred": "unrelated dirty working tree"
        }]}
        self.manifest.write_text(json.dumps(data), encoding="utf-8")

    def write_scope(self, relative=".", agents="# Project\n\nUse pnpm.\n", claude="@AGENTS.md\n"):
        scope = self.root / "repo" / relative
        scope.mkdir(parents=True, exist_ok=True)
        if agents is not None:
            (scope / "AGENTS.md").write_text(agents, encoding="utf-8")
        if claude is not None:
            (scope / "CLAUDE.md").write_text(claude, encoding="utf-8")
        return scope

    def run_tool(self, tool, *extra):
        return subprocess.run(
            ["python3", str(tool), "--manifest", str(self.manifest),
             "--cohort-root", str(self.root), *extra],
            text=True,
            capture_output=True,
            check=False,
        )

    def test_valid_wrapper_and_optional_claude_section_pass(self):
        self.write_manifest()
        self.write_scope(claude="\n@AGENTS.md\n\n# Claude-specific\n\nUse plan mode.\n")
        result = self.run_tool(CHECKER)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_missing_files_are_reported(self):
        self.write_manifest()
        (self.root / "repo").mkdir()
        result = self.run_tool(CHECKER)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("missing AGENTS.md", result.stdout)
        self.assertIn("missing CLAUDE.md", result.stdout)

    def test_malformed_import_and_duplicated_body_are_reported(self):
        self.write_manifest()
        self.write_scope(claude="# Claude\n\n@AGENTS.md\n\n# Project\n\nUse pnpm.\n")
        result = self.run_tool(CHECKER)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("first active line must be exactly @AGENTS.md", result.stdout)
        self.assertIn("duplicates AGENTS.md content", result.stdout)

    def test_nested_scope_and_oversized_agents_are_checked(self):
        self.write_manifest([".", "workflows"])
        self.write_scope()
        self.write_scope("workflows", agents="\n".join(f"line {i}" for i in range(201)) + "\n")
        result = self.run_tool(CHECKER)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("repo/workflows/AGENTS.md has 201 lines", result.stdout)

    def test_symlinked_files_are_rejected(self):
        self.write_manifest()
        scope = self.write_scope(claude=None)
        os.symlink("AGENTS.md", scope / "CLAUDE.md")
        result = self.run_tool(CHECKER)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unexpected symlink CLAUDE.md", result.stdout)

    def test_repair_dry_run_does_not_write_and_apply_only_fixes_wrapper(self):
        self.write_manifest()
        scope = self.write_scope(claude="# wrong\n")
        original_agents = (scope / "AGENTS.md").read_text(encoding="utf-8")

        dry_run = self.run_tool(REPAIR)
        self.assertEqual(dry_run.returncode, 0, dry_run.stdout + dry_run.stderr)
        self.assertIn("would replace", dry_run.stdout)
        self.assertEqual((scope / "CLAUDE.md").read_text(), "# wrong\n")

        applied = self.run_tool(REPAIR, "--apply")
        self.assertEqual(applied.returncode, 0, applied.stdout + applied.stderr)
        self.assertEqual((scope / "CLAUDE.md").read_text(), "@AGENTS.md\n")
        self.assertEqual((scope / "AGENTS.md").read_text(), original_agents)

    def test_repair_refuses_to_create_canonical_content(self):
        self.write_manifest()
        (self.root / "repo").mkdir()
        result = self.run_tool(REPAIR, "--apply")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("refusing: missing AGENTS.md", result.stdout)
        self.assertFalse((self.root / "repo" / "CLAUDE.md").exists())

    def test_skip_deferred_is_explicit_and_does_not_claim_it_was_checked(self):
        self.write_deferred_manifest()
        (self.root / "repo").mkdir()
        result = self.run_tool(CHECKER, "--skip-deferred")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("SKIP repo: unrelated dirty working tree", result.stdout)
        self.assertIn("0 checked, 1 deferred", result.stdout)


if __name__ == "__main__":
    unittest.main()
