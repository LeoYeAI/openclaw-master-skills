---
name: childcare-essentials
description: >-
  Practical physical childcare skills for ages 0-5. Use when someone is a new parent, babysitter, grandparent, or anyone suddenly responsible for a young child and needs immediate practical guidance.
metadata:
  category: life
  tagline: >-
    Hold a baby, manage a fever, recognize danger signs, childproof a home — zero-to-five survival skills for anyone responsible for a small human.
  display_name: "Childcare Essentials"
  submitted_by: HowToUseHumans
  last_reviewed: "2026-03-19"
  openclaw:
    requires:
      tools: [filesystem]
    install: "npx clawhub install howtousehumans/childcare-essentials"
---

# Childcare Essentials

Every year millions of people become responsible for a small child with essentially no training. New parents, grandparents watching a grandchild for the weekend, babysitters, aunts and uncles, family friends — and the stakes are life-or-death in ways that most people don't fully appreciate until they're holding a baby for the first time. This skill covers the physical, practical knowledge that keeps children ages 0-5 alive and healthy. Not parenting philosophy. Not screen time debates. The hands-on, body-skills stuff: how to hold them, feed them, bathe them, recognize when something is wrong, and respond when an airway is blocked. These are skills that should be taught in high school and aren't.

```agent-adaptation
# Localization note — pediatric care and safety standards vary by country
- Emergency numbers: US 911, UK 999, AU 000, EU 112
- Poison control: US 1-800-222-1222, UK 111, AU 13 11 26
- Pediatric care access differs:
  US: Pediatrician or family doctor, ER for emergencies
  UK: GP, NHS 111 for advice, A&E for emergencies
  AU: GP, 13 HEALTH (13 43 25 84) for advice
  CA: Provincial health line, walk-in clinic, ER
- Car seat laws vary by country and state/province:
  US: state-specific (rear-facing until at least age 2 in most states)
  UK: must use car seat until 12 years old or 135cm tall
  EU: varies by country, generally ECE R44/R129 compliant seats
- Vaccination schedules vary by country. Refer to local health
  authority schedule, not US CDC schedule, for non-US users.
- Formula preparation guidelines: WHO recommends water at 70C/158F
  minimum. Some national guidelines differ.
- Child protective services: US CPS (state-run), UK NSPCC,
  AU child protection services (state-run)
```

## Sources & Verification

- **American Academy of Pediatrics (AAP)** -- Infant safe sleep, feeding, and developmental guidelines. https://www.aap.org/
- **CDC** -- Child development milestones and injury prevention. https://www.cdc.gov/ncbddd/childdevelopment/
- **Safe Kids Worldwide** -- Child injury prevention and home safety data. https://www.safekids.org/
- **American Red Cross** -- Infant and child first aid and CPR. https://www.redcross.org/take-a-class/first-aid/first-aid-training/first-aid-classes
- **National Child Traumatic Stress Network** -- Trauma-informed child care resources. https://www.nctsn.org/
- **Anthropic, "Labor market impacts of AI"** -- March 2026 research showing this occupation/skill area has near-zero AI exposure. https://www.anthropic.com/research/labor-market-impacts

## When to Use

- User is a new parent and feels unprepared for basic care
- User is babysitting and doesn't know infant/toddler basics
- User is a grandparent who hasn't been around babies in decades (guidelines have changed significantly)
- User needs to know when a child's symptoms require a doctor or ER
- User wants to childproof their home
- User needs choking response for an infant or toddler
- User has questions about safe sleep, feeding, or bathing
- User is suddenly responsible for a young child (emergency guardianship, visiting relative)

## Instructions

### Step 1: How to hold a newborn

**Agent action**: Cover the physical mechanics of safely holding an infant.

