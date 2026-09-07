# Licence scope

What a type licence actually grants is a narrower question than what it appears to grant, and the appearance is where mistakes get made.

## The scope questions

- **A desktop licence does not permit web serving.** A licence bought for use inside a design tool or a print workflow is a different grant from a web-font licence, even from the same foundry for the same family; using the desktop-licensed files as `@font-face` sources is outside that grant regardless of how the files were obtained.
- **Basic authentication is still web serving.** A font served from behind a login wall, an internal VPN, or HTTP basic auth is still delivered over the web to a browser, and a "desktop only" or "internal use" reading of that delivery does not hold — the licence terms for web serving apply to any font requested by a browser over HTTP, authenticated or not.
- **Web licences are commonly priced or scoped by pageview or by domain**, not granted as a flat one-time purchase the way a desktop licence often is. The grant that applies is the one actually purchased for the domain and traffic in question, not the cheapest tier that exists for the family.

## What counts as evidence

The licence text and the foundry's own licensing documentation are the only admissible evidence for what is permitted. A marketplace listing, a cached pricing page, or a summary written by someone other than the foundry can be stale or wrong; a licence claim carries the date it was read, because pricing and terms pages change.

Where no web licence is in place for a face under consideration, name the licence that would be needed and its cost rather than silently substituting a different, already-licensed face — the substitution is a decision for whoever owns the budget, not a default an agent makes unasked.

## Sources

- `archive/skills/typography-craft/SKILL.md` @ `201bd7ed9072269c1081a0e4d2315868b84649e4`.

## Gotcha

Agents cite a marketplace listing or a cached price page as licence evidence — the grant lives in the licence text and the foundry's own documentation, and a marketplace or pricing page can be a year stale or describe a different tier than the one actually purchased.
