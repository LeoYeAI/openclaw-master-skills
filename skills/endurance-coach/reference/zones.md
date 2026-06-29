# Training Zones & Field Testing

Professional coaching requires accurate training zones derived from field tests, not arbitrary percentages of max HR.

## Lactate Threshold Heart Rate (LTHR) Zones

LTHR is the heart rate at lactate threshold—the intensity you could sustain for approximately 60 minutes in a race. It's more accurate than max HR for prescribing training.

### Running LTHR Zones (Friel 7-Zone System)

| Zone | Name          | % of LTHR | Purpose                                | Feel                               |
| ---- | ------------- | --------- | -------------------------------------- | ---------------------------------- |
| 1    | Recovery      | < 81%     | Active recovery, warm-up/cool-down     | Very easy, could talk indefinitely |
| 2    | Aerobic       | 81-89%    | Aerobic base building, fat oxidation   | Easy, full conversations           |
| 3    | Tempo         | 90-93%    | Muscular endurance, aerobic capacity   | Moderate, sentences only           |
| 4    | Sub-threshold | 94-99%    | Lactate tolerance, threshold extension | Hard, few words at a time          |
| 5a   | Threshold     | 100-102%  | Lactate threshold improvement          | Very hard, race effort for 60min   |
| 5b   | VO2max        | 103-106%  | VO2max development                     | Extremely hard, 3-8min max         |
| 5c   | Anaerobic     | > 106%    | Neuromuscular power, speed             | Max effort, < 3min                 |

### Cycling LTHR/Power Zones

| Zone | Name          | % of LTHR | % of FTP | Purpose             |
| ---- | ------------- | --------- | -------- | ------------------- |
| 1    | Recovery      | < 81%     | < 55%    | Active recovery     |
| 2    | Aerobic       | 81-89%    | 56-75%   | Endurance base      |
| 3    | Tempo         | 90-93%    | 76-90%   | Muscular endurance  |
| 4    | Sub-threshold | 94-99%    | 91-99%   | Threshold extension |
| 5a   | Threshold     | 100-102%  | 100-105% | FTP improvement     |
| 5b   | VO2max        | 103-106%  | 106-120% | VO2max intervals    |
| 5c   | Anaerobic     | > 106%    | > 120%   | Neuromuscular power |

### Swimming Zones (CSS-based)

| Zone | Name      | Pace Relative to CSS | Purpose               |
| ---- | --------- | -------------------- | --------------------- |
| 1    | Recovery  | CSS + 15-20 sec/100m | Warm-up, cool-down    |
| 2    | Aerobic   | CSS + 8-12 sec/100m  | Aerobic endurance     |
| 3    | Tempo     | CSS + 3-6 sec/100m   | Lactate tolerance     |
| 4    | Threshold | CSS pace             | Threshold development |
| 5    | VO2max    | CSS - 3-5 sec/100m   | VO2max intervals      |

---

## Field Testing Protocols

### Run: 30-Minute Threshold Test

1. Warm up 15 minutes easy (Zone 1-2)
2. Run 30 minutes at the hardest sustainable pace (simulate race effort)
3. Record average HR for the entire 30 minutes = LTHR
4. Cool down 10 minutes easy
5. Average pace = approximate lactate threshold pace

_Note: Some coaches use final 20 minutes of a 30-min test to exclude early pacing errors._

### Bike: 20-Minute FTP Test

1. Warm up 20 minutes including 3x1min high-cadence spin-ups
2. Ride 20 minutes at maximum sustainable power
3. Average power × 0.95 = FTP
4. Average HR = approximate cycling LTHR
5. Cool down 10-15 minutes

_Alternative: 2x8 minute test with 10min recovery; average power × 0.90 = FTP_

### Swim: Critical Swim Speed (CSS) Test

1. Warm up 400m easy with drills
2. Swim 400m time trial (all-out, record time)
3. Rest 10 minutes (active recovery)
4. Swim 200m time trial (all-out, record time)
5. CSS = (400m distance - 200m distance) / (400m time - 200m time)

_Example: 400m in 6:40 (400 sec), 200m in 3:00 (180 sec)_
_CSS = 200m / 220 sec = 0.909 m/sec = 1:50/100m_

### When to Retest

- Every 6-8 weeks during base/build phases
- After recovery weeks (when fresh)
- If perceived effort no longer matches prescribed zones

