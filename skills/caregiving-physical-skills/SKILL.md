---
name: caregiving-physical-skills
description: >-
  Physical caregiving techniques for assisting elderly, disabled, or recovering family members. Use when someone is caring for an aging parent, disabled family member, or recovering patient and needs hands-on physical care skills.
metadata:
  category: life
  tagline: >-
    Help someone stand, transfer, bathe, and move with dignity — the physical caregiving skills nobody teaches until you need them.
  display_name: "Caregiving Physical Skills"
  submitted_by: HowToUseHumans
  last_reviewed: "2026-03-19"
  openclaw:
    requires:
      tools: [filesystem]
    install: "npx clawhub install howtousehumans/caregiving-physical-skills"
---

# Caregiving Physical Skills

53 million Americans are unpaid caregivers, mostly for aging parents or disabled family members. Almost none of them received any training. They learn by trial and error — and the errors can mean a dropped patient, a caregiver's blown-out back, or a pressure sore that turns into a hospital stay. This skill covers the physical, hands-on techniques that professional home health aides learn in training: how to move someone safely, how to prevent falls, how to help with bathing, and how to keep both the person you're caring for and yourself from getting hurt. These are body skills — they require practice, not just reading. But knowing the correct technique before you try it is the difference between safe care and a preventable injury.

```agent-adaptation
# Localization note — healthcare systems and caregiver support vary by country
- Medical equipment availability and insurance coverage differ:
  US: Medicare covers some durable medical equipment (DME) with
      physician order. Medicaid coverage varies by state.
  UK: NHS provides equipment through occupational therapy referral.
      Social services may provide care assessments.
  Canada: Provincial health programs cover varying equipment.
  Australia: NDIS for disability, My Aged Care for elderly.
- Caregiver support programs:
  US: National Family Caregiver Support Program (state-administered),
      VA Caregiver Support for veteran caregivers
  UK: Carer's Allowance, local authority carer assessments
  AU: Carer Payment, Carer Allowance
  CA: Provincial caregiver programs
- Emergency numbers: US 911, UK 999, AU 000, EU 112
- Medication names may differ (generics vs brand names vary by country)
- Home modification grants/programs are jurisdiction-specific
```

## Sources & Verification

- **American Red Cross** -- Home health aide and caregiving training guides. https://www.redcross.org/take-a-class/home-health-aide
- **National Institute on Aging** -- Caregiving resources and guidance for families. https://www.nia.nih.gov/health/caregiving
- **Family Caregiver Alliance** -- Research, resources, and support for family caregivers. https://www.caregiver.org/
- **AARP** -- Caregiving resources including home modification guides. https://www.aarp.org/caregiving/
- **CDC** -- Caregiver health data and fall prevention resources. https://www.cdc.gov/falls/
- **Anthropic, "Labor market impacts of AI"** -- March 2026 research showing this occupation/skill area has near-zero AI exposure. https://www.anthropic.com/research/labor-market-impacts

## When to Use

- User is suddenly responsible for caring for an aging parent
- User needs to help someone transfer from bed to chair or wheelchair
- User wants to set up a home for fall prevention
- User needs to help someone bathe safely
- User is worried about hurting their own back while caregiving
- User needs to manage medications for someone else
- User wants to recognize warning signs in an elderly person
- User needs to prevent or manage pressure sores

## Instructions

### Step 1: Protect yourself first — caregiver body mechanics

**Agent action**: Before teaching any patient handling, teach the caregiver how to protect their own body. Back injuries are the number one caregiver injury.

