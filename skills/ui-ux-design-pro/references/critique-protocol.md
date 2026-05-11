# Critique Protocol

## Pre-Delivery Self-Review

Before showing ANYTHING to the user, run through this entire checklist. If any check fails, iterate before presenting.

## Composition Review

### Layout

- Does the layout have rhythm? Dense areas give way to open content — not the same gap everywhere.
- Are proportions intentional? A 280px sidebar declares "navigation serves content." A specific number says something. If you can't articulate what your proportions communicate, they communicate nothing.
- Is there a focal point? Every screen has one thing the user came for. That thing dominates — through size, position, contrast, or surrounding space. When everything competes equally, nothing wins.

### Hierarchy

- Squint test: blur your eyes. Can you still identify the three most important elements? If everything blurs into sameness, hierarchy needs work.
- Can you draw the reading path? Eyes should flow naturally from primary to secondary to tertiary content.
- Is negative space doing work? Space is not emptiness — it is a tool for grouping, emphasis, and breathing room.

## Craft Review

### Spacing

- Is spacing consistent? The clearest sign of no system is inconsistent gaps.
- Does it follow the scale? Every value traces to the spacing tokens.
- Does density match intent? Dense for power users. Generous for new users.

### Typography

- Does the type hierarchy work at a glance? Size + weight + color creates distinct levels.
- Are labels distinct from body from headings? Each should be identifiable without reading.
- Is the typeface doing its job? Would swapping for the most common alternative make no difference? If yes, you defaulted.

### Surfaces and Depth

- Is elevation whisper-quiet? You should feel the hierarchy, not see it.
- One strategy? Borders-only everywhere, or shadows everywhere — not mixed.
- Do surfaces stack logically? Higher content = higher elevation.

### Color

- Does color mean something? Every colored element should have a reason.
- One accent? Multiple accents dilute focus.
- Does the palette feel like it belongs to THIS product?

### States

- Hover on every interactive element?
- Focus-visible on every focusable element?
- Disabled state that looks disabled but is still readable?
- Loading state for async operations?
- Empty state for empty data?
- Error state for failures?

## The Four Mandate Checks

### 1. Swap Test

Swap your typeface for Inter. Swap your layout for a standard sidebar+cards. Swap your colors for slate+blue. If the design doesn't feel meaningfully different after each swap, those elements were defaults, not choices.

### 2. Squint Test

Blur your eyes or step back from the screen. Can you:

- Identify the primary content area?
- Distinguish navigation from content?
- Find the primary action?
- Feel visual hierarchy?

If it all looks the same blurred, the hierarchy is too flat.

### 3. Signature Test

Point to five specific elements — actual components, not "the overall feel" — where your signature decision appears. These should be moments where another designer couldn't find your design indistinguishable from a template.

Examples:

- A metric card that uses sparklines in a unique position
- Typography pairing that evokes the product's domain
- A specific animation that reflects the product's personality
- A navigation pattern that mirrors the user's mental model
- Color usage that comes from the domain's world

### 4. Token Test

Read your CSS custom property names out loud:

- `--ink`, `--parchment`, `--hearth` → you're building a world
- `--gray-700`, `--surface-2`, `--color-primary` → you're filling a template

If token names could belong to any product, they lack identity.

## Nielsen's 10 Heuristics (Adapted)

1. **Visibility of system status:** Users know where they are, what's happening, what happened
2. **Match the real world:** Language, concepts, and flow match user expectations
3. **User control and freedom:** Undo, cancel, go back — always available
4. **Consistency:** Same patterns mean same things everywhere
5. **Error prevention:** Design prevents errors before they happen
6. **Recognition over recall:** Options visible, not memorized
7. **Flexibility and efficiency:** Shortcuts for experts, guidance for novices
8. **Aesthetic and minimalist design:** Every element earns its place
9. **Help users recognize, diagnose, and recover from errors:** Clear messages, clear solutions
10. **Help and documentation:** Contextual, searchable, task-oriented

## The Final Question

Look at what you've built.

**"If the user said this lacks craft, what would they mean?"**

Fix that thing. Then show it.

**"Would I proudly put my name on this?"**

If you hesitate, it's not done.
