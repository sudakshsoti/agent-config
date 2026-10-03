# Formatting and Style Conventions

Read when a string involves capitalization, numbers, dates, tense, or abbreviations.

## Capitalization

- **Sentence case** (default): Body text, descriptions, helper text, error messages, success messages, tooltips, placeholder text
- **Native apps**: follow the platform convention instead of sentence case (e.g. Title Case for macOS menus and buttons)
- **Never** use all uppercase — it reduces readability and feels like shouting

## Numbers and Dates

- Use numerals, not words ("12" not "twelve") — saves space and scans faster
- Spell out the month in dates: "August 5, 2025" or "5 August 2025" — never "8/5/2025" or "8.5.2025" (ambiguous across locales)
- Spell out day of the week and month; abbreviate only when space is constrained (e.g., tables, mobile)

## Tense

- Prefer past tense over present perfect for status messages: "File uploaded" not "File has been uploaded"
- Present perfect adds words without adding meaning in most UI contexts

## Abbreviations

- Only use abbreviations your users will immediately understand (common: PDF, URL, ID)
- Spell out on first use if there's any doubt, then abbreviate after: "application programming interface (API)"
- Latin abbreviations (e.g., i.e., etc.) — use proper punctuation: period after each letter, comma before and after in a sentence
- When in doubt, spell it out