```
YOUR BODY MECHANICS — LEARN THIS BEFORE TOUCHING ANYONE:

THE CORE RULES:
1. Never lift with your back. Ever. Use your legs.
2. Keep the person close to your body. Arms extended = back injury.
3. Widen your stance. Feet shoulder-width or wider. One foot
   slightly ahead of the other for stability.
4. Bend at the hips and knees, not at the waist.
5. Tighten your core (abs and lower back) before any lift.
6. Never twist while lifting. Move your feet to turn.
7. If the person weighs more than you can safely handle,
   DO NOT attempt it alone. Use equipment or get help.

WHEN TO USE A GAIT BELT:
- A gait belt is a thick canvas or nylon belt that goes around the
  person's waist. You grip it (not their clothes, not their arms)
  when helping them stand, sit, or walk. Cost: $10-$20.
- Use it for: stand-to-sit transfers, sit-to-stand, walking assist,
  any transfer where the person has some leg strength but is
  unsteady.
- How to apply: over their clothing, around their natural waist
  (above the hips), snug enough that you can get your fingers
  under it but not so loose it rides up. Buckle in front.
- Grip: overhand grip (palms down, fingers curled under the belt)
  on each side or behind.
- NEVER use a gait belt on someone with: recent abdominal surgery,
  abdominal aortic aneurysm, severe osteoporosis of the ribs/spine,
  or a feeding tube. Check with their doctor if unsure.

SIGNS YOU'RE HURTING YOURSELF:
- Sharp pain in lower back during or after transfers
- Numbness or tingling in arms or legs
- Shoulder pain from pulling
- Persistent fatigue that doesn't resolve with rest
- You've stopped exercising because you're too tired from caregiving

GET HELP WHEN:
- The person requires more than stand-by assist (they bear less
  than 50% of their own weight)
- You're doing transfers more than 3-4 times per day
- You've already injured yourself
- The person's condition is declining and transfers are harder
  Ask their doctor for a home health referral — Medicare and most
  insurance covers physical therapy for transfer training.
```

### Step 2: Safe patient transfers

**Agent action**: Walk through the most common transfers step by step.

```
BED TO CHAIR TRANSFER (person has some leg strength):

Setup:
- Position the chair at 45 degrees to the bed, on the person's
  stronger side if they have one.
- Lock wheelchair brakes. Remove or swing away the footrest on
  the transfer side.
- Lower the bed to chair height if adjustable. Raise the head
  of the bed so they're already semi-upright.

Steps:
1. Help them roll onto their side facing you (log-roll: move
   shoulders and hips together, not separately).
2. Help them sit up by swinging their legs off the bed while
   they push up with their arms. One of your hands behind their
   shoulder, one on their thigh above the knee.
3. Let them sit on the edge of the bed for 30-60 seconds.
   CHECK FOR DIZZINESS. Blood pressure drops when going from
   lying to sitting (orthostatic hypotension). If they're dizzy,
   wait. If they're very dizzy or lightheaded, lay them back down
   and try again in a few minutes.
4. Apply the gait belt if using one.
5. Have them scoot to the edge of the bed so their feet are flat
   on the floor.
6. Stand in front of them, feet wide, knees bent. Your knees
   block their knees to prevent buckling.
7. On the count of three, they push up from the bed with their
   hands while you lift using the gait belt. Stand them up.
8. Once standing, have them pivot (small steps, turning toward
   the chair) until the chair is directly behind them.
9. Have them reach back for the armrests.
10. Lower them slowly into the chair by bending YOUR knees.
    Don't let them drop.

CHAIR TO STANDING:
1. Scoot them to the front edge of the chair.
2. Feet flat on the floor, slightly behind their knees.
3. Lean them forward — "nose over toes." Their weight must be
   over their feet before standing, or they'll sit right back down.
4. On three, they push off the armrests while you assist with
   the gait belt.
5. Wait for steadiness before walking.

CAR TRANSFER:
1. Back the person up to the open car door, facing away from
   the car.
2. Have them sit on the car seat (like sitting on a chair).
3. Then swing their legs in. You may need to help lift their legs.
4. One hand behind their head to prevent hitting the doorframe.
5. Reverse to get out: swing legs out first, scoot to edge,
   stand with assistance.
- A plastic bag on the car seat reduces friction and makes
  pivoting easier. Cheap and effective.
```

