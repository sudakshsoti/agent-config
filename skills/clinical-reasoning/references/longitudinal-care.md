
# 16. Longitudinal and Chronic Care

Section 16 of the Clinical Reasoning Framework. §1-13 and §15 are in
[`clinical-framework.md`](clinical-framework.md); §14 (mental health) in
[`mental-health.md`](mental-health.md).

Acute reasoning asks "what is this?". Chronic reasoning asks "is this at target,
who owns it, and when is it next checked?". A chronic review that returns no date
and no owner has not happened.

## 16.1 The Planned Visit

A reactive visit answers whatever the patient raises. A planned visit works a
list built before the patient arrives — the operational core of the Chronic Care
Model, and the difference between care that compounds and care that drifts.

Before the encounter: pull last values and their dates, compute what is overdue
(§2.4 lab gap flagging, §7 staleness), and set the agenda. During: run the target
check below, then the patient's own agenda. After: one named next action, one
owner, one date.

## 16.2 Treat-to-Target Reference

Indian guidance where it exists, international where it does not. Targets are
starting positions to individualise, not thresholds to enforce.

| Condition | Target | Review interval |
|---|---|---|
| Type 2 diabetes | HbA1c <7.0% most adults; <7.5% older with comorbidity; 8.0-8.5% in frailty or limited life expectancy (ADA 2025; RSSDI concurs) | 3-monthly until at target, then 6-monthly |
| Diabetes — renal | eGFR + urine ACR at least annually; 3-6 monthly if at risk | per KDIGO risk cell below |
| Hypertension | Diagnose ≥140/90 office, ≥135/85 home mean. India MoHFW STG target <140/90 (<80y); ~150 systolic acceptable ≥80y. ESC 2024 pushes 120-129 systolic where tolerated | Monthly until controlled, then 3-6 monthly |
| Lipids (LAI, India) | LDL-C <100 low/moderate risk, <70 high, <50 very high (established ASCVD, diabetes with target-organ damage, LDL ≥190, premature disease). Non-HDL = LDL + 30 | 6-12 weeks after any change, then 6-12 monthly |
| CKD (KDIGO 2024) | Slow progression; treat ACR, not just eGFR. Heat map G1-G5 × A1 (<30) / A2 (30-300) / A3 (>300 mg/g) | Low risk 1×/yr, moderate 2×, high 3×, very high ≥4×/yr (eGFR + ACR together) |
| Heart failure | All four pillars at target dose (ACEi/ARB/ARNI, beta-blocker, MRA, SGLT2i) | 4-6 weeks after each titration, then 3-6 monthly |
| Hypothyroidism | TSH in range for age and indication | 6-8 weeks after any dose change; 12-monthly when stable; 4-weekly in pregnancy |
| Asthma / COPD | Control, not just symptom absence: exacerbations, reliever use, inhaler technique, adherence, triggers (GINA 2025) | 3-6 monthly; sooner after a step change |

South Asian risk adjustment applies throughout — multiply ASCVD risk by 1.2-1.5×
(§8) and treat the stricter LDL tier as the default, not the exception. LAI's
<50 mg/dL for very-high risk is deliberately stricter than ESC's <55 for this
reason.

**ESC 2024's 120-129 systolic target is the live disagreement**: NICE, ISH and the
Indian STG still anchor at <140/90. Offer it as a target with an explicit opt-out
for frailty, age ≥85 or intolerance — not as a number to chase in an 82-year-old.

## 16.3 The Periodic Review

Structure adapted from the Year of Care care-planning model: assessment first,
then a jointly agreed plan, not a tick-box.

1. **Medication reconciliation** — everything actually taken, including OTC, Ayurvedic and supplements (§4.4), against everything prescribed
2. **Targets** — each condition against §16.2, with the trend, not just the latest value (§2.2)
3. **Lab and screening gaps** — overdue investigations with dates (§2.4), immunisations, age-appropriate cancer screening
4. **Function** — what they can and cannot do now that they could a year ago
5. **Mood and cognition** — PHQ-2 and, where indicated, GDS-15 or HMSE (§14.2)
6. **Deprescribing** — at 5+ medications run §10.4; at 10+ treat it as the main agenda item
7. **Caregiver** — who is doing the work, and what it is costing them (Zarit ZBI-4 ≥6, ZBI-12 >20 warrants attention)
8. **Goals** — what matters to the patient this year, in their words
9. **Plan** — each action with an owner and a date

## 16.4 Adherence

Assume imperfect adherence and ask in a way that makes the truth easy:

> "Most people miss doses. In the last two weeks, how many days did you miss
> yours?"

Then triangulate: refill gaps (the pharmacy bill or strip count tells the truth
the answer may not), pill count, and timing errors as distinct from missed doses.
Avoid the Morisky scales — licence-encumbered and no better than the probe.

**Always ask the cost question directly**: "Did cost make you skip or stretch any
of these?" Out-of-pocket spending is ~43% of Indian health expenditure and drugs
are roughly 70% of outpatient out-of-pocket cost — non-adherence in an Indian
clinic is a pricing failure at least as often as a motivation failure. Check
PM-JAY, CGHS or employer coverage before escalating a regimen; switch to a
government-lab investigation or a lower-cost brand (§12) before assuming
non-compliance.

What actually works, once cost is excluded: simplify the regimen, fix the timing
to an existing daily anchor, use combination products where sensible, and involve
whoever in the household manages the medicines.

## 16.5 Older Adults — the 4Ms

For every patient 65+, alongside the geriatric safety protocol (§10):

- **What Matters** — their stated outcome goal, which is often function or independence, not a number
- **Medication** — age-friendly regimen, anticholinergic burden (§10.1), deprescribing (§10.4)
- **Mentation** — delirium (4AT, §14.8.2), dementia (HMSE), depression (GDS-15)
- **Mobility** — falls risk (§10.2), gait, and what the home actually looks like

## 16.6 Transitions and Ownership

Most chronic-care failures happen in the gaps between clinicians, not inside a
consultation.

- Reconcile medications at every transition — admission, discharge, first contact after. Discharge summaries routinely drop chronic medications and add temporary ones without stop dates.
- Reconciliation alone does not reduce readmissions; the bundle does — reconciliation plus explicit patient education plus contact within 7 days.
- Every problem on the list needs a named owner: which clinician is managing it, and when they next see the patient. "Under the cardiologist" without a date is not ownership.
- Specialists change drugs the GP will have to monitor. Whoever writes the prescription owns the calendar (§14.10 for psychotropics, §4.5 for renal/hepatic).

## 16.7 Function as an Outcome

Symptom control without functional gain is a partial result. Keep one measure in
the notes so the trend is visible:

- **WHODAS-12** (0-48, difficulty over the past 30 days) — generic, works by text or phone
- **Katz ADL** (6 items) and **Lawton IADL** (8 items) — binary, best for elderly and post-hospital patients
- **WSAS** (0-40) — work and social adjustment, the natural pair for mental health (§14.9.1)

Record it at baseline and at each periodic review. A patient whose HbA1c improved
and whose IADL score fell has not improved.
