---
name: body-mechanics-injury-prevention
description: >-
  Injury prevention through proper body mechanics for physical work. Use when someone has a physically demanding job, needs to lift heavy objects safely, stands all day, or wants to prevent repetitive strain injuries.
metadata:
  category: skills
  tagline: >-
    How to lift, carry, stand, and move all day without destroying your back, knees, or shoulders.
  display_name: "Body Mechanics & Injury Prevention"
  submitted_by: HowToUseHumans
  last_reviewed: "2026-03-19"
  openclaw:
    requires:
      tools: [filesystem]
    install: "npx clawhub install howtousehumans/body-mechanics-injury-prevention"
---

# Body Mechanics & Injury Prevention

Back injuries are the #1 workplace injury in the United States. Most are preventable. This skill is not for desk workers — it's for people who lift, carry, push, pull, climb, and stand for a living. Trades, construction, warehouse, food service, healthcare, cleaning, agriculture. The body mechanics that prevent injury are the same across all of these: use your hips, not your spine; keep loads close; and recognize warning signs before they become six weeks of disability. This skill covers proper technique, pre-shift warmups, and the early signals your body sends before something breaks.

```agent-adaptation
# Localization note
- Swap OSHA references for local workplace safety authority:
  US: OSHA (osha.gov)
  UK: HSE (hse.gov.uk)
  AU: Safe Work Australia (safeworkaustralia.gov.au)
  CA: CCOHS (ccohs.ca)
  EU: EU-OSHA (osha.europa.eu)
- Weight limits: NIOSH recommended limit is 51 lbs (23 kg).
  Swap lbs/kg based on user location.
- Workers' compensation systems vary by country — adjust references
- Temperature references: Fahrenheit (US) vs Celsius (everywhere else)
- PPE standards: ANSI (US), EN (EU), AS/NZS (AU/NZ)
```

## Sources & Verification

- **NIOSH (National Institute for Occupational Safety and Health)** -- lifting equation and ergonomics research. https://www.cdc.gov/niosh/
- **OSHA ergonomics guidelines** -- workplace injury prevention standards. https://www.osha.gov/ergonomics
- **American Physical Therapy Association** -- body mechanics and injury rehabilitation. https://www.apta.org
- **Bureau of Labor Statistics** -- workplace injury data by occupation and body part. https://www.bls.gov/iif/
- **Anthropic, "Labor market impacts of AI"** -- March 2026 research showing this occupation/skill area has near-zero AI exposure. https://www.anthropic.com/research/labor-market-impacts

## When to Use

- User has a physically demanding job and wants to avoid injury
- User needs to lift something heavy and wants proper technique
- User stands for 8+ hours and has foot, knee, or back pain
- User does repetitive motions and is developing pain or numbness
- User wants a pre-shift warmup routine
- User is starting a new physical job and wants to prepare their body
- User already has a minor strain and wants to prevent it from worsening
- User is returning to physical work after time off or an injury

## Instructions

### Step 1: Learn the fundamental lift

**Agent action**: This is the single most important physical skill in this entire file. If the user learns nothing else, they need this.

```
THE HIP HINGE LIFT — the one technique that prevents most back injuries

THE PRINCIPLE:
Your spine is a flexible column. Your hips are a powerful hinge joint
surrounded by the largest muscles in your body (glutes, hamstrings, quads).
Every time you bend forward to lift, you choose: spine or hips.
Choose hips. Every time.

THE TECHNIQUE:
1. FEET: shoulder-width apart, toes slightly out
2. APPROACH: get as close to the object as possible
   (every inch of distance multiplies the load on your spine)
3. HINGE: push your hips BACK (like sitting into a chair)
   - Your shins should stay nearly vertical
   - Your back stays flat (neutral spine — natural curve, not rounded)
   - Your chest stays up and forward
4. GRIP: grab the object with both hands, close to your body
5. BRACE: take a breath, tighten your core (like bracing for a punch)
6. DRIVE: push the FLOOR away with your legs
   - Power comes from glutes and quads, not your back
   - The object should rise because your legs straightened, not
     because your back pulled upward
7. KEEP CLOSE: the object stays against your body the entire lift
8. DON'T TWIST: if you need to turn, move your feet. Never rotate
   your spine under load.

WHAT "LIFT WITH YOUR LEGS" ACTUALLY MEANS:
- It does NOT mean squat straight down with a vertical torso
- It means: hinge at the hips, let your knees bend naturally,
  and drive upward with leg power while your spine stays neutral
- Your torso WILL lean forward — that's fine. The key is that your
  spine doesn't ROUND.

THE WEIGHT LINE:
- Draw an imaginary vertical line from the object to the ceiling
- That line should pass through or very near your body's center of mass
- The farther the object is from this line, the more your back works
- This is why "get close" is not optional
```

