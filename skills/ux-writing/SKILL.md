---
name: ux-writing
description: "Use for writing, editing, or auditing interface microcopy: controls, forms, errors, onboarding, empty states, notifications, voice, tone. Not for long-form prose (writing-editor) or visual and type decisions."
disable-model-invocation: true
---

# UX Writing

Write clear, concise, user-centered interface copy (UX text/microcopy) for digital products and experiences. This skill provides frameworks, patterns, and best practices for creating text that helps users accomplish their goals.

## Workflow

Run these steps for every string. For an audit, step 3 produces the findings and the Reporting section below is the exit criterion.

1. **Understand context** — user goal, business objective, technical constraints, the user's emotional state.
2. **Draft** — start from what you would say out loud, apply the matching pattern below, then voice and tone.
3. **Edit against the four standards**
   - **Purposeful**: helps the user or the business reach a goal; focus on user benefits, not features; answer the question the user will have; use "you"; match the user's language and mental models.
   - **Concise**: every word has a job; front-load the important information; cut deadwood ("in order to" → "to", "due to the fact that" → "because", "at this point in time" → "now"); one adjective is usually enough; break dense text into scannable chunks.
   - **Conversational**: read it aloud and ask whether you would say it; keep the articles and prepositions; prefer active voice unless passive is clearer.
   - **Clear**: specific verbs, one term per concept, no jargon or idioms. Match the length and reading-level targets in references/benchmarks.md. Never build a sentence from fragments around a variable ("You have " + n + " new messages") — word order changes per language; use one templated string with proper pluralization. Match the input device: "tap" on touch, "click" with a pointer, "select" when both are possible.
4. **Check** — each string matches its pattern, and any table row cites `file:line`.

## UX Text Patterns

Apply these common patterns for interface elements.

### Titles

- **Purpose**: Orient users to where they are
- **Format**: Noun phrases
- **Types**: Brand titles, content titles, category titles, task titles
- **Examples**: "Account settings", "Your library", "Create new post"

### Buttons and Links

- **Purpose**: Enable users to take action
- **Format**: Active imperative verbs
- **Pattern**: `[Verb] [object]`
- **Examples**: "Save changes", "Delete account", "View details"
- **Avoid**: Generic labels like "OK", "Submit", "Click here"
- **Confirmation dialogs**: the button repeats the consequence, so the dialog is answerable without reading the body — "Delete this project?" pairs with `Delete project` / `Cancel`, never a bare "Yes" and "No" on a consequential action

### Error Messages

- **Purpose**: Explain problem and provide solution
- **Format**: Calm, plain, actionable — zero playfulness, no empathy phrasing
- **Pattern**: `[What failed]. [Why/context]. [What to do].`
- **Never**: technical codes ("Error 403"), blame ("invalid input"), robotic tone, dead ends, or vague causes ("Something went wrong")

Four error types — validation (inline), system (modal/banner), blocking (full-screen), and permission — each with its own pattern, timing, and placement. See references/error-patterns.md for the full breakdown with examples.

### Success Messages

- **Purpose**: Confirm action completion
- **Format**: Past tense, specific, encouraging
- **Pattern**: `[Action] [result/benefit]`
- **Examples**: "Changes saved", "Email sent", "Profile updated"

### Empty States

- **Purpose**: Guide users when content is absent
- **Types**: First-use, user-cleared, error/no results
- **Format**: Explanation + CTA to populate
- **Example**: "No messages yet. Start a conversation to connect with your team."

### Form Fields

- **Labels**: Clear noun phrases describing input ("Email address", "Phone number")
- **Instructions**: Verb-first, explain why information is needed
- **Placeholder**: Use sparingly, only for standard inputs like "name@example.com"
- **Helper text**: Static, on-demand, or automatic based on importance
- **Toggles**: label for the ON state ("Send read receipts", not "Don't send read receipts") — a negative label makes the off state a double negative

### Notifications

- **Purpose**: Deliver timely, valuable information
- **Types**: Action-required (intrusive), Passive (less intrusive)
- **Format**: Verb-first title + contextual description
- **Example**: "Update required. Install the latest version to continue."

## Formatting & Style Conventions

### Capitalization

