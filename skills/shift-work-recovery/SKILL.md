---
name: shift-work-recovery
description: >-
  Sleep and recovery protocols specifically for shift workers. Use when someone works nights, rotating shifts, doubles, or irregular schedules and is struggling with sleep, energy, health, or mental clarity.
metadata:
  category: mind
  tagline: >-
    Manage your sleep, energy, and sanity on nights, doubles, split shifts, and rotating schedules — because your body doesn't read your work calendar.
  display_name: "Shift Work Sleep & Recovery"
  submitted_by: HowToUseHumans
  last_reviewed: "2026-03-19"
  openclaw:
    requires:
      tools: [filesystem]
    install: "npx clawhub install shift-work-recovery"
---

# Shift Work Sleep & Recovery

Your body runs on a 24-hour clock that doesn't care what shift you drew this week. If you work nights, rotating schedules, doubles, or split shifts, you're fighting your own biology every day — and the generic "sleep hygiene" advice written for 9-to-5 office workers is useless to you. This skill covers circadian rhythm management, strategic napping, light exposure timing, meal scheduling, and recovery protocols designed for food service, healthcare support, protective services, transportation, and manufacturing workers who keep the world running on hours nobody else wants.

```agent-adaptation
# Localization note — shift work regulations and health resources vary by jurisdiction.
- Maximum shift lengths and mandatory rest periods vary:
  US: FLSA has no federal limit on hours for adults; state laws vary. Healthcare
  and transportation have specific federal limits (FMCSA, nurse staffing laws).
  EU: Working Time Directive caps average at 48 hours/week with 11-hour rest between shifts.
  UK: Same as EU Working Time Regulations (retained post-Brexit).
  Australia: National Employment Standards; most awards specify minimum breaks.
- Swap occupational health resources:
  US: NIOSH (cdc.gov/niosh), OSHA
  UK: NHS occupational health, HSE (hse.gov.uk)
  AU: Safe Work Australia, state WorkCover agencies
  CA: CCOHS (ccohs.ca)
- Melatonin availability varies: over-the-counter in US/CA/AU, prescription-only in UK/EU.
  Adjust supplement recommendations accordingly.
- Sleep clinic access: In universal healthcare systems (UK, AU, CA), referral through GP.
  In US, check insurance coverage or community health centers.
```

## Sources & Verification

- **National Sleep Foundation** -- Shift work sleep disorder resources and sleep duration recommendations. https://www.sleepfoundation.org
- **CDC NIOSH** -- Work schedule and fatigue guidelines for employers and workers. https://www.cdc.gov/niosh/topics/workschedules/
- **American Academy of Sleep Medicine** -- Clinical guidelines on shift work disorder diagnosis and treatment. https://aasm.org
- **"Internal Time" by Till Roenneberg** -- Chronobiology research on circadian rhythms and social jet lag. Munich Chronotype Questionnaire reference.
- **OSHA Fatigue Resources** -- Workplace fatigue risk factors and mitigation strategies. https://www.osha.gov/fatigue
- **Anthropic, "Labor market impacts of AI"** -- March 2026 research showing this occupation/skill area has near-zero AI exposure. https://www.anthropic.com/research/labor-market-impacts

## When to Use

- Someone works night shifts and can't sleep during the day
- User is on a rotating schedule and feels permanently jet-lagged
- Working doubles or extended shifts and running on fumes
- Sleep deprivation is causing mood problems, GI issues, or impaired thinking
- User's relationships are suffering because their schedule doesn't align with anyone else's
- Wants to know if what they're experiencing is normal shift work fatigue or something clinical

## Instructions

### Step 1: Understand What You're Fighting

**Agent action**: Assess user's specific shift pattern and identify the primary circadian disruption.

```
YOUR CIRCADIAN CLOCK — THE SHORT VERSION
- Your body has a master clock in the brain (suprachiasmatic nucleus) that runs on ~24 hours.
- It takes cues primarily from LIGHT. Light = awake signal. Darkness = sleep signal.
- This clock controls: sleep drive, body temperature, cortisol, melatonin, digestion, immune
  function, mood, cognitive performance.
- When you work nights, your clock says "awake" while your schedule says "sleep" — and
  your clock almost always wins.
- Rotating shifts are worse than permanent nights because your clock never fully adjusts.
- It takes approximately 1 day per hour of shift change for partial adjustment.
  A 12-hour night shift flip? Your body needs 7-12 days. Most rotations don't give you that.

THIS IS NOT A WILLPOWER PROBLEM. It's a biology problem.
```

