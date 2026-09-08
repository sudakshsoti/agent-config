# Design intent contract cases

These cases are acceptance fixtures for instruction routing, not live model tests.
Each expected result describes the structure the agent should propose.

## Case: cheatsheet

- Prompt: Create a distinctive personal tmux cheatsheet used several times a day on a 390px phone. Use bold typography.
- Expected class: reference/documentation
- Frequency: several times a day
- Reading mode: scan and act
- Narrowest viewport: 390 x 844 CSS pixels
- First viewport target: filter/navigation and at least one complete shortcut row
- Allowed opening blocks: compact identity, filter, section navigation
- Forbidden defaults: positioning-led hero, eyebrow, display headline, introductory panel, permanent Start here panel
- Typography roles: compact sans or readable UI face for orientation; monospace only for keys, commands, and data

## Case: settings

- Prompt: Design polished account notification settings for weekly use.
- Expected class: settings/form
- Frequency: weekly
- Reading mode: scan and configure
- Narrowest viewport: 390 x 844 CSS pixels
- First viewport target: first setting group and save/status behaviour
- Allowed opening blocks: compact identity and relevant status
- Forbidden defaults: promotional value proposition, positioning-led hero, repeat-use onboarding panel
- Typography roles: compact UI hierarchy; no display face or monospace headings by default

## Case: dashboard

- Prompt: Design a distinctive operations dashboard for analysts monitoring incidents all day.
- Expected class: dashboard/data
- Frequency: all day
- Reading mode: scan and compare
- Narrowest viewport: 390 x 844 CSS pixels
- First viewport target: filters/status and the primary data region
- Allowed opening blocks: compact identity, filters, task-relevant status
- Forbidden defaults: display headline, positioning-led marketing hero, decorative intro panel
- Typography roles: compact UI hierarchy; tabular or technical data treatment where alignment helps

## Case: landing page

- Prompt: Design a product landing page for an incident-response tool.
- Expected class: marketing/brand
- Frequency: occasional discovery
- Reading mode: read and decide
- Narrowest viewport: 390 x 844 CSS pixels
- First viewport target: positioning and primary conversion action
- Allowed opening blocks: hero when it advances positioning, supporting proof, primary action
- Forbidden defaults: none of the non-marketing restrictions apply; the hero is still a choice, not a requirement
- Typography roles: display type is permitted when it serves positioning; body and action roles remain readable
