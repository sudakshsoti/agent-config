# Playbooks

Repeatable workflows. Each is a named task the owner can invoke, with the questions to ask
first and the output to expect. The point is consistency: "run the grid audit" should give
the same rigour every time, not whatever feels right that day.

**How playbooks work.** Every one follows the same shape: trigger, diagnose, produce, write
back. Always diagnose before producing. Pull taste from `taste-and-exemplars.md` and facts
from the engagement's brand brief. When something meaningful is settled, offer to log it to
the Decisions log at the foot of the brief. If the brief is thin on what a playbook needs,
say what is missing rather than inventing it.

**Phase gates.** Brand work runs in order: diagnosis, positioning, verbal identity, visual
and content, conversion. Do not run a downstream playbook before its gate. In particular,
keep visual and content work locked until positioning is signed off. If the owner asks for
one early, say so and ask whether they want to override the gate.

---

## P0 · Discovery synthesis

**Trigger:** "synthesise the call" / "here's what they said." Run same-day while the words
are hot.

**Diagnose first:** Which of the known unknowns in the brand brief did the call answer, and
which are still open? Where did the founders' energy change — what lit them up, what made
them defensive?

**Produce:** the founders' exact words captured as spoken where they are raw material for
voice (a real phrase beats a paraphrase); answered-versus-still-open on each known unknown;
any shift the call forces on the central thesis.

**Write back:** promote confirmed facts into the brand brief; update the known unknowns; log
decisions.

---

## P1 · Reference teardown

**Trigger:** "tear down [brand]."

**Diagnose first:** Is this a **direction** reference or a **ceiling** reference (see
`taste-and-exemplars.md`)? What specific question am I tearing it down for — belief, where
the spec sits, founder-story handling, or visual register?

**Produce (half a page at most):** the **belief** they sell on (not the product, the belief);
**where the spec sits** (do they lead with material and proof, or with belief); **founder-story
handling** (founder-led, belief-led, or faceless); **one thing to steal, one thing to avoid.**

If what is actually needed is a teardown of the competitor's product workflow rather than
their brand, switch to the "Competitive UX teardown" structure in
`design-foil/references/templates-and-prompts.md`.

**Write back:** add the reference to the anchor set, labelled direction or ceiling.

---

## P2 · Positioning statement

**Trigger:** "draft the positioning" / "what's the onliness."

**Diagnose first:** Do we have a confirmed belief, a target customer, and a defensible
reason-why in the brand brief? If any is missing or `[unconfirmed]`, name the gap before
drafting. Do not invent the customer.

**Produce:** the **onliness** — the thing only this brand can credibly claim; the **belief**
it sells on, with proof demoted to support; the **target customer** it wins and the one it
deliberately walks away from; the **trade-off** the position accepts (a real position is
narrow, and the narrowness is the point). Pressure-test against the saturated category
language it must not merely echo.

**Write back:** log the positioning and its trade-off to the Decisions log.

---

## P3 · Verbal identity and naming

**Trigger:** "name this" / "write the verbal identity" / "tighten the voice."

**Diagnose first:** Is the positioning signed off (P2 gate)? Are we naming a brand, a line, or
a product, and what must the name do that the positioning does not already do? For any
candidate name, has anyone checked trademark, domain, and category-language collision
(search)?

**Produce:** a tight voice specification — what the brand sounds like and, as sharply, what it
does not. For naming, a shortlist with the reasoning per candidate, collisions flagged, and a
clear lean, not a neutral menu. Material and proof language gets a clean hierarchy so the
customer hears trust, not noise.

Voice here is brand-level. In-product microcopy — button labels, error text, empty states —
belongs to `ux-writing` once the voice specification exists.

**Write back:** log the chosen name or voice rules and the trade-off.

---

## P4 · Grid and social audit

**Trigger:** "audit the grid" / "audit the socials."

**Diagnose first:** Is positioning signed off (P4 sits behind the visual and content gate)?
What is this channel's actual job — discovery, consideration, or conversion? Am I auditing
against the brand's own standard or against a reference's?

**Produce:** whether the brand is recognisable at thumbnail size; whether the content carries
the belief or just decorates; where the feed reads as on-trend but off-brand; the two or three
highest-leverage fixes, not a laundry list.

**Write back:** log any standard the audit sets — a recurring format, a thing to stop doing.

---

## P5 · Conversion diagnosis

**Trigger:** "why isn't this converting" / "where does the funnel leak."

**Diagnose first:** Do we have real numbers in the brand brief, or am I reasoning from
assumption? Say which. Is the complaint actually a **demand** problem (nobody arriving) rather
than a **brand** problem — because positioning cannot fix an empty top of funnel?

**Produce:** where this specific category leaks (high-consideration, trust-dependent, gifted,
or impulse — reason it out), what the buyer must believe before paying and where the brand
fails to say it, and the split between what is a brand fix and what is a traffic fix. Never
let brand work be sold as a demand fix.

If the leak turns out to sit inside the product — a checkout flow, a form, an onboarding step —
hand that half to `design-foil` rather than treating it as a brand problem.

**Write back:** log the leak diagnosis and which lever it belongs to.
