---
name: pet-first-aid
description: >-
  Emergency first aid and health assessment for dogs and cats. Use when someone's pet is injured, choking, may have eaten something toxic, is overheating, or when the owner needs to decide if it's an emergency vet visit or can wait.
metadata:
  category: life
  tagline: >-
    Recognize when your pet needs emergency care, handle wounds, choking, poison, and heat exposure -- and find affordable vet care.
  display_name: "Pet First Aid & Emergency Care"
  submitted_by: HowToUseHumans
  last_reviewed: "2026-03-19"
  openclaw:
    requires:
      tools: [filesystem]
    install: "npx clawhub install pet-first-aid"
---

# Pet First Aid & Emergency Care

Your dog just ate chocolate. Your cat is limping. There's blood on the carpet and you don't know where it's coming from. The vet is closed or costs $300 just to walk in. This skill covers the real first-aid situations pet owners face -- how to assess whether it's an emergency, what to do right now, and how to find care you can actually afford. Dogs and cats are the focus, with notes for other common pets where relevant.

```agent-adaptation
# Localization note
- Emergency vet availability and cost vary hugely by country and region
  US: ASPCA Poison Control 1-888-426-4435 ($75 consultation fee)
  UK: Animal Poison Line 01202 509000, PDSA for low-income vet care
  Australia: Animal Poisons Helpline 1300 869 738
  Canada: Pet Poison Helpline 1-855-764-7661
- Toxic plants and wildlife vary by region (different snakes, spiders,
  toads, and plants in different climates)
- Vet school clinics and low-cost options vary by location
- In some countries, veterinary emergency care is subsidized or
  available through animal charities (RSPCA in UK/AU, SPCA in NZ/US)
- Medication names and availability may differ internationally
```

## Sources & Verification

- **American Veterinary Medical Association (AVMA)** -- pet first aid guidelines and emergency care resources. https://www.avma.org/resources-tools/pet-owners/emergencycare
- **ASPCA Animal Poison Control** -- comprehensive toxic substance database for animals. https://www.aspca.org/pet-care/animal-poison-control
- **PetMD Emergency Guides** -- veterinary-reviewed emergency care articles. https://www.petmd.com
- **Merck Veterinary Manual** -- professional veterinary reference, publicly accessible. https://www.merckvetmanual.com
- **Anthropic, "Labor market impacts of AI"** -- March 2026 research showing this occupation/skill area has near-zero AI exposure. https://www.anthropic.com/research/labor-market-impacts

## When to Use

- User's pet is bleeding, limping, or showing signs of injury
- Pet may have eaten something toxic (chocolate, medication, plant, chemical)
- Pet is choking, gagging, or having trouble breathing
- Pet appears overheated, lethargic, or is having a seizure
- User needs to decide: emergency vet NOW vs. can it wait until morning?
- User needs help finding affordable vet care
- User wants to build a pet first aid kit
- Pet was in a fight with another animal

## Instructions

### Step 1: Emergency Triage

**Agent action**: Help the user determine if this is a drop-everything-go-to-emergency-vet situation or something that can wait. This is the most critical decision.

```
EMERGENCY TRIAGE -- IS THIS A VET-NOW SITUATION?

GO TO EMERGENCY VET IMMEDIATELY:
- Difficulty breathing (gasping, blue/white gums, extended neck)
- Uncontrolled bleeding (won't stop with 5 min of pressure)
- Suspected poisoning (see Step 4 for specific toxins)
- Seizure lasting more than 3 minutes or multiple seizures
- Collapse or inability to stand
- Hit by car (even if pet seems fine -- internal injuries are common)
- Bloated/distended abdomen with retching but nothing coming up (dogs)
  THIS IS BLOAT -- LIFE-THREATENING. Minutes matter.
- Eye injury (squinting, visible damage, swelling)
- Unable to urinate for 24+ hours (especially male cats -- urinary
  blockage is fatal within 48-72 hours)
- Suspected broken bone (limb at wrong angle, won't bear weight)
- Burns
- Heatstroke (panting heavily, bright red gums, staggering)
- Penetrating wound (puncture, impaled object -- don't remove it)

CAN LIKELY WAIT UNTIL REGULAR VET HOURS:
- Minor limping but still bearing weight on the leg
- Small cuts or scrapes (superficial, bleeding stopped)
- Vomiting once or twice but otherwise alert and hydrated
- Diarrhea without blood
- Decreased appetite for less than 24 hours
- Minor ear issues (head shaking, scratching)
- Skin irritation, hot spots, rashes

WHEN IN DOUBT:
Call your vet's after-hours line. Most clinics have one.
Or call an emergency vet -- they'll do a phone triage for free
and tell you if you need to come in.
```

