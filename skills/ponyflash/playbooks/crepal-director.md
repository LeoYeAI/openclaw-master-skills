---
name: crepal-director
description: Plans and produces end-to-end videos across general-purpose agent environments. Use when the user wants to create ads, promos, explainers, social videos, brand films, story videos, talking-avatar videos, or any multi-shot video that requires requirement intake, technical method selection, storyboard creation, image generation, clip generation, voice, music, ffmpeg-based editing, and final delivery.
tags: [video, director, ad, promo, explainer, social, brand, film, story, talking-avatar, multi-shot, storyboard, production, 视频, 导演, 广告, 宣传片, 短片, 故事, 数字人, 分镜]
difficulty: intermediate
estimated_credits: 50-300
output_format: Configurable (16:9, 9:16, 1:1, etc.)
---

# CrePal Director Playbook

This playbook provides a complete creative workflow for planning and directing video productions — from concept and storyboard to shot-by-shot creative direction. It focuses on **what to create** (narrative, visual style, composition, pacing) while the base PonyFlash SKILL.md handles **how to create** (API calls, model parameters, and FFmpeg editing workflow).

## Core Operating Rules

1. Start with discovery. Do not generate assets before understanding the goal.
2. Ask from multiple angles: business goal, format, visuals, editing, audio, references, constraints, and delivery.
3. Confirm major checkpoints before expensive generation.
4. Choose the simplest production method that still gives enough creative control.
5. Keep one stable visual identity per recurring character.
6. Keep one stable voice ID per speaking character unless the user approves a change.
7. Visually inspect generated images and clips instead of trusting prompts alone.
8. State assumptions clearly when the user has not answered something.
9. Keep all written communication concise, structured, and in English.

## When To Use

Use this playbook when the user wants to:

- create a complete video from an idea, script, brief, or references;
- make a short ad, promo, explainer, trailer, story video, or social clip;
- turn static images into video clips;
- produce a talking-avatar or digital-human video;
- create a multi-shot video with music, voice-over, and editing.

## Workflow Overview

1. Requirement intake
2. Technical approach selection
3. Pre-production and storyboard
4. Image and keyframe generation
5. Music direction
6. Shot-level video generation (creative direction and prompt design)
7. Voice direction and dialogue planning

## Phase 1: Requirement Intake

### Goal

Collect enough detail to design the right video workflow before generating anything.

### Intake Rules

- Ask grouped questions instead of one long unstructured paragraph.
- If the user already provided part of the brief, do not ask for it again.
- If the user is unsure, offer defaults and mark them as assumptions.
- Prioritize the questions that affect method choice, cost, and consistency.

### Required Discovery Topics

Ask the user about all of the following:

| Topic | What to ask |
|---|---|
| Video goal | What is the video trying to achieve: sales, branding, education, announcement, storytelling, or internal communication? |
| Audience | Who will watch it? What should they feel or do after watching? |
| Duration | Desired total runtime and whether a strict length limit exists |
| Format | Aspect ratio, platform, resolution, and whether horizontal, vertical, or square output is needed |
| Video type | Ad, promo, explainer, testimonial, cinematic montage, tutorial, character story, talking avatar, or other |
| Story content | Main message, narrative arc, must-show products, people, scenes, or claims |
| Visual style | Realistic, cinematic, anime, stylized 3D, motion graphic, documentary, luxury, playful, minimal, dark, bright, or other |
| Editing style | Fast-cut, smooth cinematic, rhythmic, energetic, elegant, documentary, meme-like, or platform-native |
| Character design | Whether the video includes people, recurring characters, products, mascots, or a host |
| Audio plan | Music mood, whether voice-over is needed, whether on-screen dialogue is needed, and whether sound effects matter |
| References | Reference videos, frames, screenshots, moodboards, brand guides, logos, character sheets, or product photos |
| Language | Spoken language, subtitle language, text language, and target market |
| Constraints | Budget sensitivity, realism limits, brand restrictions, legal claims, deadlines, or tool limitations |
| Deliverables | Final render, separate clips, captions, subtitles, thumbnails, key art, or alternate aspect ratios |

