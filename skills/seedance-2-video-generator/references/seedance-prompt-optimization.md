# Werydance 2.0 Prompt Optimization (Almighty Reference)

Use this guide when users want better control, stronger consistency, or mixed-reference generation with `WERYDANCE_2_0`.

## Core rule

Do not treat prompt writing as decoration. Treat it as a production spec:

- what to preserve
- what to imitate
- what to change
- what to end on

## Recommended planning structure

For complex requests, structure internally as:

1. Mode
2. Asset mapping
3. Timeline beats
4. Final prompt
5. Constraints
6. Generation settings

## Mode selection

| Mode | Use when | Input shape |
|---|---|---|
| Text-only | no media references | `prompt` |
| Single-image | preserve one identity/composition anchor | `image + prompt` |
| Multi-image | ordered visual waypoints | `images + prompt` |
| Almighty mixed reference | need image/video/audio reference together | `images/videos/audios + prompt` |

## Layered asset mapping (@asset style)

Always map references by role before writing final prompt.

- `@图1`: identity/composition anchor (first frame)
- `@图2/@图3`: transition waypoints
- `@视频1`: camera language / motion grammar
- `@视频2`: action rhythm / effect reference
- `@音频1`: BGM rhythm, mood pacing, or narration tone

State each role explicitly. Never write only “参考这个视频的感觉”.

## Timeline beats

### 5 seconds

- `0-2s`: establish anchor and first action
- `2-4s`: core motion/effect
- `4-5s`: stable payoff frame

### 10 seconds

- `0-3s`: setup
- `3-7s`: motion development
- `7-10s`: climax and landing

### 15 seconds

- `0-4s`: establish world and subject
- `4-9s`: action build
- `9-13s`: transition/escalation
- `13-15s`: final payoff and stable frame

## Almighty prompt skeleton

```text
Use @图1 as opening composition and identity lock.
Reference @视频1 for camera movement style and @视频2 for action rhythm.
Use @音频1 as pacing bed.

9:16 vertical, 5s.
0-2s: ...
2-4s: ...
4-5s: ...

Keep identity, costume, and scene logic consistent.
No abrupt hard cut, no identity drift, no unrelated scene rewrite.
```

## Scenario templates

### Video extension

```text
Extend @视频1 by 5s as a continuous next segment.
Keep same character identity, lens logic, and lighting continuity.
Added segment only: ...
```

### Video fusion

```text
Create a smooth bridge shot between @视频1 and @视频2.
Insert one transition scene: ...
Maintain coherent camera language and consistent style.
```

### Continuous motion / one-take

```text
Use @图1 @图2 @图3 as ordered waypoints of a single uninterrupted take.
Character transitions from jump to roll in one continuous movement.
No hard cut.
```

### First-frame + motion imitation

```text
Start from @图1 exactly, then perform combat movement imitating @视频1 rhythm.
Preserve face, clothing, and environment continuity.
```

### Video edit

```text
Edit @视频1: replace character with ..., add ..., keep original pacing and shot structure.
```

## Quality checklist

Before submit, verify the prompt includes:

- identity lock
- camera language
- motion arc
- continuity constraints
- final payoff frame

## Anti-patterns

Avoid:

- “cinematic” without concrete camera/motion details
- stacking too many unrelated actions in 5s
- switching subject, environment, and style simultaneously
- vague “参考感觉” statements without role mapping

## Practical conversion rule

`rough idea -> mode -> asset mapping -> timeline beats -> final prompt -> settings`

If too long, remove decorative adjectives first; keep subject, action, camera, continuity, and payoff.