- **Sentence case** (default): Body text, descriptions, helper text, error messages, success messages, tooltips, placeholder text
- **Native apps**: follow the platform convention instead of sentence case (e.g. Title Case for macOS menus and buttons)
- **Never** use all uppercase — it reduces readability and feels like shouting

### Numbers and Dates

- Use numerals, not words ("12" not "twelve") — saves space and scans faster
- Spell out the month in dates: "August 5, 2025" or "5 August 2025" — never "8/5/2025" or "8.5.2025" (ambiguous across locales)
- Spell out day of the week and month; abbreviate only when space is constrained (e.g., tables, mobile)

### Tense

- Prefer past tense over present perfect for status messages: "File uploaded" not "File has been uploaded"
- Present perfect adds words without adding meaning in most UI contexts

### Abbreviations

- Only use abbreviations your users will immediately understand (common: PDF, URL, ID)
- Spell out on first use if there's any doubt, then abbreviate after: "application programming interface (API)"
- Latin abbreviations (e.g., i.e., etc.) — use proper punctuation: period after each letter, comma before and after in a sentence
- When in doubt, spell it out

## Voice and Tone

### Voice (Consistent Brand Personality)

Voice is the consistent personality of the product. Establish voice using:

- **Concepts**: 3-5 key brand principles/values
- **Voice characteristics**: Descriptive adjectives for each concept
- **Do/Don't examples**: Concrete examples showing voice in action

See references/voice-chart-template.md for creating a voice chart.

Use possessives sparingly ("Favorites" beats "Your Favorites") and hold one perspective throughout a flow.

### Tone (Adaptive to Context)

Tone is how voice adapts to specific situations. While voice remains constant, tone shifts based on the user's purpose, context, emotional state, and the stakes of the action.

Match tone to the user's emotional state (frustrated, confused, confident, cautious, successful) and to the content type (errors, success, instructions, onboarding, confirmations, empty states). See references/tone-adaptation.md for the full matrices with examples.

## Accessibility in UX Writing

Accessible copy works for everyone, including users of assistive technology. Core moves:

- **Screen readers**: label interactive elements explicitly ("Submit application", not "Submit"); write descriptive link text ("Read our privacy policy", not "Click here"); pair errors with their field label.
- **Cognitive load**: short sentences, scannable chunks, consistent and predictable patterns.
- **Don't rely on color alone**: pair visual indicators with text and meet WCAG AA contrast (4.5:1).
- **Plain language**: define technical terms on first use.

See references/accessibility-guidelines.md for the full guide (WCAG mapping, screen-reader behavior, and pattern examples).

## Reporting

When auditing copy (step 3 above), report findings with a fixed scaffold:

- **Severity**: `HIGH` misleads the user or hides how to recover from an error; `MEDIUM` breaks voice, terminology, or capitalization consistency; `LOW` is isolated wording polish.
- **Findings table**: one row per root cause, listing every location it appears in — `Severity | Location | Before | After | Why` (`Location` is `path/to/file:line`; `Why` names the principle and the user impact).
- **Verdict**: `Block` when any `HIGH` finding remains, `Approve` otherwise, leaving the rest in the table as work to do. `Approve` only the coverage you inspected.
- **No findings**: state "No actionable writing findings"; report only real findings.

## Resources

This skill includes:

- **references/error-patterns.md**: The four error message types (validation, system, blocking, permission) with patterns and examples
- **references/tone-adaptation.md**: Tone matrices by user emotional state and by content type
- **references/benchmarks.md**: Length and reading-level targets by content type and audience (the single home for these numbers)
- **references/accessibility-guidelines.md**: Comprehensive guide to writing accessible UX text for all users
- **references/voice-chart-template.md**: Template for creating a product voice chart
- **references/content-usability-checklist.md**: Comprehensive checklist for evaluating UX text quality
- **references/patterns-detailed.md**: Extended examples of UX text patterns in different voices
- **examples/real-world-improvements.md**: Before/after transformations with detailed analysis and scoring
- **templates/error-message-template.md**: Fillable template for writing effective error messages
- **templates/empty-state-template.md**: Guide for creating helpful empty states
- **templates/onboarding-flow-template.md**: Framework for designing clear onboarding experiences
