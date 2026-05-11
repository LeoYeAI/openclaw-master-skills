---
name: gaggiuino-local
description: Gaggiuino analytical skill for machine control, shot expression analysis, and high-performance visualization. It interprets shot data through profile intent and generates unified static/animated graphs or synchronized video overlays.
metadata: { "openclaw": { "requires": { "bins": ["curl", "python3", "mktemp", "ffmpeg"] } } }
---

# Gaggiuino Local

Gaggiuino Local is a machine-connected skill for espresso machines running the Gaggiuino mod. 
It enables live status monitoring, in-depth shot analysis based on profile intent vs. actual expression, profile management, and settings configuration. Additionally, it provides a high-performance rendering engine for generating static graphs, animated trajectory videos, and synchronized overlays for extraction footage.

Its core question is not simply **“is this cup good?”**
It first asks whether the shot became what its profile was trying to make it become.
In other words, it asks:

> **Did this shot become the kind of coffee it was trying to be?**

In Chinese:

> **这杯咖啡有没成为它本来想成为的样子？**

Only after that should it move into troubleshooting or dial-in guidance.

All machine interaction goes through `scripts/gaggiuino.sh`.

---


## What this skill is for

Use this skill when the task involves one or more of these:
- checking current machine state, readiness, temperature, water level, or active profile / 当前状态
- analyzing the latest shot / 萃取 or a historical one (**preferred; strongest evidence**)
- generating static graphs, animated trajectory videos, or synchronized overlays / 萃取可视化与视频叠加
- dialing in or troubleshooting espresso taste and shot behavior
- recommending a profile / 曲线 or profile family
- listing or switching profiles / 曲线 on the real machine
- helping identify what family a named profile / 曲线 belongs to
- reading or updating Gaggiuino settings
- interpreting graph screenshots or machine screen photos (**fallback; lower-confidence evidence**)


## What this skill is not for

- It is **not** a generic coffee essay generator.
- It is **not** a profile-name cookbook detached from real machine behavior.
- It should not answer live-status questions from memory or guesswork when the API path is available.
- It should not assume every coffee question needs machine control if the user is only asking for general dial-in reasoning.

## Direct machine asks

### Immediate command routing
- machine status / readiness / temperature / online / current profile / 当前状态 / 准备好了没 / 当前温度 / 在线吗 / 当前曲线 / 现在是什么曲线  
  → `scripts/gaggiuino.sh status`
- available profiles / what profiles are installed / 有哪些曲线 / 可用曲线 / 装了哪些曲线  
  → `scripts/gaggiuino.sh profiles`
- switch to a named profile / use profile XXX / 切到 XXX 曲线 / 换成 XXX 曲线 / 用 XXX 曲线  
  → `scripts/gaggiuino.sh profiles` → resolve id → `scripts/gaggiuino.sh select-profile <id>`
- latest shot / latest extraction / last shot / latest extraction / 最新一杯 / 最新萃取 / 上一杯 / 最近一杯  
  → `scripts/gaggiuino.sh latest-shot`
- historical shot by id / extraction by id / 按 id 查历史萃取 / 查某一杯历史记录  
  → `scripts/gaggiuino.sh shot <id>`
- settings read/change / 读设置 / 改设置 / 查看设置 / 修改设置  
  → `scripts/gaggiuino.sh get-settings <category>` first, then `scripts/gaggiuino.sh update-settings <category> <json>`
- shot graph (static/dynamic) / overlay video / 渲染萃取图 / 合成视频  
  → `scripts/render_shot_graph.py` & `scripts/render_shot_video_overlay.py`

