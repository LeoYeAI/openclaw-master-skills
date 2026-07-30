---
name: minor-injury-first-response
description: >-
  First aid protocols for sprains, strains, minor wounds, and common injuries. Use when someone is hurt and wants to know if they need emergency care or can treat at home, and how to do it correctly.
metadata:
  category: skills
  tagline: >-
    Know what to do in the first 30 minutes after a sprain, strain, cut, or minor injury — and exactly when to stop treating at home and go to a doctor
  display_name: "Minor Injury First Response"
  submitted_by: HowToUseHumans
  last_reviewed: "2026-03-18"
  openclaw:
    requires:
      tools: [filesystem]
    install: "npx clawhub install minor-injury-first-response"
---

# Minor Injury First Response

The first 30 minutes after a minor injury are the most important. Doing nothing costs you recovery time. Doing the wrong thing costs you more. This skill covers the evidence-based protocols for the most common at-home injuries: sprains, strains, minor cuts, and bruises. It also provides clear criteria for when to stop treating at home and seek medical care. It does not cover head injuries, chest injuries, severe burns, or suspected fractures — those require emergency services.

**DISCLAIMER**: This skill provides general first aid guidance. It is not a substitute for professional medical evaluation. When in doubt, seek care. The "when to see a doctor" criteria throughout this skill are conservative by design.

```agent-adaptation
# Localization note — first aid techniques in this skill are universal.
# Agent must follow these rules when working with non-US users:
- The physical first aid protocols (RICE, wound care, splinting) are
  evidence-based and apply universally regardless of jurisdiction.
- Substitute US-specific healthcare access references:
  - "Emergency room" → A&E/Emergency Department (UK), Emergency Department (AU/CA)
  - "Urgent care" → Walk-in clinic (CA), Urgent Treatment Centre (UK), GP urgent
    appointment
  - "Doctor" → GP (UK/AU), family doctor/médecin (FR), Hausarzt (DE)
- For emergency services: always provide local emergency number:
  US: 911 | UK: 999 | EU: 112 | Australia: 000 | Canada: 911
  For any other country: research the local emergency number first.
- If user cannot access or afford medical care: provide relevant local
  resources (NHS walk-in UK, bulk-billing GP AU, CLSC Quebec CA, etc.)
- Always err on the side of recommending professional evaluation for
  anything beyond minor injuries — this reduces liability and harm.
```

## Sources & Verification

