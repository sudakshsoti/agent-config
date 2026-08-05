# Motion standards

## Decide before animating

Every motion must earn its cost. State its purpose: feedback, spatial
orientation, state indication, continuity, explanation or a rare moment of
delight. Consider frequency: repeated actions, especially keyboard-first ones,
need no motion or the shortest perceptible feedback; occasional transitions can
carry more context; rare explanatory moments can be more expressive. Never
block input for decoration.

Match motion to the product's character and existing conventions. Test the
complete state change, including entry, exit, interruption and an error or
empty state.

## Timing and easing

Use component-specific ranges as starting points, then validate in context:

| Interaction | Starting range |
| --- | --- |
| Press feedback | 100–160 ms |
| Tooltip or small popover | 125–200 ms |
| Dropdown or select | 150–250 ms |
| Modal or drawer | 200–500 ms |
| Deliberate hold confirmation | Match the required hold time; release promptly |

Use an ease-out curve for entering or user-triggered responses, an
ease-in-out curve for an object already moving between visible states, and
linear only for progress or other intentionally constant motion. A spring has
no fixed duration: choose damping and response/physics for the required feel.
Default to critically damped or near-critically damped motion. Reserve visible
overshoot for momentum-bearing or intentionally playful interactions, not
routine menus.

Keep enter and exit spatially consistent. Set a transform origin that explains
the relationship to a trigger; centred dialogs are the usual exception. For
rapid state changes, animate from the current presentation value and preserve
velocity where the library supports it.

## Implementation and performance

Prefer compositor-friendly `transform` and `opacity` where they express the
interaction. Animate layout dimensions when real spatial continuity requires
them, such as an accordion or a reflowing list, only after measuring the
affected work and controlling the scope. Do not make blanket claims that a
property, browser API or library always runs on the GPU or off the main thread.

Use CSS transitions for ordinary state-to-state changes, keyframes for
predetermined sequences, and an imperative or spring system when continuous
input, velocity hand-off or interruption requires it. `requestAnimationFrame`
is display-synchronised, not a performance guarantee. Measure on the target
browser and device with browser performance tools; check for long frames,
layout/paint cost and input latency. Use `will-change` sparingly and remove it
when the imminent animation ends.

Avoid `transition: all`; name the animated properties. Keep transform origins
intentional. Do not start a UI element at `scale(0)` when a small visible scale
plus opacity communicates its origin better. Gate hover motion behind
`(hover: hover) and (pointer: fine)`.

## Accessibility and input parity

Honour `prefers-reduced-motion: reduce`: replace travel, parallax, elastic
motion and large repositioning with a short opacity transition or a static
state while retaining essential feedback. Do not rely on motion alone to convey
state. Ensure a keyboard and assistive-technology path reaches the same outcome
as every gesture, with visible focus and no transition-based input lockout.

For moving or translucent surfaces, also consider supported contrast and
reduced-transparency preferences, but feature-detect and provide a readable
fallback. Test focus restoration, escape/cancel, screen resize and interruption.

## Quality gates

Before calling motion complete, confirm:

- it has a named purpose and acceptable frequency cost;
- it responds at input time and remains interruptible where users can redirect it;
- direction, origin and exit path preserve spatial continuity;
- reduced-motion and keyboard paths work;
- the rendered interaction is measured on a representative target device.
