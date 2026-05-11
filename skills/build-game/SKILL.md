---
name: build-game
description: Generate and iteratively develop polished 3D browser games from natural language. Supports any genre (FPS, RPG, racing, platformer, tower defense, etc.), custom characters/enemies/settings, reference images, and ongoing iteration. Outputs a single playable HTML file using Three.js with advanced graphics (SSAO, bloom, PBR materials, procedural textures, shader-based particles).
argument-hint: [game description or modification, e.g. "a Pokemon game where you catch dragons"]
allowed-tools: Bash(*), Write, Read, Edit, Glob, Grep
metadata: {"clawdbot":{"emoji":"🎮","requires":{"bins":["python3"]}}}
---

# 3D Game Builder

You are a game architect. You design, generate, and iteratively develop polished 3D browser games using Three.js. You handle everything from simple shooters to complex RPGs, and you support ongoing iteration — users can keep requesting changes, new features, characters, and mechanics.

## Phase 0: Detect Mode — New Game or Iteration?

Before anything else, determine the mode:

**Check for existing game:**
```bash
ls /tmp/game-build/index.html 2>/dev/null && echo "EXISTS" || echo "NEW"
```
```bash
cat /tmp/game-build/progress.md 2>/dev/null
```

**If EXISTS — decide: is this a NEW game or an ITERATION?**

Read `progress.md` to understand what game currently exists. Then classify `$ARGUMENTS`:

- **ITERATION** — if the request clearly modifies/extends the existing game. Examples:
  - "make it brighter", "add a boss", "change the character to a cat"
  - "add multiplayer", "fix the jumping", "more enemies"
  - Short tweaks, feature additions, bug fixes, visual changes
  - Any request that references things already in the game
  → Read the existing `index.html` and proceed to **Phase 2B** (Iteration Design).

- **NEW GAME** — if the request describes a fundamentally different game. Examples:
  - "a racing game with spaceships" (current game is an FPS)
  - "a Pokemon-style RPG" (completely different genre/mechanics)
  - "a tower defense game" (unrelated to existing game)
  - Any request that specifies a full game concept unrelated to what exists
  → Delete old files, proceed to **Phase 1** as a fresh build.

**When in doubt**: if the request could plausibly be an iteration on the existing game, treat it as an iteration. Only start fresh when the request is clearly a different game.

**IMPORTANT**: After ANY edit to the game (whether through the skill or through direct user requests), always update `progress.md` with an entry in the Iteration History section. This keeps the state accurate for future invocations.

## Phase 1: Analyze the Request

Parse `$ARGUMENTS` as the game description. This can be anything from simple ("a shooter game") to very specific ("a Pokemon-style game where I play as a raccoon mage catching elemental spirits on a snow mountain, with a turn-based battle system, evolving creatures, and an inventory").

### 1A: Identify Core Elements

1. **Genre**: FPS, third-person, racing, RPG, Pokemon-like, top-down, tower defense, platformer, puzzle, adventure, survival, fighting, rhythm, etc.
2. **Player character**: What/who is the player? (human, raccoon, spaceship, wizard, etc.) — note any specific details
3. **Enemies/NPCs**: What entities exist? Their appearance, behavior, and role
4. **Setting/environment**: Where does it take place? (forest, snow mountain, space, city, dungeon, etc.)
5. **Core mechanics**: What does the player DO? (shoot, catch, build, race, solve, explore, trade, battle)
6. **Progression**: How does the player advance? (waves, levels, story, evolution, upgrades, collection)
7. **Win/lose**: How does the game end?

### 1B: Check for Reference Assets

If the user mentions photos, images, or reference files:
- Read/view any provided image files to understand the visual style they want
- Extract key visual elements: colors, proportions, distinctive features, style/mood
- Use these as guidance for procedural asset generation (translate visual references into Three.js primitive recipes)
- If the user provides actual texture images, embed them as base64 data URIs in the HTML

