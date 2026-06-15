# Storage Schema

> **Purpose:** Define HealthFit data storage architecture and specifications  
> **Last Updated:** 2026-03-17

---

## Storage Architecture Overview

```
HealthFit Data Storage
│
├── JSON Files (Structured Data)
│   ├── profile.json — Basic physiological data profile
│   ├── profile_health_history.json — Health history
│   ├── profile_fitness_baseline.json — Fitness baseline
│   ├── private_sexual_health.json — Sexual health private data
│   ├── tcm_profile.json — TCM constitution profile
│   └── daily/ — Daily comprehensive logs
│
├── TXT Files (Text Records)
│   ├── workout_log.txt — Workout training logs
│   ├── nutrition_log.txt — Diet records logs
│   ├── glossary_western.txt — Western terminology database
│   ├── glossary_tcm.txt — TCM terminology database
│   └── achievements.txt — Achievement milestone records
│
└── SQLite Database (Query Optimization)
    └── healthfit.db
        ├── workouts — Workout records table
        ├── nutrition_entries — Diet records table
        ├── metrics_daily — Daily body metrics table
        ├── pr_records — Personal records table
        ├── weekly_summaries — Weekly statistics cache
        └── monthly_summaries — Monthly statistics cache
```

---

## JSON Schema Definitions

### 1. profile.json (Basic Physiological Data)

```json
{
  "created_at": "2026-03-17",
  "updated_at": "2026-03-17",
  "nickname": "User Nickname",
  "gender": "male",
  "age": 28,
  "height_cm": 175,
  "weight_kg": 70.5,
  "body_fat_pct": 18.5,
  "waist_cm": 82,
  "hip_cm": 96,
  "bmi": 23.0,
  "bmr": 1780,
  "tdee": 2490,
  "activity_level": "moderate",
  "primary_goal": "fat_loss",
  "secondary_goals": ["glute_shape", "cardio"],
  "target_weight_kg": 65,
  "goal_deadline": "2026-09-16",
  "has_gym": true,
  "equipment": ["dumbbells", "resistance_bands"],
  "weekly_workout_days": 4,
  "session_duration_min": 60,
  "preferred_time": "evening",
  "diet_type": "omnivore",
  "food_allergies": [],
  "alcohol_weekly": "occasional",
  "work_type": "sedentary",
  "stress_level": 6,
  "sleep_target_hours": 7.5
}
```

### 2. profile_health_history.json (Health History)

```json
{
  "medications": [
    {
      "name": "Medication Name",
      "category": "Antihypertensive",
      "dosage": "10mg/day",
      "start_date": "2025-01-01",
      "current_status": "ongoing",
      "purpose": "Blood pressure control"
    }
  ],
  "surgeries": [
    {
      "name": "Surgery Name",
      "date": "2024-06-15",
      "type": "Minimally invasive",
      "recovery_status": "Fully recovered"
    }
  ],
  "chronic_conditions": [
    {
      "name": "Condition Name",
      "diagnosed_date": "2023-01-01",
      "current_status": "Under control",
      "medications": ["Medication 1", "Medication 2"]
    }
  ]
}
```

### 3. profile_fitness_baseline.json (Fitness Baseline)

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

### 4. private_sexual_health.json (Sexual Health Private Data)

**Note:** This file is stored independently, excluded from backup/export by default, requires secondary confirmation to access.

```json
{
  "enabled": true,
  "created_at": "2026-03-17",
  "gender_specific": {
    "male": {
      "frequency": "2-3 times/week",
      "quality_rating": 7,
      "concerns": []
    },
    "female": {
      "cycle_tracking": true,
      "last_period_start": "2026-03-01",
      "cycle_length_days": 28
    }
  },
  "notes": "Optional user notes"
}
```

### 5. tcm_profile.json (TCM Constitution Profile)

```json
{
  "identified_at": "2026-03-17",
  "primary_constitution": "yang_deficiency",
  "secondary_constitution": "qi_deficiency",
  "tongue_records": [
    {
      "date": "2026-03-17",
      "body_color": "pale",
      "body_shape": "swollen_with_tooth_marks",
      "coating_color": "white",
      "coating_texture": "greasy",
      "moisture": "wet",
      "notes": "User reports feeling cold this week",
      "dr_chen_assessment": "Typical Yang Deficiency + Qi Deficiency tongue"
    }
  ],
  "wellness_plan": {
    "dietary_therapy": "Warm and tonify Yang Qi",
    "exercise": "Tai Chi, Baduanjin, walking in sunshine",
    "acupoints": ["Guanyuan (CV4)", "Mingmen (GV4)"]
  }
}
```

### 6. daily/YYYY-MM-DD.json (Daily Comprehensive Logs)

