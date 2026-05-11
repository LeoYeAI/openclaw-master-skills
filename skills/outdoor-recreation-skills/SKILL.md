---
name: outdoor-recreation-skills
description: >-
  Practical skills for camping, hiking, and outdoor recreation. Use when someone wants to start camping, plan a hiking trip, learn outdoor cooking, or build confidence in nature without prior experience.
metadata:
  category: skills
  tagline: >-
    Set up a tent, pack a backpack, cook on a camp stove, and navigate a trail -- weekend outdoor skills that build real competence.
  display_name: "Outdoor Recreation Skills"
  submitted_by: HowToUseHumans
  last_reviewed: "2026-03-19"
  openclaw:
    requires:
      tools: [filesystem]
    install: "npx clawhub install outdoor-recreation-skills"
---

# Outdoor Recreation Skills

Getting outside and being competent in nature is a skill, not a personality trait. You don't need to have grown up camping or own a truck full of gear. You need a tent, a backpack, a plan, and some basic knowledge. This covers the practical mechanics of weekend camping and hiking -- the stuff experienced outdoors people take for granted and beginners don't know to ask about. How to set up a tent so it doesn't leak, pack a backpack so your shoulders don't die, cook a real meal on a camp stove, and navigate a trail without getting lost.

```agent-adaptation
# Localization note
- Trail systems, park regulations, and permit requirements vary massively by country
  US: National Park Service (NPS), US Forest Service (USFS), Bureau of Land Management (BLM)
  UK: National Trust, Forestry England, right-to-roam laws apply in Scotland/Scandinavia
  Canada: Parks Canada, provincial parks
  Australia: National Parks and Wildlife Service (per state)
  New Zealand: Department of Conservation (DOC)
- Wildlife varies: bears (North America), snakes (Australia, US), large cats (parts of Africa,
  Americas), no large predators (UK, most of Europe)
- Camping culture and infrastructure differ: established campgrounds (US/Canada/AU),
  wild camping legal (Scotland, Scandinavia, much of Eastern Europe),
  wild camping restricted (England, most of Western Europe)
- Measurement units: miles vs kilometers, Fahrenheit vs Celsius
- Water purification urgency varies (generally safe streams in some regions,
  giardia risk in others, no safe natural water sources in some areas)
```

## Sources & Verification

- **Leave No Trace Center for Outdoor Ethics** -- the 7 principles of responsible outdoor recreation. https://lnt.org
- **REI Expert Advice** -- gear guides and technique articles reviewed by experienced outdoor educators. https://www.rei.com/learn/expert-advice
- **National Park Service Trip Planning** -- trail conditions, permits, safety alerts. https://www.nps.gov/planyourvisit
- **Appalachian Mountain Club** -- outdoor skills education and trip planning resources. https://www.outdoors.org
- **American Hiking Society** -- trail finding, advocacy, and beginner resources. https://americanhiking.org
- **Anthropic, "Labor market impacts of AI"** -- March 2026 research showing this occupation/skill area has near-zero AI exposure. https://www.anthropic.com/research/labor-market-impacts

## When to Use

- User wants to go camping for the first time and doesn't know where to start
- Someone is planning a hiking trip and needs to know what to bring
- User wants to learn camp cooking
- Someone feels intimidated by outdoor recreation and needs a confidence boost
- User needs to plan a trip with a group (family, scouts, friends)
- Someone wants to build outdoor skills progressively (car camping to backpacking)

## Instructions

### Step 1: Tent Setup

**Agent action**: Walk the user through selecting a campsite and setting up a tent properly -- the thing most first-time campers get wrong.

