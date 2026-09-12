# Critic prompt

A reviewer with fresh context is harder on a page than the session that built it. Run this pass as a separate process with the screenshots attached and the audit output pasted in. The reviewer must return the fixed format below; a bare "looks good" or "ship" is not an answer.

## Run it

Codex, from the artifact directory, after the screenshots and `audit.txt` exist:

```sh
codex exec -i mobile.png -i desktop.png -i "$SKILL_ROOT/screenshots/$LANGUAGE/reference.png" \
  "$(sed "s/{{LANGUAGE}}/$LANGUAGE/; s/{{JOB}}/$JOB/" "$SKILL_ROOT/references/critic-prompt.md" | sed -n '/^## Prompt/,$p')

$(cat audit.txt)" < /dev/null
```

Check `codex exec --help` for the image flag on the installed version; `-i` and `--image` are the documented forms. Pi attaches the same three images to a model with verified image input. Claude Code reads the PNGs directly in a subagent with the same prompt. If no image-capable reviewer is available, say "Critic pass unavailable" in the report; do not run the prompt text-only and call it a review.

Pass the language profile's three distinguishing features into the `{{FEATURES}}` slot, and the artifact's stated job into `{{JOB}}`.

## Prompt

You are reviewing a rendered standalone web page against a selected visual language. You are not the author. Do not be polite; be specific and measurable. Every claim you make must point at something visible in the screenshots or a line in the audit output.

Language: {{LANGUAGE}}. Job of the page: {{JOB}}.

The language's three distinguishing features:
{{FEATURES}}

You have three images: the page at 390px wide, the page at 1440px wide, and the reference screenshot for this language. The reference is evidence of relationships (measure, hierarchy, spacing, how evidence sits beside text), not a brand to copy.

Answer in exactly this structure.

**1. Three differences from the reference.** For each, name the relationship in the reference, what the page does instead, and whether the difference is justified by the page's content. Ratios and pixel estimates, not adjectives.

**2. Feature check.** For each of the three distinguishing features: visible, partly visible, or absent, with the element that proves it.

**3. Generic tells.** List every item from this set you can see: hero opening, three-column feature grid, card around every section, gradient, shadow on static content, pill badges, emoji icons, centred title over left prose, uniform spacing, system or fallback font rendering, decorative dividers or numbering, filler copy. Say "none" only if none is visible.

**4. Audit output.** For each FAIL in the pasted audit, say whether the screenshot confirms it and what the fix is. For each WARN, say keep or fix.

**5. First useful unit.** At 390px, what is the first thing a reader can use, and how far down does it start?

**6. Verdict.** `ship` or `fix`. If `fix`, list at most five changes in priority order, each as observation → change. The builder gets one pass, so put the change with the largest visible effect first.
