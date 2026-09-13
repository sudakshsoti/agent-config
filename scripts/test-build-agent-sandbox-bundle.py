#!/usr/bin/env python3
"""Contract tests for the committed-HEAD sandbox bootstrap bundle."""
from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "scripts/build-agent-sandbox-bundle.sh"


def run(command: list[str], *, cwd: Path | None = None, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=cwd, env=env, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return run(["git", "-C", str(repo), *args])


class BundleContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="agent-sandbox-test-")
        self.tmp = Path(self.temp.name)
        self.fixture = self.tmp / "fixture"
        clone = run(["git", "clone", "--quiet", "--no-local", str(ROOT), str(self.fixture)])
        self.assertEqual(clone.returncode, 0, clone.stderr)
        # The test also works before this change is committed: put the new
        # source into an isolated fixture, then commit that fixture's HEAD.
        source = ROOT / "sandbox/bootstrap"
        fixture_source = self.fixture / "sandbox/bootstrap"
        if not fixture_source.exists() or (source / "install.sh").read_bytes() != (fixture_source / "install.sh").read_bytes():
            fixture_source.parent.mkdir(parents=True, exist_ok=True)
            if fixture_source.exists():
                shutil.rmtree(fixture_source, ignore_errors=True)
            shutil.copytree(source, fixture_source)
        fixture_builder = self.fixture / "scripts/build-agent-sandbox-bundle.sh"
        if not fixture_builder.exists() or fixture_builder.read_bytes() != BUILDER.read_bytes():
            shutil.copy2(BUILDER, fixture_builder)
            fixture_builder.chmod(0o755)
        add = run(["git", "add", "sandbox/bootstrap", "scripts/build-agent-sandbox-bundle.sh"], cwd=self.fixture)
        self.assertEqual(add.returncode, 0, add.stderr)
        commit = run(["git", "-c", "user.name=Bundle Test", "-c", "user.email=bundle-test@example.invalid", "commit", "--quiet", "-m", "test fixture"], cwd=self.fixture)
        self.assertEqual(commit.returncode, 0, commit.stderr)
        self.output = self.tmp / "bundle"
        self.build()

    def tearDown(self) -> None:
        self.temp.cleanup()

    def build(self, output: Path | None = None, cwd: Path | None = None, home: Path | None = None) -> subprocess.CompletedProcess[str]:
        environment = os.environ.copy()
        if home is not None:
            environment["HOME"] = str(home)
        return run(
            [str((cwd or self.fixture) / "scripts/build-agent-sandbox-bundle.sh"), "--output", str(output or self.output)],
            cwd=cwd or self.fixture,
            env=environment,
        )

    def install(self, bundle: Path, home: Path, *args: str, path: str | None = None) -> subprocess.CompletedProcess[str]:
        environment = os.environ.copy()
        environment["HOME"] = str(home)
        if path is not None:
            environment["PATH"] = path
        return run([str(bundle / "install.sh"), *args], env=environment)

    def test_bundle_is_allowlisted_and_has_metadata(self) -> None:
        self.assertTrue((self.output / "install.sh").exists())
        self.assertEqual((self.output / "VERSION").read_text().splitlines()[0], "bundle_format=1")
        self.assertEqual(
            (self.output / ".agent-config-sandbox-bundle").read_text(),
            "agent-config-sandbox-bundle:1\n",
        )
        metadata = (self.output / "VERSION").read_text()
        self.assertIn("pi_target_version=0.85.1", metadata)
        self.assertIn("omp_target_version=18.1.19", metadata)
        self.assertIn("sbx_tested_version=0.42.1", metadata)
        head_commit = git(self.fixture, "rev-parse", "HEAD").stdout.strip()
        self.assertIn(f"commit={head_commit}", metadata)
        self.assertEqual(
            {path.name for path in self.output.iterdir()},
            {"install.sh", "manifest.txt", "VERSION", "SHA256SUMS", "snapshot", ".agent-config-sandbox-bundle"},
        )
        paths = {str(path.relative_to(self.output)) for path in self.output.rglob("*")}
        forbidden = ("auth.json", "models-store", "mcp.json", "web-search.json", ".env", "vendor", "sessions", "cache", "database", "omp/agents", "pi/pi-fff.json")
        for item in forbidden:
            self.assertFalse(any(item in path for path in paths), item)
        self.assertTrue((self.output / "snapshot/pi/extensions/catastrophe-guard/index.js").exists())
        self.assertTrue((self.output / "snapshot/omp/config.yml").exists())
        self.assertFalse((self.output / "snapshot/pi/web-search.json").exists())
        self.assertFalse((self.output / "snapshot/omp/agents").exists())

        # The snapshot is exactly the committed allowlist: every file that a
        # committed manifest entry (expanded from HEAD, never the worktree)
        # denotes, and nothing else.
        manifest_text = git(self.fixture, "show", "HEAD:sandbox/bootstrap/manifest.txt").stdout
        allowlist: set[str] = set()
        for line in manifest_text.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if line.endswith("/"):
                listed = git(self.fixture, "ls-tree", "-r", "--name-only", "HEAD", "--", line).stdout.splitlines()
                self.assertTrue(listed, line)
                allowlist.update(listed)
            else:
                allowlist.add(line)
        bundled = {
            str(path.relative_to(self.output / "snapshot"))
            for path in (self.output / "snapshot").rglob("*")
            if path.is_file()
        }
        self.assertEqual(bundled, allowlist)

        # Exported bytes come from committed HEAD, not the working tree.
        for relative in ("global-agents.md", "pi/settings.json", "omp/config.yml"):
            committed = git(self.fixture, "show", f"HEAD:{relative}").stdout
            self.assertEqual((self.output / "snapshot" / relative).read_text(), committed)

        checks = (self.output / "SHA256SUMS").read_text().splitlines()
        self.assertGreater(len(checks), 10)
        for line in checks:
            digest, relative = line.split("  ", 1)
            self.assertEqual(len(digest), 64)
            self.assertTrue((self.output / relative).is_file())

    def test_unrelated_untracked_file_is_tolerated_but_selected_dirty_content_is_refused(self) -> None:
        unrelated = self.fixture / "docs/local-note.md"
        unrelated.parent.mkdir(exist_ok=True)
        unrelated.write_text("local only\n")
        tolerated = self.tmp / "tolerated-bundle"
        result = self.build(tolerated)
        self.assertEqual(result.returncode, 0, result.stderr)

        selected = self.fixture / "pi/settings.json"
        original = selected.read_text()
        selected.write_text(original + "\n")
        refused = self.build(self.tmp / "dirty-bundle")
        self.assertNotEqual(refused.returncode, 0)
        self.assertIn("selected path is dirty", refused.stderr)
        selected.write_text(original)

        untracked_selected = self.fixture / "pi/prompts/local.md"
        untracked_selected.write_text("must not leak\n")
        refused_untracked = self.build(self.tmp / "untracked-bundle")
        self.assertNotEqual(refused_untracked.returncode, 0)
        self.assertIn("selected path has untracked content", refused_untracked.stderr)

    def test_output_inside_repository_is_refused(self) -> None:
        result = self.build(self.fixture / "output-inside-repo")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("outside the repository", result.stderr)

    def test_output_under_home_dev_is_refused(self) -> None:
        fake_home = self.tmp / "fake-home"
        target = fake_home / "dev" / "workspace" / "bundle"
        target.parent.mkdir(parents=True)
        result = self.build(target, home=fake_home)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("HOME/dev", result.stderr)
        self.assertFalse(target.exists())
        self.assertEqual({path.name for path in (fake_home / "dev").iterdir()}, {"workspace"})

    def test_existing_unmarked_directory_is_refused_and_preserved(self) -> None:
        target = self.tmp / "unmarked-dir"
        target.mkdir()
        sentinel = target / "keep.txt"
        sentinel.write_text("do not touch\n")
        result = self.build(target)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unmarked output directory", result.stderr)
        self.assertEqual(sentinel.read_text(), "do not touch\n")
        self.assertEqual(sorted(path.name for path in target.iterdir()), ["keep.txt"])

    def test_existing_unmarked_file_is_refused_and_preserved(self) -> None:
        target = self.tmp / "unmarked-file"
        target.write_text("not a bundle\n")
        result = self.build(target)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("existing non-directory output", result.stderr)
        self.assertEqual(target.read_text(), "not a bundle\n")

    def test_existing_directory_with_wrong_marker_is_refused(self) -> None:
        target = self.tmp / "wrong-marker"
        target.mkdir()
        (target / ".agent-config-sandbox-bundle").write_text("some-other-tool\n")
        sentinel = target / "keep.txt"
        sentinel.write_text("keep\n")
        result = self.build(target)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unrecognized bundle marker", result.stderr)
        self.assertEqual(sentinel.read_text(), "keep\n")

    def test_marked_prior_bundle_is_replaced(self) -> None:
        marker = self.output / ".agent-config-sandbox-bundle"
        self.assertEqual(marker.read_text(), "agent-config-sandbox-bundle:1\n")
        obsolete = self.output / "obsolete.txt"
        obsolete.write_text("stale\n")
        head_commit = git(self.fixture, "rev-parse", "HEAD").stdout.strip()
        rebuilt = self.build()
        self.assertEqual(rebuilt.returncode, 0, rebuilt.stderr)
        self.assertFalse(obsolete.exists())
        self.assertTrue((self.output / "install.sh").is_file())
        self.assertEqual(marker.read_text(), "agent-config-sandbox-bundle:1\n")
        self.assertIn(f"commit={head_commit}", (self.output / "VERSION").read_text())

    def test_filesystem_root_output_is_refused(self) -> None:
        result = self.build(Path("/"))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("filesystem root", result.stderr)

    def test_linked_worktree_builds_and_shared_checkout_output_is_refused(self) -> None:
        worktree = self.tmp / "linked-worktree"
        add = git(self.fixture, "worktree", "add", "--quiet", "--detach", str(worktree), "HEAD")
        self.assertEqual(add.returncode, 0, add.stderr)
        # The builder runs from a linked worktree, where .git is a file.
        outside = self.tmp / "worktree-bundle"
        built = self.build(outside, cwd=worktree)
        self.assertEqual(built.returncode, 0, built.stderr)
        self.assertTrue((outside / "VERSION").exists())
        # Output must not land in the checkout that hosts the linked worktree.
        stray = self.build(self.fixture / "stray-output", cwd=worktree)
        self.assertNotEqual(stray.returncode, 0)
        self.assertIn("outside the source repository", stray.stderr)

    def test_home_with_symlinked_ancestor_is_supported(self) -> None:
        # macOS exposes mktemp paths through /var -> /private/var; the installer
        # must canonicalize existing ancestors instead of rejecting them.
        real_parent = self.tmp / "real-home-parent"
        home = real_parent / "home"
        home.mkdir(parents=True)
        link_parent = self.tmp / "link-parent"
        link_parent.symlink_to(real_parent, target_is_directory=True)
        result = self.install(self.output, link_parent / "home", "--config-only")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((home / ".pi/agent/settings.json").is_file())
        self.assertTrue((home / ".omp/agent/config.yml").is_file())

    def test_config_directory_symlink_escaping_home_is_refused(self) -> None:
        home = self.tmp / "escaping-home"
        (home / ".pi").mkdir(parents=True)
        outside = self.tmp / "outside-target"
        outside.mkdir()
        (home / ".pi/agent").symlink_to(outside, target_is_directory=True)
        result = self.install(self.output, home, "--config-only")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("escapes HOME", result.stderr)
        self.assertEqual(list(outside.iterdir()), [])

    def test_config_only_is_idempotent_and_preserves_unmanaged_state(self) -> None:
        home = self.tmp / "home"
        (home / ".pi/agent").mkdir(parents=True)
        (home / ".omp/agent").mkdir(parents=True)
        (home / ".config/omp").mkdir(parents=True)
        runtime = home / ".pi/agent/runtime-state.db"
        runtime.write_text("do not remove\n")
        omp_runtime = home / ".omp/agent/session.sqlite"
        omp_runtime.write_text("do not remove\n")
        first = self.install(self.output, home, "--config-only")
        self.assertEqual(first.returncode, 0, first.stderr)
        second = self.install(self.output, home, "--config-only")
        self.assertEqual(second.returncode, 0, second.stderr)
        self.assertEqual(runtime.read_text(), "do not remove\n")
        self.assertEqual(omp_runtime.read_text(), "do not remove\n")
        self.assertEqual((home / ".pi/agent/AGENTS.md").read_text(), (self.output / "snapshot/global-agents.md").read_text())
        self.assertEqual((home / ".omp/agent/config.yml").read_text(), (self.output / "snapshot/omp/config.yml").read_text())
        self.assertTrue((home / ".agents/skills/design-interface").is_dir())
        self.assertFalse((home / ".agents/skills/design-interface").is_symlink())
        self.assertTrue((home / ".pi/agent/extensions/catastrophe-guard/index.js").exists())
        self.assertTrue((home / ".config/omp/go-overlay.yml").exists())
        self.assertFalse((home / ".pi/agent/web-search.json").exists())

        managed = home / ".pi/agent/settings.json"
        managed.write_text("local edit\n")
        rerun = self.install(self.output, home, "--config-only")
        self.assertEqual(rerun.returncode, 0, rerun.stderr)
        self.assertEqual(managed.read_text(), (self.output / "snapshot/pi/settings.json").read_text())

    def test_missing_manifest_tampering_and_path_escape_are_refused(self) -> None:
        missing = self.tmp / "missing-manifest"
        shutil.copytree(self.output, missing)
        (missing / "manifest.txt").unlink()
        home = self.tmp / "missing-home"
        home.mkdir()
        result = self.install(missing, home, "--config-only")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("missing manifest", result.stderr)

        tampered = self.tmp / "tampered"
        shutil.copytree(self.output, tampered)
        payload = tampered / "snapshot/pi/settings.json"
        payload.write_text(payload.read_text() + "tampered\n")
        tampered_home = self.tmp / "tampered-home"
        tampered_home.mkdir()
        result = self.install(tampered, tampered_home, "--config-only")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("checksum mismatch", result.stderr)

        escaping = self.tmp / "escaping"
        shutil.copytree(self.output, escaping)
        manifest = escaping / "manifest.txt"
        manifest.write_text(manifest.read_text() + "../../outside\n")
        # Make the deliberate manifest edit pass the checksum stage, so the
        # installer reaches its lexical path validation.
        import hashlib
        digest = hashlib.sha256(manifest.read_bytes()).hexdigest()
        checks = escaping / "SHA256SUMS"
        lines = checks.read_text().splitlines()
        checks.write_text("\n".join((f"{digest}  manifest.txt" if line.endswith("  manifest.txt") else line) for line in lines) + "\n")
        escaping_home = self.tmp / "escaping-home"
        escaping_home.mkdir()
        result = self.install(escaping, escaping_home, "--config-only")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unsafe manifest path", result.stderr)

    def test_required_binary_version_mismatch_fails(self) -> None:
        home = self.tmp / "version-home"
        home.mkdir()
        bin_dir = self.tmp / "bin"
        bin_dir.mkdir()
        for name in ("pi", "omp"):
            program = bin_dir / name
            program.write_text("#!/bin/sh\necho wrong-version\n")
            program.chmod(0o755)
        result = self.install(self.output, home, path=f"{bin_dir}:{os.environ['PATH']}")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("required", result.stderr)
        self.assertFalse((home / ".pi/agent/settings.json").exists())

    def test_matching_binary_versions_install_configuration(self) -> None:
        home = self.tmp / "pinned-home"
        home.mkdir()
        bin_dir = self.tmp / "pinned-bin"
        bin_dir.mkdir()
        for name, version in (("pi", "0.85.1"), ("omp", "18.1.19")):
            program = bin_dir / name
            program.write_text(f"#!/bin/sh\necho '{name} {version}'\n")
            program.chmod(0o755)
        result = self.install(self.output, home, path=f"{bin_dir}:{os.environ['PATH']}")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("verified pi 0.85.1 / omp 18.1.19", result.stdout)
        self.assertTrue((home / ".pi/agent/settings.json").is_file())


if __name__ == "__main__":
    unittest.main()
