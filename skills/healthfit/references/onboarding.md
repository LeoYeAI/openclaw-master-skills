# Western Profiling Flow (Onboarding) - Complete Version

> **Purpose:** Establish user's basic physiological data and health profile  
> **Estimated Time:** 15-20 minutes (Standard Mode)  
> **Last Updated:** 2026-03-18

---

## Profiling Mode Selection (Choose One of Three)

**Before starting profiling, please select your preferred profiling mode:**

See: `references/onboarding_options.md`

- **A. Questionnaire Mode** (Recommended) — About 20-25 questions, 20-25 minutes, most comprehensive information
- **B. Chat Mode** (Relaxed) — 25-30 minutes, natural conversation without pressure
- **C. File Upload Mode** (Quick) — 10-15 minutes, requires AI tool to support file reading capability

**⚠️ File Upload Mode Prerequisites:** Your AI tool must support one of the following capabilities:
- 📄 File upload function (can upload PDF/images/Excel)
- 📸 Image reading capability (can recognize health checkup report photos)
- 📁 Project file reading capability (can read files in workspace)

---

## Profiling Depth Selection (Important)

**Please select your desired profiling depth:**

### 🚀 Minimal Mode (5 minutes, 10 questions)
- **Collects:** Nickname, gender, age, height, weight, goals only
- **Suitable for:** Users who want to quickly experience the function
- **Follow-up:** Can supplement complete profile anytime

### ⚖️ Standard Mode (15-20 minutes, 25 questions) ⭐ Recommended
- **Collects:** Basic data + health history + goals + resources
- **Skips:** Fitness testing, detailed lifestyle habits
- **Suitable for:** Most users
- **Follow-up:** Recommended to supplement fitness data within 1-2 weeks

### 📋 Complete Mode (30-40 minutes, 45+ questions)
- **Collects:** All data + fitness baseline + TCM constitution identification
- **Suitable for:** Users pursuing precise personalized recommendations
- **Advantage:** Immediately obtain most precise training and diet plans

**Response Method:** Each question provides fixed options + vague options + free description, AI will intelligently extract key information!

---

## Profiling Principles

- **Phased collection:** Don't ask 20 questions at once, group logically, 3-5 questions per group, complete in rounds
- **Proactive follow-up:** If user answers are vague or incomplete, proactively ask until data is precise enough
- **Skippable options:** Data marked as "optional" can be skipped, supplemented later
- **Privacy marking:** For privacy data involving sexual health, medication history, clearly inform storage method
- **Three response methods:** Each question provides fixed options + vague options + free description
- **Progress prompts:** At start of each question group, display current progress (e.g., "Group 1/5, completed 20%")

---

## Question Response Method Explanation

**Each question provides three response methods, user can freely choose:**

### Example: Question — What is your exercise experience?

**Method 1: Fixed Options (Recommended)**
- A. Beginner (almost no exercise)
- B. Novice (occasional exercise, no systematic training)
- C. Intermediate (regular exercise 3-6 months)
- D. Advanced (systematic training 1+ years)

**Method 2: Vague Option**
- E. Not sure / Can't say clearly

**Method 3: Free Description**
> You can also describe directly in natural language, for example:
> "I occasionally go for runs, but haven't been to a gym, don't know how to train with weights"

**AI will intelligently extract key information from your response!**

---

## 🔒 Privacy Module Selection (Ask at Profiling Start)

**Before starting profiling, please select whether to enable privacy module:**

HealthFit includes an **optional privacy module** (sexual health records and guidance) for:
- 📝 Record sexual activity frequency and quality
- 🏋️ Provide male/female-specific training (pelvic floor, glute shaping, etc.)
- 🌿 TCM sexual wellness advice
- 📊 Sexual function and overall health correlation analysis

**Privacy Protection:**
- ✅ Completely optional, doesn't affect other functions if not filled
- ✅ Data stored independently (`private_sexual_health.json`)
- ✅ Excluded from backup/export by default
- ✅ Requires secondary confirmation to view or export

**Would you like to enable this module?**
- A. Yes, enable (enter sexual health profiling flow)
- B. No, skip (can fill in later anytime)
- C. Not sure, learn more information first

---

## Group 1: Basic Physiological Data (Required)

### Question List

