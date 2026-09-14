#!/usr/bin/env python3
"""Self-test for scripts/check.sh: discovery, ok/FAIL/SKIP states, the
exit-77 convention, keep-going after failures, and the git-status guard.

check.sh is run against a temporary minimal copy of the repo holding only
scripts/check.sh, stub static checks and planted tests. The copy never
contains this file, so check.sh's discovery cannot recurse into it; the
environment guard below is a second line of defence.
"""

from __future__ import annotations

import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

GUARD = "AGENT_CONFIG_CHECK_SELFTEST"
REPO = Path(__file__).resolve().parent.parent
FAILURES: list[str] = []


def expect(condition: bool, message: str, output: str = "") -> None:
    if condition:
        print(f"  ok    {message}")
    else:
        print(f"  FAIL  {message}")
        if output:
            print("        --- check.sh output ---")
            print("        " + output.replace("\n", "\n        "))
        FAILURES.append(message)


def clean_env() -> dict[str, str]:
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env[GUARD] = "1"
    return env


def git(root: Path, *args: str) -> None:
    subprocess.run(
        [
            "git",
            "-c", "user.name=check-selftest",
            "-c", "user.email=check-selftest@example.invalid",
            "-c", "commit.gpgsign=false",
            "-c", "core.hooksPath=/dev/null",
            *args,
        ],
        cwd=root,
        env=clean_env(),
        check=True,
        capture_output=True,
    )


def make_fixture(root: Path, tests: dict[str, str]) -> None:
    scripts = root / "scripts"
    scripts.mkdir(parents=True)
    shutil.copy2(REPO / "scripts" / "check.sh", scripts / "check.sh")
    for static in ("lint-skills.py", "check-zips.py"):
        (scripts / static).write_text("import sys\nsys.exit(0)\n")
    for name, body in tests.items():
        (scripts / name).write_text(body)
    git(root, "init", "-q")
    git(root, "add", ".")
    git(root, "commit", "-q", "-m", "fixture")


def run_check(root: Path) -> tuple[int, str]:
    proc = subprocess.run(
        ["bash", str(root / "scripts" / "check.sh")],
        cwd=root,
        env=clean_env(),
        capture_output=True,
        text=True,
        timeout=120,
    )
    return proc.returncode, proc.stdout + proc.stderr


def result_lines(output: str) -> dict[str, str]:
    lines = {}
    for match in re.finditer(r"^  (ok|FAIL|SKIP) +(\S+)", output, re.MULTILINE):
        lines[match.group(2)] = match.group(1)
    return lines


def test_states_and_discovery(tmp: Path) -> None:
    root = tmp / "states"
    make_fixture(
        root,
        {
            "test-aa-pass.sh": "exit 0\n",
            "test-mm-skip.py": "import sys\nsys.exit(77)\n",
            "test-note.txt": "not a runnable test\n",
            "test-pass.mjs": "process.exit(0);\n",
            "test-zz-fail.sh": "exit 3\n",
        },
    )
    code, out = run_check(root)
    states = result_lines(out)
    expect(code != 0, "a failing test makes check.sh exit non-zero", out)
    expect(states.get("test-aa-pass.sh") == "ok", "exit 0 reports ok", out)
    expect(states.get("test-pass.mjs") == "ok", ".mjs runs under node", out)
    expect(states.get("test-mm-skip.py") == "SKIP", "exit 77 reports SKIP", out)
    expect(states.get("test-zz-fail.sh") == "FAIL", "exit 3 reports FAIL", out)
    expect("test-zz-fail.sh (exit 3)" in out, "FAIL line carries the exit code", out)
    expect(
        states.get("test-note.txt") == "FAIL",
        "a test-* file with no runner is reported FAIL, not ignored",
        out,
    )
    expect(
        states.get("git-status-unchanged") == "ok",
        "a clean run passes the git-status guard",
        out,
    )
    expect(
        "5 passed, 2 failed, 1 skipped" in out,
        "summary counts passed, failed and skipped",
        out,
    )
    expect("test-check.py" not in out, "the copy does not recurse into test-check.py", out)


def test_all_pass(tmp: Path) -> None:
    root = tmp / "green"
    make_fixture(
        root,
        {"test-a.sh": "exit 0\n", "test-b.py": "import sys\nsys.exit(77)\n"},
    )
    code, out = run_check(root)
    expect(code == 0, "passes and skips alone exit 0", out)
    expect("4 passed, 0 failed, 1 skipped" in out, "green summary is accurate", out)


def test_dirty_tree(tmp: Path) -> None:
    root = tmp / "dirty"
    make_fixture(
        root,
        {"test-dirty.sh": 'touch "$(dirname "$0")/../left-behind.txt"\n'},
    )
    code, out = run_check(root)
    states = result_lines(out)
    expect(code != 0, "a run that dirties the tree exits non-zero", out)
    expect(
        states.get("git-status-unchanged") == "FAIL",
        "the git-status guard reports the change",
        out,
    )
    expect("left-behind.txt" in out, "the guard names the changed path", out)


def main() -> int:
    if os.environ.get(GUARD):
        print(f"SKIP: nested check.sh self-test ({GUARD} is set)")
        return 77
    with tempfile.TemporaryDirectory(prefix="check-selftest-") as tmpdir:
        tmp = Path(tmpdir)
        test_states_and_discovery(tmp)
        test_all_pass(tmp)
        test_dirty_tree(tmp)
    if FAILURES:
        print(f"\n{len(FAILURES)} check.sh self-test(s) failed")
        return 1
    print("\ncheck.sh self-test passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