```
HOLDING A NEWBORN (0-4 months):

THE CRITICAL RULE: Support the head and neck at all times.
A newborn cannot hold their head up. Their neck muscles are too
weak. If the head flops backward or sideways unsupported, it can
obstruct their airway.

CRADLE HOLD (the classic):
1. Slide one hand under the baby's head and neck.
2. Slide the other under their bottom.
3. Lift gently, bringing them to your chest.
4. Rest their head in the crook of your elbow.
5. Your forearm supports their spine.
6. Your hand cups their bottom/thigh.
7. Your other arm can support underneath or be free.
This is the most natural hold for feeding, soothing, and rocking.

FOOTBALL HOLD (good for feeding, especially breastfeeding):
1. Tuck the baby along your forearm like a football.
2. Their head rests in your open hand, face up.
3. Their body runs along your forearm, legs tucked behind your
   elbow.
4. Support with your other hand as needed.
Good for: small babies, C-section recovery (keeps baby off the
incision), breastfeeding.

SHOULDER HOLD (for burping and calming):
1. Lift the baby to your shoulder.
2. Their chin rests on your shoulder.
3. One hand supports their bottom.
4. The other hand supports their head and neck from behind.
5. Gentle patting or rubbing on the back for burping.
Keep a burp cloth on your shoulder. You will need it.

FACE-DOWN HOLD (for colic/gas — "the colic carry"):
1. Lay the baby face-down along your forearm.
2. Their head near your elbow, legs straddling your hand.
3. Their weight rests on your forearm with gentle pressure on
   their belly.
4. Support their head with your hand or the crook of your arm.
5. Walk and gently sway.
This position puts pressure on the abdomen, which can relieve gas.

WHAT NOT TO DO:
- Never hold a baby with one hand unless the other is immediately
  available.
- Never hold a baby while carrying hot liquids or cooking.
- Never shake a baby. Ever. For any reason. Shaking causes brain
  damage and death. If you're frustrated and the baby won't stop
  crying, put them down in a safe place (crib, on their back)
  and walk away for 2-5 minutes to calm down. They will be fine
  crying in a safe space. You will not be fine if you shake them.
```

### Step 2: Safe sleep (this saves lives)

**Agent action**: Cover the ABCs of safe sleep. SIDS prevention is non-negotiable content.

```
SAFE SLEEP — THE ABCs:

A — ALONE
    Nothing in the crib except the baby and a fitted sheet.
    No blankets. No pillows. No stuffed animals. No bumper pads.
    No sleep positioners. No matter what grandma says. No matter
    what the product packaging says. These items are suffocation
    hazards. The AAP is unambiguous on this.

B — ON THEIR BACK
    Every sleep. Every nap. Every time. Until they can
    independently roll both ways (usually around 4-6 months).
    "But they sleep better on their stomach" — yes, and the risk
    of SIDS is significantly higher. Back to sleep.
    Once they can roll on their own, you don't need to keep
    flipping them back.

C — IN A CRIB (or bassinet or play yard)
    Firm, flat mattress. If you press on it and it conforms to
    the shape of your hand, it's too soft.
    No inclined sleepers (recalled by CPSC due to infant deaths).
    Crib meets current safety standards (slat spacing less than
    2-3/8 inches — a soda can should not fit through).
    No drop-side cribs (banned in the US since 2011).

ROOM SHARING VS BED SHARING:
- Room sharing (baby in a crib or bassinet in your room): AAP
  recommends for at least the first 6 months. Reduces SIDS risk
  by up to 50%.
- Bed sharing (baby in your bed): the AAP recommends against it.
  Risk factors for bed-sharing deaths: soft bedding, parental
  smoking, alcohol or sedating medication use, prematurity.

TEMPERATURE:
- Room temperature: 68-72 degrees F (20-22 C).
- Dress baby in one layer more than you're comfortable in.
- Sleep sack (wearable blanket) instead of loose blankets.
  Cost: $15-$30.
- If their chest feels warm and their hands are slightly cool,
  the temperature is right. Overheating is a SIDS risk factor.

PACIFIER: Offering a pacifier at nap and bedtime reduces SIDS
risk. Don't force it. Don't reinsert if it falls out during sleep.
Don't attach it to a string or clip in the crib.
```

### Step 3: Feeding basics

**Agent action**: Cover formula preparation and feeding safety.

