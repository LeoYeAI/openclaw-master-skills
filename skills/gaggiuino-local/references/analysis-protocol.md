# Analysis Protocol

Gaggiuino-specific diagnostic and control notes preserved from the original skill.

## Scope

Use this file when:
- analyzing real Gaggiuino shot data,
- interpreting raw shot telemetry,
- reasoning about phase behavior,
- deciding whether a shot followed its intended control mode.

## Core Analysis Protocol: Target vs Limit

To avoid misreading advanced profiles, always distinguish between **targets** and **limits** based on phase `type`.

For analysis, use the wrapper's phase-aware datapoints rather than raw machine field names:
- flow-mode datapoints expose `pumpFlowTarget` + `pressureLimit`
- pressure-mode datapoints expose `pressureTarget` + `pumpFlowLimit`

### Flow phases (`type: flow`)
- **Primary target**: flow target
- **Static limit**: pressure limit
- **Interpretation:**
  - the shot is succeeding when actual flow tracks the flow target
  - **"Full Throttle" Exception**: vibration pumps physically max out at around **7-8 ml/s** under puck resistance. If a profile sets an unusually high flow target (e.g., $\ge$ 10 ml/s), treat it as a command to run the pump at 100% capacity. If actual flow plateaus in the 6-8 ml/s range, treat the execution as **perfect/maxed out**. Do **not** advise grinding coarser just to chase a 10+ ml/s command.
  - lower pressure is often normal and desirable
  - do **not** recommend increasing pressure if flow targets are being met
  - pressure only becomes a problem when it crashes suddenly or slams into the pressure ceiling unexpectedly

### Pressure phases (`type: pressure`)
- **Primary target**: pressure target
- **Static limit**: flow limit
- **Interpretation:**
  - the shot is succeeding when actual pressure tracks the pressure target
  - flow becomes the dependent response unless a separate limit is hit

## Connection Assumptions

- Gaggiuino should be reachable on the same LAN as the OpenClaw host
- default base URL is `http://gaggiuino.local`
- `gaggiuino.local` is the machine's mDNS hostname
- if mDNS fails, use the machine's real LAN IP instead
- settings APIs are most useful on newer firmware with REST support

## Wrapper Commands

All machine interaction is via `scripts/gaggiuino.sh`.

| Command | Purpose |
|---|---|
| `status` | real-time machine state |
| `profiles` | list stored profiles |
| `select-profile <id>` | activate a profile |
| `latest-shot` | analyze most recent shot |
| `shot <id>` | analyze historical shot |
| `get-settings [cat]` | inspect settings |
| `update-settings <cat> <json>` | update settings |

## Units

In shot telemetry, the API commonly exposes deci-units; the wrapper converts them to standard units for analysis.

- Pressure → bar
- Temperature → °C
- Weight → g
- Pump flow → ml/s
- Weight flow → g/s

## Time semantics and trigger semantics

Before interpreting whether a phase "ran long enough" or "ended early," explicitly separate these fields:

### 1. `target.time` = target-curve time, not automatically phase runtime
- `target.time` controls how quickly the phase target changes over time.
- In practice, it usually defines the slope / ramp / easing duration of the target curve.
- Do **not** treat `target.time` by itself as evidence that the phase must remain active for that full time.
- A phase may exit before the target curve fully completes if one of its stop conditions fires first.

### 2. `stopConditions.time` = time-based stop condition
Interpret this based on what other stop conditions exist:

- **If `time` is the only stop condition:**
  - treat it as the intended timed hold / timed phase duration
  - in this case, the phase is normally expected to keep running until that time threshold is reached, then hand off to the next phase
- **If `time` appears alongside other stop conditions:**
  - treat it primarily as a fallback ceiling / safety cap unless stronger profile evidence says otherwise
  - do **not** treat failure to approach that time as evidence of failed expression by itself
  - first check whether another stop condition legitimately fired earlier

