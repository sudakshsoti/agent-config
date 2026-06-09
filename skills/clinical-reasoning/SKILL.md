---
name: clinical-reasoning
description: |
  Structured clinical decision-making framework for health-related queries. Trigger
  when the user discusses symptoms, lab results, medications, drug interactions,
  red flags, treatment plans, medication tapers, pediatric escalation, postpartum
  surveillance, or any medical reasoning. Provides standardised protocols for
  differential diagnosis, drug interaction checking, lab interpretation, red flag
  escalation, and temporal medication tracking. Indian healthcare context: local
  brands, ICMR/IAP/FOGSI guidelines, cost-awareness, vegetarian dietary sources.
  User has MBBS-level medical literacy — no disclaimers, no hedging, direct
  clinical language.
---

# Clinical Reasoning Framework

User has first-year MBBS knowledge and works in healthcare (UX, value-based care). No disclaimers ("consult your doctor"), no hedging, no dumbing down. Use clinical terminology directly. Reference Indian guidelines, brands, and availability.

## 1. Diagnostic Reasoning Protocol

Follow these steps for any clinical presentation. Skip steps that don't apply, but never skip Safety Checks.

**Step 1 — Information Gathering**
Review all provided information: symptoms, duration, severity, progression, labs, imaging. Identify missing critical information. Flag red flags immediately (see Section 3).

**Step 2 — Clinical Reasoning**
List differential diagnoses, most likely first. Explain reasoning for each. Consider demographics, risk factors, presentation patterns, seasonal context (dengue Jul-Nov, AQI respiratory Nov-Feb NCR, heat illness Apr-Jun).

**Step 3 — Diagnostic Workup**
Suggest investigations. Prioritise by: urgency, availability in India, cost-effectiveness. Explain what each test confirms or rules out. Reference Indian lab chains when relevant (Thyrocare, SRL, Dr. Lal PathLabs).

**Step 4 — Treatment Plan**
Evidence-based recommendations using Indian guidelines first (ICMR, AIIMS protocols, IAP for pediatric, FOGSI for obstetric/gynae, API for internal medicine, RNTCP for TB, NVBDCP for vector-borne). Prescribe using: Generic name (Indian brand examples), dose, frequency, duration, route. Consider cost and patient compliance.

**Step 5 — Safety Checks (never skip)**
Run the Drug Interaction Protocol (Section 4). List contraindications. Highlight monitoring requirements. Provide warning signs requiring immediate attention.

**Step 6 — Patient Education Points**
Lifestyle modifications. Follow-up timing. Expected treatment timeline. Warning signs to watch for.

## 2. Lab Interpretation Framework

### Severity Grading

Use consistently across all lab parameters:
- **Normal**: within reference range, no action
- **Watch**: borderline or trending toward abnormal, retest at next scheduled visit
- **Flag**: outside reference range, warrants clinical attention or workup change
- **Critical**: requires urgent action (same-day clinic or ER)

### Trend Analysis

When 3+ data points exist, calculate slope:
- Direction: improving / worsening / static
- Rate of change per unit time (e.g., eGFR mL/min/year, Hb g/dL per quarter, HbA1c % per 3 months)
- Compare against expected trajectory (age-related, disease-related, medication-related)
- Correlate changes with medication starts/stops, weight milestones, seasonal factors

Flag slow declines even if still in range (e.g., eGFR dropping >3 mL/min/year, Hb dropping 0.5 g/dL per quarter).

### Risk Scoring (when data available)

**HOMA-IR** (insulin resistance):
(Fasting Insulin µU/mL × Fasting Glucose mg/dL) / 405
<2.0 normal | 2.0–2.9 borderline | >3.0 significant IR

**FIB-4** (liver fibrosis, for NAFLD):
(Age × AST) / (Platelet count × √ALT)
<1.30 low risk (F0-F1) | 1.30–2.67 indeterminate | >2.67 advanced fibrosis likely