### Step 3: Fall prevention in the home

**Agent action**: Walk through a systematic home safety audit.

```
HOME SAFETY AUDIT — ROOM BY ROOM:

BATHROOM (where most falls happen):
[ ] Grab bars by toilet (both sides if possible) — install into
    wall studs, not just drywall. Cost: $20-$50 per bar + install.
    Suction cup bars are NOT safe for weight-bearing.
[ ] Grab bars in shower/tub — horizontal for support, vertical
    for pulling up. L-shaped is most versatile.
[ ] Non-slip mat or adhesive strips in tub/shower
[ ] Shower chair or transfer bench — Cost: $30-$80
[ ] Handheld showerhead on a slide bar — Cost: $25-$50
[ ] Raised toilet seat if they have trouble sitting low
    Cost: $25-$60. Some have built-in armrests.
[ ] Night light (motion-activated, $5-$10)
[ ] Remove bathroom door lock (or replace with one that opens
    from outside — if they fall and lock the door, you can't
    get to them)

BEDROOM:
[ ] Bed at the right height — when sitting on the edge, their
    feet should be flat on the floor and knees at 90 degrees.
    Adjust with bed risers ($15-$30) or a lower-profile mattress.
[ ] Clear path from bed to bathroom — no cords, no clutter
[ ] Night light along the path
[ ] Phone within reach from bed
[ ] Bed rail if they roll (but check: bed rails can be an
    entrapment hazard for confused or agitated patients)

THROUGHOUT THE HOME:
[ ] Remove all throw rugs or secure them with double-sided tape
[ ] Clear all walkways of cords, clutter, and low furniture
[ ] Adequate lighting — 60-watt minimum in all hallways and stairs
[ ] Light switches accessible at top and bottom of every staircase
[ ] Stair railings on both sides, firmly attached
[ ] Non-slip stair treads ($2-$5 per step)
[ ] Frequently used items at counter height (no reaching overhead,
    no bending to floor-level cabinets)
[ ] Sturdy, non-rolling chairs at the kitchen table
[ ] Remove wheeled furniture or add locking casters

WHAT THEY WEAR:
- Non-skid slippers or shoes. No socks on hard floors.
- Avoid long robes or nightgowns that can catch on feet.
- Well-fitting shoes with rubber soles when walking outside.
```

### Step 4: Helping someone bathe safely

**Agent action**: Cover bathing assistance with attention to dignity and safety.

```
BATHING ASSISTANCE — SAFETY AND DIGNITY:

SETUP:
- Warm the bathroom first (space heater for 5 minutes, $20-$40).
  Elderly people chill easily and cold is a fall risk (shivering
  affects balance).
- Gather everything before you start: towels, washcloth, soap,
  shampoo, clean clothes, lotion. No leaving mid-bath to grab
  something.
- Water temperature: test with your elbow or a thermometer.
  100-105 degrees F (38-40 C) maximum. Elderly skin burns more
  easily — what feels warm to you may scald them.
- Shower chair in place, non-slip mat down, grab bars accessible.
- Handheld showerhead: this is the single most useful bathing
  modification. Allows them to sit while you direct the water.

THE PROCESS:
1. Let them do as much as they can themselves. Offer help, don't
   take over. Independence is psychologically critical.
2. Wash from cleanest to dirtiest: face and hair first, then
   upper body, then lower body, then perineal area last.
3. If you're washing them: describe what you're doing before you
   do it. "I'm going to wash your back now." No surprises.
4. Keep them covered with a towel except for the area you're
   actively washing. This isn't just about modesty — it prevents
   chilling and preserves dignity.
5. Check skin as you go: redness, bruising, rashes, skin tears,
   pressure sore development (see Step 7).
6. Dry thoroughly, especially between toes and in skin folds.
   Moisture = skin breakdown and fungal infections.
7. Apply lotion to dry skin (not between toes — moisture trap).

IF THEY RESIST BATHING:
- This is extremely common, especially with dementia.
- Don't force it. Try again later or the next day.
- Offer a sponge bath as an alternative (warm washcloth at the
  sink — covers hygiene without the full production).
- Try bathing at the time of day they're most alert and calm.
- Let them hold the washcloth — having something in their hands
  can reduce anxiety.
- Same routine, same order, every time. Predictability reduces
  resistance.
```