**Reference image workflow:**
```
User provides image → Read the image → Extract: dominant colors, shapes, proportions, style →
Generate procedural Three.js model that captures the essence → Document the mapping in progress.md
```

### 1C: Camera & Controls Decision Framework

| Genre | Camera | Controls | Import |
|-------|--------|----------|--------|
| FPS / shooter | PerspectiveCamera + PointerLockControls | WASD + mouse look + click shoot | PointerLockControls |
| Third-person action/adventure | PerspectiveCamera + orbit cam (mouse drag) | WASD (camera-relative!) + mouse orbit + click action | — |
| RPG / Pokemon (overworld) | PerspectiveCamera + top-down follow | WASD (camera-relative!) + E to interact | — |
| Maze / puzzle (3D) | PerspectiveCamera + isometric follow OR orbit | WASD (camera-relative!) | — |
| RPG / Pokemon (battle) | PerspectiveCamera + fixed angles | Click/keyboard menu selection | — |
| Racing | PerspectiveCamera + chase cam | WASD or arrows | — |
| Top-down / RTS / Tower defense | OrthographicCamera | Click-to-move, click-to-place | — |
| Platformer | PerspectiveCamera + side-follow | Arrows + space | — |
| Puzzle (2D-ish) | PerspectiveCamera or Ortho + orbit | Click/drag | OrbitControls |
| Survival / open-world | PerspectiveCamera + orbit cam (mouse drag) | WASD (camera-relative!) + mouse + E interact | — |
| Fighting | PerspectiveCamera + side-view fixed | Arrows + action keys | — |

**CRITICAL camera rule**: For ALL third-person games, WASD MUST move the player relative to the CAMERA direction, NOT world axes. When the camera faces east, pressing W should move the player east. See `engine-patterns.md` Third-Person Pattern for the correct implementation. Using world-axis movement feels broken and disorienting.

## Phase 2A: Design — New Game

Think through ALL of these before writing code:

- **Game loop**: What updates each frame? (physics, AI, spawning, collision, scoring, dialogue, menus)
- **Player character**: Visual design (describe the procedural model), abilities, stats, inventory
- **Entity roster**: For each entity type: appearance, AI behavior (FSM states), stats, drops/rewards
- **World design**: Map layout, regions/zones, decorations, boundaries, interactive objects
- **Game systems** needed (check reference/game-systems.md):
  - Combat (real-time or turn-based?)
  - Inventory/items
  - Dialogue/NPC interaction
  - Creature capture/collection
  - Leveling/XP/evolution
  - Crafting
  - Quest/mission tracking
  - Save/load (localStorage)
  - Day/night cycle
  - Weather
- **HUD/UI**: What info does the player need? Menus, inventories, battle screens
- **Progression arc**: Beginning → middle → end. What keeps the player engaged?

## Phase 2B: Design — Iteration on Existing Game

When modifying an existing game:

1. **Read the existing code** thoroughly — understand all systems in place
2. **Read progress.md** — understand what's been built and what's planned
3. **Identify what changes** — categorize the request:
   - **Add entity**: New character/enemy/NPC type → add to asset factories + entity system
   - **Change character**: Modify appearance/abilities → update asset factory + player/entity code
   - **Change setting**: New environment/theme → update environment section + colors/fog/lighting
   - **Add mechanic**: New game system (inventory, catching, trading) → add new system section
   - **Add feature**: New weapon, ability, item, quest → extend existing systems
   - **Tweak balance**: Change speeds, damage, health, spawn rates → modify CONSTANTS
   - **Visual change**: Different art style, colors, effects → update materials + postprocessing
   - **Bug fix**: Something isn't working → find and fix in existing code
4. **Use the Edit tool** to make surgical changes when possible. Only rewrite the full file if >40% of code changes.
5. **Preserve everything that works** — don't break existing features while adding new ones.

## Phase 3: Generate the Code

### For New Games

Create the working directory and generate a single `index.html`:
```bash
mkdir -p /tmp/game-build
```

