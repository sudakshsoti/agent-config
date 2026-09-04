---
name: ux-writing
description: Create user-centered, accessible interface copy (microcopy) for digital products including buttons, labels, error messages, notifications, forms, onboarding, empty states, success messages, and help text. Use when writing or editing any text that appears in apps, websites, or software interfaces, designing conversational flows, establishing voice and tone guidelines, auditing product content for consistency and usability, reviewing UI strings, or improving existing interface copy. Applies UX writing best practices based on four quality standards — purposeful, concise, conversational, and clear. Includes accessibility guidelines, research-backed benchmarks (sentence length, comprehension rates, reading levels), expanded error patterns, tone adaptation frameworks, and comprehensive reference materials.
disable-model-invocation: true
---

# UX Writing

Write clear, concise, user-centered interface copy (UX text/microcopy) for digital products and experiences. This skill provides frameworks, patterns, and best practices for creating text that helps users accomplish their goals.

## When to Use This Skill

Use this skill when:

- Writing interface copy (buttons, labels, titles, messages, forms)
- Editing existing UX text for clarity and effectiveness
- Creating error messages, notifications, or success messages
- Designing conversational flows or onboarding experiences
- Establishing voice and tone for a product
- Auditing product content for consistency and usability

## Core UX Writing Principles

### The Four Quality Standards

Every piece of UX text should be:

1. **Purposeful** — Helps users or the business achieve goals
2. **Concise** — Uses the fewest words possible without losing meaning
3. **Conversational** — Sounds natural and human, not robotic
4. **Clear** — Unambiguous, accurate, and easy to understand

### Key Best Practices

**Conciseness**

- Use 40-60 characters per line maximum
- Every word must have a job
- Break dense text into scannable chunks
- Front-load important information
- Eliminate deadwood phrases ("in order to" → "to", "due to the fact that" → "because", "at this point in time" → "now")
- Replace phrasal verbs with direct verbs ("find out" → "discover", "set up" → "configure", "carry out" → "perform")
- Avoid stacking modifiers — one adjective is usually enough

**Clarity**

- Use plain language (7th grade reading level for general, 10th for professional)
- Avoid jargon, idioms, and technical terms
- Use consistent terminology throughout
- Choose meaningful, specific verbs

**Conversational Tone**

- Write how you speak
- Use active voice 85% of the time
- Include prepositions and articles
- Avoid robotic phrasing

**User-Centered**

- Focus on user benefits, not features
- Anticipate and answer user questions
- Use second-person ("you") language
- Match user's language and mental models

## UX Text Patterns

Apply these common patterns for interface elements.

### Titles

- **Purpose**: Orient users to where they are
- **Format**: Noun phrases, sentence case
- **Types**: Brand titles, content titles, category titles, task titles
- **Examples**: "Account settings", "Your library", "Create new post"

### Buttons and Links

- **Purpose**: Enable users to take action
- **Format**: Active imperative verbs, sentence case
- **Pattern**: `[Verb] [object]`
- **Examples**: "Save changes", "Delete account", "View details"
- **Avoid**: Generic labels like "OK", "Submit", "Click here"

### Error Messages

- **Purpose**: Explain problem and provide solution
- **Format**: Empathetic, clear, actionable
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

### Notifications

- **Purpose**: Deliver timely, valuable information
- **Types**: Action-required (intrusive), Passive (less intrusive)
- **Format**: Verb-first title + contextual description
- **Example**: "Update required. Install the latest version to continue."

## Formatting & Style Conventions

### Capitalization

- **Sentence case** (default): Body text, descriptions, helper text, error messages, success messages, tooltips, placeholder text
- **Title case**: Page titles, modal/dialog titles, menu and navigation items, form field labels
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

### Tone (Adaptive to Context)

Tone is how voice adapts to specific situations. While voice remains constant, tone shifts based on the user's purpose, context, emotional state, and the stakes of the action.

Match tone to the user's emotional state (frustrated, confused, confident, cautious, successful) and to the content type (errors, success, instructions, onboarding, confirmations, empty states). See references/tone-adaptation.md for the full matrices with examples.

