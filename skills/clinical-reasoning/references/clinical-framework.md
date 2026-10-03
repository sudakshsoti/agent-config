
# Clinical Reasoning Framework

The reader is a clinician. No disclaimers ("consult your doctor"), no hedging, no dumbing down. Use clinical terminology directly. Reference Indian guidelines, brands, and availability.

## 1. Diagnostic Reasoning Protocol

Follow these steps for any clinical presentation. Skip steps that don't apply, but never skip Safety Checks.

**Step 1 -- Information Gathering**
Review all provided information: symptoms, duration, severity, progression, labs, imaging. Identify missing critical information. Flag red flags immediately (see Section 3).

**Step 2 -- Clinical Reasoning**
List differential diagnoses, most likely first. Explain reasoning for each. Consider demographics, risk factors, presentation patterns, seasonal context (dengue Jul-Nov, AQI respiratory Nov-Feb NCR, heat illness Apr-Jun).

**Diagnostic time-out before committing.** State three answers explicitly: what else could this be (name two alternatives), what must not be missed (the lethal or reversible one), and what does not fit (the finding the leading diagnosis fails to explain). If nothing fails to fit, the differential was anchored rather than reasoned. Cognitive factors drive roughly three-quarters of diagnostic errors and premature closure is the commonest.

**Step 3 -- Diagnostic Workup**
Suggest investigations. Prioritise by: urgency, availability in India, cost-effectiveness. Explain what each test confirms or rules out. Reference Indian lab chains when relevant (Thyrocare, SRL, Dr. Lal PathLabs). Use investigation cost tiers (Section 12) to contextualise recommendations.

**Step 4 -- Treatment Plan**
Evidence-based recommendations using Indian guidelines first (ICMR, AIIMS protocols, IAP for pediatric, FOGSI for obstetric/gynae, API for internal medicine, NTEP (formerly RNTCP) for TB, NVBDCP for vector-borne). Prescribe using: Generic name (Indian brand examples), dose, frequency, duration, route. Consider cost and patient compliance. State recommendation strength using GRADE when evidence is clear (Section 8.2).

**Step 5 -- Safety Checks (never skip)**
Run the Drug Interaction Protocol (Section 4), including the CYP450 layer (Section 4.6). For patients aged 65+, run the Geriatric Safety Protocol (Section 10). List contraindications. Highlight monitoring requirements. Provide warning signs requiring immediate attention.

**Step 6 -- Patient Education Points**
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
<2.0 normal | 2.0-2.9 borderline | >3.0 significant IR

**FIB-4** (liver fibrosis, for NAFLD):
(Age × AST) / (Platelet count × √ALT)
<1.30 low risk (F0-F1) | 1.30-2.67 indeterminate | >2.67 advanced fibrosis likely

**ASCVD 10-Year Risk**: Apply 1.2-1.5× multiplier for South Asian ancestry. Standard Framingham inputs: age, TC, HDL, SBP, smoking, diabetes.

### Lab Gap Flagging

Cross-reference against clinical milestones and current date. Flag overdue investigations:
- Format: "Last [parameter]: [value] ([date]) → [N months overdue] -- [clinical reason recheck needed]"
- Prioritise: HIGH (affects active treatment decisions), CRITICAL (surveillance gap for known pathology)

## 3. Red Flag Escalation Protocol

### 3.1 Routing Decision Tree

For every acute presentation, run this cascade:

```
Entry: Patient presents with acute symptom(s)
│
├─ Altered consciousness / GCS < 15 / seizure?
│  └─ YES → ER IMMEDIATELY. Secure airway. Do not proceed further.
│
├─ Haemodynamic instability? (SBP <90 or >180, HR >120 or <50, SpO2 <92%)
│  └─ YES → ER IMMEDIATELY.
│
├─ Matches any Universal Red Flag (Section 3.2)?
│  └─ YES → ER. Run pre-hospital actions if applicable (Section 3.3).
│
├─ Age-specific red flag triggered?
│  ├─ Pediatric → Section 3.4
│  ├─ Geriatric → Section 10.3
│  ├─ Postpartum → Section 3.5
│  └─ NO → Continue
│
├─ Moderate severity? (needs assessment but stable)
│  └─ YES → Same-day clinic visit.
│       Can teleconsult suffice? (Section 3.7)
│
└─ Mild, no red flags, manageable with OTC?
   └─ YES → Home care with safety-net advice.
        Provide specific re-assessment trigger: "Return if [X] within [Y] hours."
```

### 3.2 Universal Red Flags (any patient) → ER

- Chest pain/pressure with radiation (jaw, arm, back) or diaphoresis → ACS protocol
- Syncope or presyncope with known conduction defect → cardiology/ER
- Dark/tarry stools or haematemesis → GI bleed, especially on antiplatelet/SSRI/NSAID
- Severe hypoglycaemia: confusion, tremor, LOC → glucose/glucagon → ER
- Hyperkalaemia symptoms: muscle weakness, palpitations, paraesthesias → ER for ECG + K+
- Euglycaemic DKA (on SGLT2i): illness + vomiting + normal glucose but ketotic → STOP SGLT2i → ER
- Anaphylaxis: airway compromise, widespread urticaria, haemodynamic instability → epi + ER
- Stroke signs: sudden focal neurological deficit → ER within golden hour