```
TENT SETUP -- PRACTICE AT HOME FIRST

BEFORE THE TRIP:
Set up your tent in your backyard or living room. Seriously.
Figuring out poles and stakes in the dark, in the rain, after
a 3-hour drive is miserable. Do a practice run.

CHOOSING A CAMPSITE:
- Flat ground (sleep on a slope and you'll roll all night)
- No low spots (water pools there when it rains)
- No dead branches overhead ("widow makers" -- they fall)
- 200 feet from water sources (required in most parks, protects water quality)
- Sheltered from wind if possible (tree line, not open ridge)
- Check the ground for rocks, roots, and pine cones -- clear them
  before laying the tent

SETUP SEQUENCE:
1. Lay down a ground cloth/footprint UNDER the tent
   (a cheap tarp works -- fold it so no edges stick out beyond
   the tent floor, or rain channels UNDER the tent)
2. Lay out the tent body
3. Assemble poles (most modern tents are color-coded -- match colors)
4. Attach poles to tent body (clips or sleeves)
5. Stake out the corners TIGHT (use rocks if ground is too hard for stakes)
6. Attach the rainfly

THE RAINFLY IS NON-NEGOTIABLE:
- Always put on the rainfly, even if the forecast is clear
- Orientation matters: most rainflies have a "door" side -- match it
  to the tent door. Vestibule should cover the entrance.
- Pull it taut. A saggy rainfly that touches the tent body = water
  transfers through and you get wet inside
- Guy lines (the thin cords on the rainfly): stake them out in
  windy conditions. They keep the fly off the tent walls.

INSIDE THE TENT:
- Sleeping pad goes down first (insulates from cold ground --
  more important than the sleeping bag in cold weather)
- Sleeping bag on top of pad
- Keep a headlamp and water bottle within arm's reach
- Shoes go in the vestibule (the covered area between fly and door)
- NOTHING with food smell stays in the tent (attracting animals)
```

### Step 2: Backpack Packing

**Agent action**: Teach proper packing technique for comfort and balance on the trail.

```
HOW TO PACK A BACKPACK (so your back doesn't hate you)

THE 20% RULE:
Your loaded pack should not exceed 20% of your body weight for
day hikes. For overnight, 25% max. More than that and your knees,
back, and enjoyment all suffer.

PACKING ZONES (bottom to top):

BOTTOM: Light, bulky items
- Sleeping bag (in stuff sack or compression sack)
- Extra clothing layers you won't need until camp

MIDDLE (closest to your back): Heavy, dense items
- Food, water (except what you need easy access to)
- Cook stove and fuel
- Bear canister if required
THIS IS THE KEY: Heavy items should sit between your shoulder
blades and close to your spine. This keeps the center of gravity
over your hips, not pulling you backward.

TOP: Medium-weight items you need during the day
- Rain jacket
- Lunch and snacks
- First aid kit
- Extra layer

OUTSIDE / POCKETS:
- Water bottles in side pockets
- Snacks in hip belt pockets
- Map, phone, sunscreen in top lid pocket
- Trekking poles strapped to the side when not in use

HIP BELT ADJUSTMENT:
The hip belt carries 80% of the weight. The shoulder straps guide.
1. Loosen all straps
2. Put on the pack
3. Fasten hip belt so the padding sits ON your hip bones
   (not your waist, not your stomach -- your hip bones)
4. Tighten shoulder straps until snug but not pulling down on shoulders
5. Tighten load lifter straps (above shoulders, angle upward to pack)
   at about 45 degrees
6. Walk around. If your shoulders hurt, the hip belt is too low.
   If your hips ache, the pack doesn't fit or is overloaded.
```

### Step 3: Clothing and Layering

**Agent action**: Explain the layering system that keeps people comfortable outdoors in any weather.