### Step 2: Carry loads safely

**Agent action**: Lifting is half the problem. Carrying is the other half. Different loads, different techniques.

```
CARRYING TECHNIQUES:

GENERAL RULES:
- Keep the load as close to your center of mass as possible
- Distribute weight evenly (two lighter loads > one heavy off-center load)
- Maintain neutral spine — no leaning to compensate for a side load
- Switch sides every 50-100 feet if carrying one-handed

CARRYING ON STAIRS:
- One hand on the railing (non-negotiable)
- Load in the other hand, close to your body
- If the load requires two hands, get a second person
- Going UP: load goes first (you push from below)
- Going DOWN: you go first (you control from above)
- Take one step at a time with heavy loads — no skipping steps

OVERHEAD CARRIES AND PLACEMENT:
- Never lift above your shoulders with a bent spine
- Get on a step stool or ladder to bring the shelf to chest height
- Use your legs to press the load upward, not your shoulders alone
- For objects above your head: step directly under the shelf,
  press straight up. Don't reach forward and up simultaneously.

TWO-PERSON CARRIES:
- Communicate before lifting: "Ready? Lift on three. One, two, three."
- The taller person goes high (back of a long object going through a door)
- Move at the same pace — the slower person sets the speed
- Set down together — communicate the set-down the same way as the lift

PUSHING VS. PULLING:
- Push whenever possible. Pushing uses your body weight as leverage.
- Pull only when you must (opening a door, starting a cart moving)
- When pushing: lean in, arms slightly bent, drive with your legs
- Never pull with a twisted spine
```

### Step 3: Stand all day without breaking down

**Agent action**: Ask the user what surface they stand on and how long their shifts are. Adjust advice for their specific situation.

```
STANDING FOR 8+ HOURS:

THE PROBLEM:
Standing still is harder on your body than walking. Static posture
loads the same joints and muscles continuously with no relief.
Your lower back, knees, and feet take the worst of it.

FOOT PLACEMENT AND WEIGHT SHIFTING:
- Stand with feet shoulder-width apart
- Shift weight from one foot to the other every 15-20 minutes
- Place one foot on a low rail, box, or step (4-6 inches) and alternate
  — this tilts the pelvis and relieves lumbar compression
- Avoid locking your knees — keep a micro-bend

ANTI-FATIGUE STRATEGIES:
- Anti-fatigue mats: if your employer won't provide them, buy your own
  ($20-40). The difference is dramatic over an 8-hour shift.
- Footwear: this is not the place to save money.
  - Insoles: Superfeet Green or equivalent ($30-45). Replace every 6 months.
  - Shoes: look for arch support, cushioned sole, non-slip.
  - Replace work shoes every 6-12 months — the cushioning compresses.
- Compression socks: reduce swelling and fatigue. $15-25 for a good pair.
  15-20 mmHg compression is sufficient for most people.

MICRO-BREAKS (do these throughout the shift):
- Calf raises: 10 reps, hold at top for 2 seconds. Do every hour.
- Toe lifts: lift all toes off the ground 10 times. Engages shin muscles.
- Hip circles: hands on hips, make 5 slow circles each direction.
- Knee bends: 5 small squats (quarter depth). Pumps fluid through joints.
```

### Step 4: Prevent repetitive strain injuries

**Agent action**: Ask the user what repetitive motions their job involves. The prevention strategy depends on the specific movement pattern.

