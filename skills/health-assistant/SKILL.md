---
name: health-assistant
version: 1.1.0
description: Personal health assistant with drug regulations, mental health support, and pet health guidance. Use for health tracking, medication reminders, symptom analysis, exercise/diet advice, travel health prep, first aid, international drug regulations, mental health counseling, and pet care.
---

# Personal Health Manager 🏥

Your comprehensive personal health companion for daily wellness management.

## When to Use

Use this skill whenever the user mentions:
- Health tracking, records, or data
- Medication management or reminders
- Symptoms, feeling unwell, or health concerns
- Exercise, fitness, or workout advice
- Diet, nutrition, or meal planning
- Travel preparation or trip planning
- First aid or emergency health advice
- General wellness questions

---

## User Profile Setup

Before providing personalized advice, always check or ask for:

### Basic Information
- **Age**: Required for exercise/diet recommendations
- **Gender**: Important for certain health considerations
- **Weight & Height**: For BMI calculation
- **Medical History**: Chronic conditions, past surgeries
- **Current Medications**: For drug interaction checks
- **Allergies**: Drug, food, environmental
- **Lifestyle**: Sedentary, active, smoking, alcohol

### Health Profile Template
```
👤 Profile:
- Name: [optional]
- Age: ___
- Gender: ___
- Height: ___cm
- Weight: ___kg
- BMI: ___ (auto-calculated)
- Blood Type: ___
- Allergies: ___
- Medical Conditions: ___
- Current Medications: ___
- Emergency Contact: ___
```

---

## Core Features

### 1. Health Data Recording 📊

Track and record various health metrics based on user profile:

#### Blood Pressure 💉
| Category | Systolic | Diastolic |
|----------|----------|-----------|
| Normal | <120 | <80 |
| Elevated | 120-129 | <80 |
| Stage 1 HTN | 130-139 | 80-89 |
| Stage 2 HTN | ≥140 | ≥90 |
| Crisis | >180 | >120 ⚠️ |

#### Blood Glucose 🍬
| Status | Fasting | 2h Post-Meal |
|--------|---------|---------------|
| Normal | <100 | <140 |
| Prediabetes | 100-125 | 140-199 |
| Diabetes | ≥126 | ≥200 |

#### Heart Rate ❤️
| Age Group | Normal Resting | Max Heart Rate |
|-----------|----------------|----------------|
| 20-29 | 60-100 | 190-200 |
| 30-39 | 60-100 | 180-190 |
| 40-49 | 60-100 | 170-180 |
| 50-59 | 60-100 | 160-170 |
| 60+ | 60-100 | 150-160 |

#### BMI Calculator ⚖️
| Category | BMI Range |
|----------|-----------|
| Underweight | <18.5 |
| Normal | 18.5-24.9 |
| Overweight | 25-29.9 |
| Obese | ≥30 |

---

### 2. Age-Specific Health Guidance

#### 👶 Children (0-12 years)
**Common Concerns:**
- Growth and development tracking
- Vaccination schedule
- Common childhood illnesses
- Screen time guidelines
- Sleep requirements by age

**Exercise:**
- Active play 60+ minutes/day
- Limit sedentary time

**Sleep:**
| Age | Hours |
|-----|-------|
| 0-3 months | 14-17 |
| 4-12 months | 12-16 |
| 1-2 years | 11-14 |
| 3-5 years | 10-13 |
| 6-12 years | 9-12 |

#### 👦 Teenagers (13-19 years)
**Common Concerns:**
- Puberty and development
- Mental health
- Academic stress
- Screen time balance
- Sports nutrition

**Exercise:**
- 60 min moderate-vigorous daily
- Muscle-strengthening 3x/week

**Nutrition Focus:**
- Calcium (bone growth)
- Iron (especially females)
- Protein for development

#### � adults (20-39 years)
**Common Concerns:**
- Work-life balance
- Stress management
- Preventive care
- Sexual health
- Building healthy habits

**Exercise:**
- 150 min moderate or 75 min vigorous/week
- Muscle-strengthening 2x/week

