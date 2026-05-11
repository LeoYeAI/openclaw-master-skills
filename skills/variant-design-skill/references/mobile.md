# Mobile App Reference

iOS/Android app screens, onboarding flows, home screens, feed apps, detail views, and utility apps.

> **Design system references for this domain:**
> - `design-system/typography.md` — mobile type scales, thumb-friendly sizing
> - `design-system/spatial-design.md` — thumb zone layouts, bottom-sheet patterns
> - `design-system/interaction-design.md` — gesture hints, swipe actions, haptic feedback patterns
> - `design-system/responsive-design.md` — safe areas, input detection, orientation handling
> - `design-system/motion-design.md` — page transitions, pull-to-refresh, sheet animations

## Table of Contents
1. Starter Prompts
2. Color Palettes
3. Typography Pairings
4. Layout Patterns
5. Signature Details
6. Real Community Examples

---

## 1. Starter Prompts

Pick one as the content foundation, adapt to user's domain:

**Astronomy / Science**
- "A sky observation mobile app: 'Current visibility is optimal. The Lyrid meteor shower is entering peak activity in the northern hemisphere. Look toward constellation Lyra.' — dark star field, Observation Log + Sky Map dual panel."
- "A space weather alert app home screen: solar wind speed gauge, geomagnetic storm index (Kp: 4.2 — MODERATE), aurora visibility probability by latitude, and a 3-day forecast timeline."

**Health / Wellness**
- "A meditation app home screen: daily session recommendation, streak counter (Day 14), energy/mood tracker with 5-point emoji scale, soft peach-to-lavender gradient background, featured session card with duration and category."
- "A health tracker: daily ring completion (Move 780 / Exercise 35min / Stand 10hrs), resting heart rate graph at 58 bpm, sleep summary (7h 24m — 91 score), activity timeline for the past 6 hours."
- "A habit tracker home screen: greeting header ('Good morning, Jordan'), today's habit checklist with completion rings (Meditate ✓ / Read 20 min ✓ / Workout — / Water 6/8 ○), weekly streak heatmap, and a motivational quote card at the bottom."

**Finance / Productivity**
- "A finance mobile app: net worth hero number ($84,320), portfolio donut chart by asset class, recent transactions list (Netflix $15.99, Whole Foods $62.40, Payroll +$3,200), bottom tab nav with 5 items."
- "A personal expense tracker: monthly budget ring (spent $1,840 of $2,500), top spending categories as horizontal bar chart (Food 34% / Transport 21% / Entertainment 18%), recent receipts feed with merchant logos and amounts."

**Social / Lifestyle**
- "A social feed mobile app: stories row (8 circular avatars with unread rings), post cards with user avatar, image attachment, like/comment/share actions, and a floating compose button anchored above the tab bar."
- "A dating app home screen: full-bleed profile photo card with name, age, and distance tag ('Maya, 27 — 2 miles away'), swipe action buttons (pass / super like / like), match queue strip at the top, and a settings icon."
- "A food delivery home screen: location header ('Delivering to: 340 Oak Ave'), search bar, horizontal category chips (Pizza / Sushi / Burgers / Thai / Salads), featured restaurant cards with rating stars and delivery ETA, and a persistent cart button with item count badge."

**Media / Entertainment**
- "A music player screen (Spotify-style): full-bleed album art, artist name and track title, playback progress bar with timestamps, shuffle/back/play/forward/repeat controls, heart and menu icons, lyrics toggle button at the bottom."
- "A local events discovery app: city selector with map pin, 'This Weekend' section header, event cards with cover photo / date chip / venue name / price tag, a horizontal filter row (Music / Food / Art / Sports), and a saved events count in the tab bar."

---

## 2. Color Palettes

### Night Sky (astronomy / dark media)
```
--bg:        #050A18
--surface:   #0D1525
--card:      #131E35
--border:    #1E2D4A
--text:      #E8F0FF
--muted:     #4A5A7A
--accent:    #4A9EFF   /* sky blue */
--accent-2:  #A78BFA   /* nebula purple */
--star:      #FFFFFF
--safe-area-top:    env(safe-area-inset-top)
--safe-area-bottom: env(safe-area-inset-bottom)
```

### Wellness Soft (health / meditation)
```
--bg:        #F8F5F2
--surface:   #FFFFFF
--card:      #FFFFFF
--border:    #EDE8E3
--text:      #2D2840
--muted:     #9B8FA8
--accent:    #7C6BC4   /* soft violet */
--positive:  #4CAF7D
--safe-area-top:    env(safe-area-inset-top)
--safe-area-bottom: env(safe-area-inset-bottom)
```