```json
{
  "date": "2026-03-17",
  "workout": {
    "type": "running",
    "duration_min": 32,
    "distance_km": 5,
    "rpe": 6,
    "notes": "Felt good today"
  },
  "nutrition": {
    "calories": 1800,
    "protein_g": 120,
    "carbs_g": 180,
    "fat_g": 60,
    "compliance": "good"
  },
  "metrics": {
    "weight_kg": 70.2,
    "sleep_hours": 7,
    "sleep_quality": 7,
    "energy_level": 7,
    "stress_level": 5
  },
  "tongue": {
    "observed": true,
    "body_color": "pale_red",
    "coating": "thin_white"
  }
}
```

---

## TXT File Formats

### workout_log.txt

**Format:** One line per workout, chronological order

```
2026-03-17 | Running | 5km | 32min | Pace 6'24" | RPE 6
2026-03-16 | Strength | Upper Body | 45min | 5 exercises | RPE 7
2026-03-15 | Rest | Active Recovery | Walking 30min
```

### nutrition_log.txt

**Format:** One line per meal, chronological order

```
2026-03-17 | Lunch | Chicken breast 200g, Broccoli 150g, Brown rice 1 bowl | 595 kcal
2026-03-17 | Breakfast | Eggs 2, Oatmeal 50g, Milk 200ml | 450 kcal
```

### glossary_western.txt

**Format:** `#Number | Term | English | Definition | Related Role`

See: `data/txt/glossary_western.txt` (28 terms)

### glossary_tcm.txt

**Format:** `#Number | Term | Pinyin | English | Related Constitution/Application`

See: `data/txt/glossary_tcm.txt` (20 terms)

### achievements.txt

**Format:** One line per achievement, chronological order

```
2026-03-17 | First 5km | Completed first 5km run in 32 minutes
2026-03-10 | 7-Day Streak | Completed 7 consecutive days of training
```

---

## SQLite Database Schema

### workouts Table

```sql
CREATE TABLE workouts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    exercise_name TEXT NOT NULL,
    sets INTEGER,
    reps INTEGER,
    weight_kg REAL,
    duration_min INTEGER,
    distance_km REAL,
    rpe INTEGER,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### nutrition_entries Table

```sql
CREATE TABLE nutrition_entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    meal_type TEXT NOT NULL,
    food_name TEXT NOT NULL,
    calories INTEGER,
    protein_g REAL,
    carbs_g REAL,
    fat_g REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### metrics_daily Table

```sql
CREATE TABLE metrics_daily (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL UNIQUE,
    weight_kg REAL,
    body_fat_pct REAL,
    waist_cm REAL,
    hip_cm REAL,
    resting_hr INTEGER,
    sleep_hours REAL,
    sleep_quality INTEGER,
    energy_level INTEGER,
    stress_level INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### pr_records Table

```sql
CREATE TABLE pr_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    exercise_name TEXT NOT NULL,
    pr_type TEXT NOT NULL,
    value REAL NOT NULL,
    unit TEXT NOT NULL,
    achieved_date TEXT NOT NULL,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### weekly_summaries Table

```sql
CREATE TABLE weekly_summaries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    week_start TEXT NOT NULL UNIQUE,
    week_end TEXT NOT NULL,
    total_workouts INTEGER,
    total_duration_min INTEGER,
    avg_calories INTEGER,
    avg_protein_g REAL,
    avg_sleep_hours REAL,
    weight_change_kg REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### monthly_summaries Table

```sql
CREATE TABLE monthly_summaries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    month TEXT NOT NULL UNIQUE,
    period_start TEXT,
    period_end TEXT,
    total_workouts INTEGER,
    total_duration_min INTEGER,
    avg_weight_kg REAL,
    weight_change_kg REAL,
    pr_count INTEGER,
    workout_adherence_pct REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Index Optimization

```sql
CREATE INDEX IF NOT EXISTS idx_workouts_date ON workouts(date);
CREATE INDEX IF NOT EXISTS idx_nutrition_date ON nutrition_entries(date);
CREATE INDEX IF NOT EXISTS idx_metrics_date ON metrics_daily(date);
CREATE INDEX IF NOT EXISTS idx_pr_exercise ON pr_records(exercise_name);
```

---

## User Selfie Photo Storage Scheme

**If user chooses to photograph exercise movements for AI correction:**

1. **Storage Location:** Recommended to store in user private directory (e.g., `data/private_photos/`), not skill directory
2. **Encryption Scheme:** Can use base64 encoding + password protection, or call system encryption API
3. **Access Control:** Read only when user explicitly authorizes, clean up timely after use
4. **Backup Strategy:** Excluded from backup by default, user can manually choose whether to include
5. **Current Status:** ⚠️ v3.1 plan feature, current version requires manual upload to exercise_images directory

**Implementation Example (Pseudocode):**
```python
# User selfie photo storage recommendation
photo_path = Path(__file__).parent.parent / "data" / "private_photos" / f"{date}_{exercise}.jpg"
# Recommendation: Use encryption library (e.g., cryptography) to encrypt photos
# Or: Save only base64 encoding of photo to JSON, original photo not stored locally
```

---

*HealthFit v3.0.1 | Storage Schema | Last Updated: 2026-03-17*
