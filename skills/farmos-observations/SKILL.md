---
name: farmos-observations
description: Query and create field observations and AI-processed captures. Photos, voice notes, and text notes from the field.
tags: [farming, observations, field-reports]
---

# FarmOS Observations

AI-powered quick capture system — field observations, photos, voice notes, and issue reports.

## When to Use This

**What this skill handles:** Field observations -- pest/disease/weed reports, crop condition notes, weather damage, soil issues, equipment problems spotted in the field, and photo-based scouting captures.

**Trigger phrases:** "found [pest/weed/disease] in field X", "beans look rough", "something is wrong with field 12", "create an observation", "log this problem", "any observations today?", "what has been reported in field X?"

**What this does NOT handle:** Equipment maintenance scheduling or fleet status (use farmos-equipment), task/work order creation (use farmos-tasks -- but the bot will offer to create a work order after logging an observation), weather forecasts or spray conditions (use farmos-weather).

**Minimum viable input:** Any mention of something observed in the field. "Beans look bad" is enough -- the bot will ask smart follow-ups.

## Data Completeness

1. **The `/api/integration/dashboard` endpoint is for summary stats only** — observation counts and pending reviews. Do NOT use it to list individual observations.
2. **For listing observations**, use `GET /api/observations` with appropriate filters. This endpoint is paginated — use `limit` parameter and note the total.
3. **Always state the count**: "Found 7 observations this week in field 12" — not just a list without context.
4. **If results seem low**, flag it: "Only seeing 2 observations this week — that may be incomplete, or the observations service may be having issues."
5. **If the service is down**, say so plainly. Don't present empty results as "no observations."

## API Base

http://100.102.77.110:8008

**Note:** The observations backend may have stability issues (restart loops reported). If endpoints don't respond, report that the observations service appears to be down.

## Integration Endpoints (No Auth)

### Dashboard
GET /api/integration/dashboard

Returns: Observation counts, recent activity, pending reviews.

## Authenticated Endpoints (JWT Required)

### Authentication

This skill accesses protected FarmOS endpoints that require a JWT token.

**To get a token:**
```bash
TOKEN=$(~/clawd/scripts/farmos-auth.sh manager)
```

**To use the token:**
```bash
curl -H "Authorization: Bearer $TOKEN" http://100.102.77.110:8008/api/endpoint
```

**Token expiry:** Tokens last 15 minutes. If you get a 401 response, request a new token.

### List Observations
GET /api/observations?limit=10&field_id=12
Authorization: Bearer {token}

### Observation Detail
GET /api/observations/{id}
Authorization: Bearer {token}

Returns: Full observation with AI analysis results, extracted entities, urgency score, and any created actions (tasks, maintenance records).

### Create Observation
POST /api/observations
Authorization: Bearer {token}
Content-Type: multipart/form-data

Form fields:
- `observation_type` (required) — pest, disease, weed, weather_damage, equipment_issue, soil, crop_condition, other
- `description` (required) — Text description of what was observed
- `severity` (optional) — low, medium, high (default: medium)
- `field_id` (optional) — Numeric field ID
- `equipment_id` (optional) — Numeric equipment ID
- `photo` (optional) — Image file attachment

Example using curl:
```bash
curl -X POST http://100.102.77.110:8008/api/observations \
  -H "Authorization: Bearer $TOKEN" \
  -F "observation_type=weed" \
  -F "description=Found waterhemp in northeast corner near waterway" \
  -F "severity=high" \
  -F "field_id=22" \
  -F "photo=@/path/to/photo.jpg"
```

**When crew reports a problem in #field-support or #field-ops, offer to create an observation.** Extract as much detail as you can from the message (field, observation type, severity), then create the observation.

## Usage Notes

