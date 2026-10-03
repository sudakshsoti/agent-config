#!/usr/bin/env python3
"""Tests for scripts/repo-audit.py's filing rules: findings validation,
dedupe against existing issues, and the per-run cap. No network, no omp."""

from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / "repo-audit.py"
spec = importlib.util.spec_from_file_location("repo_audit", SCRIPT)
ra = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ra)


def finding(key, **over):
    f = {"key": key, "kind": "drift", "strength": "Strong",
         "title": f"Fix {key}", "body": "## What I found\nx"}
    f.update(over)
    return f


def doc(*findings):
    return json.dumps({"findings": list(findings)})


class ParseFindings(unittest.TestCase):
    def test_accepts_valid_and_empty(self):
        self.assertEqual(len(ra.parse_findings(doc(finding("abc-one")))), 1)
        self.assertEqual(ra.parse_findings(doc()), [])

    def test_rejects_malformed(self):
        cases = {
            "not json": "{",
            "no list": json.dumps({"items": []}),
            "bad key": doc(finding("Bad Key")),
            "short key": doc(finding("ab")),
            "repeated key": doc(finding("abc-one"), finding("abc-one")),
            "unknown kind": doc(finding("abc-one", kind="style")),
            "unknown strength": doc(finding("abc-one", strength="High")),
            "empty body": doc(finding("abc-one", body="  ")),
            "long title": doc(finding("abc-one", title="x" * 121)),
        }
        for name, text in cases.items():
            with self.subTest(name), self.assertRaises(ra.AuditError):
                ra.parse_findings(text)


class Filing(unittest.TestCase):
    def test_filed_issue_is_recognised_next_run(self):
        # The marker written into a filed body is what stops next week's run
        # from filing the same finding again, whatever state the issue is in.
        body = ra.render_body(finding("install-sh-precedence"))
        known = ra.existing_keys(["unrelated issue", body, None])
        self.assertEqual(known, {"install-sh-precedence"})
        self.assertEqual(ra.select([finding("install-sh-precedence")], known, 5), [])

    def test_cap_applies_after_dedupe_in_model_order(self):
        fs = [finding(k) for k in ("aaa", "bbb", "ccc", "ddd")]
        chosen = ra.select(fs, {"aaa"}, 2)
        self.assertEqual([f["key"] for f in chosen], ["bbb", "ccc"])

    def test_body_carries_disclaimer_first(self):
        self.assertTrue(ra.render_body(finding("abc-one")).startswith(ra.DISCLAIMER))


if __name__ == "__main__":
    unittest.main()