```
BOTTLE FEEDING (formula):

FORMULA PREPARATION:
1. Wash hands thoroughly.
2. Sterilize new bottles and nipples before first use (boiling
   water for 5 minutes or use a microwave sterilizer).
3. After first use: hot soapy water or dishwasher is sufficient.
4. Follow the ratio on the formula container EXACTLY. Do not
   add extra water (dilutes nutrition, dangerous electrolyte
   imbalance). Do not add extra powder (too concentrated for
   kidneys).
5. Use clean water. If using tap water: run cold tap for 15-30
   seconds first. If concerned about water quality, use bottled
   or filtered water.
6. Mix water and powder. Swirl to mix (shaking creates air
   bubbles = more gas).
7. Test temperature on the inside of your wrist. Should feel
   lukewarm, not hot. Body temperature (98.6F / 37C) is ideal.

CRITICAL: NEVER MICROWAVE A BOTTLE. Microwaves heat unevenly
and create hot spots that can scald the baby's mouth. Use a
bottle warmer ($15-$30) or warm the bottle in a bowl of warm water.

FEEDING AMOUNTS (approximate, varies by baby):
- Newborn: 1-2 oz every 2-3 hours
- 1 month: 3-4 oz every 3-4 hours
- 3 months: 4-5 oz every 3-4 hours
- 6 months: 6-8 oz every 4-5 hours
These are guidelines. Follow the baby's hunger cues: rooting
(turning head, opening mouth), sucking on hands, fussing.

BURPING:
- Burp at every 2-3 oz and at the end of feeding.
- Shoulder method: baby upright on your shoulder, pat/rub back.
- Seated method: sit baby on your lap, lean them slightly forward
  supporting their chin and chest with one hand, pat back with
  the other.
- If no burp after 5 minutes, move on. Not every feeding produces
  a burp.

FORMULA STORAGE:
- Prepared formula: use within 1 hour if left out, within 24
  hours if refrigerated.
- Opened can of powder: use within 1 month.
- If the baby starts a bottle but doesn't finish it: discard
  within 1 hour. Bacteria from their mouth contaminates it.
```

### Step 4: Diaper changing

**Agent action**: Step-by-step diaper change for people who've never done it.

```
DIAPER CHANGING STEP-BY-STEP:

SUPPLIES (gather before starting — never leave baby on a
changing surface unattended for any reason):
- Clean diaper
- Wipes (fragrance-free for newborns — less irritation)
- Diaper cream/ointment if needed (Desitin, A&D, or any zinc
  oxide cream for rash)
- Change of clothes if needed
- Plastic bag for dirty diaper if no diaper pail nearby

THE PROCESS:
1. Place baby on a flat, safe surface. Changing table with safety
   strap, or a changing pad on the floor (safest — can't fall).
2. Unfasten the dirty diaper but don't remove it yet.
3. Lift the baby's legs by grasping both ankles gently with one
   hand (your index finger between their ankles for grip).
4. Wipe front to back (especially for girls — prevents UTIs).
   Use as many wipes as needed to get completely clean.
5. Slide the dirty diaper out. Fold it closed and set aside.
6. Slide the clean diaper under (tabs go in the back, under
   the baby).
7. Apply diaper cream if there's any redness.
8. Pull the front of the diaper up between their legs.
9. Fasten the tabs snugly but not tight — you should be able to
   fit two fingers between the diaper and their belly.
10. Done. Wash your hands.

FOR BOYS: Point the penis downward before closing the diaper.
Otherwise urine goes up and out the waistband. Also: have a
cloth ready to drape over them during the change — baby boys
will urinate when the cool air hits them. It's not a matter of if.

DIAPER RASH:
- Zinc oxide cream (Desitin Maximum Strength, 40% zinc) at every
  change if there's redness. Apply thickly — it's a barrier.
- Change diapers frequently. Sitting in a wet diaper is the
  primary cause.
- Let them go diaper-free on a towel for 10-15 minutes a few
  times a day — air is the best healer.
- If the rash has raised red bumps with satellite spots, it may
  be a yeast infection. See the pediatrician — needs antifungal
  cream, not zinc.
```

### Step 5: Recognizing fever and when to call the doctor

**Agent action**: Cover the pediatric fever rules that every caregiver must know.