**Screenings:**
- Annual physical
- Blood pressure
- BMI
- Mental health check

#### 👨 Middle-Aged (40-59 years)
**Common Concerns:**
- Metabolic changes
- Heart health
- Bone density
- Vision changes
- Hormonal changes (menopause/andropause)

**Exercise:**
- 150 min moderate + 2 strength sessions/week
- Balance exercises to prevent falls

**Additional Screenings:**
- Cholesterol (every 5 years)
- Blood glucose (every 3 years)
- Colon cancer screening (45+)
- Bone density (women 65+, men 70+)

#### 👴 Seniors (60+ years)
**Common Concerns:**
- Fall prevention
- Cognitive health
- Medication management
- Chronic disease management
- Nutrition for aging

**Exercise:**
- 150 min moderate (spread out)
- Balance exercises 3x/week
- Strength training 2x/week

**Fall Prevention:**
- Home safety check
- Regular vision/hearing checks
- Review medications that cause dizziness

**Nutrition Focus:**
- Protein (prevent muscle loss)
- Vitamin D + Calcium
- Hydration (thirst decreases with age)
- Fiber (prevent constipation)

---

### 3. Gender-Specific Health

#### 🩺 Women's Health

**Reproductive Health:**
- Menstrual cycle tracking
- Pregnancy planning
- Menopause management
- PCOS/Endometriosis awareness

**Screening Schedule:**
| Age | Screening |
|-----|-----------|
| 21-29 | Pap smear every 3 years |
| 30-65 | Pap + HPV every 5 years |
| 40+ | Mammogram annually |
| 65+ | Bone density scan |

**Common Concerns:**
- Iron deficiency (especially during menstruation)
- Thyroid (women 5x more likely)
- Osteoporosis risk
- Mental health (postpartum, menopause)

**Pregnancy Considerations:**
- Pre-conception care
- Prenatal vitamins (folic acid)
- Weight gain guidelines
- Exercise during pregnancy

**Menopause:**
- Symptoms management
- Hormone therapy considerations
- Heart health post-menopause
- Bone health

#### 🩹 Men's Health

**Screening Schedule:**
| Age | Screening |
|-----|-----------|
| 30+ | Blood pressure |
| 35+ | Cholesterol |
| 45+ | Colon cancer |
| 50+ | Prostate discussion |
| 65+ | Abdominal aortic aneurysm (smokers) |

**Common Concerns:**
- Prostate health
- Testosterone changes
- Heart disease (men 2x higher risk before 65)
- Mental health stigma

**Testosterone:**
- Symptoms of low T: fatigue, low libido, mood changes
- Not always need treatment
- Discuss with doctor

---

### 4. Medication Management 💊

**Features:**
- Add/edit/delete medications
- Track dosage and frequency
- Set medication schedules
- Drug interaction warnings
- Refill reminders
- Medication history

#### Common Medications by Condition

**Hypertension:**
- ACE inhibitors (enalapril, lisinopril)
- ARBs (losartan, valsartan)
- Beta blockers (metoprolol)
- Diuretics (hydrochlorothiazide)

**Diabetes:**
- Metformin
- Sulfonylureas
- SGLT2 inhibitors
- Insulin

**High Cholesterol:**
- Statins (atorvastatin, rosuvastatin)
- Fibrates
- Ezetimibe

**Pain:**
- Acetaminophen
- Ibuprofen
- Naproxen

**Drug Interactions to Watch:**
| Drug A | Drug B | Effect |
|--------|--------|--------|
| Warfarin | Aspirin | Bleeding risk |
| Metformin | Alcohol | Lactic acidosis |
| Statins | Grapefruit | Increased side effects |
| ACE inhibitors | Potassium | High potassium |

---

### 5. Symptom Analysis 🩺

**Process:**
1. Collect symptom details (location, duration, severity)
2. Ask relevant follow-up questions
3. Provide possible causes (informational only)
4. Recommend when to seek medical attention
5. Suggest self-care measures if appropriate

#### Age-Specific Symptom Considerations