- Observations include urgency scores (1-10). Flag anything 7+ immediately.
- AI processing classifies type and extracts equipment/field/crop references.
- Observations may create tasks (via Task Manager) or maintenance records (via Equipment).
- If the service is down, let the user know and suggest they log the observation manually.
- The observation intake system is designed for photos from the field — the bot should be ready to accept image messages and route them here.
- **Proactive observation creation:** When crew mentions issues in channel conversations ("got a bunch of weeds in field 12", "header making a weird noise"), offer to log it as an observation. Don't create silently — ask first.
- **Equipment observations:** If the observation involves equipment, include `equipment_id` when creating. This helps track equipment-specific recurring issues.


---

## Smart Observation Detection

When a user reports something that sounds like a field observation, auto-detect as much as you can from the message before asking questions.

### What to Detect

**Field identification:**
- Explicit: "field 12", "F12", "the 12"
- By name: "the Byrd farm", "Kruckeberg", "home place" -- match to known field names
- From channel context: if the conversation was already about a specific field, carry that forward
- From user location: if they mention "the field I am in" or "out here", check recent context

**Observation type** -- see the Observation Type Detection table below.

**Severity** -- see the Severity Detection table below.

**Specific pest/disease/weed identification:**
- Common Indiana pests: western corn rootworm, Japanese beetle, corn earworm, soybean aphid, bean leaf beetle, armyworm, black cutworm, stink bug
- Common diseases: tar spot, gray leaf spot, northern leaf blight, sudden death syndrome, white mold, frogeye leaf spot, Goss wilt, anthracnose
- Common weeds: waterhemp, marestail (horseweed), giant ragweed, common ragweed, Palmer amaranth, lambsquarters, foxtail, velvetleaf, morningglory
- If the reporter uses a colloquial name, map it: "buttonweed" -> common buttonweed, "volunteer corn" -> note as weed/volunteer

**Equipment reference:**
- By name/number: "the 8250", "the Kinze", "the planter", "sprayer"
- By implication: "header won't raise" implies the combine (likely 8250)

**Location within field:**
- Cardinal directions: "northeast corner", "south end"
- Landmarks: "near the waterway", "along the tree line", "by the road", "headlands", "terrace"
- Coverage: "whole field", "scattered", "in patches", "one spot"

---

## Observation Type Detection

| Keywords / Signals | Observation Type |
|--------------------|-----------------|
| bug, insect, aphid, rootworm, armyworm, beetle, cutworm, earworm, stink bug, larva, grub | pest |
| tar spot, gray leaf spot, northern leaf blight, rust, rot, blight, lesion, spots on leaves, mold, wilt, SDS, anthracnose, frogeye | disease |
| waterhemp, marestail, ragweed, foxtail, lambsquarters, Palmer, volunteer corn, weeds, escapes, resistance | weed |
| hail, wind damage, flood, frost, drought stress, storm, ice, lightning, washout, ponding | weather_damage |
| broken, leaking, stuck, noise, won't start, overheating, vibration, warning light, hydraulic, flat tire | equipment_issue |
| compaction, erosion, drainage, wet spots, tile, washout, ruts, soil test, pH | soil |
| stand count, emergence, color, lodging, population, uneven, stunted, yellowing, purpling, canopy | crop_condition |

**If multiple types match** (e.g., "yellowing leaves with spots" could be disease or crop_condition), pick the more specific one (disease in that case). If genuinely ambiguous, ask: "Is this more of a disease issue or general crop condition?"

---

## Severity Detection

| Language Signals | Severity |
|-----------------|----------|
| "bad", "terrible", "everywhere", "whole field", "never seen this before", "worst I have seen", "out of control", "lost cause" | high |
| "some", "moderate", "spreading", "getting worse", "more than last week", "quite a bit", "a lot of" | medium |
| "a few", "small patch", "just noticed", "isolated", "one spot", "not too bad", "just starting" | low |

**Default to medium** if the language is neutral or you cannot determine severity. Never guess high -- ask.

---

## Follow-Up Questions (Smart)

When the report is sparse, ask targeted follow-up questions. **Maximum 2-3 questions per interaction -- do not interrogate.**

### Question Bank (pick the most useful ones)