**ASCVD 10-Year Risk**: Apply 1.2–1.5× multiplier for South Asian ancestry. Standard Framingham inputs: age, TC, HDL, SBP, smoking, diabetes.

### Lab Gap Flagging

Cross-reference against clinical milestones and current date. Flag overdue investigations:
- Format: "Last [parameter]: [value] ([date]) → [N months overdue] — [clinical reason recheck needed]"
- Prioritise: HIGH (affects active treatment decisions), CRITICAL (surveillance gap for known pathology)

## 3. Red Flag Escalation Protocol

### Routing

**Home care**: mild symptoms, manageable with OTC, no red flags
**Clinic (same-day)**: moderate symptoms, stable but needs assessment
**ER (immediate)**: any red flag below, unstable vitals, altered consciousness

Gurugram facilities: Medanta, Artemis, Fortis Memorial Research Institute.

### Universal Red Flags (any patient) → ER

- Chest pain/pressure with radiation (jaw, arm, back) or diaphoresis → ACS protocol
- Syncope or presyncope with known conduction defect → cardiology/ER
- Dark/tarry stools or haematemesis → GI bleed, especially on antiplatelet/SSRI/NSAID
- Severe hypoglycaemia: confusion, tremor, LOC → glucose/glucagon → ER
- Hyperkalaemia symptoms: muscle weakness, palpitations, paraesthesias → ER for ECG + K+
- Euglycaemic DKA (on SGLT2i): illness + vomiting + normal glucose but ketotic → STOP SGLT2i → ER
- Anaphylaxis: airway compromise, widespread urticaria, haemodynamic instability → epi + ER
- Stroke signs: sudden focal neurological deficit → ER within golden hour

### Pediatric Red Flags (infants/toddlers) → ER

- Fever >39.2°C (102.5°F)
- <3 wet diapers in 24 hours (dehydration)
- Lethargy + fever
- Dry mucous membranes + sunken fontanelle
- Persistent vomiting >6 hours or inability to keep fluids down
- Bloody stools + fever
- Seizure (febrile or afebrile)
- Bulging fontanelle

### Pediatric Fever Escalation Ladder

- <38°C (100.4°F): Monitor at home, hydration, cool compress
- 38–38.5°C (100.4–101.3°F): Paracetamol drops (Crocin/Dolo), humidifier, observe 24h
- 38.5–39.2°C (101.3–102.5°F): Urgent clinic visit, not ER unless red flags present
- >39.2°C (102.5°F): Immediate ER

### Postpartum/Obstetric Red Flags → ER

- Heavy vaginal bleeding (soaking >1 pad/hour)
- Fever >38°C with uterine tenderness (endometritis)
- Sudden severe headache + visual changes (eclampsia)
- Calf pain/swelling (DVT risk elevated postpartum)
- Suicidal ideation or thoughts of harming infant → psychiatric emergency
- Incisional hernia: irreducible, painful, skin colour change → surgical ER

### Endometriosis-Specific Red Flags

- Acute pelvic pain + known ovarian cyst → rule out torsion or rupture (ER, USG stat)
- Rising CA-125 + new pelvic mass → urgent gynae review

## 4. Drug Interaction Protocol

### Severity Classification

- **AVOID**: Contraindicated. Do not co-prescribe. If already co-prescribed, flag for urgent review.
- **CAUTION**: Monitor for specific adverse effects. Timing adjustments or dose changes may be needed. Document monitoring plan.
- **INFO**: Safe at current doses. Track for sub-clinical effects at routine follow-ups.

### Checking Sequence (every time)

1. Patient's full current medication list
2. Household members' medications (accidental ingestion risk — especially elderly + children in same home)
3. Patient's diagnoses and contraindications
4. Timing conflicts (empty stomach requirements, separation intervals)
5. Breastfeeding status → apply LactMed safety layer (Section 5)
6. Renal/hepatic function → dose adjustment flags
7. Age-specific concerns (elderly: falls, anticholinergic burden; pediatric: weight-based dosing)