### 3. Actual runtime = what the machine really did
- Actual runtime must be inferred from the transition points in telemetry.
- Do **not** collapse `target.time`, `stopConditions.time`, and actual runtime into one number.
- In shot analysis, keep these three ideas separate:
  - target-curve duration,
  - stop-condition time ceiling or timed-hold target,
  - actual time spent in the phase.

### 4. Trigger-classification discipline
Before deciding why a phase ended, classify the relevant stop condition as one of:
- **instantaneous state**: e.g. `pressureAbove`, `pressureBelow`, `flowAbove`, `flowBelow`
- **global cumulative**: e.g. `weight` unless explicit evidence says otherwise
- **phase-local cumulative**: e.g. `waterPumpedInPhase`
- **time-based**: `stopConditions.time`

Reason from the machine state at transition time, not from final whole-shot totals.

## Three-part model for shot analysis

To keep shot analysis stable and readable, treat the current skill as three connected parts.

### 1. `processedShot.profile` — profile intent
This is the intended program structure for the shot.
It tells you what the machine was trying to do.

Use it for:
- phase order
- control mode per phase
- target / limit structure
- stop conditions
- global stop conditions
- target-curve timing such as `target.time`

This part answers:
- **what was the profile trying to do?**

### 2. `processedShot.datapoints` — processed shot datapoints
This is the executed telemetry, exposed as readable per-sample datapoints.
It tells you what the machine actually did over time.

Use it for:
- replaying phase handoffs
- checking actual pressure / flow / weight / water progression
- locating likely transition windows
- checking whether a phase appears to have run, shortened, or been skipped

The datapoints are already phase-aware for analysis:
- flow-mode points expose `pumpFlowTarget` + `pressureLimit`
- pressure-mode points expose `pressureTarget` + `pumpFlowLimit`
- each point also carries `phaseIndex` and `controlMode`

This part answers:
- **what actually happened during the shot?**

### 3. `interpreted` — interpreted scaffold
This is the middle orchestration layer.
It helps the skill read the shot correctly and structure the next step.

Use it for:
- compact field-semantics reminders
- phase-level semantic summaries
- analysis ordering and replay scaffolding
- routing toward the right downstream reference material

It may connect to:
- profile mapping
- profile descriptions
- family taxonomy
- troubleshooting
- dial-in guidance

But it should **not** absorb or duplicate those full knowledge sources.
Use it to decide **what to consult next** and **how to structure the result**, not to replace the specialized reference files.

### How the parts connect
Read the shot in this order:
1. `processedShot.profile` → understand intent
2. `processedShot.datapoints` → reconstruct execution
3. `interpreted` → organize semantics, replay, and the next reasoning step
4. downstream references → only when needed for family interpretation or next-move advice

### When adding new fields or behaviors
When a new diagnosis-relevant field or shot behavior is introduced:
1. decide whether it belongs primarily to profile intent, processed execution datapoints, or interpreted scaffold
2. define its meaning clearly where it belongs
3. connect it to replay / diagnosis only after that
4. avoid copying full downstream knowledge into `interpreted`

Do **not** add new reasoning rules that depend on an undefined field meaning.
Do **not** let `interpreted` grow into a second copy of profile-family, troubleshooting, or dial-in references.

### Human-readable output
When replying to the user:
- explain profile intent first when it matters
- describe executed behavior in natural language
- use `interpreted` to structure the explanation, not to dump internal labels
- prefer phrases such as timed hold, fallback ceiling, phase-local pumped water, phase skip, target flow, and pressure limit over raw machine field names unless raw names are specifically needed

## Wrapper output structure

For shot retrieval, the wrapper returns two practical sections:

- **`processedShot`**
  - `processedShot.profile` holds the intended program structure
  - `processedShot.datapoints[]` holds readable per-sample execution data
  - each datapoint is already normalized into phase-aware analysis fields
- **`interpreted`**
  - holds compact semantic reminders, phase summaries, and analysis scaffolding
  - helps route the next reasoning step without replacing downstream reference files

Read `processedShot` as the shot itself and `interpreted` as the compact scaffold for understanding and presenting it.
Keep the parent distinction between `processedShot.profile` and `processedShot.datapoints[]` intact.