### Step 2: Control Light Exposure

**Agent action**: Create a light exposure schedule based on user's specific shift times.

Light is the single most powerful tool for shifting your circadian clock. Use it strategically.

```
LIGHT EXPOSURE PROTOCOL

NIGHT SHIFT (e.g., 7pm-7am):
- First half of shift: Maximize bright light exposure. Overhead fluorescents ON.
  If possible, use a 10,000 lux light therapy lamp at your workstation.
- Second half of shift: Begin dimming. Reduce overhead lights if possible.
- Commute home: Wear wraparound sunglasses. Yes, even if it looks weird.
  Morning sunlight is the strongest "wake up" signal and will destroy your
  ability to fall asleep when you get home.
- Bedroom: COMPLETE darkness. Not "pretty dark." BLACK.

BLACKOUT SETUP ($15-30):
- Option 1 (Renters): Blackout curtains with Velcro strips on frame edges ($20-30).
  Brand example: Deconovo thermal blackout curtains + 3M Command Velcro strips.
- Option 2 (Cheapest): Heavy-duty black trash bags + painter's tape on windows ($5).
  Ugly but effective. No shame in it.
- Option 3: Blackout roller shades with side channels ($30-50 for permanent install).
- Sleep mask: As backup or addition. Contoured (Manta or Alaska Bear brand) so it
  doesn't press on eyelids. $10-15.
- Cover ALL light sources in bedroom: Alarm clock, power strips, smoke detector LED.
  Use electrical tape.

ROTATING SHIFTS:
- On day-shift weeks: Get morning sunlight within 30 minutes of waking.
- On night-shift weeks: Follow the night shift protocol above.
- On transition days: Wear sunglasses for the first 3 hours after your last night shift
  to help your clock start swinging back.
```

### Step 3: Time Your Melatonin

**Agent action**: Calculate melatonin timing based on user's target sleep window.

```
MELATONIN PROTOCOL
- Dose: 0.5mg. NOT the 5mg or 10mg pills at the drugstore. Those are massively
  overdosed and cause grogginess. Research supports 0.3-0.5mg as the effective dose.
  You may need to buy 1mg tablets and cut them in half, or find 0.5mg formulations
  (Natrol makes one).
- Timing: 5 hours before your desired sleep onset.
  Example: Want to sleep at 8am after a night shift? Take melatonin at 3am.
- Consistency: Take it at the same time every shift day. Your clock responds to consistency.
- Duration: Use for the first 2-3 weeks of a new schedule, then taper off.
  Melatonin is a clock-shifting signal, not a sleeping pill.
- Not a replacement for: Blackout curtains, light management, or proper sleep environment.
  It's one tool, not the whole toolbox.

NOTE: Melatonin is OTC in the US, Canada, and Australia. In the UK and most of the EU,
it requires a prescription. If prescription-only in your country, discuss with your GP
and mention shift work as the reason.
```

### Step 4: Master Strategic Napping

**Agent action**: Recommend nap timing and duration for user's shift pattern.

```
NAP RULES FOR SHIFT WORKERS
- 20-minute power nap: Light sleep only. Set alarm for 25 minutes (5 min to fall asleep).
  Boosts alertness for 2-3 hours. Best mid-shift if allowed, or pre-shift.
- 90-minute full cycle: One complete sleep cycle. Wake feeling refreshed, not groggy.
  Best on days off or when you have a longer break.
- NOTHING IN BETWEEN: 30-60 minute naps put you into deep sleep then rip you out.
  You'll feel worse than before. 20 or 90. Those are your numbers.

PRE-SHIFT NAP:
- Before a night shift: Nap 90 minutes, ending 1-2 hours before your shift starts.
  This is the single best fatigue countermeasure available.

CAFFEINE + NAP COMBO (the "nappuccino"):
- Drink coffee immediately before a 20-minute nap.
- Caffeine takes 20-25 minutes to hit your bloodstream.
- You wake up with both the nap refresh AND the caffeine kick.
- Sounds counterintuitive. Works extremely well. Research-backed.

ON DAYS OFF:
- Do NOT try to flip entirely back to a day schedule if you're on permanent nights.
  It destroys any circadian adjustment you've built.
- Compromise: Sleep until noon or 1pm on days off instead of staying up all night.
  Social life during afternoon/evening hours.
```