### Step 2: Basic Vital Signs

**Agent action**: Teach the user how to check their pet's basic vital signs so they can report accurately to the vet.

```
NORMAL VITAL SIGNS -- KNOW THESE

             DOGS                    CATS
Heart rate:  60-140 bpm (small dogs  120-220 bpm
             up to 180 bpm)
Breathing:   10-30 breaths/min       20-30 breaths/min
Temperature: 101-102.5F (38.3-39.2C) 100.5-102.5F (38-39.2C)
Gum color:   Pink and moist          Pink and moist

HOW TO CHECK:

HEART RATE: Place your hand on the left side of the chest, just
behind the elbow. Count beats for 15 seconds, multiply by 4.
Or feel the femoral pulse: inside of the rear thigh, where the
leg meets the body.

BREATHING: Watch the chest rise and fall. Count breaths for
15 seconds, multiply by 4.

GUM COLOR (Capillary Refill Test):
1. Lift the lip and look at the gums
2. Press a finger against the gum for 2 seconds (it goes white)
3. Release and count how fast the pink color returns
4. Normal: returns in 1-2 seconds
5. ABNORMAL: pale/white gums, blue gums, bright brick-red gums,
   yellow gums, or refill time over 3 seconds
   ANY of these = go to vet NOW

TEMPERATURE: Rectal thermometer with petroleum jelly.
Insert 1 inch. Wait for beep.
Over 104F (40C) = overheating. Under 99F (37.2C) = hypothermia.
Both need vet attention.
```

### Step 3: Wound Care

**Agent action**: Walk the user through basic wound care for cuts, bites, and scrapes.

```
WOUND CARE -- DOGS AND CATS

MINOR WOUNDS (shallow cuts, scrapes, small punctures):

1. RESTRAIN SAFELY: Even gentle pets may bite when in pain.
   - Dog: Have someone hold the head. Muzzle if needed (use a
     strip of cloth -- loop around snout, tie under chin, tie behind ears).
     NEVER muzzle a vomiting animal.
   - Cat: Wrap in a towel ("burrito wrap"), leaving wound exposed.

2. CLEAN THE WOUND:
   - Flush with warm water or saline solution (1 tsp salt per quart water)
   - Use a syringe or squeeze bottle for gentle pressure
   - Remove visible debris with tweezers
   - Do NOT use hydrogen peroxide (damages tissue and slows healing)
   - Do NOT use alcohol (pain, tissue damage)
   - Betadine diluted to the color of weak tea is OK

3. APPLY ANTIBIOTIC OINTMENT:
   - Plain Neosporin/triple antibiotic is safe for dogs
   - For cats: use only if they won't lick it (they usually will)
   - Do NOT use any ointment with pain relief ingredients
     (the "-caine" ingredients are toxic to cats)

4. COVER AND PROTECT:
   - Light gauze bandage, secured with medical tape
   - Prevent licking: E-collar (cone of shame) is most reliable
   - DIY alternative: a baby onesie or old t-shirt can cover torso wounds
   - Check and change bandage daily

5. WATCH FOR INFECTION (next 3-5 days):
   - Increasing redness, swelling, warmth
   - Discharge (pus, especially green/yellow)
   - Bad smell
   - Pet becoming lethargic or feverish
   -> Any of these = vet visit

DEEP WOUNDS / HEAVY BLEEDING:
1. Apply direct pressure with a clean cloth for 5-10 minutes
2. Don't remove the cloth -- add more on top if it soaks through
3. If bleeding won't stop, apply pressure AND go to emergency vet
4. For puncture wounds: do NOT try to clean deep inside.
   Flush the surface, cover, and get to the vet.
   Puncture wounds are high infection risk.
```