## Shot Diagnostics

### Routing note: profile execution first, family second
When real shot data already includes a named profile or embedded phase structure, do **not** start by treating family mapping as the main execution verdict.

For real-shot analysis, the preferred order is:
1. reconstruct what the named profile actually intended,
2. replay what actually executed,
3. only then use family to explain broader intent, expected taste direction, and misread risk.

Family is still valuable here, but mainly as an **interpretation layer**:
- to explain what kind of shot the profile was broadly trying to be,
- to warn against the wrong generic expectations,
- and to support fallback reasoning when profile-specific source material is weak.
- when the named profile and its family mapping are already clear, do **not** present family again as a second conclusion; use it only to explain intent, expectation, or misread risk.

Do **not** let a correct family read overrule a clearer profile-specific execution mismatch.
A shot may fit the broader family yet still fail to express the named profile.
In known-profile real-shot analysis, prefer wording that uses family to explain **intent** rather than to announce a separate family verdict.

### Default evidence model: single-shot first
Unless the current analysis explicitly includes multiple comparable shots, treat the task as a **single-shot diagnosis**.

Do **not** assume stable long-context memory across compaction, reset, or separate sessions.
If repeated-pattern evidence is needed, prefer evidence that is explicitly present in the current analysis context.

In the default case:
- prioritize the immediate trigger over profile fragility,
- treat profile-level susceptibility as secondary,
- and avoid profile-redesign conclusions unless the current evidence explicitly supports them.

### Diagnostic discipline for staged systems
- Treat a salient local event as a clue, not a diagnosis.
- Diagnose stage entry conditions before diagnosing a stage in isolation.
- Prefer root-cause explanations that fit the whole shot trajectory, not just the loudest local moment.
- In single-shot analysis, prefer the smallest sufficient explanation.
- User-proposed causes are hypotheses to test, not evidence to adopt.

### 1. Phase transition replay comes before diagnosis
Before deciding *why* a shot went wrong, reconstruct **what actually executed**.

For each phase, answer in order:
1. what the phase control mode was,
2. what the active target and active limits were,
3. whether `target.time` matters to the target shape in this phase,
4. what stop conditions could end it,
5. whether `stopConditions.time` was the only stop condition or only a fallback ceiling,
6. which stop condition was satisfied first,
7. what the global shot state looked like at handoff to the next phase,
8. whether the next phase actually ran, or was effectively skipped on entry.

Do **not** jump from “the profile intended some intermediate stage here” to “that stage failed because one expected shape did not appear.”
First verify that the phase truly had runtime before any of its own stop conditions were already satisfied.

### 2. Stop-condition semantics: OR + global state
When a phase lists multiple stop conditions, treat them as **OR** conditions unless the machine proves otherwise.
Any one of them may end the phase.

Important default interpretation rules:
- `weight` should be treated as **global cumulative shot values**, not phase-local deltas, unless explicit evidence says otherwise
- `waterPumpedInPhase` should be treated as a **phase-local cumulative** condition
- `pressureAbove` / `pressureBelow` are instantaneous pressure-state checks that can be satisfied immediately on entry
- `flowAbove` / `flowBelow` are instantaneous flow-state checks that can be satisfied immediately on entry
- if `stopConditions.time` is the **only** stop condition, it usually defines a timed hold / timed stage duration rather than a mere fallback ceiling
- if `stopConditions.time` appears **alongside** other stop conditions, it may be bypassed because another stop condition fired first
- a phase can be effectively **instant-exited** if one of its stop conditions is already true at the moment it begins

A phase that appears “not to have worked” may in fact have been **skipped**, not poorly executed.

### 3. Explicit phase-skip detection
Always check for this pattern around each transition:
- phase N ends,
- phase N+1 begins,
- one of phase N+1's stop conditions is already satisfied,
- phase N+1 therefore exits immediately into phase N+2.

If that pattern fits, describe it explicitly as:
- **phase skip**,
- **instant exit**, or
- **entry-satisfied stop condition**.

Do **not** describe it as a normal phase that simply “failed to achieve its intended shape.”
Those are different failure modes and lead to different recommendations.