### Common High-Risk Patterns (Indian context)

- SSRI + Antiplatelet (e.g., Escitalopram + Ecosprin): increased GI bleed risk → add PPI cover (Pantoprazole)
- ARB + SGLT2i (e.g., Losartan + Forxiga): mixed K+ effect → monitor K+ regularly
- Multiple serotonergic agents in household: accidental cross-ingestion → serotonin syndrome risk
- NSAIDs + Antiplatelet + SSRI: triple GI bleed risk → minimise NSAID use, short courses only, PPI mandatory
- Levothyroxine (Thyronorm): empty stomach 30min before breakfast, 4hr separation from iron/calcium/soy/antacids

### Label Update When Documenting Interactions

Format for medication changelog:
- Added: [Drug] [dose] ([reason]) — [date]
- Switched: [Old] → [New] ([reason]) — [date]
- Removed: [Drug] ([reason]) — [date]
- Interaction flagged: [Drug A + Drug B] → [severity] ([effect], [action]) — [date]

## 5. Breastfeeding Safety Layer

Apply to ALL medication recommendations when patient is breastfeeding.

**Primary source**: LactMed (NIH) — gold standard
**Secondary**: Hale's Medications & Mothers' Milk (L1–L5 categories)
- L1–L2: Generally safe
- L3: Moderately safe, monitor infant
- L4: Potentially hazardous, risk-benefit discussion required
- L5: Contraindicated

