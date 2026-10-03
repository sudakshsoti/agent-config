# Forms and validation

Read when building or reviewing a form, a field, or an error state. Field attributes (`autocomplete`, `inputmode`, `type`) are in `form-attributes.md`. Blur validation shows errors but never blocks submit; the submit rules below govern what a submit attempt does.

- Every form control must have a programmatically associated label. Verify with an accessibility tree inspection, not by eye.
- An error state must name what is wrong and, where fixable by the user, what to do about it. Verify by reading the error copy against those two criteria.
- Validation runs inline as the user types — soft while typing, hard on blur — rather than being deferred to submit; a failed submit still moves focus to the first invalid field. Verify by submitting an invalid form and reading `document.activeElement`.
- The submit control is not disabled until the form is valid, because disabling it removes the route to the error messages. Verify by loading the empty form and reading the submit control's disabled state.
- A submit attempt is never blocked by client-side validation; an incomplete or invalid submission still runs, so every field's error surfaces at once rather than only the first one caught while typing. Input is accepted as free text with no character filtering as the user types, and every value is trimmed before validation, since autocomplete and text expansion add trailing spaces. Verify by submitting a form with several invalid fields at once and confirming every error appears together, and by validating a value with leading or trailing whitespace.
- An invalid field carries `aria-invalid` and an `aria-describedby` pointing at its message. Verify in the accessibility tree, not the DOM.
