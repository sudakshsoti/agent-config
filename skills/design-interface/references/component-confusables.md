# Component confusables

Pairs that look alike but differ in behaviour, so the wrong pick breaks an expectation the user already has. Pick by behaviour, not by appearance.

## Tooltip vs popover

A tooltip is a hover/focus label that explains an element; it cannot hold interactive content — no links, no buttons. A popover is a click-anchored overlay that can hold interactive content and stays open until dismissed. A link or button living inside a "tooltip" is the tell that it should have been a popover.

## Badge vs tag

A badge is attached to another element and read-only — a count, or a status word. A tag is standalone and interactive: selectable, removable, used to categorise or filter. A badge is pinned on; a tag is handled.

## Dialog vs sheet vs drawer

All three are overlays. A dialog interrupts the flow centre-screen to demand a decision now, with focus trapped and the background inert. A sheet slides in from a screen edge for secondary or contextual actions. A drawer is a bottom sheet pulled up from the base, a frequent mobile substitute for a dialog. Reach for a dialog when the choice must be made now; reach for a sheet or drawer when the surface is secondary and dismissible.

## Gotcha

Agents use this list to rename a component instead of changing its behaviour — swapping the label from "tooltip" to "popover" on an element that still dismisses on pointer-leave fixes nothing. The behaviour has to change first; the name follows.

## Sources

- Retired skill design-engineering, file skills/design-engineering/references/components/component-confusables.md @ `81805dc89d40889639a95502bfb578a098266dc8`.