```
THE LAYERING SYSTEM -- COTTON KILLS, LAYERS SAVE

WHY LAYERS:
Weather changes. Exertion levels change. You'll be sweating uphill
and freezing at the summit. Layers let you adjust constantly.

THE THREE LAYERS:

1. BASE LAYER (next to skin):
   Purpose: Wick sweat away from your body
   Material: Merino wool or synthetic (polyester)
   NEVER cotton. Cotton absorbs sweat, stays wet, and sucks heat
   from your body. "Cotton kills" is not an exaggeration in cold/wet
   conditions. This is the single most important clothing rule.

2. MID LAYER (insulation):
   Purpose: Trap warm air
   Material: Fleece, down, or synthetic insulated jacket
   - Fleece: cheap, warm when wet, durable ($20-40)
   - Down: lightest, most compressible, useless when wet ($80-200)
   - Synthetic insulated: good balance, works when damp ($50-120)

3. OUTER LAYER (shell):
   Purpose: Block wind and rain
   Material: Waterproof/breathable jacket (Gore-Tex or similar)
   - For casual hiking: a basic rain jacket ($30-60) works fine
   - Bring rain pants for extended trips or cold/wet forecasts

SPECIFIC GEAR:
- SOCKS: Merino wool. Not cotton. Change into dry socks mid-hike
  if your feet are wet. Blisters come from moisture + friction.
- FOOTWEAR: Broken-in hiking boots or trail runners. NOT brand-new
  boots (guaranteed blisters). Trail running shoes are lighter and
  fine for most day hikes and moderate trails.
- HAT: Sun hat in summer, warm beanie in cold weather. You lose
  significant heat through your head.
- GLOVES: Lightweight pair for cold mornings. Heavier pair for winter.

THE "JUST RIGHT" FEEL:
When you start hiking, you should feel slightly cold. Within
10 minutes of moving, you'll warm up. If you start comfortable,
you'll overheat in 15 minutes and have to stop to de-layer.
```

### Step 4: Camp Stove Cooking

**Agent action**: Cover practical camp cooking from stove selection to real meals.

```
CAMP STOVE COOKING

STOVE OPTIONS:
- CANISTER STOVE ($25-40): Screws onto an isobutane fuel canister.
  Compact, fast, easy. Boils 1 liter in 3-4 minutes.
  Recommended: MSR PocketRocket or Soto Amicus.
  Fuel canisters: $5-8 each, last 1-3 days depending on use.
  Best for: most camping situations.

- ALCOHOL STOVE ($10-15 or make from a soda can): Ultralight,
  no moving parts, silent. Slower. Good for simple boil-only cooking.

- WOOD-BURNING STOVE ($25-40): Burns sticks and twigs.
  No fuel to carry. Slower, requires dry wood. Fun but less practical.

BOIL TIMES (at sea level, canister stove):
- 1 cup water: ~2 minutes
- 1 liter: ~3-4 minutes
- At altitude: add 1 minute per 1,000 feet above 5,000 feet

CAMP MEAL CATEGORIES:

NO-COOK (simplest):
- Tortillas with peanut butter and honey
- Trail mix, dried fruit, nuts
- Summer sausage, cheese, crackers
- Tuna packets on bread

BOIL-ONLY (most practical):
- Instant oatmeal + dried fruit + nuts (breakfast)
- Ramen + dehydrated vegetables + soy sauce
- Instant mashed potatoes + canned chicken
- Couscous + olive oil + sun-dried tomatoes
- Freeze-dried backpacking meals (add boiling water, wait 10 min)
  $8-12 each but convenient

ACTUAL COOKING:
- Scrambled eggs (crack into a container at home, carry in leak-proof
  bottle) in a small pan with butter
- Quesadillas on a pan (tortilla, cheese, pre-cooked meat)
- One-pot pasta (everything goes in one pot -- pasta, sauce,
  vegetables, protein)
- Foil packet meals (wrap meat, vegetables, seasoning in heavy foil,
  cook on coals or grill grate for 20-30 min)

CLEANING:
- Scrape food scraps into trash (not on the ground)
- Wash dishes 200 feet from any water source
- Use biodegradable soap (Dr. Bronner's) sparingly
- Strain food particles from wash water, pack out the solids
- Scatter strained wash water broadly over soil
```

### Step 5: Trail Navigation

**Agent action**: Cover basic trail navigation so the user doesn't get lost.