### 3.3 Pre-Hospital Actions (while awaiting ambulance/transport)

These are first-responder actions for household members, not clinical protocols:

| Scenario | Immediate Action | Do NOT Do |
|----------|-----------------|-----------|
| Suspected ACS | Aspirin 325mg chewed, sit upright, loosen clothing | Do not give water to wash down aspirin |
| Anaphylaxis | Epi auto-injector (EpiPen) 0.3mg IM anterolateral thigh. Repeat in 5-15 min if no improvement. Lay flat, legs elevated (unless breathing difficulty) | Do not induce vomiting. Do not give oral antihistamine as sole treatment |
| Severe hypoglycaemia (conscious) | 15g fast-acting glucose (3-4 glucose tablets, 150ml juice, 1 tbsp honey) | Do not give food requiring chewing if semi-conscious |
| Severe hypoglycaemia (unconscious) | Glucagon 1mg IM/SC if available. Recovery position. Nothing by mouth | Do not attempt oral glucose |
| Seizure | Protect head, recovery position after cessation. Time the seizure. Midazolam buccal 10mg if available and seizure >5 min | Do not restrain. Do not put anything in mouth |
| Suspected stroke | Note time of onset (critical for thrombolysis window). FAST assessment | Do not give aspirin (could be haemorrhagic). Do not lower BP |

### 3.4 Pediatric Red Flags and Escalation

**Fever Escalation Ladder:**

```
Entry: Child with fever
│
├─ Age <3 months?
│  └─ ANY fever ≥38°C → ER regardless of appearance
│
├─ Age 3-36 months?
│  ├─ <38°C (100.4°F) → Monitor at home, hydration, cool compress
│  ├─ 38-38.5°C → Paracetamol drops (Crocin/Dolo), observe 24h
│  ├─ 38.5-39.2°C → Urgent clinic visit (not ER unless red flags)
│  └─ >39.2°C (102.5°F) → ER
│
└─ Age >36 months?
   └─ Apply same thresholds but with higher tolerance for clinic vs ER.
      Red flags override temperature thresholds.
```

**Pediatric Red Flags → ER:**
- <3 wet diapers in 24 hours (dehydration)
- Lethargy + fever (not just sleepiness: unresponsive to stimulation)
- Dry mucous membranes + sunken fontanelle
- Persistent vomiting >6 hours or inability to keep fluids down
- Bloody stools + fever
- Seizure (febrile or afebrile)
- Bulging fontanelle
- Mottled skin, prolonged capillary refill >3 seconds

### 3.5 Postpartum/Obstetric Red Flags → ER

- Heavy vaginal bleeding (soaking >1 pad/hour)
- Fever >38°C with uterine tenderness (endometritis)
- Sudden severe headache + visual changes (eclampsia)
- Calf pain/swelling (DVT risk elevated postpartum)
- Suicidal ideation or thoughts of harming infant → psychiatric emergency
- Incisional hernia: irreducible, painful, skin colour change → surgical ER

### 3.6 Endometriosis-Specific Red Flags

- Acute pelvic pain + known ovarian cyst → rule out torsion or rupture (ER, USG stat)
- Rising CA-125 + new pelvic mass → urgent gynae review

### 3.7 Teleconsult vs In-Person Decision

Teleconsult is sufficient when:
- No examination findings would change management (e.g., lab interpretation, medication adjustment, follow-up discussion)
- Patient can self-report vitals (BP cuff, thermometer, pulse ox at home)
- Condition is stable, previously diagnosed, and being monitored

In-person is non-negotiable when:
- New neurological symptoms (requires cranial nerve exam, reflexes, gait)
- Abdominal pain (requires palpation, guarding/rebound assessment)
- Joint/MSK complaints (requires range of motion, special tests)
- Skin lesions needing dermoscopy or biopsy
- Pediatric assessment in infants (unreliable parental vitals)
- Any red flag triggered

Indian teleconsult platforms: Practo, Apollo 24|7, Tata Health, MFine.

### 3.8 Gurugram Facility Reference

- **Medanta**: multi-specialty tertiary, strong cardiology/neurology/oncology
- **Artemis**: good general surgery, ortho, emergency
- **Fortis Memorial Research Institute**: spine surgery, interventional cardiology
- **Max Hospital Gurugram**: nephrology, urology
- **Paras Hospital**: cost-effective for routine procedures

## 4. Drug Interaction Protocol

### 4.1 Severity Classification

- **AVOID**: Contraindicated. Do not co-prescribe. If already co-prescribed, flag for urgent review.
- **CAUTION**: Monitor for specific adverse effects. Timing adjustments or dose changes may be needed. Document monitoring plan.
- **INFO**: Safe at current doses. Track for sub-clinical effects at routine follow-ups.

