---
name: gevety
version: 1.8.0
description: Access your Gevety health data - biomarkers, healthspan scores, biological age, supplements, medications, medical profile, activities, strength training, erg results, daily actions, 90-day health protocol, upcoming tests, lab reports, health documents, and health content
homepage: https://gevety.com
user-invocable: true
command: gevety
metadata:
  clawdbot:
    primaryEnv: GEVETY_API_TOKEN
    requires:
      env:
        - GEVETY_API_TOKEN
---

# Gevety Health Assistant

You have access to the user's health data from Gevety via the REST API. Use `web_fetch` to retrieve their biomarkers, healthspan scores, and wearable statistics.

## First-Time Setup

If this is the user's first time using Gevety, guide them through setup:

1. **Get a Gevety account**: Sign up at https://gevety.com if they don't have one
2. **Upload blood tests**: They need to upload lab reports to have biomarker data
3. **Generate an API token**:
   - Go to https://gevety.com/settings
   - Click "Developer API" tab
   - Click "Generate Token"
   - Copy the token (starts with `gvt_`)
4. **Configure Clawdbot**: Add the token to `~/.clawdbot/clawdbot.json`:

```json
{
  "skills": {
    "entries": {
      "gevety": {
        "apiKey": "gvt_your_token_here"
      }
    }
  }
}
```

After adding the token, they'll need to restart Clawdbot for changes to take effect.

## Authentication

All requests require Bearer authentication. Use the `GEVETY_API_TOKEN` environment variable:

```
Authorization: Bearer $GEVETY_API_TOKEN
```

Base URL: `https://api.gevety.com`

## Biomarker Name Handling

The API preserves biomarker specificity. Fasting and non-fasting variants are distinct:

| Input Name | API Returns | Notes |
|------------|-------------|-------|
| CRP, C-Reactive Protein | **CRP** or **C-Reactive Protein** | Standard CRP (LOINC 1988-5) |
| hsCRP, hscrp, Cardio CRP | **hs-CRP** | High-sensitivity CRP (LOINC 30522-7) |
| Glucose, Blood Glucose | **Glucose** | Generic/unspecified glucose |
| Fasting Glucose, FBS, FBG | **Glucose Fasting** | Fasting-specific glucose |
| Insulin, Serum Insulin | **Insulin** | Generic/unspecified insulin |
| Fasting Insulin | **Insulin Fasting** | Fasting-specific insulin |
| IG | **Immature Granulocytes** | Expanded for clarity |
| Vitamin D, 25-OH Vitamin D | **Vitamin D** | |
| LDL, LDL Cholesterol | **LDL Cholesterol** | |

**Important**: The API no longer forces fasting assumptions. If a lab report says "Glucose" without specifying fasting, it returns as "Glucose" (not "Fasting Glucose"). This preserves the original context from your lab results.

## Available Endpoints

### 1. List Available Data (Start Here)

**Always call this first** to discover what health data exists.

```
GET /api/v1/mcp/tools/list_available_data
```

Returns:
- `biomarkers`: List of tracked biomarkers with test counts and latest dates
- `wearables`: Connected devices and available metrics
- `insights`: Whether healthspan score is calculated, axis scores available
- `data_coverage`: Percentage of recommended biomarkers tracked (0-100)

### 2. Get Health Summary

Overview of the user's health status.

```
GET /api/v1/mcp/tools/get_health_summary
```

Returns:
- `overall_score`: Healthspan score (0-100)
- `overall_status`: OPTIMAL, GOOD, SUBOPTIMAL, or NEEDS_ATTENTION
- `trend`: IMPROVING, STABLE, or DECLINING
- `axis_scores`: Scores for each health dimension (metabolic, cardiovascular, etc.)
- `top_concerns`: Biomarkers needing attention
- `scoring_note`: Explanation when overall score differs from axis scores (e.g., "Overall healthspan is high, but Inflammation axis needs attention")

