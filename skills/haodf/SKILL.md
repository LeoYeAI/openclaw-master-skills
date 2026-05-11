---
name: haodf
description: Help patients find suitable doctors based on symptoms, specialty, location, and doctor ratings. Use when the user wants to find a doctor, get medical recommendations, or seek healthcare provider information.
---

# Haodf (好大夫)

Help patients find suitable doctors based on symptoms, specialty, location, and doctor ratings.

## Triggers

Activate on: "找医生", "推荐医生", "看什么科", "医院", "专家", "挂号", "病症", doctor search requests.

**Before acting:** Clarify:
- Symptoms or condition
- Location preference (city/district)
- Hospital preference (public vs private, general vs specialized)
- Doctor level preference (resident, attending, chief physician)

## Core Flow

1. **Understand Symptoms** — What are the patient's symptoms or conditions?
2. **Determine Specialty** — Map symptoms to appropriate medical specialty
3. **Filter by Location** — Consider patient's location and travel preference
4. **Evaluate Doctors** — Check ratings, experience, patient reviews
5. **Recommend** — Provide 2-3 doctor options with reasoning

## Specialty Mapping

| Symptoms/Condition | Suggested Specialty |
|-------------------|---------------------|
| Fever, cold, flu | Internal Medicine / General Practice |
| Stomach pain, digestion issues | Gastroenterology |
| Headache, dizziness | Neurology |
| Chest pain, palpitations | Cardiology |
| Skin rash, allergies | Dermatology |
| Bone/joint pain | Orthopedics |
| Children's illness | Pediatrics |
| Women's health | Gynecology |
| Eye problems | Ophthalmology |
| Ear/nose/throat | ENT (Otolaryngology) |
| Dental issues | Dentistry |
| Mental health concerns | Psychiatry / Psychology |

## Doctor Evaluation Criteria

**Essential factors:**
- Specialty match with patient's condition
- Hospital affiliation and reputation
- Years of experience
- Patient ratings and reviews

**Additional considerations:**
- Availability (appointment wait time)
- Consultation fees
- Languages spoken
- Online consultation availability

## Output Format

For each recommended doctor:

**Doctor Name** - Specialty, Hospital
- **Experience:** X years
- **Rating:** ⭐⭐⭐⭐⭐ (X/5 from Y reviews)
- **Expertise:** Key areas of specialization
- **Location:** Hospital address
- **Appointment:** How to book

## Important Notes

⚠️ **Medical Disclaimer:**
- This skill helps find doctors but does NOT provide medical advice
- For emergencies, call 120 or go to nearest ER immediately
- Always consult a licensed physician for diagnosis and treatment
- Online information may be outdated; verify with hospital directly

## Example Interactions

**User:** "我头痛应该看什么科？"
**Response:** 头痛建议先看神经内科。如果伴随视力问题看眼科，外伤引起看神经外科。

**User:** "帮我找北京看胃病好的医生"
**Response:** [推荐消化内科医生列表，包含医院、专长、评价等]

**User:** "孩子发烧了挂什么号？"
**Response:** 建议挂儿科。如果高烧不退或精神萎靡，建议直接去儿童医院急诊。