### Connection default and fallback
- default base URL is `http://gaggiuino.local`
- `gaggiuino.local` is the machine's **mDNS hostname**
- on first use, if no remembered fixed LAN IP exists, the script tries `gaggiuino.local` first
- the remembered fixed LAN IP is stored at `~/.openclaw/workspace/memory/gaggiuino-base-url.json`
- if `gaggiuino.local` fails, guide the user to check the machine's network connection and find its real LAN IP in **router settings**
- for long-term stability, suggest setting a **DHCP static lease on the router**
- when the user confirms a stable LAN IP they want to keep using, save it with `scripts/gaggiuino.sh set-base-url <url-or-host>`
- once a remembered fixed LAN IP exists, the script tries that address first and falls back to `gaggiuino.local` on connection-layer failure
- if both the remembered address and `gaggiuino.local` fail, treat the remembered IP as possibly stale and guide the user to re-check the network or update the saved address
- use `scripts/gaggiuino.sh get-base-url` to inspect the remembered address and `scripts/gaggiuino.sh clear-base-url` to remove it
- these addresses are intended for trusted local/LAN endpoints; do **not** point them at untrusted remote servers
- prefer retrying with a concrete LAN IP over guessing

---

## Terminology normalization

Use these as output-normalization rules, especially when replying in Chinese coffee context.
They are meant to prevent literal but unnatural translations.

### General rule
- Match the user's language.
- In Chinese coffee context, prefer established coffee terms over literal translation.
- Treat these as normalization hints for analysis and replies, unless the user clearly means something else.

### Core term mappings
- **profile** → **曲线**
- **shot** → **萃取**
- **phase** → **阶段**
- **Bloom** → **焖蒸**
- **phase transition** → **阶段切换** / **阶段过渡**
- **yield** → **出液**
- **channeling** → **通道效应**
- **puck** → **粉饼**
  - Do **not** use the literal sports translation **冰球**.
- **control mode** → **控制模式**
- **family** → **方案**
- **flow phase** → **流速先决阶段**
- **pressure phase** → **压力先决阶段**

### Local alias / machine-specific interpretation
- In this local context, **超萃** usually refers to the local `HyperEx` / `HyperEx 2.0` profiles.
- When users say **超萃** here, default to checking whether they mean the local HyperEx lineage first.

### Phase Replay Nomenclature (Target vs Limit)
Use the terminology rules above, but for phase-transition replays and control-mode summaries apply the following stricter formatting rules.

When writing phase transition replays or summarizing control modes, **strictly avoid** exposing raw machine fields or machine-style shorthand such as `type: "FLOW"`, `target.end: 3`, `restriction: 4`, `stopConditions.pressureAbove: 4`, or compressed tuples built from them. Translate them into human-readable descriptions centered on **Targets**, **Limits**, and exit conditions.

**Critically: Match the output language strictly to the user's query language. Do not mix English and Chinese.**

**For `type: flow`:**
- The mode is the **flow phase** (EN) / **流速先决阶段** (CN).
- The **flow target** is the target (EN) / **目标流速** (CN).
- The **pressure limit** is the limit (EN) / **压力限制** (CN).
- *Format Example (EN):* "Flow phase, flow target 12 ml/s, pressure limit 6 bar."
- *Format Example (CN):* "流速先决阶段，目标流速 12 ml/s，压力限制 6 bar。"

**For `type: pressure`:**
- The mode is the **pressure phase** (EN) / **压力先决阶段** (CN).
- The **pressure target** is the target (EN) / **目标压力** (CN).
- The **flow limit** is the limit (EN) / **流速限制** (CN).
- *Format Example (EN):* "Pressure phase, pressure target 6 bar, flow limit 2 ml/s."
- *Format Example (CN):* "压力先决阶段，目标压力 6 bar，流速限制 2 ml/s。"

---

## Core operating rule

Always decide first whether the task is mainly about:
1. **real machine state / real shot data**
2. **general dial-in reasoning**
3. **graph interpretation**
4. **local profile classification**

Then read only the references needed for that path.

For real machine tasks, default to:
1. fetch the actual state / shot / settings payload
2. reconstruct what the named profile actually tried to do
3. interpret the machine-side semantics correctly
4. use family as an interpretation layer, not the first execution verdict
5. only then recommend the next move

---

## Primary routing logic