### Step 4: Poisoning Response

**Agent action**: Cover the most common pet toxins with specific urgency levels and responses. This is the section most people need.

```
COMMON PET POISONS -- RESPONSE BY URGENCY

CALL POISON CONTROL FIRST: ASPCA 1-888-426-4435 ($75 fee)
They will tell you exactly what to do for the specific substance
and amount ingested. Worth the money every time.

HIGH URGENCY -- VET IMMEDIATELY:
- XYLITOL (sugar-free gum, some peanut butter, sugar-free candy):
  Can cause fatal blood sugar crash and liver failure in dogs
  within 30 minutes. EXTREMELY dangerous. Even small amounts.
  Go to vet NOW. Do not wait for symptoms.

- ANTIFREEZE (ethylene glycol): Lethal in tiny amounts.
  1 tablespoon can kill a cat. 3 tablespoons can kill a medium dog.
  Sweet taste attracts pets. Vet within 1-2 hours or it's often fatal.

- RAT POISON (rodenticides): Multiple types, each with different
  treatment. Bring the packaging to the vet -- the active ingredient
  determines the treatment. Time window varies by type.

- LILY (all parts -- Lilium and Hemerocallis species): CATS ONLY.
  Even pollen on fur that's groomed off can cause fatal kidney
  failure. Any lily exposure in a cat = emergency vet immediately.

- GRAPES AND RAISINS: Kidney failure in dogs. Amount that causes
  toxicity is unpredictable -- some dogs eat a handful and are fine,
  others are poisoned by a few. Treat every exposure as serious.

MODERATE URGENCY -- VET WITHIN A FEW HOURS:
- CHOCOLATE: Toxicity depends on type and amount.
  Dark/baking chocolate: dangerous in small amounts
  Milk chocolate: dangerous in moderate amounts
  White chocolate: low toxicity but high fat (pancreatitis risk)
  Rule of thumb: 1 oz of dark chocolate per pound of body weight
  is a medical emergency. Less = call poison control for guidance.

- IBUPROFEN / NAPROXEN (Advil, Motrin, Aleve): Toxic to dogs and
  cats. Can cause kidney failure and stomach ulcers.
  Even one pill for a small dog or cat = call vet.

- ACETAMINOPHEN (Tylenol): Extremely toxic to CATS. One pill can
  be fatal. Dogs tolerate slightly more but still dangerous.

- ONIONS AND GARLIC: Toxic to dogs and cats (cats more sensitive).
  Causes red blood cell damage. Effects may be delayed 3-5 days.
  Small amounts in food are usually OK; a whole onion is not.

LOWER URGENCY -- MONITOR AND CALL VET:
- MARIJUANA/THC: Dogs are very sensitive. Lethargy, wobbling,
  urine dribbling, dilated pupils. Rarely fatal but vet if severe.
  Be honest with the vet -- they don't report you.
- COFFEE/CAFFEINE: Similar to chocolate toxicity. Small amounts
  cause restlessness, large amounts can be serious.

WHEN TO INDUCE VOMITING vs. WHEN NOT TO:
- ONLY induce vomiting if instructed by a vet or poison control
- NEVER induce vomiting if:
  -> Pet ate something caustic (bleach, drain cleaner, batteries)
  -> Pet ate something sharp
  -> Pet is already vomiting
  -> Pet is unconscious or seizing
  -> It's been more than 2 hours since ingestion
- If told to induce vomiting in a dog: 3% hydrogen peroxide,
  1 teaspoon per 5 lbs of body weight, max 3 tablespoons.
  Give by mouth with syringe. Walk the dog -- movement helps.
- NEVER induce vomiting in cats at home. Cats are different --
  the vet needs to do this.
```

