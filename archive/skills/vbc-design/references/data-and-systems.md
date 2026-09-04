# Data and systems

Load this for anything involving a registry, cohort, integration, or
AI-generated query. This is the file that makes the skill's advice
different from generic UX advice — the operational gotchas live here in
depth (the in-body checklist in `SKILL.md` is the summary).

## Data types and what each can and cannot tell you

- **Claims.** Complete for what was paid, but arrives late (see run-out
  below) — the most reliable source for cost, but never current.
- **Encounter data.** Similar to claims but common in capitated
  arrangements where no fee-for-service claim is generated; can be sparser
  or differently structured than FFS claims.
- **Eligibility and enrolment.** Who is covered, when — spans, not a single
  status; the backbone every other join depends on and the first thing to
  distrust when a number looks wrong.
- **Clinical data via HL7 v2, C-CDA, and FHIR.** Fast relative to claims,
  but partial — only reflects what was documented, in the systems this
  particular integration reaches.
- **Lab results vs. lab orders.** An order doesn't mean a result exists yet
  or that the patient completed the test — don't treat an order as
  evidence of a completed action.
- **Pharmacy claims vs. prescribing and medication possession.** A
  prescription written is not a prescription filled, and a fill is not
  medication actually taken — three different signals with three different
  reliability levels, commonly conflated in a UI as "medication."
- **ADT feeds (Admission/Discharge/Transfer)** for transitions of care —
  high-value, time-sensitive signal for post-acute intervention, and
  timeliness of the feed matters more than for most other data types.
- **SDoH and consumer data.** Often third-party, inferred rather than
  clinically confirmed — treat with appropriately lower confidence than
  claims or clinical data.
- **Provider directory.** Notoriously stale industry-wide; treat directory
  accuracy as an active workflow problem, not a solved lookup.
- **Supplemental care-gap data.** Provider-submitted data used to close
  measure gaps that claims alone would miss (e.g. a vaccination given but
  not billed) — valuable but only as reliable as the submission process
  feeding it.

## Identifiers and the joins that break

Member ID vs. subscriber ID vs. MBI (Medicare Beneficiary Identifier) vs.
MRN (Medical Record Number) — the same person can carry several of these
across systems, with no guaranteed single source of truth linking them all.
NPI (National Provider Identifier) vs. TIN (Tax ID Number) vs. an internal
provider ID — the same physician can bill under multiple TINs depending on
practice affiliation at time of service, which breaks a naive "provider ="
one row" assumption. Member matching across line of business and plan year
is genuinely hard because there's no universal national patient
identifier in the US — identity resolution is itself a workflow with a
false-positive and false-negative rate, not a solved join.

## Time, the biggest lie in healthcare data

Claims run-out and completion factors — a recent month's claims total will
keep growing for months as run-out claims arrive, so a "final" number for
last month is not final. IBNR is the financial expression of this same
lag. Paid date, service date, and incurred date are three different dates
on the same claim and answer three different questions — mixing them up
produces a chart that looks precise and is wrong. Measurement-year close,
retro eligibility, and retro attribution all mean a number that was correct
last week can be wrong this week without anyone having made an error.
Refresh cadence vs. perceived freshness: a dashboard that updates nightly
but doesn't say so reads to the user as always-current, which it isn't.

Design rule: a screen that says "current" without a data-through date will
be wrong in a meeting — every count, rate, or list needs a visible as-of
date and, ideally, a one-line completeness caveat next to it.

## Attribution

Prospective (assigned before the measurement period, based on prior-year
utilisation) vs. retrospective (assigned after the fact, based on the
measurement period itself) — these produce genuinely different member
lists for the same programme and the same time window. Plurality of
primary-care visits is the most common underlying logic (whichever PCP saw
the member most), but geographic assignment and other methods exist and
MA and MSSP differ in their specific rules. Two systems can legitimately
disagree about which patients belong to which provider, because they're
running different attribution logic, not because one is wrong.

