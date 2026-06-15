# Fitness Baseline Test Guide

> **Purpose:** Establish user's initial fitness level  
> **Testing Frequency:** Once at profiling, then every 4-6 weeks  
> **Last Updated:** 2026-03-17

---

## Testing Overview

Fitness baseline tests help:
- Understand current fitness level
- Set reasonable training goals
- Track training progress
- Adjust training plans

---

## Test Items

### 1. Cardiovascular Endurance

**5km Run/Walk Test**

**Procedure:**
1. Warm up for 5-10 minutes
2. Complete 5km as fast as possible (run or walk)
3. Record time and average heart rate (if available)
4. Cool down with walking and stretching

**Standards (Male, 20-39 years):**
- Excellent: <25 minutes
- Good: 25-30 minutes
- Average: 30-35 minutes
- Below Average: >35 minutes

**Standards (Female, 20-39 years):**
- Excellent: <28 minutes
- Good: 28-33 minutes
- Average: 33-38 minutes
- Below Average: >38 minutes

---

### 2. Upper Body Strength

**Push-up Test**

**Procedure:**
1. Standard position (male): Hands shoulder-width apart, toes on ground
2. Modified position (female/beginners): Knees on ground
3. Complete as many reps as possible with proper form
4. Record total reps

**Standards (Male, 20-39 years):**
- Excellent: >40 reps
- Good: 30-40 reps
- Average: 20-29 reps
- Below Average: <20 reps

**Standards (Female, 20-39 years):**
- Excellent: >25 reps (modified)
- Good: 15-25 reps (modified)
- Average: 10-14 reps (modified)
- Below Average: <10 reps (modified)

---

### 3. Lower Body Strength

**Squat Test (Bodyweight)**

**Procedure:**
1. Stand with feet shoulder-width apart
2. Squat until thighs parallel to ground (or as low as comfortable)
3. Complete as many reps as possible in 60 seconds
4. Record total reps

**Standards:**
- Excellent: >50 reps
- Good: 40-50 reps
- Average: 30-39 reps
- Below Average: <30 reps

---

### 4. Core Strength

**Plank Test**

**Procedure:**
1. Start in forearm plank position
2. Maintain straight line from head to heels
3. Hold as long as possible with proper form
4. Record time in seconds

**Standards (Male, 20-39 years):**
- Excellent: >120 seconds
- Good: 90-120 seconds
- Average: 60-89 seconds
- Below Average: <60 seconds

**Standards (Female, 20-39 years):**
- Excellent: >90 seconds
- Good: 60-90 seconds
- Average: 45-59 seconds
- Below Average: <45 seconds

---

### 5. Flexibility

**Sit and Reach Test**

**Procedure:**
1. Sit on floor with legs extended
2. Reach forward as far as possible
3. Measure distance from toes (positive = beyond toes, negative = before toes)
4. Record best of 3 attempts

**Standards:**
- Excellent: >15 cm beyond toes
- Good: 0-15 cm beyond toes
- Average: At toes to -5 cm
- Below Average: <-5 cm (cannot reach toes)

---

## Recording Results

**Save to:** `data/json/profile_fitness_baseline.json`

**Format:**
```json
{
  "test_date": "2026-03-17",
  "tests": {
    "cardio_5km": {
      "value": 32,
      "unit": "minutes",
      "level": "average"
    },
    "pushups": {
      "value": 25,
      "unit": "reps",
      "level": "good"
    },
    "squats": {
      "value": 35,
      "unit": "reps",
      "level": "average"
    },
    "plank": {
      "value": 75,
      "unit": "seconds",
      "level": "good"
    },
    "flexibility": {
      "value": -3,
      "unit": "cm",
      "level": "below_average"
    }
  },
  "overall_assessment": "Average fitness level with room for improvement in flexibility"
}
```

---

## Retesting Schedule

**Recommended frequency:** Every 4-6 weeks

**Why retest:**
- Track training progress
- Adjust training plans
- Set new goals
- Stay motivated

**Between tests:**
- Focus on training, not daily fluctuations
- Trust the process
- Consistency over perfection

---

*HealthFit v3.0.1 | Fitness Baseline Test Guide*
