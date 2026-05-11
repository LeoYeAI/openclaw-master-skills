# Sample SOAP Notes

## Example 1: Cardiology Consultation

### Input (Raw Dictation)
```
45-year-old male here for follow-up after MI last month. Says he's feeling much better now. 
Walking 30 minutes daily without chest pain. Taking his medications as prescribed - 
metoprolol 50mg twice daily, atorvastatin 40mg daily, aspirin 81mg daily. No side effects. 
Vitals today: BP 128/78, HR 72 regular. Exam shows clear lungs, regular heart sounds, 
no edema. Assessment: Post-MI recovery progressing well, NYHA Class I. Plan: Continue 
current medications, repeat lipid panel in 3 months, follow up in 6 weeks, return sooner 
if chest pain recurs.
```

### Output (Structured SOAP)

**Subjective**
45-year-old male presents for post-MI follow-up. Patient reports significant improvement in symptoms. Currently walking 30 minutes daily without chest pain or shortness of breath. Adherent to medication regimen: metoprolol 50mg BID, atorvastatin 40mg daily, aspirin 81mg daily. Denies medication side effects.

**Objective**
- Vitals: BP 128/78 mmHg, HR 72 bpm (regular)
- Physical Exam: Lungs clear bilaterally, heart sounds regular, no peripheral edema

**Assessment**
1. Post-myocardial infarction - recovery phase
2. NYHA Class I (no limitation of physical activity)
3. Good medication compliance

**Plan**
1. Continue current medications:
   - Metoprolol 50mg PO BID
   - Atorvastatin 40mg PO daily
   - Aspirin 81mg PO daily
2. Laboratory: Fasting lipid panel in 3 months
3. Follow-up: Return in 6 weeks
4. Patient Education: Return immediately if chest pain recurs

---

## Example 2: Primary Care Visit - Diabetes Management

### Input (Raw Dictation)
```
62-year-old female with Type 2 diabetes here for routine follow-up. Home glucose logs 
show fasting readings 120-140. No hypoglycemic episodes. Reports good adherence to 
metformin 1000mg twice daily. Diet improved, walking 20 minutes most days. Weight 
down 3 pounds since last visit. Vitals: Weight 174 lbs, BP 138/84, HR 76. Exam 
unremarkable. Hgb A1c from last week is 7.2%, improved from 7.8%. Assessment: Type 2 
diabetes mellitus, well controlled. Plan: Continue metformin, recheck A1c in 3 months, 
continue lifestyle modifications, follow up in 3 months.
```

### Output (Structured SOAP)

**Subjective**
62-year-old female with Type 2 DM presents for routine follow-up. Home glucose monitoring shows fasting glucose 120-140 mg/dL. Denies hypoglycemic episodes. Reports excellent medication compliance with metformin 1000mg BID. Improved dietary habits with increased physical activity (walking 20 minutes most days). Reports 3-pound weight loss since last visit.

**Objective**
- Vitals: Weight 174 lbs, BP 138/84 mmHg, HR 76 bpm
- Physical Exam: Unremarkable
- Labs: Hgb A1c 7.2% (improved from 7.8% 3 months ago)

**Assessment**
1. Type 2 Diabetes Mellitus - well controlled
2. Improved glycemic control (A1c 7.2%)
3. Successful lifestyle modifications

**Plan**
1. Medications: Continue metformin 1000mg PO BID
2. Monitoring: Recheck Hgb A1c in 3 months
3. Lifestyle: Continue current diet and exercise regimen
4. Follow-up: Return in 3 months

---

## Example 3: Emergency Department Visit

### Input (Raw Dictation)
```
28-year-old female came in with right ankle injury after twisting it playing soccer 2 
hours ago. Heard a pop, immediate swelling. Pain 7/10, can't bear weight. No other 
injuries. No numbness or tingling. Vitals stable. Exam shows significant swelling 
over lateral ankle, tenderness over ATFL, positive anterior drawer. Distal pulses 
intact, sensation normal. X-ray negative for fracture. Assessment: Right ankle sprain, 
Grade 2. Plan: RICE protocol, ace wrap, crutches, ibuprofen 600mg q6h PRN pain, 
refer to orthopedics, follow up in 1 week or sooner if worsening.
```

### Output (Structured SOAP)

**Subjective**
28-year-old female presents with acute right ankle injury sustained 2 hours ago during soccer. Reports twisting mechanism with audible "pop" and immediate swelling. Pain rated 7/10. Unable to bear weight on affected limb. Denies numbness, tingling, or other injuries.

**Objective**
- Vitals: Stable
- Physical Exam:
  - Significant swelling over lateral right ankle
  - Tenderness over anterior talofibular ligament (ATFL)
  - Positive anterior drawer test
  - Distal pulses intact
  - Sensation normal
- Imaging: X-ray negative for fracture

**Assessment**
1. Right ankle sprain, Grade 2
2. ATFL injury

**Plan**
1. Conservative management:
   - RICE protocol (Rest, Ice, Compression, Elevation)
   - Ace wrap compression
   - Crutches for ambulation
2. Medications: Ibuprofen 600mg PO q6h PRN pain
3. Referral: Orthopedics for follow-up
4. Follow-up: Return in 1 week or sooner if symptoms worsen

---

## Example 4: Psychiatry Initial Evaluation

### Input (Raw Dictation)
```
34-year-old male referred by PCP for anxiety evaluation. Reports 6-month history of 
excessive worry about work performance, difficulty sleeping, muscle tension. Using 
alcohol 2-3 drinks nightly to relax. No suicidal thoughts. FH positive for anxiety 
in mother. Vitals stable. Mental status exam shows anxious affect, racing thoughts, 
no psychosis. Assessment: Generalized Anxiety Disorder, mild-moderate. Alcohol use 
as coping mechanism. Plan: Start sertraline 25mg daily, CBT referral, reduce alcohol, 
follow up in 2 weeks to assess medication tolerance.
```

### Output (Structured SOAP)

**Subjective**
34-year-old male presents for initial psychiatric evaluation (referred by PCP). Reports 6-month history of excessive worry about work performance. Associated symptoms include difficulty initiating and maintaining sleep, and persistent muscle tension. Using alcohol 2-3 drinks nightly as self-treatment for anxiety. Denies suicidal ideation, homicidal ideation, or psychotic symptoms. Family history positive for anxiety disorder in mother.

**Objective**
- Vitals: Stable
- Mental Status Exam:
  - Appearance: Well-groomed
  - Affect: Anxious
  - Thought process: Racing thoughts
  - Thought content: No psychosis, no SI/HI
  - Judgment/Insight: Fair

**Assessment**
1. Generalized Anxiety Disorder (F41.1) - mild to moderate severity
2. Alcohol use as maladaptive coping mechanism
3. Insomnia secondary to anxiety

**Plan**
1. Pharmacotherapy: Initiate sertraline 25mg PO daily, titrate as tolerated
2. Psychotherapy: Refer for Cognitive Behavioral Therapy (CBT)
3. Lifestyle: Patient counseled on reducing alcohol consumption
4. Safety: No current safety concerns
5. Follow-up: Return in 2 weeks to assess medication tolerance and efficacy
