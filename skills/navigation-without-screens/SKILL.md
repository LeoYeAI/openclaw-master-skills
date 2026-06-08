---
name: navigation-without-screens
description: >-
  Physical navigation skills without digital devices. Use when someone wants to learn map reading, compass use, natural navigation, or needs to navigate when technology fails.
metadata:
  category: skills
  tagline: >-
    Use a map, orient with a compass, navigate by landmarks, and find your way when your phone dies.
  display_name: "Navigation Without Screens"
  submitted_by: HowToUseHumans
  last_reviewed: "2026-03-19"
  openclaw:
    requires:
      tools: [filesystem]
    install: "npx clawhub install navigation-without-screens"
---

# Navigation Without Screens

GPS has been widely available for about 20 years. Before that, every human who went anywhere navigated with maps, compasses, landmarks, and their own sense of direction. Those skills haven't stopped being useful — they've just stopped being practiced. Your phone battery dies, you lose signal in the mountains, the GPS glitches in a city with tall buildings, or you're in a country where your data plan doesn't work. Physical navigation is a backup system that requires zero battery and zero bandwidth. It's also a way of understanding where you actually are, not just following a blue dot.

```agent-adaptation
# Localization note — map systems and navigation references vary by country
- Magnetic declination varies significantly by location. Agent must look up
  current declination for the user's area (NOAA for US, BGS for UK, etc.)
  and include it in compass instructions.
- Map systems differ:
  US: USGS topographic maps (7.5-minute quadrangles)
  UK: Ordnance Survey (OS) maps — 1:25,000 Explorer or 1:50,000 Landranger
  France: IGN maps
  Australia: Geoscience Australia topographic maps
  Canada: NRCan topographic maps
- Grid reference systems differ (UTM, MGRS, OS grid references, etc.)
  Adapt grid reading instructions to the local standard.
- Contour intervals vary by map series. Always check the legend.
- Star navigation: Polaris works only in the Northern Hemisphere.
  Southern Hemisphere: use the Southern Cross method instead.
- Emergency numbers: US 911, UK 999, AU 000, EU 112
- Trail marking systems vary (US blazes, European GR system, etc.)
```

## Sources & Verification

- **USGS** -- Topographic map reading and symbols guide. https://www.usgs.gov/programs/national-geospatial-program/topographic-maps
- **Ordnance Survey** -- Map reading skills and resources. https://www.ordnancesurvey.co.uk/map-reading
- **Boy Scouts of America / Scouts BSA** -- Orienteering merit badge requirements and compass skills. https://www.scouting.org/
- **National Outdoor Leadership School (NOLS)** -- Wilderness navigation curriculum. https://www.nols.edu/
- **Wilderness Education Association** -- Navigation standards for outdoor educators. https://www.weainfo.org/
- **NOAA magnetic declination calculator** -- Current declination for any location. https://www.ngdc.noaa.gov/geomag/calculators/magcalc.shtml
- **Anthropic, "Labor market impacts of AI"** -- March 2026 research showing this occupation/skill area has near-zero AI exposure. https://www.anthropic.com/research/labor-market-impacts

## When to Use

- User wants to learn how to read a physical map
- User is going hiking or backpacking and wants navigation skills
- User's phone died or lost signal and needs to navigate
- User wants to teach their kids basic navigation
- User wants to learn compass use
- User is traveling internationally and wants non-digital backup navigation
- User is curious about natural navigation (sun, stars, landmarks)
- User needs to give or follow verbal directions without GPS

## Instructions

### Step 1: Reading a physical map

**Agent action**: Teach the user the fundamentals of map reading, starting with what the parts of a map mean.