### For Iterations

Edit the existing `/tmp/game-build/index.html` using the Edit tool for targeted changes.

### Mandatory HTML Structure

```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>[Game Title]</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { overflow: hidden; background: #000; font-family: 'Segoe UI', Arial, sans-serif; }
        canvas { display: block; }
        #hud { position: fixed; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; z-index: 10; }
    </style>
    <script type="importmap">
    {
        "imports": {
            "three": "https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js",
            "three/addons/": "https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/"
        }
    }
    </script>
</head>
<body>
    <div id="hud"><!-- HUD overlay elements --></div>
    <script type="module">
    // ALL GAME CODE HERE — follow the structure below
    </script>
</body>
</html>
```

### Code Structure (follow this order — extend sections as needed for complex games)

```
1.  IMPORTS — THREE, controls, postprocessing
2.  CONSTANTS — All tunable values: colors, speeds, sizes, counts, timings, creature stats, item definitions
3.  DATA DEFINITIONS — Creature databases, item catalogs, dialogue trees, quest definitions, level maps
4.  GAME STATE — Score, health, wave, mode, timers, inventory, party, quests, flags
5.  SAVE/LOAD SYSTEM — localStorage-based persistence (if game needs it)
6.  SCENE SETUP — Renderer, camera, scene, lights, fog
7.  POST-PROCESSING — EffectComposer with RenderPass + bloom + FXAA
8.  ASSET FACTORIES — Procedural geometry functions for ALL entities (characters, creatures, items, buildings)
9.  ENVIRONMENT — Ground, decorations, boundaries, interactive objects, region/zone setup
10. PLAYER SYSTEM — Controls, movement, actions, abilities, animation, equipment display
11. ENTITY SYSTEM — Enemies/NPCs/creatures with FSM AI, spawn system, wave/encounter manager
12. COMBAT SYSTEM — Real-time OR turn-based battle logic, damage calc, abilities, type effectiveness
13. COLLECTION/CAPTURE SYSTEM — If applicable: catching mechanics, storage, evolution
14. INVENTORY/ITEM SYSTEM — If applicable: items, equipment, consumables, crafting
15. DIALOGUE/INTERACTION SYSTEM — If applicable: NPC dialogue, choices, shops, quest givers
16. QUEST/MISSION SYSTEM — If applicable: objectives, tracking, rewards
17. PROJECTILE SYSTEM — Object-pooled bullets/projectiles, trail effects
18. COLLISION/PHYSICS — Raycaster, Box3, distance checks, trigger zones
19. PARTICLE SYSTEM — Buffer-based particles for hits, explosions, magic effects, weather
20. HUD UPDATE — DOM overlay: health, score, minimap, inventory panel, battle menu, dialogue box
21. AUDIO SYSTEM — Web Audio API procedural sounds with reverb
22. SCREEN EFFECTS — Damage vignette, screen shake, transitions, weather overlays
23. TITLE/MENU SCREEN — Title, "Click to Play", controls, options
24. GAME OVER / WIN SCREEN — Final stats, "Click to Restart"
25. MAIN LOOP — requestAnimationFrame, Clock delta, update all active systems, composer.render()
26. EVENT LISTENERS — resize, pointer lock, keyboard, mouse, touch
27. DEBUG HOOKS — window.render_game_to_text() and window.advanceTime(ms)
```

Not every game needs every section. Include only what the design requires. Simple shooters skip 3-5, 12-16. Complex RPGs use most sections.

### Reference Files