**Children:**
- Temperature thresholds lower
- Behavior changes more important than specific symptoms
- Dehydration happens faster
- When to seek care: fever >48h, unable to drink, rash with fever

**Adults:**
- Standard symptom assessment
- Chronic conditions affect presentation
- Medication side effects

**Elderly:**
- Symptoms often less typical
- Confusion can be only sign of infection
- Falls may indicate underlying problem
- Medication side effects more common

#### Red Flags - Seek Immediate Care 🚨
- Chest pain + sweating + pain in arm/jaw
- Difficulty breathing
- Severe bleeding
- Sudden severe headache
- Confusion/loss of consciousness
- Sudden weakness/numbness (stroke)
- High fever + rash
- Severe vomiting + unable to keep fluids down
- Overdose symptoms

---

### 6. Exercise Recommendations 🏃

#### By Age & Fitness Level

**Beginner (Any Age):**
- Start with 10-minute walks
- Chair exercises
- Water aerobics
- Dancing

**Intermediate:**
- Brisk walking 30 min
- Swimming
- Cycling
- Light strength training

**Advanced:**
- Running
- HIIT
- Heavy strength training
- Sports

#### By Health Condition

**High Blood Pressure:**
- Walking, swimming, cycling
- Avoid heavy weightlifting
- Include cool-down

**Diabetes:**
- Check blood sugar before/after exercise
- Carry fast-acting carbs
- Avoid exercise if glucose >250

**Arthritis:**
- Swimming (joint-friendly)
- Stationary bike
- Gentle yoga
- Avoid high-impact

**Heart Disease:**
- Cardiac rehab programs
- Start slow, gradual increase
- Monitor heart rate

---

### 7. Nutrition Advice 🥗

#### By Age

**Children:**
- Make food fun
- Involve in cooking
- Model healthy eating
- Don't force foods

**Adults:**
- Balanced macronutrients
- Meal prep for busy days
- Mindful eating
- Limit processed foods

**Seniors:**
- High protein (1.0-1.2g/kg)
- Vitamin D + B12
- Easy-to-chew foods
- Small, frequent meals

#### By Condition

**High Blood Pressure:**
- Low sodium (<1500mg/day)
- DASH diet
- Limit alcohol

**Diabetes:**
- Consistent carb intake
- High fiber
- Limit simple sugars
- Spread meals throughout day

**High Cholesterol:**
- Low saturated fat
- High fiber
- Omega-3 fatty acids
- Plant sterols

**Weight Management:**
- Calorie awareness (not counting)
- Protein + fiber for fullness
- Limit added sugars
- Drink water before meals

---

### 8. Travel Health Preparation ✈️

#### Pre-Trip Planning

**🧳 Clothing Checklist:**
- Weather-appropriate attire
- Comfortable shoes
- Extra layers
- Rain gear
- Sun protection

**💊 Medications:**
- Regular meds (extra supply)
- Pain relievers
- Anti-diarrheal
- Antihistamines
- Motion sickness pills
- First aid basics
- Destination-specific needs

**🏥 Health Documents:**
- Travel insurance
- Emergency contacts
- Medical history
- Prescription copies
- Vaccination records

#### By Destination

**Tropical:**
- Mosquito protection
- Sun protection
- Water safety
- Food safety

**Cold Climate:**
- Layer clothing
- Protect extremities
- Indoor air dryness
- Frostbite awareness

**High Altitude:**
- Acclimatization days
- Altitude sickness meds
- Extra hydration
- Limited exertion

**Long Flights:**
- Compression socks
- Move every 2 hours
- Stay hydrated
- Avoid alcohol/caffeine

---

## Data Storage

**Local Storage:**
- JSON files in workspace
- Export to CSV/JSON

**Privacy:**
- All data stored locally
- No external servers by default
- Easy export/deletion

---

## Emergency Information Template

```
🚨 EMERGENCY HEALTH CARD
─────────────────────────────────
Name: _________________
Blood Type: ___
Allergies: _________________
Medical Conditions: _________________
Current Medications: _________________

Emergency Contact:
Name: _________________
Phone: _________________

Doctor:
Name: _________________
Phone: _________________

Insurance: _________________
Policy #: _________________
─────────────────────────────────
```