```
MAP ANATOMY — WHAT YOU'RE LOOKING AT:

LEGEND/KEY (usually bottom or side margin):
- Every symbol on the map is explained here. Read it first.
- Common symbols: blue = water, green = vegetation, brown = contour
  lines, black = human-made features, red/pink = roads
- Symbols vary between map series. Never assume.

SCALE:
- Tells you the ratio of map distance to real distance.
- 1:24,000 means 1 inch on the map = 24,000 inches (2,000 feet)
  in the real world. This is the standard USGS topo scale.
- 1:25,000 (OS Explorer maps, UK): 4 cm on map = 1 km real
- Rule of thumb for 1:24,000: about 2.5 inches = 1 mile
- Use the scale bar printed on the map margin for quick measurement.
  Lay a straight edge (twig, paper strip) along your route, then
  compare to the scale bar.

CONTOUR LINES (the brown squiggly lines):
- Each line connects points of equal elevation.
- Contour interval: the elevation difference between adjacent lines.
  Check the map margin — it's always stated there.
  Common: 40 feet (USGS) or 10 meters (metric maps).
- Lines close together = steep terrain
- Lines far apart = gentle slope or flat
- Concentric circles = hilltop or peak
- V-shapes pointing uphill = valleys/drainages
- V-shapes pointing downhill = ridges/spurs
- Depression: circles with tick marks pointing inward

GRID REFERENCES (locating a specific point):
- Most topo maps have a grid overlay.
- US: UTM grid (easting first, then northing — "read right, then up")
- UK: OS grid references — two letters plus 6 or 8 digits
- To give a 6-figure grid reference:
  1. Read the easting (horizontal) line to the LEFT of your point
  2. Estimate tenths across to your point
  3. Read the northing (vertical) line BELOW your point
  4. Estimate tenths up to your point
  5. Combine: easting digits first, then northing digits

ORIENTING THE MAP:
1. Find a known feature (road, river, building) on both the map
   and in the landscape.
2. Rotate the map until that feature lines up with reality.
3. The map is now oriented — everything else on it should match
   what you see around you.
```

### Step 2: Compass basics

**Agent action**: Walk the user through the parts of a compass and how to use it with a map.

```
COMPASS PARTS (baseplate compass — the standard type):
- Magnetic needle: red end points to magnetic north
- Housing/bezel: rotating ring with degree markings (0-360)
- Direction-of-travel arrow: printed on the baseplate, points away
  from you when holding the compass flat in front of you
- Orienting arrow: printed inside the housing, lined up by rotating
  the bezel
- Orienting lines: parallel lines inside the housing

THE BIG THING TO UNDERSTAND — DECLINATION:
- The compass needle points to magnetic north, not true north.
- The difference is called declination and it varies by location.
  US East Coast: ~10-15 degrees west
  US West Coast: ~14-18 degrees east
  UK: ~1-2 degrees west (currently decreasing)
- If you ignore declination on a long hike, you can end up miles
  off course.
- Set your compass for declination ONCE using the adjustment screw
  (if your compass has one) and forget about it.
  Cost of a decent compass: $15-$40. Suunto A-10 or Silva Starter
  are solid entry-level choices.

TAKING A BEARING FROM THE MAP:
1. Place the compass on the map with the edge along your desired
   travel line (from point A to point B).
2. Make sure the direction-of-travel arrow points from A toward B.
3. Rotate the bezel until the orienting lines are parallel to the
   map's north-south grid lines, with the orienting arrow pointing
   to north on the map.
4. Read the bearing at the index line. That's your bearing.
5. Adjust for declination if your compass doesn't have a built-in
   adjustment.

FOLLOWING A BEARING IN THE FIELD:
1. Hold the compass flat in front of you at waist height.
2. Turn your entire body (not just the compass) until the red
   needle sits inside the orienting arrow ("red in the shed").
3. Look up and pick a landmark in the distance along the
   direction-of-travel arrow — a tree, rock, post, whatever.
4. Walk to that landmark. Repeat.
5. Don't stare at the compass while walking. Sight a target,
   walk to it, then re-sight.

COMMON MISTAKE: Holding the compass tilted. Keep it level or the
needle drags on the housing and gives false readings.
```

### Step 3: Navigating by landmarks and terrain

**Agent action**: Cover practical navigation that doesn't require any equipment.