### Recommended Intake Question Block

Use this structure and adapt it to the request:

```markdown
To design the right workflow, please confirm:

1. What is the goal of the video, and who is the target audience?
2. How long should it be?
3. What format do you need: 16:9, 9:16, 1:1, or multiple?
4. What type of video is it: ad, explainer, cinematic montage, social clip, talking avatar, or something else?
5. What visual style do you want?
6. What editing style do you want?
7. Do you need people, characters, products, or a digital host on screen?
8. Do you want voice-over, dialogue, subtitles, music, and sound effects?
9. Do you have any reference videos, images, logos, or brand guidelines?
10. Are there any hard constraints or must-include elements?
```

### Intake Output

After the user replies, return a brief in this format before moving on:

```markdown
VIDEO BRIEF SUMMARY

- Goal:
- Audience:
- Duration:
- Format:
- Video type:
- Visual style:
- Editing style:
- Characters or subjects:
- Audio requirements:
- References provided:
- Constraints:
- Deliverables:

Open questions:
- ...

Assumptions:
- ...
```

Do not start production until the brief is clear enough to choose a method.

## Phase 2: Technical Approach Selection

### Goal

Select the most suitable generation method for the whole video and for each shot.

### Available Production Methods

#### 1. First-Frame Video

Use one starting image to generate a clip.

- Best for: simple shots, object motion, camera drift, atmosphere, reveal shots, mood shots
- Strengths: lowest cost, fastest iteration, simple setup
- Limitations: weaker ending control, more drift across shots
- Default use case: non-speaking shots with modest motion

#### 2. First-Last-Frame Video

Use a starting image and an ending image to control both clip endpoints.

- Best for: transformation shots, before-and-after shots, clean transitions, precise opening and ending composition
- Strengths: stronger endpoint control, useful for morphs and reveals
- Limitations: more setup, higher generation cost than first-frame
- Default use case: shots where the ending composition matters as much as the start

#### 3. Multi-Reference Video

Use multiple references such as character, wardrobe, prop, scene, and style images.

- Best for: recurring characters, continuity across shots, branded scenes, consistent environments
- Strengths: highest consistency for identity and scene control
- Limitations: higher setup cost, more reference management, can slow iteration
- Default use case: any project where consistency matters more than speed

#### 4. Digital Human

Use a face or character image plus generated audio to create a speaking video.

- Best for: hosts, presenters, founders, spokespersons, teachers, talking avatars
- Strengths: direct lip sync workflow, efficient for speaking scenes
- Limitations: depends on clean face reference and strong audio quality; less flexible for complex body action
- Default use case: any shot where a visible character must speak clearly to camera

### Method Selection Logic

Choose the method with this priority:

1. If a visible character must speak on camera, prefer `digital_human`.
2. If a shot needs exact start and end control, prefer `first_last_frame`.
3. If consistency across character or scene identity is critical, prefer `multi_reference`.
4. If the shot is simple and cost-sensitive, prefer `first_frame`.

### Method Comparison Table

| Method | Cost | Control | Consistency | Best for |
|---|---|---|---|---|
| `first_frame` | Low | Medium | Medium-Low | Quick non-speaking shots |
| `first_last_frame` | Medium | High on endpoints | Medium | Transformations and reveals |
| `multi_reference` | Medium-High | High | High | Recurring character and scene continuity |
| `digital_human` | Medium-High | High for talking shots | High for host identity | Presenter or avatar scenes |

### Hybrid Planning Rule

Do not force one method on the entire video. Use the best method per shot.

Typical hybrid examples:

- Open with `first_last_frame` for a reveal, use `first_frame` for cinematic inserts, use `multi_reference` for recurring character shots.
- Use `digital_human` only for speaking scenes and another method for b-roll.
- Use `multi_reference` for all hero shots if brand identity must remain stable.