### Step 5: Choking Response

**Agent action**: Walk through the choking response for dogs and cats.

```
CHOKING -- DOGS

SIGNS: Pawing at mouth, gagging, drooling, blue gums, distress

1. OPEN THE MOUTH AND LOOK:
   - Restrain the dog. Open the jaw wide.
   - If you can SEE the object, try to sweep it out with your finger.
   - Use caution -- a choking dog may bite.
   - Do NOT blindly push your fingers deep into the throat
     (can push the object further in).

2. IF YOU CAN'T REMOVE IT -- MODIFIED HEIMLICH:
   Small dog (under 30 lbs):
   - Hold dog with back against your chest
   - Place fist just below the rib cage
   - Give 5 quick upward thrusts

   Large dog:
   - Stand behind the dog
   - Wrap arms around the belly
   - Place fist just below the rib cage
   - Give 5 firm upward thrusts

3. IF STILL CHOKING:
   - Lay dog on its side
   - Give 5 sharp compressions to the rib cage
   - Check mouth, sweep if object is visible
   - Repeat Heimlich and compressions
   - Get to vet while continuing attempts

CHOKING -- CATS
- Open mouth, look for visible object
- If visible, attempt removal with tweezers (not fingers -- cat
  mouths are small and you risk being bitten)
- DO NOT attempt Heimlich on cats -- their ribcages are fragile
- If cat is choking and you can't see/remove the object, go to vet
  immediately

AFTER ANY CHOKING EPISODE: See the vet even if you cleared the
object. The throat may be damaged or irritated.
```

### Step 6: Heatstroke

**Agent action**: Cover heat stroke recognition and immediate cooling protocol.

```
HEATSTROKE -- RECOGNITION AND RESPONSE

IT'S HEATSTROKE IF:
- Heavy, rapid panting that won't stop
- Bright red tongue and gums
- Thick, sticky saliva
- Staggering or wobbling
- Vomiting or diarrhea
- Collapse
- Rectal temperature above 104F (40C)

BREEDS AT HIGHEST RISK: Brachycephalic (flat-faced) dogs --
Bulldogs, Pugs, French Bulldogs, Boxers, Boston Terriers,
Shih Tzus, Cavalier King Charles Spaniels. Also: overweight dogs,
elderly dogs, thick-coated breeds, and any dog with heart/lung issues.

IMMEDIATE COOLING PROTOCOL:
1. Move to shade or air conditioning immediately
2. Offer cool (not cold) water to drink -- don't force it
3. Apply cool (not ice cold) water to:
   - Groin area
   - Armpits
   - Paw pads
   - Belly
4. Place cool wet towels on these areas (replace frequently --
   towels warm up quickly and then insulate heat IN)
5. Fan the dog while wet
6. DO NOT use ice water or ice packs -- causes blood vessels to
   constrict, trapping heat inside. Cool water only.
7. STOP active cooling when temperature reaches 103F (39.4C)
   -- overcooling is also dangerous
8. GO TO THE VET even if the dog seems to recover.
   Heatstroke causes organ damage that may not show immediately.

PREVENTION:
- Never leave a pet in a parked car. Ever. Even with windows cracked.
  A car hits 120F inside in 20 minutes on an 80F day.
- Walk dogs in early morning or evening during summer
- Asphalt test: place your hand on the pavement for 7 seconds.
  If it's too hot for your hand, it's too hot for paw pads.
- Always provide shade and water outdoors
- Clip (don't shave) thick-coated breeds in summer
```

### Step 7: Seizures

**Agent action**: Cover seizure response for pets.