### Step 5: Manage Caffeine and Meals

**Agent action**: Calculate caffeine cutoff time and meal timing for user's shift.

```
CAFFEINE PROTOCOL
- Cutoff: Minimum 6 hours before intended sleep. 8 hours is better.
  Night shift sleeping at 8am? Last caffeine at 2am maximum.
- Front-load: Drink coffee at the START of your shift, not the end.
- Half-life reminder: Caffeine's half-life is 5-6 hours. That 2am coffee still has
  50% potency at 7am when you're trying to sleep.
- If you "need" caffeine in the last 3 hours of your shift, you need a nap instead.

MEAL TIMING
- Your gut has its own circadian clock. Eating during your biological night (roughly
  midnight-6am) causes more GI distress than the same food during the day.
- Night shift strategy:
  - Eat your main meal BEFORE your shift (6-7pm for a 7pm start).
  - Light snacks during shift: nuts, cheese, crackers, fruit, yogurt.
  - Avoid heavy, greasy, or spicy food between midnight and 6am.
  - Small meal after shift if hungry, but don't force it.
- Rotating shifts: Eat meals at consistent times relative to your WAKE time,
  not the clock on the wall. Wake + 1 hour = breakfast, regardless of actual time.
- Common trap: Eating a huge meal after a night shift, then trying to sleep.
  Your body will choose digestion over sleep. Eat light or wait.
```

### Step 6: Exercise Without Wrecking Your Sleep

**Agent action**: Recommend exercise timing relative to user's shift schedule.

```
EXERCISE TIMING
- BEFORE shift: 20-30 minutes of moderate exercise (brisk walk, bodyweight circuit)
  1-2 hours before clocking in. Boosts alertness for hours.
- AFTER shift: AVOID intense exercise. It raises core body temperature and cortisol,
  both of which delay sleep onset by 1-2 hours.
- If after-shift is your only option: Gentle stretching or yoga. Nothing that makes
  you sweat heavily.
- Days off: Exercise whenever works. Morning is ideal for circadian alignment on
  day-schedule days.
- Minimum effective dose: 20 minutes, 3x per week. You don't need a gym membership.
  Walking counts. Pushups in your living room count.
```

### Step 7: Protect Your Relationships

**Agent action**: Provide communication templates for partners and family members.

```
THE SCHEDULE MISMATCH PROBLEM
When you work nights or rotating shifts, your free time rarely overlaps with anyone
else's. This strains relationships, parenting, friendships, and social connection.

COMMUNICATION TEMPLATE FOR PARTNER/FAMILY:
"I need to sleep from [time] to [time]. During that window, I need the house
to be as quiet as possible and for you to handle [specific tasks]. I know this
is hard on you too. Let's find [specific overlap time] as our protected time
together every [frequency]."

PRACTICAL STRATEGIES:
- Establish one protected shared meal per day, even if it's "your breakfast,
  their dinner."
- Use a shared calendar that shows your shifts, sleep blocks, AND available time.
  Family members can't respect what they can't see.
- Have the "I'm not ignoring you, I'm unconscious" conversation proactively.
- Schedule date time the way you schedule shifts — it won't happen spontaneously.
- For parents: Quality over quantity. 30 focused minutes beats 3 hours of
  exhausted presence.
```

### Step 8: Recognize When It's Clinical

**Agent action**: Screen for shift work disorder symptoms and recommend professional help if indicated.