### 3.5 Upstream-cause traceback after a phase skip
When a phase is skipped or instant-exited because one of its stop conditions is already satisfied on entry, do not stop the analysis at the skipped phase.

Always look upstream and ask:

1. which earlier phase made that entry condition true,
2. whether the triggering variable rose unusually early,
3. whether that early trigger is better explained by shot condition or by profile logic.

A skipped phase is not the root cause by itself.
Treat it first as a downstream symptom that requires upstream traceback.
A skip-triggering stop condition explains the immediate handoff, but does not by itself determine the primary diagnosis.

#### Causal explanation discipline
When explaining *why* a shot failed, do not stop at a shallow pressure event description such as “pressure rose too fast” or “pressure reached the cap early.”

Instead, prefer the deeper causal chain:
- what that pressure event implies about puck resistance or flow control,
- whether cumulative cup weight or water advanced unusually early,
- and how that upstream state caused a downstream phase to shorten, skip, or mis-express.

In other words, pressure events are often **intermediate signals**, not the final diagnosis by themselves.
Whenever possible, explain them in terms of resistance, cumulative yield timing, phase transition logic, and intended family expression.

#### Early cumulative yield and skip-on-entry
If an upstream flow-led phase produces unusually early cumulative cup weight, and a downstream bloom/pause phase is skipped on entry because its weight condition is already satisfied, first suspect reduced puck resistance as the first-pass explanation.

Typical first-pass causes include:
- grind too coarse,
- dose too low,
- weak puck prep / loose puck structure.

Do not jump to profile design first unless the current analysis explicitly includes multiple comparable shots showing the same skip under otherwise reasonable preparation.

### 4. Phase alignment and control-mode interpretation
Correlate raw shot telemetry with phase definitions.

Pay attention to:
- whether a phase ended earlier than its intended role suggests,
- whether weight- or water-based exits happened implausibly fast,
- whether a pressure-triggered transition indicates a resistance mismatch,
- whether a control-mode handoff explains the visible change better than puck diagnosis does,
- whether the intended overall shape was actually expressed.

When a visible stage appears absent, distinguish between:
- **the phase entered and behaved badly**, versus
- **the phase was skipped because entry conditions already satisfied one of its exits**.

### 5. Stage-shape interpretation
When a phase is expected to create a visible change in shot behavior, interpret that shape cautiously.

General rules:
- smooth behavior that matches the active control mode usually suggests a coherent phase execution
- abrupt shape changes near a handoff may come from the phase transition itself rather than from puck failure
- an absent shape does **not** automatically mean the phase logic was wrong; first rule out phase skip via weight / water / pressure / time entry checks

#### Downward Flow Step (Handoff Artifact)
When a flow phase transitions to a significantly lower flow target (e.g., dropping from 6 ml/s to 3 ml/s), expect a temporary flow overshoot and a slow glide path to the new target (often lasting 3-5 seconds). This is caused entirely by the release of stored elastic pressure in the water path as the system depressurizes.
- **Interpretation:** Treat this delayed stabilization as a normal hardware handoff artifact, rather than puck degradation or insufficient resistance.
- **Action:** Do not advise grinding finer to fix this overshoot; higher preceding pressure will only worsen the elastic release.

### 6. Channeling vs normal puck degradation
#### Pressure phases
- sudden spike in weightFlow plus inability to maintain pressure → likely channeling

#### Flow phases
- smooth pressure decline while actual flow still follows the flow target → usually normal puck erosion / natural resistance decay
- sudden pressure-profile collapse or unstable flow tracking → more suspicious of fracture / channeling

### 7. Flow/pressure/weight/time cross-consistency check
Before concluding **too fine / too much resistance / dose too high**, cross-check that claim against the rest of the shot.

At minimum, compare it against:
- total shot time,
- how early cup weight accumulated,
- whether actual flow tracked the flow target,
- whether the shot ran globally fast or slow,
- whether a later high-pressure event could be explained by a skipped phase or control-mode handoff,
- whether the proposed root cause is consistent with both the early and late shot behavior.