```
SEIZURES -- WHAT TO DO

DURING A SEIZURE:
1. DO NOT restrain the pet
2. DO NOT put your hand near the mouth (they can't swallow their tongue)
3. Move objects away from the pet so they don't injure themselves
4. Note the TIME -- start a timer or check the clock
5. Turn off loud music/TV, dim lights if possible
6. VIDEO THE SEIZURE on your phone if possible (extremely helpful
   for the vet to see)

AFTER THE SEIZURE:
- The pet will be disoriented (post-ictal phase), may stagger,
  seem blind, or not recognize you. This is normal and temporary.
- Speak calmly, keep the environment quiet
- Don't try to give food or water until fully alert
- Note how long the seizure lasted and any unusual movements

VET IMMEDIATELY IF:
- Seizure lasts longer than 3 minutes
- Multiple seizures within 24 hours
- Pet doesn't return to normal within 30 minutes
- First-ever seizure (needs diagnosis)
- Pet is very young or very old

COMMON SEIZURE CAUSES:
- Epilepsy (most common in dogs, manageable with medication)
- Poisoning
- Liver or kidney disease
- Brain tumor (more common in older pets)
- Low blood sugar (especially small breeds and puppies)
```

### Step 8: Finding Affordable Vet Care

**Agent action**: Help the user find vet care they can actually afford. This is often the real barrier.

```
AFFORDABLE VET CARE OPTIONS

VET SCHOOL CLINICS:
- Teaching hospitals at veterinary schools offer care at 30-50% less
  than private practice
- You get experienced vets supervising students -- often excellent care
- Wait times are longer
- Search: "[your state] veterinary school clinic"

LOW-COST CLINICS:
- ASPCA and local SPCAs often run low-cost clinics
- Humane societies frequently offer affordable basic care
- Search: "low-cost vet clinic near me" or check humanesociety.org

PAYMENT OPTIONS:
- CareCredit: Medical credit card, 0% interest promotions
  (6-24 months depending on amount). Apply at carecredit.com
- Scratchpay: Financing specifically for vet bills. scratchpay.com
- Ask your vet about payment plans -- many offer them if you ask

FINANCIAL ASSISTANCE PROGRAMS:
- RedRover Relief: redrover.org (emergency financial assistance)
- The Pet Fund: thepetfund.com (non-emergency veterinary care)
- Brown Dog Foundation: browndogfoundation.org
- Breed-specific rescues often have emergency funds for their breed
- GoFundMe: many people successfully fundraise for vet emergencies

PET INSURANCE (for next time):
- Average cost: $30-60/month for dogs, $15-30/month for cats
- Covers accidents and illness (not pre-existing conditions)
- Worth it for: young pets, breeds prone to health issues, anyone who
  couldn't handle a sudden $3,000-5,000 vet bill
- Top-rated options as of 2026: Healthy Paws, Embrace, Trupanion
- Read the fine print: deductibles, coverage limits, waiting periods

PET FIRST AID KIT ($25):
[ ] Gauze rolls and pads
[ ] Medical tape (paper tape -- doesn't pull fur)
[ ] Triple antibiotic ointment
[ ] Hydrogen peroxide 3% (for inducing vomiting ONLY when directed by vet)
[ ] Digital thermometer (rectal)
[ ] Petroleum jelly
[ ] Tweezers
[ ] Blunt-tip scissors
[ ] Disposable gloves
[ ] Saline solution (wound flushing)
[ ] Diphenhydramine (Benadryl) -- 1mg per pound for dogs, ask vet for cat dose
[ ] Your vet's phone number and address
[ ] Emergency vet's phone number and address
[ ] ASPCA Poison Control: 1-888-426-4435
```

## If This Fails

