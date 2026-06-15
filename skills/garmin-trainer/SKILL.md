---
name: garmin-trainer
description: Adaptive 12-week training plan generator using Garmin Connect data. Creates structured workouts and schedules them on your Garmin calendar. Use this skill whenever the user asks about training plans, workout scheduling, race preparation, building fitness for upcoming events, or wants to generate/update their training calendar. Also triggers when the user mentions Garmin training, weekly workouts, taper plans, base building, interval sessions, or periodization.
homepage: https://github.com/bpauli/gccli
metadata: {"clawdbot":{"emoji":"🏋️","os":["darwin","linux"],"requires":{"bins":["gccli"]},"install":[{"id":"homebrew","kind":"brew","formula":"bpauli/tap/gccli","bins":["gccli"],"label":"Homebrew (recommended)"},{"id":"source","kind":"source","url":"https://github.com/bpauli/gccli","bins":["gccli"],"label":"Build from source (Go 1.24+)"}]}}
---

# Garmin Trainer

Generate an adaptive 12-week training plan based on real Garmin Connect data. The plan accounts for all upcoming events (races across different sports), current fitness level, recent training load, and recovery status. Each run of this skill pulls fresh data so the plan stays current.

For all gccli command examples (data gathering, workout creation, scheduling), read `references/gccli-commands.md`.

## Step 0: Choose a Training Philosophy

Before building the plan, ask the user which coaching philosophy to follow. Present these six options — each shapes how the plan balances intensity, volume, strength work, and recovery:

### 1. Joe Friel — Periodization Bible
Based on "The Triathlete's Training Bible". Classic structured periodization with distinct phases (base → build → peak → race). Strength training is integral, progressing from anatomical adaptation (high rep, low weight) through max strength to explosive power as the season advances. Includes year-round mobility work. Best for athletes who like structure and measurable progression.

- **Intensity split**: ~75% easy / 5% tempo / 20% high intensity (shifts across phases)
- **Strength**: 2-3x/week in base phase (full-body compound lifts), tapering to 1x/week maintenance closer to events
- **Mobility**: dynamic stretching before sessions, 10-15min flexibility routine post-workout

### 2. Matt Fitzgerald — 80/20 Polarized
From "80/20 Triathlon". Strictly 80% of training time at low intensity (zones 1-2), 20% at moderate-to-high intensity (zones 3-5). No junk miles in between. Research-backed approach that builds a massive aerobic engine while keeping the hard sessions truly hard. Supplemental strength focused on injury prevention rather than performance.

- **Intensity split**: 80% easy (strictly enforced) / 20% moderate-to-hard
- **Strength**: 2x/week functional strength and injury prevention (single-leg work, hip stability, core)
- **Mobility**: foam rolling and dynamic mobility as part of warmup/cooldown routines

### 3. Phil Maffetone — MAF Method
Heart rate-based aerobic development. All easy training stays below the MAF heart rate (180 minus age, adjusted for health/fitness). Build a huge aerobic base before adding any intensity. Holistic philosophy that treats nutrition, sleep, and stress management as part of training. Strength is bodyweight and functional movement focused.

- **Intensity split**: 90-100% below MAF HR in base building, intensity added only when aerobic base plateaus
- **MAF HR formula**: 180 - age (subtract 5 if recovering from illness/injury, add 5 if consistently training 2+ years injury-free)
- **Strength**: 2x/week bodyweight and functional movement (planks, lunges, squats, hip bridges)
- **Mobility**: daily 15-20min routine — yoga-style flows, hip openers, thoracic spine mobility. Treated as non-negotiable, not optional

### 4. Kristian Blummenfelt — Norwegian Method
Threshold-heavy, data-driven approach pioneered by coach Olav Aleksander Bu. High volume of lactate-guided threshold work — more time at threshold than traditional plans, but carefully controlled via lactate (or HR proxy). Double sessions common. Strength training is functional and explosive, supporting sport-specific power. Very demanding — best for experienced athletes with a solid training base.

- **Intensity split**: ~75% easy / 20% threshold / 5% VO2max (notably more threshold than other methods)
- **Strength**: 2-3x/week functional and explosive work (Olympic lift derivatives, plyometrics, heavy squats)
- **Mobility**: integrated into warmup routines, focused on range of motion for swim/bike/run efficiency

