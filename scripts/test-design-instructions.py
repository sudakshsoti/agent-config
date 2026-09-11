#!/usr/bin/env python3
"""Check the cross-harness interface-intent instruction contract.

This is a contract smoke test. It checks routing language and structured prompt
fixtures; it does not claim to measure whether a model obeys the contract.
"""

from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]


def require(path: Path, text: str) -> None:
    content = path.read_text(encoding="utf-8")
    if text not in content:
        raise AssertionError(f"{path.relative_to(ROOT)} is missing {text!r}")


def main() -> int:
    global_agents = ROOT / "global-agents.md"
    interface = ROOT / "skills/design-interface/SKILL.md"
    visual = ROOT / "skills/design-visual-system/SKILL.md"
    typography = ROOT / "skills/design-typography/SKILL.md"
    artifact = ROOT / "skills/frontend-artifact/SKILL.md"
    infographic = ROOT / "ux-first-pi-configuration-plan.html"
    plugins = ROOT / "plugins.txt"
    skills_readme = ROOT / "skills/README.md"
    cases = ROOT / "tests/design-intent-cases.md"

    for surface_class in (
        "marketing/brand",
        "reference/documentation",
        "task utility",
        "dashboard/data",
        "settings/form",
        "content/editorial",
    ):
        require(global_agents, surface_class)
    require(global_agents, "frontend-design` is for marketing and brand surfaces only")
    require(global_agents, "applicable `[stated]` project decisions")
    require(global_agents, "narrowest target viewport")

    require(interface, "## Surface intent gate")
    require(interface, "top 40% of the viewport")
    require(interface, "A screen needs an accessible name, not automatically a large visible heading")
    require(interface, "First-run help is a state, not permanent page furniture")
    require(visual, "Opening hierarchy follows the surface’s job")
    require(visual, "A polished header does not count as useful content")
    require(visual, "Begin reference, utility and dashboard surfaces with a solid background")
    require(typography, "reserve monospace for code, key sequences")
    require(typography, "A visible title earns space only when it adds orientation")
    require(artifact, "This is a hard gate")
    require(artifact, "do not write or edit files")
    require(typography, "font-kerning: normal")
    require(typography, "Negative tracking is limited to proofed display typography")
    require(typography, "inspect the current Google Fonts catalogue")

    visual_text = visual.read_text(encoding="utf-8")
    for retired_example in (
        "grotesque at tight tracking",
        "Söhne Buch at 16px with -1% tracking",
    ):
        if retired_example in visual_text:
            raise AssertionError(f"design-visual-system retains {retired_example!r}")

    infographic_text = infographic.read_text(encoding="utf-8")
    if re.search(r"letter-spacing\s*:\s*-", infographic_text):
        raise AssertionError("UX-first Pi infographic contains negative letter-spacing")

    plugin_text = plugins.read_text(encoding="utf-8")
    if "Product screens go to `app-ui`" in plugin_text:
        raise AssertionError("plugins.txt still routes product screens to archived app-ui")
    require(plugins, "lookup-documentation surfaces follow the always-loaded")
    require(skills_readme, "The active design set is")
    if "`design-visual-system`, and most of the `design-brief` pipeline" in skills_readme.read_text(encoding="utf-8"):
        raise AssertionError("skills/README.md still calls active design skills archived")

    case_text = cases.read_text(encoding="utf-8")
    expected_cases = {
        "cheatsheet": "reference/documentation",
        "settings": "settings/form",
        "dashboard": "dashboard/data",
        "landing page": "marketing/brand",
    }
    for name, expected_class in expected_cases.items():
        marker = f"## Case: {name}"
        if marker not in case_text:
            raise AssertionError(f"missing structured case {name!r}")
        section = case_text.split(marker, 1)[1].split("\n## Case:", 1)[0]
        if f"- Expected class: {expected_class}" not in section:
            raise AssertionError(f"case {name!r} has the wrong expected class")
        for field in (
            "Frequency:",
            "Reading mode:",
            "Narrowest viewport:",
            "First viewport target:",
            "Allowed opening blocks:",
            "Forbidden defaults:",
            "Typography roles:",
        ):
            if f"- {field}" not in section:
                raise AssertionError(f"case {name!r} is missing {field}")

    print("design instruction contract: ok")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AssertionError, OSError) as exc:
        print(f"design instruction contract: FAIL ({exc})")
        raise SystemExit(1)