Design rule: never show an attributed panel or cohort without stating the
method and the effective date next to it — an unlabelled panel invites a
provider dispute the product has no way to resolve.

## Cohort and registry construction gotchas

Continuous-enrolment gaps silently exclude or include members incorrectly
if the query doesn't explicitly check for them. Exclusions for hospice,
ESRD, and palliative care are measure-specific and easy to miss, producing
a cohort that includes members who should be excluded on clinical or
policy grounds. Deceased flags need to be checked explicitly — a stale
data source can include deceased members in an active outreach list, which
is both operationally embarrassing and emotionally damaging if it reaches
a family member. Denominators must mirror the measure spec exactly (see
`economics-and-incentives.md`). Duplicate members and test members
sitting in production data quietly inflate counts. Cohort drift on refresh
— a saved cohort that re-runs its query on a schedule will change
membership over time, and a user who thinks they're looking at a fixed
list may not realise it drifted. The difference between a saved query
(re-evaluates each time) and a materialised list (frozen at save time) is
a real design decision, not an implementation detail — surface which one
the user is looking at.

## AI and Text-to-SQL specifics

Plain-English intent restatement before showing results — "I understood:
members with diabetes AND HbA1c > 9 AND no PCP visit in 6 months" — lets a
non-technical user validate intent without reading SQL. Treat the
generated SQL as evidence for a technical user to inspect, not as the
primary interface for anyone else. Confidence communication matters more
than a bare answer — a wrong-but-confident-looking cohort is far more
dangerous than an obviously broken one, because nobody double-checks a
plausible answer. Disambiguation is a real design problem: "diabetics"
could resolve to several different value sets depending on which codes are
included, and the system needs to either ask or show its resolution
explicitly. Code-system and value-set provenance — ICD-10, CPT/HCPCS,
SNOMED, RxNorm, NDC, LOINC, and VSAC-sourced value sets — needs to be
traceable, because two "diabetes" cohorts built on different code sets
will produce different member counts and nobody will know why without
provenance. Watch for joins a model reliably gets wrong: date-range logic,
exclusion criteria, and multi-table joins across claims and eligibility are
common failure points. Guard against silent row-level filters — a model
that quietly narrows a "eligible" or "active" filter without surfacing it
produces a plausible-looking wrong cohort, the worst failure mode in this
space. Human validation plus an auditable, re-runnable record of exactly
what query executed is a requirement, not a nice-to-have, given the
downstream stakes of a wrong registry.

## Interoperability plumbing, kept short

Enough to speak credibly and to know which integrations are genuinely
hard, not exhaustive protocol detail: X12 837 (claim), 835 (remittance),
834 (enrolment), 270/271 (eligibility inquiry/response), 276/277 (claim
status), 278 (prior auth) as the EDI backbone still underneath most payer
systems. FHIR R4 resources actually used in this space: Patient, Coverage,
Claim, ExplanationOfBenefit, Encounter, Observation, MeasureReport. Da
Vinci implementation guides define payer-provider FHIR exchange patterns
(e.g. for prior auth and quality reporting) — verify current adoption
status before assuming a specific guide is live in a given integration.
HIE (Health Information Exchange) and the TEFCA direction represent the
industry's push toward broader clinical-data interoperability — worth
knowing the direction of travel even without deep protocol detail.

## Security and access as UI

Role-scoped PHI access and minimum-necessary design shape which fields
appear by default for which role — this is a layout decision, not only an
access-control backend rule. Break-the-glass (emergency override access
with a mandatory justification and audit trail) needs a real UI, not just
a backend permission. Audit logging is itself a user-visible feature in
this domain — a user who knows their access is logged behaves differently,
and a compliance officer needs to review that log through a real
interface. De-identified vs. identified views are a genuine design fork,
not a toggle — different roles may only ever be entitled to one or the
other. CSV export of PHI-containing data is a governance decision with
real consequences, not a convenience feature to add by default.