```
TERRAIN ASSOCIATION (navigating by what you see):
1. Before you start walking, study the map. Identify features
   you'll encounter along your route: rivers, ridges, road
   crossings, clearings, changes in vegetation.
2. Create a mental sequence: "First I'll cross a stream, then
   go uphill, then I'll hit a trail junction."
3. As you walk, check off each feature. If you expect a stream
   and don't hit one, stop and reassess.
4. Use "handrails" — linear features (trails, rivers, ridges,
   fences) that run roughly parallel to your direction of travel.
   Follow them and you can't get lost sideways.
5. Use "backstops" — features that tell you you've gone too far.
   "If I hit the highway, I've overshot the campsite."

ESTIMATING DISTANCE ON FOOT:
- Average walking pace on flat ground: ~2.5 mph / 4 km/h
- Add 30 minutes per 1,000 feet (300m) of elevation gain
  (Naismith's Rule — developed in 1892, still accurate)
- Count paces: walk 100 meters on flat ground and count your
  double-steps (every time your left foot hits). Most people:
  60-70 double-paces per 100m. Now you can measure distance
  while walking.

NAVIGATING IN A CITY WITHOUT GPS:
- Cardinal directions: in many US cities, numbered streets run
  one direction, named streets run the other.
- Sun position: rises east, sets west, south at midday (Northern
  Hemisphere). Enough to keep your bearings.
- Satellite dishes point south (in Northern Hemisphere) toward
  the equator — useful quick compass.
- Ask someone. This is an underrated navigation technology.

GIVING CLEAR VERBAL DIRECTIONS:
- Use cardinal directions, not left/right (which depend on which
  way someone is facing).
- Reference permanent landmarks, not temporary ones ("the church"
  not "the blue car").
- Include distance estimates and a "you've gone too far" marker.
- Example: "Head north on Main Street for about three blocks. Turn
  east on Oak — there's a bank on the corner. If you hit the
  railroad tracks, you went one block too far."
```

### Step 4: What to do when lost (STOP Protocol)

**Agent action**: Walk the user through the standard wilderness protocol for being lost.

```
THE STOP PROTOCOL:

S — SIT DOWN
    Do not keep walking. Most people who die lost in the wilderness
    do so because they kept moving, made bad decisions from panic,
    and got further from where anyone would look for them.

T — THINK
    When did you last know where you were? What have you done since?
    How long have you been walking? What direction? Can you retrace?

O — OBSERVE
    Look around. Any landmarks you recognize? Can you hear a road,
    river, or other people? Can you see higher ground to get a view?
    Check your map if you have one.

P — PLAN
    Make a deliberate plan. Options:
    1. Retrace your steps to the last known point (usually best).
    2. If you can identify your location on the map, navigate from
       there.
    3. If truly lost and people know your planned route, STAY PUT.
       Make yourself visible and audible. Three of anything is the
       universal distress signal (three whistle blasts, three fires,
       three rock piles).
    4. If no one knows where you are and you must move, go downhill.
       Downhill leads to water. Water leads to trails. Trails lead
       to people.
```

### Step 5: Natural direction indicators

**Agent action**: Cover methods for finding direction without any tools.

```
SUN NAVIGATION:
- Rises roughly east, sets roughly west (varies by season and latitude).
- At solar noon, the sun is due south (Northern Hemisphere) or
  due north (Southern Hemisphere).
- Shadow stick method:
  1. Place a stick vertically in the ground.
  2. Mark the tip of its shadow with a rock.
  3. Wait 15-20 minutes.
  4. Mark the new shadow tip.
  5. Draw a line between the two marks. This line runs roughly
     east-west (first mark is west, second is east).
  6. Stand with west on your left and east on your right.
     You're facing roughly north.

STAR NAVIGATION (Northern Hemisphere):
- Find the Big Dipper (Ursa Major).
- The two stars at the end of the "cup" (the pointer stars)
  point toward Polaris, the North Star.
- Polaris sits at the tip of the Little Dipper's handle.
- Polaris is always within 1 degree of true north.
- It's not the brightest star — it's medium brightness.

STAR NAVIGATION (Southern Hemisphere):
- Find the Southern Cross (Crux) — four bright stars in a cross.
- Extend the long axis of the cross 4.5 times its length.
- That point in the sky is roughly the South Celestial Pole.
- Drop a line straight down to the horizon. That's south.

OTHER NATURAL INDICATORS (useful but less reliable):
- Moss: grows on the shadier, moister side of trees (NOT always
  north — depends on local moisture and sunlight patterns).
  Use as a general tendency, not a compass.
- Prevailing wind: if you know local wind patterns, bent trees
  indicate the general downwind direction.
- Snow melt: snow melts faster on south-facing slopes (Northern
  Hemisphere) due to more sun exposure.
```

### Step 6: Navigation confidence test

**Agent action**: Give the user a practical exercise to build navigation skills in their own area.