**Note on scores**: The overall healthspan score is a weighted composite. It's possible to have a high overall score while one axis is low (or vice versa). The `scoring_note` field explains these situations.

### 3. Query Biomarker

Get detailed history for a specific biomarker.

```
GET /api/v1/mcp/tools/query_biomarker?biomarker={name}&days={days}
```

Parameters:
- `biomarker` (required): Name or alias (e.g., "vitamin d", "ldl", "hba1c", "crp")
- `days` (optional): History period, 1-730, default 365

Returns:
- `canonical_name`: Standardized biomarker name (see table above)
- `history`: Array of test results with dates, values, units, flags
- `latest`: Most recent result
- `trend`: Direction (IMPROVING, STABLE, DECLINING) and percent change
- `optimal_range`: Evidence-based optimal values

**Tip**: If biomarker not found, the response includes `did_you_mean` suggestions.

### 4. Get Wearable Stats

Daily metrics from connected wearables (Garmin, Oura, Whoop, etc.).

```
GET /api/v1/mcp/tools/get_wearable_stats?days={days}&metric={metric}
```

Parameters:
- `days` (optional): History period, 1-90, default 30
- `metric` (optional): Focus on specific metric (steps, hrv, sleep, etc.)

Returns:
- `connected_sources`: List of connected wearable platforms
- `daily_metrics`: Per-day data (steps, resting HR, HRV, sleep, recovery)
- `summaries`: Aggregated stats with averages, min, max, trends

### 5. Get Opportunities

Get ranked health improvement opportunities with estimated healthspan impact.

```
GET /api/v1/mcp/tools/get_opportunities?limit={limit}&axis={axis}
```

Parameters:
- `limit` (optional): Max opportunities to return, 1-50, default 10
- `axis` (optional): Filter by health axis (metabolic, cardiovascular, etc.)

Returns:
- `opportunities`: Ranked list of improvement opportunities
- `total_opportunity_score`: Total healthspan points available
- `total_years_estimate`: Estimated years of healthy life if all optimized
- `healthspan_score`: Current healthspan score

Each opportunity includes:
- `biomarker`: Standardized biomarker name
- `current_value` / `optimal_value`: Where you are vs target
- `opportunity_score`: Healthspan points gained if optimized
- `years_estimate`: Estimated healthy years gained
- `priority`: Rank (1 = highest impact)

### 6. Get Biological Age

Calculate biological age using validated algorithms (PhenoAge, Light BioAge).

```
GET /api/v1/mcp/tools/get_biological_age
```

Returns:
- `result`: Biological age calculation (if available)
  - `biological_age`: Calculated biological age
  - `chronological_age`: Calendar age
  - `age_acceleration`: Difference (positive = aging faster)
  - `algorithm`: Which algorithm was used
  - `biomarkers_used`: Biomarkers that contributed
  - `interpretation`: What the result means
- `available`: Whether calculation was possible
- `reason`: Why not available (if applicable)
- `upgrade_available`: Can unlock better algorithm with more data
- `upgrade_message`: What additional tests would help

### 7. List Supplements

Get the user's supplement stack.

```
GET /api/v1/mcp/tools/list_supplements?active_only={true|false}
```

Parameters:
- `active_only` (optional): Only show currently active supplements, default false

Returns:
- `supplements`: List of supplements with dosage, frequency, duration
- `active_count`: Number of currently active supplements
- `total_count`: Total supplements tracked

Each supplement includes:
- `name`: Supplement name
- `dose_text`: Formatted dosage (e.g., "1000 mg daily", "200mg EPA + 100mg DHA daily")
- `is_active`: Currently taking
- `duration_days`: How long on this supplement

**Note**: For multi-component supplements (like fish oil), `dose_text` shows all components (e.g., "200mg EPA + 100mg DHA daily").

### 8. Get Activities

Get workout/activity history from connected wearables.

```
GET /api/v1/mcp/tools/get_activities?days={days}&activity_type={type}
```

Parameters:
- `days` (optional): History period, 1-90, default 30
- `activity_type` (optional): Filter by type (running, cycling, strength, etc.)