### Spotify Dark (music / media streaming)
```
--bg:        #000000
--surface:   #121212
--card:      #1A1A1A
--border:    #282828
--text:      #FFFFFF
--muted:     #B3B3B3
--accent:    #1DB954   /* Spotify green */
--accent-2:  #1ED760   /* hover green */
--safe-area-top:    env(safe-area-inset-top)
--safe-area-bottom: env(safe-area-inset-bottom)
```

### iOS Light (system / utility / finance)
```
--bg:        #F2F2F7
--surface:   #FFFFFF
--card:      #FFFFFF
--border:    #C6C6C8
--text:      #000000
--muted:     #8E8E93
--accent:    #007AFF   /* iOS blue */
--positive:  #34C759
--destructive: #FF3B30
--safe-area-top:    env(safe-area-inset-top)
--safe-area-bottom: env(safe-area-inset-bottom)
```

### Warm Lifestyle (food / social / dating)
```
--bg:        #FDF6F0
--surface:   #FFFFFF
--card:      #FFFFFF
--border:    #F0E4D7
--text:      #1A1008
--muted:     #A0846A
--accent:    #F4622A   /* warm orange */
--accent-2:  #F9A86C   /* peach */
--positive:  #4CAF7D
--safe-area-top:    env(safe-area-inset-top)
--safe-area-bottom: env(safe-area-inset-bottom)
```

---

## 3. Typography Pairings

| Display (headings / hero text) | Body (labels / descriptions) | Feel |
|---|---|---|
| `Plus Jakarta Sans` | `DM Sans` | Modern, friendly, app-native |
| `Nunito` | `Inter` | Rounded, approachable, lifestyle |
| `Outfit` | `Manrope` | Clean geometric, fintech / utility |
| `Sora` | `Figtree` | Airy, editorial-adjacent, wellness |
| `Onest` | `Geist` | Sharp, developer / productivity |
| `Manrope` | `Nunito` | Balanced weight contrast, social / dating |

**Rule:** Mobile body text minimum 15px/16px. Touch targets 44px minimum. Use `font-size: 16px` on inputs to prevent iOS zoom. Hero numbers and metric displays work well in the Display font at 32–48px. Tab bar labels should be 10–11px, caps or sentence case depending on palette weight.

---

## 4. Layout Patterns

### Pattern A: Astronomy App (dual panel)
```
┌─────────────────────────┐
│ ◀  Observation Log      │  ← header with back nav
├─────────────────────────┤
│ [STAR MAP — dark bg]    │
│   constellation lines   │
│   labeled stars         │
├─────────────────────────┤
│ Current visibility:     │
│ optimal                 │
│ ─────────────────────   │
│ The Lyrid meteor shower │
│ is entering peak...     │
├─────────────────────────┤
│ Log Entry  •  3 Hrs Ago │
│ Sky Map    •  Loading   │
└─────────────────────────┘
```

### Pattern B: Onboarding Flow (full-screen card + progress dots)
```
┌─────────────────────────┐
│                         │  ← status bar (safe area)
│   [ILLUSTRATION / BG]   │
│                         │
│                         │
│   ● ● ○ ○               │  ← progress dots (step 2 of 4)
│                         │
│  ┌───────────────────┐  │
│  │  Your mindful     │  │
│  │  journey starts   │  │
│  │  here.            │  │
│  │                   │  │
│  │  Set your daily   │  │
│  │  intention and    │  │
│  │  build a streak.  │  │
│  └───────────────────┘  │
│                         │
│  [    Get Started    ]  │  ← primary CTA button (44px+)
│  Already have account?  │  ← secondary text link
│                         │  ← home indicator (safe area)
└─────────────────────────┘
```

### Pattern C: Feed / Social Timeline
```
┌─────────────────────────┐
│ ≡  MyApp       🔔  👤   │  ← top nav bar
├─────────────────────────┤
│ ○ ○ ○ ○ ○ ○ ○ ○        │  ← stories row (avatars)
├─────────────────────────┤
│ ┌─────────────────────┐ │
│ │ 👤 username  • 2h   │ │
│ │ [POST IMAGE]        │ │
│ │ Caption text here…  │ │
│ │ ♡ 142  💬 38  ↗    │ │  ← action row
│ └─────────────────────┘ │
├─────────────────────────┤
│ ┌─────────────────────┐ │
│ │ 👤 username  • 5h   │ │
│ │ Caption only post…  │ │
│ │ ♡ 89   💬 12  ↗    │ │
│ └─────────────────────┘ │
├─────────────────────────┤
│  🏠    🔍    ✚    🔔    👤  │  ← bottom tab bar (5 items)
└─────────────────────────┘
       ↑ floating compose button anchored above tabs
```