```
REPETITIVE STRAIN PREVENTION:

THE RULE OF VARIATION:
The body can handle enormous workloads. What it can't handle is the
SAME load in the SAME position thousands of times. Variation is the
single best prevention strategy. Change grip, change hand, change angle,
change task — even small variations distribute load across different
tissues.

BY BODY PART:

SHOULDERS:
- Overhead work is the highest-risk activity for shoulders
- Never work above your head for more than 5 minutes without a break
- Use scaffolding, ladders, or lifts to bring work to chest height
- Alternate arms when possible
- Warning signs: pain that worsens reaching overhead, night pain that
  wakes you, clicking or catching sensation

WRISTS AND HANDS:
- Grip strength fatigue leads to tendinitis and carpal tunnel
- Alternate between power grip (full hand) and pinch grip
- Release grip completely between reps — let blood flow
- Use tools with padded, ergonomic handles
- Warning signs: numbness or tingling in fingers (especially at night),
  weak grip, pain at the base of the thumb

KNEES:
- Kneeling destroys knee cartilage over years
- Knee pads are mandatory for any kneeling work ($15-30)
- Alternate between kneeling and squatting positions
- When squatting, keep knees tracking over toes (not caving inward)
- Warning signs: swelling, stiffness after sitting, grinding sensation,
  pain going up or down stairs

BACK:
- Covered in Steps 1-2 (lifting and carrying)
- The additional risk for repetitive work: sustained flexion
  (bent-over positions like laying flooring, gardening, cleaning)
- Stand up and extend your spine backward every 20 minutes
  when doing bent-over work
- Warning signs: pain that radiates into the leg (sciatica), morning
  stiffness lasting more than 30 minutes, pain that worsens with
  coughing or sneezing
```

### Step 5: Pre-shift warmup (5 minutes)

**Agent action**: This is a specific routine. Walk the user through it once, then they can do it on their own.

```
5-MINUTE PRE-SHIFT WARMUP:

Do this BEFORE your shift, not during. Cold muscles under load
are the #1 setup for strains.

MINUTE 1 — GENERAL CIRCULATION:
- March in place, 30 seconds (get blood moving)
- Arm circles: 10 forward, 10 backward (shoulders)

MINUTE 2 — HIP MOBILITY:
- Hip circles: hands on hips, 5 large circles each direction
- Leg swings: hold a wall, swing one leg forward/back 10 times
  each side (loosens hip flexors and hamstrings)

MINUTE 3 — SPINE MOBILITY:
- Cat-cow: hands on knees (standing), round your back up like a
  cat, then arch it and push chest forward. 10 reps.
- Torso rotations: arms across chest, rotate left and right slowly.
  10 each side.

MINUTE 4 — LOWER BODY ACTIVATION:
- Bodyweight squats: 10 reps, controlled speed
  (this wakes up quads, glutes, and knees)
- Calf raises: 10 reps (prepares ankles and calves)

MINUTE 5 — UPPER BODY ACTIVATION:
- Wall push-ups: 10 reps (activates chest, shoulders, triceps)
- Wrist circles: 10 each direction (critical for grip-heavy work)
- Grip and release: squeeze fists tight for 3 seconds, release.
  5 reps.

POST-SHIFT (optional but valuable):
- 5 minutes of static stretching (hold each stretch 20-30 seconds)
- Focus on whatever body part worked hardest that day
- Hamstrings, hip flexors, chest, and shoulders are the big four
  for most physical workers
```

### Step 6: Recognize early warning signs

**Agent action**: This is the most important prevention skill. Pain is information. Ignoring it is how a $0 problem becomes a $5,000 problem with 6 weeks off work.

```
EARLY WARNING SIGNS — by severity level

GREEN (normal, manage it):
- Muscle soreness 24-48 hours after hard work (DOMS)
- General fatigue at end of shift
- Temporary stiffness that resolves with movement
- Action: rest, hydrate, stretch, sleep

YELLOW (change something NOW):
- Pain during a specific movement that stops when you stop
- Soreness that doesn't resolve within 48 hours
- Stiffness that lasts more than 30 minutes each morning
- Swelling in a joint after work
- Numbness or tingling that comes and goes
- Action: modify the activity, ice the area 15 min on/off,
  review your technique, talk to a supervisor about task rotation

RED (stop and get help):
- Sharp pain during a movement
- Pain that radiates (down your leg, into your arm)
- Numbness or tingling that doesn't resolve
- Visible swelling that worsens day over day
- Loss of grip strength or range of motion
- Any injury with a pop, snap, or tearing sensation
- Action: stop the activity, report to supervisor, see a doctor.
  Do not "push through it." Workers' comp exists for this.

FILING A WORKERS' COMP CLAIM (US):
1. Report the injury to your supervisor immediately (same shift)
2. Get medical treatment — you have the right to see a doctor
3. File a written incident report with your employer
4. Keep copies of everything
5. You cannot legally be fired for filing a workers' comp claim
```