---

## Disclaimer

⚠️ This provides health INFORMATION only, not medical advice. Always:
- Recommend professional medical consultation
- Suggest emergency services for serious symptoms
- Never claim to diagnose conditions
- Encourage regular health checkups
- Respect user privacy with health data

---

## Best Practices

1. **Personalize**: Ask age, gender, conditions before advice
2. **Clarify**: Ask follow-up questions
3. **Context**: Remember conversation history
4. **Empathize**: Be supportive about health concerns
5. **Safety First**: Err on side of caution
6. **Empower**: Teach, don't just give answers
7. **Follow Up**: Check on previous concerns

---

## 9. Drug Regulations & International Travel 🌍

When users ask about bringing medications across borders, traveling with medicines, or drug regulations in different countries, provide accurate information based on official sources.

### General Principles

| Category | Rule |
|----------|------|
| Personal use | "Self-use, reasonable quantity" - typically 1-3 months supply |
| Prescription drugs | Always carry prescription/doctor's note |
| Controlled substances | Check destination country regulations |
| Declare when in doubt | Red channel if uncertain |

### Key Countries/Regions

#### 🇯🇵 Japan
- OTC medicines available in drugstores (drugstore cosmetics)
- Some cold medicines contain codeine/methylephedrine - restricted
- Personal import: up to 2 months supply for personal use
- Declare at customs

#### 🇺🇸 USA
- FDA regulates all drugs entering US
- 3-month supply allowed for personal use
- Controlled substances require prescription
- Some ingredients banned (ephedrine in large quantities)

#### 🇦🇺 Australia
- Strict customs control
- TGA approval needed for some medicines
- Declare all medications
- 3-month supply for prescription drugs

#### 🇸🇬 Singapore
- Very strict drug laws
- Codeine-containing medicines restricted
- Prescription required for many drugs
- Severe penalties for violations

#### 🇨🇦 Canada
- 90-day supply allowed
- Prescription for controlled substances
- Health Canada import rules

#### 🇳🇿 New Zealand
- 3-month supply for prescription drugs
- 1 month for controlled drugs (e.g., pseudoephedrine)
- Declare all medications

#### 🇹🇭 Thailand
- Codeine/morphine controlled
- Prescription needed for sedatives
- Tourist-friendly but check ingredients

#### 🇭🇰 Hong Kong
- 7-day supply for prescription drugs
- RX标志 (registered pharmacy) recommended
- Avoid unregistered "药坊"

### Common Restricted Ingredients

| Ingredient | Concern | Countries |
|-----------|---------|------------|
| Codeine | Controlled narcotic | Most countries |
| Pseudoephedrine | Methamphetamine precursor | USA, Japan, Australia, NZ |
| Ephedrine | Controlled | Many countries |
| Melatonin | Regulated differently | EU, China |
| Traditional Chinese Medicine | Endangered animals | CITES restrictions |

### Special Cases

**Traditional Chinese Medicine:**
- 麝香 (musk), 虎骨 (tiger bone), 犀牛角 (rhino horn) - BANNED
- Other TCM usually OK in reasonable quantities
- Keep original packaging

**Online Pharmacy:**
- Many countries restrict cross-border drug sales
- Personal import usually OK in small quantities
- Requires prescription documentation

---

## 10. Mental Health Support 🧠

When users ask about mental health, psychological issues, emotional wellbeing, or psychological counseling.

### When to Use

Use this section for:
- Depression, anxiety, stress
- Sleep disorders
- Mental health of special groups (teens, elderly, postpartum)
- Psychological counseling
- Trauma recovery
- How to help others with mental health issues

### Depression

**Common Symptoms (lasting >2 weeks):**
- Persistent sadness, emptiness
- Loss of interest in hobbies
- Fatigue, low energy
- Sleep changes (insomnia or oversleeping)
- Appetite changes
- Difficulty concentrating
- Feelings of worthlessness
- Thoughts of self-harm

**When to Seek Help:**
- Symptoms lasting >2 weeks
- Affecting daily life
- Physical symptoms without clear cause
- Thoughts of self-harm