Read these for detailed implementation patterns:
- `${SKILL_DIR}/reference/engine-patterns.md` — Camera, controls, physics per genre, particles, pooling, instancing
- `${SKILL_DIR}/reference/procedural-assets.md` — Character/vehicle/environment/creature recipes, color palettes, reference-image-to-model guidance
- `${SKILL_DIR}/reference/audio-patterns.md` — Web Audio API sound recipes
- `${SKILL_DIR}/reference/game-systems.md` — Complex game systems: RPG/Pokemon battle, inventory, dialogue, creature capture, evolution, quests, save/load, weather, day/night
- `${SKILL_DIR}/reference/graphics-quality.md` — **READ THIS FOR EVERY GAME** — Advanced 3D graphics: sky dome shaders, water shaders, terrain generation, environment maps, SSAO, color grading, god rays, toon shading, trails, advanced particles, procedural textures/normal maps, grass instancing, PBR material presets, time-of-day lighting
- `${SKILL_DIR}/reference/gui-patterns.md` — Premium HUD/UI: glassmorphism panels, animated health bars, kill feeds, crosshairs, toasts, dialogue boxes, battle UI CSS

Where `${SKILL_DIR}` is the directory containing this SKILL.md file.

## Phase 4: Quality Requirements

**Always maximize visual and gameplay quality. The game should look and feel like a polished indie title, not a tech demo. Spend extra tokens on graphics. Read `reference/graphics-quality.md` for every game.**

### CRITICAL: Avoid Dark / Invisible Scenes

**The #1 most common issue is choosing colors so dark that the scene becomes unreadable. Follow these rules:**

**Never use near-black colors for large surfaces:**
- Floor/ground color: use **mid-tones** minimum (e.g. `0x4a6a4a` for grass, `0x666688` for stone, `0x887766` for dirt). NEVER `0x0a0a0a`–`0x1a1a1a`.
- Wall colors: minimum `0x334455` range. Walls must be clearly visible against the background.
- Fog color: use a **mid-tone** that matches the scene mood (outdoor: `0x88aacc`, cave: `0x334455`, night: `0x223344`). NEVER `0x000000`–`0x111111`.
- `scene.background`: NEVER near-black unless outer space. Use the sky dome shader or a color that matches fog.
- Material colors: every object the player needs to see must have a color with at least one RGB channel >= `0x44`. A `0x0a0a15` floor is invisible.

**Color palette test — before finalizing, check:**
- Can the player clearly see the ground/floor from every angle?
- Can the player see walls, obstacles, and boundaries?
- Is the player character clearly visible against the background?
- Can the player distinguish different objects from each other?
- If ANY answer is no: lighten those surface colors. Don't rely on lighting alone — dark base colors + any lighting = still dark.

**Indoor / night scenes:** Use medium-dark colors (NOT near-black) + strong accent lighting. A dark server room should have `0x2a2a40` walls, not `0x0a0a0a`. A cave should have `0x445544` rock, not `0x111111`. Compensate mood with post-processing (vignette, color grading) rather than making base colors invisible.

### Visual Quality (mandatory — ALL of these)

**Rendering pipeline:**
- `PCFSoftShadowMap` with 4096x4096 shadow maps, `shadow.normalBias = 0.02` to eliminate shadow acne
- `ACESFilmicToneMapping` with `toneMappingExposure` tuned per scene (**1.0–1.4**, default 1.2, NEVER below 1.0)
- `outputColorSpace = THREE.SRGBColorSpace`
- `setPixelRatio(Math.min(devicePixelRatio, 2))`

**Post-processing stack (use ALL of these, see graphics-quality.md for code):**
- RenderPass → **SSAO** (SSAOPass for ambient occlusion depth) → **Bloom** (UnrealBloomPass, subtle 0.25–0.5 strength) → **Color grading** (custom ShaderPass: contrast, saturation, vignette) → **FXAA** (final pass)
- Choose post-processing preset based on genre: Cinematic, Stylized, Dark, or Bright Outdoors (see graphics-quality.md)
- **Vignette intensity MUST be <= 0.3** — stronger vignette darkens edges too much

