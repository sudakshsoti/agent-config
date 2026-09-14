#!/usr/bin/env python3
"""Self-test for scripts/check.sh.

check.sh is the repo's verification entry point, so its own discovery, skip and
working-tree-guard behaviour is worth testing rather than trusting. Each case
runs check.sh against a disposable copy of a minimal scripts/ directory holding
the real check.sh, a stub static check and planted tests.

The copy never contains this file, so discovery cannot re-run the self-test and
recurse. Standard library only, so check.sh can run it wherever python3 exists.
"""

from __future__ import annotations

import contextlib
import os
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
CHECK_SH = REPO_ROOT / "scripts" / "check.sh"

RESULT_LINE = re.compile(
    r"^  (?P<status>ok|FAIL|SKIP)\s+(?P<label>\S+)(?:\s+\((?P<detail>[^)]*)\))?$"
)
TOTALS_LINE = re.compile(
    r"^(?P<pass>\d+) passed, (?P<fail>\d+) failed, (?P<skip>\d+) skipped$"
)

# Git identity and isolation for the disposable repo, so neither the machine's
# git config nor a missing identity can change what the guard sees.
GIT_ENV = {
    "GIT_AUTHOR_NAME": "check self-test",
    "GIT_AUTHOR_EMAIL": "check-self-test@example.invalid",
    "GIT_COMMITTER_NAME": "check self-test",
    "GIT_COMMITTER_EMAIL": "check-self-test@example.invalid",
    "GIT_CONFIG_NOSYSTEM": "1",
    "GIT_CONFIG_GLOBAL": os.devnull,
}
QUIET_STDOUT = subprocess.DEVNULL
QUIET_STDERR = subprocess.DEVNULL


def isolated_git_environment() -> dict[str, str]:
    """Run fixture Git with no repository selectors inherited from the host."""
    environment = {
        key: value for key, value in os.environ.items() if not key.startswith("GIT_")
    }
    environment.update(GIT_ENV)
    return environment

PASS_STUB = "print('pass stub')\n"
SKIP_STUB = "exit 77\n"
FAIL_STUB = "raise SystemExit(1)\n"
CONTINUE_STUB = "console.log('continue stub');\n"
UNSUPPORTED_STUB = "not a runnable test\n"
DIRTY_STUB = 'echo "artifact" > "$(dirname "$0")/zz-dirty-artifact.txt"\n'


