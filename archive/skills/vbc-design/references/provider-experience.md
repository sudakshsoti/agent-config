# Provider experience

Load this when the user or the persona under discussion sits inside a
practice, provider group, or health system — the other side of every
payer-side workflow.

## Org types and their different tolerances

- **Independent practice.** Thin administrative bench, often no dedicated
  analyst; anything that adds work without an obvious near-term payoff
  gets ignored.
- **MSO/IPA.** Manages shared services (billing, credentialing, sometimes
  VBC contracting) across multiple independent practices; sits between
  practice-level reality and payer-level contracts.
- **FQHC.** Federally qualified health centre; safety-net population, its
  own funding and reporting regime, high SDoH load.
- **Multi-specialty group.** More administrative capacity, more internal
  politics over whose workflow a tool optimises for.
- **Health system / IDN.** Deep IT governance, a real EHR team, long
  procurement cycles, and a strong pull toward "does it live inside Epic"
  as the first question.
- **ACO.** A contracting entity layered over some of the above, whose staff
  may not be the same people delivering care.
- **Home health.** Field-based, connectivity-constrained, different
  visit-and-documentation rhythm entirely.

A workflow designed for a health system's IT-governed rollout will not fit
an independent practice with no analyst, and vice versa. Ask which org type
before assuming administrative or technical capacity.

## Roles — day shape, screen reality

### PCP

Short visit (order of magnitude ten to twenty minutes, verify per setting),
a panel in the low thousands, an EHR in-basket that never empties, and
after-hours documentation ("pajama time") eating into personal time.
Prior-auth burden lands substantially on this role even when a plan employs
staff to help. An intra-visit pop-up almost always fails — it competes with
the patient for the twelve minutes that exist. Design implication: surface
information before or after the visit, inside the EHR workflow the
physician already uses, not as an interruption during it.

### Specialist

Referral-driven; consult notes are the unit of communication back to the
referring provider. Design implication: closing the loop back to the PCP is
itself a workflow, and a broken loop is where care coordination actually
fails.

### Nurse / MA

Handles rooming, pre-visit planning, standing orders, and gap closure at the
point of care — often the role that actually executes a "close this gap"
prompt generated elsewhere. Design implication: point interventions at this
role's workflow, not just the physician's.

### Care coordinator and population-health team

Runs outreach lists, no-show follow-up, and the billable workflows —
Transitional Care Management, Annual Wellness Visit, Chronic Care
Management — that both generate revenue and close gaps simultaneously.
Design implication: an outreach list that doesn't distinguish billable
workflow opportunities from generic reminders leaves money on the table
that would otherwise fund the program.

### Practice manager and revenue-cycle staff

For an FFS practice, this is where the money actually is: denial worklist,
eligibility checks, days in A/R, clearinghouse rejects. Design implication:
a VBC-framed product that ignores this role's FFS-driven daily reality will
read as irrelevant to the practice's actual cash flow, even if the VBC
upside is real.

### Coder and CDI

Chart abstraction, physician query loop, and HCC recapture concentrated
around the Annual Wellness Visit. Design implication: recapture prompts
need to land before or during that specific visit type, not as a generic
year-round reminder.

### Quality lead and ACO analyst

Owns the shared-savings settlement calculation, the benchmark, and
attribution reconciliation — and lives with a long lag before knowing
whether the group actually earned anything. Design implication: a
performance dashboard needs to show progress against benchmark with the
lag made explicit, not present a number as if settlement were final.

### Medical director

Physician buy-in gatekeeper. Will not deploy anything that adds clicks to a
visit, regardless of the analytics case behind it. Design implication: lead
any pitch to this role with interaction cost, not with the dashboard.

## The EHR reality

The EHR market is concentrated among a small number of vendors (order of
magnitude, verify current share before quoting a figure) — knowing which
vendor a health system runs changes what's technically possible.
Distinguish a SMART on FHIR launch (an app that opens inside the EHR's own
context) from a standalone destination the user must separately navigate
to; the former survives adoption, the latter mostly doesn't. Vendor
app-programme politics (certification, marketplace approval, revenue share)
determine whether a SMART on FHIR app is even reachable. Single sign-on and
patient-context passing (the app opening already on the right patient) are
the difference between a tool that gets used and one that doesn't. Reading
data out of an EHR is comparatively easy; writing back into it is hard —
most integration timelines blow up on write-back, not read. CDS Hooks can
surface an alert at the point of decision, but alert fatigue and override
rates are real and well-documented — a poorly targeted alert trains
clinicians to dismiss the next one too. "We send them a list" is not a
workflow: a list with no destination inside the clinician's existing screen
is an extra task, not an integration.

## Provider gotchas

- Attribution lists arrive late and frequently disagree with the practice's
  own sense of its panel — a provider group will dispute a payer's
  attribution the moment it affects their shared-savings number.
- Out-of-network care is invisible to the practice, the same blind spot the
  payer has in reverse.
- The practice holds clinical truth, the payer holds claims truth, and
  neither side has the complete picture of the patient — design for
  reconciling two partial views, not for one authoritative source.
- Small practices typically have no dedicated analyst — a tool that assumes
  someone will interpret a report is assuming capacity that doesn't exist.
- Incentive money (shared savings, quality bonuses) arrives long after the
  work that earned it, which weakens the felt connection between action and
  reward inside the product.
- Scheduling capacity, not information, is usually the real constraint on
  closing a gap — a perfect gap list against a fully booked panel doesn't
  close gaps; it just adds guilt.

## Point-of-care vs. between-visit

Two design surfaces with different rules. Point-of-care: interruption is
expensive, depth must be near-zero, and latency has to be near-instant or
it won't be used inside the visit. Between-visit (outreach lists, portal
messaging, care-coordinator workflows): interruption cost is much lower,
more depth is tolerable, and latency of hours or days is often fine. A
design pattern that works between-visit will usually fail at point-of-care,
and the reverse — over-simplifying a between-visit workflow to match
point-of-care constraints throws away useful depth for no reason.