### 5. Dan Lorang — Data-Driven Individualization
Coach of Jan Frodeno and Anne Haug (both Ironman world champions). Highly individualized, technology-driven approach that relies on power meters, lactate diagnostics, and continuous data analysis. Periodization is fluid rather than rigid — training blocks are adjusted based on real-time performance data, not fixed calendars. Combines high aerobic volume with precisely dosed threshold and VO2max work. Strength training is sport-specific and prevention-oriented, designed to support the demands of each discipline rather than build general strength.

- **Intensity split**: ~80% low intensity / 15% threshold / 5% VO2max (but distribution shifts dynamically based on data)
- **Key principle**: every session has a clear physiological purpose — no filler workouts. If the data says rest, you rest.
- **Strength**: 2-3x/week sport-specific and preventive (core stability, hip/glute activation, rotator cuff for swim, single-leg work for run). Periodized — heavier in off-season/base, lighter and more explosive closer to events.
- **Mobility**: daily activation and mobility routines (10-15min), focused on individual limiters identified through movement screening

### 6. Mark Allen — Balanced Holistic
Six-time Ironman world champion, trained under Phil Maffetone but added his own emphasis on mental preparation and whole-body balance. Combines aerobic base building with progressive race-specific intensity. Yoga and flexibility are core components, not afterthoughts. Strength work focuses on muscular balance and injury resilience.

- **Intensity split**: ~80% aerobic base / 15% tempo-threshold / 5% race-pace and above
- **Strength**: 2x/week — balanced full-body work emphasizing posterior chain and core stability
- **Mobility**: 2-3x/week dedicated yoga or stretching sessions (30-45min), daily post-workout flexibility

If the user has previously selected a philosophy, remember it and mention it — but always offer to change. If the user doesn't care or is unsure, default to **Matt Fitzgerald 80/20** as a well-rounded starting point.

Note: Dan Lorang's approach is the most adaptive — it naturally aligns with this skill's re-run behavior. When using Lorang's philosophy, lean even more heavily on the Garmin data (training status, HRV, training load tunnel) to decide session intensity day-by-day rather than following a rigid week-by-week plan.

## Running Target Mode

The running target mode (heart rate or pace) is set automatically based on the chosen training philosophy. Cycling always uses power (watts).

| Philosophy | Running Mode | Rationale |
|---|---|---|
| Joe Friel | Heart rate | Periodization phases are defined by HR zones; base building relies on staying in aerobic HR range |
| Matt Fitzgerald | Pace | 80/20 intensity is enforced via pace zones; hard sessions need precise pace targets |
| Phil Maffetone | Heart rate | MAF method is entirely HR-driven (180-age formula) |
| Kristian Blummenfelt | Pace | Threshold work requires precise pace control; lactate-guided sessions translate to pace targets |
| Dan Lorang | Pace | Data-driven approach optimizes for measurable output; pace is the running equivalent of cycling power |
| Mark Allen | Heart rate | Built on Maffetone's aerobic base philosophy; HR keeps easy sessions honest |

Derive the target values from the athlete's data:
- **HR zones**: from recent activity HR zone data, resting HR, and max HR
- **Pace zones**: from lactate threshold pace, recent race/tempo efforts, and easy run averages
- **Power zones**: from FTP (cycling)

See `references/gccli-commands.md` for workout creation examples in both modes.

## Workout Types Beyond Sport-Specific Training

Regardless of which events are on the calendar, every week should include strength and mobility sessions based on the chosen philosophy. These keep the athlete robust, prevent injury, and support long-term performance.

Strength and mobility volume should scale with the philosophy and training phase:
- Reduce strength volume (but maintain frequency) during taper weeks
- During recovery weeks, keep mobility sessions but make strength optional
- In base phases, strength can be more ambitious (heavier, more volume)

Schedule strength on easy or rest-adjacent days (e.g., Tuesday and/or Friday). See `references/gccli-commands.md` for creation examples.

## Workflow

### Step 1: Gather Data

