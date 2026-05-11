# SaaS & Landing Page Reference

B2B product pages, startup homepages, developer tools, pricing pages, feature showcases.

> **Design system references for this domain:**
> - `design-system/typography.md` — hero type scales, code font pairing for developer tools
> - `design-system/color-and-contrast.md` — brand palette construction, dark/light mode theming
> - `design-system/spatial-design.md` — landing page rhythm, feature grid patterns
> - `design-system/motion-design.md` — scroll-triggered reveals, hero animations
> - `design-system/ux-writing.md` — CTA copy, value proposition clarity

## Table of Contents
1. Starter Prompts
2. Color Palettes
3. Typography Pairings
4. Layout Patterns
5. Signature Details
6. Real Community Examples

---

## 1. Starter Prompts

**AI / Data Products**
- "Landing page for an AI data platform: 'Mosaic builds datasets for humans and agents' — hero statement, feature grid (competitive intelligence / trend signals / MCP API access), social proof stats (2.4B+ daily, 14K+ sources), CTA."
- "Homepage for an AI agent marketplace: what agents can do, how to deploy, pricing tiers, featured agents."
- "Product page for a vector database: benchmark chart vs. competitors, code snippet showing simple API, enterprise logos, latency guarantee."

**Infrastructure / DevOps**
- "Landing page for a cloud compute product: 'Structural Efficiency.' — dark hero, three-column feature cards (Fluid Instance / Synthetic Ri / Geo-Cluster), architecture diagram, get-started CTA."
- "Developer tools homepage: code-first hero with syntax-highlighted snippet, feature icons, changelog feed, GitHub star count badge."
- "Serverless functions product: cold start comparison chart, supported runtimes grid, pricing calculator, migration guide CTA."

**Productivity / Workspace**
- "Workspace tool landing page: command palette demo, integrations grid, team collaboration screenshot, 'Works where you work' section."
- "Project management SaaS: before/after comparison, drag-and-drop demo GIF placeholder, team testimonials, pricing comparison table."

**Fintech / Security**
- "Payments API product page: single integration code snippet, supported payment methods logos, transaction speed badge, compliance certifications."
- "Security/compliance SaaS: threat detection stats, SOC2/ISO badges, incident response timeline demo, enterprise trust logos."

---

## 2. Color Palettes

### Dark Indigo (modern SaaS)
```
--bg:        #0F172A
--surface:   #1E293B
--card:      #1E293B
--border:    #334155
--text:      #F1F5F9
--muted:     #94A3B8
--accent:    #6366F1   /* indigo */
--accent-2:  #38BDF8   /* sky */
--cta:       #6366F1
```

### Minimal Light (clean/enterprise)
```
--bg:        #FFFFFF
--surface:   #F8FAFC
--card:      #FFFFFF
--border:    #E2E8F0
--text:      #0F172A
--muted:     #64748B
--accent:    #0EA5E9   /* sky blue */
--cta:       #0F172A
```

### Structural Black (infra/engineering)
```
--bg:        #111111
--surface:   #1A1A1A
--card:      #222222
--border:    #333333
--text:      #FFFFFF
--muted:     #888888
--accent:    #FF6B35   /* orange */
--accent-2:  #FFFFFF
```

### Warm Startup (consumer SaaS)
```
--bg:        #FAFAF9
--surface:   #F5F5F4
--card:      #FFFFFF
--border:    #E7E5E4
--text:      #1C1917
--muted:     #78716C
--accent:    #EA580C   /* orange */
--cta:       #EA580C
```

### Deep Purple (AI/ML)
```
--bg:        #09090B
--surface:   #18181B
--card:      #27272A
--border:    #3F3F46
--text:      #FAFAFA
--muted:     #A1A1AA
--accent:    #A855F7   /* purple */
--accent-2:  #EC4899
```

---

## 3. Typography Pairings

| Display | Body | Character |
|---|---|---|
| `Syne` | `Plus Jakarta Sans` | Modern, geometric, startup |
| `Cabinet Grotesk` | `Satoshi` | Friendly, contemporary |
| `Clash Display` | `General Sans` | Bold, product-forward |
| `Bebas Neue` | `DM Sans` | Strong, direct |
| `Bricolage Grotesque` | `Outfit` | Quirky, memorable |
| `Neue Haas Grotesk` alt: `Geist` | `Geist` | Developer-grade, clean |