### Technical Proposal Output

After reviewing the brief, return a technical proposal in this format:

```markdown
TECHNICAL PROPOSAL

Recommended overall approach:
- Primary method:
- Secondary methods:
- Why this is the best fit:

Method by shot type:
- Intro or hook:
- Character continuity shots:
- Transition or transformation shots:
- Speaking shots:
- Product or environment inserts:

Tradeoffs:
- Cost:
- Speed:
- Consistency:
- Creative flexibility:

Approval request:
- Confirm this production approach before storyboard and asset generation.
```

Do not generate storyboard assets until the user approves the production approach.

## Phase 3: Pre-Production And Storyboard

### Goal

Turn the approved brief and method selection into a production-ready plan.

### Required Outputs

Create the following before image generation:

- creative brief;
- subject and character registry;
- scene registry;
- asset checklist;
- shot list;
- storyboard;
- approval gate.

### Subject And Character Registry

For each recurring subject, record:

| Field | Description |
|---|---|
| `subject_id` | Stable identifier |
| `type` | Human, product, mascot, environment, prop, logo, text card |
| `role` | Host, hero product, supporting object, background, etc. |
| `appearance` | Face, hair, clothing, color palette, materials, silhouette |
| `consistency_rule` | What must never drift across shots |
| `voice_id` | Only for speaking characters; one character must keep one voice ID |

### Scene Registry

For each environment, record:

| Field | Description |
|---|---|
| `scene_id` | Stable scene identifier |
| `location` | Studio, street, office, fantasy world, room, etc. |
| `time_of_day` | Day, sunset, night, unspecified |
| `lighting` | Soft daylight, hard sunlight, moody rim light, neon, etc. |
| `style_rule` | Visual consistency rules for that scene |

### Storyboard Rules

Build the storyboard shot by shot. Every shot must include:

| Field | Description |
|---|---|
| `shot_no` | Sequential number |
| `duration` | Planned clip length |
| `goal` | What the shot must communicate |
| `method` | `first_frame`, `first_last_frame`, `multi_reference`, or `digital_human` |
| `subjects` | Character, product, environment, or props used |
| `visual` | What appears on screen |
| `motion` | Object, camera, and atmosphere motion |
| `camera` | Angle, lens feel, framing, movement |
| `dialogue` | Spoken line if any |
| `voice_id` | Required for speaking shots |
| `music_note` | Energy or mood guidance |
| `sfx_note` | Sound effects guidance |
| `references_needed` | Which images, logos, or clips are required |
| `approval_status` | Pending or approved |

### Storyboard Output Template

```markdown
STORYBOARD

Shot 1
- Duration:
- Goal:
- Method:
- Subjects:
- Visual:
- Motion:
- Camera:
- Dialogue:
- Music note:
- SFX note:
- References needed:

Shot 2
- ...
```

### Approval Gate

After writing the storyboard, ask the user to confirm:

- shot flow;
- tone and pacing;
- character design direction;
- speaking lines;
- any must-change shots before generation begins.

Do not move to Phase 4 until the storyboard is approved.

## Phase 4: Image And Keyframe Generation

### Goal

Generate all images needed to support clip generation and keep visual identity stable.

### Generation Order

1. Generate or collect hero references first.
2. Generate scene references second.
3. Generate shot keyframes third.
4. Review each image before moving to video generation.

### Required Image Types

Generate whichever of these are needed:

| Image type | Purpose |
|---|---|
| Character reference | Locks face, wardrobe, expression, and silhouette |
| Product reference | Locks product shape, materials, and brand details |
| Scene reference | Locks environment, palette, and lighting |
| Prop reference | Locks recurring objects |
| Start keyframe | For `first_frame` or `first_last_frame` shots |
| End keyframe | For `first_last_frame` shots |
| Style board | Optional style anchor for look and mood |
| Thumbnail frame | Optional approval frame before full clip generation |

### Visual Review Checklist

Inspect every image against this checklist:

- anatomy and proportions are correct;
- identity matches the intended character or product;
- clothing, props, and brand details are accurate;
- background and lighting fit the approved style;
- no extra limbs, artifacts, warped text, or broken objects;
- the image is strong enough to be used as a keyframe;
- recurring subjects still look like the same subject.

### Image Confirmation Loop

Return images to the user in manageable batches, usually by shot or by subject set.

Use this format:

```markdown
IMAGE REVIEW

Assets ready for approval:
- Character reference:
- Scene reference:
- Shot 1 keyframe(s):
- Shot 2 keyframe(s):

Please confirm:
- keep as is;
- revise specific assets;
- replace style direction.
```

If the user requests revisions, update only the affected assets and keep approved ones unchanged.

## Phase 5: Music Generation

### Goal

Create background music that fits the approved narrative and editing rhythm.

### Music Planning Rules

- Generate music only after the storyboard and core image direction are approved.
- Match the music to audience, pace, emotional arc, and platform.
- If the user wants heavy dialogue clarity, avoid music that competes with speech.
- If the user wants multiple edits, prefer loopable or stem-friendly music.

### Music Brief Fields

| Field | Description |
|---|---|
| `mood` | Inspirational, intense, playful, elegant, emotional, suspenseful, etc. |
| `tempo` | Slow, medium, fast, or BPM target |
| `genre` | Cinematic, electronic, ambient, orchestral, pop, lo-fi, corporate, etc. |
| `structure` | Intro, build, peak, outro |
| `edit_notes` | Beat drop, transitions, pauses for dialogue |
| `duration` | Match or slightly exceed final runtime |

### Music Approval Output

```markdown
MUSIC REVIEW

- Direction:
- Tempo:
- Genre:
- Structure:
- Intended use on timeline:

Please confirm whether this music direction works before final shot generation and edit assembly.
```

## Phase 6: Shot-Level Video Generation

### Goal

Generate each video clip with the most suitable method and the right prompt structure.

### General Rules

- Produce clips shot by shot.
- Keep all clip filenames and versions stable.
- Use approved images only.
- Use the selected method per shot, not a one-method shortcut.
- If a shot fails, revise that shot instead of restarting the whole project.

### Prompt Structure For Non-Speaking Shots

For each non-speaking shot, build prompts with these parts:

| Prompt section | What to include |
|---|---|
| Subject | Who or what is in frame |
| Environment | Background, weather, lighting, and atmosphere |
| Composition | Framing and camera position |
| Motion | Subject motion and camera motion |
| Style | Approved visual style and realism level |
| Continuity anchors | Character, product, wardrobe, scene, and color constraints |
| Restrictions | What must not change or appear |

### Prompt Structure For Speaking Shots

For a speaking shot, include:

- character identity;
- framing suitable for lip sync;
- facial expression and tone;
- speaking energy;
- exact dialogue or attached audio;
- subtitle requirement if needed;
- strict continuity with approved character image.

### Shot Production Record

Maintain a record like this:

```markdown
SHOT PRODUCTION RECORD

Shot:
- Method:
- Duration:
- Source references:
- Prompt summary:
- Audio dependency:
- Status:
- Revision notes:
```

### Shot Review Loop

After generating clips, return them for review in batches.

Use this format:

```markdown
SHOT REVIEW

Completed shots:
- Shot 1:
- Shot 2:
- Shot 3:

Please confirm for each shot:
- approve;
- revise motion;
- revise framing;
- revise style;
- revise continuity.
```

Do not finalize the timeline until all critical shots are approved.

## Phase 7: Voice Generation And Dialogue

### Goal

Generate voice-over or character dialogue that matches the approved creative direction.

### Voice Rules

1. Voice generation is optional unless the project requires narration or speaking characters.
2. Each recurring character must keep one voice ID through the whole project.
3. The narrator should also keep one stable voice ID.
4. Only change a voice ID if the user explicitly approves it.
5. If the project uses a digital human, generate or confirm the dialogue audio before or during shot generation for those speaking clips.