```
FEVER IN CHILDREN — WHEN IT'S AN EMERGENCY:

HOW TO TAKE A TEMPERATURE:
- Under 3 months: rectal thermometer ONLY. Most accurate.
  Lubricate tip with petroleum jelly, insert 1/2 inch, wait
  for beep. Cost of a digital rectal thermometer: $8-$12.
- 3 months to 3 years: rectal is still most accurate. Armpit
  (axillary) is acceptable for screening but reads ~1 degree
  lower.
- Over 3 years: oral or ear (tympanic) thermometer is fine.
- Forehead (temporal artery) thermometers are convenient but
  less accurate. Fine for screening, not definitive.

WHEN TO CALL THE DOCTOR:
- Under 3 months: ANY fever of 100.4F (38C) or higher is an ER
  visit. Do not wait. Do not pass Go. Newborns can't fight
  infection well and a fever can indicate something serious.
- 3-6 months: fever over 101F (38.3C) — call the pediatrician.
- 6-24 months: fever over 102F (38.9C) that lasts more than
  one day — call the pediatrician.
- Over 2 years: fever over 104F (40C) or any fever lasting
  more than 3 days — call the pediatrician.

FEVER MEDICATION:
- Acetaminophen (Tylenol): safe from 3 months. Dose by WEIGHT,
  not age. Follow the package carefully or ask the pharmacist.
- Ibuprofen (Motrin/Advil): safe from 6 months. Dose by WEIGHT.
- NEVER give aspirin to children under 18 (Reye's syndrome risk).
- Don't alternate Tylenol and ibuprofen unless your doctor
  specifically tells you to — it's easy to accidentally double-dose.

OTHER EMERGENCY SIGNS (call 911 or go to ER regardless of fever):
- Difficulty breathing (ribs visible with each breath, nostrils
  flaring, grunting sounds, lips or fingernails turning blue)
- Unresponsive or unusually difficult to wake
- Seizure (fever-related seizures happen — they look terrifying
  but are usually not dangerous. Keep the child safe, don't
  restrain them, time it, call 911.)
- Rash that doesn't blanch when you press on it (press a clear
  glass against it — if the rash is still visible through the
  glass, seek emergency care)
- Bulging fontanelle (the soft spot on a baby's head)
- Persistent vomiting — can't keep any fluids down for 8+ hours
- No wet diapers for 8+ hours (dehydration)
```

### Step 6: Choking response

**Agent action**: Cover choking protocol for infants and toddlers. This is life-saving content.

```
CHOKING RESPONSE — INFANT (under 1 year):

SIGNS OF CHOKING: Can't cry, cough, or breathe. May turn red
or blue. Silent or making high-pitched sounds.

IF THE BABY IS COUGHING FORCEFULLY: Let them cough. Don't
interfere. A strong cough is the most effective clearing mechanism.

IF THE BABY CANNOT COUGH, CRY, OR BREATHE:

Back blows + chest thrusts (NOT the Heimlich maneuver):
1. Sit down. Lay the baby face-down on your forearm, which
   rests on your thigh. Their head is lower than their body.
2. Support their head and jaw with your hand (don't cover
   the mouth).
3. Give 5 firm back blows between the shoulder blades with
   the heel of your other hand.
4. Turn the baby over (face-up on your forearm, head still
   lower than body).
5. Give 5 chest thrusts: two fingers on the breastbone, just
   below the nipple line. Push down about 1.5 inches. Quick,
   firm compressions.
6. Look in the mouth. If you SEE the object, sweep it out with
   your finger. Do NOT do a blind finger sweep — you can push
   the object deeper.
7. Repeat back blows and chest thrusts until the object comes
   out or the baby becomes unconscious.
8. If unconscious: call 911, begin infant CPR.

CHOKING RESPONSE — TODDLER/CHILD (over 1 year):

IF THEY CAN COUGH: Encourage them to keep coughing.

IF THEY CANNOT COUGH, SPEAK, OR BREATHE:
Abdominal thrusts (Heimlich maneuver):
1. Stand or kneel behind the child.
2. Make a fist with one hand. Place thumb side against their
   abdomen, just above the navel, well below the ribcage.
3. Grasp your fist with the other hand.
4. Give quick upward thrusts — inward and upward.
5. Repeat until the object comes out or they become unconscious.
6. If unconscious: call 911, begin child CPR.

COMMON CHOKING HAZARDS (children under 4):
- Hot dogs (cut lengthwise, then into small pieces — never rounds)
- Grapes (cut in quarters lengthwise)
- Popcorn (no popcorn under age 4)
- Nuts and seeds
- Hard candy
- Raw carrots (cook until soft or cut very thin)
- Chunks of meat or cheese
- Peanut butter (thin layer only, never a glob — it sticks)
- Coins, buttons, batteries (button batteries are a medical
  emergency if swallowed — call poison control immediately)
- Balloons (uninflated or popped — leading cause of choking
  death from toys)
- Small toy parts (anything that fits through a toilet paper
  tube is a choking hazard)
```