```
Q1. What should I call you? (Nickname is fine)

Q2. What is your biological sex?
    A. Male
    B. Female
    C. Other / Prefer not to disclose

Q3. Age?

Q4. Height (cm)?

Q5. Current weight (kg)?

Q6. Body fat percentage (%)? (Optional, can skip if unknown)
    → If unknown, can estimate through visual description or skinfold thickness

Q7. Waist and hip circumference (cm)? (Optional)
    → Used to track body composition changes
```

### AI Calculation Output

**After profiling completion, automatically calculate:**

```
📊 Basic Data Calculation Results

BMI (Body Mass Index): {bmi}
→ Formula: weight (kg) ÷ height² (m)
→ Classification:
  - <18.5: Underweight
  - 18.5-24.9: Normal range ✅
  - 25-29.9: Overweight
  - ≥30: Obese

BMR (Basal Metabolic Rate): {bmr} kcal/day
→ Formula: Mifflin-St Jeor Formula
  Male: (10 × weight) + (6.25 × height) - (5 × age) + 5
  Female: (10 × weight) + (6.25 × height) - (5 × age) - 161
→ Interpretation: Minimum calories required to maintain vital signs when completely at rest

TDEE (Total Daily Energy Expenditure): {tdee} kcal/day
→ Formula: BMR × Activity Factor
→ Activity Factor:
  - Sedentary (almost no exercise): 1.2
  - Lightly active (1-3 days/week exercise): 1.375
  - Moderately active (3-5 days/week exercise): 1.55
  - Very active (6-7 days/week exercise): 1.725
  - Extra active (physical job + daily training): 1.9

Ideal weight range: {min_weight} - {max_weight} kg
→ Based on height and sex, weight range corresponding to BMI 18.5-24.9
```

---

## Group 2: Recent 2-3 Year Health History (Important)

### Medication Records

```
Q8. Are you currently taking prescription medications long-term? (Taking continuously for more than 1 month)
    A. Yes
    B. No

If Yes:
Q8-1. Medication name or category? (e.g., antihypertensives, hormones, antidepressants, etc.)

Q8-2. Medication start time?

Q8-3. Current status?
    A. Still taking
    B. Stopped (when stopped?)

Q8-4. Medication purpose? (Helps determine impact on exercise and nutrition)
```

### Disease & Surgery Records

```
Q9. In the past 2-3 years, have you experienced any of the following? (Multiple choice)
    A. Hospitalized illness
    B. Surgery (including minimally invasive surgery)
    C. Chronic disease diagnosis (hypertension, diabetes, thyroid issues, etc.)
```

### Allergies & Sensitivities

```
Q10. Do you have any food allergies or sensitivities?
    A. No
    B. Yes (please specify): ____________

Q11. Do you have any exercise limitations or injuries?
    A. No
    B. Yes (please specify): ____________
```

---

## Group 3: Exercise Habits & Goals (Important)

### Exercise Experience

```
Q12. What is your exercise experience?
    A. Beginner (almost no exercise)
    B. Novice (occasional exercise, no systematic training)
    C. Intermediate (regular exercise 3-6 months)
    D. Advanced (systematic training 1+ years)

Q13. How many days per week can you exercise?
    A. 1-2 days
    B. 3-4 days
    C. 5-6 days
    D. Every day

Q14. How long is each exercise session?
    A. <30 minutes
    B. 30-45 minutes
    C. 45-60 minutes
    D. >60 minutes

Q15. What time of day do you prefer to exercise?
    A. Morning (6:00-9:00)
    B. Midday (9:00-12:00)
    C. Afternoon (12:00-18:00)
    D. Evening (18:00-22:00)
```

### Equipment & Resources

```
Q16. Do you have a gym membership?
    A. Yes (distance/commute time?)
    B. No, but considering
    C. No, not planning to

Q17. What equipment do you have at home? (Multiple choice)
    A. Dumbbells (what weight?)
    B. Resistance bands
    C. Yoga mat
    D. Treadmill / Elliptical
    E. Barbell + plates
    F. Pull-up bar
    G. No equipment

Q18. What are your outdoor exercise conditions?
    A. Park/track nearby (within 5 min walk)
    B. Have facilities, but need commute
    C. No suitable facilities nearby
```

### Primary Goals

