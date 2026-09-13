#!/usr/bin/env python3
"""Regression tests for the omp catastrophe-guard policy in omp/config.yml.

The omp guard is declarative: omp applies `bash.patterns` in order, so what is
worth testing is the presence, exact spelling and order of the rule lines. The
Pi side of the same guard is covered by scripts/test-catastrophe-guard.mjs.

Standard library only, so check.sh can run it wherever python3 exists.
"""

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "omp" / "config.yml"

# Listed in the order the config must use: every deny before any prompt, so a
# protected target can never fall through to a confirmation.
DENY_RULES = [
    "sudo *",
    "rm *-r* /",
    "rm *-r* /*",
    "rm *-r* /Users",
    "rm *-r* /Users/*",
    "rm *-r* /Volumes",
    "rm *-r* /Volumes/*",
    "rm *-r* ~*",
    "find / *-delete*",
    "find /Users/* -delete*",
    "find /Volumes/* -delete*",
    "mkfs*",
    "dd *of=/dev/*",
    "diskutil erase*",
    "diskutil partition*",
    "chmod *-R* /*",
    "chown *-R* /*",
]

PROMPT_RULES = [
    "rm *-r*",
    "git reset --hard*",
    "git clean *",
    "git push *--force*",
]


def rule(match: str, approval: str) -> str:
    """Exact config line for one rule."""
    return f'- {{ match: "{match}", approval: {approval} }}'


def top_level_block(lines: list[str], name: str) -> list[str] | None:
    """Lines inside the top-level `name:` mapping, stopping at the next key."""
    start = next(
        (index for index, line in enumerate(lines) if line.rstrip() == f"{name}:"),
        None,
    )
    if start is None:
        return None
    block = []
    for line in lines[start + 1 :]:
        if line.strip() and not line[:1].isspace():
            break
        block.append(line)
    return block


class OmpCatastrophePolicyTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.lines = CONFIG.read_text(encoding="utf-8").splitlines()
        cls.tools = top_level_block(cls.lines, "tools")
        cls.bash = top_level_block(cls.lines, "bash")

    def stripped(self, block):
        return [line.strip() for line in block] if block is not None else []

    def test_yolo_mode_and_eval_deny(self):
        self.assertIsNotNone(self.tools, "missing top-level tools: block")
        tools = self.stripped(self.tools)
        self.assertIn("approvalMode: yolo", tools)
        self.assertIn("eval: deny", tools)

    def test_bash_block_exists(self):
        self.assertIsNotNone(self.bash, "missing top-level bash: block")

    def test_protected_deny_rules_present(self):
        lines = self.stripped(self.bash)
        for match in DENY_RULES:
            with self.subTest(match=match):
                self.assertEqual(lines.count(rule(match, "deny")), 1)

    def test_generic_prompt_rules_present(self):
        lines = self.stripped(self.bash)
        for match in PROMPT_RULES:
            with self.subTest(match=match):
                self.assertEqual(lines.count(rule(match, "prompt")), 1)

    def test_denies_precede_prompts_in_documented_order(self):
        lines = self.stripped(self.bash)
        required = [rule(match, "deny") for match in DENY_RULES] + [
            rule(match, "prompt") for match in PROMPT_RULES
        ]
        self.assertEqual([line for line in required if line not in lines], [])

        deny_positions = [lines.index(rule(match, "deny")) for match in DENY_RULES]
        prompt_positions = [lines.index(rule(match, "prompt")) for match in PROMPT_RULES]
        self.assertEqual(deny_positions, sorted(deny_positions))
        self.assertLess(max(deny_positions), min(prompt_positions))
        self.assertLess(max(deny_positions), lines.index(rule("rm *-r*", "prompt")))


if __name__ == "__main__":
    unittest.main()
