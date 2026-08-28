# Economics and incentives

Load this to locate the deal — who bears risk, what programme governs, and
why a proposal is or isn't fundable. Deepens the payment and policy material
that used to live inside design-foil before the healthcare split.

## Payment spectrum

For each point on the spectrum: who holds the money, what the actor
optimises for, and what the software must therefore show.

- **Fee-for-service (FFS).** Provider paid per service; optimises for
  volume and coding completeness. Software must make billing-complete
  documentation easy, because incomplete coding is lost revenue today, not
  a future risk.
- **Pay-for-performance (P4P).** FFS plus a quality bonus layer; optimises
  for hitting measure thresholds on top of volume. Software must connect a
  specific action to a specific measure's numerator.
- **One-sided shared savings.** Provider gets upside if costs come in under
  benchmark, no downside if they don't; optimises cautiously for cost
  reduction without real risk tolerance. Software must show progress
  against benchmark without implying certainty.
- **Two-sided shared savings.** Real downside risk now exists; optimises
  aggressively for cost and utilisation management, because a bad year
  costs the group money. Software needs to support proactive intervention,
  not retrospective reporting only.
- **Bundles / episodes.** A fixed payment for an episode of care (e.g. a hip
  replacement, 90 days); optimises for controlling everything inside that
  episode window, especially post-acute cost. Software must be
  episode-scoped, not population-scoped.
- **Capitation.** A fixed per-member-per-month payment regardless of
  utilisation; optimises for keeping the population healthy and out of
  expensive care, because every avoidable visit is pure cost. This is the
  economic logic that makes population-health software valuable in the
  first place — capitation is why "prevent" beats "treat" financially, not
  just clinically.
- **Global risk / direct contracting.** Full financial responsibility for a
  population's total cost of care; optimises like an insurer, not a
  provider. Software must support the full population-health stack:
  identify, stratify, intervene, measure.

## Programme specifics

- **Medicare Advantage.** Plans submit an annual bid; CMS pays a
  risk-adjusted capitated rate plus rebate dollars tied to Star Rating.
  Star Ratings are directly a revenue lever, not just a quality label — a
  half-Star movement carries real dollar magnitude at the book-of-business
  level (verify current figures before quoting).
- **MSSP and ACO REACH.** Shared-savings programmes against a calculated
  benchmark and a minimum savings rate threshold before any payout occurs;
  settlement happens on a real lag (often well over a year from
  performance-period start), which is why an ACO analyst lives with
  prolonged uncertainty about whether the group earned anything.
- **Medicaid managed care.** Governed by a state contract, often with a
  withhold (a portion of payment held back, released against quality
  performance) and a quality pool. State-specific measure sets and rules
  mean this is the line of business least tolerant of a single national
  workflow.
- **Commercial.** ASO (employer bears risk, plan is administrator) vs.
  fully insured (plan bears risk) changes who the real economic buyer is.
  Stop-loss insurance caps an employer's downside in ASO arrangements —
  relevant context for who ultimately cares about cost outcomes.

## Risk adjustment

HCC (Hierarchical Condition Category) is the Medicare risk-adjustment model,
currently transitioning through model versions (v24 toward v28 — verify
current CMS phase-in status before asserting a specific version is live).
CDPS covers Medicaid, HHS-HCC covers commercial risk-adjustment transfers.
The core mechanic: a member's RAF (risk adjustment factor) score, built from
diagnosis-driven HCC coefficients, sets a payment level for that member —
which is why "recapture" (re-documenting a chronic condition every calendar
year, since HCCs generally don't carry forward) is a recurring, high-stakes
workflow. RADV (Risk Adjustment Data Validation) audits can claw back
payment when a coded HCC lacks supporting documentation.

Design implication: a suspecting workflow (surfacing likely-undocumented
HCCs to a coder or physician) needs provenance and a defensible audit trail
on every suggestion — this is the line between legitimate documentation
improvement and an upcoding exposure, and the product sits directly on that
line.

## Quality

HEDIS measure anatomy: denominator (the eligible population), numerator
(who met the criteria), exclusions (who's carved out despite meeting
denominator criteria), and a continuous-enrolment requirement that trips up
naive registry logic. Administrative measures pull from claims alone;
hybrid measures require chart chase on top of claims; the ECDS
(Electronic Clinical Data Systems) reporting path is the industry's
direction of travel toward more automated, clinical-data-sourced
measurement — verify current NCQA timelines before asserting adoption
status. Star Rating weighting assigns different point values to different
measure categories and applies cut points that shift periodically — verify
current weights and cuts before quoting one. CAHPS (member experience
survey) and HOS (Health Outcomes Survey) feed into Star Ratings alongside
clinical measures. Measurement year (the calendar year being measured) and
reporting year (when results are submitted and published) are not the same
year, and confusing them in a UI produces confidently wrong dates.

Design implication: registry logic must mirror measure logic exactly — the
same denominator population, the same exclusions, the same continuous
enrolment window — or the product's own numbers will not tie to the
official rate, and that single reconciliation failure destroys the
product's credibility with the one audience (the quality/HEDIS analyst)
most equipped to notice it.

## Financial vocabulary that decides funding

- **TCOC (Total Cost of Care).** The north-star metric for value-based
  arrangements; every intervention needs a plausible TCOC story to survive
  a funding conversation.
- **PMPM (Per Member Per Month).** The standard cost-normalisation unit;
  lets costs be compared across populations of different sizes.
- **MLR (Medical Loss Ratio).** The share of premium spent on care versus
  administration/profit; regulated minimums exist, and MLR pressure shapes
  what a plan will fund.
- **IBNR (Incurred But Not Reported).** Claims for care that happened but
  haven't been submitted/paid yet — a real financial liability that isn't
  visible in raw claims data, and the reason claims data always looks
  artificially low for recent months.
- **Run-out.** The tail of claims that keeps arriving for months after a
  service date; a "final" number for a recent period isn't final.
- **Trend.** The expected year-over-year cost growth rate; used to project
  and to judge whether an intervention actually bent the curve.

Design implication: a savings claim needs a stated comparison population
plus an explicit attribution and lag method, or a CFO discards it on sight
— "we saved $X" without those two things is not a claim a finance audience
can act on.

## Order-of-magnitude stakes

A meaningful Star Rating movement or a material RAF shift carries real
dollar consequences at scale for a large plan — treat any specific figure
here as something to verify by search before quoting to a stakeholder, not
as a fact to state from memory.

## Regulatory pressure and its design consequences

Interoperability and API rules (CMS interoperability mandates, patient
access APIs), prior-auth reform direction (electronic prior auth, faster
decision timeframes), price transparency requirements, information-blocking
rules under the 21st Century Cures Act, state Medicaid variation, HIPAA
minimum-necessary standard, 42 CFR Part 2 (extra protection for
substance-use treatment records, stricter than general HIPAA), and
state-specific consent regimes for behavioural health and other sensitive
categories. Design implication: PHI segmentation — what a given role can
see, by data category — is a layout and defaults constraint that has to be
designed in from the start, not a compliance checkbox bolted on afterward.

## Durable vs. churn-prone

| Durable | Churn-prone |
|---|---|
| How risk transfers between payer and provider | Specific Star cut points and category weights |
| Why capitation creates population-health logic | HCC model version and coefficients |
| How a quality measure is constructed (denominator/numerator/exclusion) | Specific measure specifications and value sets |
| How claims lag and run-out work structurally | Current rate notices and benchmarks |
| Why attribution requires a method and effective date | Prior-auth and interoperability rule effective dates |
| The shape of the payment spectrum | State Medicaid contract terms |