### Step 5: Medication management

**Agent action**: Cover the basics of managing someone else's medications.

```
MEDICATION MANAGEMENT BASICS:

ORGANIZATION:
- Weekly pill organizer with AM/PM compartments. Cost: $5-$10.
  Fill it at the same time every week.
- Keep an updated medication list: drug name, dose, frequency,
  prescribing doctor, what it's for, and when it was last changed.
  Take this list to every doctor visit and ER trip.
- Use one pharmacy for all prescriptions. The pharmacist catches
  dangerous interactions that individual doctors might miss.

CRITICAL RULES:
- NEVER crush or split a pill without checking with the pharmacist.
  Some pills are extended-release or enteric-coated — crushing them
  dumps the full dose at once, which can be fatal.
- If they can't swallow pills, ask the pharmacist about liquid
  alternatives. Most common medications have them.
- Don't mix medications from different bottles into one container.
  If there's a problem, you won't know which drug caused it.
- Refill prescriptions 5-7 days before they run out.
  Set a phone reminder.

COMMON MEDICATION PROBLEMS IN ELDERLY:
- Taking the wrong dose (especially if they're also managing
  their own meds and you're supplementing)
- Duplicate dosing (they forgot they took it)
- Dangerous interactions with over-the-counter drugs
  (especially NSAIDs like ibuprofen with blood thinners)
- New confusion or behavior changes after a medication change
  (report this to the doctor — it may be the drug, not decline)
- Not taking medications because of side effects they haven't
  told anyone about

WHEN TO CALL THE DOCTOR:
- Any new medication side effect
- Missed doses of blood thinners, seizure meds, heart meds,
  insulin, or blood pressure meds — these are the high-risk ones
- Any sudden change in behavior, alertness, or confusion after
  a medication change
```

### Step 6: Recognizing medical emergencies in elderly

**Agent action**: Cover the warning signs that are specific to and easily missed in elderly patients.

```
EMERGENCY SIGNS THAT LOOK DIFFERENT IN THE ELDERLY:

STROKE (act FAST — every minute matters):
F — Face drooping (ask them to smile — is it uneven?)
A — Arm weakness (can they raise both arms equally?)
S — Speech difficulty (are they slurring or not making sense?)
T — Time to call 911. Note the time symptoms started — this
    determines treatment options.
ALSO: sudden severe headache, sudden vision loss, sudden confusion
    or inability to understand you.

FALL ASSESSMENT (after any fall):
1. Don't move them immediately. Ask: "Where does it hurt?"
2. Check for: head injury (confusion, unequal pupils, vomiting),
   hip pain (can't stand or bear weight — possible hip fracture),
   wrist or arm pain (broken wrist from catching themselves)
3. If they hit their head and they're on blood thinners: ER visit,
   even if they feel fine. Internal bleeding risk is high and
   symptoms can be delayed 24-48 hours.
4. Any fall with loss of consciousness = call 911.
5. Document: when, where, what they were doing, what they tripped
   on. Patterns reveal preventable causes.

DEHYDRATION (extremely common, easily missed):
Signs: dark urine, dry mouth, sunken eyes, confusion, dizziness
when standing, skin that "tents" when pinched on the back of the
hand and stays up instead of flattening back.
Risk factors: diuretic medications, hot weather, illness with
vomiting/diarrhea, simply forgetting to drink.
Response: encourage fluids throughout the day. Keep a water bottle
within reach always. If severe (can't keep fluids down, very
confused), call the doctor or go to the ER for IV fluids.

UTI (URINARY TRACT INFECTION) — THE GREAT MIMICKER:
In elderly people, UTIs often present as sudden confusion,
agitation, or behavioral changes — NOT the typical burning or
frequency that younger people experience. If your parent suddenly
seems confused or is acting unlike themselves, a UTI is one of
the first things to rule out. A simple urine test at the doctor's
office takes minutes.

SILENT HEART ATTACK:
Elderly people (especially women and diabetics) can have heart
attacks without the classic chest-clutching pain. Watch for:
unexplained fatigue, shortness of breath, nausea, jaw or back
pain, breaking out in a cold sweat. When in doubt, call 911.
```