def write(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")


def init_git(root: Path) -> None:
    env = isolated_git_environment()
    subprocess.run(
        ["git", "init", "-q", str(root)],
        check=True,
        env=env,
        stdout=QUIET_STDOUT,
        stderr=QUIET_STDERR,
    )
    subprocess.run(
        ["git", "-C", str(root), "add", "-A"],
        check=True,
        env=env,
        stdout=QUIET_STDOUT,
        stderr=QUIET_STDERR,
    )
    subprocess.run(
        ["git", "-C", str(root), "commit", "-q", "-m", "init"],
        check=True,
        env=env,
        stdout=QUIET_STDOUT,
        stderr=QUIET_STDERR,
    )


@contextlib.contextmanager
def disposable_copy(*, include_dirty: bool):
    """A minimal git checkout whose scripts/ holds the real check.sh."""
    with tempfile.TemporaryDirectory(prefix="check-self-test-") as tmp:
        root = Path(tmp)
        scripts = root / "scripts"
        scripts.mkdir()
        # A present pi-tui marker means the bootstrap step has nothing to do,
        # so these general discovery/guard cases stay unaffected by it.
        pi_tui_marker = root / "node_modules" / "@earendil-works" / "pi-tui"
        pi_tui_marker.mkdir(parents=True)
        shutil.copy2(CHECK_SH, scripts / "check.sh")
        write(scripts / "lint-skills.py", "raise SystemExit(0)\n")
        write(scripts / "check-manifest.py", "raise SystemExit(0)\n")
        write(scripts / "test-aa-pass.py", PASS_STUB)
        write(scripts / "test-ab-skip.sh", SKIP_STUB)
        write(scripts / "test-ac-fail.py", FAIL_STUB)
        write(scripts / "test-ad-unsupported.txt", UNSUPPORTED_STUB)
        write(scripts / "test-ae-continue.mjs", CONTINUE_STUB)
        if include_dirty:
            write(scripts / "test-af-dirty.sh", DIRTY_STUB)
        init_git(root)
        yield root


def run_check(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", str(root / "scripts" / "check.sh")],
        cwd=str(root),
        capture_output=True,
        text=True,
        env=isolated_git_environment(),
    )


def git_status(root: Path) -> str:
    result = subprocess.run(
        ["git", "-C", str(root), "status", "--porcelain"],
        check=True,
        capture_output=True,
        text=True,
        env=isolated_git_environment(),
    )
    return result.stdout


def parse(output: str) -> tuple[dict[str, str], tuple[str, str, str] | None]:
    rows: dict[str, str] = {}
    totals = None
    for line in output.splitlines():
        match = RESULT_LINE.match(line)
        if match:
            rows[match.group("label")] = match.group("status")
        totals_match = TOTALS_LINE.match(line)
        if totals_match:
            totals = (
                totals_match.group("pass"),
                totals_match.group("fail"),
                totals_match.group("skip"),
            )
    return rows, totals


class CheckShSelfTest(unittest.TestCase):
    def test_reports_every_status_and_keeps_going(self):
        with disposable_copy(include_dirty=False) as root:
            before = git_status(root)
            result = run_check(root)
            after = git_status(root)

        rows, totals = parse(result.stdout)
        self.assertEqual(rows.get("lint-skills.py"), "ok", result.stdout)
        self.assertEqual(rows.get("check-manifest.py"), "ok", result.stdout)
        self.assertEqual(rows.get("test-aa-pass.py"), "ok", result.stdout)
        self.assertEqual(rows.get("test-ab-skip.sh"), "SKIP", result.stdout)
        self.assertEqual(rows.get("test-ac-fail.py"), "FAIL", result.stdout)
        self.assertEqual(rows.get("test-ad-unsupported.txt"), "FAIL", result.stdout)
        self.assertEqual(rows.get("test-ae-continue.mjs"), "ok", result.stdout)
        self.assertEqual(rows.get("git-status-unchanged"), "ok", result.stdout)
        self.assertIn("unsupported extension", result.stdout)
        self.assertEqual(totals, ("5", "2", "1"), result.stdout)
        self.assertNotEqual(result.returncode, 0)

        # The .mjs stub is discovered after the failures and still ran.
        labels = []
        for line in result.stdout.splitlines():
            match = RESULT_LINE.match(line)
            if match:
                labels.append(match.group("label"))
        self.assertLess(
            labels.index("test-ac-fail.py"),
            labels.index("test-ae-continue.mjs"),
        )

        # The clean run is non-recursive and leaves the tree exactly as it was.
        self.assertNotIn("test-check.py", rows)
        self.assertEqual(before, "")
        self.assertEqual(after, "")

    def test_fails_when_a_test_dirties_the_tree(self):
        with disposable_copy(include_dirty=True) as root:
            result = run_check(root)
            after = git_status(root)

        rows, totals = parse(result.stdout)
        self.assertEqual(rows.get("git-status-unchanged"), "FAIL", result.stdout)
        self.assertIn("working tree changed", result.stdout)
        self.assertEqual(totals, ("5", "3", "1"), result.stdout)
        self.assertNotEqual(result.returncode, 0)

        # The planted artifact is what the guard noticed.
        self.assertIn("zz-dirty-artifact.txt", after)


def find_tool(name: str) -> str:
    path = shutil.which(name)
    if path is None:
        raise unittest.SkipTest(f"{name} not found on PATH")
    return path


def make_shim(shim_dir: Path, tools: tuple[str, ...]) -> None:
    """Symlink only the named real executables into an otherwise-empty dir."""
    shim_dir.mkdir(parents=True, exist_ok=True)
    for tool in tools:
        (shim_dir / tool).symlink_to(find_tool(tool))


def write_npm_logging_shim(shim_dir: Path, log_path: Path) -> None:
    """A fake `npm` that records its argv and plants the pi-tui marker.

    Standing in for a real `npm ci`, so tests never touch the network or the
    real dependency tree: it only proves check.sh calls it at most once per
    missing-dependency state, with the expected flags.
    """
    shim_dir.mkdir(parents=True, exist_ok=True)
    npm_path = shim_dir / "npm"
    write(
        npm_path,
        "#!/usr/bin/env bash\n"
        f'echo "$*" >> {shlex_quote(str(log_path))}\n'
        'if [[ "$1" == "ci" ]]; then\n'
        '  mkdir -p "node_modules/@earendil-works/pi-tui"\n'
        "fi\n"
        "exit 0\n",
    )
    npm_path.chmod(0o755)


def shlex_quote(value: str) -> str:
    return "'" + value.replace("'", "'\\''") + "'"


@contextlib.contextmanager
def npm_bootstrap_fixture(tmp: Path):
    """A minimal git checkout for the npm-bootstrap / skip-rule self-tests.

    Deliberately smaller than disposable_copy: only the static-check stubs and
    the two discovery cases these tests care about (a `requires-npm`-marked
    .mjs and a plain one), so PATH restriction is the only variable per case.
    """
    root = tmp / "repo"
    scripts = root / "scripts"
    scripts.mkdir(parents=True)
    # Mirrors the real repo: node_modules/ is a gitignored, npm-ci-restorable
    # build product, so the bootstrap step creating it must not trip the
    # working-tree guard.
    write(root / ".gitignore", "node_modules/\n")
    shutil.copy2(CHECK_SH, scripts / "check.sh")
    write(scripts / "lint-skills.py", "raise SystemExit(0)\n")
    write(scripts / "check-manifest.py", "raise SystemExit(0)\n")
    write(
        scripts / "test-zz-requires-npm.mjs",
        '// check.sh: requires-npm\nconsole.log("ran");\n',
    )
    write(scripts / "test-zz-plain.mjs", 'console.log("ran");\n')
    init_git(root)
    yield root


def run_check_with_path(root: Path, path_value: str) -> subprocess.CompletedProcess[str]:
    env = isolated_git_environment()
    env["PATH"] = path_value
    return subprocess.run(
        [find_tool("bash"), str(root / "scripts" / "check.sh")],
        cwd=str(root),
        capture_output=True,
        text=True,
        env=env,
    )


class NpmBootstrapSelfTest(unittest.TestCase):
    """Issue #35: bootstrap npm's ignored node_modules/ and skip cleanly."""

    def test_npm_missing_skips_marked_test_and_runs_plain_one(self):
        with tempfile.TemporaryDirectory(prefix="check-npm-bootstrap-") as tmp_str:
            tmp = Path(tmp_str)
            with npm_bootstrap_fixture(tmp) as root:
                shim = tmp / "shim"
                make_shim(shim, ("node", "python3", "bash", "git"))
                result = run_check_with_path(root, str(shim))

        rows, totals = parse(result.stdout)
        self.assertEqual(
            rows.get("test-zz-requires-npm.mjs"), "SKIP", result.stdout
        )
        self.assertIn(
            "dependency unavailable: npm not found", result.stdout
        )
        self.assertEqual(rows.get("test-zz-plain.mjs"), "ok", result.stdout)
        self.assertEqual(rows.get("npm-ci-bootstrap"), "SKIP", result.stdout)
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_node_missing_skips_every_js_test(self):
        with tempfile.TemporaryDirectory(prefix="check-node-missing-") as tmp_str:
            tmp = Path(tmp_str)
            with npm_bootstrap_fixture(tmp) as root:
                shim = tmp / "shim"
                make_shim(shim, ("python3", "bash", "git"))
                result = run_check_with_path(root, str(shim))

        rows, totals = parse(result.stdout)
        self.assertEqual(
            rows.get("test-zz-requires-npm.mjs"), "SKIP", result.stdout
        )
        self.assertEqual(rows.get("test-zz-plain.mjs"), "SKIP", result.stdout)
        self.assertIn("dependency unavailable: node not found", result.stdout)
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_npm_shim_runs_ci_once_then_stays_quiet(self):
        with tempfile.TemporaryDirectory(prefix="check-npm-shim-") as tmp_str:
            tmp = Path(tmp_str)
            with npm_bootstrap_fixture(tmp) as root:
                log_path = tmp / "npm-invocations.log"
                write(log_path, "")
                shim = tmp / "shim"
                # mkdir is only for the fake npm's own use (simulating what a
                # real `npm ci` would restore), not a check.sh dependency.
                make_shim(shim, ("node", "python3", "bash", "git", "mkdir"))
                write_npm_logging_shim(shim, log_path)
                path_value = str(shim)

                first = run_check_with_path(root, path_value)
                first_rows, _ = parse(first.stdout)
                self.assertEqual(
                    first_rows.get("npm-ci-bootstrap"), "ok", first.stdout
                )
                self.assertEqual(
                    first_rows.get("test-zz-requires-npm.mjs"),
                    "ok",
                    first.stdout,
                )
                first_log = log_path.read_text(encoding="utf-8").strip()
                self.assertEqual(
                    first_log, "ci --ignore-scripts --no-audit --no-fund"
                )
                self.assertTrue(
                    (root / "node_modules" / "@earendil-works" / "pi-tui").is_dir()
                )

                write(log_path, "")
                second = run_check_with_path(root, path_value)
                second_rows, _ = parse(second.stdout)
                self.assertNotIn("npm-ci-bootstrap", second_rows)
                self.assertEqual(
                    second_rows.get("test-zz-requires-npm.mjs"),
                    "ok",
                    second.stdout,
                )
                self.assertEqual(
                    log_path.read_text(encoding="utf-8"),
                    "",
                    "second run must not invoke npm again",
                )


def main() -> int:
    missing = [name for name in ("git", "node") if shutil.which(name) is None]
    if missing:
        print(f"SKIP: check self-test prerequisites missing: {', '.join(missing)}")
        return 77
    loader = unittest.defaultTestLoader
    suite = unittest.TestSuite(
        [
            loader.loadTestsFromTestCase(CheckShSelfTest),
            loader.loadTestsFromTestCase(NpmBootstrapSelfTest),
        ]
    )
    result = unittest.TextTestRunner().run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