Returns:
- `activities`: List of workouts with metrics
- `total_count`: Number of activities
- `total_duration_minutes`: Total workout time
- `total_distance_km`: Total distance covered
- `total_calories`: Total calories burned

Each activity includes:
- `activity_type`: Type (running, cycling, swimming, etc.)
- `name`: Activity name
- `start_time`: When it started
- `duration_minutes`: How long
- `distance_km`: Distance (if applicable)
- `calories`: Calories burned
- `avg_hr` / `max_hr`: Heart rate data
- `source`: Where the data came from (garmin, strava, hevy, concept2, etc.)
- `elevation_gain_m`: Elevation gain in meters (outdoor activities)
- `avg_pace_min_per_km`: Average running pace
- `avg_watts`: Average cycling power
- `strain_score`: Whoop strain (0-21)
- `avg_cadence`: Cadence (RPM or steps/min)
- `is_indoor`: Indoor activity flag
- `total_volume_kg`: Total weight lifted (Hevy strength workouts)
- `exercise_count`: Number of exercises (Hevy)
- `set_count`: Number of sets (Hevy)
- `pace_500m`: Pace per 500m (Concept2 erg sessions)
- `stroke_rate`: Strokes per minute (Concept2)
- `machine_type`: Erg machine type — rower, skierg, bikerg (Concept2)

**Note**: Source-specific fields (volume, pace, stroke rate, etc.) are only populated for the relevant source. For example, `total_volume_kg` only appears on Hevy activities and `pace_500m` only on Concept2 activities.

### 9. Get Today's Actions

Get the user's action checklist for today.

```
GET /api/v1/mcp/tools/get_today_actions?timezone={timezone}
```

Parameters:
- `timezone` (optional): IANA timezone (e.g., "America/New_York"), default UTC

Returns:
- `effective_date`: The date being queried in user's timezone
- `timezone`: Timezone used for calculation
- `window_start` / `window_end`: Day boundaries (ISO datetime)
- `actions`: List of today's actions
- `completed_count` / `total_count`: Completion stats
- `completion_pct`: Numeric completion percentage (0-100)
- `last_updated_at`: Cache staleness indicator

Each action includes:
- `action_id`: Stable ID for deep-linking
- `title`: Action title
- `action_type`: Type (supplement, habit, diet, medication, test, procedure)
- `completed`: Whether completed today
- `scheduled_window`: Time window (morning, afternoon, evening, any)
- `dose_text`: Dosage info if applicable (e.g., "1000 mg daily")

### 10. Get Protocol

Get the user's 90-day health protocol with top priorities.

```
GET /api/v1/mcp/tools/get_protocol
```

Returns:
- `protocol_id`: Stable protocol ID
- `phase`: Current phase (week1, month1, month3)
- `days_remaining`: Days until protocol expires
- `generated_at` / `last_updated_at`: Timestamps
- `top_priorities`: Top 5 health priorities with reasoning
- `key_recommendations`: Diet and lifestyle action items
- `total_actions`: Total actions in protocol

Each priority includes:
- `priority_id`: Stable ID (same as rank)
- `rank`: Priority rank (1 = highest)
- `biomarker`: Standardized biomarker name
- `status`: Current status (critical, concerning, suboptimal, optimal)
- `target`: Target value with unit
- `current_value` / `unit`: Current measured value
- `measured_at`: When this biomarker was last measured
- `why_prioritized`: Explanation for why this is prioritized

**Note**: If no protocol exists, returns a helpful error with suggestion to generate one at gevety.com/protocol.

### 11. Get Upcoming Tests

Get tests that are due or recommended based on biomarker history and AI recommendations.

```
GET /api/v1/mcp/tools/get_upcoming_tests
```

Returns:
- `tests`: List of upcoming tests sorted by urgency
- `overdue_count`: Number of overdue tests
- `due_soon_count`: Tests due within 30 days
- `recommended_count`: AI-recommended tests
- `total_count`: Total number of upcoming tests