### Step 7: Childproofing the home

**Agent action**: Walk through a systematic childproofing checklist.

```
CHILDPROOFING — START AT 4-6 MONTHS (before they're mobile):

ELECTRICAL:
[ ] Outlet covers on all unused outlets ($5 for a pack of 30).
    Sliding plate covers are more effective than plug-in caps
    (which kids learn to remove quickly).
[ ] Secure cords from lamps, blinds, and electronics — cord
    wraps or cord covers. Blind cords are a strangulation hazard.
[ ] Power strips: use covers or mount them out of reach.

KITCHEN:
[ ] Cabinet locks on all lower cabinets, especially under the
    sink (cleaning chemicals). Magnetic locks ($15-$25 for a
    set) are the most effective.
[ ] Stove knob covers ($8-$12)
[ ] Turn pot handles to the back of the stove when cooking
[ ] Lock the oven door (oven lock clip, $5)
[ ] Keep knives in a locked drawer or high, secured block
[ ] Move all cleaning products to a high, locked cabinet
[ ] Dishwasher: keep locked. Detergent pods look like candy
    and are highly toxic.

BATHROOM:
[ ] Toilet lock ($8-$12) — toddlers can drown in a toilet
[ ] Medicine cabinet: everything locked or above reach. Even
    vitamins and supplements can be toxic in quantity.
[ ] Water heater set to 120F (49C) maximum — prevents scalding.
    Call your utility company if you're not sure how to adjust it.
[ ] Non-slip mat in tub
[ ] Never leave a child in water unattended. Not for a phone
    call. Not for a doorbell. Not for any reason. Drowning happens
    in under 2 minutes and is silent.

STAIRS AND DOORS:
[ ] Gates at top and bottom of stairs. Hardware-mounted at the
    top (pressure-mounted gates can be pushed out). Cost: $30-$80.
[ ] Door knob covers on doors to dangerous areas (basement,
    garage, outside).
[ ] Door stops or finger guards to prevent pinched fingers.
[ ] Sliding door locks above child's reach.

FURNITURE AND HEAVY OBJECTS:
[ ] Anchor all bookshelves, dressers, and TVs to the wall.
    Anti-tip straps cost $5-$10 and prevent crush deaths. A
    falling dresser kills a child roughly every two weeks in
    the US.
[ ] Move climbable furniture away from windows.
[ ] Window stops: windows should open no more than 4 inches.
    Cost: $5-$10 per window.

MISCELLANEOUS:
[ ] Button batteries: keep all devices with accessible battery
    compartments out of reach. Swallowed button batteries burn
    through tissue in 2 hours. If swallowed: ER immediately.
    Give honey (if over 1 year) on the way — it slows the burn.
[ ] Houseplants: several common ones are toxic (dieffenbachia,
    philodendron, pothos). Move out of reach or remove.
[ ] Pet food and water bowls: toddlers will eat pet food and can
    drown in pet water bowls.

CAR SEAT BASICS:
- Rear-facing until at least age 2, or until they exceed the
  seat's rear-facing height/weight limit. Longer is better.
- Read the car seat manual AND your car's manual for installation.
- The seat should not move more than 1 inch side-to-side when
  tested at the belt path.
- Harness straps should be snug — you should not be able to
  pinch excess strap material at the shoulder.
- Chest clip at armpit level.
- If you're unsure about installation: fire stations and hospitals
  often offer free car seat checks. SafeKids.org has an inspection
  station locator.
```

## If This Fails

- If the baby won't stop crying and you've checked everything (hunger, diaper, temperature, gas, overtired), put them in a safe place and take a 5-minute break. Babies cry — sometimes for hours. It's not a failure. Shaken baby syndrome happens when frustrated caregivers reach their breaking point. Walking away is the right response.
- If you're unsure whether a symptom is serious, call your pediatrician's nurse line. After hours, most practices have an on-call nurse. When in doubt, go to the ER. No one will fault you for being cautious with a child.
- If you can't install the car seat correctly, do not guess. Go to a certified car seat inspection station (SafeKids.org/coalitions, or call your local fire department).
- If childproofing feels overwhelming, start with the three highest-risk items: anchoring furniture, locking chemicals, and outlet covers. These address the most common serious injuries.
- Poison control (US: 1-800-222-1222) is 24/7, free, and staffed by toxicology experts. Save the number in your phone now.

