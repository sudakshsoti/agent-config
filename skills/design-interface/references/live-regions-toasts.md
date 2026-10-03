# Live regions and toasts

Read when a surface announces a status, error or outcome to assistive technology, or shows a toast, snackbar or inline notification.

- A status region is `aria-live="polite"`; `assertive` is for errors only. Verify in the accessibility tree.
- A repeated polite announcement renders as a stable, empty `aria-live="polite"` region before its text is ever populated, rather than being inserted into the DOM already carrying content; a dynamically inserted `role="alert"` is announced inconsistently across screen-reader and browser combinations, so test the specific combinations the project targets. Keep each message short and self-contained, because `aria-atomic` re-reads the whole region on every change. Never move focus to a toast; stage a loading update with `aria-busy="true"` on the region, then announce the outcome. Verify in the accessibility tree that the live region exists before its content changes.
- An auto-dismissing toast never carries the only path to an action; auto-dismissal suits low-stakes confirmation only. Where a toast must time out, 5 seconds is the floor, and hovering or focusing it pauses the timer. Verify by checking whether the toast's action remains reachable elsewhere after it disappears.