If the shot reached cup-weight milestones unusually early, ran short overall, and broadly followed flow targets in the early phase, be very cautious about calling it “too fine” just because pressure later climbed high.
A late pressure rise may be a **phase-transition artifact**, not the root cause.

#### Do not infer “too fine” from an early pressure-cap hit alone
In a **flow phase**, an early hit of the pressure limit does **not** automatically mean the puck was too resistant.
Treat an early pressure-cap exit as only one clue, not a diagnosis.

Before concluding **too fine / too much resistance**, look for a consistent cluster such as:
- actual flow struggling to reach or hold the flow target,
- globally slower or more choked shot pacing,
- delayed or reluctant cup-weight accumulation,
- sustained high-resistance behavior beyond a single capped transition,
- and a later shot structure that still looks resistance-dominated rather than merely transition-shaped.

If those signals are absent, do **not** let one early pressure-cap event overrule the broader shot evidence.

#### Do not infer “too coarse” from one fast-looking segment alone
Likewise, do not diagnose **too coarse / too little resistance** from one open-looking moment by itself.
Prefer a consistent cluster such as:
- unusually early cumulative cup weight,
- setup phases such as soak / bloom being shortened, skipped, or reduced to a brief transition window,
- globally loose or under-supported early structure,
- and a later body phase that looks more like recovery than a fully prepared main extraction.

The diagnosis should come from the whole shot narrative, not from one dramatic local event.
Also avoid the reverse mistake: if a staged setup runs too open, causes unusually early cumulative yield, and shortens or skips a downstream setup-defining phase, do not let a later stable body phase erase that earlier shot-condition evidence.

#### Global coherence outranks local drama
When local pressure drama and whole-shot behavior disagree, prefer the whole-shot consistency check.
A single eye-catching pressure event is weaker evidence than a coherent multi-signal reading across flow, pressure, time, and cumulative yield.

#### Early pressure-cap + healthy flow tracking is an anti-pattern for lazy “too fine” calls
If a flow-led setup phase broadly tracks its flow target, but ends early on the pressure cap, do **not** immediately label the shot “too fine”.
That pattern can also come from a setup structure that became tight too early, a downstream stage that lost room to express, or a shot that is locally constrained but not globally resistance-dominated.
Always inspect what this early cap did to the downstream structure before turning it into a grind recommendation.

#### A phase not reaching max duration is not the same as a failed phase
If a phase ends before its maximum programmed duration, do **not** describe that fact alone as “the phase failed to run” or “did not run”.
A phase may end legitimately because one of its stop conditions fired.
The real diagnostic question is:
- whether the stop-condition-triggered exit still allowed the intended structure to express,
- or whether it shortened / skipped the downstream role that the profile needed.

Use this distinction carefully, especially for setup phases in fill-and-soak, bloom, and staged profiles.

Also distinguish these two cases explicitly:
- **time-only phase**: if `stopConditions.time` is the only stop condition, that time threshold is often the intended timed hold / timed duration and reaching it may be central to correct handoff
- **multi-condition phase**: if `time` coexists with pressure / weight / water-style exits, do not assume the phase was supposed to approach the time threshold before switching

#### Entered phase ≠ expressed phase
For structure-defining phases such as **soak**, **bloom**, **hold**, or other setup stages:
- entering the phase is **not** enough,
- a very short pressure release or transition window is **not automatically** a successful expression of that stage.

If the stage appears only briefly and does not have enough runtime to perform its intended structural role, prefer language such as:
- **compressed**,
- **truncated**,
- **partially expressed**, or
- **nominally entered but not meaningfully expressed**.

Do **not** upgrade it to “normal” or “successfully expressed” merely because the state machine touched that phase.

#### Anti-pattern — early pressure-cap hit ≠ automatic “too fine”
If a flow-led setup phase broadly tracks its flow target but exits early on a pressure cap, do **not** immediately diagnose “too fine”.

First ask:
- did the phase end legitimately by stop condition?
- did that early exit compress a downstream soak / bloom / hold stage?
- does the whole shot still read as globally resistance-dominated, or only locally capped?