### Step 7: Pressure sore prevention

**Agent action**: Cover bed positioning and skin integrity for people who are immobile or bed-bound.

```
PRESSURE SORE PREVENTION:

WHERE THEY DEVELOP:
- Sacrum (tailbone) — the most common location
- Heels
- Hips (greater trochanter)
- Shoulder blades
- Back of the head
- Anywhere bone is close to the skin surface

STAGES:
Stage 1: Red area that doesn't blanch (turn white) when pressed.
  Skin is intact. THIS IS YOUR WARNING. Act now.
Stage 2: Blister or shallow open area. Dermis is exposed.
Stage 3: Full-thickness skin loss. Fat may be visible.
Stage 4: Muscle, bone, or tendon exposed. Medical emergency.
Stages 3-4 require professional wound care. Call the doctor.

PREVENTION PROTOCOL:
1. Reposition every 2 hours if bed-bound. Use a schedule:
   2 AM — left side
   4 AM — back
   6 AM — right side
   (Continue rotating. Set phone alarms.)
2. When on their back, elevate heels off the bed with a pillow
   under the calves (not under the knees — that compresses blood
   vessels).
3. Use pillows between the knees when side-lying.
4. Don't drag them across sheets — lift to reposition. Friction
   causes skin breakdown.
5. Keep skin clean and dry. Change soiled linens immediately.
6. Keep sheets wrinkle-free under them (wrinkles = pressure points).
7. Nutrition matters: adequate protein and hydration are essential
   for skin integrity. If they're not eating well, talk to the
   doctor about supplementation.
8. Pressure-redistribution mattress overlay: Cost $50-$200.
   Medicare covers with physician order for qualifying patients.
   This is one of the most effective single interventions.

CHECK SKIN DAILY. Especially sacrum and heels. Early detection
prevents weeks of wound care and possible hospitalization.
```

## If This Fails

- If transfers are too difficult or unsafe for you alone, request a home health aide assessment through their doctor. Medicare covers skilled home health services when ordered by a physician.
- If the person is resistant to help and you can't manage safely, contact the Area Agency on Aging (eldercare.acl.gov, 1-800-677-1116) for local support options.
- If you're experiencing caregiver burnout (exhaustion, depression, resentment, health decline), contact the Family Caregiver Alliance (caregiver.org, 1-800-445-8106) for support services and respite care referrals.
- If you discover a Stage 3 or 4 pressure sore, this requires professional wound care immediately. Call their physician the same day.
- If you've injured your own back, see a doctor and request a home care reassessment. Continuing to lift while injured will make it permanent.

## Rules

- Never drag a person across a surface — always lift or use a slide sheet. Friction tears elderly skin.
- Never rush a transfer. Orthostatic hypotension (dizziness from position change) causes falls. Wait 30-60 seconds after position changes.
- Never leave someone alone in a bathtub or shower, even "just for a second"
- Check medication lists before crushing any pill — extended-release or enteric-coated pills can be fatal if crushed
- Reposition bed-bound individuals every 2 hours minimum — pressure sores can develop in a single day
- Your own physical health is not optional. If you get injured, you can't provide care. Protect your body with proper mechanics every single time.