### 4.2 Checking Sequence (every time)

1. Patient's full current medication list
2. Household members' medications (accidental ingestion risk -- especially elderly + children in same home)
3. Patient's diagnoses and contraindications
4. Timing conflicts (empty stomach requirements, separation intervals)
5. Breastfeeding status → apply LactMed safety layer (Section 5)
6. Renal/hepatic function → dose adjustment flags (Section 4.5)
7. Age-specific concerns: elderly → Section 10, pediatric → weight-based dosing
8. CYP450/transporter interactions → Section 4.6

### 4.3 Common High-Risk Patterns (Indian context)

- SSRI + Antiplatelet (e.g., Escitalopram + Ecosprin): increased GI bleed risk → add PPI cover (Pantoprazole)
- ARB + SGLT2i (e.g., Losartan + Forxiga): mixed K+ effect → monitor K+ regularly
- Multiple serotonergic agents in household: accidental cross-ingestion → serotonin syndrome risk
- NSAIDs + Antiplatelet + SSRI: triple GI bleed risk → minimise NSAID use, short courses only, PPI mandatory
- Levothyroxine (Thyronorm): empty stomach 30min before breakfast, 4hr separation from iron/calcium/soy/antacids
- Statin + Fibrate (e.g., Atorvastatin + Fenofibrate): myopathy risk → avoid gemfibrozil specifically, fenofibrate is safer combination
- Pregabalin + other CNS depressants: additive sedation, respiratory depression in elderly, falls risk

### 4.4 Drug-Food and Drug-Supplement Interactions

Common in Indian households where Ayurvedic supplements and home remedies coexist with prescriptions:

| Drug | Interacting Substance | Effect | Action |
|------|-----------------------|--------|--------|
| Warfarin/Acenocoumarol | Green leafy vegetables (palak, methi), turmeric supplements | Altered INR, bleeding risk | Consistent dietary intake, avoid turmeric supplements |
| Fluoroquinolones (Cipro, Levo) | Calcium, iron, antacids, milk/dahi | Chelation, reduced absorption | 2hr separation before, 6hr after |
| Statins (Atorvastatin) | Grapefruit, amla in large quantities | CYP3A4 inhibition, increased statin levels | Avoid grapefruit; amla in dietary amounts is fine |
| Metformin | Alcohol | Lactic acidosis risk | Limit alcohol, avoid binge drinking |
| Levothyroxine | Soy products, ragi (calcium), coffee | Reduced absorption | 30-60 min separation |
| ACE inhibitors/ARBs | High-potassium foods (coconut water, banana, orange) | Hyperkalaemia | Monitor K+ if consuming large amounts daily |
| Tetracyclines (Doxycycline) | Milk, dahi, paneer, iron | Chelation | 1-2hr separation |
| MAOIs | Fermented foods (idli batter if very aged, aged cheese, soy sauce) | Tyramine reaction (hypertensive crisis) | Avoid aged/fermented foods |

Ayurvedic/herbal interactions to flag:
- **Ashwagandha**: may potentiate sedatives, thyroid medications
- **Triphala**: mild laxative effect, may alter drug absorption timing
- **Guggul**: may reduce effectiveness of propranolol, diltiazem
- **Giloy/Guduchi**: immunomodulatory, caution with immunosuppressants
- **Turmeric (curcumin supplements, not dietary haldi)**: antiplatelet effect, CYP inhibition at supplement doses

### 4.5 Renal/Hepatic Dose Adjustment Triggers

**Renal (eGFR-based):**
- eGFR <60: Review metformin dose (reduce if <45, stop if <30). Review gabapentinoids (reduce pregabalin). Review SGLT2i efficacy.
- eGFR <45: Stop metformin or reduce to 500mg BD max. Avoid NSAIDs entirely. Adjust digoxin.
- eGFR <30: Stop SGLT2i. Reduce pregabalin to 75mg/day max. Avoid nitrofurantoin.
- eGFR <15: Specialist nephrology input for all prescribing.

**Hepatic (Child-Pugh or clinical judgement):**
- Avoid paracetamol >2g/day in significant liver disease
- Reduce statin doses; avoid in active liver disease (ALT >3x ULN)
- SSRIs: reduce escitalopram to 10mg max in hepatic impairment
- Avoid methotrexate in significant fibrosis

### 4.6 CYP450 Interaction Framework

Key CYP enzymes relevant to commonly prescribed Indian medications:

**CYP3A4** (most broadly relevant):
- Substrates: atorvastatin, amlodipine, apixaban, midazolam, many immunosuppressants
- Inhibitors: ketoconazole, itraconazole, clarithromycin, erythromycin, grapefruit, diltiazem, verapamil
- Inducers: rifampicin (most potent -- wrecks nearly everything), phenytoin, carbamazepine, St John's Wort

**CYP2D6**:
- Substrates: metoprolol, tramadol (prodrug -- needs 2D6 for efficacy), tamoxifen (prodrug), many SSRIs
- Inhibitors: fluoxetine, paroxetine, bupropion
- Clinical relevance: fluoxetine/paroxetine + tamoxifen = AVOID (blocks activation). Fluoxetine + metoprolol = increased metoprolol levels.