```
SHIFT WORK DISORDER — SELF-CHECK
If you answer "yes" to 3+ of these, talk to a doctor:
- You've worked shifts for 3+ months and sleep problems persist despite trying
  blackout curtains, melatonin, and consistent scheduling.
- You fall asleep unintentionally during your shift.
- You sleep less than 5 hours per day on average, despite having 7-8 hours available.
- You have persistent GI problems (nausea, heartburn, irregular bowel) that correlate
  with your shift schedule.
- Your mood has significantly worsened since starting shift work (constant irritability,
  hopelessness, loss of interest in things you used to enjoy).
- You've had a near-miss or accident due to fatigue at work or while driving.

WHERE TO GET HELP:
- Primary care doctor: Can diagnose shift work disorder, prescribe modafinil (for
  wakefulness) or short-term sleep aids. Ask specifically about shift work disorder.
- Sleep specialist/clinic: For persistent cases. May do a sleep study.
- EAP (Employee Assistance Program): Free, confidential, through your employer.
  Most shift workers don't know this exists. Ask HR for the number.
```

## If This Fails

- Still can't sleep after blackout + melatonin + light management: See a sleep specialist. You may have shift work disorder requiring medication (modafinil for wake, short-term sleep aids for sleep). This is a medical condition, not a weakness.
- Rotating schedule is too fast to ever adjust: Talk to your supervisor about slower rotations (3-4 weeks per shift instead of weekly). Research shows forward-rotating schedules (days -> evenings -> nights) are easier on the body than backward rotation. If your employer won't change the schedule, document your fatigue and look at the workplace-injury-rights skill for safety reporting.
- Can't function despite all strategies: Some people's chronotypes are fundamentally incompatible with night work. This isn't a moral failing. If you've tried everything for 6+ months with no improvement, changing to a day schedule may be the only real solution.
- Relationship strain is severe: Couples counseling, specifically requesting someone experienced with shift-worker families. Many EAPs cover this.

## Rules

- Never drive drowsy. Drowsy driving kills as many people as drunk driving. If you're nodding off on the commute home, pull over and nap 20 minutes. No job is worth dying on the highway.
- Alcohol is not a sleep aid. It causes fragmented sleep and worsens circadian disruption. One beer to wind down is a slippery slope when you're exhausted and your clock is broken.
- Sleeping pills (Ambien, Benadryl) are a last resort, not a routine. They don't produce restorative sleep. Use behavioral strategies first.
- Protect your sleep window like it's your shift. Tell people. Silence your phone. Close the door. Sleep is not optional — it's how your body repairs.
- Do not let anyone shame you for sleeping during the day. You're not lazy. You're on a different schedule.

## Tips

- A fan or white noise machine ($15-25) masks daytime noise (neighbors, traffic, lawn mowers) better than earplugs for most people. Use both if needed.
- Keep your bedroom cold: 65-68F (18-20C). Your body needs a temperature drop to initiate sleep.
- Blue-light blocking glasses ($10-15, amber or red lens) for the last 2-3 hours of a night shift can help with melatonin onset. Not a substitute for the full light protocol, but a useful addition.
- If you commute by car, keep sunglasses in the vehicle specifically for the morning drive home after nights.
- Anchor sleep: If you're on rotating schedules, keep a consistent 4-hour sleep block at the same time every day (e.g., 3am-7am), regardless of which shift you're on. Fill remaining sleep needs with naps. This gives your clock one stable reference point.
- Meal prep on days off. You will not cook healthy food at 3am when you're exhausted. Having pre-made meals is the difference between eating real food and eating vending machine garbage.

## Agent State

```yaml
shift_work_session:
  shift_pattern: null
  shift_times: null
  current_sleep_hours: null
  primary_complaint: null
  blackout_setup_complete: false
  melatonin_timing_calculated: false
  caffeine_cutoff_set: false
  clinical_screening_done: false
```

## Automation Triggers

```yaml
triggers:
  - name: shift_change_adjustment
    condition: "user reports upcoming schedule change or rotation"
    schedule: "on_demand"
    action: "Recalculate light exposure timing, melatonin timing, caffeine cutoff, and meal schedule for new shift pattern"
  - name: fatigue_screening
    condition: "user reports persistent sleep problems lasting more than 4 weeks"
    schedule: "on_demand"
    action: "Run shift work disorder self-check and recommend professional evaluation if indicated"
  - name: seasonal_light_adjustment
    condition: "daylight savings change or significant seasonal shift"
    schedule: "biannual_march_november"
    action: "Remind user to adjust light exposure protocol and blackout setup for new daylight patterns"
```