If the downstream setup structure was shortened but the later body phase still stabilized coherently, prefer:
- **partially expressed**
over
- **cleanly expressed**, and
- do not reduce the diagnosis to a one-step grind call.

### 8. Failure mechanism vs primary cause
Do **not** confuse the observed failure mechanism with the primary cause of that failure.
When expression fails, classify the failure mechanism in this order:
1. **phase execution problem** — wrong phase ran, skipped phase, instant-exit, malformed handoff
2. **shot condition problem** — grind / dose / puck prep / coffee behavior caused an unintended trigger
3. **profile design problem** — stop thresholds or phase logic are too fragile even when shot prep is reasonable

Do **not** jump to profile redesign if a single shot is more simply explained by grind, dose, or puck behavior triggering an early exit.

#### Single-shot diagnosis: trigger first, susceptibility second
When both a shot-condition trigger and a profile-level susceptibility are present, distinguish them explicitly.

- The **trigger** is what caused this shot to fail now (e.g., grind too coarse).
- The **susceptibility** is what made the profile easier to derail under those conditions (e.g., a weight limit that is too tight).

On a single shot, report the trigger as the primary diagnosis.
Only elevate susceptibility or profile fragility to the main diagnosis when the current analysis explicitly includes multiple comparable shots showing the same phase logic failing under otherwise reasonable preparation.
Do **not** demote a supported shot-condition trigger below profile susceptibility in the final diagnosis.
If early cumulative yield or an overly open setup structure already supports a grind / dose / puck-condition reading, keep that as the **primary diagnosis** on a single shot, and treat tight cumulative thresholds only as **secondary susceptibility**.

### 9. Recommendation routing
Before giving advice, decide which recommendation path the shot belongs to:

#### Single-shot condition problem
Use this when the profile logic is plausible, but this specific shot triggered exits too early or too late.
Typical recommendation order:
1. grind,
2. dose,
3. puck prep / distribution,
4. yield target.

#### Explicit multi-shot evidence of profile fragility
Use this only when the current analysis explicitly includes multiple comparable shots that repeatedly skip or collapse the same phase under otherwise reasonable preparation.
Typical recommendation order:
1. revise the fragile stop condition,
2. add or prefer a time floor / minimum runtime,
3. reduce dependence on ambiguous cumulative triggers when that better matches intent.

#### Mixed case
Use this when both are true:
- the shot condition likely contributed,
- and the profile logic is unusually easy to derail.

In mixed cases, say which fix you would try **first**.
Default to the smallest practical next move, and on a single shot prefer the smallest practical **shot-condition** adjustment before profile redesign.

### 10. Recommended answer structure for shot analysis
When a user asks for analysis of a real shot, prefer this order:
- **Control summary:** what modes/phases actually ran
- **Transition summary:** which exits fired, and whether any phase was skipped
- **Expression status:** expressed / partially expressed / failed
- **Primary issue type:** phase execution / shot condition / **rare profile fragility (only with explicit multi-shot evidence)** / mixed
- **Next move:** 1–2 concrete actions only

This structure should work for most profiles before any family-specific interpretation is added.

### 11. Short calibration examples
Use these as pattern anchors and anti-misread examples, not as rigid templates.

#### Example A — single-shot composite case: skip, handoff, and trigger-first diagnosis
If a single shot shows unusually early cumulative cup weight in an upstream flow-led phase, a downstream phase is skipped on entry because one of its stop conditions is already satisfied, and pressure rises sharply only after a later handoff:
- do **not** describe the skipped downstream phase as a normal phase that simply “failed to develop”
- first identify the skipped phase explicitly as a **phase skip** or **entry-satisfied stop condition**
- do **not** jump straight from the later pressure rise to “too fine”; first ask whether the later rise is better explained by a **handoff artifact** or transition effect
- first report the likely **trigger** as a shot-condition problem such as grind too coarse, dose too low, or weak puck prep when the upstream evidence supports it
- you may note a tight cumulative stop condition or fragile threshold as a **susceptibility**, but keep it secondary on a single shot
- do **not** recommend profile redesign unless the current analysis explicitly includes multiple comparable shots showing the same failure pattern under otherwise reasonable preparation