## Editing Process

Edit UX text in four phases:

### Phase 1: Purposeful

- Does text help user achieve their goal?
- Does text serve business objectives?
- Is value to user clear?
- Are concerns anticipated and addressed?

### Phase 2: Concise

- Remove unnecessary words
- Combine redundant information
- Ensure every word earns its space
- Front-load important concepts

### Phase 3: Conversational

- Read aloud—would you say this?
- Use active voice (unless passive is clearer)
- Include natural connecting words
- Avoid corporate jargon

### Phase 4: Clear

- Use specific, accurate verbs
- Maintain consistent terminology
- Test readability (Hemingway Editor, Flesch-Kincaid)
- Ensure unambiguous meaning

## Workflow

1. **Understand context**
   - User goals and needs
   - Business objectives
   - Technical constraints
   - Emotional state of user

2. **Draft content**
   - Start with conversation (what would you say?)
   - Apply appropriate pattern
   - Consider voice and tone
   - Front-load important information

3. **Edit iteratively**
   - Phase 1: Purposeful
   - Phase 2: Concise
   - Phase 3: Conversational
   - Phase 4: Clear

4. **Test and measure**
   - Review with team
   - Test with users when possible
   - Measure task completion, comprehension
   - Iterate based on feedback

## Accessibility in UX Writing

Accessible copy works for everyone, including users of assistive technology. Core moves:

- **Screen readers**: label interactive elements explicitly ("Submit application", not "Submit"); write descriptive link text ("Read our privacy policy", not "Click here"); pair errors with their field label.
- **Cognitive load**: 8–14 words per sentence; scannable chunks; consistent, predictable patterns.
- **Don't rely on color alone**: pair visual indicators with text and meet WCAG AA contrast (4.5:1).
- **Plain language**: 7th–8th grade reading level; define technical terms on first use.

See references/accessibility-guidelines.md for the full guide (WCAG mapping, screen-reader behavior, and pattern examples).

## UX Text Benchmarks

Hit research-backed targets for length and reading level — e.g. buttons 2–4 words / 15–25 chars, titles ≤40 chars, errors 12–18 words, lines 40–60 chars, and 8 words = 100% comprehension. General audiences read at a 7th–8th grade level (Flesch-Kincaid). See references/benchmarks.md for the full tables by content type and audience.

## Common Mistakes to Avoid

- Using passive voice excessively
- Generic button labels ("Submit", "OK")
- Blaming users in error messages
- Overly clever humor in serious contexts
- Inconsistent terminology
- Hidden instructions or explanations
- System-oriented language vs. user language
- Too many words (not concise enough)
- Robotic, corporate tone
- Relying on color alone for meaning
- Writing inaccessible link text ("Click here")

## Quick Reference

**Sentence case**: "Save your changes" (not "Save Your Changes")  
**Active imperative for buttons**: "Delete account" (not "Account deletion")  
**User-focused**: "Save time with shortcuts" (not "We offer shortcuts")  
**Specific verbs**: "Delete" (not "Remove" when permanently deleting)  
**Front-loaded**: "Password must be 8 characters" (not "Must be 8 characters for your password")

## Resources

This skill includes:

- **references/error-patterns.md**: The four error message types (validation, system, blocking, permission) with patterns and examples
- **references/tone-adaptation.md**: Tone matrices by user emotional state and by content type
- **references/benchmarks.md**: Research-backed length, comprehension, and reading-level targets
- **references/accessibility-guidelines.md**: Comprehensive guide to writing accessible UX text for all users
- **references/voice-chart-template.md**: Template for creating a product voice chart
- **references/content-usability-checklist.md**: Comprehensive checklist for evaluating UX text quality
- **references/patterns-detailed.md**: Extended examples of UX text patterns in different voices
- **examples/real-world-improvements.md**: Before/after transformations with detailed analysis and scoring
- **templates/error-message-template.md**: Fillable template for writing effective error messages
- **templates/empty-state-template.md**: Guide for creating helpful empty states
- **templates/onboarding-flow-template.md**: Framework for designing clear onboarding experiences
