# Profiling Mode Selection Guide

> **Estimated Total Time:** 20-30 minutes (including sexual health module)  
> **Question Count:** About 20-25 core questions + optional questions  
> **After Completion:** All four advisors will provide personalized health recommendations

---

## 📋 Profiling Mode Selection (Choose One of Three)

### A. Questionnaire Mode (Recommended ⭐⭐⭐⭐⭐)

**Suitable for:** Users who prefer structured approach and want comprehensive profiling

**Estimated Time:** 20-25 minutes

**Question Count:** About 20-25 core questions, distributed as follows:

| Category | Question Count | Description |
|----------|---------------|-------------|
| 1. Basic Physiological Data | 5-6 | Age, height, weight, body fat, etc. |
| 2. Exercise Habits & Goals | 4-5 | Exercise experience, training frequency, main goals |
| 3. Diet Preferences & Restrictions | 3-4 | Diet type, food allergies, cooking habits |
| 4. Health Status & Medication History | 3-4 | Chronic diseases, current medications |
| 5. Lifestyle | 3-4 | Sleep, stress, work type |
| 6. TCM Constitution Preliminary Screening | 2-3 | Cold/heat sensitivity, fatigue level, etc. |

**Advantages:**
- ✅ Most comprehensive and accurate information
- ✅ Structured for easier subsequent analysis
- ✅ AI can ask targeted follow-up questions

**Response Method:** Each question provides fixed options + free description

---

### B. Chat Mode (Relaxed ⭐⭐⭐⭐)

**Suitable for:** Users who don't like questionnaires, prefer natural conversation

**Estimated Time:** 25-30 minutes

**Flow:**
1. AI guides you to freely describe your health status
2. Extract key information from your description
3. Follow-up confirmation for vague information

**Example:**
> "I'm 28 years old, work in an office, want to lose weight recently, but don't have much exercise experience..."

**Advantages:**
- ✅ Relaxed and natural, no pressure
- ✅ Can narrate at your own pace
- ✅ Suitable for users not good at multiple-choice questions

**Note:** May take slightly longer than questionnaire mode

---

### C. File Upload Mode (Quick ⭐⭐⭐)

**Suitable for:** Users who already have health checkup reports / health profiles / exercise data

**Estimated Time:** 10-15 minutes (preparing files) + 5 minutes (AI reading)

**⚠️ Prerequisites:** Your AI tool must support one of the following capabilities:
- 📄 File upload function (can upload PDF/images/Excel)
- 📸 Image reading capability (can recognize health checkup report photos)
- 📁 Project file reading capability (can read files in workspace)

**Supported File Types:**
| File Type | Examples | Extractable Information |
|-----------|----------|------------------------|
| Health Checkup Report | PDF/Images | Height, weight, blood pressure, blood tests, etc. |
| Fitness APP Export | Excel/CSV | Workout records, weight changes, PR records |
| Past Health Profile | Any format | Medical history, medication history, allergies |
| Diet Records | Screenshots/Documents | Dietary habits, preferences |

**Flow:**
1. Upload files (or place in `data/uploads/` directory)
2. AI automatically reads and extracts information
3. Ask follow-up questions for missing information

**Advantages:**
- ✅ Fastest (when files already exist)
- ✅ Most accurate data (from checkups/instruments)
- ✅ Avoids manual input errors

---

## 💡 Recommendations

| Your Situation | Recommended Mode |
|----------------|------------------|
| First-time profiling, no existing data | A. Questionnaire (most comprehensive) |
| Don't like questionnaires, prefer chatting | B. Chat mode (most relaxed) |
| Just had health checkup, have reports | C. File upload (fastest) |
| Have fitness habits, APP has data | C. File upload + A. Questionnaire supplement |

---

## 🔒 Privacy Module Selection (Important)

HealthFit includes an **optional privacy module** (sexual health records and guidance) for:

**Functions:**
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

## 📝 Question Response Method Explanation

**Each question provides three response methods, user can freely choose:**

### Example: Question 3 — What is your exercise experience?

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

*Last Updated: 2026-03-17 | HealthFit v3.0.1*