**CYP2C19**:
- Substrates: clopidogrel (prodrug), omeprazole, escitalopram
- Inhibitors: omeprazole, fluoxetine, fluvoxamine
- Clinical relevance: omeprazole + clopidogrel = CAUTION (prefer pantoprazole which has weaker 2C19 inhibition). Genetic poor metabolisers: clopidogrel resistance.

**CYP1A2**:
- Substrates: theophylline, clozapine, caffeine
- Inhibitors: ciprofloxacin (strong), fluvoxamine
- Inducers: smoking, chargrilled food
- Clinical relevance: ciprofloxacin + theophylline = AVOID (toxicity). Smoking cessation in clozapine patients = dose adjustment needed.

**Rifampicin Rule**: Rifampicin is the most powerful enzyme inducer in clinical practice. It accelerates metabolism of nearly everything metabolised by CYP3A4, 2C9, 2C19. When a patient on TB treatment (DOTS/ATT) is co-prescribed any chronic medication, check for rifampicin interaction first. Common casualties: OCP (contraceptive failure), warfarin (subtherapeutic INR), statins (reduced efficacy), amlodipine (reduced BP control).

### 4.7 Label Update When Documenting Interactions

Format for medication changelog:
- Added: [Drug] [dose] ([reason]) -- [date]
- Switched: [Old] → [New] ([reason]) -- [date]
- Removed: [Drug] ([reason]) -- [date]
- Interaction flagged: [Drug A + Drug B] → [severity] ([effect], [action]) -- [date]

## 5. Breastfeeding Safety Layer

Apply to ALL medication recommendations when patient is breastfeeding.

**Primary source**: LactMed (NIH) -- gold standard
**Secondary**: Hale's Medications & Mothers' Milk (L1-L5 categories)
- L1-L2: Generally safe
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
- 3-4 week buffer between completing one taper and starting the next
- Track taper phases with absolute dates, not relative
- Distinguish withdrawal symptoms from relapse/recurrence
- **Taper hyperbolically, not linearly.** Receptor occupancy is hyperbolic in dose, so equal milligram steps are not equal effect steps: reduce by 10-25% of the *current* dose per step and slow further at the bottom of the range, where liquid or compounded doses are often needed below the smallest tablet. Pace by symptoms, patient-led, over months rather than weeks. Linear "halve it, then stop" schedules are deprecated (Horowitz & Taylor 2019; Maudsley Deprescribing Guidelines 2024). Psychiatric specifics in §14.9.5.

**Taper documentation format**:
- Phase [N] ([date]): [old dose] → [new dose]. Expected effects: [list]. Duration: [weeks].
- Buffer period: [end date of last phase] + 3-4 weeks before next taper begins

**Psychological preparation (for psychiatric medications)**:
- Pre-taper: explore what returning emotional range means for the patient
- During: normalise withdrawal symptoms (brain zaps, mood instability, sleep disruption) as withdrawal, not relapse
- After: anticipate ambivalence -- return of feeling is both wanted and feared
- Mandatory psychiatrist coordination -- never solo self-guided tapering

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
- Format: [Age milestone]: [Vaccines due] -- [target date]

## 7. Staleness Protocol

For patients with active monitoring (chronic conditions, postpartum, pediatric growth):

**Trigger**: If profile data is >21 days old, prompt for refresh before proceeding.

**Refresh fields** (adapt to patient):
- Weight, vitals, current symptoms
- Medication changes since last update
- New lab results or imaging
- Milestone updates (pediatric)
- Feeding/dietary changes

Format: "Your last profile update was [date] -- [N] days ago. Before I proceed, can you confirm [relevant fields]?"

## 8. Indian Clinical Reference

### 8.1 Guideline Hierarchy

1. ICMR (Indian Council of Medical Research) -- national guidelines
2. IAP (Indian Academy of Pediatrics) -- pediatric
3. FOGSI (Federation of Obstetric and Gynaecological Societies of India) -- obstetric/gynae
4. API (Association of Physicians of India) -- internal medicine
5. CSI (Cardiological Society of India) -- cardiology
6. RSSDI (Research Society for Study of Diabetes in India) -- diabetes
7. NTEP (formerly RNTCP) -- tuberculosis
8. NVBDCP -- vector-borne disease (dengue, malaria, chikungunya)
9. AIIMS protocols -- tertiary care standards
10. LAI (Lipid Association of India) -- dyslipidaemia

**International cross-reference** (use when Indian guideline is absent or outdated):

