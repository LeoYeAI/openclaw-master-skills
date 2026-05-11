# Education & Learning Apps Reference

Language learning, science education, quiz/flashcard apps, tutoring interfaces, LMS platforms, kids learning, coding bootcamps.

> **Design system references for this domain:**
> - `design-system/typography.md` — readable body text, accessibility-first sizing
> - `design-system/color-and-contrast.md` — semantic feedback colors (correct/incorrect), calming palettes
> - `design-system/interaction-design.md` — quiz interactions, progress indicators, gamification states
> - `design-system/motion-design.md` — celebration animations, progress transitions
> - `design-system/ux-writing.md` — encouraging feedback copy, instructional microcopy

## Table of Contents
1. Starter Prompts
2. Color Palettes
3. Typography Pairings
4. Layout Patterns
5. Signature Details
6. Real Community Examples

---

## 1. Starter Prompts

**Language Learning**
- "A French sentence translation exercise: 'TRANSLATE THIS SENTENCE: The museum is closed on Mondays.' — Le musée / fermé / lundi word chips, CHECK ANSWER button, green accent background."
- "A Japanese-English language app: bilingual side-by-side layout, Japanese large on left, English translation right, furigana support, vocabulary drill flow."

**Science & Math Education**
- "A planetary science database: Mars element table (Overview/Aphelion/Mass/Gravity/Orbital Period), red/orange dominant, encyclopedia-style card."
- "A math problem-solving app: step-by-step equation reveal, hint system, progress bar, worked example toggle."

**General Study Tools**
- "A vocabulary flashcard app: word front/back flip, difficulty rating (Easy/Hard/Again), session streak, spaced repetition progress."
- "A coding tutorial interface: lesson outline sidebar, live code editor, output panel, concept explanation tooltip."

**Coding Bootcamp**
- "A coding bootcamp curriculum dashboard: 12-week track progress, module completion rings, daily challenge streak, leaderboard panel. Dark IDE-style with neon green accent. Current lesson: 'React Hooks — useState & useEffect'. Next milestone badge unlocking at 70%."
- "A hands-on JavaScript bootcamp exercise: split-screen editor on the left with syntax highlighting, test output on the right showing pass/fail cases. Bright pass indicators (#22C55E), red fail markers, 'Run Tests' CTA full-width at bottom."

**Medical & Health Education**
- "A medical anatomy learning app: 3D body diagram with clickable regions, selected region 'Cardiac Muscle' shows definition card, related quiz question, and difficulty tier badge. Clinical white surface, deep navy text, red accent on active region."
- "A pharmacology flashcard session: drug name front-face bold, back reveals mechanism / indications / contraindications in grouped sections. Progress ring in corner: 14/40 cards. Calm blue-gray palette for focus."

**Corporate Training LMS**
- "A corporate compliance training module: 'Data Privacy & GDPR' course header, chapter list with locked/unlocked states, current lesson video embed, note-taking sidebar, completion certificate progress at 60%. Professional navy and white, company logo placeholder."
- "An employee onboarding LMS dashboard: welcome banner 'Day 1 of 30', required modules checklist, time-to-complete estimates per course, manager-assigned tasks panel, completion donut chart. Clean enterprise layout, trust-building sans-serif."

**Kids Learning App**
- "A kids reading comprehension app for ages 6–9: large friendly type, illustrated story panel, 3-question quiz below, star reward animation on completion, 'Read to me' audio toggle. Bright primary colors, rounded corners everywhere, large tap targets."
- "An elementary math game: single addition problem centered, illustrated number line below, animated character reacts to correct/wrong answers, score counter top-right. Bold playful palette: sunshine yellow bg, cobalt blue accents."

**University Course Platform**
- "A university online course platform: course header 'Introduction to Cognitive Science — Week 7 of 12', lecture video player, downloadable slides list, discussion thread panel on the right. Academic but modern: warm white bg, deep charcoal text, university blue accent."
- "A graduate seminar reading interface: PDF annotation view, inline highlighting tool, margin comment thread, citation cross-reference sidebar. Scholarly serif body text, muted cream background, ink-dark text."

---

## 2. Color Palettes

### French Green (language learning)
```
--bg:        #16A34A
--surface:   #15803D
--card:      #FAFAF9
--border:    #D1FAE5
--text:      #1C1C1C
--muted:     #6B7A6B
--accent:    #FDE047   /* bright yellow — CTA, word chips */
--correct:   #22C55E
--wrong:     #EF4444
```

