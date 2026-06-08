---
name: mental-reset-suite
description: >-
  Two-module mental health protocol covering burnout recovery and sleep overhaul. Module A: structured burnout recovery using the Maslach framework — identify your stage, install boundaries, rebuild energy. Module B: evidence-based sleep improvement in 14 days — sleep anchoring, wind-down rituals, caffeine timing, environment. Use when someone is burned out, exhausted, can't sleep, or needs a complete mental reset.
metadata:
  category: mind
  tagline: >-
    Module A: recover from burnout in 6 weeks using the Maslach framework. Module B: fix your sleep in 14 days using evidence-based protocols. Two problems, one skill.
  display_name: "Mental Reset Suite"
  submitted_by: HowToUseHumans
  last_reviewed: "2026-03-18"
  openclaw:
    requires:
      tools: [calendar, filesystem]
    install: "npx clawhub install mental-reset-suite"
---

# Mental Reset Suite

Two linked protocols for the two most common mental health problems in post-white-collar survival: burnout and broken sleep. They feed each other — burnout destroys sleep, broken sleep accelerates burnout. Fix them together.

Module A is the flagship burnout protocol based on the Maslach Burnout Inventory framework. Module B is the evidence-based sleep overhaul. Both include agent-driven assessments, tracking, and automation triggers.

## Sources & Verification