Each test includes:
- `test_id`: Stable ID for deep-linking (format: `panel_{id}` or `recommended_{id}`)
- `name`: Test or panel name
- `test_type`: Type (panel, biomarker, recommended)
- `urgency`: Priority level (overdue, due_soon, recommended)
- `due_reason`: Why this test is needed (e.g., "Due 2 weeks ago", "AI recommendation")
- `last_tested_at`: When this was last tested (if applicable)
- `biomarkers`: List of biomarkers included (for panels)

### 12. List Test Results

Get a list of uploaded lab reports with dates, source, and biomarker count.

```
GET /api/v1/mcp/tools/list_test_results?limit={limit}&start_date={date}&end_date={date}
```

Parameters:
- `limit` (optional): Max reports to return, 1-50, default 10
- `start_date` (optional): Filter from date (YYYY-MM-DD)
- `end_date` (optional): Filter to date (YYYY-MM-DD)

Returns:
- `reports`: List of lab reports
- `total_reports`: Total number of reports

Each report includes:
- `report_id`: Stable report ID
- `report_date`: Date of the lab test
- `source`: How it was uploaded (pdf, email, manual)
- `lab_name`: Laboratory name (if available)
- `biomarker_count`: Number of biomarkers in this report
- `filename`: Original filename (if uploaded as PDF)

### 13. List All Biomarkers

Get ALL tracked biomarkers with current value, status classification, and trend in one call.

```
GET /api/v1/mcp/tools/list_all_biomarkers?category={category}&status={status}
```

Parameters:
- `category` (optional): Filter by category (e.g., "metabolic", "cardiovascular")
- `status` (optional): Filter by status (optimal, suboptimal, high, low, critical_high, critical_low)

Returns:
- `biomarkers`: List of all biomarkers with latest values
- `total_count`: Total number of biomarkers
- `counts_by_status`: Breakdown by status (optimal, suboptimal, high, low, critical_high, critical_low, unknown)

Each biomarker includes:
- `name`: Standardized biomarker name
- `category`: Health category (metabolic, cardiovascular, etc.)
- `latest_value`: Most recent test value
- `unit`: Measurement unit
- `status`: Classification (optimal, suboptimal, high, low, critical_high, critical_low, unknown)
- `last_test_date`: When this was last tested
- `trend_direction`: Trend since previous test (increasing, decreasing, stable)

### 14. Get Content Recommendations

Get personalized health content recommendations based on biomarker profile.

```
GET /api/v1/mcp/tools/get_content_recommendations?limit={limit}&category={category}
```

Parameters:
- `limit` (optional): Max recommendations, 1-20, default 5
- `category` (optional): Filter by content category

Returns:
- `recommendations`: List of recommended articles
- `total_available`: Total recommendations available

Each recommendation includes:
- `content_id`: Stable content ID
- `title`: Article title
- `summary`: Brief summary
- `category`: Content category
- `relevance_reason`: Why this is relevant to the user
- `quality_score`: Evidence quality score (only high-quality content is shown)
- `url`: Link to the article

### 15. Get Strength Training

Get detailed strength training data from Hevy (workouts, volume, muscle distribution).

```
GET /api/v1/mcp/tools/get_strength_training?days={days}&muscle_group={group}
```

Parameters:
- `days` (optional): History period, 1-90, default 30
- `muscle_group` (optional): Filter by muscle group (e.g., "chest", "back", "legs")

Returns:
- `workouts`: List of strength workouts with exercises, sets, and volume
- `total_workouts`: Total workout count
- `total_volume_kg`: Total weight lifted
- `avg_sessions_per_week`: Training frequency
- `muscle_distribution`: Volume breakdown by muscle group (with percentages)
- `weekly_volume`: Weekly volume trend data