### Academic Dark (science/reference)
```
--bg:        #1A0A00
--surface:   #2C1200
--card:      #FDF5E6
--border:    #7B1E1E
--text:      #FDF5E6
--muted:     #A0846A
--accent:    #E55A00   /* burnt orange — headings, highlights */
--correct:   #22C55E
--wrong:     #EF4444
```

### Study Light (general education)
```
--bg:        #F0F9FF
--surface:   #E0F2FE
--card:      #FFFFFF
--border:    #BAE6FD
--text:      #0C4A6E
--muted:     #4A7A9B
--accent:    #0EA5E9   /* sky blue — interactive elements */
--correct:   #16A34A
--wrong:     #DC2626
```

### Duolingo Green (gamified learning)
```
--bg:        #FFFFFF
--surface:   #F7F7F7
--card:      #FFFFFF
--border:    #E5E5E5
--text:      #3C3C3C
--muted:     #AFAFAF
--accent:    #58CC02   /* Duolingo signature green — XP, streaks, CTAs */
--correct:   #58CC02
--wrong:     #FF4B4B
```

### Corporate LMS (enterprise training)
```
--bg:        #F4F6F9
--surface:   #FFFFFF
--card:      #FFFFFF
--border:    #D1D9E6
--text:      #0F1E3C
--muted:     #6B7A99
--accent:    #1A4FA0   /* professional navy — module headers, progress */
--correct:   #0D7A3E
--wrong:     #C62828
```

---

## 3. Typography Pairings

| Display (headings/titles) | Body (content/labels) | Feel |
|---|---|---|
| `Nunito` | `Nunito` (lighter weight) | Friendly, rounded — kids & language apps |
| `Poppins` | `DM Sans` | Modern, approachable — bootcamp, LMS |
| `Quicksand` | `Source Serif 4` | Playful yet legible — elementary education |
| `Plus Jakarta Sans` | `Literata` | Clean editorial — university, long-form course content |
| `Space Grotesk` | `Work Sans` | Technical, structured — coding tutorials, STEM |
| `Outfit` | `Merriweather` | Warm and scholarly — science reference, medical education |

**Rule:** Reading comprehension contexts require generous line-height 1.8+ and paragraph max-width capped at 65ch to prevent eye fatigue during extended study sessions.

---

## 4. Layout Patterns

### Pattern A: Translation Exercise
```
┌──────────────────────────────────┐
│  TRANSLATE THIS SENTENCE         │
│  ─────────────────────────────  │
│  "The museum is closed on        │
│   Mondays."                      │
├──────────────────────────────────┤
│  [Le musée] [fermé] [lundi]      │  ← word chips
│  [le] [est] [fermé] [lundi]      │
├──────────────────────────────────┤
│  YOUR TRANSLATION:               │
│  [________________]              │
│  [CHECK ANSWER]                  │
└──────────────────────────────────┘
```

### Pattern B: Flashcard / Spaced Repetition
```
┌──────────────────────────────────┐
│  DECK: Organic Chemistry  14/40  │  ← deck name + card counter
│  ████████████░░░░░░░░ 35%        │  ← session progress bar
├──────────────────────────────────┤
│                                  │
│                                  │
│        mitochondria              │  ← front face: term
│                                  │
│                                  │
│         [ SHOW ANSWER ]          │  ← tap to flip
└──────────────────────────────────┘

After flip:
┌──────────────────────────────────┐
│  DECK: Organic Chemistry  14/40  │
│  ████████████░░░░░░░░ 35%        │
├──────────────────────────────────┤
│                                  │
│  The powerhouse of the cell;     │  ← back face: definition
│  produces ATP via oxidative      │
│  phosphorylation.                │
│                                  │
├──────────────────────────────────┤
│  [Again]   [Hard]   [Good]   [Easy] │  ← spaced repetition rating
└──────────────────────────────────┘
```