| Domain | Indian Guideline | International Equivalent | Notes |
|--------|-----------------|------------------------|-------|
| Diabetes | RSSDI/ICMR | ADA Standards of Care | Indian guidelines use lower BMI thresholds for screening |
| Lipids | LAI 2024 | ESC/EAS 2019, ACC/AHA 2018 | LAI has South Asian-specific risk thresholds |
| Hypertension | CSI/ISH | ESC 2023, AHA/ACC 2017 | Indian guidelines generally align with ESC |
| Heart failure | CSI | ESC 2021 | CSI largely follows ESC framework |
| Syncope | No Indian guideline | ESC 2018, ACC/AHA/HRS 2017 | Use international directly |
| Stroke | ISA (Indian Stroke Association) | AHA/ASA 2019, ESO 2022 | ISA adapts to Indian infrastructure |
| TB | RNTCP/NTEP | WHO 2022 | Indian guidelines are more prescriptive on DOTS |
| Pediatric immunisation | IAP | WHO EPI | IAP schedule is more comprehensive than NIS |
| Antenatal care | FOGSI | NICE, ACOG | FOGSI adapts to Indian prevalence patterns |

### 8.2 GRADE Evidence Reference

When stating recommendation strength, use this shorthand:

| Grade | Strength | Evidence Quality | Meaning |
|-------|----------|-----------------|---------|
| 1A | Strong | High (RCTs, meta-analyses) | Do this. Benefits clearly outweigh risks. |
| 1B | Strong | Moderate (limited RCTs, strong observational) | Do this. Confident despite imperfect evidence. |
| 2A | Conditional | High | Probably do this. Trade-offs exist, patient values matter. |
| 2B | Conditional | Moderate | Probably do this, but reasonable to choose otherwise. |
| 2C | Conditional | Low (case series, expert opinion) | Consider this. Uncertain evidence, may change with new data. |

**How to apply in bedside reasoning:**
- 1A/1B: State the recommendation directly. "Empagliflozin is indicated here (GRADE 1A, EMPEROR-Reduced)."
- 2A/2B: Present as preferred option with alternatives. "Pregabalin is reasonable here (GRADE 2B), though duloxetine is an alternative with different side-effect profile."
- 2C: Frame as clinical judgement call. "Evidence is limited (GRADE 2C), but based on mechanism and clinical experience, [approach] is reasonable."
- No grade: When evidence is purely experiential or guideline-absent, say so explicitly rather than implying false certainty.

**Indian guideline grading note**: ICMR and many Indian guidelines do not use GRADE formally. When referencing Indian guidelines, note the guideline source and year rather than assigning a GRADE retroactively. Reserve GRADE for international guidelines that use it natively (ESC, AHA/ACC, WHO).

### 8.3 Common Drug Brands (India)

| Generic | Indian Brands |
|---------|--------------|
| Paracetamol | Crocin, Dolo 650 |
| Ibuprofen + Paracetamol | Bugesic Plus |
| Aspirin 75mg | Ecosprin |
| Telmisartan + Amlodipine | Telma AM, Telmikind AM |
| Levothyroxine | Thyronorm |
| Metformin | Glycomet, Glykind |
| Dapagliflozin | Forxiga |
| Empagliflozin | Jardiance |
| Saroglitazar | Lipaglyn |
| Pantoprazole | Pan 40, Pantocid |
| Atorvastatin | Atorva, Storvas, Lipicure |
| Rosuvastatin | Rozavel, Crestor |
| Furosemide | Lasix |
| Venlafaxine XR | Venlor XR |
| Escitalopram | Nexito, Stalopam |
| Clonazepam | Lonazep |
| Pregabalin | Pregalin, Pregabalin-NT |
| Silodosin | Urimax-S, Silodal |
| Dutasteride | Duprost, Veltride |
| Semaglutide (injectable) | Wegovy, Ozempic |
| Isotretinoin | Tretiva, Isotroin |
| Methylcobalamin | Mecobalamin, Nurokind |
| Gabapentin | Gabantin, Gabapin |
| Duloxetine | Duzela, Cymbalta |

Always use format: Generic name (Brand) when prescribing.

### 8.4 Seasonal Disease Awareness (NCR Delhi)

- **Nov-Feb**: AQI peaks (respiratory precautions, nebuliser readiness for vulnerable patients, limit outdoor exercise)
- **Jul-Nov**: Dengue, malaria, chikungunya endemic season (fever + thrombocytopenia → dengue until proven otherwise)
- **Apr-Jun**: Heat illness, dehydration (adjust fluid recommendations, ORS thresholds)
- **Year-round**: Enteric fever (typhoid) endemic, TB prevalent

### 8.5 Dietary Sources by Nutrient (Vegetarian Variants)

**Protein**: Paneer, dahi, moong/masoor/chana dal, soy chunks, whey supplements (MuscleBlaze, Oziva)
**Iron**: Spinach (palak), beetroot, pomegranate, jaggery (gur), fortified cereals, iron supplements (Orofer XT, Autrin)
**Calcium**: Milk, dahi, paneer, ragi, sesame (til), nachni
**B12**: Milk products, fortified foods, supplements (Methylcobalamin -- Mecobalamin, Nurokind)
**Omega-3**: Flaxseed (alsi), walnuts, fish oil supplements (if non-veg acceptable)
**Vitamin D**: Sunlight (limited utility in NCR due to AQI Nov-Feb), supplements (D-Rise 60K sachets, Calcirol)
**Potassium**: Coconut water, banana, orange, sweet potato, dal