#### Example B — explicit multi-shot evidence of profile fragility
Use this example only when the current analysis explicitly includes multiple comparable shots.

If several otherwise reasonable shots keep skipping or collapsing the same phase in the same way:
- do **not** treat every shot as a fresh grind-only problem
- elevate suspicion toward **profile fragility**
- then consider whether the stop condition, runtime floor, or trigger logic is too easy to derail

#### Example C — time-only phase vs multi-condition phase
Use this as a semantic calibration check when reading phase definitions.

**Case 1 — time-only phase**
If a phase has:
- `stopConditions: { time: 5000 }`

then that phase is usually intended to remain active until the 5 s threshold is reached.
In this case:
- treat the phase as a timed hold / timed transition / timed stage,
- do **not** downplay the time threshold as a mere fallback,
- and if the phase exits much earlier, explain why that happened rather than assuming the timing was irrelevant.

**Case 2 — multi-condition phase**
If a phase has:
- `stopConditions: { time: 30000, pressureBelow: 0.6, weight: 5 }`

then the `time` condition is usually a fallback ceiling rather than the main expectation.
In this case:
- first check whether `pressureBelow` or `weight` fired earlier,
- do **not** assume the phase was supposed to approach 30 s,
- and if one of the non-time conditions was already satisfied on entry, classify the phase as an instant exit / phase skip rather than as a short but normally expressed phase.

The core rule is:
- **time-only phase** → time is often the intended duration target
- **multi-condition phase** → time is often a fallback unless the profile's structure clearly says otherwise

### 12. Scale noise tolerance
Vibration-pump machines can produce noisy scale traces.

When using `weightFlow` to reason about channeling:
- prefer short moving-trend interpretation over single-point spikes
- mentally smooth over about 1 to 1.5 seconds
- do not overreact to one anomalous 0.5 s blip

### 13. Thermal stability / Brew Delta (Predictive Heating)
Gaggiuino does **not** use a traditional reactive PID for temperature control during an active shot. Instead, it uses a predictive/feedforward algorithm (Brew Delta) that aggressively adds heat based on real-time flow to counteract incoming cold water.

- **Intentional Overshoot:** A rapid rise in the recorded temperature (often spiking significantly above the target) during flow is normal and expected. This reflects the boiler wall heating up predictively, not the actual water temperature hitting the puck.
- **Diagnosis Constraint:** Do **NOT** diagnose intra-shot temperature spikes as a "PID overshoot", "poor PID tuning", or a hardware failure. Never advise the user to "fix" a high temperature peak during the shot.
- **Thermal Sag:** For long, high-yield, or high-flow shots (e.g., Turbo/Soup), check if the temperature shows persistent intra-shot thermal sag *below* the target during the main extraction. Persistent sag indicates true thermal stress and boiler limitation, whereas temporary spikes above the target are simply the feedforward algorithm working correctly.

## Readiness Checks

When asked if the machine is ready, use `status` to check:
- temperature proximity to target,
- stability rather than a single instantaneous reading,
- water level,
- current machine state.

## Troubleshooting Connection Issues

If the machine cannot be reached:
- explain that `gaggiuino.local` is the machine's mDNS hostname and may not resolve on the current network
- ask for the machine's real LAN IP from the router settings
- prefer retrying with the concrete LAN IP rather than guessing

## Local role

This file is the Gaggiuino-specific hard core of Local.

Its job is to determine whether the machine-side behavior and control semantics make sense.
That is necessary, but not always sufficient.

A protocol pass is **not** the same thing as a family-expression pass.
A shot can be coherent in control terms and still fail to express the intent of its profile family.
That higher-level judgment belongs elsewhere when needed.

Public knowledge should live elsewhere; this file should remain focused on:
- real machine behavior,
- shot-data interpretation,
- phase behavior and transition logic,
- control-mode semantics.