## Rules

- Under 3 months with any fever of 100.4F or higher is always an ER visit — no exceptions
- Never leave a child unattended in water, on a changing table, or near stairs
- Back to sleep, every sleep, every time until the baby can roll independently
- Nothing in the crib except the baby and a fitted sheet
- Never shake a baby — put them down and walk away if frustrated
- Dose children's medication by weight, not by age, and never give aspirin to children under 18
- Cut round foods (grapes, hot dogs, cherry tomatoes) lengthwise into small pieces for children under 4

## Tips

- The inside of your wrist is your best thermometer for bottles and bath water. If it feels warm but not hot, it's right.
- Baby boys will urinate during diaper changes. Have a cloth ready. This is not a theory, it's a guarantee.
- White noise (a fan, a sound machine, a running dryer) calms many babies because the womb is loud — about 80-90 decibels. Keep sound machines at least 7 feet from the crib and below 50 decibels.
- The "toilet paper tube test" is the easiest choking hazard check: if it fits through the tube, it's a choking hazard for kids under 3.
- Zip-up sleepwear instead of button-up. At 3 AM with a crying baby, you'll thank yourself.
- Take an infant CPR class before the baby arrives. The American Red Cross offers 2-hour in-person and online courses. The $30 and 2 hours could save a life.

## Agent State

```yaml
childcare:
  user_context:
    role: null
    child_age_months: null
    experience_level: null
    living_situation: null
    has_pediatrician: false
  safety_completed:
    safe_sleep_reviewed: false
    choking_response_learned: false
    fever_rules_reviewed: false
    childproofing_completed: false
    car_seat_installed: false
    cpr_training_taken: false
    poison_control_saved: false
  skills_covered:
    holding_baby: false
    feeding: false
    diaper_changing: false
    bathing: false
    fever_management: false
    choking_response: false
    childproofing: false
  concerns:
    current_symptom: null
    urgency_level: null
  follow_up:
    pediatrician_next_visit: null
    vaccination_schedule_reviewed: false
    developmental_milestones_discussed: false
```

## Automation Triggers

```yaml
triggers:
  - name: emergency_symptom
    condition: "childcare.concerns.current_symptom IS SET AND childcare.concerns.urgency_level == 'high'"
    action: "You described symptoms that may need immediate medical attention. If the child is under 3 months with any fever, having difficulty breathing, is unresponsive, or had a seizure, call 911 or go to the ER now. For possible poisoning, call Poison Control at 1-800-222-1222."

  - name: newborn_safety_priority
    condition: "childcare.user_context.child_age_months < 3 AND childcare.safety_completed.safe_sleep_reviewed IS false"
    action: "For a newborn under 3 months, safe sleep setup is the most critical safety item. Let's review the ABCs: Alone, on their Back, in a Crib with a firm mattress and nothing else. This reduces SIDS risk significantly."

  - name: choking_prep
    condition: "childcare.user_context.child_age_months >= 4 AND childcare.safety_completed.choking_response_learned IS false"
    action: "Your child is approaching or at the age where they'll start putting things in their mouth. Knowing the choking response (back blows and chest thrusts for infants, Heimlich for toddlers) is critical. Want to walk through it? Also consider taking a hands-on infant CPR class."

  - name: childproofing_timing
    condition: "childcare.user_context.child_age_months >= 4 AND childcare.user_context.child_age_months <= 6 AND childcare.safety_completed.childproofing_completed IS false"
    action: "Your child is at the age where mobility starts — crawling, pulling up, reaching. Childproofing should happen before they're mobile, not after. Want to go through the room-by-room checklist?"

  - name: cpr_training_nudge
    condition: "childcare.safety_completed.cpr_training_taken IS false AND childcare.user_context.role IS SET"
    schedule: "once"
    action: "You haven't taken an infant/child CPR class yet. The American Red Cross offers 2-hour courses (in-person and online) for about $30. It's the single most valuable thing you can do to prepare for a choking or breathing emergency. Want me to help you find a class near you?"
```