Collect all relevant data from Garmin Connect in parallel. Always use `--json` for parseable output. See `references/gccli-commands.md` — "Data Gathering" section for all commands.

Gather:
- Events and existing scheduled workouts (next 84 days)
- Recent activities (last 4-6 weeks, up to 50)
- Current fitness: training status, training readiness, VO2max/max metrics, HRV, resting HR, sleep
- Performance benchmarks: lactate threshold, cycling FTP
- Splits and HR zones for the last 2-3 key activities per sport type

### Step 2: Analyze the Athlete

From the gathered data, build an athlete profile:

- **Sport types trained**: which sports appear in recent activities (running, cycling, swimming, etc.)
- **Weekly volume**: average distance and duration per sport over the last 4 weeks
- **Intensity distribution**: how much time at easy vs. threshold vs. high intensity (from HR zones)
- **Current paces/power**: derive training zones from recent activity data, lactate threshold, and FTP
- **Training status**: Garmin's training status value (1=detraining, 2=recovery, 3=maintaining, 4=productive, 5=peaking, 6=overreaching, 7=unproductive)
- **Weekly training load**: current load vs. the optimal load tunnel (loadTunnelMin/Max)
- **Recovery signals**: HRV trends, resting HR, sleep quality, training readiness score

### Step 3: Map All Events

This is critical — scan ALL events in the 12-week window, not just the nearest one. Events drive the plan structure.

For each event, determine:
- **Date** and **sport type** (running, cycling, trail_running, triathlon, etc.)
- **Distance** (from `completionTarget`)
- **Goal time** (from `eventCustomization.customGoal` if set)
- **Is it a race?** (`race: true`)
- **Priority level** — from `eventCustomization` in the JSON:
  - **Primary** (`isPrimaryEvent: true`): the athlete's A-race, the main goal everything builds toward
  - **Training** (`isTrainingEvent: true`): a B-race or preparation event, important but subordinate to the primary event
  - **Unclassified** (both false): a C-event, treated as a training opportunity with no special plan adjustments

**How priority shapes the plan:**

| Aspect | Primary (A) | Training (B) | Unclassified (C) |
|---|---|---|---|
| Taper | Full taper (1-2 weeks, volume -40-60%) | Short taper (3-5 days, volume -20-30%) | No taper |
| Recovery after | Full recovery week (volume -50%) | 2-3 easy days | Continue normal training |
| Specificity | Dedicated build phase with race-pace sessions | Some sport-specific sessions woven in | Train through, no plan changes |
| Volume share | Gets the majority of weekly training volume | Moderate share alongside primary sport | Minimal — fit into existing schedule |
| Goal pacing | Workouts target goal pace/power if set | Workouts at moderate race effort | Easy/moderate effort on the day |

When multiple events exist, the primary event anchors the plan. Training events are stepping stones — use them to practice race execution and build confidence, but don't sacrifice primary event preparation for them. Unclassified events are just dates on the calendar; schedule around them but don't restructure training for them.

Sort events chronologically. The plan must build toward each event with appropriate specificity and include recovery between events. For example, if a half marathon (Training) on week 6 is followed by a marathon (Primary) on week 10, the plan prioritizes the marathon:
- Build phase with increasing volume (weeks 1-5)
- Short taper + half marathon as race-pace dress rehearsal (week 6)
- Brief recovery then peak training block (weeks 7-8)
- Full taper for the marathon (weeks 9-10)
- Recovery + base (weeks 11-12)

If no events exist in the window, build a general fitness plan based on the sports the athlete currently trains.

### Step 4: Design the Plan

Apply the chosen training philosophy to structure the 12 weeks. The philosophy determines the intensity distribution, strength/mobility frequency, and how aggressively to periodize.

**General structure per training block (leading to an event):**
- **Base/Build phase**: progressive overload, increase volume ~10% per week
- **Specific phase**: race-pace workouts, event-specific sessions
- **Taper**: reduce volume 40-60% while maintaining intensity, 1-2 weeks before the event
- **Recovery**: easy week after a race event (reduce volume 50%)