### Analysis Principle: Family vs. Profile
Use family as an interpretation layer, not as the first execution verdict.
In real-shot analysis, judge the intended **named profile** first, then use family to explain broader intent, likely expectations, and common misreads.

A shot may fit the broader family yet still fail to express the named profile.
A shot may also express the named profile coherently and still be worth changing for taste reasons.

For full machine semantics, read:
- [references/analysis-protocol.md](references/analysis-protocol.md)

For family intent, graph interpretation, and broader next-move reasoning, read:
- [references/profile-families.md](references/profile-families.md)
- [references/shot-graph-analysis.md](references/shot-graph-analysis.md)
- [references/troubleshooting.md](references/troubleshooting.md)

---

### 1. Current machine state / readiness / live status
If the user asks whether the machine is ready, online, hot enough, or what profile is active:
- run `scripts/gaggiuino.sh status` immediately
- use [references/analysis-protocol.md](references/analysis-protocol.md) only if interpretation is needed
- if the connection fails, apply the mDNS → LAN IP fallback rule above

### 2. Latest shot / historical shot analysis
If the user wants analysis of the latest shot or a specific shot:
- run `scripts/gaggiuino.sh latest-shot` or `scripts/gaggiuino.sh shot <id>`
- if a specific named profile is known and more than the raw phase list is needed, read [references/profile-descriptions.md](references/profile-descriptions.md)
- then follow the mandatory shot-analysis order below

#### Mandatory shot-analysis order

For latest-shot or historical-shot analysis, do **not** jump straight to troubleshooting.
Always complete the following order before giving recommendations:

1. **Identify the named profile and intended structure**
   - read the embedded profile metadata first
   - if the named profile is known and the analysis needs more than the raw phase list, read [references/profile-descriptions.md](references/profile-descriptions.md)
   - identify the strongest available source for intended execution: `profile.phases` first, then profile description when needed

2. **Reconstruct what actually executed**
   - read [references/analysis-protocol.md](references/analysis-protocol.md)
   - replay the control modes, targets, limits, exits, skips, and handoffs
   - keep intended structure and actual behavior separate

3. **Add family interpretation only after the execution replay**
   - resolve the intended family from [references/profile-mapping.md](references/profile-mapping.md) when mapped
   - use [references/profile-families.md](references/profile-families.md) only when broader family interpretation is still needed
   - use family to explain intent and misread risk, not as the first execution verdict
   - in real-shot analysis with a known named profile, do **not** present family as a second conclusion; use it only to clarify intent, likely expectations, or common misreads

4. **Judge expression at the right level**
   - state whether the named profile appears:
     - **expressed**
     - **partially expressed**
     - **failed to express**
   - if useful, also state whether the broader family still fits
   - do **not** give grind / ratio / pressure advice before making this judgment

5. **Classify the main problem type and next move**
   - prefer phase execution and shot-condition diagnosis before profile fragility
   - distinguish the immediate **trigger** from any profile-level **susceptibility**
   - then give the smallest sensible next move

#### Recommended answer structure for shot analysis

When replying to latest-shot or historical-shot requests, prefer this structure:

- **Profile:** `<profile name>`
- **Execution summary:** `what phases / handoffs actually ran`
- **Profile expression:** `expressed / partially expressed / failed`
- **Family intention:** `only when it adds value; explain the family-level intent or expected misread without turning it into a second conclusion`
- **Primary issue type:** `phase execution / shot condition / mixed / rare profile fragility`
- **Next move:** `1–2 concrete actions only`

#### Hard guardrail

Do **not** collapse real shot analysis into a generic coffee answer.
Do **not** let family resemblance outrank a clearer profile-specific execution mismatch.
Treat `profile.name` as the starting point, not the conclusion. If `profile.phases` clearly indicate a different known variant within the same broader family, use phase structure to refine the resolved variant.
Keep intended structure and actual behavior separate: `processedShot.profile.phases` define the intended program structure; `processedShot.datapoints` show what the machine actually did over the shot. Do **not** use execution datapoints to replace a clearer structural signal already present in the profile phase definitions.
A shot-analysis answer is incomplete unless it explicitly states whether the named profile **expressed / partially expressed / failed to express** before giving troubleshooting or dial-in advice.
For staged named profiles, do not equate “all expected phases were entered” with “the profile was fully expressed”; judge whether key setup stages actually had enough runtime to perform their intended role.

