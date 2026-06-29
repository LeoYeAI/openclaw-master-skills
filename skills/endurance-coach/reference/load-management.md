# Training Load Management

Professional coaches quantify training stress to manage fatigue, prevent overtraining, and peak for races.

## Training Stress Score (TSS)

TSS measures the physiological cost of a workout. For cycling with power:

```
TSS = (Duration in seconds × NP × IF) / (FTP × 3600) × 100

Where:
- NP = Normalized Power (accounts for variability)
- IF = Intensity Factor (NP / FTP)
```

### TSS Guidelines by Workout Type

| Workout               | Typical TSS | Recovery Needed |
| --------------------- | ----------- | --------------- |
| Easy 1hr ride         | 40-50       | Same day OK     |
| 2hr endurance ride    | 80-100      | 24 hours        |
| Hard interval session | 70-90       | 24-48 hours     |
| 4hr long ride         | 150-200     | 48-72 hours     |
| Century (100mi)       | 250-350     | 3-5 days        |
| Ironman bike          | 300-400     | 1-2 weeks       |

### Running TSS (rTSS)

Estimated from pace and HR. Use Strava's suffer_score as a proxy:

- suffer_score ≈ rTSS for most athletes
- Compare suffer_score per hour across sessions to gauge relative intensity

### Swim TSS (sTSS)

Use duration × intensity factor:

- Easy swim: 25-30 TSS/hour
- Moderate swim: 40-50 TSS/hour
- Hard intervals: 60-70 TSS/hour

---

## Chronic Training Load (CTL) - "Fitness"

CTL is the rolling 42-day weighted average of daily TSS. It represents accumulated fitness.

### CTL Ramp Rate Guidelines

| Athlete Level | Max CTL Increase/Week | Notes                            |
| ------------- | --------------------- | -------------------------------- |
| Beginner      | 3-5 TSS/day           | Conservative to prevent injury   |
| Intermediate  | 5-7 TSS/day           | Standard progression             |
| Advanced      | 7-10 TSS/day          | Aggressive; requires monitoring  |
| Pro           | 8-12 TSS/day          | With careful recovery management |

_A CTL ramp of 7/week means adding ~50 TSS/week to your average weekly load._

---

## Acute Training Load (ATL) - "Fatigue"

ATL is the rolling 7-day weighted average of daily TSS. It represents recent fatigue.

---

## Training Stress Balance (TSB) - "Form"

```
TSB = CTL - ATL
```

| TSB Range  | State        | Implication                                |
| ---------- | ------------ | ------------------------------------------ |
| +15 to +25 | Fresh/peaked | Race ready, may lose fitness if maintained |
| +5 to +15  | Rested       | Good for quality sessions, minor events    |
| -10 to +5  | Neutral      | Normal training state                      |
| -10 to -30 | Fatigued     | Building load, need recovery soon          |
| < -30      | Overreaching | High injury/burnout risk, reduce load      |

### Race Day TSB Targets

| Event       | Target TSB | Taper Length |
| ----------- | ---------- | ------------ |
| Sprint Tri  | 0 to +10   | 5-7 days     |
| Olympic Tri | +5 to +15  | 10-14 days   |
| 70.3        | +10 to +20 | 14-18 days   |
| Ironman     | +15 to +25 | 21-28 days   |
| Marathon    | +10 to +20 | 14-21 days   |

---

## Weekly TSS Targets by Phase

| Phase         | % of Peak TSS | Focus                                  |
| ------------- | ------------- | -------------------------------------- |
| Base (early)  | 60-70%        | Building volume                        |
| Base (late)   | 75-85%        | Volume + introducing intensity         |
| Build         | 90-100%       | Peak volume, race-specific work        |
| Peak          | 85-95%        | Maintaining fitness, sharpening        |
| Taper         | 40-60%        | Reducing volume, maintaining intensity |
| Recovery week | 50-60%        | Every 3-4 weeks                        |

---

## Recovery Monitoring

### Heart Rate-Based Indicators

**Resting Heart Rate (RHR):**

- Measure every morning before getting up
- RHR elevated 5-10+ bpm = accumulated fatigue
- Sustained elevation over 3+ days = consider recovery day/week
- Sudden drop below baseline = potential illness onset

**Heart Rate Variability (HRV):**

- Higher HRV = better recovered
- Lower HRV = stressed/fatigued
- HRV 10%+ below baseline = reduce intensity
- Track 7-day rolling average, not daily swings

### Subjective Indicators (1-5 scale)

| Metric          | Questions                        |
| --------------- | -------------------------------- |
| Sleep quality   | How restful? Wake during night?  |
| Energy          | How do you feel getting up?      |
| Muscle soreness | General or localized?            |
| Mood            | Motivated or dreading training?  |
| Appetite        | Normal, elevated, or suppressed? |

**Warning patterns:**

- 2+ low scores for 3+ days = back off
- Sleep + mood both low = high burnout risk

### Recovery Week Structure

Every 3-4 weeks:

| Day | Prescription                                    |
| --- | ----------------------------------------------- |
| 1   | Complete rest or 30min Zone 1                   |
| 2   | 45-60min Zone 2, single sport                   |
| 3   | 30-45min Zone 2, different sport                |
| 4   | Complete rest                                   |
| 5   | 45-60min Zone 2 with 3-4 short accelerations    |
| 6   | Light session, re-assess readiness              |
| 7   | If feeling good, ease back into normal training |

**Volume reduction:** 40-50% of normal week
**Intensity reduction:** No Zone 4+ work
