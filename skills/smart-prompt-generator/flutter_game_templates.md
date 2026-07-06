# Flutter Game Development Templates

This file contains detailed prompt templates specifically for Flutter game development using Flame, Forge2D, and other game engines.

## Game Types Covered

- 2D Platformers
- Puzzle Games
- Endless Runners
- RPGs
- Strategy Games
- Casual Games
- Educational Games
- Multiplayer Games

## Template Library

### 1. Complete Game Setup

```
Create a complete [GAME_TYPE] game in Flutter using Flame with:

GAME SPECIFICATIONS:
- Type: [2D platformer/puzzle/RPG/endless runner/etc.]
- Perspective: [side-scrolling/top-down/isometric]
- Target Platform: [mobile/web/desktop]
- Orientation: [portrait/landscape]
- Resolution: [target resolution and scaling approach]

CORE MECHANICS:
- Primary Gameplay: [main game loop activities]
- Player Actions: [movement/attack/interact/etc.]
- Progression System: [levels/achievements/unlocks]
- Win/Lose Conditions: [victory and failure states]

TECHNICAL REQUIREMENTS:
- Game Engine: [Flame/Forge2D/custom]
- State Management: [Riverpod/Provider/Bloc]
- Save System: [Hive/SharedPreferences/Cloud]
- Audio: [background music and SFX]
- Ads/IAP: [monetization approach]

DELIVERABLES:
1. Complete project structure
2. Game loop implementation
3. Scene management system
4. Player controller
5. Level/World system
6. UI/HUD implementation
7. Save/Load system
8. Audio manager
9. Performance optimizations
10. Testing strategy
```

### 2. Player Character System

```
Design and implement a player character system for [GAME_TYPE]:

CHARACTER SPECIFICATIONS:
- Type: [humanoid/vehicle/creature/abstract]
- Movement: [walk/run/jump/fly/swim/etc.]
- Abilities: [double jump/dash/attack/etc.]
- Attributes: [health/speed/power/etc.]
- Visual Style: [pixel art/cartoon/realistic/etc.]

COMPONENTS NEEDED:
1. Movement Component
   - Input handling
   - Physics (velocity, acceleration)
   - Collision detection
   - Animation states

2. Animation Component
   - Sprite animations
   - State-based animation switching
   - Transition effects
   - Frame timing

3. Ability Component
   - Ability definitions
   - Cooldown system
   - Input mapping
   - Visual/audio feedback

4. Stats Component
   - Health/mana/etc.
   - Stat modifiers
   - Level progression
   - Save/load integration

IMPLEMENTATION DETAILS:
- State Machine: [finite state machine pattern]
- Input System: [keyboard/touch/gamepad]
- Physics: [custom/Forge2D/Flame's built-in]
- Rendering: [sprite batches/optimized rendering]

Provide complete code with:
- Base character class
- Component classes
- Input handling
- Example usage
- Testing approach
```

### 3. Enemy/NPC AI System

```
Create an AI system for enemies and NPCs in [GAME_TYPE]:

AI REQUIREMENTS:
- Entity Types: [enemies/NPCs/bosses]
- Behaviors: [patrol/chase/attack/flee/etc.]
- Intelligence Level: [simple/intermediate/complex]
- Interaction: [combat/dialogue/trading/etc.]

AI ARCHITECTURE:
1. Behavior Tree System
   - Node types (selector, sequence, action)
   - Custom nodes for game-specific behaviors
   - Visual debugging tools

2. State Machine
   - States: [idle/patrol/chase/attack/etc.]
   - Transitions: [triggers and conditions]
   - State-specific logic

3. Pathfinding
   - Algorithm: [A*/Dijkstra/navmesh]
   - Obstacle avoidance
   - Dynamic path updates

4. Decision Making
   - Target selection
   - Ability usage
   - Retreat/advance logic

IMPLEMENTATION:
- Base AI controller class
- Behavior tree implementation
- Pathfinding system
- Example AI configurations
- Performance optimizations
- Testing framework
```

### 4. Level Design System

```
Design a level/world system for [GAME_TYPE]:

LEVEL STRUCTURE:
- Organization: [linear/hub-based/open-world]
- Progression: [sequential/unlock-based]
- Size: [small/medium/large levels]
- Complexity: [simple/complex]

LEVEL COMPONENTS:
1. Tile System
   - Tile types and properties
   - Collision mapping
   - Visual layers
   - Interactive elements

2. Object Placement
   - Enemies/NPCs
   - Collectibles
   - Obstacles
   - Triggers/events

3. Level Data
   - Serialization format (JSON/custom)
   - Level loading/unloading
   - Memory management

4. Level Editor Integration
   - External tools (Tiled/custom)
   - Import/export
   - Testing workflow

FEATURES:
- Checkpoint system
- Level transitions
- Secret areas
- Dynamic elements
- Environmental hazards

DELIVERABLES:
1. Level data structure
2. Level loader/renderer
3. Tile system
4. Object spawner
5. Level streaming (for large worlds)
6. Save integration
7. Example levels
8. Editor workflow documentation
```

