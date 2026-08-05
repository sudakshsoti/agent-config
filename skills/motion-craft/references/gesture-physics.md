# Gesture physics

## Direct manipulation

Respond on pointer-down and keep feedback continuous during the gesture. Use
Pointer Events and `setPointerCapture()` so a drag continues outside the
element. Preserve the grab offset rather than snapping the element to the
pointer. Track a short position and timestamp history so release velocity is
available; ignore additional touch points once a drag has started.

Apply a small movement threshold before committing to a drag direction. Consider
plausible gesture directions from the first move, then cancel losing recognisers
once intent is clear. Avoid APIs that report only a completed swipe: the user
needs 1:1 feedback while moving. Keep hit targets forgiving and allow cancelling
a tap by dragging away where that fits the control.

## Interruption and velocity

Never lock input while a gesture-driven element settles. Start a new animation
from the element's current presentation value, not its prior target. Carry the
release velocity into the spring when the chosen library supports it; retain its
sign when deciding whether to reverse or commit. For independent horizontal and
vertical behaviours, model the axes independently when their velocities differ.

For a flick, project a plausible resting point from the release velocity and
then choose the nearest allowed snap point. Treat this as a product-tuned
heuristic, not universal physics. Test slow drags, fast flicks, reversal during
settling and a second pointer-down mid-transition.

## Boundaries and resistance

At a boundary, progressively resist overshoot rather than abruptly freezing the
element, unless the constraint itself must be unmistakable. Increase resistance
with distance; on release, settle to a valid snap point. Match the entry and
exit direction so users can predict where the object came from and where it is
going.

## Sheets, drawers and swipe dismissal

Track a sheet or drawer 1:1 during drag. On release, combine position and
velocity to select a snap point or dismissal; a fast intentional flick can
outweigh distance, but the threshold must be calibrated on devices. Give users
an explicit close action and an equivalent keyboard route. Restore focus after
dismissal and do not make the dragged surface the only path to content.

Use a critically damped settle by default. Add modest bounce only when a
momentum-bearing gesture makes the energy legible. Reduced motion should avoid
travel and elastic settling while leaving the state change understandable.

## Gesture test matrix

Test pointer, touch and keyboard paths for:

- press feedback and cancellation;
- slow drag, fast flick, boundary resistance and release;
- mid-flight re-grab and reverse;
- focus handling, Escape and explicit close;
- reduced motion and a narrow viewport.