Each workout includes:
- `started_at`: When the workout started
- `duration_minutes`: Workout duration
- `total_volume_kg`: Total volume for this workout
- `exercise_count` / `set_count`: Number of exercises and sets
- `exercises`: Detailed exercise list with name, muscle group, sets, top set weight, total volume, total reps
- `enrichment_source`: If enriched with HR data from another wearable (garmin, strava, etc.)
- `enrichment_avg_hr`: Average HR from enrichment source

**Note**: Requires Hevy connection. Returns error if user has no Hevy integration.

### 16. Get Erg Results

Get Concept2 ergometer results (rowing, skiing, biking).

```
GET /api/v1/mcp/tools/get_erg_results?days={days}&machine_type={type}
```

Parameters:
- `days` (optional): History period, 1-90, default 30
- `machine_type` (optional): Filter by machine — rower, skierg, bikerg

Returns:
- `sessions`: List of erg sessions with detailed metrics
- `total_sessions`: Total session count
- `total_meters`: Total distance
- `total_time_seconds`: Total time on erg
- `avg_pace_formatted`: Overall average pace per 500m (e.g., "2:05.3")
- `machines`: Per-machine summary (session count, total meters, avg pace)
- `weekly_volume`: Weekly volume trend data

Each session includes:
- `date`: Session date
- `machine_type`: rower, skierg, or bikerg
- `distance_meters`: Distance in meters
- `time_seconds`: Duration in seconds
- `pace_500m`: Pace per 500m formatted (e.g., "2:05.3")
- `calories`: Calories burned
- `stroke_rate`: Average strokes per minute
- `avg_hr`: Average heart rate (if available)
- `drag_factor`: Erg drag factor setting

**Note**: Requires Concept2 connection. Returns error if user has no Concept2 integration.

### 17. List Medications

Get the user's prescription medications.

```
GET /api/v1/mcp/tools/list_medications?active_only={true|false}
```

Parameters:
- `active_only` (optional): Only show currently active medications, default true

Returns:
- `medications`: List of medications with dosage, frequency, route, and reason
- `active_count`: Number of currently active medications
- `total_count`: Total medications tracked

Each medication includes:
- `name`: Medication name (brand)
- `generic_name`: Generic/active ingredient name
- `dosage`: Dosage (e.g., "500mg")
- `frequency`: How often taken (e.g., "twice daily")
- `route`: Route of administration (oral, topical, injection, etc.)
- `is_active`: Currently taking
- `start_date` / `end_date`: When started/stopped
- `duration_days`: How long on this medication
- `reason`: Why prescribed (auto-decrypted from encrypted storage)

### 18. Get Medical Profile

Get the user's medical profile including conditions, allergies, family history, and health goals.

```
GET /api/v1/mcp/tools/get_medical_profile
```

Returns:
- `conditions`: List of medical conditions (active/managed)
- `allergies`: List of allergies with severity and reaction type
- `family_history`: Family medical history with relationships and onset ages
- `goals`: Active health goals with priorities and target dates
- `diet_type`: Current dietary pattern (if set)
- `condition_count` / `allergy_count`: Summary counts

Each condition includes: `name`, `status` (active/managed/resolved/monitoring), `severity`, `diagnosed` date, `notes`

Each allergy includes: `allergen`, `severity` (mild/moderate/severe/life_threatening), `reaction_type`

Each family history item includes: `condition`, `relationship` (father/mother/etc.), `age_at_onset`, `notes`

### 19. List Health Documents

List all health documents including procedure reports, imaging, prescriptions, and more.

```
GET /api/v1/mcp/tools/list_health_documents?limit={limit}&document_type={type}
```

Parameters:
- `limit` (optional): Max documents to return, 1-50, default 20
- `document_type` (optional): Filter by type (lab_report, procedure_report, imaging, prescription, doctor_note, other)

Returns:
- `documents`: List of health documents sorted by received date (newest first)
- `total_count`: Total documents for this user
- `by_type`: Breakdown of document counts by type