**Burnout:**
- Maslach Burnout Inventory: Maslach, C. & Jackson, S.E., *Maslach Burnout Inventory Manual*, 4th ed., Mind Garden, 2016
- Three dimensions of burnout: Maslach, C. & Leiter, M.P., *The Truth About Burnout*, Jossey-Bass, 1997
- Exercise as burnout intervention: Gerber et al., *BMC Research Notes*, 2013 ([DOI: 10.1186/1756-0500-6-78](https://doi.org/10.1186/1756-0500-6-78))
- Lack of control as burnout predictor: Karasek, R., *Administrative Science Quarterly*, 1979
- Burnout and depression comorbidity: Bianchi et al., *Clinical Psychology Review*, 2015
- 988 Suicide & Crisis Lifeline: [988lifeline.org](https://988lifeline.org/) — verified active March 2026
- Open Path Collective: [openpathcollective.org](https://openpathcollective.org) — verified active March 2026
- NAMI Helpline: 1-800-950-NAMI — verified active March 2026

**Sleep:**
- Walker, M., *Why We Sleep*, Scribner, 2017
- American Academy of Sleep Medicine (AASM) Clinical Practice Guidelines for Insomnia. aasm.org
- Edinger et al., "CBT for adults with insomnia," *Sleep*, 2021 ([DOI: 10.5664/jsl.8558](https://doi.org/10.5664/jsl.8558)) — CBT-I outperforms sleep medication long-term
- Czeisler, C.A., "Duration, timing and quality of sleep," *Sleep Health*, 2015 — consistent wake time as the strongest single lever
- Chang et al., "Evening use of light-emitting eReaders negatively affects sleep," *PNAS*, 2015 ([DOI: 10.1073/pnas.1418490112](https://doi.org/10.1073/pnas.1418490112)) — blue light suppresses melatonin
- Drake et al., "Caffeine effects on sleep," *Journal of Clinical Sleep Medicine*, 2013 — caffeine 6 hours before bed cuts sleep by 1 hour
- National Sleep Foundation: sleepfoundation.org — verified active March 2026
- Society of Behavioral Sleep Medicine (CBT-I providers): behavioralsleep.org

## When to Use

**Module A (Burnout) — use when:**
- User says they're burned out, exhausted, or "running on empty"
- Can't stop thinking about work at night
- Feels cynical, detached, or like nothing they do matters
- Dreads Monday starting from Sunday morning
- Physical symptoms: insomnia, headaches, constant fatigue

**Module B (Sleep) — use when:**
- Takes more than 30 minutes to fall asleep most nights
- Wakes multiple times during the night
- Wakes feeling unrefreshed even after 7-8 hours
- Relies on caffeine or willpower to function in the morning
- Wants to reduce reliance on melatonin, alcohol, or sleep aids
- Experiencing regular Sunday-night insomnia

**Both together — use when:**
- Burnout and sleep problems are clearly feeding each other
- User has tried one protocol and hasn't improved
- Starting fresh after a major breakdown or health crisis

---

# MODULE A: BURNOUT RECOVERY

## Instructions

### Step 1: Identify burnout stage

**Agent action**: Administer the assessment interactively — ask each question one at a time, record the score, and calculate totals. Store the scores and burnout stage in agent state.

```
BURNOUT ASSESSMENT (answer 1=never to 5=every day)

EXHAUSTION:
[ ] I feel emotionally drained by my work
[ ] I feel used up at the end of the day
[ ] I dread getting up to face another day
[ ] Working all day is really a strain

CYNICISM:
[ ] I've become more callous toward people since this job
[ ] I don't really care what happens to some people I work with
[ ] I feel like I'm just going through the motions
[ ] I doubt the significance of my work

INEFFICACY:
[ ] I can't deal with problems effectively anymore
[ ] I feel I'm not making a difference
[ ] I've accomplished less than I used to
[ ] I don't feel excited about my achievements

SCORING:
- 12-24: Mild burnout — prevention stage. Focus on boundaries.
- 25-40: Moderate burnout — active recovery needed.
- 41-60: Severe burnout — consider medical leave, therapy, or major life change.
```

### Step 2: Emergency stabilization (Week 1)

Do NOT try to fix everything at once. This week is about stopping the bleeding.

**Agent action**: Set daily evening reminders for the screen cutoff time. Create a "Week 1 Priorities" note with only the user's top 3 must-do items. Schedule a check-in for end of Week 1.

**Sleep protocol:**
- Set a hard stop on screens at 10pm
- No work email after 7pm — delete the app from your phone if you have to
- If you can't sleep, write down every thought for 10 minutes, then close the notebook

**The "absolute minimum" exercise:**
- Identify the 3 things at work that MUST happen this week
- Everything else gets pushed, delegated, or dropped
- Write this and tape it to your monitor: "Good enough is good enough this week."

**One recovery activity per day:**
- Walk outside for 20 minutes (slow walk, not a power walk)
- Call one person you actually like talking to
- Do one thing that has nothing to do with productivity

### Step 3: Boundary installation (Weeks 2-3)

**Agent action**: Help the user customize each script below with their specific names, times, and situations. Save customized scripts to `~/documents/burnout-recovery/boundary-scripts.txt`. Track which boundaries have been set and enforced.

```
BOUNDARY SCRIPTS — copy and use as needed

DECLINING EXTRA WORK:
"I want to do a good job on what I already have. If I take this on,
something else will suffer. Can we talk about what to deprioritize?"

PROTECTING OFF-HOURS:
"I'm offline after [time]. If it's genuinely urgent, text me.
Otherwise I'll see it tomorrow morning."

SAYING NO TO MEETINGS:
"Can I get the summary notes instead? I want to protect my focus
time so I can deliver [specific thing] on time."

PUSHING BACK ON SCOPE:
"I can do A or B this week, not both. Which one matters more?"
```

### Step 4: Energy audit (Week 3-4)

Track every activity for one work week. Mark each as:
- **E** = Energizing (you feel better after)
- **N** = Neutral
- **D** = Draining (you feel worse after)

**Agent action**: Send a daily prompt at end of workday asking the user to rate their activities. Compile the week's data. Identify the top 3 drains and top 3 energizers.

```
ENERGY AUDIT TEMPLATE

PATTERNS TO IDENTIFY:
-> Which tasks drain you most? Can any be delegated?
-> Which people drain you most? Can you reduce contact?
-> When is your best energy? Protect those hours.
-> What energizes you that you've stopped doing?
```

### Step 5: Rebuild meaning (Month 2+)

**Agent action**: Guide the user through these reflection questions over several sessions. Record their answers and surface them during low moments.

Ask yourself:
1. "If money weren't an issue, what would I still want to do?"
2. "What was I doing the last time I felt genuinely proud of my work?"
3. "What part of my work actually helps someone?"

The goal isn't to love every minute. It's to have enough meaning to offset the hard parts.

### Step 6: Decide if the situation can change

After 4-6 weeks of active recovery, ask honestly:
- Are the conditions that caused burnout fixable?
- Is the organization willing to change?
- Have your boundaries been respected?

If no on 2+ of those: this isn't a recovery problem, it's an environment problem. Start planning your exit. See the layoff-72-hours and career-reinvention skills.

## Burnout: If This Fails

1. **Symptoms worsening after 4-6 weeks**: Burnout can coexist with clinical depression. Contact your primary care doctor. Many employers offer free EAP sessions — ask HR.
2. **Can't afford therapy**: Open Path Collective (openpathcollective.org) offers sessions for $30-80. NAMI Helpline: 1-800-950-NAMI for free peer support.
3. **Boundaries not respected**: Document the pattern (dates, requests, responses). This documentation is valuable for escalating to HR or building a case for medical leave.
4. **Considering quitting with nothing lined up**: See the layoff-72-hours skill for financial stabilization first. Build 3+ months of runway before the leap.
5. **Having dark thoughts**: Call or text 988. Burnout can push you to a breaking point — this is a medical situation, not a character flaw.

---

# MODULE B: SLEEP OVERHAUL

## Instructions

### Step 1: Sleep audit

**Agent action**: Ask the user each question below, one at a time. Record answers in agent state. Use the results to generate a personalized protocol.

```
SLEEP AUDIT

1. What time do you currently go to bed? (average)
2. What time do you currently wake up? (average on weekdays)
3. What time do you actually fall asleep after getting into bed?
4. How many times do you wake up during the night?
5. How do you feel within 30 minutes of waking? (1 = exhausted, 5 = alert)
6. Do you use alcohol to help you sleep?
7. Do you use screens (phone, TV, laptop) in bed?
8. What time is your last caffeine most days?
9. Do you nap? If yes, how long and when?
10. Is your bedroom dark? Cool? Quiet?

RED FLAGS:
- Falls asleep in under 5 min: may be chronically sleep-deprived
- Wakes unrefreshed regardless of duration: possible sleep apnea
  (recommend doctor consult)
- Uses alcohol to sleep: address this first
- Last caffeine after 2pm: address in Step 4
```

### Step 2: Set your sleep anchor (do this first, everything else second)

The single most powerful intervention is a consistent wake time — 7 days a week, including weekends.

**Agent action**: Ask "What time must you be awake for work or responsibilities?" Set a daily morning reminder at that time. Track wake time adherence in state.

```
SLEEP ANCHOR RULES:

1. Pick one wake time. Keep it every day, including weekends.
   Variation of more than 30 minutes breaks the system.

2. Do NOT "catch up" on sleep on weekends.
   Weekend sleep debt recovery resets your anchor.

3. Get out of bed within 10 minutes of your alarm.

4. Your body will correct bedtime naturally within 1-2 weeks
   once the anchor is consistent.

WHY IT WORKS:
Sleep drive (adenosine) builds from the moment you wake.
Consistent wake time = consistent sleep drive at the same hour
each night = falling asleep faster and sleeping deeper.
```

### Step 3: Build a 30-minute wind-down ritual

**Agent action**: Help the user build their specific ritual from the options below. Set a daily reminder 35 minutes before their target bedtime.

```
WIND-DOWN RITUAL BUILDER — pick 2-3 from each tier

START (35 min before bed):
[ ] Dim all lights or switch to lamps only
[ ] Stop eating — digestion competes with sleep
[ ] Set out tomorrow's clothes, bag, keys
[ ] Write tomorrow's 3-item priority list

MIDDLE (20 min before bed):
[ ] Take a warm shower or bath (the body temperature drop
    afterward triggers sleep onset)
[ ] Read a physical book or e-ink reader (no backlit screens)
[ ] Do 5 minutes of gentle stretching
[ ] Write a "brain dump" — everything in your head, on paper

FINAL (10 min before bed):
[ ] Phone face-down on charger outside the bedroom
[ ] Drop bedroom temperature to 65-68F / 18-20C if possible
[ ] 4-7-8 breathing: inhale 4s, hold 7s, exhale 8s (x3)
[ ] No clock-checking — turn clocks away
```

### Step 4: Caffeine cutoff calculator

Caffeine has a half-life of 5-7 hours. To have less than 25% caffeine remaining at bedtime, your last caffeine = bedtime minus 12 hours.

```
CAFFEINE CUTOFF EXAMPLES:
  Bedtime 10:30pm → last caffeine by 10:30am
  Bedtime 11:30pm → last caffeine by 11:30am
  Bedtime midnight → last caffeine by noon

HIDDEN CAFFEINE SOURCES:
  - Green tea: 25-45mg per cup
  - Dark chocolate: 12-25mg per ounce
  - "Decaf" coffee: 2-25mg per cup
  - Pre-workout and energy drinks: read the label
  - Some pain relievers (Excedrin): 65mg per tablet
```

### Step 5: Optimize the sleep environment

```
SLEEP ENVIRONMENT CHECKLIST:

DARKNESS (most impactful after timing):
[ ] Blackout curtains or sleep mask
[ ] No LED indicator lights in bedroom (cover with black tape)
[ ] No screen glow at all

TEMPERATURE:
[ ] Bedroom at 65-68F / 18-20C
[ ] Fan, lighter duvet, cotton sheets, open window if you run hot

QUIET (or consistent noise):
[ ] White noise machine or fan
[ ] Earplugs if partner snores

STIMULUS CONTROL (bed is for sleep only):
[ ] No working in bed
[ ] No TV in bed
[ ] No scrolling in bed
[ ] If you can't sleep after 20 minutes: GET UP. Do something
    boring in dim light until sleepy. Return to bed only when sleepy.
    (This is counterintuitive. It works.)
```

### Step 6: Two-week check-in

**Agent action**: After 14 days, re-administer the sleep audit. Compare to baseline.

```
IF NO IMPROVEMENT after 14 days with anchor + environment fixes:
  Consider: sleep apnea screening (home sleep tests often covered
  by insurance), or referral to sleep medicine specialist for CBT-I
  (Cognitive Behavioral Therapy for Insomnia — more effective than
  any sleep medication, no side effects).

CBT-I providers: behavioralsleep.org
```

## Sleep: If This Fails

1. **Waking unrefreshed no matter what**: Ask your doctor about a home sleep study for sleep apnea. This skill cannot address sleep apnea.
2. **Can't stop racing thoughts at night**: This is anxiety driving sleep problems. See the anxiety-emergency skill. Also consider CBT-I.
3. **Using alcohol to sleep**: Alcohol suppresses REM sleep in the second half of the night. You'll fall asleep faster and wake up exhausted. Expect 2-3 nights of worse sleep when removing it.
4. **Tried everything and still struggling**: Ask your doctor about CBT-I. The American College of Physicians recommends it as first-line treatment over medication. Find a provider at behavioralsleep.org.

## Rules

- Never tell someone to "just push through" burnout — it gets worse without intervention
- Always assess burnout severity first — severe cases may need professional support
- Focus on one step at a time, not the whole protocol at once
- Burnout is not a personal failure — it's a response to sustained impossible conditions
- Never recommend prescription sleep medication — this protocol is behavioral
- Always flag waking-unrefreshed + snoring as a potential medical issue
- Set the expectation upfront: sleep improvement takes 7-14 days

## Tips

**Burnout:**
- The biggest predictor of burnout isn't workload — it's lack of control. Focus on what the user CAN control.
- Recovery is not linear. Bad days during recovery are normal.
- Physical exercise is the single most effective burnout intervention. Even a 15-min walk counts.

**Sleep:**
- The most impactful change for most people is wake-time consistency, not bedtime.
- Warm showers work because the body temperature DROP afterward triggers sleep onset, not the warmth.
- Weekend "sleep ins" of even 90 minutes shift your circadian rhythm by the equivalent of mild jet lag.
- Blue light from screens suppresses melatonin for 1-3 hours. The issue is the wavelength, not just brightness.

## Agent State

Persist across sessions:

```yaml
mental_reset:
  burnout:
    assessment_scores:
      exhaustion: null
      cynicism: null
      inefficacy: null
      total: null
      date: null
    assessment_history: []
    burnout_stage: null
    current_week: 0
    recovery_start_date: null
    boundaries_set: []
    boundaries_enforced: []
    energy_audit:
      energizers: []
      drains: []
      completed_days: 0
    meaning_reflections: []
    exit_decision: null
  sleep:
    audit:
      bedtime_current: null
      wake_time_current: null
      sleep_onset_minutes: null
      night_wakings: null
      morning_feel_score: null
      uses_alcohol: null
      uses_screens_in_bed: null
      last_caffeine_time: null
      audit_date: null
    sleep_anchor_time: null
    anchor_adherence_days: 0
    wind_down_ritual: []
    caffeine_cutoff_time: null
    protocol_start_date: null
    checkin_scores: []
    flags:
      possible_sleep_apnea: false
      alcohol_dependency: false
      anxiety_driven: false
```

## Automation Triggers

```yaml
triggers:
  - name: burnout_evening_wind_down
    condition: "burnout.current_week <= 4"
    schedule: "daily at user's chosen cutoff time"
    action: "Gentle reminder: screens off soon. How was today on a 1-5 scale? Log any recovery activity."

  - name: burnout_energy_audit_prompt
    condition: "burnout.current_week >= 3 AND burnout.current_week <= 4 AND burnout.energy_audit.completed_days < 5"
    schedule: "daily at end of workday"
    action: "End of day energy check: What did you do today? Rate each activity E/N/D."

  - name: burnout_weekly_checkin
    condition: "burnout.recovery_start_date IS SET"
    schedule: "weekly on Sunday evening"
    action: "Weekly recovery check-in: How are you feeling compared to last week? Review boundaries set vs enforced."

  - name: burnout_reassessment
    condition: "burnout.current_week >= 6"
    schedule: "once"
    action: "Time for reassessment. Re-administer the burnout assessment and compare to your initial baseline. If scores haven't improved, recommend professional support."

  - name: sleep_morning_anchor
    condition: "sleep.sleep_anchor_time IS SET"
    schedule: "daily at sleep.sleep_anchor_time"
    action: "Time to get up. Keeping this consistent is the most important thing you can do for your sleep. How did last night go? (1-5)"

  - name: sleep_wind_down_start
    condition: "sleep.wind_down_ritual IS SET"
    schedule: "daily 35 minutes before target bedtime"
    action: "Wind-down time. Dim your lights now. Screens off in 25 minutes."

  - name: sleep_two_week_checkin
    condition: "sleep.protocol_start_date IS SET"
    schedule: "14 days after sleep.protocol_start_date"
    action: "Two-week sleep check-in. Let's re-run the sleep audit and compare to your baseline. Ready?"

  - name: depression_flag
    condition: "burnout.assessment_scores.total >= 50 OR (6 weeks elapsed AND scores not improving)"
    action: "Burnout may coexist with depression. Recommend speaking with a mental health professional. Crisis line: call or text 988."
```