Dietary restrictions to confirm: pure vegetarian, lacto-vegetarian, Jain (no onion/garlic/root vegetables), egg-inclusive.

## 9. Postpartum Surveillance Matrix

For postpartum patients, track these domains ranked by clinical urgency:

1. **Surgical recovery**: diastasis recti screening if multiple abdominal surgeries, incisional hernia monitoring
2. **Haematological**: Hb at 6 weeks, 3 months, 6 months postpartum. Target >11 g/dL. Iron demand elevated if breastfeeding.
3. **Thyroid**: postpartum thyroiditis window (first 12 months). Recheck TSH if fatigue, mood changes, weight gain.
4. **Endometriosis/gynae**: annual review with imaging. Serial CA-125 if prior elevated. TVS if transabdominal USG incomplete.
5. **Metabolic**: weight trajectory, LFTs if prior NAFLD, lipids
6. **Mood**: EPDS at 6 weeks and again if symptoms emerge — ≥10 screens positive, ≥13 is specific, and **item 10 positive requires same-day assessment**. Red flag: suicidal ideation, thoughts of harming infant.
7. **Nutrition**: calcium, vitamin D, iron, protein adequacy if breastfeeding. Minimum ~1800 kcal/day.
8. **Pelvic floor/core**: assess before returning to exercise. Refer physio if diastasis >2 finger widths.
9. **Contraception**: endometriosis-aware choices (hormonal may be protective against recurrence)
10. **Menses return**: track timing, character, pain level relative to pre-pregnancy baseline

## 10. Geriatric Safety Protocol

Apply to all patients aged 65+ or any patient with frailty markers (unintentional weight loss, slow gait, low grip strength, fatigue, low physical activity). In Indian joint-family context, apply liberally to elderly household members whose medications you're reviewing.

### 10.1 Medication Review Framework

**Anticholinergic Burden Screening:**
Run through the full medication list and score anticholinergic load. Common culprits in Indian prescribing:

| Drug | ACB Score | Common Reason Prescribed | Safer Alternative |
|------|-----------|-------------------------|-------------------|
| Hydroxyzine (Atarax) | 3 | Anxiety, pruritus | Cetirizine (score 0) for itch; low-dose SSRI for anxiety |
| Chlorpheniramine (Avil) | 3 | Allergic rhinitis | Fexofenadine, cetirizine |
| Oxybutynin | 3 | Urinary urgency | Mirabegron (Myrbetriq) |
| Amitriptyline | 3 | Neuropathic pain, insomnia | Duloxetine or pregabalin for pain; melatonin for sleep |
| Cyclobenzaprine | 2 | Muscle spasm | Short course only, avoid chronic use |
| Ranitidine (discontinued) / Famotidine | 1 | Acid reflux | PPI if needed, but review duration |
| Paroxetine | 2 | Depression | Escitalopram (lower ACB) |

Total ACB ≥3: increased falls, cognitive decline, delirium risk. Flag for review.

**Beers Criteria Key Items (Indian-relevant):**
- Long-acting benzodiazepines (diazepam, clonazepam >0.5mg) → falls, cognitive impairment
- NSAIDs chronic use → GI bleed, renal injury, CV risk
- Glibenclamide/glimepiride → prolonged hypoglycaemia (prefer vildagliptin, linagliptin in elderly)
- Metoclopramide >12 weeks → tardive dyskinesia
- PPIs >8 weeks without clear indication → reassess, risk of Mg depletion, fractures

### 10.2 Falls Risk Assessment

Screen when adding any sedating medication or when patient reports unsteadiness:

**High-risk medication combinations for falls:**
- Pregabalin/gabapentin + antihypertensive (orthostatic hypotension)
- SSRI + antiplatelet (bleeding risk if fall occurs)
- Benzodiazepine + opioid (sedation, respiratory depression)
- Alpha-blocker (silodosin/tamsulosin for BPH) + antihypertensive (first-dose syncope)

**Environmental screen** (ask patient/family):
- Bathroom grab bars? Wet floors?
- Adequate lighting, especially at night?
- Loose rugs, cables, uneven surfaces?
- Footwear appropriate?

### 10.3 Geriatric Red Flags → ER