Each document includes:
- `document_id`: Document ID
- `document_type`: Type (lab_report, procedure_report, imaging, etc.)
- `document_subtype`: Subtype (cac, dexa, colonoscopy, mammogram, etc.)
- `status`: Processing status (pending, processing, needs_review, extracted, archived)
- `filename`: Original filename
- `received_at`: When received (ISO format)
- `ai_summary`: AI-generated summary of the document
- `lab_name`: Lab name (for lab reports)
- `test_date`: Test/procedure date

**Note**: This goes beyond `list_test_results` which only shows lab reports. This includes ALL uploaded documents — procedure reports (CAC, DEXA, colonoscopy), imaging studies, prescriptions, and doctor notes.

## Interpreting Scores

### Healthspan Score (0-100)
| Range | Status | Meaning |
|-------|--------|---------|
| 80-100 | OPTIMAL | Excellent health optimization |
| 65-79 | GOOD | Above average, minor improvements possible |
| 50-64 | SUBOPTIMAL | Room for improvement |
| <50 | NEEDS_ATTENTION | Several areas need focus |

### Axis Scores
Each health dimension is scored independently:
- **Metabolic**: Blood sugar, insulin, lipids
- **Cardiovascular**: Heart health markers
- **Inflammatory**: hs-CRP, homocysteine
- **Hormonal**: Thyroid, testosterone, cortisol
- **Nutritional**: Vitamins, minerals
- **Liver/Kidney**: Organ function markers

**Important**: It's possible to have a high overall score with one low axis score (or vice versa). The `scoring_note` field in `get_health_summary` explains these situations.

### Biomarker Status Labels
| Label | Meaning |
|-------|---------|
| OPTIMAL | Within evidence-based ideal range |
| NORMAL | Within lab reference range |
| SUBOPTIMAL | Room for improvement |
| HIGH/LOW | Outside lab reference range |
| CRITICAL | Needs immediate medical attention |

## Common Workflows

### "How am I doing?"
1. Call `list_available_data` to see what's tracked
2. Call `get_health_summary` for the overall picture
3. Highlight top concerns and recent trends
4. If `scoring_note` is present, explain the score discordance

### "Tell me about my vitamin D"
1. Call `query_biomarker?biomarker=vitamin d`
2. Present history, current status, and trend
3. Note optimal range vs current value

### "What's my CRP?" / "How's my inflammation?"
1. Call `query_biomarker?biomarker=crp` (returns as "CRP" or "hs-CRP" depending on lab)
2. Present the value and trend
3. Explain what CRP measures (inflammation marker) - note if it's high-sensitivity

### "How's my sleep/HRV?"
1. Call `get_wearable_stats?metric=sleep` or `?metric=hrv`
2. Show recent trends and averages
3. Compare to healthy baselines

### "What should I focus on?"
1. Call `get_opportunities?limit=5`
2. Present top opportunities ranked by healthspan impact
3. Explain what each biomarker does and why optimizing it matters

### "How old am I biologically?"
1. Call `get_biological_age`
2. If available, compare biological vs chronological age
3. Explain what age acceleration means
4. If not available, explain what tests are needed

### "What supplements am I taking?"
1. Call `list_supplements?active_only=true`
2. List active supplements with dosages (use `dose_text` field)
3. Note duration on each supplement

### "What workouts have I done?"
1. Call `get_activities?days=30`
2. Summarize total activity (duration, calories, distance)
3. List recent workouts with key metrics