```
TRAIL NAVIGATION BASICS

BEFORE YOU GO:
1. Download the trail map to your phone for OFFLINE use
   Apps: AllTrails (most popular), Gaia GPS (most detailed),
   CalTopo (free, excellent for planning)
2. Tell someone your plan: trail name, start time, expected return
3. Check trail conditions and weather (the park's website or
   visitor center)
4. Know the trailhead location and parking situation

ON THE TRAIL:

TRAIL MARKERS:
- BLAZES: Paint marks on trees (usually rectangles, 2" x 6").
  Color indicates which trail. White blaze = Appalachian Trail.
  Two blazes stacked = turn coming (top blaze offset shows direction).
- CAIRNS: Stacks of rocks. Mark the route above treeline or in
  open terrain where you can't paint trees.
- SIGNS: At intersections. Note the trail name and distance.
  Take a photo of every sign for reference.
- COLORED MARKERS/FLAGGING: Ribbons or diamonds on trees or posts.

STAYING FOUND:
1. Look behind you regularly. The trail looks different going back.
   Memorize landmarks from the return direction.
2. At every intersection, note which way you came from
3. Track your time: if you've been hiking 2 hours in, plan for
   2 hours out (plus 50% more if there's significant elevation gain
   on the return)
4. If the trail disappears or you're unsure: STOP. Look for the
   last blaze/cairn you passed. Retrace to it. Don't push forward
   into uncertainty.

IF YOU'RE LOST:
S.T.O.P.
- Sit down (don't panic-walk further into lostness)
- Think about where you last knew your position
- Observe landmarks, terrain, sun position
- Plan your next move

If you have phone service: call for help, share GPS coordinates.
If you don't: stay put. You told someone your plan (you did,
right?). Staying in one place makes you findable. Moving makes
you harder to find.

PHONE AS BACKUP, NOT PRIMARY:
- Batteries die, screens break in rain, cold kills batteries faster
- Always download offline maps before the hike
- Carry a portable charger
- For serious backcountry: a paper topo map and compass are the
  failsafe. Learn basic compass navigation if you're going
  beyond well-marked trails.
```

### Step 6: Water Purification

**Agent action**: Cover the methods for making water safe to drink in the backcountry.

```
WATER PURIFICATION -- BECAUSE GIARDIA IS REAL

RULE: Assume all natural water sources are contaminated.
Even clear, cold mountain streams can carry giardia, crypto,
bacteria, and viruses. Treat everything.

METHOD 1: PUMP/SQUEEZE FILTER ($25-40)
- Sawyer Squeeze ($25-30) -- most popular. Screws onto a water
  bottle or hangs from a tree for gravity filtering.
- Removes: bacteria, protozoa (giardia, crypto)
- Does NOT remove: viruses (not typically a concern in North America
  or Europe, but is in developing countries)
- Flow rate: ~1 liter per minute
- Lifetime: 100,000+ gallons (backflush to maintain flow)
- Best for: most camping and hiking situations

METHOD 2: CHEMICAL TREATMENT ($8-15)
- Aquamira drops or Katadyn Micropur tablets
- Drop in, wait 15-30 minutes, drink
- Removes: bacteria, viruses, protozoa (with sufficient wait time)
- Pros: ultralight, cheap, no moving parts
- Cons: takes time, slight taste, doesn't work well in very cold
  or cloudy water

METHOD 3: UV TREATMENT ($80-100)
- SteriPen or similar UV wand
- Stir in water for 60-90 seconds
- Removes: bacteria, viruses, protozoa
- Pros: fast, no chemicals, no taste change
- Cons: battery-dependent, doesn't work in cloudy water, fragile

METHOD 4: BOILING (free, requires stove)
- Bring water to a rolling boil for 1 minute
  (3 minutes above 6,500 feet / 2,000 meters elevation)
- Removes: everything
- Pros: 100% effective, no equipment beyond stove
- Cons: uses fuel, takes time, water is hot after

WHAT TO USE:
- Day hike: Carry enough water from home. Sawyer Squeeze as backup.
- Overnight: Sawyer Squeeze or pump filter.
- International travel / developing countries: Filter + chemical
  treatment (double protection against viruses).
- Emergency: Boil.

HOW MUCH WATER:
- Day hike: 0.5 liters per hour of hiking (1 liter/hour in heat)
- Overnight: 3-4 liters per day per person
  (drinking + cooking + cleaning)
```

