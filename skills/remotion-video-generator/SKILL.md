---
name: remotion-video-generator
description: AI video production workflow using Remotion. Use when creating videos, short films, commercials, or motion graphics. Triggers on requests to make promotional videos, product demos, social media videos, animated explainers, or any programmatic video content. Produces polished motion graphics, not slideshows.
version: "1.0.0"
metadata: {"openclaw":{"emoji":"🎬","requires":{"bins":["node","npm","python3"]}, "tags":["video", "remotion", "motion-graphics", "production"]}}
---

# Remotion Video Generator

> "Create professional motion graphics videos programmatically with React and Remotion."

---

## Credits & References

### Original Skill
- **Source:** [Superskills - Video Generator (Remotion)](https://superskills.vibecode.run/)
- **Author:** Riley Brown / VibeCode Community

### Modifications
- **Firecrawl replaced with Scrapling** for brand data extraction
- Uses Python `scrapling` library instead of Firecrawl API
- Added comprehensive troubleshooting for Remotion v4 API

### Core Technologies
- **Remotion:** https://www.remotion.dev/
- **Scrapling:** https://github.com/D4Vinci/Scrapling
- **React:** https://react.dev/

### Tested With
- OpenClaw promotional video - successfully rendered! 🎉

---

## Quick Usage Guide (Step-by-Step)

### Step 1: Scrape Brand Data
```bash
# Run the scrapling script to get brand colors, logo, tagline
bash skills/remotion-video-generator/scripts/scrapling.sh "https://brand-website.com"
```

This extracts: brandName, tagline, logoUrl, faviconUrl, primaryColors, ogImageUrl, screenshotUrl

### Step 2: Download Brand Assets
```bash
mkdir -p public/images/brand
curl -sL "https://brand.com/logo.svg" -o public/images/brand/logo.svg
curl -sL "https://brand.com/og-image.png" -o public/images/brand/og-image.png
curl -sL "https://image.thum.io/get/width/1200/crop/800/https://brand.com" -o screenshot.png
```

### Step 3: Create Project Structure
```bash
mkdir -p my-video/src my-video/public/images/brand my-video/public/audio
```

### Step 4: Create package.json
```json
{
  "name": "my-video",
  "scripts": {
    "dev": "npx remotion studio",
    "build": "npx remotion bundle"
  },
  "dependencies": {
    "@remotion/cli": "^4.0.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "remotion": "^4.0.0",
    "lucide-react": "^0.300.0"
  }
}
```

### Step 5: Install Dependencies
```bash
cd my-video && npm install
```

### Step 6: Create Video Component
Create `src/MyVideo.tsx` with:
- AbsoluteFill for full-screen layout
- Sequence components for scene timing
- useCurrentFrame, useVideoConfig, interpolate, spring for animations

### Step 7: Create Entry Point (Remotion v4 API)
Create `src/index.tsx` - **MUST use `.tsx` extension**:

```tsx
import { registerRoot, Composition } from "remotion";
import { AbsoluteFill, Sequence, useCurrentFrame, useVideoConfig, interpolate, spring } from "remotion";

const MyVideo = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Animations - ALWAYS pass fps to spring()
  const scale = spring({ frame, fps, from: 0.8, to: 1 });

  return (
    <AbsoluteFill style={{ backgroundColor: "#000" }}>
      <Sequence from={0} durationInFrames={90}>
        <h1>Hello World</h1>
      </Sequence>
    </AbsoluteFill>
  );
};

registerRoot(() => {
  return (
    <Composition
      id="MyVideo"
      component={MyVideo}
      durationInFrames={240}
      fps={30}
      width={1920}
      height={1080}
    />
  );
});
```

**⚠️ CRITICAL Remotion v4 Rules:**
1. Use `.tsx` extension (NOT `.ts`) for files with JSX
2. MUST use `registerRoot` + `Composition` API
3. ALWAYS pass `fps` to `spring()`: `spring({ frame, fps, from: 0.8, to: 1 })`
4. Use `useVideoConfig()` to get fps: `const { fps } = useVideoConfig()`
5. Render with composition name: `npx remotion render MyVideo out/video.mp4`

### Step 8: Start Dev Server
```bash
cd my-video && npm run dev
```
Server runs on http://localhost:3000

### Step 9: Preview & Iterate
- Open browser to preview
- Edit source files - hot-reloads automatically
- User reviews and requests changes

### Step 10: Render Final Video (when user asks)
```bash
npx remotion render index out/final-video.mp4
```

---

## Credits

- **Original Skill:** https://superskills.vibecode.run/
- **Modified:** Firecrawl replaced with Scrapling for brand data extraction
- **Remotion:** https://www.remotion.dev/

---

## Installation

```bash
# Install Remotion globally
npm install -g remotion

# Install dependencies for video projects
npm install lucide-react

# Install Scrapling (already in workspace skills)
pip install scrapling
```

---

## Agent Instructions

### When to Use Video Generator

**Use this skill when:**
- Creating promotional videos
- Making product demos
- Social media video content
- Animated explainers
- Commercials
- Any programmatic video content

**Do NOT use for:**
- Simple slideshows (use other tools)
- Video editing of existing footage
- Live streaming

---

## Default Workflow (ALWAYS follow this)

1. **Scrape brand data** (if featuring a product) using **Scrapling** (NOT Firecrawl)
2. **Create the project** in `output/<project-name>/`
3. **Build all scenes** with proper motion graphics
4. **Install dependencies** with `npm install`
5. **Fix package.json scripts** to use `npx remotion` (not bun):
   ```json
   "scripts": {
     "dev": "npx remotion studio",
     "build": "npx remotion bundle"
   }
   ```
6. **Start Remotion Studio** as a background process:
   ```bash
   cd output/<project-name> && npm run dev
   ```
7. **Expose via Cloudflare tunnel** so user can access:
   ```bash
   bash skills/cloudflare-tunnel/scripts/tunnel.sh start 3000
   ```
8. **Send the user the public URL** (e.g. `https://xxx.trycloudflare.com`)

The user will preview in their browser, request changes, and you edit the source files. Remotion hot-reloads automatically.

---

## Rendering (only when user explicitly asks to export)

```bash
cd output/<project-name>
npx remotion render CompositionName out/video.mp4
```

---

## Quick Start

```bash
# Scaffold project
cd output && npx --yes create-video@latest my-video --template blank
cd my-video && npm install

# Add motion libraries
npm install lucide-react

# Fix scripts in package.json (replace any "bun" references with "npx remotion")

# Start dev server
npm run dev

# Expose publicly
bash skills/cloudflare-tunnel/scripts/tunnel.sh start 3000
```

---

## Fetching Brand Data with Scrapling

**MANDATORY:** When a video mentions or features any product/company, use Scrapling to scrape the product's website for brand data, colors, screenshots, and copy BEFORE designing the video. This ensures visual accuracy and brand consistency.

### Using the Scrapling Script

```bash
# Run the brand data extraction script
bash skills/remotion-video-generator/scripts/scrapling.sh "https://example.com"
```

This returns structured brand data: brandName, tagline, headline, description, features, logoUrl, faviconUrl, primaryColors, ctaText, socialLinks, plus screenshot URL and OG image URL.

### Manual Scrapling Extraction

If the script isn't available, use Python directly:

```python
import json
from scrapling.fetchers import StealthyFetcher
from urllib.parse import urljoin
import re

url = 'https://brand.com'
page = StealthyFetcher.fetch(url, headless=True)
html = page.text

def resolve(u):
    return urljoin(url, u) if u and not u.startswith('http') else u

colors = list(set(re.findall(r'#(?:[0-9a-fA-F]{3}){1,2}', html)))[:5]

data = {
    'brandName': page.css('[property="og:site_name"]::text').get() or page.title(),
    'tagline': page.css('[property="og:description"]::text').get(),
    'headline': page.css('h1::text').get(),
    'description': page.css('[property="og:description"]::text').get(),
    'logoUrl': resolve(page.css('[rel="icon"]::attr(href)').get()),
    'faviconUrl': resolve(page.css('[rel="icon"]::attr(href)').get()),
    'primaryColors': colors,
    'ctaText': page.css('a[href*="signup"]::text').get(),
    'ogImageUrl': resolve(page.css('[property="og:image"]::attr(content)').get()),
    'screenshotUrl': f"https://image.thum.io/get/width/1200/crop/800/{url}"
}

print(json.dumps(data, indent=2))
```

---

## Download Assets After Scraping

```bash
mkdir -p public/images/brand
curl -s "https://example.com/favicon.ico" -o public/images/brand/favicon.ico
curl -s "${OG_IMAGE_URL}" -o public/images/brand/og-image.png
curl -sL "${SCREENSHOT_URL}" -o public/images/brand/screenshot.png
```

**Note:** Some S3 buckets block direct access. Use thum.io screenshot service as fallback.

---

## Core Architecture

### Scene Management

Use scene-based architecture with proper transitions:

```typescript
const SCENE_DURATIONS: Record<string, number> = {
  intro: 3000,      // 3s hook
  problem: 4000,    // 4s dramatic
  solution: 3500,   // 3.5s reveal
  features: 5000,  // 5s showcase
  cta: 3000,        // 3s close
};
```

### Video Structure Pattern

```typescript
import { AbsoluteFill, Sequence, useCurrentFrame, useVideoConfig, interpolate, spring, Img, staticFile, Audio } from "remotion";

export const MyVideo = () => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  return (
    <AbsoluteFill>
      {/* Background music */}
      <Audio src={staticFile("audio/bg-music.mp3")} volume={0.35} />

      {/* Persistent background layer - OUTSIDE sequences */}
      <AnimatedBackground frame={frame} />

      {/* Scene sequences */}
      <Sequence from={0} durationInFrames={90}>
        <IntroScene />
      </Sequence>
      <Sequence from={90} durationInFrames={120}>
        <FeatureScene />
      </Sequence>
    </AbsoluteFill>
  );
};
```

---

## Motion Graphics Principles

### AVOID (Slideshow patterns)

- Fading to black between scenes
- Centered text on solid backgrounds
- Same transition for everything
- Linear/robotic animations
- Static screens
- Emoji icons — NEVER use emoji, always use Lucide React icons

### PURSUE (Motion graphics)

- Overlapping transitions (next starts BEFORE current ends)
- Layered compositions (background/midground/foreground)
- Spring physics for organic motion
- Varied timing (2-5s scenes, mixed rhythms)
- Continuous visual elements across scenes
- Custom transitions with clipPath, 3D transforms, morphs
- Lucide React for ALL icons (`npm install lucide-react`) — never emoji

---

## Transition Techniques

| Technique | Description |
|-----------|-------------|
| **Morph/Scale** | Element scales up to fill screen, becomes next scene's background |
| **Wipe** | Colored shape sweeps across, revealing next scene |
| **Zoom-through** | Camera pushes into element, emerges into new scene |
| **Clip-path reveal** | Circle/polygon grows from point to reveal |
| **Persistent anchor** | One element stays while surroundings change |
| **Directional flow** | Scene 1 exits right, Scene 2 enters from right |
| **Split/unfold** | Screen divides, panels slide apart |
| **Perspective flip** | Scene rotates on Y-axis in 3D |

---

## Animation Timing Reference

```typescript
// Timing values (in seconds)
const timing = {
  micro: 0.1-0.2,     // Small shifts, subtle feedback
  snappy: 0.2-0.4,    // Element entrances, position changes
  standard: 0.5-0.8,   // Scene transitions, major reveals
  dramatic: 1.0-1.5,  // Hero moments, cinematic reveals
};

// Spring configs
const springs = {
  snappy: { stiffness: 400, damping: 30 },
  bouncy: { stiffness: 300, damping: 15 },
  smooth: { stiffness: 120, damping: 25 },
};
```

---

## Visual Style Guidelines

### Typography

- One display font + one body font max
- Massive headlines, tight tracking
- Mix weights for hierarchy
- Keep text SHORT (viewers can't pause)

### Colors

- **Use brand colors from Scrapling scrape** as the primary palette — match the product's actual look
- Avoid purple/indigo gradients unless the brand uses them or the user explicitly requests them
- Simple, clean backgrounds are generally best — a single dark tone or subtle gradient beats layered textures
- Intentional accent colors pulled from the brand

### Layout

- Use asymmetric layouts, off-center type
- Edge-aligned elements create visual tension
- Generous whitespace as design element
- Use depth sparingly — a subtle backdrop blur or single gradient, not stacked textures

---

## Remotion Essentials

### Interpolation

```typescript
const opacity = interpolate(frame, [0, 30], [0, 1], {
  extrapolateLeft: "clamp",
  extrapolateRight: "clamp"
});

const scale = spring({
  frame,
  fps,
  from: 0.8,
  to: 1,
  durationInFrames: 30,
  config: { damping: 12 }
});
```

### Sequences with Overlap

```tsx
<Sequence from={0} durationInFrames={100}>
  <Scene1 />
</Sequence>
<Sequence from={80} durationInFrames={100}>
  <Scene2 />
</Sequence>
```

### Cross-Scene Continuity

Place persistent elements OUTSIDE Sequence blocks:

```tsx
const PersistentShape = ({ currentScene }: { currentScene: number }) => {
  const positions = {
    0: { x: 100, y: 100, scale: 1, opacity: 0.3 },
    1: { x: 800, y: 200, scale: 2, opacity: 0.5 },
    2: { x: 400, y: 600, scale: 0.5, opacity: 1 },
  };

  return (
    <motion.div
      animate={positions[currentScene]}
      transition={{ duration: 0.8, ease: "easeInOut" }}
      className="absolute w-32 h-32 rounded-full bg-gradient-to-r from-coral to-orange"
    />
  );
};
```

---

## Quality Tests

Before delivering, verify:

- **Mute test:** Story follows visually without sound?
- **Squint test:** Hierarchy visible when squinting?
- **Timing test:** Motion feels natural, not robotic?
- **Consistency test:** Similar elements behave similarly?
- **Slideshow test:** Does NOT look like PowerPoint?
- **Loop test:** Video loops smoothly back to start?

---

## Implementation Steps

1. **Scrapling brand scrape** — If featuring a product, scrape its site first
2. **Director's treatment** — Write vibe, camera style, emotional arc
3. **Visual direction** — Colors, fonts, brand feel, animation style
4. **Scene breakdown** — List every scene with description, duration, text, transitions
5. **Plan assets** — User assets + generated images/videos + brand scrape assets
6. **Define durations** — Vary pacing (2-3s punchy, 4-5s dramatic)
7. **Build persistent layer** — Animated background outside scenes
8. **Build scenes** — Each with enter/exit animations, 3-5 timed moments
9. **Open with hook** — High-impact first scene
10. **Develop narrative** — Content-driven middle scenes
11. **Strong ending** — Intentional, resolved close
12. **Start Remotion Studio** — `npm run dev` on port 3000
13. **Expose via tunnel** — `bash skills/cloudflare-tunnel/scripts/tunnel.sh start 3000`
14. **Send user the public URL** — They preview and request changes live
15. **Iterate** — Edit source, hot-reload, repeat
16. **Render** — Only when user says to export final video

---

## File Structure

```
my-video/
├── src/
│   ├── Root.tsx          # Composition definitions
│   ├── index.ts          # Entry point
│   ├── index.css         # Global styles
│   ├── MyVideo.tsx       # Main video component
│   └── scenes/           # Scene components (optional)
├── public/
│   ├── images/
│   │   └── brand/        # Scrapling-scraped assets
│   └── audio/            # Background music
├── remotion.config.ts
└── package.json
```

---

## Common Components

See `references/components.md` for reusable:
- Animated backgrounds
- Terminal windows
- Feature cards
- Stats displays
- CTA buttons
- Text reveal animations

---

## Tunnel Management

```bash
# Start tunnel (exposes port 3000 publicly)
bash skills/cloudflare-tunnel/scripts/tunnel.sh start 3000

# Check status
bash skills/cloudflare-tunnel/scripts/tunnel.sh status 3000

# List all tunnels
bash skills/cloudflare-tunnel/scripts/tunnel.sh list

# Stop tunnel
bash skills/cloudflare-tunnel/scripts/tunnel.sh stop 3000
```

---

## Troubleshooting

### Common Issues & Fixes

| Issue | Solution |
|-------|----------|
| `Expected ">" but found "schema"` | Use `.tsx` extension for files with JSX, not `.ts` |
| `useCurrentFrame() can only be called inside a component` | Use `registerRoot` + `Composition` API (see Step 7) |
| `"fps" must be a number, but you passed undefined to spring()` | Pass `fps` to spring: `spring({ frame, fps, from: 0.8, to: 1 })` |
| `Could not find composition with ID index` | Use composition name: `npx remotion render MyVideo out.mp4` |
| `Module build failed` | Ensure `react` and `react-dom` are in dependencies |
| Remotion not found | Run `npm install` in project directory |
| Hot reload not working | Ensure running `npm run dev`, not `npx remotion` directly |
| Brand colors not extracting | Some sites use CSS variables - check page source manually |

### File Extension Rules
- Use `.tsx` for files with JSX (components with `< tags >`)
- Use `.ts` for pure TypeScript files
- Entry point MUST be `.tsx` if it uses JSX

### Testing Your Video
1. Start dev server: `npm run dev`
2. Open http://localhost:3000
3. Make changes - auto-refreshes
4. Check composition in browser

---

## Changelog

### v1.0.0 (2026-02-25)
- Initial release (adapted from superskills)
- **Firecrawl replaced with Scrapling** for brand data extraction
- Uses StealthyFetcher for JS-heavy sites
- Full brand data extraction: brandName, tagline, headline, description, features, logoUrl, faviconUrl, primaryColors, ctaText, socialLinks, screenshotUrl, ogImageUrl

### v1.1.0 (2026-02-25)
- Added Quick Usage Guide with step-by-step instructions
- Added troubleshooting section for common issues
- Tested with OpenClaw promotional video - working! 🎉
- Documented file extension requirements (.tsx vs .ts)
- Fixed Remotion v4 API: `registerRoot` + `Composition` pattern
- Fixed spring() must receive `fps` parameter
- Fixed composition name in render command

---

## Practical Example: OpenClaw Promo Video

Here's the actual project created during testing:

**Location:** `skills/remotion-video-generator/openclaw-promo/`

**Brand Data Extracted:**
- Tagline: "The AI that actually does things."
- Logo: favicon.svg from openclaw.ai
- Primary Color: #FF6B35 (extracted from design)
- Screenshot: Generated via thum.io

**Project Structure:**
```
openclaw-promo/
├── src/
│   ├── index.tsx        # Entry point
│   └── OpenClawPromo.tsx # Video component
├── public/
│   └── images/
│       └── brand/
│           ├── logo.svg
│           ├── og-image.png
│           └── screenshot.png
├── package.json
└── tsconfig.json
```

**Commands:**
```bash
cd skills/remotion-video-generator/openclaw-promo
npm run dev    # Start studio at localhost:3000
npm run build  # Bundle for production
```

---

*Last updated: 2026-02-25*