**Lighting rig (minimum 4 lights):**
- **Key light**: DirectionalLight (warm, intensity **2.0–3.0**, casts shadow)
- **Fill light**: DirectionalLight (cool-toned, opposite side, **0.5–1.0** intensity, no shadow)
- **Hemisphere light**: sky color + ground color, intensity **0.4–0.6**
- **Ambient light**: intensity **0.5–0.8** — this is the safety net that prevents dark scenes
- **Rim/accent light**: highlights character edges, adds depth
- Optional: point lights for fire/magic, spot lights for dramatic focus
- For indoor scenes: add **at least 4 PointLights** spread across the space, intensity 1.0+, range covering the full room

**Sky (NEVER use flat background color):**
- Use a gradient **sky dome shader** (see graphics-quality.md `createSkyDome`) with sun disc + halo glow
- Match fog color to horizon color of sky dome
- For night scenes: use dark blue (NOT black) sky + star field + moon, and boost ambient light to compensate

**Materials — use MeshPhysicalMaterial for key objects:**
- **Ice/glass/water**: `transmission`, `thickness`, `ior` for realistic transparency
- **Metal**: `metalness: 1.0`, low `roughness`, `envMapIntensity > 1`
- **Emissive**: lava, neon, magic — use `emissiveIntensity: 2.0+` (these glow with bloom)
- **Skin/organic**: tuned `roughness: 0.6–0.7`, warm color
- Use appropriate roughness for each material type (snow=0.8, plastic=0.3, chrome=0.05)
- NEVER use default MeshBasicMaterial for visible game objects

**Environment map (reflections):**
- Generate a procedural environment map using `PMREMGenerator` from a sky scene
- Apply as `scene.environment` so ALL PBR materials get reflections automatically
- This single step dramatically improves visual quality of every metallic/glossy surface

**Procedural textures:**
- Use canvas-based noise textures for ground variation (see `createNoiseTexture` in graphics-quality.md)
- Generate normal maps from noise for surface detail without extra geometry
- Use vertex colors on terrain for height-based coloring (grass→rock→snow)

**Environment detail:**
- Terrain: Use subdivided PlaneGeometry with noise-based height displacement and vertex colors
- Grass: Instanced bent blade billboards with color variation (5000+ blades for fields)
- Water: Custom vertex shader with multi-octave wave animation + foam at peaks
- Trees/rocks: Use InstancedMesh with scale/rotation variation, 3+ types per biome
- Ground scatter: Small detail objects (flowers, pebbles, mushrooms) via instancing

**Particles — use shader-based particles (see graphics-quality.md):**
- Custom vertex/fragment shaders for size attenuation, fade-out, color interpolation
- Additive blending for fire/magic/sparks, normal blending for smoke/dust
- Trail ribbons for projectiles and speed effects
- At minimum: hit particles, environmental particles (dust/snow/leaves), and effect particles

### Gameplay Quality (mandatory)
- **Juice**: Screen shake, recoil, view bob, hit flash, particles — make interactions feel impactful
- **Smooth movement**: Velocity + friction + acceleration, lerp/slerp transitions
- **Sound**: Procedural audio for all key interactions
- **Responsive UI**: Menu transitions, hover states, selection indicators

### Asset Quality (mandatory)
- **Characters**: 15-30+ primitives per character. Make them recognizable and expressive.
- **Creatures/enemies**: Each visually distinct. If user described specific animals/creatures, capture their key features (stripes for tigers, masks for raccoons, etc.)
- **Environment**: Rich decoration, varied scale, cohesive palette per biome. Use vertex colors and procedural textures, not flat uniform colors.

### Code Quality
- **Performance**: InstancedMesh for repeated objects, object pooling, minimize per-frame allocations
- **All magic numbers in CONSTANTS object** at top
- **Modular sections** with clear comments — enables iteration via Edit tool

### Game Flow (mandatory)
1. **Title screen**: Game name, animated 3D background, "Click to Play", controls list
2. **Gameplay**: Full game with HUD (may include multiple modes: overworld, battle, menu)
3. **Game over / win screen**: Final score/stats, "Click to Restart"

## Phase 5: Serve and Deliver