---

## Running Pace Zones (VDOT / Jack Daniels)

For athletes with known race times:

| Zone | Name       | Description                  | How to Determine                                  |
| ---- | ---------- | ---------------------------- | ------------------------------------------------- |
| E    | Easy       | Daily running, long runs     | 59-74% VO2max; 1:00-1:30/km slower than threshold |
| M    | Marathon   | Marathon race pace           | 75-84% VO2max; sustainable for 2-4 hours          |
| T    | Threshold  | Tempo runs, cruise intervals | 83-88% VO2max; ~60min race pace                   |
| I    | Interval   | VO2max development           | 95-100% VO2max; 3-5min repeats                    |
| R    | Repetition | Speed, neuromuscular         | > 100% VO2max; short reps with full recovery      |

**Pace Estimation from Threshold:**

- Easy pace: Threshold + 50-70 sec/km
- Marathon pace: Threshold + 15-25 sec/km
- Interval pace: Threshold - 15-20 sec/km
- Repetition pace: Threshold - 25-35 sec/km

---

## Power-Based Training (Cycling)

When power data is available, use power zones exclusively—they're more accurate than HR which lags and drifts.

| Workout Type | Zone             | Duration             | Recovery | Weekly Frequency |
| ------------ | ---------------- | -------------------- | -------- | ---------------- |
| Endurance    | 2                | 1-5 hours            | N/A      | 2-4x             |
| Tempo        | 3                | 20-60 min continuous | N/A      | 1-2x             |
| Sweet Spot   | 3-4 (88-93% FTP) | 2x20-30 min          | 5-10 min | 1-2x             |
| Threshold    | 5a               | 2-4 x 8-15 min       | 5-8 min  | 1x               |
| VO2max       | 5b               | 4-6 x 3-5 min        | 3-5 min  | 1x               |
| Anaerobic    | 5c               | 6-10 x 30sec-2min    | 2-4 min  | 0-1x             |

---

## Auto-Calculation in Compact Plans (v2.0)

In the v2.0 compact plan format, you only need to specify threshold values. The plan expander automatically calculates all zone ranges using the standard percentages documented above.

### Specifying Zones

```yaml
# In your compact plan YAML
athlete:
  zones:
    hr:
      lthr: 165 # Auto-calculates HR zones
    power:
      ftp: 250 # Auto-calculates power zones
    swim:
      css: "1:45" # Auto-calculates swim zones
```

### What Gets Calculated

**From LTHR (165 bpm example):**

- Zone 1 (Recovery): < 134 bpm (< 81%)
- Zone 2 (Aerobic): 134-147 bpm (81-89%)
- Zone 3 (Tempo): 148-154 bpm (90-93%)
- Zone 4 (Sub-threshold): 155-163 bpm (94-99%)
- Zone 5a (Threshold): 165-168 bpm (100-102%)
- Zone 5b (VO2max): 170-175 bpm (103-106%)
- Zone 5c (Anaerobic): > 175 bpm (> 106%)

**From FTP (250W example):**

- Zone 1: < 138W (< 55%)
- Zone 2: 140-188W (56-75%)
- Zone 3: 190-225W (76-90%)
- Zone 4: 228-248W (91-99%)
- Zone 5a: 250-263W (100-105%)
- Zone 5b: 265-300W (106-120%)
- Zone 5c: > 300W (> 120%)

**From CSS (1:45/100m example):**

- Zone 1: 2:00-2:05/100m (CSS + 15-20s)
- Zone 2: 1:53-1:57/100m (CSS + 8-12s)
- Zone 3: 1:48-1:51/100m (CSS + 3-6s)
- Zone 4: 1:45/100m (CSS)
- Zone 5: 1:40-1:42/100m (CSS - 3-5s)

### Field Testing Still Required

**Auto-calculation does NOT replace field testing.** The calculated zones are only as accurate as the threshold values you provide.

Athletes should perform field tests (see protocols above) to establish accurate LTHR, FTP, and CSS values. Include validation workouts in the first 1-2 weeks of any plan when working with estimated or manual data.

### Expanding to See Calculated Zones

To see the expanded zones, use:

```bash
npx -y endurance-coach@latest expand plan.yaml --verbose
```

This shows the full expanded plan including all calculated zone ranges
