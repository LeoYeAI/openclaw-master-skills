# Example: Flutter Game Jump Mechanic

This example demonstrates how to use the AI Prompt Generator skill to create a jumping mechanic for a 2D platformer game in Flutter.

## 📋 Request to Skill

**User says:**
```
Add jumping to my 2D platformer game using Flame
```

## 🎨 Generated Prompt

```dart
Implement a jumping mechanic for a 2D platformer game in Flutter using Flame:

REQUIREMENTS:
- Jump Types:
  * Single jump (tap once)
  * Variable height (hold for higher jump, tap for short hop)
  * Double jump (optional power-up)
- Physics:
  * Realistic gravity (9.8 m/s²)
  * Predictable jump arc
  * Terminal velocity for falling
- Input:
  * Touch/screen tap for jump
  * Keyboard support (Space bar)
  * Gamepad support (A button)
- Visual Feedback:
  * Jump animation (crouch → jump → fall → land)
  * Dust particles on landing
  * Stretch/squash effect during jump
  * Trail effect for double jump
- Audio:
  * Jump sound (whoosh)
  * Landing sound (thud)
  * Double jump sound (sparkle)
- Controls:
  * Variable height based on press duration
  * Coyote time (jump grace period after leaving platform)
  * Jump buffering (register jump input slightly before landing)

IMPLEMENTATION DETAILS:

1. Player Component
   - Jump velocity calculation:
     * Base jump force: 400 pixels/second
     * Variable height: 200-600 pixels/second based on hold time
   - Gravity application:
     * Gravity constant: 1200 pixels/second²
     * Terminal velocity: 800 pixels/second
   - Ground detection:
     * Collision with platform tiles
     * One-way platforms (jump through from below)
   - Coyote time:
     * 0.1 seconds grace period after leaving platform
   - Jump buffering:
     * 0.05 seconds input buffer before landing

2. Animation System
   - States: Idle, Crouch, Jump, Fall, Land
   - Transitions:
     * Idle → Crouch (when jump input detected)
     * Crouch → Jump (after 0.05s crouch animation)
     * Jump → Fall (when vertical velocity becomes negative)
     * Fall → Land (when ground detected)
   - Particle effects:
     * Dust cloud on landing (8-12 particles)
     * Landing impact animation (scale effect)
   - Stretch/squash:
     * Stretch vertically during jump (120% height, 80% width)
     * Squash horizontally on landing (120% width, 80% height)

3. Input Handling
   - Touch detection:
     * Tap anywhere on right side of screen
     * Multi-touch support (movement + jump)
   - Press duration tracking:
     * Min hold: 0.05s (short hop)
     * Max hold: 0.3s (full jump)
     * Linear interpolation between min and max
   - Jump strength calculation:
     * jumpForce = lerp(minJump, maxJump, holdTime/maxHoldTime)
   - Buffer system:
     * Queue jump input if pressed slightly before landing
     * Execute buffered jump on landing

4. Audio Integration
   - Sound effect triggers:
     * Jump: When jump velocity applied
     * Land: When ground detected after falling
     * Double jump: When second jump executed
   - Volume control:
     * Master volume setting
     * SFX volume multiplier
   - Pooling:
     * Pre-load 3 instances of each sound
     * Prevent sound overlap

INCLUDE:
1. Player component with complete jump logic
   - Jump mechanics implementation
   - Gravity and physics
   - Ground detection
   - State management

2. Physics implementation (gravity, velocity)
   - Gravity constant definition
   - Velocity updates
   - Position integration
   - Collision response

3. Input handling for variable jump
   - Touch input processing
   - Duration tracking
   - Buffer system
   - Coyote time logic

4. Animation system for jump states
   - Sprite animation setup
   - State machine
   - Transition logic
   - Particle effects

5. Particle effects for landing
   - Particle emitter configuration
   - Dust cloud generation
   - Performance optimization
   - Visual polish

6. Audio integration
   - Sound loading
   - Trigger logic
   - Volume control
   - Pooling system

7. Example usage
   - Complete player component setup
   - Game integration
   - Configuration options
   - Testing commands

8. Performance optimizations
   - Object pooling for particles
   - Efficient collision detection
   - Sprite batching
   - Update optimization

9. Testing approach
   - Unit tests for jump logic
   - Integration tests for physics
   - Manual testing checklist
   - Performance benchmarks

CONFIGURATION:
```dart
class JumpConfig {
  static const double gravity = 1200.0;
  static const double minJumpForce = 200.0;
  static const double maxJumpForce = 600.0;
  static const double terminalVelocity = 800.0;
  static const double coyoteTime = 0.1;
  static const double jumpBufferTime = 0.05;
  static const double minHoldTime = 0.05;
  static const double maxHoldTime = 0.3;
  static const bool enableDoubleJump = false;
  static const bool enableCoyoteTime = true;
  static const bool enableJumpBuffer = true;
}
```

EXAMPLE USAGE:
```dart
// In your game class
class PlatformerGame extends FlameGame {
  late Player player;
  
  @override
  Future<void> onLoad() async {
    await super.onLoad();
    
    player = Player(
      position: Vector2(100, 300),
      jumpConfig: JumpConfig(
        enableDoubleJump: true,
        maxJumpForce: 650.0,
      ),
    );
    
    add(player);
  }
}

// Player component
class Player extends SpriteAnimationComponent with HasGameRef, Gravity {
  late final JumpBehavior _jumpBehavior;
  