### Pattern D: Detail View (hero image + scrollable content + FAB)
```
┌─────────────────────────┐
│ ◀                   ⋯   │  ← overlay nav on hero
│ [HERO IMAGE — full      │
│  bleed, 240px tall]     │
│                         │
├─────────────────────────┤
│ Restaurant Name         │  ← scrollable content begins
│ ★ 4.7  (320 reviews)   │
│ Italian · $$  · 0.4 mi  │
│ ─────────────────────── │
│ About                   │
│ Authentic Neapolitan    │
│ pizza since 1987…       │
│ ─────────────────────── │
│ Most Ordered            │
│ [Item card] [Item card] │
│ [Item card] [Item card] │
│                         │
│         [  Order Now  ] │  ← floating action button
│                         │  ← safe area bottom
└─────────────────────────┘
```

---

## 5. Signature Details

- **Status bar**: time left, battery, signal — always present on mobile; use `padding-top: env(safe-area-inset-top)` to avoid overlap
- **Bottom tab bar**: 4–5 icons with labels, active state in accent color, unread badges as small red circles
- **Safe area**: respect notch/home indicator spacing on both top and bottom with `env(safe-area-inset-*)` CSS variables
- **Card radius**: 16–20px on mobile (larger than desktop); use 24px for hero cards and modals
- **Touch targets**: minimum 44px height for all interactive elements; add padding rather than increasing visual size
- **Haptic hint text**: "Tap to expand" / "Swipe to dismiss" in tiny muted caption text (11–12px)
- **Pull-to-refresh indicator** at top of scroll views with spinner or custom animation

---

## 6. Real Community Examples

### Night Sky Observer — @astrobuilder

**Prompt:** "A dark-mode astronomy app showing a live sky map for tonight's Lyrid meteor shower. Top panel: interactive star map with constellation lines in muted blue, labeled stars (Vega, Altair, Deneb), and current meteor radiant marker. Bottom panel: observation log with 'Current visibility: Optimal' status chip, scroll-locked entry text, and a 'Begin Log' button. Status bar visible. Deep navy background #050A18."

**What makes it work:**
- The dual-panel split uses the full screen height intentionally — the star map gets ~55% of the viewport, establishing atmosphere before any text appears, which is the correct mobile hierarchy for an immersive utility app.
- Constellation lines rendered at 15% opacity avoid competing with the labeled accent stars, showing restraint that keeps the map readable on a phone held at arm's length in the dark.
- The "Current visibility: Optimal" status chip uses the accent blue (#4A9EFF) at full saturation as the one high-attention element — every other color on screen is desaturated, so the eye lands there first without fighting for attention.

---

### Still — Daily Meditation — @calmui

**Prompt:** "A meditation app home screen for 6:45 AM. Soft peach-to-lavender gradient background. Top section: greeting 'Good morning, Sarah' with today's date. Featured session card: 'Morning Clarity — 10 min' with a Play button, category tag 'Focus', and a faint wave illustration. Below: streak counter '14 days' with a flame icon. Mood check-in row: 5 emoji buttons (😴 😕 😐 🙂 😊) with 'How are you feeling?' label. Bottom tab bar with 5 icons."

**What makes it work:**
- The gradient background (#FDF0E8 to #EDE8F5) does the entire emotional job of the palette — every surface layer above it stays white or near-white, so the warmth reads as a considered design decision rather than noise.
- Placing the streak counter below the featured session rather than above it respects the user's primary goal (starting a session) before surfacing the gamification layer — a subtle content hierarchy choice that keeps the app from feeling manipulative on first open.
- The mood check-in uses emoji rather than sliders or text labels, cutting cognitive load to near zero at a time of day when the user is still waking up — the input mechanism matches the context.

---

### Flare — Food Delivery Home — @deliveryux

**Prompt:** "A food delivery app home screen. Warm white background #FDF6F0. Top: location header with pin icon 'Delivering to: 340 Oak Ave' and a dropdown chevron. Search bar below. Horizontal scrollable category chips: Pizza / Sushi / Burgers / Thai / Salads / Ramen — active chip filled in warm orange #F4622A with white text. Featured section 'Popular Near You': two large restaurant cards with cover photo, restaurant name, star rating (4.6 ★), cuisine tag, and '25–35 min' delivery estimate. Bottom tab bar. Floating cart button in orange with item count badge '3'."

**What makes it work:**
- The active category chip uses the full accent color (#F4622A fill, white label) while inactive chips stay border-only — this single pattern communicates filter state without any icon or checkmark, which is the right level of visual economy for a horizontal scroll component where space is tight.
- Delivery time estimates ('25–35 min') appear on the card before price or distance, matching the actual mental model of a hungry user: feasibility first, cost second.
- The floating cart button with a live item count badge stays anchored above the tab bar rather than replacing a tab — this preserves the navigation structure while keeping the purchase action permanently visible, which increases conversion without cluttering the information architecture.
