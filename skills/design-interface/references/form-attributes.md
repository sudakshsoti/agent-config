# Form field attributes: autocomplete, inputmode, spellcheck

Citation: HTML Living Standard, "Autofill" (autofill field / autofill detail token processing model), https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#autofill.

## `autocomplete` tokens

Every field that collects information about the user takes a meaningful `autocomplete` value; the spec defines these as autofill detail tokens consumed by the user agent's autofill algorithm.

| Field | `autocomplete` |
| --- | --- |
| Full name | `name` |
| Email | `email` |
| Phone | `tel` |
| Street address | `street-address` |
| Postal code | `postal-code` |
| Card number | `cc-number` |
| Card expiry | `cc-exp` |
| Card security code | `cc-csc` |
| Card holder name | `cc-name` |
| Username | `username` |
| Current password | `current-password` |
| New password | `new-password` |
| One-time code | `one-time-code` |

Where a field belongs to a specific address group, prefix the token with `shipping` or `billing`: `autocomplete="shipping street-address"`, `autocomplete="billing postal-code"`. The prefix is a separate space-delimited token before the field name, per the spec's autofill detail token grammar; it is not a hyphenated variant of the token itself.

## `inputmode` and `type`

`inputmode` selects the on-screen keyboard without changing the field's value type; `type` changes both. Picking the wrong one either loses the numeric keyboard or forces the wrong parsing:

| Case | Attributes | Why |
| --- | --- | --- |
| One-time code | `type="text" inputmode="numeric"` | Numeric keyboard without the stepper/spinner or value coercion a `type="number"` field applies, which would strip a leading zero from a code such as `0192` |
| Money / decimal amount | `type="text" inputmode="decimal"` | Numeric keyboard that permits a decimal separator; `inputmode="numeric"` omits it and `type="number"` again coerces the value |
| True numeric quantity (e.g. item count) | `type="number"` | The value is genuinely numeric and coercion is correct |

## `spellcheck`

Set `spellcheck="false"` on email, one-time-code, and username fields. These values are never dictionary words, so spellcheck offers no benefit and instead red-underlines valid input and can interfere with browser/OS autocorrect substituting a "corrected" value into the field.
