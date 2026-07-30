# Larry Case Study — 500K TikTok Views in 5 Days

Source: Oliver Henry (@oliverhenry on X), February 2026

## Setup

- **Agent:** Larry, running on OpenClaw on an old gaming PC (NVIDIA 2070 Super, Ubuntu)
- **Model:** Claude (Anthropic) via OpenClaw
- **Apps promoted:** Snugly (AI room redesign), Liply (lip filler preview)
- **Posting tool:** Postiz API (posts as drafts, human adds music + publishes)
- **Image gen:** OpenAI gpt-image-1.5 (~$0.50/post, $0.25 with Batch API)
- **Communication:** WhatsApp
- **Skills used from ClaHub:** RevenueCat (analytics), Bird (X browsing)

## Results

- 500,000+ TikTok views in 5 days
- 234K views on top post
- 167K on second best
- 147K on third
- Four posts cleared 100K views
- 108 paying subscribers across both apps
- $588/month MRR
- Cost per post: ~$0.50 in API calls
- Human time per post: ~60 seconds

## The Slideshow Format

TikTok data: slideshows get 2.9x more comments, 1.9x more likes, 2.6x more shares vs video. Algorithm actively pushing photo content in 2026.

**Every slideshow has:**
- 6 slides exactly (TikTok's sweet spot)
- Text overlay on slide 1 with the hook
- Story-style caption mentioning the app naturally
- Max 5 hashtags

## Image Generation — Prompt Engineering

**The critical lesson: Lock the architecture.**

Write one incredibly detailed room/scene description and copy-paste into every prompt. Only change the STYLE between slides.

Lock: room dimensions, window count/position, door location, camera angle, furniture size, ceiling height, floor type.
Change: wall color, bedding, decor, lighting fixtures, style name.

**Example prompt:**
```
iPhone photo of a small UK rental kitchen. Narrow galley style kitchen, roughly 2.5m x 4m. Shot from the doorway at the near end, looking straight down the length. Countertops along the right wall with base cabinets and wall cabinets above. Small window on the far wall, centered, single pane, white UPVC frame, about 80cm wide. Left wall bare except for a small fridge freezer near the far end. Vinyl flooring. White ceiling, fluorescent strip light. Natural phone camera quality, realistic lighting. Portrait orientation. **Beautiful modern country style. Sage green painted shaker cabinets with brass cup handles. Solid oak butcher block countertop. White metro tile splashback in herringbone. Small herb pots on the windowsill...**
```

Bold part = only thing that changes per slide.

**Key tips:**
- Include "iPhone photo" and "realistic lighting" — makes images look like real phone photos
- "Before" rooms need to look modern but tired, not derelict
- Add signs of life: flat screen TV, mugs, remote control, everyday items
- Without everyday items, rooms look like empty show homes — nobody relates
- Portrait orientation: 1024x1536 (NOT 1536x1024 landscape — causes black bars)
- Don't add people — doesn't work

## Text Overlays

**Rules learned from failures:**
- Font size: 6.5% minimum (5% is unreadable)
- Position: NOT too high — hidden behind TikTok's status bar
- Line length: must fit max width or canvas rendering compresses text horizontally
- Test on phone before posting — desktop looks different

## The Hook Formula That Works

**WINNER formula:**
> [Another person] + [conflict or doubt] → showed them AI → they changed their mind

**Examples that hit:**
- "My landlord said I can't change anything so I showed her what AI thinks it could look like" → **234,000 views**
- "I showed my mum what AI thinks our living room could be" → **167,000 views**
- "My landlord wouldn't let me decorate until I showed her these" → **147,000 views**

Every post following this formula clears 50K minimum. Most clear 100K.

**What FAILED:**
- "Why does my flat look like a student loan" → 905 views
- "See your room in 12+ styles before you commit" → 879 views
- "The difference between $500 and $5000 taste" → 2,671 views

**Why failures failed:** Self-focused. Talking about the app's features. Nobody cares about YOUR problems.

**Why winners won:** Creates a tiny story in your head. You picture the other person's reaction. It's about the HUMAN MOMENT, not the app.

**Hook brainstorm rule:** "Who's the other person, and what's the conflict?" If there isn't one, the hook probably won't work.

## Posting Workflow

1. Larry generates images, adds text overlays, writes caption
2. Larry uploads to TikTok as draft via API (`privacy_level: "SELF_ONLY"`)
3. Larry sends caption to Oliver via message
4. Oliver opens TikTok, picks trending sound, pastes caption, publishes (~60 sec)
5. Runs on cron jobs at peak times

**Why drafts:** Music is everything on TikTok. Can't add music via API. Trending sounds change constantly. Human adds the finishing touch.

## Planning & Iteration

- Brainstorm 10-15 hooks at once, referencing performance data
- Pick best ones, tweak, lock in multi-day plan
- Pre-generate overnight using OpenAI Batch API (50% cheaper)
- Entire day's content ready by morning
- Track RevenueCat analytics to see if marketing converts to subscribers

## The Learning System

**Skill files** = the most important thing. Difference between useful and useless.

- Larry's TikTok skill file: 500+ lines
- Rewritten ~20 times in first week
- Every failure becomes a rule
- Every success becomes a formula
- It compounds — agent gets smarter with every post

**Memory files** = performance data that persists between sessions.
- Every post, view count, insight logged
- Hook brainstorming references actual data, not guessing

## Key Takeaways

1. Volume matters — 6 posts/day to find winners
2. Lock architecture in prompts, only change style
3. Hook formula: other person + conflict + showed them → reaction
4. Self-focused hooks die. Story hooks win.
5. Post as drafts, human adds music (60 sec)
6. Skill files are everything — obsessively specific, updated constantly
7. Failures are the curriculum — log every one
8. $0.50/post is nothing compared to manual content creation time
9. The agent is only as good as its memory
10. The system compounds — Larry is now better at creating viral TikToks than Oliver
