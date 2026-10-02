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
task:
  agentModelOverrides:
    builder: anthropic/claude-sonnet-5-5:high
    scout: opencode-go/glm-5.3-flash:low
retry:
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

PI_SETTINGS = '{"defaultProvider": "opencode-go", "defaultModel": "deepseek-v4.1-flash"}\n'
PI_SETTINGS_WITH_SHIM = (
    '{"defaultProvider": "opencode-go", "defaultModel": "deepseek-v4.1-flash",'
    ' "packages": ["npm:pi-memory", "npm:@gotgenes/pi-anthropic-auth"]}\n'
)


class RoutingCheckTest(unittest.TestCase):
    def run_check(self, config=BASE_CONFIG, builder=BUILDER, pi_agent=PI_AGENT, pi_settings=PI_SETTINGS):
        parsed, parse_failures = MODULE.parse_config(config, "omp/config.yml")
        self.assertEqual(parse_failures, [])
        return MODULE.check(
            parsed,
            {"builder.md": builder},
            {"Explore.md": pi_agent},
            json.loads(pi_settings),
        )

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


if __name__ == "__main__":
    unittest.main(verbosity=1)