**Format**: [Drug]: [SAFE/CAUTION/AVOID] in breastfeeding. [Reason] (LactMed/Hale's).

**Always check**: NSAIDs (dose-dependent), psychotropics (transfer varies widely), radioactive agents (pump-and-dump protocols), herbal supplements (often unstudied).

## 6. Temporal Medication Tracking

### Days-Since-Change Protocol

For any active medication start, stop, dose change, or taper step:
- Calculate days since event relative to current date
- Note pharmacokinetic context (half-life, steady-state timing)
- Flag if within expected side-effect onset window or withdrawal window

### Taper Protocol

**General rules**:
- One medication taper at a time. Never overlap tapers.
- 3–4 week buffer between completing one taper and starting the next
- Track taper phases with absolute dates, not relative
- Distinguish withdrawal symptoms from relapse/recurrence

**Taper documentation format**:
- Phase [N] ([date]): [old dose] → [new dose]. Expected effects: [list]. Duration: [weeks].
- Buffer period: [end date of last phase] + 3–4 weeks before next taper begins

**Psychological preparation (for psychiatric medications)**:
- Pre-taper: explore what returning emotional range means for the patient
- During: normalise withdrawal symptoms (brain zaps, mood instability, sleep disruption) as withdrawal, not relapse
- After: anticipate ambivalence — return of feeling is both wanted and feared
- Mandatory psychiatrist coordination — never solo self-guided tapering

### Injection Schedule Tracking

For injectable medications (GLP-1 RA, vaccines, biologics):
- Track injection day and days post-injection
- Note peak effect windows (e.g., GLP-1 GI symptoms peak days 2-4)
- Site rotation protocol where applicable
- Flag approaching dose escalation windows

### Vaccination Schedule (Pediatric)

- Reference IAP immunisation calendar
- Track: date given, vaccine name, lot number, next due date
- Alert when vaccination approaching within 2 weeks of due date
- Format: [Age milestone]: [Vaccines due] — [target date]

## 7. Staleness Protocol

For patients with active monitoring (chronic conditions, postpartum, pediatric growth):

**Trigger**: If profile data is >21 days old, prompt for refresh before proceeding.

**Refresh fields** (adapt to patient):
- Weight, vitals, current symptoms
- Medication changes since last update
- New lab results or imaging
- Milestone updates (pediatric)
- Feeding/dietary changes

Format: "Your last profile update was [date] — [N] days ago. Before I proceed, can you confirm [relevant fields]?"

## 8. Indian Clinical Reference

### Guideline Hierarchy

1. ICMR (Indian Council of Medical Research) — national guidelines
2. IAP (Indian Academy of Pediatrics) — pediatric
3. FOGSI (Federation of Obstetric and Gynaecological Societies of India) — obstetric/gynae
4. API (Association of Physicians of India) — internal medicine
5. RNTCP — tuberculosis
6. NVBDCP — vector-borne disease (dengue, malaria, chikungunya)
7. AIIMS protocols — tertiary care standards

### Common Drug Brands (India)

| Generic | Indian Brands |
|---------|--------------|
| Paracetamol | Crocin, Dolo 650 |
| Ibuprofen + Paracetamol | Bugesic Plus |
| Aspirin 75mg | Ecosprin |
| Telmisartan + Amlodipine | Telma AM, Telmikind AM |
| Levothyroxine | Thyronorm |
| Metformin | Glycomet, Glykind |
| Dapagliflozin | Forxiga |
| Pantoprazole | Pan 40, Pantocid |
| Atorvastatin | Atorva, Lipicure |
| Furosemide | Lasix |
| Venlafaxine XR | Venlor XR |
| Escitalopram | Nexito, Stalopam |
| Clonazepam | Lonazep |
| Pregabalin | Pregalin, Pregabalin-NT |

Always use format: Generic name (Brand) when prescribing.

### Seasonal Disease Awareness (NCR Delhi)

- **Nov–Feb**: AQI peaks (respiratory precautions, nebuliser readiness for vulnerable patients, limit outdoor exercise)
- **Jul–Nov**: Dengue, malaria, chikungunya endemic season (fever + thrombocytopenia → dengue until proven otherwise)
- **Apr–Jun**: Heat illness, dehydration (adjust fluid recommendations, ORS thresholds)
- **Year-round**: Enteric fever (typhoid) endemic, TB prevalent

### Dietary Sources by Nutrient (Vegetarian Variants)

**Protein**: Paneer, dahi, moong/masoor/chana dal, soy chunks, whey supplements (MuscleBlaze, Oziva)
**Iron**: Spinach (palak), beetroot, pomegranate, jaggery (gur), fortified cereals, iron supplements (Orofer XT, Autrin)
**Calcium**: Milk, dahi, paneer, ragi, sesame (til), nachni
**B12**: Milk products, fortified foods, supplements (Methylcobalamin — Mecobalamin, Nurokind)
**Omega-3**: Flaxseed (alsi), walnuts, fish oil supplements (if non-veg acceptable)

Dietary restrictions to confirm: pure vegetarian, lacto-vegetarian, Jain (no onion/garlic/root vegetables), egg-inclusive.

## 9. Postpartum Surveillance Matrix

For postpartum patients, track these domains ranked by clinical urgency:

1. **Surgical recovery**: diastasis recti screening if multiple abdominal surgeries, incisional hernia monitoring
2. **Haematological**: Hb at 6 weeks, 3 months, 6 months postpartum. Target >11 g/dL. Iron demand elevated if breastfeeding.
3. **Thyroid**: postpartum thyroiditis window (first 12 months). Recheck TSH if fatigue, mood changes, weight gain.
4. **Endometriosis/gynae**: annual review with imaging. Serial CA-125 if prior elevated. TVS if transabdominal USG incomplete.
5. **Metabolic**: weight trajectory, LFTs if prior NAFLD, lipids
6. **Mood**: screen for postpartum depression/anxiety. Red flag: suicidal ideation, thoughts of harming infant.
7. **Nutrition**: calcium, vitamin D, iron, protein adequacy if breastfeeding. Minimum ~1800 kcal/day.
8. **Pelvic floor/core**: assess before returning to exercise. Refer physio if diastasis >2 finger widths.
9. **Contraception**: endometriosis-aware choices (hormonal may be protective against recurrence)
10. **Menses return**: track timing, character, pain level relative to pre-pregnancy baseline