### 5. Game Physics System

```
Implement a physics system for [GAME_TYPE] in Flutter:

PHYSICS REQUIREMENTS:
- Type: [2D platformer/top-down/etc.]
- Realism Level: [arcade/semi-realistic/realistic]
- Performance: [lightweight/heavy simulation]

CORE PHYSICS:
1. Collision Detection
   - Shapes: [AABB/circle/polygon]
   - Layers/masks
   - Collision response
   - Trigger volumes

2. Movement Physics
   - Gravity
   - Friction
   - Velocity/acceleration
   - Air resistance

3. Advanced Features (if needed)
   - Rigid body dynamics
   - Joints/constraints
   - Particle physics
   - Fluid dynamics

IMPLEMENTATION OPTIONS:
- Custom lightweight physics
- Flame's built-in collision
- Forge2D integration
- Box2D integration

Provide:
1. Physics world setup
2. Collision system
3. Movement/force application
4. Performance optimizations
5. Debug visualization
6. Example usage
```

### 6. UI/UX System

```
Create a comprehensive UI/UX system for [GAME_TYPE]:

UI SCREENS NEEDED:
1. Main Menu
   - Start game
   - Settings
   - Achievements
   - Credits
   - Exit

2. In-Game HUD
   - Health/mana bars
   - Score/coins
   - Mini-map (if applicable)
   - Controls hints
   - Pause button

3. Pause Menu
   - Resume
   - Settings
   - Save/Load
   - Quit to menu

4. Game Over Screen
   - Stats summary
   - High score
   - Retry/Quit options

5. Settings Menu
   - Audio controls
   - Graphics settings
   - Controls customization
   - Accessibility options

UI FRAMEWORK:
- State Management: [how UI state is managed]
- Animations: [transitions and effects]
- Responsive Design: [different screen sizes]
- Theme System: [consistent styling]

ACCESSIBILITY:
- Screen reader support
- Color blind modes
- Adjustable text sizes
- Control customization

Provide:
1. Base UI component system
2. Screen management
3. Animation system
4. Complete implementations of all screens
5. Theme/styling system
6. Example usage
```

### 7. Save/Load System

```
Design a robust save/load system for [GAME_TYPE]:

SAVE REQUIREMENTS:
- What to Save: [player progress, stats, unlocks, settings]
- When to Save: [checkpoints/manual/auto-save]
- Where to Save: [local/cloud/both]
- Save Slots: [single/multiple]

DATA TO PERSIST:
1. Player Data
   - Current level/scene
   - Stats and attributes
   - Inventory/items
   - Abilities unlocked

2. Game State
   - Current objectives
   - Completed levels
   - Achievements
   - High scores

3. Settings
   - Audio preferences
   - Graphics settings
   - Control mappings
   - Accessibility options

4. World State
   - Enemy spawn states
   - Collected items
   - Triggered events
   - Environmental changes

IMPLEMENTATION:
- Storage: [Hive/SharedPreferences/SQLite/Cloud]
- Serialization: [JSON/binary/custom]
- Version Control: [save format migration]
- Validation: [data integrity checks]

FEATURES:
- Auto-save
- Quick save/load
- Cloud sync
- Save file management UI

Provide:
1. Save data models
2. Save/load manager
3. Serialization logic
4. Cloud integration (if applicable)
5. Error handling
6. Example usage
```

### 8. Audio System

```
Create an audio management system for [GAME_TYPE]:

AUDIO REQUIREMENTS:
- Music: [background music tracks]
- Sound Effects: [UI, gameplay, ambient]
- Voice Over: [if applicable]
- Quality: [compression, formats]

AUDIO COMPONENTS:
1. Background Music
   - Track management
   - Crossfading
   - Dynamic music (intensity changes)
   - Volume control

2. Sound Effects
   - One-shot sounds
   - Looping sounds
   - 3D spatial audio (if needed)
   - Priority system

3. Audio Pooling
   - Pre-loading
   - Memory management
   - Performance optimization

4. Audio Controls
   - Master volume
   - Music volume
   - SFX volume
   - Mute toggle

IMPLEMENTATION:
- Audio Engine: [Flame's audioplayers/Just Audio/custom]
- Format Support: [MP3/OGG/WAV]
- Platform Considerations: [iOS/Android/Web differences]

Provide:
1. Audio manager class
2. Music controller
3. SFX player
4. Audio pooling system
5. Settings integration
6. Example usage
7. Performance optimizations
```