### Step 7: Leave No Trace and Campfire Basics

**Agent action**: Cover the essential outdoor ethics and campfire fundamentals.

```
LEAVE NO TRACE -- 7 PRINCIPLES (condensed)

1. PLAN AHEAD: Know regulations, weather, group size limits
2. TRAVEL ON DURABLE SURFACES: Stay on trail. Don't shortcut
   switchbacks. Camp on established sites.
3. DISPOSE OF WASTE PROPERLY: Pack out all trash. For human waste:
   dig a cathole 6-8 inches deep, 200 feet from water/trail/camp.
   Pack out toilet paper (or use a WAG bag in sensitive areas).
4. LEAVE WHAT YOU FIND: Don't pick wildflowers, move rocks, or
   carve trees. Take photos, not souvenirs.
5. MINIMIZE CAMPFIRE IMPACTS: Use established fire rings. Keep fires
   small. Burn wood completely to ash.
6. RESPECT WILDLIFE: Store food properly (bear canister, bear hang,
   or hard-sided vehicle). Don't feed animals. 200 feet minimum
   distance from large wildlife.
7. BE CONSIDERATE OF OTHERS: Keep noise down. Yield to uphill hikers.
   Don't blast music on the trail.

CAMPFIRE BASICS:
- Check fire restrictions before lighting ANYTHING (many areas ban
  fires during dry seasons -- this is enforced and fines are real)
- Use established fire rings only
- Keep fires small (the warmth is in the coals, not the flames)
- Gather only dead wood from the ground (never cut live trees)
- No larger than wrist-diameter (burns completely)
- Fully extinguish: drown with water, stir ashes, drown again,
  feel with your hand. If it's too hot to touch, it's too hot to leave.
- "Dead out" means COLD ashes. Not just no visible flame.

WILDLIFE FOOD STORAGE:
- Bear country: bear canister or bear hang (check local requirements)
- Bear hang: 100 feet from camp, food bag on rope, 12 feet up,
  6 feet from trunk, 6 feet below branch
- Bear canister: 100 feet from camp, on flat ground
- Even in non-bear areas: hang or secure food to prevent raccoons,
  mice, squirrels, and other raiders
- Cook and eat 100 feet from your tent. Food smell attracts animals.
```

### Step 8: The 10 Essentials

**Agent action**: Provide the standard 10 essentials checklist adapted for modern gear.

```
THE 10 ESSENTIALS -- WHAT YOU CARRY EVERY HIKE

This list was developed by The Mountaineers in the 1930s and
updated over decades. It's the baseline for every outdoor trip.

1. NAVIGATION: Map (downloaded offline + paper backup for big trips),
   compass, GPS device or phone with GPS

2. SUN PROTECTION: Sunscreen (SPF 30+), sunglasses, hat

3. INSULATION: Extra clothing layer beyond what you think you'll need.
   Weather changes. An emergency can extend your time outdoors by hours.

4. ILLUMINATION: Headlamp with extra batteries. Not a phone flashlight.

5. FIRST AID: Basic kit (bandages, tape, pain relievers, blister treatment,
   antihistamine, any personal meds). Know what's in it.

6. FIRE: Waterproof matches or lighter. Fire starter (dryer lint,
   cotton balls with petroleum jelly). For emergency warmth.

7. REPAIR TOOLS: Knife or multi-tool. Duct tape (wrap some around
   a water bottle to save space).

8. NUTRITION: Extra food beyond planned meals. High-calorie,
   no-cook (trail mix, bars, jerky). Enough for an extra day.

9. HYDRATION: Extra water beyond planned amount. Water purification
   method as backup.

10. EMERGENCY SHELTER: Emergency bivvy ($10-15) or space blanket ($2).
    Weighs almost nothing. Saves your life if you're stuck overnight.

TRIP PLANNING CHECKLIST:
[ ] Downloaded trail map (offline)
[ ] Checked weather forecast
[ ] Told someone: where you're going, when you'll be back,
    what to do if you're not back by [time]
[ ] Checked trail conditions and closures
[ ] Checked permit requirements
[ ] Packed the 10 essentials
[ ] Charged phone and portable charger
[ ] Checked gear condition (tent seams, stove function, water filter)
```