- If your pet's condition is worsening and you can't reach a vet, call the closest emergency animal hospital and describe the symptoms over the phone. They'll advise.
- If you can't afford emergency vet care, tell the vet upfront. Many will work with you on payment plans or prioritize the most critical treatment.
- If you can't find affordable care in your area, call your local SPCA or humane society. They often know of emergency funds or reduced-cost options that aren't well advertised.
- If your pet ate something and you're not sure if it's toxic, call ASPCA Poison Control (1-888-426-4435). The $75 fee is worth it -- they have the most comprehensive animal toxicology database in the world.
- If you're in a rural area without nearby emergency vets, establish a relationship with your regular vet and ask about their after-hours policy. Many rural vets will meet you at the clinic for true emergencies.

## Rules

- Never give human medications to pets without vet guidance. Many are toxic, especially to cats.
- Always call poison control or your vet before inducing vomiting. Some substances cause more damage coming back up.
- Muzzle injured dogs before treating them -- pain makes any animal unpredictable
- Do not use ice or ice water for heatstroke. Cool water only.
- An animal that's been hit by a car needs a vet even if it looks fine. Internal injuries don't show externally.
- Never remove an impaled object. Stabilize it and get to the vet.
- When in doubt, call a vet. The worst outcome of an unnecessary vet visit is a bill. The worst outcome of skipping a necessary one is losing your pet.

## Tips

- Benadryl (diphenhydramine) at 1mg per pound is safe for most dogs and useful for allergic reactions, bee stings, and mild itching. Not for cats without vet guidance.
- The baby onesie or old t-shirt trick to cover a torso wound is genuinely effective and cheaper than a full surgical suit.
- A sock taped loosely over a paw wound (with gauze underneath) works as a temporary paw bandage.
- Pumpkin puree (plain, not pie filling) helps with both dog diarrhea and constipation. 1-2 tablespoons for medium dogs.
- Keep your vet's number and the emergency vet's number in your phone contacts labeled clearly. You won't want to search for them during a crisis.
- Annual vet visits catch problems early when they're cheaper to treat. Skipping preventive care costs more in the long run.
- If your pet has regular medications, keep a written list with dosages in your wallet or phone. You'll need this at the emergency vet.

## Agent State

```yaml
pet_emergency:
  pet_type: null
  pet_name: null
  pet_breed: null
  pet_weight: null
  emergency_type: null
  substance_ingested: null
  amount_ingested: null
  time_since_incident: null
  symptoms: []
  vital_signs:
    heart_rate: null
    breathing_rate: null
    gum_color: null
    temperature: null
  triage_result: null
  vet_contacted: false
  poison_control_called: false
  first_aid_administered: []
  vet_visit_needed: null
  affordable_care_options_provided: false
```

## Automation Triggers

```yaml
triggers:
  - name: poison_urgency
    condition: "substance_ingested IS NOT null AND poison_control_called IS false"
    action: "Your pet may have been poisoned and you haven't called poison control yet. Call ASPCA Poison Control at 1-888-426-4435 now. They'll tell you the exact urgency level and what to do. Have the substance packaging ready if possible."

  - name: triage_escalation
    condition: "symptoms CONTAINS 'difficulty breathing' OR symptoms CONTAINS 'seizure' OR symptoms CONTAINS 'collapse' OR symptoms CONTAINS 'bloat'"
    action: "Based on the symptoms you've described, this is likely a veterinary emergency. Stop reading and get to the nearest emergency vet immediately. Call them en route so they can prepare."

  - name: follow_up_check
    condition: "first_aid_administered IS NOT EMPTY AND vet_visit_needed IS 'monitor'"
    schedule: "12 hours after incident"
    action: "Checking in on your pet after the incident. How are they doing? Any new symptoms, changes in appetite, energy level, or bathroom habits? If anything has worsened, it's time for a vet visit."

  - name: preventive_care_reminder
    condition: "emergency_type IS NOT null AND affordable_care_options_provided IS true"
    schedule: "30 days after incident"
    action: "It's been a month since your pet's emergency. Have you scheduled a follow-up vet visit? Also consider whether pet insurance or a pet emergency fund might help if something like this happens again."
```
