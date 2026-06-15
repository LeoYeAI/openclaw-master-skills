# Athlete Assessment Guide

## Foundation vs Current Form

These are two different things:

| Dimension               | Timeframe           | What It Tells You                                                 |
| ----------------------- | ------------------- | ----------------------------------------------------------------- |
| **Athletic Foundation** | Lifetime / 2+ years | What the athlete is capable of; training history; race experience |
| **Current Form**        | Last 8-12 weeks     | Where they are RIGHT NOW; starting point for the plan             |

**Why this matters**: An athlete who completed an Ironman last year but has barely trained in 10 weeks is NOT the same as a beginner. They have:

- Muscle memory and movement efficiency
- Mental toughness and race experience
- Knowledge of pacing, nutrition, transitions
- A body that has adapted to high training loads before

Their plan should focus on **rebuilding** (faster progression possible) rather than **building from scratch** (conservative progression required).

## Interpreting Foundation vs Form

| Scenario                       | Foundation  | Current Form | Plan Approach                                      |
| ------------------------------ | ----------- | ------------ | -------------------------------------------------- |
| Ironman finisher, 10 weeks off | Very strong | Low          | Rebuild: faster progression OK, body remembers     |
| First-time triathlete          | None        | Moderate     | Build: conservative progression, everything is new |
| Marathoner doing first tri     | Strong run  | Moderate     | Build swim/bike carefully, leverage run strength   |
| Consistent trainer, no races   | Moderate    | Strong       | Peak: maintain and sharpen, add race specificity   |

## Interpreting Strength Signals

| Signal                              | Interpretation                       |
| ----------------------------------- | ------------------------------------ |
| Long sessions at low HR             | Excellent aerobic base in that sport |
| Low suffer_score per minute         | Sport feels easy to them (strength)  |
| High suffer_score per minute        | Sport is hard for them (limiter)     |
| Historical peaks >> recent activity | Dormant fitness, will return quickly |
| No historical data for a sport      | True beginner, needs careful build   |
| Consistent high volume              | Sport they enjoy and prioritize      |

**Limiter identification**: Compare suffer_per_minute and average HR across sports. The sport with highest relative effort for similar durations is the limiter.

## Example Interpretation

_"The athlete's swim data shows 5000m sessions at avg HR 125 with suffer_score of 45. Their runs show 10km at avg HR 165 with suffer_score of 120. Swimming is clearly a strength (low effort, long duration). Running is a limiter (high effort, shorter duration). Even though they haven't swum in 4 months, that fitness will return quickly with a few weeks of swimming. The plan should prioritize run development while maintaining swim fitness with modest volume."_

## Event Requirements Reference

| Event               | Swim  | Bike  | Run  |
| ------------------- | ----- | ----- | ---- |
| Sprint Tri          | 750m  | 20km  | 5km  |
| Olympic Tri         | 1500m | 40km  | 10km |
| 70.3 / Half Ironman | 1900m | 90km  | 21km |
| Full Ironman        | 3800m | 180km | 42km |
| Marathon            | -     | -     | 42km |
| Ultra (50k)         | -     | -     | 50km |

**Gap analysis**: Compare their longest recent/historical sessions against these requirements.

---

## Validating With The Athlete

**IMPORTANT**: Before creating the training plan, always share your assessment and validate it with the athlete.

### What to Ask

1. **Race history / athletic foundation**: _"I see you completed an Ironman in [year] and have [X] years of triathlon history. Does that match your background?"_

2. **Reason for time off**: _"You've had lower training volume recently. Was this due to injury, life circumstances, or something else?"_ (Injury = more conservative; life = faster rebuild OK)

3. **Strengths assessment**: _"Based on your data, swimming appears to be a strength—you've done 5km sessions at low effort. Does that match your perception?"_

4. **Limiter identification**: _"Running shows higher relative effort for shorter distances. Would you say the run is your biggest area for improvement?"_

5. **Dormant fitness**: _"I see you haven't swum in 4 months but had strong swim fitness earlier this year. Do you expect that to come back quickly?"_

6. **Constraints**: _"Any injuries, schedule constraints, upcoming travel, or equipment limitations I should know about?"_

7. **Goals**: _"Do you have a time goal, or is finishing the main focus?"_

8. **Preferences**: _"Are there workouts you love or hate? Sports you'd rather emphasize?"_

9. **Long session scheduling**: _"Which days work best for your long ride and long run? I see from your data you typically do long rides on [day]."_ (Check their historical patterns first—look for rides >2hr and runs >1hr to infer preferred days)

### Inferring Long Session Preferences

Before asking, analyze their Strava data to identify patterns:

```sql
-- Find preferred days for long rides (>90 min)
SELECT
  strftime('%w', start_date) as day_of_week,
  COUNT(*) as count
FROM activities
WHERE sport_type = 'Ride'
  AND moving_time > 5400
GROUP BY day_of_week
ORDER BY count DESC;

-- Find preferred days for long runs (>60 min)
SELECT
  strftime('%w', start_date) as day_of_week,
  COUNT(*) as count
FROM activities
WHERE sport_type IN ('Run', 'Trail Run')
  AND moving_time > 3600
GROUP BY day_of_week
ORDER BY count DESC;
```

Day mapping: 0=Sunday, 1=Monday, ..., 6=Saturday

Use this data to make an informed suggestion: _"I notice you typically do your long rides on Saturday and long runs on Sunday. Should we keep that pattern?"_

### Example Dialogue

```
Based on your Strava data, here's my initial assessment:

**Strengths:**
- Swimming: Your 5000m sessions at HR 125 suggest excellent swim fitness.
  Even though you haven't swum since August, this should return quickly.

**Limiters:**
- Running: Your runs show higher effort (HR 165+) for shorter distances.
  Your longest run is 12km; we'll need to build toward 21km for the 70.3.
- Cycling: Moderate—you're doing 60-80km rides but we'll need to push toward 100km+.

**My recommendation:** Focus training time on run and bike development.
Maintain swim with 2x/week sessions; it doesn't need major building.

Before I create the plan:
1. Does this assessment match how you feel about each sport?
2. Any injuries or constraints I should know about?
3. Do you have a time goal, or is finishing the focus?
```

### Why Validation Matters

- Data can mislead: Low recent volume ≠ lack of ability
- Athletes know their bodies: Prior injuries, what causes burnout, what they enjoy
- Buy-in matters: Athletes follow plans they helped shape
- Context changes everything: A "weak" run might be due to recovering from injury, not lack of fitness

**Never finalize a plan without athlete confirmation of the assessment.**
