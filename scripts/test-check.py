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
        shutil.copy2(CHECK_SH, scripts / "check.sh")
        write(scripts / "lint-skills.py", "raise SystemExit(0)\n")
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
        self.assertEqual(rows.get("test-aa-pass.py"), "ok", result.stdout)
        self.assertEqual(rows.get("test-ab-skip.sh"), "SKIP", result.stdout)
        self.assertEqual(rows.get("test-ac-fail.py"), "FAIL", result.stdout)
        self.assertEqual(rows.get("test-ad-unsupported.txt"), "FAIL", result.stdout)
        self.assertEqual(rows.get("test-ae-continue.mjs"), "ok", result.stdout)
        self.assertEqual(rows.get("git-status-unchanged"), "ok", result.stdout)
        self.assertIn("unsupported extension", result.stdout)
        self.assertEqual(totals, ("4", "2", "1"), result.stdout)
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
        self.assertEqual(totals, ("4", "3", "1"), result.stdout)
        self.assertNotEqual(result.returncode, 0)

        # The planted artifact is what the guard noticed.
        self.assertIn("zz-dirty-artifact.txt", after)


def main() -> int:
    missing = [name for name in ("git", "node") if shutil.which(name) is None]
    if missing:
        print(f"SKIP: check self-test prerequisites missing: {', '.join(missing)}")
        return 77
    result = unittest.TextTestRunner().run(
        unittest.defaultTestLoader.loadTestsFromTestCase(CheckShSelfTest)
    )
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