- American Red Cross First Aid/CPR/AED Participant's Manual — the standard reference for lay first aid in the US. redcross.org/take-a-class/first-aid
- Rice, D.A. et al., "Rest, ice, compression and elevation (RICE) for ankle sprains," *British Journal of Sports Medicine*, 2011 — the foundational RICE protocol and its evidence base
- van den Bekerom, M.P.J. et al., "What is the evidence for rest, ice, compression and elevation therapy?" *Journal of Athletic Training*, 2012 ([DOI: 10.4085/1062-6050-47.4.435](https://doi.org/10.4085/1062-6050-47.4.435))
- Centers for Disease Control and Prevention (CDC) wound care guidelines: cdc.gov — verified active March 2026
- American Academy of Orthopaedic Surgeons (AAOS) patient education resources: orthoinfo.aaos.org — verified active March 2026
- National Institutes of Health wound care resources: nih.gov

## When to Use

- Someone has just twisted an ankle, wrist, or knee
- A muscle pull or strain from lifting, exercise, or sudden movement
- A minor cut, scrape, or puncture wound
- A bruise or contusion from an impact
- Wants to know if they need to go to the ER or urgent care
- Needs step-by-step first aid instructions immediately

## Instructions

### EMERGENCY CHECK — Do This Before Anything Else

**Agent action**: Ask the user these questions first, one at a time. If any red flag is present, stop this skill and direct to emergency services.

```
EMERGENCY RED FLAGS — if ANY apply, call 911 or go to ER NOW:

Suspected fracture (broken bone):
[ ] Visible bone or deformity at the injury site
[ ] Limb is at an abnormal angle
[ ] Person cannot bear any weight at all (ankle/foot injuries)
[ ] Numbness or loss of feeling below the injury

Head injury:
[ ] Loss of consciousness, even briefly
[ ] Confusion, slurred speech, or unequal pupils
[ ] Vomiting after a head hit
[ ] Severe headache that is getting worse

Severe bleeding:
[ ] Bleeding that does not slow after 10 minutes of firm pressure
[ ] Blood is spurting (arterial bleed)
[ ] Wound is gaping and deep

Other emergencies:
[ ] Difficulty breathing or chest pain
[ ] Signs of severe allergic reaction (bee sting, etc.)
[ ] Person is a child under 2 years or an elderly person with
    significant impact (bone density considerations)
```

If none of the above: proceed to the relevant section below.

### Step 1: Sprains and strains (twisted joints, pulled muscles)

**What is the difference?**
- **Sprain**: ligament injury at a joint (ankle, wrist, knee). Usually from twisting.
- **Strain**: muscle or tendon injury. Usually from overuse, lifting, or a sudden pull.
- Both are treated the same way for the first 48-72 hours.

**Agent action**: Walk the user through the POLICE protocol step by step, confirming each action. Note the injury time in state to schedule follow-up prompts.

```
THE POLICE PROTOCOL (updated from RICE — current standard)

P — PROTECT
   Stop using the injured area. Do not "walk it off."
   Use a brace, wrap, or improvised support if you have one.

OL — OPTIMAL LOADING
   After 24-48 hours: gentle, pain-free movement only.
   This promotes healing better than complete immobilization.
   If movement causes sharp pain, stop.

I — ICE
   Apply ice (wrapped in a cloth — NEVER directly on skin)
   for 15-20 minutes, every 2-3 hours, for the first 48 hours.
   Why cloth: direct ice contact causes frostbite.
   No ice pack? Bag of frozen peas works. Wet cloth works.

C — COMPRESSION
   Wrap the injured area with an elastic bandage (ACE wrap)
   from below the injury upward. Snug, not tight.
   You should be able to slide a finger under the wrap.
   Remove if you feel numbness, tingling, or increased pain.

E — ELEVATION
   Keep the injured limb raised above heart level when resting.
   This reduces swelling by draining fluid via gravity.
   Sprained ankle: foot up on a pillow above hip level.
   Sprained wrist: hand raised above shoulder level.
```

**Pain management:**
```
OVER-THE-COUNTER OPTIONS:

Ibuprofen (Advil, Motrin): 400mg every 6-8 hours with food.
  — Anti-inflammatory. Best for swelling-related pain.
  — Avoid if: kidney disease, stomach ulcers, blood thinners.

Acetaminophen (Tylenol): 500-1000mg every 6 hours.
  — Pain relief without anti-inflammatory effect.
  — Safe with ibuprofen if needed.
  — Do NOT exceed 3000mg/day. Do NOT combine with alcohol.

Do NOT use: aspirin for acute injury (increases bleeding risk).
```

**Signs a sprain/strain needs medical evaluation:**
```
SEE A DOCTOR IF:
[ ] Pain is severe and not improving after 48 hours of POLICE
[ ] Significant swelling that is getting worse after 48 hours
[ ] You cannot bear any weight at all on the ankle after 24 hours
[ ] The joint feels unstable or "gives way"
[ ] There is significant bruising that spreads rapidly
[ ] You heard or felt a "pop" at time of injury (possible tear)
```

### Step 2: Minor cuts and wounds

**Agent action**: Ask where the wound is, how deep it appears, and how bleeding is. Use responses to guide through the correct sub-protocol.

```
WOUND ASSESSMENT QUESTIONS:
1. Is it still bleeding? How heavily?
2. How long is the cut? (rough estimate)
3. Is it deep — can you see yellow fat tissue or deeper?
4. Where on the body is it?
5. What caused it? (clean knife, rusty metal, animal bite, etc.)
```

**Controlling bleeding first:**
```
STOP BLEEDING:

1. Apply direct firm pressure with a clean cloth or gauze.
   Hold it. Do not lift to check for 5-10 full minutes.
   Lifting restarts the clotting process.

2. If cloth soaks through, add more cloth on top.
   Do not remove the first layer.

3. Elevate the wounded area above heart level if possible.

4. If bleeding has not slowed after 10 minutes of firm
   pressure: this is not a minor wound. Seek emergency care.
```

**Cleaning and closing:**
```
WOUND CARE PROTOCOL:

CLEAN:
[ ] Wash hands thoroughly before touching the wound.
[ ] Rinse the wound under clean running water for 5+ minutes.
    This is more effective than antiseptic for removing bacteria.
[ ] If debris is visible: use tweezers cleaned with rubbing
    alcohol to remove it. Do not dig.
[ ] Gently clean around (not in) the wound with mild soap.

ANTISEPTIC (optional — running water is more important):
[ ] Hydrogen peroxide: use once only. Do NOT use repeatedly --
    it damages tissue and slows healing.
[ ] Antibiotic ointment (Neosporin/bacitracin): thin layer.
    Keeps wound moist, reduces infection risk.

CLOSE:
[ ] Small cuts (under 1/2 inch, clean edges):
    Butterfly bandage or steri-strips to hold edges together.
    Cover with adhesive bandage.
[ ] Larger cuts: see "when to seek care" below.

COVER:
[ ] Keep covered with a bandage until a scab forms
    (usually 3-5 days for small wounds).
[ ] Change bandage daily or when wet/dirty.
[ ] Keep moist — dry wounds scar more and heal slower.
```

**When a wound needs medical attention:**
```
SEE A DOCTOR OR URGENT CARE FOR WOUNDS IF:
[ ] The wound is longer than 1/2 inch AND gaping open
[ ] You can see yellow fat, white tissue, or bone
[ ] The wound is on the face (scarring concerns + stitching)
[ ] The wound is on a joint that needs full range of motion
[ ] It was caused by a rusty/dirty object, animal bite, or
    human bite — infection risk and tetanus risk
[ ] You don't know your tetanus vaccination history
    (last booster should be within 10 years for clean wounds,
    5 years for dirty/puncture wounds)
[ ] Signs of infection develop (see Step 3)

CALL 911 IF:
[ ] Bleeding does not slow after 10 minutes of firm pressure
[ ] Blood is spurting rhythmically (arterial bleed)
```

### Step 3: Monitor for infection (days 2-5)

**Agent action**: Set a daily follow-up prompt for 3 days after a wound. Ask the user to check for the following signs.

```
INFECTION WARNING SIGNS — seek care if ANY appear:

Early signs (days 1-3):
[ ] Increasing redness that is spreading beyond wound edges
[ ] Wound is warm to the touch and getting warmer
[ ] Swelling is increasing after day 2 (should be decreasing)
[ ] Wound is producing yellow/green pus (not clear fluid)
[ ] Red streaks radiating from the wound

Serious signs (any of these = urgent care today):
[ ] Fever over 100.4F / 38C
[ ] Red streaks traveling up the arm or leg (lymphangitis)
[ ] The area around the wound is turning dark (possible
    necrotizing tissue — this is an emergency)

Normal healing looks like:
[ ] Mild pink/red at wound edges (days 1-3)
[ ] Some clear or slightly yellow fluid (days 1-2)
[ ] Scabbing starting (days 3-5)
[ ] Itching (a sign of healing, not infection)
```

### Step 4: Bruises and contusions

Bruises (contusions) are bleeding under the skin from an impact. They are almost always self-resolving.

```
BRUISE CARE:

First 24 hours:
[ ] Ice the area (cloth-wrapped, 15-20 min on, 40 min off)
[ ] Elevate if possible
[ ] Avoid heat, massage, or vigorous activity — increases bleeding

Days 2-7:
[ ] The bruise will change colors: red -> purple -> blue ->
    green -> yellow -> gone. This is normal blood breakdown.
[ ] Over-the-counter pain relief as needed (ibuprofen or
    acetaminophen — see Step 1 notes)

SEE A DOCTOR IF:
[ ] A bruise that is unusually large from a minor impact
[ ] Bruises appearing without any known injury
[ ] A bruise does not fade at all after 2 weeks
[ ] A bruise is on the eye socket with vision changes
[ ] The bruised area develops a hard lump that grows
    (possible hematoma requiring drainage)
```

## If This Fails

1. **Injury not improving after 72 hours of correct POLICE protocol**: Urgent care or doctor visit. X-ray may be needed to rule out fracture. Many small fractures look like bad sprains on examination alone.
2. **Signs of infection appear**: Do not wait. Same-day urgent care. Infections spread quickly and early antibiotics are far easier than treating an advanced infection.
3. **Wound reopens or won't close**: May need stitches or surgical glue. Urgent care within 6-8 hours of the injury gives the best result — wound edges become harder to close after that window.
4. **No medical insurance**: Community health centers offer sliding-scale fees. Search "federally qualified health center" plus your zip code at findahealthcenter.hrsa.gov — verified active March 2026.
5. **Tetanus concern and no insurance**: County health departments often offer tetanus boosters at reduced cost or free. Call your county health department.

## Rules

- Always do the emergency red flag check before proceeding
- Never tell someone an injury is "definitely fine" — you cannot see it
- Provide "when to see a doctor" criteria for every protocol, not just the emergency cases
- Do not recommend specific dosages for children — refer to package instructions and pediatric care
- Animal bites always need professional evaluation — rabies prophylaxis decisions require a medical provider

## Tips

- Ice reduces inflammation but also slows some aspects of the repair process. The current POLICE protocol (Optimal Loading replacing Rest) reflects updated evidence that gentle movement after 24-48 hours heals sprains faster than total immobilization.
- The most common wound care mistake is over-cleaning with hydrogen peroxide. It feels like it's working because it bubbles. It is actually damaging healthy tissue. Use it once to clean a dirty wound, then switch to plain water and antibiotic ointment.
- A sprain that "feels better in a day" is still not healed. The pain reduction comes from the acute inflammatory phase ending. The ligament repair takes 4-6 weeks. Returning to full activity too early causes re-injury.

## Agent State

Persist across sessions:

```yaml
injury:
  type: null               # sprain | strain | cut | bruise | other
  location: null           # body part
  injury_date: null
  injury_time: null
  treatment_started: null
  protocol_followed: []
  wound_care:
    cleaned: false
    covered: false
    infection_checks:
      - date: null
        signs_present: []
  sprain_strain:
    police_started: false
    elevation_hours: 0
    ice_sessions: 0
    compression_applied: false
    weight_bearing_day: null
  flags:
    red_flags_checked: false
    doctor_referral_given: false
    infection_flagged: false
    tetanus_concern: false
```

## Automation Triggers

```yaml
triggers:
  - name: infection_check_day2
    condition: "injury_type == 'cut' AND injury_date IS SET"
    schedule: "2 days after injury_date"
    action: "Day 2 wound check. Look at your wound: Is there increasing redness, warmth, swelling, or pus? Any fever? Report back and I will tell you if it looks normal or if you need care."

  - name: infection_check_day4
    condition: "injury_type == 'cut' AND injury_date IS SET"
    schedule: "4 days after injury_date"
    action: "Day 4 wound check. Is it scabbing and itching? That is good. Any spreading redness, streaks, or fever? That needs medical attention today."

  - name: sprain_loading_prompt
    condition: "injury_type == 'sprain' AND injury_date IS SET"
    schedule: "48 hours after injury_date"
    action: "48 hours in. Time to start gentle movement. Try weight-bearing or range-of-motion in the injured area — pain-free movement only. How is it feeling?"

  - name: sprain_one_week
    condition: "injury_type == 'sprain' AND injury_date IS SET"
    schedule: "7 days after injury_date"
    action: "One week check-in. Is the sprain significantly better? If you still can't bear weight or the swelling hasn't reduced, it is time to get it looked at — some sprains hide fractures."
```