**How to Help:**
- Listen without judgment
- Encourage professional help
- Offer companionship
- Crisis hotline: 400-161-9995 (China)

### Anxiety

**Normal Anxiety vs Anxiety Disorder:**

| Normal Anxiety | Anxiety Disorder |
|----------------|-------------------|
| Has clear trigger | No clear cause or disproportionate |
| Goes away after event | Persists >6 months |
| Mild physical symptoms | Severe symptoms affecting life |
| Can function normally | Impaired work/social functioning |

**Coping Strategies:**
- Deep breathing (4-7-8 method)
- Physical exercise
- Sleep management
- Cognitive restructuring
- Mindfulness meditation
- Limit caffeine/alcohol

### Mental Health by Age Group

#### Adolescents
- Emotional regulation
- Academic stress
- Peer relationships
- Screen time balance
- Signs to watch: mood changes, social withdrawal, sleep changes

#### Postpartum
- Baby blues vs postpartum depression
- Support systems
- When to seek help: persistent sadness >2 weeks, thoughts of harm

#### Elderly
- Loneliness, social isolation
- Cognitive changes
- Depression often mistaken for aging
- Importance of social connection

### Psychological Counseling

**When to Consider:**
- Persistent emotional problems
- Relationship difficulties
- Life transitions
- Trauma recovery
- Behavioral issues

**Types of Help:**
- Counselor: mild-moderate issues
- Psychiatrist: medication needed
- Psychotherapist: deep treatment (CBT, EMDR)

---

## 11. Pet Health 🐕🐱

When users ask about pet care, animal health, pet nutrition, or veterinary questions.

### Dogs

**Common Health Issues:**

| Issue | Symptoms | When to See Vet |
|-------|----------|-----------------|
| Skin problems | Itching, redness, hair loss | >3 days |
| Ear infections | Head shaking, odor | Immediately |
| Digestive issues | Vomiting, diarrhea | If bloody or >24h |
| Parasites | Scratching, visible fleas | With prescription |

**Vaccination Schedule:**
- 6-8 weeks: First DHPP vaccine
- 10-12 weeks: Second vaccine
- 14-16 weeks: Third vaccine + rabies
- Annually: Booster

**Food & Nutrition:**
- High protein, animal-based
- Avoid: chocolate, grapes, onions, xylitol
- Puppies: high-protein, high-calorie
- Seniors: joint support, lower calories

**Emergency Signs:**
- Difficulty breathing
- Seizures
- Ingestion of toxins
- Severe bleeding
- Bloated/stretched abdomen

### Cats

**Common Health Issues:**

| Issue | Symptoms | When to See Vet |
|-------|----------|-----------------|
| Hairballs | Vomiting fur | Frequent (>1/week) |
| URI | Sneezing, discharge | With fever |
| FLUTD | Straining to urinate | Immediately (emergency!) |
| Dental disease | Bad breath, drooling | Regular checkups |

**Vaccination:**
- FVRCP (core): 8, 12, 16 weeks
- Rabies: 12-16 weeks
- Annual boosters

**Litter Box:**
- Clean daily
- Full change weekly
- 1.5-2 inches of litter
- One box per cat + 1

**Food & Nutrition:**
- Obligate carnivore - needs animal protein
- Wet food for hydration
- Avoid: dog food, raw eggs, milk

### Small Pets

**Hamsters:**
- Diet: seeds, grains, vegetables, protein
- Avoid: citrus, onions, almonds
- Fresh water daily
- Exercise wheel (solid surface)

**Rabbits:**
- Hay: 80% of diet
- Pellets: limited
- Vegetables daily
- Not: ice lettuce, potatoes

### General Pet Care

**Parasite Prevention:**
- Dogs: monthly flea/tick, heartworm prevention
- Cats: monthly topical/oral
- Indoor cats: still at risk

**Senior Pets:**
- More frequent vet visits (every 6 months)
- Joint supplements
- Comfortable bedding
- Adapted exercise

---

*Your health is your wealth. Take care of it!* 💚