- **Scope:** "How widespread is it? Just that spot or across the field?"
- **Adjacent fields:** "Have you seen this in adjacent fields?"
- **Percentage:** "Roughly what percentage of the field is affected?"
- **Photos:** "Any photos? A picture would help me nail down exactly what this is."
- **Treatment history:** "Was this field treated with anything recently?"
- **Recurrence:** "Is this the same issue you reported on [date]?" (only if a similar recent observation exists -- check observation history first)
- **Timing:** "When did you first notice this?"
- **Trend:** "Is it getting worse or holding steady?"

### Which Questions to Ask

| Missing Info | Ask |
|-------------|-----|
| No field identified | "Which field are you in?" (always ask this -- cannot create without a field) |
| No type identifiable | "What are you seeing exactly? Weeds? Bugs? Crop damage? Equipment problem?" |
| Has type but no scope | "How widespread is it?" |
| Weed/pest report | "Any photos?" (visual ID is high value for these) |
| Sounds like recurring issue | "Is this the same issue from [date]?" |

---

## Reporter-Adaptive Behavior

### Detailed Reporters (agronomists, Brian, experienced crew)
- They will say things like "Found western corn rootworm beetle damage in field 22, northeast corner, about 15% of the rows affected, adult count was 8 per plant"
- **Auto-detect everything. Confirm the details. Create the observation.**
- Skip redundant questions -- they have already given you what you need
- Example response: "Got it -- rootworm beetle damage in F22, northeast corner, ~15% of rows, 8 adults/plant. Severity: high. Creating the observation now."

### Sparse Reporters (field crew, seasonal workers)
- They will say things like "something's wrong with field 12" or "beans look bad"
- **Ask 2-3 targeted follow-up questions. Do NOT interrogate.**
- Pick the highest-value questions for the situation
- After 2-3 questions, create the observation with whatever you have
- Example exchange:
  - Crew: "Beans look rough in 12"
  - Bot: "What are you seeing -- weeds, bugs, disease, or just the crop looking off? And is it the whole field or just a section?"
  - Crew: "Weeds. Northeast side mostly."
  - Bot: "Got it. Creating an observation -- weed pressure in field 12, northeast section, medium severity. Want me to create a scouting work order for it too?"

### Key Rules
- **Always offer before creating:** "Want me to create an observation for this?" Do NOT create silently -- unless the user has explicitly asked you to create one.
- **Exception:** If the user directly says "Log this" or "Create an observation for...", that IS explicit permission -- go ahead and create.
- **Never ask more than 3 follow-up questions.** After 3, create with what you have and note what was unknown.

---

## Post-Creation Actions

After successfully creating an observation, offer related actions:

- **Work order:** "Want me to create a work order for this?" (especially for weed/pest/equipment issues that need action)
- **Adjacent field check:** "Should I check if adjacent fields have the same issue?" (useful for pest/disease/weed spread)
- **Scouting task:** "Want me to schedule a follow-up scouting trip?" (for observations that need monitoring)
- **Equipment maintenance:** If equipment_issue type, "Want me to log this against the equipment maintenance record?"

Only offer 1-2 of the most relevant follow-up actions. Do not overwhelm the reporter with options.

---

## Urgency Escalation

**Flag the operator immediately** (in addition to creating the observation) for:

- **Crop damage** at high severity -- potential yield loss, Brian needs to know
- **Equipment safety** -- hydraulic leak, structural failure, anything that could injure someone
- **Chemical exposure** -- drift, spill, re-entry violation, any chemical safety concern
- **Pest/disease outbreak** -- high severity pest or disease that could spread rapidly (tar spot, sudden death syndrome, heavy rootworm pressure)
- **Weather damage** at high severity -- hail, flood, significant storm damage

When escalating, send a concise alert: "URGENT: [type] reported in field [X] -- [one-line summary]. Severity: high. Observation #[id] created."

Do NOT escalate routine observations (low/medium severity, isolated issues, normal scouting finds).


---

## Cross-Module Context

After creating or reviewing observations, connect to other modules:

**Observations → Pattern Detection:**
- When a new observation is created, check for similar recent observations (same type, nearby fields, same week): "This is the third waterhemp observation this week across three different fields. Might be time for a blanket spray program rather than spot treatments."
- When listing observations, group by pattern when multiple share type/field/timeframe: "3 disease observations this week, all in the east fields. Could be spreading."
- Track escalation: "First report was low severity last Tuesday, now we're at high severity across 4 fields. This is moving fast."

**Observations → Tasks:**
- After creating an observation, check farmos-tasks for existing work orders related to this field or issue: "There's already a scouting task open for field 22 from yesterday — want me to add this observation to it?"
- If no related task exists and the observation is actionable (pest, disease, weed at medium+ severity), offer to create one.
- Connect observation patterns to task suggestions: "Third waterhemp sighting this week — want me to create a blanket spray task?"

**Observations → Weather:**
- Connect recent weather to observation context: "3 disease observations after last week's rain — moisture likely drove this."
- When a weather_damage observation is created, pull the actual weather data: "You're reporting hail damage in field 14. Records show we got 1.2 inches with possible hail Tuesday evening."
- Flag ongoing weather risk: "With more rain coming Thursday, expect this fungal pressure to continue."

**Observations → Equipment:**
- If an observation leads to a task that requires specific equipment, check equipment availability: "If you're going to spray for this waterhemp, the sprayer is available — 153 hours, no maintenance due."
- For equipment_issue observations, cross-reference with farmos-equipment for that machine's maintenance history.

Cross-reference when it adds context. A simple "log this observation" doesn't need a full cross-module sweep. But when patterns emerge or observations drive action, connect the dots.

## Image Understanding

When a photo accompanies an observation (the image description will appear in your context as `[Image] Description: ...`), use it to enhance the observation record.

### Photo-Enhanced Detection

**Use the image description to refine type and severity:**
- Photo of lesions on leaves -- identify disease characteristics (shape, color, pattern, location on leaf) -- refine observation_type to "disease" and attempt specific ID
- Photo of insects or insect damage -- identify species or damage pattern -- refine observation_type to "pest"
- Photo of weeds -- identify species from leaf shape, growth habit, flower/seed head -- refine observation_type to "weed"
- Photo of equipment in the field -- note the machine and any visible issues -- set observation_type to "equipment_issue" and include equipment_id
- Photo of crop conditions -- note growth stage, color, stand count, uniformity -- refine observation_type to "crop_condition"
- Photo of weather damage -- note damage pattern (hail bruising, wind lodging, flood line) -- set observation_type to "weather_damage"

**Always include the image description in the observation `description` field.** Combine what the reporter said with what the photo shows:
> "Reporter: Found some weird spots on the corn in field 12. Photo shows: rectangular tan lesions between leaf veins, approximately 1-3cm long, consistent with gray leaf spot (Cercospora zeae-maydis). Northeast section of field."

### Photo Quality Handling

- **Clear photo:** Use it confidently to refine detection. State what you see and your assessment.
- **Unclear/blurry/dark photo:** Say so honestly: "I can make out [what you can see] but the photo is too blurry/dark for a confident ID. Can you get a closer shot, or describe what you are seeing?"
- **Photo does not match description:** If the photo shows something different from what the reporter described, mention it: "You mentioned weeds but the photo looks like it might be disease lesions -- can you clarify?"
- **Multiple issues visible:** Note all of them: "I can see both waterhemp and what looks like tar spot lesions in this photo. Want me to create observations for both?"

### Photo Prompt for Sparse Reports

When a reporter sends a text-only observation about something visual (pest, disease, weed, damage), and has NOT included a photo:
- "Any photos? A picture would help me nail down exactly what this is." (already in the follow-up question bank)
- Do NOT demand photos. A text description is always enough to create an observation.

### Attaching Photos to Observations

When creating an observation via `POST /api/observations`, include the photo as the `photo` form field if a MediaPath is available in your context. The image gets archived with the observation record for future reference.