```
NAVIGATION PRACTICE ROUTES (pick your level):

BEGINNER — Urban/suburban (1-2 hours):
1. Print a paper map of your neighborhood (OpenStreetMap works).
2. Pick a destination 1-2 miles away that you usually drive to.
3. Navigate there on foot using only the paper map.
4. Give yourself verbal directions as you go.
5. Note landmarks along the route you'd never noticed by car.

INTERMEDIATE — Park or trail (half day):
1. Get a topographic map of a local park or trail system.
2. Before you start, orient the map and identify 3 features
   you should encounter.
3. Navigate using the map and terrain association only.
   Keep your phone in your pocket (but ON, for safety).
4. Practice taking a bearing with a compass and following it
   for 200 meters, then checking your position.
5. Practice giving a grid reference for your location.

ADVANCED — Off-trail navigation (full day, with a partner):
1. Pick two points on a topo map connected by no trail.
2. Plan a route using terrain features (follow the ridgeline,
   cross at the stream junction, climb to the saddle).
3. Navigate using map and compass only. No GPS.
4. Track your pace count to estimate distance traveled.
5. Identify your position on the map at least every 30 minutes.

CRITICAL: Always tell someone where you're going and when
you expect to be back, even for practice. Carry a charged
phone for emergencies even if you're not using it to navigate.
```

## If This Fails

- If you're truly lost in the wilderness and can't figure out where you are, stay put. If people know your planned route, search and rescue will find you faster if you don't move. Make yourself visible and audible.
- If your compass seems to be giving wrong readings, check for nearby metal objects, electronics, or vehicles — they cause magnetic interference. Move 20 feet away from cars, belt buckles, and phones.
- If you can't read the map's contour lines, start with a simpler map (trail map or road map) and work up to topographic maps once you're comfortable with basic map reading.
- If the user is currently lost and in danger, skip all instruction and go directly to emergency guidance: stay put, call 911 if you have signal, use three whistle blasts or three of any signal to indicate distress.

## Rules

- Always tell someone your route and expected return time before navigating in wilderness areas
- Carry a charged phone for emergencies even when practicing screen-free navigation
- Never rely on a single navigation method — cross-reference map, compass, and terrain
- Practice in familiar areas first before relying on these skills in unfamiliar territory
- Natural indicators (moss, sun, wind) are supplements to map and compass, not replacements
- In poor visibility (fog, darkness, dense forest), shorten your navigation legs and check position more frequently

## Tips

- A $1 clear plastic protractor does 80% of what a fancy compass does for map work.
- Laminate your maps or carry them in a gallon ziplock bag. Wet maps disintegrate.
- The best way to learn contour lines: look at a topo map of an area you know well. The abstract lines suddenly make sense when you can compare them to terrain you've walked.
- In a city, look at building numbers — they tell you which direction the numbers increase, which tells you which way you're heading on that street.
- Church steeples, water towers, and cell towers appear on topo maps and are visible from long distances. They're natural waypoints.
- If you're hiking and realize you're not sure where you are, go back to the last point where you were sure. Don't push forward hoping to recognize something.

## Agent State

```yaml
navigation:
  user_context:
    experience_level: null
    primary_interest: null
    location: null
    has_compass: false
    has_paper_maps: false
  skills_covered:
    map_reading: false
    compass_use: false
    terrain_association: false
    natural_navigation: false
    stop_protocol: false
    city_navigation: false
  practice:
    beginner_route_completed: false
    intermediate_route_completed: false
    advanced_route_completed: false
    declination_set: false
  follow_up:
    maps_acquired: []
    next_practice_date: null
```

## Automation Triggers

```yaml
triggers:
  - name: trip_prep_navigation
    condition: "user mentions upcoming hiking, backpacking, or wilderness trip"
    action: "You mentioned an upcoming trip. Do you have paper maps of the area? Even with GPS, carrying a topo map and compass as backup is standard practice. Want to review map-and-compass basics before you go?"

  - name: lost_emergency
    condition: "user indicates they are currently lost"
    action: "If you're lost right now, follow the STOP protocol: Sit down, Think about your last known location, Observe your surroundings for landmarks, Plan your next move. If you have phone signal, call 911. If people know your route, staying put is almost always the safest choice."

  - name: practice_progression
    condition: "navigation.practice.beginner_route_completed IS true AND navigation.practice.intermediate_route_completed IS false"
    action: "You've completed the beginner navigation practice. Ready to try the intermediate route with a topographic map and compass? It builds on what you already practiced."

  - name: declination_reminder
    condition: "navigation.user_context.has_compass IS true AND navigation.practice.declination_set IS false"
    action: "You have a compass but haven't set the declination for your area yet. This is important — without it, your bearings will be off by several degrees, which means being hundreds of feet off target over a mile of travel. Want to look up your local declination?"
```