---

## 4. Layout Patterns

### Pattern A: Hero + Feature Grid (standard)
```
┌──────────────────────────────────────────┐
│  NAV: Logo   Features  Pricing  Docs  CTA│
├──────────────────────────────────────────┤
│                                          │
│  [Overline: "Introducing..."]            │
│  BIG HERO HEADLINE                       │
│  Subheadline in muted, 1-2 lines         │
│  [Primary CTA]  [Secondary CTA]          │
│                                          │
│  ┌──────────────────────────────────┐    │
│  │  Hero image / demo / code block  │    │
│  └──────────────────────────────────┘    │
├──────────────────────────────────────────┤
│  Stat  │  Stat  │  Stat  │  Stat        │
├──────────────────────────────────────────┤
│  Feature   │  Feature   │  Feature      │
│  ────────  │  ────────  │  ────────     │
│  Icon+title│  Icon+title│  Icon+title   │
│  Desc text │  Desc text │  Desc text    │
└──────────────────────────────────────────┘
```

### Pattern B: Split Hero (product screenshot)
```
┌──────────────────┬───────────────────────┐
│                  │                       │
│  Headline        │   [Product screenshot │
│  Subhead         │    or demo UI]        │
│  [CTA]           │                       │
│                  │                       │
└──────────────────┴───────────────────────┘
```

### Pattern C: Code-First (developer tools)
```
┌──────────────────────────────────────────┐
│  Small label: "Simple to integrate"      │
│  Bold headline                           │
├───────────────────────┬──────────────────┤
│  npm install xyz      │  Features list   │
│  ─────────────────    │  ✓ Feature one   │
│  const client = ...   │  ✓ Feature two   │
│  const result = ...   │  ✓ Feature three │
│  console.log(result)  │                  │
└───────────────────────┴──────────────────┘
```

### Pattern D: Dark Hero + 3-Column Cards (infrastructure)
```
┌──────────────────────────────────────────┐
│  [DARK BACKGROUND]                       │
│  "Structural Efficiency."                │
│  One-line subhead                        │
│  [CTA button]                            │
├──────────┬───────────┬───────────────────┤
│ Card 1   │  Card 2   │  Card 3           │
│ ───────  │  ───────  │  ───────          │
│ Title    │  Title    │  Title            │
│ Desc     │  Desc     │  Desc             │
└──────────┴───────────┴───────────────────┘
```

---

## 5. Signature Details

- **Stat badges**: "2.4B+ daily" / "14K+ sources" in large number + small label
- **Logos strip**: "Trusted by" + muted grayscale company logos
- **Code snippet hero**: syntax-highlighted, dark bg, copy button
- **Feature icon**: simple 24px icon + bold title + 2-line description
- **CTA hierarchy**: primary (filled, accent) + secondary (outline or text)
- **Changelog/release notes**: version badge + date + 2-line summary
- **Pricing toggle**: monthly/annual with annual savings badge
- **Integration logos**: grid of logos with hover tooltips
- **Trust badges**: SOC2 / GDPR / ISO 27001 inline near CTA

---

## 6. Real Variant Community Examples

**Mosaic (AI data product)**:
- White/light background, clean layout
- Hero: "Mosaic builds high-fidelity datasets for the people and systems that run modern marketing"
- Feature list: competitive intelligence / trend signals & benchmarks / distributed + export / MCP API access / clean schema, zero hallucination
- Stats: 2.4B+ (large), 14K+ (large)
- Subtle grid/table showing dataset preview
- "Mosaic Ads" sub-product callout at bottom

**Structural Efficiency (cloud infra)**:
- Dark `#111111` background
- "Structural Efficiency." in large bold sans
- Subtext: "REDUCTION AI DEPLOYS THREE CORE ARCHITECTURAL MODELS OPTIMIZED FOR LIQUIDITY, WELL-SPACE, AND MAXIMUM CAPITAL CAPTURE ACROSS CLOUD INFRASTRUCTURE."
- Three cards: Fluid Instance / Synthetic Ri / Geo-Cluster
- Each card: bold name + description paragraph