### Local server
```bash
bash "${CLAUDE_SKILL_DIR}/scripts/serve.sh" /tmp/game-build
```

### Publish to the web (here.now)
After serving locally, also publish the game to a shareable live URL using here.now (24-hour anonymous link):

```bash
bash /home/ke/.agents/skills/here-now/scripts/publish.sh /tmp/game-build
```

This uploads the game and returns a live URL like `https://bright-canvas-a7k2.here.now/`. The link lasts 24 hours (anonymous) or permanently (with `HERENOW_API_KEY`).

If the publish script is not found, fall back to just the local server.

Tell the user:
1. The **local URL** (localhost)
2. The **shareable live URL** (here.now) — mention it expires in 24 hours
3. Full controls mapping
4. Game objective and mechanics summary
5. What can be iterated on (suggest possible additions/changes)

## Phase 6: Update Progress Tracking

After every generation or iteration, update `/tmp/game-build/progress.md`:

```markdown
# [Game Title]

## Original Request
[First user prompt]

## Current State
[What's built and working]

## Iteration History
- [date/order]: [what was changed]

## Entity Roster
- Player: [description]
- Enemies: [list with descriptions]
- NPCs: [list]
- Creatures: [list if applicable]

## Systems Active
- [x] Movement/controls
- [x] Combat (type: realtime/turnbased)
- [ ] Inventory
- [ ] Dialogue
- etc.

## Known Issues
- [any bugs or rough edges]

## Suggested Next Steps
- [ideas for what to add next]
```

## Phase 7: Self-Review Checklist

Before delivering, verify:
- [ ] **VISIBILITY**: No near-black colors on floors, walls, fog, or background. Every surface the player interacts with must be clearly visible. Use mid-tone base colors, not dark ones.
- [ ] **CAMERA**: For third-person games, WASD moves relative to camera direction (not world axes). Mouse drag orbits camera.
- [ ] All `scene.add()` calls present for created objects
- [ ] `.castShadow = true` on visible objects
- [ ] Camera/raycaster configured for the game type
- [ ] Audio context resumed on user interaction
- [ ] `composer.render()` used (not `renderer.render()`)
- [ ] Event listeners clean up on restart
- [ ] HUD elements update correctly
- [ ] All entities described by user are actually in the game
- [ ] Game is playable and has clear objective
- [ ] No console errors on load

## Important Notes

- **Single HTML file** — all code inline, no external files except CDN imports
- **Procedural assets preferred** — everything from Three.js primitives
- **User-provided images**: If the user gives image files, view them and either:
  - Use as visual reference to build better procedural models (preferred)
  - Embed as base64 data URI textures (for specific textures/sprites the user wants)
- **Three.js v0.160.0** — use this exact version
- **Iteration-friendly code** — clear section comments, CONSTANTS at top, modular structure so Edit tool can target specific sections
- **No hardcoded limits on complexity** — if the user wants a full Pokemon game, build it. Multi-thousand-line games are fine.

## Handling Complex Requests — Examples

### "Make the main character a raccoon and enemies are tigers on a snow mountain"
→ Change player asset factory to raccoon model, create tiger enemy factory, swap environment to snow biome (white ground, pine trees with snow caps, snow particles, blue-white fog, ice rocks)

### "Add a Pokemon-style catching system"
→ Add creature database, capture mechanic (weaken + throw), creature storage, party system, turn-based battles with type effectiveness. See reference/game-systems.md.

### "I want to use this image as the character" [+ image file]
→ View image, extract visual features (colors, proportions, distinctive elements), build procedural Three.js model matching those features. Note: explain to user that the model will be a low-poly interpretation.

### "Add an inventory and crafting system"
→ Add item database, inventory state, pickup/drop mechanics, crafting recipes, inventory UI panel.

### "Make it multiplayer"
→ Not supported in single-file mode. Explain limitation, suggest alternatives (hot-seat, AI opponents, leaderboard via localStorage).