### Pattern C: Video Lesson + Notes Split View
```
┌─────────────────────────┬────────────────────┐
│  Course: Week 7 / Ch 3  │  MY NOTES          │
├─────────────────────────┤  ────────────────  │
│                         │  [+ Add note]      │
│  ┌───────────────────┐  │                    │
│  │   VIDEO PLAYER    │  │  12:34 — Heap      │
│  │   ▶  00:12:34     │  │  allocation note   │
│  └───────────────────┘  │                    │
│                         │  08:02 — Compare   │
│  ── Chapters ─────────  │  with stack alloc  │
│  ✓ 1. Intro (4 min)     │                    │
│  ✓ 2. Stack (8 min)     │  ────────────────  │
│  ▶ 3. Heap  (11 min)    │  RESOURCES         │
│  ○ 4. GC    (9 min)     │  ↓ Slides.pdf      │
│  ○ 5. Quiz              │  ↓ Cheat Sheet     │
└─────────────────────────┴────────────────────┘
```

### Pattern D: Course Progress / Chapter Navigator
```
┌──────────────────────────────────────────────┐
│  Introduction to Cognitive Science           │
│  ██████████████████░░░░░░░  Week 7 of 12     │
├──────────────────────────────────────────────┤
│  COMPLETED                                   │
│  ✓  Ch 1 — Foundations of Cognition          │
│  ✓  Ch 2 — Perception & Attention            │
│  ✓  Ch 3 — Memory Systems                   │
│  ✓  Ch 4 — Language & Thought               │
│  ─────────────────────────────────────────   │
│  IN PROGRESS                                 │
│  ▶  Ch 5 — Decision Making          60%      │
│  ─────────────────────────────────────────   │
│  UPCOMING                            LOCKED  │
│  ○  Ch 6 — Emotion & Motivation      🔒      │
│  ○  Ch 7 — Social Cognition          🔒      │
│  ─────────────────────────────────────────   │
│  [ VIEW CERTIFICATE PROGRESS ]  4/8 done     │
└──────────────────────────────────────────────┘
```

---

## 5. Signature Details

- **Word chips**: rounded pill buttons, drag-to-arrange
- **CHECK ANSWER** CTA: full-width, high contrast
- **Progress bar**: lesson completion at top of every screen
- **Streak counter**: 🔥 12 days (emoji acceptable in educational context)
- **Correct/wrong flash**: green overlay vs. red shake animation
- **Bilingual layout**: language A large left, language B smaller right

---

## 6. Real Community Examples

### Duolingo-Style Language Lesson — @learnfast_ui
**Prompt:** "A French translation exercise app screen: bright green background (#58CC02), white card for the exercise area, bold Nunito heading 'TRANSLATE THIS SENTENCE', word chip row with [Le musée] [est] [fermé] [lundi], full-width yellow CHECK ANSWER button at bottom, 🔥 7-day streak in top right, XP progress bar at top."

**What makes it work:** The high-chroma green background creates immediate energy without sacrificing legibility — the white card acts as a focused reading zone that pops off it. Word chips use generous padding (12px 20px) and a subtle drop shadow so they read as interactive objects rather than static labels. The single full-width CTA eliminates decision fatigue: there is only one next action.

---

### Science Flashcard Deck — @khan_cards
**Prompt:** "A spaced repetition flashcard app for high school biology: card-centered layout on a calm #F0F9FF background, front face shows 'Mitochondria' in 32px Plus Jakarta Sans bold, back face reveals a two-section definition (Function / Key Detail) with a small diagram area. Bottom bar has four rating buttons — Again / Hard / Good / Easy — in muted pill style. Progress ring in top right: 18 of 40 cards."

**What makes it work:** The two-section back face (Function vs. Key Detail) mirrors how students naturally encode information — function first, then elaboration — which improves recall. Rating buttons use low-saturation colors so they don't compete with the card content; only the "Easy" button gets the accent green. The progress ring uses a thin 3px stroke so it stays informative without dominating the header.

---

### Corporate Compliance Training Module — @lms_design_co
**Prompt:** "A corporate LMS module screen for 'Data Privacy & GDPR Essentials': professional navy (#1A4FA0) header bar with company logo placeholder and course title, chapter list below showing 5 modules with locked/unlocked states and time estimates, current lesson area with embedded video player and a notes sidebar, bottom footer showing 'Module 3 of 5 — 60% complete' with a completion certificate progress indicator. Clean white surface, Poppins for headings and DM Sans for body."

**What makes it work:** The locked/unlocked chapter states use a consistent iconography system (filled check, active play arrow, padlock) that communicates course linearity at a glance — learners always know where they are and what's next. The 60% progress indicator in the footer is persistent rather than modal, creating low-friction awareness of progress without interrupting the lesson flow. Navy as the sole accent color reads as institutional trust — appropriate for compliance content where authority signals matter.
