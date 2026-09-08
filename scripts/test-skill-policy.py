#!/usr/bin/env python3
"""Regression tests for skill policy parsing, overlays, and OMP-local writes."""

from contextlib import redirect_stderr
from io import StringIO
from pathlib import Path
import json
import os
import sys
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import skill_policy  # noqa: E402


class SkillPolicyTest(unittest.TestCase):
    def entry(self, name="sample", exposure="manual", description=None, root="skills"):
        if description is None:
            description = (
                "Plan reliable policy changes with clear validation and safe atomic writes "
                "for every affected skill."
            )
        return {
            "name": name,
            "root": root,
            "exposure": exposure,
            "description": description,
        }

    def write_skill(self, directory, text):
        directory.mkdir(parents=True, exist_ok=True)
        (directory / "SKILL.md").write_bytes(text.encode("utf-8"))

    def test_rewrites_plain_quoted_and_block_descriptions_preserving_metadata_and_body(self):
        bodies = {}
        forms = {
            "plain": "description: old plain value\n",
            "quoted": 'description: "old quoted: value"\n',
            "block": "description: |\n  old block value\n  continued value\n",
        }
        for form, description_line in forms.items():
            body = "# Body\n\nUnicode: café\n"
            text = (
                "---\n"
                "name: sample\n"
                + description_line
                + 'title: "Unknown metadata: retain this"\n'
                + "labels:\n"
                + "  team: policy\n"
                + "---\n"
                + body
            )
            fields, parsed_body, error = skill_policy.parse_frontmatter(text)
            self.assertIsNone(error)
            self.assertEqual(fields["description"].value, {
                "plain": "old plain value",
                "quoted": "old quoted: value",
                "block": "old block value continued value",
            }[form])
            self.assertEqual(parsed_body, body)

            rewritten = skill_policy.rewrite_frontmatter(
                text,
                "A new description: preserve this value",
                "manual",
            )
            rewritten_fields, rewritten_body, error = skill_policy.parse_frontmatter(rewritten)
            self.assertIsNone(error)
            self.assertEqual(
                rewritten_fields["description"].value,
                "A new description: preserve this value",
            )
            self.assertEqual(rewritten_fields["disable-model-invocation"].value, "true")
            self.assertEqual(rewritten_body.encode("utf-8"), body.encode("utf-8"))
            self.assertIn('title: "Unknown metadata: retain this"\n', rewritten)
            self.assertIn("labels:\n  team: policy\n", rewritten)
            bodies[form] = rewritten

        self.assertEqual(len(bodies), 3)

    def test_manual_add_and_automatic_remove_flag(self):
        original = "---\nname: sample\ndescription: old\n---\nbody\n"
        manual = skill_policy.rewrite_frontmatter(original, "manual description text", "manual")
        self.assertIn("disable-model-invocation: true\n", manual)
        automatic = skill_policy.rewrite_frontmatter(manual, "automatic description text", "automatic")
        self.assertNotIn("disable-model-invocation", automatic)
        fields, body, error = skill_policy.parse_frontmatter(automatic)
        self.assertIsNone(error)
        self.assertEqual(fields["description"].value, "automatic description text")
        self.assertEqual(body, "body\n")

    def test_materialisation_uses_relative_root_symlinks_and_is_idempotent(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "source"
            output = root / "generated" / "sample"
            self.write_skill(
                source,
                "---\nname: sample\ndescription: upstream\n---\nbody\n",
            )
            (source / "asset.txt").write_text("asset", encoding="utf-8")
            nested = source / "nested"
            nested.mkdir()
            (nested / "inside.txt").write_text("nested", encoding="utf-8")
            entry = self.entry(description="A rewritten description with enough words here.")

            skill_policy.materialise_external_skill(source, output, entry)
            first = self.tree_signature(output)
            for asset in (output / "asset.txt", output / "nested"):
                self.assertTrue(asset.is_symlink())
                self.assertFalse(os.path.isabs(os.readlink(asset)))
            self.assertEqual((output / "asset.txt").read_text(encoding="utf-8"), "asset")
            self.assertEqual(
                (output / "nested" / "inside.txt").read_text(encoding="utf-8"),
                "nested",
            )

            skill_policy.materialise_external_skill(source, output, entry)
            self.assertEqual(first, self.tree_signature(output))

            (source / "asset.txt").unlink()
            (source / "nested").joinpath("inside.txt").unlink()
            (source / "nested").rmdir()
            (source / "new.txt").write_text("new", encoding="utf-8")
            skill_policy.materialise_external_skill(source, output, entry)
            self.assertFalse((output / "asset.txt").exists())
            self.assertFalse((output / "nested").exists())
            self.assertEqual((output / "new.txt").read_text(encoding="utf-8"), "new")

    def tree_signature(self, directory):
        result = []
        for path in sorted(directory.iterdir(), key=lambda item: item.name):
            if path.is_symlink():
                result.append((path.name, "symlink", os.readlink(path)))
            elif path.is_file():
                result.append((path.name, "file", path.read_bytes()))
            else:
                result.append((path.name, "directory", self.tree_signature(path)))
        return result

    def test_malformed_or_wrong_name_source_never_partially_replaces_output(self):
        cases = {
            "malformed": "name: sample\ndescription: not frontmatter\n---\nbody\n",
            "wrong-name": "---\nname: another\ndescription: valid\n---\nbody\n",
        }
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for label, source_text in cases.items():
                source = root / (label + "-source")
                output = root / (label + "-output")
                self.write_skill(source, source_text)
                output.mkdir()
                sentinel = output / "sentinel"
                sentinel.write_bytes(b"existing output")
                before = self.tree_signature(output)
                before_root_names = sorted(path.name for path in root.iterdir())
                with self.assertRaises(skill_policy.PolicyError):
                    skill_policy.materialise_external_skill(source, output, self.entry())
                self.assertEqual(before, self.tree_signature(output))
                self.assertEqual(
                    before_root_names,
                    sorted(path.name for path in root.iterdir()),
                )

    def test_missing_omp_local_skill_warns_while_present_skill_is_applied(self):
        with tempfile.TemporaryDirectory() as temporary:
            omp_root = Path(temporary)
            present = omp_root / "skills" / "present"
            original = "---\nname: present\ndescription: original\n---\nbody\n"
            self.write_skill(present, original)
            entries = {
                "missing": self.entry("missing", description="Missing optional skill entry text."),
                "present": self.entry("present", description="Present replacement description text."),
            }
            stderr = StringIO()
            with redirect_stderr(stderr):
                applied = skill_policy.apply_omp_local(omp_root, entries)
            self.assertEqual(applied, [str(present / "SKILL.md")])
            self.assertIn("warning: optional OMP-local skill missing:", stderr.getvalue())
            self.assertIn("missing", stderr.getvalue())
            fields, _body, error = skill_policy.parse_frontmatter(
                (present / "SKILL.md").read_text(encoding="utf-8")
            )
            self.assertIsNone(error)
            self.assertEqual(fields["description"].value, "Present replacement description text.")
            self.assertEqual(fields["disable-model-invocation"].value, "true")

    def test_omp_local_backup_is_restorable_and_concurrent_change_stays_atomic(self):
        with tempfile.TemporaryDirectory() as temporary:
            omp_root = Path(temporary)
            target = omp_root / "skills" / "present" / "SKILL.md"
            original = "---\nname: present\ndescription: original\n---\nbody\n"
            changed = "---\nname: present\ndescription: concurrent\n---\nchanged\n"
            self.write_skill(target.parent, original)
            entries = {"present": self.entry("present", description="Replacement description text.")}

            skill_policy.apply_omp_local(omp_root, entries)
            backup = omp_root / "skill-policy-backups" / "skills" / "present" / "SKILL.md"
            self.assertEqual(backup.read_bytes(), original.encode("utf-8"))
            target.write_bytes(backup.read_bytes())
            self.assertEqual(target.read_bytes(), original.encode("utf-8"))

            calls = 0
            real_read_and_hash = skill_policy._read_and_hash

            def race(path):
                nonlocal calls
                result = real_read_and_hash(path)
                calls += 1
                if calls == 2:
                    Path(path).write_bytes(changed.encode("utf-8"))
                return result

            with mock.patch.object(skill_policy, "_read_and_hash", side_effect=race):
                with self.assertRaises(skill_policy.PolicyError):
                    skill_policy.apply_omp_local(omp_root, entries)
            self.assertEqual(target.read_bytes(), changed.encode("utf-8"))
            self.assertEqual(backup.read_bytes(), original.encode("utf-8"))
            self.assertFalse(any(path.name.startswith(".skill-policy-") for path in target.parent.iterdir()))

    def test_policy_inventory_and_word_budget_errors_are_sorted_and_actionable(self):
        valid_manual = self.entry("alpha")
        valid_manual.pop("name")
        valid_manual.pop("root")
        valid_automatic = {
            "exposure": "automatic",
            "description": "Use this automatic skill description with enough words to satisfy the configured policy budget and routing contract.",
        }
        policy = {
            "version": 1,
            "budgets": {
                "manualAwareDescriptionCharacters": 100,
                "alwaysListedDescriptionCharacters": 100,
            },
            "skills": {"beta": valid_manual, "alpha": valid_automatic},
            "ompLocalSkills": {"local": self.entry("local")},
        }
        with tempfile.TemporaryDirectory() as temporary:
            policy_path = Path(temporary) / "policy.json"
            policy_path.write_text(json.dumps(policy), encoding="utf-8")
            with self.assertRaises(skill_policy.PolicyError) as caught:
                skill_policy.load_policy(policy_path)
            self.assertEqual(
                str(caught.exception),
                "skills.alpha description has 17 words; expected 25-45",
            )

        unknown = dict(policy)
        unknown["zeta"] = True
        unknown["aardvark"] = True
        with self.assertRaises(skill_policy.PolicyError) as caught:
            skill_policy.validate_policy(unknown)
        self.assertEqual(str(caught.exception), "unknown policy fields: aardvark, zeta")

        too_short = dict(policy)
        too_short["skills"] = {"alpha": {"exposure": "manual", "description": "short"}}
        with self.assertRaises(skill_policy.PolicyError) as caught:
            skill_policy.validate_policy(too_short)
        self.assertEqual(str(caught.exception), "skills.alpha description has 1 words; expected 10-25")

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            repo = root / "repo"
            vendor = root / "vendor"
            (repo / "skills" / "aardvark").mkdir(parents=True)
            (repo / "skills" / "zeta").mkdir(parents=True)
            (repo / "skills" / "aardvark" / "SKILL.md").write_text("---\nname: aardvark\n---\n", encoding="utf-8")
            (repo / "skills" / "zeta" / "SKILL.md").write_text("---\nname: zeta\n---\n", encoding="utf-8")
            inventory_policy = {
                "version": 1,
                "budgets": {"manualAwareDescriptionCharacters": 100, "alwaysListedDescriptionCharacters": 100},
                "skills": {
                    "beta": {"exposure": "manual", "description": "One two three four five six seven eight nine ten"},
                    "alpha": {"exposure": "manual", "description": "One two three four five six seven eight nine ten"},
                },
                "ompLocalSkills": {"local": self.entry("local")},
            }
            errors = skill_policy.validate_inventory(inventory_policy, repo, vendor)
            self.assertEqual(errors, [
                "missing shared skills: alpha, beta",
                "unexpected repo skills: aardvark, zeta",
            ])


if __name__ == "__main__":
    unittest.main()