### 3. Shot Visualization / 萃取可视化

The skill includes a unified rendering engine for transforming shot data into visual assets. All modes share a deterministic **2400x1080** pixel layout to ensure consistency between static and animated output. Both rendering scripts support absolute or relative paths, including user-home expansion (`~`) and automatic creation of missing parent directories.

#### Standard Output Location
All visual assets generated by the skill are captured in a defined standard directory with automatic naming:
- Static: `shot<id>_static.png`
- Animated: `shot<id>_animated.mp4`
- Overlay: `shot<id>_overlay_landscape.mp4` or `shot<id>_overlay_portrait.mp4`
`~/.openclaw/workspace/gaggiuino-output`

The `--out` parameter is optional; if omitted, the scripts will automatically archive the file using this standard location and naming convention.

#### Rendering Modes
- **Static Graph (PNG)**: A single high-resolution image (2400x1080) for quick review.
- **Dynamic Animation (MP4/GIF)**: A 10fps animation showing the progression of the shot with a moving time cursor. Supports multi-process rendering for high-speed output.
- **Video Overlay (MP4)**: Synchronizes graph animation with a user-supplied extraction video.
    - **Landscape video**: Stacks the graph animation on top of the original video.
    - **Portrait video**: Overlays the graph animation semi-transparently at the top or bottom of the video.
    - **Sync Offset**: Supports a manual time offset to align video audio/visuals perfectly with graph data.

#### Visualization CLI Reference

##### Graph Renderer
`scripts/render_shot_graph.py`
```bash
# Generate static PNG (shot<id>_static.png)
python3 render_shot_graph.py --shot-id <id> --mode png

# Generate animated MP4 (shot<id>_animated.mp4)
python3 render_shot_graph.py --shot-id <id> --mode mp4
```

##### Video Overlay Renderer
`scripts/render_shot_video_overlay.py`
**Synchronization Offset**
- `--offset <seconds>`: Align the graph with the video. 
  - **Positive (e.g., 1.4)**: Video started **before** the shot. Graph animation will wait 1.4s before starting.
  - **Negative (e.g., -1.2)**: Shot started **before** the video recording.

**Landscape (Horizontal)**
Automatically uses a **Vertical Stack (VSTACK)** layout. The graph is placed above the video.
```bash
# Video starts 1.4s before graph (shot<id>_overlay.mp4)
python3 render_shot_video_overlay.py --shot-id <id> --video landscape.mp4 --offset 1.4
```

**Portrait (Vertical / Smartphone)**
Automatically uses a **Semi-transparent Overlay**. The graph floats over the video.
- `--alpha <0.1-1.0>`: Adjust opacity (1.0 = solid, 0.7 is recommended).
- `--position <top/bottom>`: Place the graph at the top or bottom of the frame.

```bash
# Portrait overlay with custom alpha (0.7) at the bottom
python3 render_shot_video_overlay.py --shot-id <id> --video portrait.mp4 --alpha 0.7 --position bottom
```

---

### 4. Taste-based dial-in and troubleshooting with no telemetry
If the user only describes taste, extraction behavior, or dialing problems:
- start with [references/dial-in-basics.md](references/dial-in-basics.md)
- then read [references/troubleshooting.md](references/troubleshooting.md)
- use [references/extraction-levers.md](references/extraction-levers.md) when you need to distinguish **extraction vs strength vs evenness**, or decide why a lever such as ratio, flow, pressure, temperature, or water is the right next move

