#!/usr/bin/env python3
"""Regression tests for scripts/lint-skills.py's catalogue count check.

Focused on the "The list below covers the N repo-owned skills" sentence in
skills/README.md — lint_catalogue also checks bullets-vs-directories, but that
half already has coverage via the real tree passing under check.sh; this file
adds the stated-count half, which had none.

Hermetic: everything runs against an in-memory string plus a `dirnames` set,
never against the real skills/README.md or skills/ tree.
"""

import importlib.util
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]

spec = importlib.util.spec_from_file_location("lint_skills", ROOT / "scripts" / "lint-skills.py")
lint_skills = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lint_skills)


def readme_text(sentence):
    return (
        "# Skills library\n\n"
        "## Convention\n\n"
        f"{sentence}\n\n"
        "- `alpha` — Alpha skill.\n"
        "- `beta` — Beta skill.\n"
    )


class StatedCountTest(unittest.TestCase):
    def lint(self, sentence, dirnames, tmp_path):
        skills_dir = tmp_path / "skills"
        skills_dir.mkdir()
        (skills_dir / "README.md").write_text(readme_text(sentence), encoding="utf-8")
        return lint_skills.lint_catalogue(str(skills_dir), dirnames)

    def test_matching_count_passes(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            fails, _ = self.lint(
                "The list below covers the 2 repo-owned skills.",
                ["alpha", "beta"],
                Path(tmp),
            )
        self.assertEqual(fails, [])

    def test_stale_count_fails(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            fails, _ = self.lint(
                "The list below covers the 3 repo-owned skills.",
                ["alpha", "beta"],
                Path(tmp),
            )
        self.assertTrue(
            any("states 3 repo-owned skills but 2 exist" in f for f in fails),
            fails,
        )

    def test_missing_sentence_fails(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            fails, _ = self.lint(
                "This README has no count sentence at all.",
                ["alpha", "beta"],
                Path(tmp),
            )
        self.assertTrue(
            any("no 'covers the N repo-owned skills' sentence" in f for f in fails),
            fails,
        )

    def test_bullet_mismatch_still_reported_alongside_count(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            fails, _ = self.lint(
                "The list below covers the 2 repo-owned skills.",
                ["alpha", "gamma"],
                Path(tmp),
            )
        self.assertTrue(any("gamma" in f for f in fails), fails)
        self.assertTrue(any("beta" in f for f in fails), fails)


def make_tree(tmp, skills, plugins="", extra=None):
    """Write a fixture repo: skills = {name: {relative path: text}}."""
    root = Path(tmp)
    for name, files in skills.items():
        for rel, text in files.items():
            path = root / "skills" / name / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
    (root / "plugins.txt").write_text(plugins, encoding="utf-8")
    for rel, text in (extra or {}).items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    return root


def skill_text(body, description="Use when testing."):
    return f"---\nname: x\ndescription: {description}\n---\n\n{body}\n"


class ReferenceTest(unittest.TestCase):
    def refs(self, skills, plugins="", extra=None):
        with tempfile.TemporaryDirectory() as tmp:
            root = make_tree(tmp, skills, plugins, extra)
            return lint_skills.lint_references(str(root), sorted(skills))

    def test_missing_reference_file_fails(self):
        fails = self.refs({"a": {"SKILL.md": skill_text("See `references/missing.md`.")}})
        self.assertTrue(any("references/missing.md" in f for f in fails), fails)

    def test_present_reference_file_passes(self):
        fails = self.refs(
            {"a": {"SKILL.md": skill_text("See `references/there.md`."), "references/there.md": "hi\n"}}
        )
        self.assertEqual(fails, [])

    def test_missing_markdown_link_fails(self):
        fails = self.refs({"a": {"SKILL.md": skill_text("See [it](references/gone.md#top).")}})
        self.assertTrue(any("references/gone.md" in f for f in fails), fails)

    def test_sibling_link_resolves_and_missing_sibling_fails(self):
        ok = self.refs(
            {
                "a": {"SKILL.md": skill_text("[b](../b/SKILL.md) skill://b")},
                "b": {"SKILL.md": skill_text("hi")},
            }
        )
        self.assertEqual(ok, [])
        bad = self.refs({"a": {"SKILL.md": skill_text("[b](../zzz/SKILL.md)")}})
        self.assertTrue(any("../zzz/SKILL.md" in f for f in bad), bad)

    def test_repo_root_script_path_resolves(self):
        body = "Run `scripts/tool.py`."
        self.assertEqual(
            self.refs({"a": {"SKILL.md": skill_text(body)}}, extra={"scripts/tool.py": "x"}), []
        )
        fails = self.refs({"a": {"SKILL.md": skill_text(body)}})
        self.assertTrue(any("scripts/tool.py" in f for f in fails), fails)

    def test_reference_files_are_scanned_too(self):
        fails = self.refs(
            {"a": {"SKILL.md": skill_text("x"), "references/r.md": "See `references/nope.md`."}}
        )
        self.assertTrue(any("references/r.md" in f and "nope.md" in f for f in fails), fails)

    def test_placeholders_fences_and_archive_history_are_ignored(self):
        body = (
            "Make `skills/<name>/SKILL.md` and `references/*.md`.\n"
            "```\nsee `references/in-fence.md` and skill://nofence\n```\n"
            "The deleted `skills/_archive/old/SKILL.md` is recoverable from git.\n"
        )
        self.assertEqual(self.refs({"a": {"SKILL.md": skill_text(body)}}), [])

    def test_nonexistent_skill_in_handoff_contexts_fails(self):
        for body in (
            "Follow skill://ghost now.",
            "Load the `ghost` skill first.",
            "Then hand off to `ghost`.",
            "Next -> `ghost`",
        ):
            fails = self.refs({"a": {"SKILL.md": skill_text(body)}})
            self.assertTrue(any("'ghost'" in f for f in fails), (body, fails))

    def test_description_not_for_clause_names_must_exist(self):
        desc = '"Use when testing. Not for other work (ghost, b)."'
        fails = self.refs(
            {"a": {"SKILL.md": skill_text("x", desc)}, "b": {"SKILL.md": skill_text("y")}}
        )
        self.assertTrue(any("'ghost'" in f for f in fails), fails)
        self.assertFalse(any("'b'" in f for f in fails), fails)

    def test_repo_owned_and_plugins_txt_skills_pass(self):
        body = "Use skill://b, then the `ext-one` skill, then hand off to `ext-two`."
        desc = '"Use when testing. Not for brand pages (ext-one)."'
        fails = self.refs(
            {"a": {"SKILL.md": skill_text(body, desc)}, "b": {"SKILL.md": skill_text("y")}},
            plugins="external some/repo ext-one ext-two\n",
        )
        self.assertEqual(fails, [])

    def test_vendored_skill_dirs_count_when_present(self):
        extra = {"vendor/o-r/skills/bare-skill/SKILL.md": "x"}
        fails = self.refs(
            {"a": {"SKILL.md": skill_text("Use the `bare-skill` skill.")}},
            plugins="external o/r\n",
            extra=extra,
        )
        self.assertEqual(fails, [])

    def test_external_skills_file_names_pass_and_others_fail(self):
        listing = "# comment\nlisted-one  # trailing comment\n\nlisted-two\n"
        body = "Use the `listed-one` skill, then hand off to `listed-two`."
        fails = self.refs(
            {"a": {"SKILL.md": skill_text(body)}}, extra={"external-skills.txt": listing}
        )
        self.assertEqual(fails, [])
        fails = self.refs(
            {"a": {"SKILL.md": skill_text("Use the `ghost` skill.")}},
            extra={"external-skills.txt": listing},
        )
        self.assertTrue(any("'ghost'" in f for f in fails), fails)

    def test_missing_external_skills_file_is_empty_not_fatal(self):
        fails = self.refs({"a": {"SKILL.md": skill_text("Use the `ghost` skill.")}})
        self.assertTrue(any("'ghost'" in f for f in fails), fails)

    def test_vendored_skill_known_by_frontmatter_name_not_directory(self):
        vendored = "---\nname: real-name\ndescription: d\n---\n"
        extra = {"vendor/o-r/skills/dirname/SKILL.md": vendored}
        ok = self.refs(
            {"a": {"SKILL.md": skill_text("Use the `real-name` skill.")}},
            plugins="external o/r\n",
            extra=extra,
        )
        self.assertEqual(ok, [])
        bad = self.refs(
            {"a": {"SKILL.md": skill_text("Use the `dirname` skill.")}},
            plugins="external o/r\n",
            extra=extra,
        )
        self.assertTrue(any("'dirname'" in f for f in bad), bad)

    def test_vendored_skill_without_frontmatter_name_falls_back_to_directory(self):
        extra = {"vendor/o-r/skills/bare-dir/SKILL.md": "no frontmatter\n"}
        fails = self.refs(
            {"a": {"SKILL.md": skill_text("Use the `bare-dir` skill.")}},
            plugins="external o/r\n",
            extra=extra,
        )
        self.assertEqual(fails, [])

    def test_lowercase_not_for_clause_is_checked(self):
        desc = '"Use when testing; not for other work (ghost)."'
        fails = self.refs({"a": {"SKILL.md": skill_text("x", desc)}})
        self.assertTrue(any("'ghost'" in f for f in fails), fails)

    def test_real_external_skills_file_covers_bare_sources(self):
        names = lint_skills.load_external_skills(str(ROOT))
        for name in ("grilling", "diagnosing-bugs", "writing-for-agents", "animate", "emil-design-eng"):
            self.assertIn(name, names)

    def test_archived_skills_are_not_live_targets_or_sources(self):
        skills = {
            "a": {"SKILL.md": skill_text("Use the `old` skill.")},
            "_archive": {"old/SKILL.md": skill_text("x"), "bad/SKILL.md": skill_text("`references/no.md`")},
        }
        with tempfile.TemporaryDirectory() as tmp:
            root = make_tree(tmp, skills)
            fails = lint_skills.lint_references(str(root), ["a"])
        self.assertTrue(any("'old'" in f for f in fails), fails)
        self.assertFalse(any("no.md" in f for f in fails), fails)

    def test_real_tree_passes(self):
        dirnames = sorted(
            d.name
            for d in (ROOT / "skills").iterdir()
            if d.is_dir() and not d.name.startswith(("_", ".")) and (d / "SKILL.md").is_file()
        )
        self.assertEqual(lint_skills.lint_references(str(ROOT), dirnames), [])


class ExternalDriftTest(unittest.TestCase):
    """external-skills.txt must match what a cloned bare source really ships."""

    LISTING = "# o/r:skills/eng\none\ntwo\n\n# p/q\nthree\n"

    def drift(self, listing, clones, plugins="external o/r:skills/eng\nexternal p/q\n"):
        extra = {"external-skills.txt": listing}
        for rel, name in clones.items():
            extra[rel] = f"---\nname: {name}\ndescription: d\n---\n"
        with tempfile.TemporaryDirectory() as tmp:
            root = make_tree(tmp, {}, plugins, extra)
            return lint_skills.lint_external_drift(str(root))

    CLONES = {
        "vendor/o-r/skills/eng/dir-one/SKILL.md": "one",
        "vendor/o-r/skills/eng/two/SKILL.md": "two",
        "vendor/p-q/skills/three/SKILL.md": "three",
    }

    def test_matching_section_passes(self):
        self.assertEqual(self.drift(self.LISTING, self.CLONES), [])

    def test_clone_ships_name_missing_from_section_fails(self):
        clones = dict(self.CLONES, **{"vendor/o-r/skills/eng/new/SKILL.md": "fresh"})
        fails = self.drift(self.LISTING, clones)
        self.assertEqual(len(fails), 1, fails)
        self.assertIn("o/r:skills/eng", fails[0])
        self.assertIn("fresh", fails[0])

    def test_section_lists_name_clone_lacks_fails(self):
        fails = self.drift(self.LISTING.replace("three", "three\nghost"), self.CLONES)
        self.assertEqual(len(fails), 1, fails)
        self.assertIn("'p/q'", fails[0])
        self.assertIn("ghost", fails[0])

    def test_frontmatter_name_not_directory_is_compared(self):
        fails = self.drift(self.LISTING.replace("one", "dir-one"), self.CLONES)
        self.assertEqual(len(fails), 2, fails)

    def test_source_without_a_section_fails(self):
        fails = self.drift("# o/r:skills/eng\none\ntwo\n", self.CLONES)
        self.assertTrue(any("no section 'p/q'" in f and "three" in f for f in fails), fails)

    def test_no_clone_keeps_todays_behaviour(self):
        self.assertEqual(self.drift("# o/r:skills/eng\nwhatever\n", {}), [])

    def test_allowlisted_sources_are_not_compared(self):
        clones = {"vendor/o-r/skills/a/SKILL.md": "a", "vendor/o-r/skills/b/SKILL.md": "b"}
        self.assertEqual(self.drift("", clones, plugins="external o/r a\n"), [])

    def test_real_tree_has_no_drift(self):
        self.assertEqual(lint_skills.lint_external_drift(str(ROOT)), [])


if __name__ == "__main__":
    unittest.main()
