#!/usr/bin/env python3
"""test-check-model-routing.py — the drift cases check-model-routing.py must catch.

Each test builds a throwaway repo tree, so the real checkout is never touched.
The negative cases are the ones that matter: a check that only ever passes on
the current tree is not a check.
"""

import importlib.util
import os
import sys
import tempfile
import textwrap
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
  task: anthropic/claude-sonnet-5:medium
disabledProviders:
  - openai-codex
task:
  agentModelOverrides:
    builder: anthropic/claude-sonnet-5:high
    scout: opencode-go/glm-5.3-flash:low
retry:
  fallbackChains:
    anthropic/claude-opus-5:
      - anthropic/claude-sonnet-5:high
"""

OVERLAY = """\
modelRoles:
  default: opencode-go/glm-5.3-flash:high
  task: opencode-go/glm-5.3-flash:high
disabledProviders:
  - anthropic
task:
  agentModelOverrides:
    builder: opencode-go/glm-5.3-flash:high
    scout: opencode-go/glm-5.3-flash:low
"""

BUILDER = """\
---
name: builder
description: Implements an approved UX plan.
model: anthropic/claude-sonnet-5:high
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


class RoutingCheckTest(unittest.TestCase):
    def build(self, **overrides):
        root = Path(tempfile.mkdtemp())
        files = {
            "omp/config.yml": BASE_CONFIG,
            "omp/overlays/go-overlay.yml": OVERLAY,
            "omp/agents/builder.md": BUILDER,
            "pi/agents/Explore.md": PI_AGENT,
            "pi/settings.json": PI_SETTINGS,
        }
        files.update(overrides)
        for relative, content in files.items():
            path = root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
        return root

    def test_clean_tree_passes(self):
        self.assertEqual(MODULE.check(str(self.build())), [])

    def test_real_repo_passes(self):
        self.assertEqual(MODULE.check(str(ROOT)), [])

    def test_frontmatter_drift_is_reported(self):
        drifted = BUILDER.replace(
            "model: anthropic/claude-sonnet-5:high", 'model: "@default"'
        )
        failures = MODULE.check(str(self.build(**{"omp/agents/builder.md": drifted})))
        self.assertTrue(any("resolves to" in f and "builder" in f for f in failures), failures)

    def test_alias_matching_its_override_passes(self):
        aliased = BUILDER.replace(
            "model: anthropic/claude-sonnet-5:high", 'model: "@task"'
        )
        config = BASE_CONFIG.replace(
            "builder: anthropic/claude-sonnet-5:high",
            "builder: anthropic/claude-sonnet-5:medium",
        )
        failures = MODULE.check(
            str(self.build(**{"omp/agents/builder.md": aliased, "omp/config.yml": config}))
        )
        self.assertEqual([f for f in failures if "builder" in f], [])

    def test_override_key_naming_no_agent_is_reported(self):
        config = BASE_CONFIG.replace(
            "    scout: opencode-go/glm-5.3-flash:low",
            "    scout: opencode-go/glm-5.3-flash:low\n    librarian: opencode-go/glm-5.3-flash:low",
        )
        failures = MODULE.check(str(self.build(**{"omp/config.yml": config})))
        self.assertTrue(any("librarian" in f and "names no agent" in f for f in failures), failures)

    def test_overlay_missing_role_is_reported(self):
        overlay = OVERLAY.replace("  task: opencode-go/glm-5.3-flash:high\n", "")
        failures = MODULE.check(str(self.build(**{"omp/overlays/go-overlay.yml": overlay})))
        self.assertTrue(any("modelRoles.task not overridden" in f for f in failures), failures)

    def test_overlay_missing_agent_is_reported(self):
        overlay = OVERLAY.replace("    builder: opencode-go/glm-5.3-flash:high\n", "")
        failures = MODULE.check(str(self.build(**{"omp/overlays/go-overlay.yml": overlay})))
        self.assertTrue(
            any("agentModelOverrides.builder not overridden" in f for f in failures), failures
        )

    def test_selector_pinned_to_locally_disabled_provider_is_reported(self):
        config = BASE_CONFIG.replace(
            "  default: anthropic/claude-opus-5:medium",
            "  default: openai-codex/gpt-5.6-luna:high",
        )
        failures = MODULE.check(str(self.build(**{"omp/config.yml": config})))
        self.assertTrue(any("disabledProviders" in f for f in failures), failures)

    def test_malformed_selector_is_reported(self):
        config = BASE_CONFIG.replace(
            "  default: anthropic/claude-opus-5:medium", "  default: claude-opus-5:medium"
        )
        failures = MODULE.check(str(self.build(**{"omp/config.yml": config})))
        self.assertTrue(any("provider/model" in f for f in failures), failures)

    def test_unknown_effort_is_reported(self):
        config = BASE_CONFIG.replace(
            "  default: anthropic/claude-opus-5:medium",
            "  default: anthropic/claude-opus-5:enormous",
        )
        failures = MODULE.check(str(self.build(**{"omp/config.yml": config})))
        self.assertTrue(any("provider/model" in f for f in failures), failures)

    def test_claude_pin_in_pi_agent_is_reported(self):
        agent = PI_AGENT.replace(
            "model: opencode-go/glm-5.3-flash", "model: anthropic/claude-opus-5"
        )
        failures = MODULE.check(str(self.build(**{"pi/agents/Explore.md": agent})))
        self.assertTrue(
            any("no working credential path" in f for f in failures), failures
        )

    def test_unreachable_pi_default_provider_is_reported(self):
        settings = '{"defaultProvider": "anthropic", "defaultModel": "claude-opus-5"}\n'
        failures = MODULE.check(str(self.build(**{"pi/settings.json": settings})))
        self.assertTrue(any("defaultProvider" in f for f in failures), failures)

    def test_unreachable_pi_enabled_model_is_reported(self):
        settings = (
            '{"defaultProvider": "opencode-go", "defaultModel": "deepseek-v4.1-flash",'
            ' "enabledModels": ["openrouter/anthropic/claude-opus-5"]}\n'
        )
        failures = MODULE.check(str(self.build(**{"pi/settings.json": settings})))
        self.assertTrue(any("enabledModels" in f for f in failures), failures)

    def test_agent_without_model_key_is_reported(self):
        agent = BUILDER.replace("model: anthropic/claude-sonnet-5:high\n", "")
        failures = MODULE.check(str(self.build(**{"omp/agents/builder.md": agent})))
        self.assertTrue(any("no `model:` key" in f for f in failures), failures)


if __name__ == "__main__":
    unittest.main(verbosity=1)
