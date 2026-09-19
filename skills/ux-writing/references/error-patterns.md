# Error Message Patterns

Detailed patterns for the four error message types. All errors should explain the problem and provide a solution — never a dead end.

General pattern: `[What failed]. [Why/context]. [What to do].`

## Tone

Errors are calm and plain with zero playfulness and no empathy move. Do not acknowledge frustration, apologize, or soften the message — state the problem and the fix.

## Validation Errors (Inline)

- Show as user completes field or on blur
- Brief, specific guidance to correct input
- Pattern: `[Field] [specific requirement]`
- Examples:
  - "Email must include @"
  - "Password must be at least 8 characters"
  - "Choose a date in the future"
- Timing: Real-time or on field exit
- Location: Below or beside the field

## System Errors (Modal/Banner)

- Show when backend operations fail
- Explain what happened and why
- Pattern: `[Action failed]. [Likely cause]. [Recovery step].`
- Examples:
  - "Payment failed. Your card was declined. Try a different payment method."
  - "Couldn't save changes. Connection lost. Reconnect and try again."
  - "Upload failed. File is too large. Choose a file under 10MB."
- Timing: Immediately after failure
- Location: Modal dialog or prominent banner

## Blocking Errors (Full-screen)

- Prevent continued use until resolved
- Clear explanation of blocker and resolution
- Pattern: `[What's blocked]. [Why]. [Specific action needed].`
- Examples:
  - "Update required. This version is no longer supported. Update now to continue."
  - "Subscription expired. Your account is paused. Renew subscription to restore access."
  - "Verification needed. Confirm your email to access features. Check your inbox."
- Timing: On app launch or feature access
- Location: Full screen or large modal

## Permission Errors

- Explain benefit before requesting permission
- Pattern: `[User benefit]. [Permission needed].`
- Examples:
  - "Get notified when orders ship. Enable notifications."
  - "Find nearby stores. Allow location access."
  - "Back up your photos. Grant storage permission."
- Timing: When feature is first used
- Location: In context of the feature

## What to Avoid

- Technical codes without explanation ("Error 403")
- Blame language ("invalid input", "illegal character")
- Robotic tone ("An error has occurred")
- Dead ends (error with no recovery path)
- Vague causes ("Something went wrong")
- "We" — it invites ambiguity about who failed and reads as deflection: "Unable to load content", not "We're having trouble loading this content"

## Prevent, Don't Just Reword

Show hints before the mistake, not after — a password rule stated up front beats a rejection message. When the same error keeps firing for users, redesign the interaction so the error cannot happen; rewording the message again is not a fix.