**Weekly pattern:**
- Monday is always a rest day
- Sunday is the long session day (long run, long ride)
- 1-2 key quality sessions per sport on weekdays (intervals, tempo)
- Strength sessions on easy or rest-adjacent days (e.g., Tuesday and/or Friday)
- Mobility/yoga sessions per the philosophy's prescription
- Easy/recovery sessions between hard days
- Never schedule hard sessions on Saturday — keep it easy or off to prepare for Sunday's long session

**Intensity distribution** — follow the chosen philosophy's split (e.g., 80/20 for Fitzgerald, threshold-heavy for Norwegian) and apply it to the athlete's actual training zones derived from their data.

**Multi-sport considerations:**
- When training for events in different sports, interleave sport-specific sessions
- Avoid stacking hard sessions in different sports on consecutive days
- The primary event gets the lion's share of training volume; training events get moderate share
- Use cross-training benefits (e.g., cycling aerobic base supports running)
- Strength and mobility sessions support all sports — don't drop them even when single-sport focused

**Intensity targets** — derive from the athlete's actual data:
- Easy pace: from recent easy run data or ~60-70% max HR (for MAF: use 180-age formula)
- Tempo/threshold: from lactate threshold or recent threshold efforts
- Interval: from recent fast segments or ~90-95% max HR
- Cycling power zones: from FTP if available

### Step 5: Create Workouts and Schedule

For each workout in the plan, create it via `gccli workouts create` and then schedule it. Use the athlete's chosen running target mode (pace or HR). Cycling always uses power.

Read `references/gccli-commands.md` for full command syntax and examples covering all workout types (running pace/HR, cycling power, strength, mobility) and scheduling/cleanup operations.

**Naming convention**: prefix with the week number (W1, W2, ...) and include the session purpose and key metric, e.g. "W3 Tempo Run 25min @4:45", "W5 Long Run 16km", "W8 FTP Intervals 5x6min".

### Step 6: Present the Plan

After scheduling all workouts, present a summary to the user:

1. **Philosophy**: which coaching philosophy is applied and what that means in practice
2. **Event overview**: list all events in the 12-week window with dates, goals, and priority (A/B/C)
3. **Phase breakdown**: which weeks are base, build, taper, recovery
4. **Weekly summary table**: for each week show planned sessions including strength and mobility, total volume per sport, and key workouts
5. **Training zones used**: the pace/power/HR values the plan is based on
6. **Strength & mobility plan**: weekly frequency and focus areas per phase
7. **Adaptation notes**: what changed compared to the previous plan if this is a re-run (e.g., "reduced volume in week 3 because recent training load is above the optimal tunnel")

## Re-running the Plan

When the user re-runs this skill, the plan should adapt:

- Pull all fresh data (Step 1) to see what actually happened vs. what was planned
- Compare completed activities against scheduled workouts to assess adherence
- If the athlete missed workouts or is behind on volume, don't try to "catch up" — adjust the remaining weeks to build gradually from where they actually are
- If the athlete is ahead of schedule or training load is high, consider adding a recovery week
- If training status shows overreaching, reduce intensity and volume
- Check if any new events were added and restructure phases accordingly

Before scheduling new workouts, automatically remove all existing future scheduled workouts created by this skill (identifiable by the "W" prefix naming convention like "W3 Tempo Run"). Do not ask for confirmation — these are skill-managed workouts. For workouts that don't match the W-prefix pattern (user-created), leave them in place and schedule around them.

See `references/gccli-commands.md` — "Scheduling & Cleanup" section for commands.

## Important Principles

- **Be conservative with volume increases.** Never increase weekly volume more than 10-15% week-over-week. If the athlete's recent volume is low, start from where they are, not where they "should" be.
- **Recovery is training.** Always include recovery weeks (every 3-4 weeks) and post-race recovery.
- **Specificity matters.** The closer to an event, the more sport-specific the training should be.
- **Use real data.** Every pace, power, and HR target should come from the athlete's actual Garmin data, not from generic tables.
- **Respect the schedule.** Don't schedule workouts on days where the athlete already has non-training commitments visible in their calendar.
- **Respect user workouts.** If existing scheduled workouts don't match the W-prefix pattern (i.e., the user manually scheduled them), leave them in place and plan around them.