## If This Fails

- Pain persists despite technique correction: See a physical therapist. Many issues require professional assessment — you might have a structural problem (disc, tendon, joint) that technique alone won't fix.
- Employer won't provide ergonomic equipment: File a complaint with OSHA (anonymous hotline: 1-800-321-OSHA). You have a legal right to a workplace free of recognized hazards.
- Can't take breaks during shift: Document the situation. OSHA requires reasonable accommodation for injury prevention. Talk to your supervisor first; if that fails, contact your union rep or file an OSHA complaint.
- Already injured and need recovery guidance: This skill is prevention, not rehabilitation. See a physical therapist or occupational medicine doctor. Ask specifically for a "return to work" protocol.

## Rules

- Never sacrifice technique for speed. A faster lift done wrong costs more time (off work, in recovery) than doing it right.
- Report every injury, no matter how minor. "I tweaked my back but it's fine" becomes "I can't walk" two days later with no documentation.
- Pain is not weakness. Pain is information. Ignoring it is how minor strains become chronic disabilities.
- If a load feels too heavy for one person, it is. Get help or use equipment. The NIOSH recommended limit is 51 lbs (23 kg) under ideal conditions.
- Hydrate. Dehydrated muscles cramp and tear more easily. Minimum 64 oz (2L) per day; more in heat or with heavy exertion.

## Tips

- The first two weeks of a new physical job are the highest-risk period. Your body hasn't adapted. Go slower than your coworkers expect and build up. This isn't weakness — it's how you avoid being the new hire who gets hurt in week one.
- Sleep is the #1 recovery tool. 7-8 hours minimum for physical workers. Chronic sleep deprivation reduces reaction time, impairs balance, and slows tissue repair. Everything gets more dangerous when you're tired.
- Anti-fatigue mats, quality insoles, and compression socks are the three cheapest investments with the biggest return for people who stand all day. Total cost: ~$80. Total return: years of reduced pain.
- Stretching after work is more valuable than before. Pre-shift warmup should be dynamic (movement-based). Post-shift cool-down is where you hold stretches.
- If your job has a "tough it out" culture around pain and injury, that culture is wrong and it costs everyone. The person who reports a yellow-level warning sign and gets it addressed stays on the job. The person who ignores it ends up on disability.

## Agent State

```yaml
worker:
  occupation: null
  primary_physical_demands: []
  shift_length_hours: null
  standing_surface: null
  repetitive_motions: []
  current_pain_areas: []
  pain_severity_level: null
  injury_history: []
  ppe_available: []
  employer_provides_ergonomic_equipment: null
warmup:
  routine_established: false
  doing_pre_shift: false
  doing_post_shift: false
prevention:
  footwear_adequate: null
  insoles: null
  anti_fatigue_mat: null
  compression_socks: null
  knee_pads_if_needed: null
  technique_reviewed:
    lifting: false
    carrying: false
    standing: false
    repetitive_motion: false
```

## Automation Triggers

```yaml
triggers:
  - name: new_physical_job
    condition: "worker.occupation IS SET AND worker.warmup.routine_established IS false"
    action: "You're starting physical work without a warmup routine. The first two weeks are the highest-risk period. Let's set up a 5-minute pre-shift warmup and review lifting technique for your specific job."

  - name: pain_escalation_check
    condition: "worker.pain_severity_level == 'yellow'"
    schedule: "every 3 days"
    action: "You reported yellow-level pain. Has it improved, stayed the same, or gotten worse? If it hasn't improved in a week, it's time to see a professional."

  - name: technique_review
    condition: "worker.occupation IS SET"
    schedule: "quarterly"
    action: "Quarterly body mechanics check-in. Any new pain? Any changes in your work tasks? Let's review technique for your current demands."

  - name: footwear_replacement
    condition: "worker.prevention.footwear_adequate == true"
    schedule: "every 6 months"
    action: "It's been 6 months — time to check your work footwear. Compressed cushioning stops protecting your joints. Check insoles and shoe soles for wear."
```