### 9. Particle System

```
Implement a particle system for visual effects in [GAME_TYPE]:

EFFECTS NEEDED:
- Explosions
- Fire/smoke
- Magic spells
- Weather effects
- Impact effects
- Ambient particles

PARTICLE FEATURES:
1. Emission
   - Shapes: [point/line/circle/area]
   - Rate control
   - Burst vs continuous

2. Particle Properties
   - Lifetime
   - Velocity
   - Color/opacity over time
   - Size over time
   - Rotation

3. Physics
   - Gravity influence
   - Wind effects
   - Collision (optional)

4. Rendering
   - Blending modes
   - Texture atlas support
   - Performance optimization

IMPLEMENTATION:
- Use Flame's particle system or custom
- Object pooling for performance
- Configuration via data files

Provide:
1. Particle emitter class
2. Particle configuration system
3. Pre-built effect library
4. Editor/preview tool (if feasible)
5. Performance optimizations
6. Example effects
```

### 10. Monetization System

```
Integrate monetization into [GAME_TYPE]:

MONETIZATION MODEL:
- Type: [Free with Ads/Freemium/Premium/Hybrid]
- Ad Types: [Banner/Interstitial/Rewarded]
- IAP: [consumables/non-consumables/subscriptions]

COMPONENTS:
1. Ad Integration
   - AdMob/Unity Ads/other
   - Ad placement strategy
   - Rewarded ad logic
   - Banner management

2. In-App Purchases
   - Product catalog
   - Purchase flow
   - Receipt validation
   - Restore purchases

3. Premium Features
   - Unlock mechanics
   - Feature gating
   - Upgrade paths

4. Analytics
   - Revenue tracking
   - Conversion metrics
   - A/B testing

IMPLEMENTATION:
- Platform-specific code (iOS/Android)
- Fallback for non-monetized builds
- Testing environment
- Compliance (GDPR, COPPA)

Provide:
1. Monetization manager
2. Ad integration
3. IAP system
4. Analytics integration
5. UI for store/shop
6. Testing approach
```

## Quick Reference Templates

### Simple Character Movement
```
Implement basic 2D character movement for a platformer:
- Left/right movement with acceleration
- Jump with gravity
- Collision with platforms
- Simple animation states (idle, walk, jump)
Using Flame engine in Flutter.
```

### Basic Enemy AI
```
Create simple enemy AI for a platformer:
- Patrol between two points
- Chase player when in range
- Return to patrol when player leaves range
- Simple collision with player
Using Flame engine in Flutter.
```

### Score System
```
Implement a scoring system for [GAME_TYPE]:
- Point values for different actions
- High score tracking
- Score multipliers
- Score display in HUD
- Save high scores locally
```

### Power-Up System
```
Create a power-up system for [GAME_TYPE]:
- Power-up types: [speed boost/shield/etc.]
- Duration-based effects
- Visual feedback
- Collection mechanics
- UI indication
```

## Usage Tips

1. **Customize Templates**: Replace placeholders with your specific requirements
2. **Combine Templates**: Mix and match components for complex features
3. **Iterate**: Start simple, then add complexity
4. **Test Early**: Prototype core mechanics before full implementation
5. **Optimize Later**: Focus on functionality first, optimize when needed

## Common Patterns

### Component-Based Design
```
Break game entities into reusable components:
- Position component
- Velocity component
- Collision component
- Render component
- Input component
```

### State Machine Pattern
```
Use state machines for:
- Character states (idle, walk, jump, attack)
- Game states (menu, playing, paused, game over)
- UI states (hidden, visible, animating)
```

### Observer Pattern
```
Use for event handling:
- Achievement unlocked
- Level completed
- Enemy defeated
- Item collected
```

## Performance Tips

1. **Object Pooling**: Reuse objects instead of creating/destroying
2. **Culling**: Don't render off-screen elements
3. **Batching**: Group similar draw calls
4. **LOD**: Level of detail for distant objects
5. **Profiling**: Use Flutter's performance tools

## Testing Strategy

1. **Unit Tests**: Test individual components and systems
2. **Widget Tests**: Test UI components
3. **Integration Tests**: Test system interactions
4. **Performance Tests**: Benchmark critical systems
5. **Playtesting**: Real user feedback
