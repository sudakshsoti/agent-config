# Payer experience

Load this when the user or the persona under discussion sits inside a health
plan — UM, care management, quality, risk, claims, network, actuarial, or
member services.

## Lines of business, and why they change everything

A health plan is not one product. Each line of business carries a different
regulatory regime, measure set, member tenure, and even what you're allowed
to say to a member:

- **Commercial group and individual.** Employer-sponsored or marketplace,
  younger and more transient membership, less regulatory density than
  government lines.
- **ASO vs. fully insured.** Administrative-services-only means the employer
  bears the risk and the plan is a vendor; fully insured means the plan bears
  it. This changes who the real buyer is and what "success" means to them.
- **Medicare Advantage.** Star Ratings drive revenue directly through
  quality bonus payments; heavy CMS marketing and communication rules
  constrain member-facing copy.
- **D-SNP (Dual-Eligible Special Needs Plans).** Medicare and Medicaid
  overlap, higher acuity, integrated care requirements.
- **Medicaid managed care.** State-contracted, state-specific measure sets
  and reporting, member churn tied to eligibility redetermination cycles.
- **Marketplace.** ACA-regulated, risk-adjustment transfers between issuers,
  annual open-enrolment churn.
- **Med Supp.** Older, low-churn membership, thin product surface.

A workflow or dashboard built for MA Stars logic will misfire if pointed at a
Medicaid population with a different measure set and a different
redetermination clock. Ask which line of business before assuming any of
this transfers.

## Roles — day shape, queue, metrics, what they hate

### UM nurse / prior-auth reviewer

Queue-driven work against a clock. Standard vs. expedited turnaround
requirements dictate literal minutes of allowable delay, not a soft SLA.
Works through criteria screens (InterQual/MCG-style logic), escalates
ambiguous cases to a medical director, and the outcome triggers a
member/provider letter with regulated content. What they hate: a UI that
buries the clock, forces re-entry of clinical detail already in the
request, or hides which criteria line actually failed. Design implication:
the turnaround countdown and the escalation path are primary UI, not a
footnote.

### Care manager

A caseload (order-of-magnitude tens to low hundreds of members, verify per
programme), mostly telephonic in practice however the product markets
itself. Real day: dialing unreachable members, documenting a care plan
against a required assessment instrument, tracking consent, and reconciling
time-on-phone against time-in-system. What they hate: documentation UI that
takes longer than the call itself, or a system that can't represent "tried,
no answer, will retry" without a full workflow detour. Design implication:
the fastest path is the default path; a five-minute call should not require
fifteen minutes of data entry.

### Quality / HEDIS analyst

Runs the annual hybrid measurement cycle: chart chase for hybrid measures,
supplemental-data ingestion, submission against a hard NCQA/CMS deadline.
Lives inside measurement year vs. reporting year confusion daily and
produces provider-facing gap reports that other roles consume. What they
hate: a registry or dashboard whose denominator logic doesn't match the
actual measure specification — it means their number won't reconcile with
the official rate, and they own that discrepancy in the audit. Design
implication: show the measure version and the as-of date next to every rate.

### Risk-adjustment and coding operations

Runs retrieval (chart pulls), suspecting (finding likely-undocumented HCCs),
and sweeps against a compliance line that separates legitimate documentation
improvement from upcoding — RADV audit exposure sits behind every suspect
list. Sends provider queries and tracks their resolution. What they hate: a
suspect list with no evidence trail, because it's indistinguishable from a
mandate to code more aggressively. Design implication: every suspected HCC
needs a visible clinical-evidence citation, not just a code and a dollar
estimate.

### Claims examiner and appeals/grievances

Pend-deny-adjust workflow against regulated appeal levels and timeframes.
Denial reason codes and member notice language are themselves regulated —
this is where `ux-writing` involvement matters. What they hate: ambiguous
denial reasons that generate a predictable wave of appeals. Design
implication: the reason code and the appeal path belong on the same screen
as the denial, not behind a separate lookup.

### Network and provider relations

Manages fee schedules, VBC contract terms, attribution disputes (a provider
group disputing which members are attributed to them, because attribution
drives their shared-savings calculation), regulated directory-accuracy
requirements, and provider-facing reporting packets. What they hate:
directory or attribution data that's stale enough to trigger a compliance
finding or a contract dispute. Design implication: attribution disputes are
a workflow, not an edge case — design the correction path, not just the
display.

### Actuarial, finance, and Stars leadership

Owns MLR, IBNR, the annual bid cycle, and Star-revenue modelling — thinks in
terms of leverage: what a half-Star movement or an RAF shift is worth to the
book of business (order of magnitude, verify current figures before
quoting). What they hate: any number that can't be traced back to the book
of record — a dashboard figure gets ignored the moment it can't reconcile.
Design implication: every executive-facing number needs a stated source and
lag.

### Member services rep

Works three systems open simultaneously — eligibility, claims, and a CRM or
case system — under after-call-work and average-handle-time pressure. What
they hate: a fourth system. Design implication: embed, don't add a login;
see gotcha (j) in the main skill.

## Payer gotchas

- Rosters churn monthly and retro-terminate — a member active last week can
  be retroactively removed this week, and any list built on a snapshot will
  disagree with the system of record.
- Eligibility spans, not a single status flag — a member can have gaps and
  multiple concurrent spans across products.
- Member IDs are not stable across line of business or plan year; the same
  person can show up as multiple IDs.
- PBM (pharmacy benefit manager) data often lives in a separate system
  entirely, so pharmacy claims may lag or be absent from the plan's own
  data.
- Behavioural-health carve-outs mean a subcontracted vendor, not the plan
  itself, holds part of the clinical picture.
- Delegated entities (delegated UM, delegated claims) own part of the
  workflow the plan's own product may assume it owns.
- State-by-state Medicaid variation means a single national workflow is
  often wrong somewhere.
- CMS marketing and communication rules constrain what member-facing copy
  can say, especially for MA — route wording decisions through
  `ux-writing` with this constraint stated explicitly.
- The plan cannot see care it didn't pay for — out-of-network or
  cash-pay care is a blind spot baked into the data, not a bug.

## What payers buy and why

ROI gets framed in Star movement, risk-accuracy improvement, or MLR impact —
translate any product pitch into one of these or it won't survive a
budget conversation. Security review is a real gate, not a formality, given
PHI exposure. The typical adoption path is pilot inside one line of business
or market before enterprise rollout — design for that path rather than
assuming day-one universal deployment. And the "why one more login kills
adoption" pattern is not a platitude here: a plan employee already has
several mandatory systems open, and anything that isn't embedded loses to
whatever's already on screen.