In addition to universal red flags (Section 3.2):
- Acute confusion/delirium (not baseline): UTI, medication effect, metabolic derangement, stroke
- Fall with head injury on anticoagulant/antiplatelet → CT head even if asymptomatic
- New urinary retention → medication review (anticholinergics, alpha-agonists)
- Sudden functional decline (can't do what they did yesterday) → broad workup

### 10.4 Deprescribing Framework

When total medication count exceeds 5 (polypharmacy) or 10 (hyperpolypharmacy), initiate deprescribing review:

```
Step 1: List all medications with indication for each.
        Flag any without clear current indication.

Step 2: Rank by risk-benefit in current clinical context.
        "Was this started for a problem that's resolved?"
        "Has the risk profile changed with ageing/new diagnoses?"

Step 3: Identify candidates for removal or dose reduction.
        Priority targets: PPIs >8 weeks, statins in very elderly (>85) with limited life expectancy,
        chronic benzodiazepines, duplicate therapies.

Step 4: One change at a time. Wait 2-4 weeks before next change.
        Monitor for withdrawal effects vs symptom recurrence.

Step 5: Document rationale. "Stopped [drug] because [reason]. Monitor for [specific symptom] over [timeframe]."
```

### 10.5 CKD-Adjusted Prescribing Quick Reference

Most relevant for elderly patients with age-related eGFR decline:

| eGFR Range | Key Adjustments |
|------------|----------------|
| 45-60 | Reduce metformin to 1000mg/day max. Monitor Mg if on PPI. |
| 30-45 | Stop metformin or 500mg/day max. Halve pregabalin dose. Reduce digoxin. Avoid colchicine long-term. |
| 15-30 | Stop SGLT2i. Stop metformin. Stop nitrofurantoin. Reduce gabapentinoids further. Nephrology input. |
| <15 | All prescribing via nephrologist. Dialysis-adjusted dosing. |

## 11. Imaging Interpretation Framework

### 11.1 How to Read a Radiology Report

Structure your interpretation in this order:

1. **Technique**: What was done? (MRI vs CT, contrast vs non-contrast, specific sequences). This determines what pathology can and cannot be seen.
2. **Key findings**: What's abnormal? Translate radiology language into clinical significance.
3. **Incidental findings**: What was found that wasn't the clinical question? Do they need follow-up?
4. **What's NOT mentioned**: If your clinical suspicion wasn't addressed, the study may not have been adequate to answer the question.
5. **Correlation**: Do findings match the clinical picture? Discordance between imaging and symptoms should trigger further investigation, not dismissal of either.

### 11.2 Spine MRI Interpretation (Common Use Case)

Spine MRI is one of the most frequently misread reports. Structured approach:

**Disc pathology grading:**
- Bulge: broad-based, symmetric, >180° of disc circumference. Often incidental, age-related.
- Protrusion: focal, <180° of disc circumference, base wider than apex. May or may not be symptomatic.
- Extrusion: base narrower than apex, disc material extends beyond annulus. More likely clinically significant.
- Sequestration: free fragment, separated from parent disc. Usually requires intervention.

**What matters clinically:**
- Neural foraminal narrowing grade (mild/moderate/severe) and correlation with radiculopathy dermatome
- Thecal sac compression and central canal stenosis grade
- Facet arthropathy (contributor to axial pain)
- Modic changes (Type 1 = inflammation/active, Type 2 = fatty/stable, Type 3 = sclerotic)
- Ligamentum flavum hypertrophy (contributes to stenosis)

**When to push for advanced imaging:**
- MRI non-concordant with symptoms → consider dynamic flexion/extension MRI or CT myelogram
- Suspected instability → flexion/extension X-rays
- Post-surgical spine → MRI with gadolinium (to differentiate scar from recurrent disc)
- Suspected infection/tumour → MRI with contrast mandatory

### 11.3 Imaging Urgency Decision

| Finding | Urgency | Action |
|---------|---------|--------|
| Acute cord compression signs on MRI | EMERGENCY | Neurosurgery same day |
| Cauda equina features (bilateral symptoms, bowel/bladder, saddle anaesthesia) | EMERGENCY | MRI stat if not done, neurosurgery |
| Vertebral fracture with retropulsion | URGENT | Spine surgery consult within 24-48h |
| Moderate-severe foraminal stenosis matching symptoms | SEMI-URGENT | Spine clinic within 1-2 weeks |
| Mild degenerative changes, no neural compromise | ROUTINE | Conservative management, clinic follow-up |
| Incidental renal/adrenal/hepatic finding | DEPENDS | Follow radiology recommendation for follow-up imaging |

### 11.4 Chest X-ray Quick Read

Systematic approach: ABCDEFGH
- **A**irway: trachea midline? Deviation suggests tension pneumothorax, large effusion, or mass.
- **B**ones: rib fractures, lytic lesions, osteopenia
- **C**ardiac: cardiothoracic ratio >0.5 = cardiomegaly. Boot-shaped = RV hypertrophy. Globular = pericardial effusion.
- **D**iaphragm: elevated? Flattened (hyperinflation in COPD)? Free air under diaphragm (perforation)?
- **E**dges (costophrenic angles): blunted = effusion (need ~200ml to blunt on PA film)
- **F**ields (lung): opacities, consolidation, nodules, hyperinflation
- **G**astric bubble: confirm left side (situs)
- **H**ilum: lymphadenopathy, vascular prominence

## 12. Investigation Cost Tiers (India, 2025-26 approximate)

Useful for prioritising workup when advising family members. Prices are approximate for private labs in NCR (Thyrocare, Dr. Lal, SRL). Government hospital labs are cheaper but slower.

| Tier | Cost Range | Examples |
|------|-----------|---------|
| Tier 1 (Basic) | Under ₹500 | CBC, ESR, urine routine, random blood sugar, blood group |
| Tier 2 (Standard) | ₹500-1,500 | LFT, KFT, lipid panel, HbA1c, TSH, uric acid, fasting insulin, iron studies, Widal |
| Tier 3 (Moderate) | ₹1,500-3,000 | Vitamin D, B12, complete thyroid panel (T3/T4/TSH), dengue NS1+IgM combo, urine culture, stool culture, PT/INR, fibroscan |
| Tier 4 (Expensive) | ₹3,000-8,000 | MRI (single region), CT scan (with contrast), echocardiography, treadmill test, Holter monitor, 24hr urine protein, HbA1c + fasting insulin + HOMA-IR panel |
| Tier 5 (High) | ₹8,000-20,000 | MRI with contrast, PET-CT, cardiac catheterisation, nerve conduction study, endoscopy/colonoscopy, polysomnography |
| Tier 6 (Very high) | ₹20,000+ | PET-CT whole body, cardiac MRI, whole-exome sequencing, specialised autoimmune panels |

**Cost optimisation strategies:**
- Thyrocare offers bundled panels at significant discounts vs individual tests
- Government hospital labs (AIIMS, Safdarjung, district hospitals) are 50-80% cheaper but turnaround is longer
- Some tests are cheaper at standalone radiology centres vs hospital radiology (especially MRI)
- Preventive health packages often bundle Tier 1-3 tests at 30-40% less than individual pricing

## 13. Response Templates

Not every query needs the full diagnostic workup. Match response structure to query type:

### Template A: Acute Presentation
Use for: new symptoms, "what could this be?", emergency assessment
Structure: Red flags check → Clinical assessment → Differential → Workup → Treatment → Safety → Follow-up

### Template B: Lab Review
Use for: "interpret these results", "are these numbers concerning?"
Structure: Parameter-by-parameter grading (Section 2 severity) → Trend analysis if prior data exists → Lab gaps flagging → Clinical correlation → Action items with timeline

### Template C: Medication Review
Use for: "check this medication plan", "any interactions?", "should I add/change X?"
Structure: Current med list reconciliation → Interaction check (Section 4, including CYP450) → Age-appropriate safety (geriatric if applicable) → Specific recommendation with rationale → Monitoring plan

### Template D: Chronic Management Review
Use for: quarterly check-ins, "how is Dad's regimen looking?", ongoing condition management
Structure: Days since last changes → Medication reconciliation including OTC/Ayurvedic → Each condition against its target and review interval (Section 16.2) → Trend, not just latest value → Outstanding lab and screening gaps → Adherence and cost probe (Section 16.4) → Function → Deprescribing review if 5+ medications → Adjusted plan with one owner and one date per action (Section 16.3)

### Template E: Quick Clinical Question
Use for: "is X safe with Y?", "what's the dose of Z?", factual lookups
Structure: Direct answer → Brief rationale → Caveats if any. No full workup needed.

**Selection rule**: Default to the simplest template that answers the question. Escalate to a more comprehensive template only if the clinical picture demands it or if red flags emerge during reasoning.

## 14. Mental Health Assessment Framework

Moved to [`mental-health.md`](mental-health.md): when to apply (§14.1), screening
instruments with cut-offs (§14.2), referral thresholds (§14.3), Indian access
realities (§14.4), brand and teleprescribing table (§14.5), pharmacokinetic
engineering (§14.6), biopsychosocial-existential formulation (§14.7), diagnostic
discipline before the label (§14.8), longitudinal psychiatric care (§14.9),
monitoring calendars (§14.10), Indian regulatory constraints (§14.11), anxiety
disorders — panic, agoraphobia and the depression mislabel (§14.12), boundary
with therapy (§14.13).

## 15. Clinical Search Triggers

When to search the web for clinical queries (beyond the generic search protocol):

**Always search for:**
- Drug availability: "Is [brand] still marketed in India?" (brands get discontinued, e.g., ranitidine)
- Guideline updates: "Current ICMR guidelines for [condition]" -- guidelines update without notice
- Drug pricing: if cost comparison is relevant to the recommendation
- New formulations: "Is [drug] available as [form] in India?" (e.g., injectable semaglutide availability)
- Interaction databases: when a novel or uncommon drug combination is being evaluated
- Procedure costs: "ESI cost at Fortis Gurgaon" or "MRI lumbar spine cost NCR"

**Don't search for:**
- Standard drug dosing for well-established medications
- Basic pharmacology (mechanism, half-life) for common drugs
- Clinical features of common conditions
- Lab reference ranges (use standard values unless population-specific needed)

## 16. Longitudinal and Chronic Care

Moved to [`longitudinal-care.md`](longitudinal-care.md): the planned visit (§16.1),
treat-to-target reference with review intervals (§16.2), the periodic review
(§16.3), adherence and cost (§16.4), the 4Ms for older adults (§16.5), transitions
and ownership (§16.6), function as an outcome (§16.7).