### "What should I do today?"
1. Call `get_today_actions?timezone=America/New_York` (use user's timezone if known)
2. Group actions by scheduled window (morning, afternoon, evening)
3. Show completion progress
4. Highlight uncompleted actions

### "What should I focus on?" / "What are my health priorities?"
1. Call `get_protocol`
2. Present top priorities with current values and targets
3. Explain why each is prioritized
4. List key recommendations
5. Note protocol phase and days remaining

### "What tests should I do next?" / "Am I due for any blood work?"
1. Call `get_upcoming_tests`
2. Highlight overdue tests first (urgent)
3. List tests due soon with timeframes
4. Mention AI-recommended tests for optimization
5. Note which biomarkers each panel covers

### "Show me my lab reports" / "When was my last blood test?"
1. Call `list_test_results?limit=10`
2. Show reports with dates, lab names, and biomarker counts
3. Note the source (PDF upload, email, manual entry)

### "Give me a full overview of all my biomarkers"
1. Call `list_all_biomarkers`
2. Group by category (metabolic, cardiovascular, etc.)
3. Highlight any critical or high/low values
4. Show status counts (e.g., "12 optimal, 3 suboptimal, 1 high")
5. Note trends (increasing/decreasing/stable)

### "Show me my strength training" / "How's my lifting?"
1. Call `get_strength_training?days=30`
2. Summarize workout frequency and total volume
3. Show muscle group distribution (highlight any imbalances)
4. List recent workouts with top exercises

### "Show me my rowing results" / "How are my erg sessions?"
1. Call `get_erg_results?days=30`
2. Summarize total sessions, distance, and average pace
3. Show per-machine breakdown if using multiple ergs
4. Highlight pace trends (improving/declining)

### "What medications am I on?" / "What prescriptions do I take?"
1. Call `list_medications?active_only=true`
2. List active medications with dosage and frequency
3. Note route and reason if available
4. To see historical medications too, use `active_only=false`

### "What are my medical conditions?" / "Do I have any allergies?"
1. Call `get_medical_profile`
2. Present conditions with status and severity
3. List allergies with severity levels
4. Show family history (relevant for risk assessment)
5. Note active health goals

### "Show me all my health documents" / "What procedure reports do I have?"
1. Call `list_health_documents?limit=20`
2. Show type breakdown (lab reports, procedures, imaging, etc.)
3. List documents with AI summaries
4. Filter by type if user asks about specific category: `document_type=procedure_report`

### "What should I read about?" / "Any health articles for me?"
1. Call `get_content_recommendations?limit=5`
2. Present articles with titles and relevance reasons
3. Explain why each is relevant to the user's biomarker profile

## Example API Call

```javascript
// Using web_fetch
web_fetch({
  url: "https://api.gevety.com/api/v1/mcp/tools/get_health_summary",
  method: "GET",
  headers: {
    "Authorization": "Bearer $GEVETY_API_TOKEN",
    "Content-Type": "application/json"
  }
})
```

## Important Guidelines

1. **Never diagnose** - Present data clearly but always suggest consulting healthcare providers for medical decisions
2. **Trends matter more than single values** - A slightly elevated reading improving over time is better than a normal reading that's declining
3. **Note data freshness** - Lab results may be weeks/months old; wearable data is typically daily
4. **Context is key** - Ask about supplements, medications, or lifestyle changes that might explain trends
5. **Privacy first** - Health data is sensitive; don't share or reference specific values outside this conversation

## Error Handling

| Error Code | Meaning | Action |
|------------|---------|--------|
| 401 | Invalid or expired token | User needs to regenerate token at gevety.com/settings |
| 404 + `did_you_mean` | Biomarker not found | Suggest alternatives from the response |
| 404 | No data found | User may not have uploaded labs yet |
| 429 | Rate limited | Wait a moment and retry |

## Getting a Token

Users can generate their API token at:
**https://gevety.com/settings** → Developer API → Generate Token

The token format is `gvt_` followed by random characters.

## Checking for Updates

On first use each session, optionally check for updates:

```
GET https://api.gevety.com/api/v1/mcp/tools/status
```

No authentication required. If the request fails or times out, skip the check and proceed normally.

Response (when successful):
```json
{
  "clawdbot_skill": { "latest": "1.8.0", "update_command": "clawdhub update gevety" },
  "announcement": "New feature available!"
}
```

**If `clawdbot_skill.latest` > 1.8.0** (this skill's version), tell the user:
> "A Gevety skill update is available. Run: `clawdhub update gevety`"

**If `announcement` is present**, mention it once per session.

**If the status check fails**, don't mention it - just proceed with the user's request.

To manually update:
```bash
clawdhub update gevety
```