#### Conceptual profile-fragility questions with no telemetry
If the user asks a conceptual causality question such as “does this mean the profile itself is flawed?” but does **not** provide telemetry or explicit multi-shot evidence:
- do **not** jump straight to profile design as the main diagnosis
- apply the same **single-shot-first** logic from [references/analysis-protocol.md](references/analysis-protocol.md)
- treat profile fragility as a secondary suspicion unless the current analysis explicitly includes multiple comparable shots showing the same failure pattern under otherwise reasonable preparation
- if needed, use [references/extraction-levers.md](references/extraction-levers.md) to explain why the next move should still target shot condition, evenness, or family choice before redesigning the profile

### 5. Graph / screenshot / curve reading
If the user provides a graph screenshot, machine screen image, or curve description:
- treat it as **graph-only interpretation**
- start with [references/shot-graph-analysis.md](references/shot-graph-analysis.md)

#### Mandatory graph-analysis order

1. **Assess evidence quality**
   - note what is visible, missing, and how confident the read can be

2. **Do a provisional family read**
   - identify the most likely family from the visible graph shape
   - keep it provisional unless the intended profile is already known

3. **Upgrade immediately if the user supplies profile context**
   - if the user gives a named profile, profile description, or phase details, re-check the graph against that known structure
   - do **not** equate “fits the family” with “the named profile was successfully expressed”

4. **State the result at the right level**
   - if only family-level evidence exists, report a family-level judgment
   - if named-profile structure is known, report both **family fit** and **named-profile fit**

5. **Keep the next move minimal**
   - prefer asking for intended profile or cup result over aggressive dial-in advice from a weak image alone

#### Recommended answer structure for graph analysis

- **Likely family:** `<family> (<confidence>)`
- **Evidence quality:** `strong / partial / weak`
- **What the graph most likely shows:** `the 2–4 most important observations`
- **What remains uncertain:** `missing intent / weak image / missing profile context`
- **Next move:** `ask for intended profile or give 1 tentative adjustment`

#### Hard guardrails

- Do **not** treat a visual family inference as settled fact when the intended profile is unknown.
- Do **not** treat “fits the family” as equivalent to “the named profile expressed successfully.”
- If the user later provides stronger profile context, revise the earlier graph read instead of merely relabeling it.

### 6. Profile selection and family reasoning
If the user asks what profile / 曲线 to use, what a named profile / 曲线 is like, or asks to switch profiles / 曲线:
- first distinguish between conceptual profile advice and real machine switching
- for conceptual advice, use [references/profile-families.md](references/profile-families.md) and read [references/profile-descriptions.md](references/profile-descriptions.md) only when the named profile needs more than a family-level explanation
- if the question depends on this machine's named profiles, also read [references/profile-mapping.md](references/profile-mapping.md)

#### Mandatory profile-selection order

First distinguish between:
- **conceptual profile advice**
- **real machine profile switching**

Do **not** treat a profile question as permission to change the machine.

For conceptual profile advice:
- explain the likely family, use case, and tradeoffs
- use [references/profile-families.md](references/profile-families.md) for family reasoning
- use [references/profile-mapping.md](references/profile-mapping.md) when the answer depends on this machine's named profiles

For real machine switching, always follow this order:

1. **Confirm explicit switching intent**
   - only switch when the user clearly wants the real machine changed
   - if the user is still comparing options, stay in advice mode

2. **Resolve the requested profile against the machine list**
   - run `scripts/gaggiuino.sh profiles` first
   - resolve the requested name to a concrete profile id from the returned list
   - if multiple candidates match, ask before switching

3. **Send the switch request precisely**
   - use `scripts/gaggiuino.sh select-profile <id>` only after the target id is clear
   - do **not** guess a profile id from memory or from a partial name alone

4. **Report switch status precisely**
   - treat `select-profile <id>` as a **sent request**, not a confirmed switch, unless a follow-up read confirms it
   - if confirmation matters, read machine state or profiles again after sending the request

#### Hard guardrail

For real profile switching, the minimum valid sequence is:

**confirm explicit switch intent → list profiles → resolve concrete id → send switch request → report status precisely**

### 7. Settings changes
If the user wants machine settings changed:
- always `get-settings <category>` first
- then make the minimal requested change
- then `update-settings <category> <json>`
- use [references/analysis-protocol.md](references/analysis-protocol.md) for settings-safety rules

#### Mandatory settings-change order

For settings changes, first distinguish between a **read** request and a **write** request.
Do **not** treat a settings question as permission to modify the machine.

For real settings writes, always follow this order:

1. **Read the current category first**
   - run `scripts/gaggiuino.sh get-settings <category>` before planning the write
   - do **not** invent or guess the current payload

2. **Modify only the explicit delta**
   - preserve every untouched field from the fetched payload
   - change only what the user clearly asked to change
   - do **not** rewrite the whole category speculatively

3. **Require clarity before writing**
   - if the target category, field, or intended value is ambiguous, ask before posting
   - if the user is only exploring options, explain first and wait for explicit change intent

4. **Write back a complete valid payload**
   - use `scripts/gaggiuino.sh update-settings <category> <json>` with a complete payload based on the fetched response
   - do **not** send a partial delta-only payload when the endpoint expects the full category object

5. **Report status precisely**
   - do **not** claim a speculative or unperformed change was applied
   - if the write was sent, say it was sent
   - if confirmation matters, read the category again and compare the returned values

#### Hard guardrail

For settings writes, the minimum valid sequence is:

**read current category → modify explicit delta only → write complete payload → report status precisely**

---

## Machine-specific hard rules

When interpreting real Gaggiuino data:
- in **flow phases**, the **flow target** is the target and the **pressure limit** is the limit
- in **pressure phases**, the **pressure target** is the target and the **flow limit** is the limit
- do **not** misread healthy pressure decline in a flow-led phase as automatic channeling
- real telemetry is stronger evidence than screenshots
- in real-shot analysis, judge execution against the intended **named profile** first
- then use the intended **family** to explain broader intent and avoid universal 9-bar assumptions

---

## Language and tone

- Reply in the same language as the user.
- Prefer practical, specific guidance over coffee-theory monologues.
- Use theory to explain decisions, not to overwhelm the answer.
- When machine data is available, keep interpretations tied to actual numbers and actual shot behavior.

---

## Host dependencies

The visualization and rendering features require these system-level tools to be installed on the host:

### Public install strategy
- **Debian/Ubuntu:**
  ```bash
  sudo apt install python3-matplotlib ffmpeg
  ```
- **macOS (Homebrew):**
  ```bash
  brew install ffmpeg python-matplotlib
  ```

### Notes
- On this host, `PYTHONNOUSERSITE=1` is automatically used by the renderers to avoid numpy 2.x ABI conflicts from user-site packages in `~/.local`.

---

## Reference map

### Common references
- [references/dial-in-basics.md](references/dial-in-basics.md)
- [references/extraction-levers.md](references/extraction-levers.md)
- [references/troubleshooting.md](references/troubleshooting.md)
- [references/profile-families.md](references/profile-families.md)

### Gaggiuino-specific references
- [references/analysis-protocol.md](references/analysis-protocol.md)
- [references/profile-mapping.md](references/profile-mapping.md)
- [references/profile-descriptions.md](references/profile-descriptions.md)
- [references/shot-graph-analysis.md](references/shot-graph-analysis.md)

---

This is an unofficial, non-commercial interoperability skill for machines running the Gaggiuino mod. It does not include or redistribute Gaggiuino source code. Any Gaggiuino-related materials remain subject to their original terms, including the project’s CC BY-NC 4.0 license where applicable.

Some reference material in this skill was adapted from https://espressoaf.com/guides and https://github.com/Zer0-bit/gaggiuino/tree/community/profiles.
The Gaggiuino-specific analysis protocol in this skill is an original local framework built on top of those sources and real machine behavior.

Acknowledgement: Gaggiuino — the greatest coffee project on the planet.