```
Q19. What is your PRIMARY fitness goal?
    A. Fat loss / Weight loss
    B. Muscle building / Hypertrophy
    C. Maintenance / General health
    D. Sports performance
    E. Postpartum recovery
    F. Rehabilitation

Q20. Any secondary goals? (Multiple choice)
    A. Glute shaping
    B. Cardiovascular improvement
    C. Flexibility
    D. Strength
    E. Posture correction
```

---

## Group 4: Lifestyle & Habits (Optional but Recommended)

### Sleep & Recovery

```
Q21. What time do you usually go to bed and wake up?
    → Bedtime: ____:____
    → Wake time: ____:____

Q22. Average sleep duration per night?
    A. <6 hours
    B. 6-7 hours
    C. 7-8 hours
    D. >8 hours

Q23. Sleep quality self-rating (1-10 scale)?
    → 1: Very poor, difficulty falling/staying asleep
    → 10: Excellent, fall asleep easily, sleep through night

Q24. Do you have any sleep issues? (Multiple choice)
    A. Difficulty falling asleep (>30 min)
    B. Easy to wake, light sleep
    C. Early waking, can't fall back asleep
    D. None
```

### Stress & Work

```
Q25. What is your work type?
    A. Sedentary (desk job)
    B. Light activity (some walking)
    C. Moderate activity (regular movement)
    D. Heavy physical labor

Q26. How would you rate your stress level (1-10 scale)?
    → 1: Very low, relaxed lifestyle
    → 10: Very high, often overwhelmed

Q27. How do you usually manage stress?
    A. Exercise
    B. Meditation / Breathing
    C. Social activities
    D. Entertainment (TV, games)
    E. Other: ____________
```

### Dietary Habits

```
Q28. What is your diet type?
    A. Omnivore (eat everything)
    B. Pescatarian (fish OK, no meat)
    C. Vegetarian (no meat/fish)
    D. Vegan (no animal products)

Q29. How many meals per day?
    A. 1-2 meals
    B. 3 meals
    C. 4-5 meals (including snacks)

Q30. Do you cook at home or eat out more?
    A. Mostly cook at home
    B. Mix of both
    C. Mostly eat out / order in

Q31. Alcohol consumption per week?
    A. None
    B. Occasional (1-2 drinks/week)
    C. Moderate (3-7 drinks/week)
    D. Frequent (>7 drinks/week)
```

---

## Group 5: Fitness Baseline Testing (Optional)

**Note:** This group can be skipped and completed later.

### Cardiovascular Endurance

```
Q32. 5km Run/Walk Test (if able):
    Time: ____ minutes
    Average heart rate (if available): ____ bpm

If unable to run 5km:
    - 1 mile walk time: ____ minutes
    - Or: 3-minute step test heart rate recovery: ____ bpm
```

### Upper Body Strength

```
Q33. Push-up Test:
    Standard push-ups (male): ____ reps
    OR Knee push-ups (female/beginners): ____ reps
```

### Lower Body Strength

```
Q34. Bodyweight Squat Test (60 seconds):
    ____ reps
```

### Core Strength

```
Q35. Plank Test:
    ____ seconds
```

### Flexibility

```
Q36. Sit and Reach Test:
    ____ cm (positive = beyond toes, negative = before toes)
```

---

## Profiling Completion Output

**After all groups completed:**

```
🎉 Profiling Complete!

═══════════════════════════════════════════════════

📋 Your Profile Summary

Nickname: {nickname}
Gender: {gender}
Age: {age}
Height: {height} cm
Weight: {weight} kg
BMI: {bmi} ({interpretation})

🎯 Goals
Primary: {primary_goal}
Secondary: {secondary_goals}

📅 Training Plan
Frequency: {weekly_days} days/week
Duration: {duration} minutes/session
Equipment: {equipment_list}

⚠️ Health Considerations
{medications/allergies/limitations summary}

═══════════════════════════════════════════════════

✅ Profile saved!

Next Steps:
1. Coach Alex will create your first week's training plan
2. Dr. Mei will calculate your nutrition targets
3. Recommended: Complete TCM constitution identification (optional, but recommended)

Ready to start your first week's training?
```

---

## Data Storage Operations

### Profile data saved to:
- `data/json/profile.json` - Basic profile
- `data/json/profile_health_history.json` - Health history
- `data/json/profile_fitness_baseline.json` - Fitness baseline (if completed)

---

*HealthFit v3.0.1 | Western Profiling Flow (Complete Version) | Last Updated: 2026-03-18*