### Voice Planning Fields

| Field | Description |
|---|---|
| `character_name` | Speaker name |
| `voice_id` | Stable voice identifier |
| `voice_type` | Narrator, host, character, announcer |
| `tone` | Warm, authoritative, friendly, energetic, calm, luxury, etc. |
| `pace` | Slow, medium, fast |
| `accent_or_locale` | Optional locale requirement |
| `script` | Exact spoken text |

### Voice Output Template

```markdown
VOICE REVIEW

Speakers:
- Narrator:
- Character A:
- Character B:

Voice assignments:
- Narrator -> voice_id:
- Character A -> voice_id:
- Character B -> voice_id:

Scripts ready:
- ...

Please confirm voice choice and script before final FFmpeg assembly and export.
```

## Fallbacks And Recovery Rules

### If references are missing

- Ask the user for them first.
- If unavailable, propose a reference-free path and warn that consistency may drop.
- Mark every inferred design choice as an assumption.

### If image consistency breaks

- Regenerate the affected asset using the approved hero reference set.
- Reduce style variation and strengthen continuity constraints.
- Do not regenerate unrelated approved assets.

### If the clip drifts from the storyboard

- Tighten the prompt around composition, motion, and restrictions.
- If endpoint control matters, switch from `first_frame` to `first_last_frame`.
- If identity control matters, switch to `multi_reference`.

### If a speaking shot looks wrong

- Verify the face reference first.
- Verify the audio quality and pacing second.
- Shorten the dialogue if needed.
- If the body motion is too complex, simplify the framing to head-and-shoulders or bust shot.

### If the user requests late changes

- Isolate the impact first: script, images, clips, audio, or timeline.
- Rework the smallest affected layer.
- Tell the user which approved assets remain reusable.

## Minimal Execution Policy

Use this order unless the project has a strong reason not to:

1. Brief
2. Technical proposal
3. Storyboard
4. Hero references
5. Shot keyframes
6. Music direction
7. Shot generation
8. Voice generation

Exception: for digital-human shots, dialogue audio may need to be created before the corresponding clip. Once all creative assets are approved, hand off to the base SKILL.md for FFmpeg assembly, subtitle handling, and final export.

## Reusable Agent Templates

### Template A: Discovery

```markdown
To plan the video correctly, please confirm:

1. Goal and audience
2. Desired runtime
3. Output format and platform
4. Video type
5. Visual style
6. Editing style
7. Subjects or characters on screen
8. Music, voice-over, dialogue, and subtitles
9. Reference videos, images, or brand materials
10. Hard constraints and deliverables
```

### Template B: Technical Proposal

```markdown
Based on your brief, I recommend this production setup:

- Primary method:
- Additional methods:
- Why:
- Best method for speaking shots:
- Best method for continuity-heavy shots:
- Best method for transformation shots:
- Cost and speed tradeoff:

Please confirm this approach before I build the storyboard.
```

### Template C: Storyboard Delivery

```markdown
I have prepared the storyboard.

Please review:
- shot order;
- pacing;
- visual direction;
- dialogue;
- any scenes that need changes.

Once approved, I will generate the key images for each shot.
```

### Template D: Asset Review

```markdown
The first image batch is ready for review.

Please tell me for each asset whether to:
- approve;
- revise;
- replace.
```

### Template E: Music Review

```markdown
The music direction is ready.

Please confirm:
- mood;
- tempo;
- genre;
- whether it leaves enough room for dialogue.
```

### Template F: Clip Review

```markdown
The first video clips are ready.

Please review each shot for:
- motion;
- framing;
- continuity;
- style;
- overall fit with the storyboard.
```

## Success Criteria

This playbook is successful when the agent:

- asks the right requirement questions first;
- selects the correct creative method per shot;
- creates a coherent storyboard before generation;
- gets user approval at major checkpoints;
- keeps visual and voice consistency across the project;
- delivers a complete set of approved creative assets ready for final assembly.