## Tips

- A $10 gait belt is the single most useful piece of caregiving equipment. Get one before you need it.
- A plastic bag on a car seat or transfer surface reduces friction and makes pivoting much easier.
- When helping someone stand, the command "nose over toes" is the most useful cue. If their center of gravity isn't over their feet, they can't stand.
- Keep a go-bag packed for ER visits: medication list, insurance cards, ID, phone charger, a change of clothes, a snack. You'll be waiting.
- Respite care exists for a reason. Even 4 hours a week of someone else providing care can prevent burnout. Adult day programs, in-home respite, and volunteer visitor programs are available in most areas through the Area Agency on Aging.
- Talk to an occupational therapist (OT) — they specialize in making daily activities possible and safe. A single home visit from an OT can transform the care environment. Most insurance covers it with a doctor's referral.

## Agent State

```yaml
caregiving:
  user_context:
    relationship_to_patient: null
    patient_condition: null
    patient_mobility_level: null
    living_situation: null
    other_caregivers_involved: false
    has_professional_support: false
  safety_audit:
    home_assessment_completed: false
    bathroom_modifications: []
    grab_bars_installed: false
    bed_height_adjusted: false
    throw_rugs_removed: false
    lighting_adequate: false
    medication_list_current: false
  equipment:
    gait_belt: false
    shower_chair: false
    handheld_showerhead: false
    raised_toilet_seat: false
    bed_rail: false
    pressure_mattress: false
  skills_covered:
    body_mechanics: false
    transfers: false
    fall_prevention: false
    bathing_assistance: false
    medication_management: false
    emergency_recognition: false
    pressure_sore_prevention: false
  caregiver_health:
    back_pain_reported: false
    burnout_indicators: false
    last_respite: null
  follow_up:
    next_doctor_appointment: null
    medication_refill_dates: []
    skin_check_schedule: null
```

## Automation Triggers

```yaml
triggers:
  - name: caregiver_burnout_check
    condition: "caregiving.caregiver_health.burnout_indicators IS true OR days_since(caregiving.caregiver_health.last_respite) > 30"
    schedule: "monthly"
    action: "Caregiver check-in: How are you doing? Burnout is real and common — you can't pour from an empty cup. Have you had any time for yourself in the last month? Respite care, adult day programs, or even a few hours of in-home help can make a major difference. Want help finding options in your area?"

  - name: medication_refill_reminder
    condition: "caregiving.safety_audit.medication_list_current IS true"
    schedule: "weekly"
    action: "Weekly medication check: Are any prescriptions running low? Refill 5-7 days before they run out to avoid gaps, especially for blood thinners, seizure meds, and blood pressure medications."

  - name: skin_check_reminder
    condition: "caregiving.user_context.patient_mobility_level == 'bed-bound' OR caregiving.user_context.patient_mobility_level == 'chair-bound'"
    schedule: "daily"
    action: "Daily skin check reminder: Check the sacrum, heels, hips, and shoulder blades for redness that doesn't blanch when pressed. Early detection of pressure sores prevents weeks of wound care."

  - name: home_safety_followup
    condition: "caregiving.safety_audit.home_assessment_completed IS false AND caregiving.user_context.living_situation IS SET"
    action: "You're providing care at home but haven't done a home safety audit yet. Falls are the leading cause of injury in elderly people, and most are preventable with simple modifications. Want to walk through the room-by-room checklist?"

  - name: transfer_difficulty_escalation
    condition: "caregiving.user_context.patient_mobility_level IS SET AND caregiving.caregiver_health.back_pain_reported IS true"
    action: "You mentioned back pain and you're doing physical transfers. This is a serious warning sign — continuing to lift while injured can cause permanent damage. Ask the patient's doctor for a home health referral. Medicare covers physical therapy for transfer training, and an aide can help with the heaviest tasks."
```
