# Disabled and loading controls

Read when a control can be disabled, loading, or unavailable. The first rule fixes what a disabled state means; the second picks the mechanism. For how long a press may go unacknowledged, and what loading treatment to show, see `loading-states.md`.

- A disabled or loading control cannot be activated: it has a visually distinct state, and it is focusable only when it carries `aria-disabled="true"`, in which case it still blocks activation. Verify by inspecting both the render and the focus behaviour.
- Use native `disabled` only when a control is genuinely unavailable; reach for `aria-disabled="true"` when it must stay focusable, and never set both on one element. `aria-disabled` changes announcement only, so pointer activation, keyboard activation, and form submission must be blocked in code — verify by attempting all three against the disabled control. A tooltip attached to a natively `disabled` control never opens, because the control leaves the tab order and suppresses pointer events; put the reason in text beside the control instead, or switch to `aria-disabled`.
