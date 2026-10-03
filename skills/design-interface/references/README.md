# references: interface

Evidence-backed detail that supports `../SKILL.md`: measured target-size thresholds by platform, keyboard-order worked examples, tested empty/overflow state comparisons, accessibility-tree checks with named tools, and citations to interaction research.

Not for: a component library, a set of ready-made field styles, theme values, or any recipe presented as the correct look. Those belong in a project's `design/decisions.md`, not here.

Naming: kebab-case, one topic per file, for example `forms-validation.md`, `disabled-state.md`, `target-size-exceptions.md`, or `form-attributes.md`. `../SKILL.md` points to each file from the branch that needs it.

Every file must carry its evidence: a measurement, a citation, or a named real project case. An assertion with no evidence attached does not belong here — raise it as an open question in `../SKILL.md` instead.

## Gotcha

Agents read "a measurement, a citation, or a named real project case" and paste in a plausible-sounding citation without checking it actually supports the claim being filed — an accessibility guideline that discusses a related but different threshold, cited as if it settled this one.