  @override
  Future<void> onLoad() async {
    await super.onLoad();
    _jumpBehavior = JumpBehavior(config: JumpConfig());
    add(_jumpBehavior);
  }
  
  void jump() {
    _jumpBehavior.executeJump();
  }
}
```

TESTING CHECKLIST:
- [ ] Single jump works correctly
- [ ] Variable height based on hold time
- [ ] Double jump works (if enabled)
- [ ] Coyote time functions properly
- [ ] Jump buffer registers early inputs
- [ ] Animations play correctly
- [ ] Particle effects display on landing
- [ ] Sound effects play at right times
- [ ] No performance issues
- [ ] Works on mobile and desktop
- [ ] Gamepad support works
- [ ] Keyboard support works
```

## 🤖 AI Tool Response Example

When you paste this prompt into ChatGPT or Claude, you'll get:

1. **Complete Player Component**
   ```dart
   class Player extends SpriteAnimationComponent 
       with HasGameRef, Gravity, CollisionCallbacks {
     // ... full implementation with jump mechanics
   }
   ```

2. **Jump Behavior Class**
   ```dart
   class JumpBehavior extends Component {
     final JumpConfig config;
     // ... complete jump logic
   }
   ```

3. **Physics System**
   ```dart
   mixin Gravity on Component {
     Vector2 velocity = Vector2.zero();
     double gravity = JumpConfig.gravity;
     // ... physics implementation
   }
   ```

4. **Animation Controller**
   ```dart
   class PlayerAnimationController {
     late SpriteAnimation idleAnimation;
     late SpriteAnimation jumpAnimation;
     // ... animation states
   }
   ```

5. **Particle System**
   ```dart
   class LandingParticles extends ParticleSystemComponent {
     // ... dust cloud effect
   }
   ```

6. **Audio Manager**
   ```dart
   class JumpAudio {
     final FlameAudio audio;
     // ... sound effect management
   }
   ```

7. **Input Handler**
   ```dart
   class JumpInputHandler extends Component {
     // ... touch and keyboard input
   }
   ```

8. **Tests**
   ```dart
   group('Jump Mechanics', () {
     test('should apply correct jump force', () {
       // ... unit tests
     });
   });
   ```

## 📊 Results

### What You Get

✅ **Complete Jump System** - All mechanics implemented
✅ **Polish Effects** - Animations, particles, audio
✅ **Responsive Controls** - Coyote time, jump buffering
✅ **Configuration** - Easy to tweak parameters
✅ **Performance Optimized** - Object pooling, efficient updates
✅ **Well Tested** - Unit and integration tests

### Time Saved

| Task | Manual | With Prompt |
|------|--------|-------------|
| Jump physics | 2-3 hours | 15 minutes |
| Variable height | 1-2 hours | 10 minutes |
| Animations | 2-3 hours | 15 minutes |
| Audio integration | 1 hour | 10 minutes |
| Polish effects | 2-3 hours | 20 minutes |
| Testing | 1-2 hours | 10 minutes |
| **Total** | **9-14 hours** | **1.5 hours** |

## 🎯 Customization Options

### Adjust Feel

**Floaty Jump (like Mario):**
```dart
JumpConfig(
  gravity: 800.0,  // Lower gravity
  maxJumpForce: 500.0,
  coyoteTime: 0.15,  // Longer grace period
)
```

**Snappy Jump (like Celeste):**
```dart
JumpConfig(
  gravity: 1500.0,  // Higher gravity
  maxJumpForce: 700.0,
  jumpBufferTime: 0.1,  // Longer buffer
)
```

**Realistic Physics:**
```dart
JumpConfig(
  gravity: 980.0,  // Real-world gravity (scaled)
  terminalVelocity: 600.0,
  enableDoubleJump: false,
  enableCoyoteTime: false,
)
```

### Add Features

**Wall Jump:**
```dart
// Add to requirements:
- Wall slide when touching wall while falling
- Wall jump away from wall
- Wall jump cooldown to prevent spam
```

**Air Dash:**
```dart
// Add to requirements:
- Dash in 8 directions while airborne
- Dash cooldown (1 second)
- Dash trail effect
- Limited uses (reset on landing)
```

**Variable Gravity:**
```dart
// Add to requirements:
- Lower gravity during jump apex
- Higher gravity when falling
- Creates more floaty feel at peak of jump
```

## 💡 Pro Tips

1. **Tweak Values**: Adjust gravity and jump force to match your game's feel
2. **Test Often**: Jump feel is crucial - test on actual devices
3. **Watch Frame Rate**: Ensure 60fps during jumps
4. **Add Juice**: Small effects make jumps feel satisfying
5. **Get Feedback**: Let players test and give feedback on feel

## 🎮 Game Feel Principles

### The 3 Core Elements

1. **Responsive** - Input feels immediate
2. **Forgiving** - Coyote time and buffering
3. **Satisfying** - Audio, visual, and motion feedback

### Polish Checklist

- [ ] Screen shake on landing
- [ ] Time slowdown during jump apex
- [ ] Trail effect during fast movement
- [ ] Dust particles on landing
- [ ] Sound effects for every action
- [ ] Stretch and squash animations
- [ ] Camera follow with slight lag

## 🔗 Related Examples

- [Player Movement System](./player_movement.md)
- [Enemy AI](./enemy_ai.md)
- [Level Design](./level_design.md)
- [Camera System](./camera_system.md)

---

**Next**: [Example: Flutter E-Commerce App](./ecommerce_app.md)