## If This Fails

- If the user is overwhelmed by the gear list, start with a day hike. You need: water, snacks, sunscreen, a rain jacket, and your phone with an offline map. That's it. Build from there.
- If camping gear is too expensive, rent it. REI rents tents, sleeping bags, and pads. Many outdoor clubs and university programs rent gear cheaply.
- If the user's first trip goes badly (rain, gear failure, uncomfortable), acknowledge it and help them identify the one thing to fix. Bad first trips are normal. Experienced campers have dozens of "disaster" stories.
- If they can't find anyone to go with, many areas have hiking groups (Meetup, local outdoor clubs, REI organized hikes) specifically for beginners.
- If physical limitations are a concern, car camping requires almost no physical exertion -- you drive to your site. Start there.

## Rules

- Never recommend heading into the backcountry without telling someone your plan. This is the safety baseline.
- Cotton clothing in cold/wet conditions is genuinely dangerous. Be direct about this.
- Fire restrictions are not suggestions. Check before every trip.
- Food storage rules in bear country are non-negotiable. A fed bear is a dead bear.
- Water purification is not optional in the backcountry. All natural water should be treated.
- Encourage starting easy (car camping, short day hikes) and building up gradually. Overambitious first trips create people who "don't like camping."

## Tips

- Car camping is the best way to learn. You have your car as backup for forgotten gear, cold nights, and rain. Build skills there before going remote.
- Two water bottles (one on each side of your pack) are easier to access than a hydration bladder and remind you to drink.
- Baby wipes are the backcountry shower. Pack some. You'll be grateful.
- A $15 inflatable camp pillow is the difference between sleeping and not sleeping. Don't stuff a jacket in a stuff sack and pretend that's a pillow.
- Earplugs for camping. Other campers snore, animals are noisy, wind flaps the tent. Earplugs fix all of it.
- Trail running shoes have largely replaced heavy hiking boots for most conditions. They're lighter, dry faster, and cause fewer blisters. Save boots for heavy packs and rough terrain.
- The best meal after a day of hiking is the one you don't have to cook. Pre-make sandwiches or wraps for the first night of car camping trips.

## Agent State

```yaml
outdoor:
  experience_level: null
  trip_type: null
  trip_destination: null
  trip_duration: null
  group_size: null
  gear_owned: []
  gear_needed: []
  gear_rented: []
  skills_practiced:
    tent_setup: false
    backpack_packing: false
    camp_cooking: false
    trail_navigation: false
    water_purification: false
    fire_building: false
  ten_essentials_packed: false
  trip_plan_filed: false
  permits_secured: false
```

## Automation Triggers

```yaml
triggers:
  - name: pre_trip_check
    condition: "trip_destination IS SET AND trip_plan_filed IS false"
    action: "You have a destination but haven't filed a trip plan yet. Tell someone where you're going, what trail, when you're leaving, when you expect to return, and what to do if you don't check in by a specific time. This is the single most important safety step."

  - name: gear_check
    condition: "trip_destination IS SET AND ten_essentials_packed IS false"
    schedule: "2 days before trip"
    action: "Trip is coming up. Run through the 10 essentials checklist and verify your gear. Check stove fuel, water filter function, headlamp batteries, and phone charge. Download your trail map for offline use now."

  - name: weather_check
    condition: "trip_destination IS SET"
    schedule: "1 day before trip"
    action: "Final weather check for your trip. Look at hourly forecasts for your trailhead and destination. Adjust clothing layers and gear accordingly. If severe weather is forecasted, consider rescheduling -- the trail will be there next weekend."

  - name: post_trip_review
    condition: "trip_type IS SET AND trip_duration IS SET"
    schedule: "2 days after trip ends"
    action: "How did the trip go? What worked, what didn't? Let's note what gear to add, what to leave behind, and what skills to practice before next time. Each trip teaches something for the next one."
```
