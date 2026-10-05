#!/usr/bin/env python3
"""test-check-model-routing.py — the drift cases check-model-routing.py must catch.

Rule tests hand `check` in-memory inputs; only test_real_repo_passes reads the checkout.
The negative cases are the ones that matter: a check that only ever passes on
the current tree is not a check.
"""

import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "check_model_routing", ROOT / "scripts" / "check-model-routing.py"
)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)

BASE_CONFIG = """\
modelRoles:
  default: anthropic/claude-opus-5:medium
  task: anthropic/claude-sonnet-5-5:medium
disabledProviders:
  - openai-codex
providers:
  autoThinkingMaxEffort: high
task:
  maxEffort: high
  agentModelOverrides:
    builder: anthropic/claude-sonnet-5-5:high
    scout: opencode-go/glm-5.3-flash:low
retry:
  usageAwareFallback: true
  usageReservePct: 20
  usageReservePolicy: auto
  fallbackChains:
    anthropic/claude-opus-5:
      - anthropic/claude-sonnet-5-5:high
"""

BUILDER = """\
---
name: builder
description: Implements an approved UX plan.
model: anthropic/claude-sonnet-5-5:high
---

Body.
"""

PI_AGENT = """\
---
description: Explorer.
model: opencode-go/glm-5.3-flash
thinking: low
---

Body.
"""

PI_SETTINGS = (
    '{"defaultProvider": "opencode-go", "defaultModel": "deepseek-v4.1-flash",'
    ' "defaultThinkingLevel": "high",'
    ' "enabledModels": ["opencode-go/deepseek-v4.1-flash:high", "opencode-go/glm-5.3-flash:high"]}\n'
)
PI_SETTINGS_WITH_SHIM = (
    '{"defaultProvider": "opencode-go", "defaultModel": "deepseek-v4.1-flash",'
    ' "packages": ["npm:pi-memory", "npm:@gotgenes/pi-anthropic-auth"]}\n'
)

OMP_DOC = """\
# Agents

| Roles/settings | Value |
| --- | --- |
| `default` role | `anthropic/claude-opus-5:medium` |
| `task` role | `anthropic/claude-sonnet-5-5:medium` |
| `scout` agent | `opencode-go/glm-5.3-flash:low` |
| `builder` agent | `anthropic/claude-sonnet-5-5:high` |
| `disabledProviders` | `[openai-codex]` |
| `retry.usageAwareFallback` / `retry.usageReservePct` / `retry.usageReservePolicy` | `true` / `20` / `auto` |
| `task.maxEffort` / `providers.autoThinkingMaxEffort` | `high` / `high` |

History: `openai-codex` is retired and `claude-opus-4` was once the default.

<!-- routing:current -->
`default` → `anthropic/claude-opus-5` medium
`scout` and `builder` → see below
<!-- routing:end -->

Outside the markers: `scout` → `nonsense/model` max.
""".replace("`scout` and `builder` → see below", "`scout` → `opencode-go/glm-5.3-flash` low\n`builder` → `anthropic/claude-sonnet-5-5` high")

PI_DOC = """\
# Pi

| Task / agent | Provider and model | Effort |
| --- | --- | --- |
| Main session | `opencode-go/deepseek-v4.1-flash` | high |
| `Explore` discovery | `opencode-go/glm-5.3-flash` | low |
| Manual fallback (Ctrl+P) | `opencode-go/glm-5.3-flash` | high |

Run Claude work in OMP.

<!-- routing:current -->
`main` → `opencode-go/deepseek-v4.1-flash` high
`Explore` → `opencode-go/glm-5.3-flash` low
<!-- routing:end -->
"""


