# Component polish

Use this reference only when motion implementation also changes component
defaults, public API, naming or documentation.

## Defaults and interaction detail

Ship a component that feels complete without configuration. Give pressable
controls immediate, subtle active feedback when it does not interfere with
their semantics. Keep popovers origin-aware; retain a centred origin for
viewport-centred dialogs. After one tooltip is open, adjacent tooltips may open
without their initial delay when that improves scanning.

Use transitions for state changes that must retarget during rapid interaction;
use keyframes for predetermined sequences. Pair list entry/exit opacity with
the required spatial change and tune the combination in the rendered component.
For deliberate hold-to-confirm actions, make the hold clearly progressive and
the release or cancellation prompt.

## Component API and naming

Prefer a small API and strong defaults over a menu of timing and easing knobs.
Expose configuration only when product use cases require it. Name components
and variants for the behaviour or user outcome, not their implementation.
Choose a memorable name where it benefits the product, while retaining clear
documentation and discoverable examples.

Handle edge cases invisibly: pause time-based UI when appropriate, retain drag
capture, preserve hover bridges for stacked/transient surfaces, and keep focus
and cancellation reliable. Match the motion personality to the component's job:
a daily dashboard control should be crisp; a rare celebratory moment may carry
more expression.

## Documentation and validation

Document the default behaviour, keyboard path, reduced-motion behaviour,
configuration boundary and known interaction constraints. Provide a runnable
example that lets users test the component rather than only reading a static
description.

Review motion in slow motion or frame-by-frame and on a physical touch device
when gesture behaviour matters. Revisit it with fresh eyes after the initial
implementation; inspect timing, transform origin and synchronisation of all
animated properties.