class RoutingCheckTest(unittest.TestCase):
    def run_check(
        self,
        config=BASE_CONFIG,
        builder=BUILDER,
        pi_agent=PI_AGENT,
        pi_settings=PI_SETTINGS,
        omp_doc=None,
        pi_doc=None,
    ):
        parsed, parse_failures = MODULE.parse_config(config, "omp/config.yml")
        self.assertEqual(parse_failures, [])
        return MODULE.check(
            parsed,
            {"builder.md": builder},
            {"Explore.md": pi_agent},
            json.loads(pi_settings),
            docs=None
            if omp_doc is None and pi_doc is None
            else {"AGENTS.md": omp_doc or OMP_DOC, "pi/model-ladder.md": pi_doc or PI_DOC},
        )

    def docs_check(self, **kwargs):
        kwargs.setdefault("omp_doc", OMP_DOC)
        kwargs.setdefault("pi_doc", PI_DOC)
        return self.run_check(**kwargs)

    def assert_fails(self, failures, *needles):
        self.assertTrue(any(all(n in f for n in needles) for f in failures), failures)

    def test_clean_tree_passes(self):
        self.assertEqual(self.run_check(), [])

    def test_real_repo_passes(self):
        self.assertEqual(MODULE.check_repo(str(ROOT)), [])

    def test_frontmatter_drift_is_reported(self):
        drifted = BUILDER.replace(
            "model: anthropic/claude-sonnet-5-5:high", 'model: "@default"'
        )
        failures = self.run_check(builder=drifted)
        self.assertTrue(any("resolves to" in f and "builder" in f for f in failures), failures)

    def test_block_scalar_model_is_resolved_not_misread(self):
        block = BUILDER.replace(
            "model: anthropic/claude-sonnet-5-5:high",
            "model: >-\n  anthropic/claude-sonnet-5-5:high",
        )
        failures = self.run_check(builder=block)
        self.assertEqual(failures, [])

    def test_block_scalar_model_drift_is_reported(self):
        block = BUILDER.replace(
            "model: anthropic/claude-sonnet-5-5:high", 'model: |\n  "@default"'
        )
        failures = self.run_check(builder=block)
        self.assertTrue(any("builder" in f for f in failures), failures)

    def test_unparseable_frontmatter_is_reported(self):
        failures = self.run_check(builder="no frontmatter here\n")
        self.assertTrue(any("builder.md" in f and "frontmatter" in f for f in failures), failures)

    def test_alias_matching_its_override_passes(self):
        aliased = BUILDER.replace(
            "model: anthropic/claude-sonnet-5-5:high", 'model: "@task"'
        )
        config = BASE_CONFIG.replace(
            "builder: anthropic/claude-sonnet-5-5:high",
            "builder: anthropic/claude-sonnet-5-5:medium",
        )
        failures = self.run_check(config=config, builder=aliased)
        self.assertEqual([f for f in failures if "builder" in f], [])

    def test_override_key_naming_no_agent_is_reported(self):
        config = BASE_CONFIG.replace(
            "    scout: opencode-go/glm-5.3-flash:low",
            "    scout: opencode-go/glm-5.3-flash:low\n    librarian: opencode-go/glm-5.3-flash:low",
        )
        failures = self.run_check(config=config)
        self.assertTrue(any("librarian" in f and "names no agent" in f for f in failures), failures)

    def test_selector_pinned_to_locally_disabled_provider_is_reported(self):
        config = BASE_CONFIG.replace(
            "  default: anthropic/claude-opus-5:medium",
            "  default: openai-codex/gpt-5.6-luna:high",
        )
        failures = self.run_check(config=config)
        self.assertTrue(any("disabledProviders" in f for f in failures), failures)

    def test_malformed_selector_is_reported(self):
        config = BASE_CONFIG.replace(
            "  default: anthropic/claude-opus-5:medium", "  default: claude-opus-5:medium"
        )
        failures = self.run_check(config=config)
        self.assertTrue(any("provider/model" in f for f in failures), failures)

    def test_unknown_effort_is_reported(self):
        config = BASE_CONFIG.replace(
            "  default: anthropic/claude-opus-5:medium",
            "  default: anthropic/claude-opus-5:enormous",
        )
        failures = self.run_check(config=config)
        self.assertTrue(any("provider/model" in f for f in failures), failures)

    def test_claude_pin_in_pi_agent_is_reported(self):
        """Without the shim, a Claude pin in a Pi agent is a broken route."""
        agent = PI_AGENT.replace(
            "model: opencode-go/glm-5.3-flash", "model: anthropic/claude-opus-5"
        )
        failures = self.run_check(pi_agent=agent)
        self.assertTrue(any("pins Claude" in f for f in failures), failures)

    def test_claude_pin_is_allowed_when_shim_is_installed(self):
        """With the shim present an explicit agent pin is deliberate, not drift."""
        agent = PI_AGENT.replace(
            "model: opencode-go/glm-5.3-flash", "model: anthropic/claude-opus-5"
        )
        failures = self.run_check(pi_agent=agent, pi_settings=PI_SETTINGS_WITH_SHIM)
        self.assertFalse(any("pins Claude" in f for f in failures), failures)

    def test_claude_default_provider_is_reported_even_with_shim(self):
        """The shim must never become the face of the harness."""
        settings = (
            '{"defaultProvider": "anthropic", "defaultModel": "claude-opus-5",'
            ' "packages": ["npm:@gotgenes/pi-anthropic-auth"]}\n'
        )
        failures = self.run_check(pi_settings=settings)
        self.assertTrue(any("defaultProvider" in f for f in failures), failures)

    def test_claude_enabled_model_is_reported_even_with_shim(self):
        """Claude must stay out of the Ctrl+P cycle regardless of the shim."""
        settings = (
            '{"defaultProvider": "opencode-go", "defaultModel": "deepseek-v4.1-flash",'
            ' "enabledModels": ["anthropic/claude-opus-5:high"],'
            ' "packages": ["npm:@gotgenes/pi-anthropic-auth"]}\n'
        )
        failures = self.run_check(pi_settings=settings)
        self.assertTrue(any("enabledModels" in f for f in failures), failures)

    def test_scoped_and_pinned_package_names_parse(self):
        """`npm:@scope/name@1.2.3` must not split on the scope's `@`."""
        self.assertEqual(
            MODULE._package_name("npm:@gotgenes/pi-anthropic-auth@3.4.2"),
            "@gotgenes/pi-anthropic-auth",
        )
        self.assertEqual(MODULE._package_name("npm:pi-memory@1.2.3"), "pi-memory")
        self.assertEqual(MODULE._package_name("npm:@scope/name"), "@scope/name")

    def test_missing_pi_settings_means_shim_absent(self):
        """No settings file must fail closed, not open."""
        self.assertEqual(MODULE._declared_pi_packages(None), frozenset())
        self.assertEqual(MODULE._declared_pi_packages({}), frozenset())

    def test_unreachable_pi_default_provider_is_reported(self):
        settings = '{"defaultProvider": "anthropic", "defaultModel": "claude-opus-5"}\n'
        failures = self.run_check(pi_settings=settings)
        self.assertTrue(any("defaultProvider" in f for f in failures), failures)

    def test_unreachable_pi_enabled_model_is_reported(self):
        settings = (
            '{"defaultProvider": "opencode-go", "defaultModel": "deepseek-v4.1-flash",'
            ' "enabledModels": ["openrouter/anthropic/claude-opus-5"]}\n'
        )
        failures = self.run_check(pi_settings=settings)
        self.assertTrue(any("enabledModels" in f for f in failures), failures)

    def test_agent_without_model_key_is_reported(self):
        agent = BUILDER.replace("model: anthropic/claude-sonnet-5-5:high\n", "")
        failures = self.run_check(builder=agent)
        self.assertTrue(any("no `model:` key" in f for f in failures), failures)

    # --- docs vs config ------------------------------------------------

    def test_consistent_docs_pass(self):
        self.assertEqual(self.docs_check(), [])

    def test_retired_models_outside_markers_are_ignored(self):
        self.assertIn("claude-opus-4", OMP_DOC)
        self.assertEqual(self.docs_check(), [])

    def test_config_role_change_without_docs_fails_naming_both(self):
        config = BASE_CONFIG.replace("opus-5:medium", "opus-5:high")
        failures = self.docs_check(config=config)
        self.assert_fails(failures, "AGENTS.md:", "`default`", "claude-opus-5:medium", "claude-opus-5:high")

    def test_doc_role_change_without_config_fails(self):
        doc = OMP_DOC.replace("| `task` role | `anthropic/claude-sonnet-5-5:medium` |", "| `task` role | `anthropic/claude-sonnet-5-5:high` |")
        self.assert_fails(self.docs_check(omp_doc=doc), "`task`", "sonnet-5-5:high", "sonnet-5-5:medium")

    def test_config_model_change_without_docs_fails(self):
        config = BASE_CONFIG.replace("builder: anthropic/claude-sonnet-5-5:high", "builder: anthropic/claude-haiku-4-5:high")
        builder = BUILDER.replace("sonnet-5-5", "haiku-4-5")
        self.assert_fails(self.docs_check(config=config, builder=builder), "`builder`", "haiku-4-5:high")

    def test_doc_selector_missing_level_never_matches(self):
        doc = OMP_DOC.replace("| `scout` agent | `opencode-go/glm-5.3-flash:low` |", "| `scout` agent | `opencode-go/glm-5.3-flash` |")
        self.assert_fails(self.docs_check(omp_doc=doc), "AGENTS.md:", "`scout`")

    def test_grouped_row_splits_and_catches_one_member(self):
        doc = OMP_DOC.replace(
            "| `scout` agent | `opencode-go/glm-5.3-flash:low` |",
            "| `default` role; `scout` agent | `opencode-go/glm-5.3-flash:low` |",
        )
        self.assertEqual([f for f in self.docs_check(omp_doc=doc) if "scout" in f], [])
        failures = self.docs_check(omp_doc=doc)
        self.assert_fails(failures, "role `default`", "glm-5.3-flash:low", "claude-opus-5:medium")
        doc = OMP_DOC.replace(
            "| `scout` agent | `opencode-go/glm-5.3-flash:low` |",
            "| `scout`/`builder` agents | `opencode-go/glm-5.3-flash:low` |",
        )
        self.assert_fails(self.docs_check(omp_doc=doc), "agent `builder`")

    def test_role_and_agent_groups_resolve_in_their_own_namespace(self):
        doc = OMP_DOC.replace("| `scout` agent |", "| `scout` role |")
        self.assert_fails(self.docs_check(omp_doc=doc), "is not in modelRoles")

    def test_unparseable_table_row_fails_with_line_number(self):
        doc = OMP_DOC.replace("| `scout` agent |", "| `scout` agent and more |")
        self.assert_fails(self.docs_check(omp_doc=doc), "AGENTS.md:7:", "cannot parse")

    def test_row_without_role_or_agent_word_fails_not_skipped(self):
        doc = OMP_DOC.replace("| `scout` agent |", "| `scout` |")
        self.assert_fails(self.docs_check(omp_doc=doc), "AGENTS.md:7:")

    def test_value_with_trailing_note_fails(self):
        doc = OMP_DOC.replace("`anthropic/claude-sonnet-5-5:medium` |", "`anthropic/claude-sonnet-5-5:medium` (note) |", 1)
        self.assert_fails(self.docs_check(omp_doc=doc), "not one backticked")

    def test_settings_rows_each_checked_in_both_directions(self):
        cases = [
            ("disabledProviders:\n  - openai-codex", "disabledProviders:\n  - openai-codex\n  - google", "disabledProviders"),
            ("usageAwareFallback: true", "usageAwareFallback: false", "retry.usageAwareFallback"),
            ("usageReservePct: 20", "usageReservePct: 30", "retry.usageReservePct"),
            ("usageReservePolicy: auto", "usageReservePolicy: never", "retry.usageReservePolicy"),
            ("maxEffort: high", "maxEffort: xhigh", "task.maxEffort"),
            ("autoThinkingMaxEffort: high", "autoThinkingMaxEffort: max", "providers.autoThinkingMaxEffort"),
        ]
        for old, new, key in cases:
            with self.subTest(key=key):
                self.assert_fails(self.docs_check(config=BASE_CONFIG.replace(old, new)), "AGENTS.md:", key)
        doc = OMP_DOC.replace("`true` / `20` / `auto`", "`true` / `25` / `auto`")
        self.assert_fails(self.docs_check(omp_doc=doc), "retry.usageReservePct", "'25'", "'20'")
        doc = OMP_DOC.replace("`[openai-codex]`", "`[]`")
        self.assert_fails(self.docs_check(omp_doc=doc), "disabledProviders")

    def test_setting_value_count_mismatch_fails(self):
        doc = OMP_DOC.replace("`true` / `20` / `auto`", "`true` / `20`")
        self.assert_fails(self.docs_check(omp_doc=doc), "setting(s)")

    def test_omp_table_found_by_header_not_position(self):
        doc = "| Other | Table |\n| --- | --- |\n| a | b |\n\n" + OMP_DOC
        self.assertEqual(self.docs_check(omp_doc=doc), [])
        self.assert_fails(self.docs_check(omp_doc="no table\n"), "routing table", "not found")

    def test_pi_agent_model_change_without_ladder_fails(self):
        agent = PI_AGENT.replace("glm-5.3-flash", "deepseek-v4.1-flash")
        self.assert_fails(self.docs_check(pi_agent=agent), "pi/model-ladder.md:", "`Explore`", "deepseek-v4.1-flash:low")

    def test_pi_agent_thinking_change_without_ladder_fails(self):
        agent = PI_AGENT.replace("thinking: low", "thinking: high")
        self.assert_fails(self.docs_check(pi_agent=agent), "`Explore`", "glm-5.3-flash:low", "glm-5.3-flash:high")

    def test_pi_ladder_change_without_agent_fails(self):
        doc = PI_DOC.replace("| `Explore` discovery | `opencode-go/glm-5.3-flash` | low |", "| `Explore` discovery | `opencode-go/glm-5.3-flash` | minimal |")
        self.assert_fails(self.docs_check(pi_doc=doc), "`Explore`", "minimal")

    def test_pi_ladder_unknown_agent_fails(self):
        doc = PI_DOC.replace("`Explore` discovery", "`Ghost` discovery")
        self.assert_fails(self.docs_check(pi_doc=doc), "`Ghost`", "no pi/agents/Ghost.md")

    def test_pi_main_session_row_checks_default(self):
        settings = PI_SETTINGS.replace('"defaultThinkingLevel": "high"', '"defaultThinkingLevel": "xhigh"')
        self.assert_fails(self.docs_check(pi_settings=settings), "Main session", "high", "xhigh")
        doc = PI_DOC.replace("| Main session | `opencode-go/deepseek-v4.1-flash` | high |", "| Main session | `opencode-go/glm-5.3-flash` | high |")
        self.assert_fails(self.docs_check(pi_doc=doc), "Main session", "glm-5.3-flash:high")

    def test_pi_manual_fallback_row_must_be_in_enabled_models(self):
        doc = PI_DOC.replace("| Manual fallback (Ctrl+P) | `opencode-go/glm-5.3-flash` | high |", "| Manual fallback (Ctrl+P) | `opencode-go/glm-5.3-flash` | max |")
        self.assert_fails(self.docs_check(pi_doc=doc), "Manual fallback", "enabledModels")
        settings = PI_SETTINGS.replace('"opencode-go/glm-5.3-flash:high"', '"opencode-go/glm-5.3-flash:low"')
        self.assert_fails(self.docs_check(pi_settings=settings), "Manual fallback")

    def test_pi_unparseable_row_fails_with_line_number(self):
        doc = PI_DOC.replace("| `Explore` discovery | `opencode-go/glm-5.3-flash` | low |", "| `Explore` discovery | run it in OMP | \u2014 |")
        self.assert_fails(self.docs_check(pi_doc=doc), "pi/model-ladder.md:6:", "cannot parse")
        doc = PI_DOC.replace("`Explore` discovery", "discovery")
        self.assert_fails(self.docs_check(pi_doc=doc), "pi/model-ladder.md:6:", "cannot parse")

    def test_marked_line_drift_fails_in_both_docs(self):
        doc = OMP_DOC.replace("`default` \u2192 `anthropic/claude-opus-5` medium", "`default` \u2192 `anthropic/claude-opus-5` high")
        self.assert_fails(self.docs_check(omp_doc=doc), "AGENTS.md:", "`default`", "medium", "high")
        doc = PI_DOC.replace("`Explore` \u2192 `opencode-go/glm-5.3-flash` low", "`Explore` \u2192 `opencode-go/glm-5.3-flash` high")
        self.assert_fails(self.docs_check(pi_doc=doc), "pi/model-ladder.md:", "`Explore`")
        doc = PI_DOC.replace("`main` \u2192 `opencode-go/deepseek-v4.1-flash` high", "`main` \u2192 `opencode-go/deepseek-v4.1-flash` xhigh")
        self.assert_fails(self.docs_check(pi_doc=doc), "`main`", "xhigh")

    def test_marked_line_with_shared_names_checks_every_name(self):
        doc = OMP_DOC.replace(
            "`scout` \u2192 `opencode-go/glm-5.3-flash` low\n`builder` \u2192 `anthropic/claude-sonnet-5-5` high",
            "`scout`, `builder` and `default` \u2192 `opencode-go/glm-5.3-flash` low",
        )
        failures = self.docs_check(omp_doc=doc)
        self.assert_fails(failures, "`builder`")
        self.assert_fails(failures, "`default`")
        self.assertFalse(any("`scout`" in f for f in failures), failures)

    def test_marked_line_not_in_fixed_form_fails_with_line_number(self):
        doc = OMP_DOC.replace("`default` \u2192 `anthropic/claude-opus-5` medium", "default is opus 5 at medium")
        self.assert_fails(self.docs_check(omp_doc=doc), "AGENTS.md:16:", "cannot parse marked line")

    def test_marked_line_with_unknown_name_or_missing_level_fails(self):
        doc = OMP_DOC.replace("`default` \u2192", "`ghost` \u2192")
        self.assert_fails(self.docs_check(omp_doc=doc), "`ghost`")
        doc = OMP_DOC.replace("`anthropic/claude-opus-5` medium", "`anthropic/claude-opus-5`")
        self.assert_fails(self.docs_check(omp_doc=doc), "cannot parse marked line")

    def test_marked_scope_prefix_crosses_sources(self):
        doc = OMP_DOC.replace(
            "<!-- routing:end -->",
            "`pi:Explore` \u2192 `opencode-go/glm-5.3-flash` low\n`pi:main` \u2192 `opencode-go/deepseek-v4.1-flash` high\n<!-- routing:end -->",
            1,
        )
        self.assertEqual(self.docs_check(omp_doc=doc), [])
        bad = doc.replace("`pi:Explore` \u2192 `opencode-go/glm-5.3-flash` low", "`pi:Explore` \u2192 `opencode-go/glm-5.3-flash` high")
        self.assert_fails(self.docs_check(omp_doc=bad), "`pi:Explore`")

    def test_duplicate_table_is_checked_not_ignored(self):
        extra = "\n| Roles/settings | Value |\n| --- | --- |\n| `task` role | `anthropic/claude-sonnet-5-5:high` |\n"
        failures = self.docs_check(omp_doc=OMP_DOC + extra)
        self.assert_fails(failures, "AGENTS.md:", "`task`", "claude-sonnet-5-5:high")
        extra = "\n| Task / agent | Provider and model | Effort |\n| --- | --- | --- |\n| `Explore` discovery | `opencode-go/glm-5.3-flash` | high |\n"
        self.assert_fails(self.docs_check(pi_doc=PI_DOC + extra), "pi/model-ladder.md:", "`Explore`")

    def test_table_without_separator_or_rows_fails(self):
        doc = OMP_DOC.replace("| --- | --- |\n", "")
        self.assert_fails(self.docs_check(omp_doc=doc), "AGENTS.md:", "separator")
        doc = "| Roles/settings | Value |\n| --- | --- |\n\n" + OMP_DOC.split("| --- | --- |\n", 1)[0].replace("| Roles/settings | Value |\n", "")
        self.assert_fails(self.docs_check(omp_doc=doc), "no rows")

    def test_suffixed_or_malformed_markers_fail_not_skip(self):
        doc = OMP_DOC.replace("<!-- routing:current -->", "<!-- routing:current --> extra")
        self.assert_fails(self.docs_check(omp_doc=doc), "AGENTS.md:", "malformed routing marker")
        doc = OMP_DOC.replace("<!-- routing:end -->", "<!-- routing:end --> extra")
        self.assert_fails(self.docs_check(omp_doc=doc), "malformed routing marker")
        doc = OMP_DOC.replace("<!-- routing:current -->", "<!--routing:current-->")
        self.assert_fails(self.docs_check(omp_doc=doc), "malformed routing marker")

    def test_backticked_marker_mentions_are_prose(self):
        doc = OMP_DOC + "\nUse `<!-- routing:current -->` and `<!-- routing:end -->` to mark lines.\n"
        self.assertEqual(self.docs_check(omp_doc=doc), [])

    def test_bullet_form_is_not_in_the_grammar(self):
        doc = OMP_DOC.replace("`default` \u2192", "- `default` \u2192")
        self.assert_fails(self.docs_check(omp_doc=doc), "AGENTS.md:", "cannot parse marked line")

    def test_empty_marked_block_fails(self):
        doc = OMP_DOC.replace("<!-- routing:current -->\n", "<!-- routing:current -->\n<!-- routing:end -->\n<!-- routing:current -->\n", 1).replace(
            "`default` \u2192 `anthropic/claude-opus-5` medium\n", "", 1)
        self.assert_fails(self.docs_check(omp_doc=doc), "no lines to check")

    def test_unbalanced_markers_fail(self):
        self.assert_fails(self.docs_check(omp_doc=OMP_DOC.replace("<!-- routing:end -->", "")), "never closed")
        self.assert_fails(self.docs_check(omp_doc=OMP_DOC.replace("<!-- routing:current -->", "")), "without")

    def test_doc_without_any_marked_block_fails(self):
        doc = OMP_DOC.replace("<!-- routing:current -->\n", "").replace("<!-- routing:end -->\n", "")
        self.assert_fails(self.docs_check(omp_doc=doc), "AGENTS.md:", "no routing:current block")
        doc = PI_DOC.replace("<!-- routing:current -->\n", "").replace("<!-- routing:end -->\n", "")
        self.assert_fails(self.docs_check(pi_doc=doc), "pi/model-ladder.md:", "no routing:current block")

    def test_missing_doc_fails(self):
        parsed, _ = MODULE.parse_config(BASE_CONFIG, "omp/config.yml")
        failures = MODULE.check(parsed, {"builder.md": BUILDER}, {"Explore.md": PI_AGENT}, json.loads(PI_SETTINGS), docs={})
        self.assert_fails(failures, "AGENTS.md: missing")



class ClaudeAgentModelTest(unittest.TestCase):
    def agent(self, model_line):
        return {"scout.md": f"---\nname: scout\ndescription: x\n{model_line}---\n\nBody\n"}

    def test_claude_alias_and_id_pass(self):
        self.assertEqual(MODULE.check_claude_agents(self.agent("model: haiku\n")), [])
        self.assertEqual(
            MODULE.check_claude_agents(self.agent("model: claude-sonnet-5-5\n")), []
        )

    def test_non_claude_model_is_reported(self):
        failures = MODULE.check_claude_agents(self.agent("model: opencode-go/glm-5.3-flash\n"))
        self.assertTrue(any("not a Claude alias" in f for f in failures), failures)

    def test_missing_model_is_reported(self):
        failures = MODULE.check_claude_agents(self.agent(""))
        self.assertTrue(any("inherits" in f for f in failures), failures)

if __name__ == "__main__":
    unittest.main(verbosity=1)
