# UI De-AI Aesthetic Checklist

Reduce AI-generated look in Phase 2b (Design Preview) and Phase 3 (Generate). All rules yield to explicit brand guidelines when they exist.

## Color

| Avoid | Prefer |
|-------|--------|
| Blue-purple gradients, neon glows, aurora backgrounds | Intentional, limited palette tied to brand or domain — vibrant (Figma), monochrome (Vercel), or warm (Notion) are all fine. The key: every color has a reason. |
| Excessive gradient layering | Flat or subtle single-hue gradients (< 10% lightness delta) |
| High-contrast neon accents (#00FFxx, #FF00xx) | Muted accent colors drawn from the brand or domain |

Pick 1 primary + 1 accent + 2–3 neutrals + 4 semantic colors (success/error/warning/info — don't count toward the palette limit).

## Layout

| Avoid | Prefer |
|-------|--------|
| Hero banner + 3-column card grid | Asymmetric splits, left-heavy layouts, varied section structures |
| Giant rounded-corner cards (border-radius ≥ 20px) everywhere | Moderate rounding (4–12px) or mix rounded + sharp edges |
| Full-screen glow / blur overlays | Subtle shadows, thin borders, or whitespace for separation |

No two consecutive sections should share the same grid structure.

## Typography & Spacing

| Avoid | Prefer |
|-------|--------|
| Oversized hero headings (> 4rem) with gradient text | Standard hierarchy (h1 2–3rem, h2 1.5–2rem) |
| Arbitrary spacing (padding: 17px, margin: 23px) | 4px-base scale: 4, 8, 12, 16, 24, 32, 48, 64px |
| Excessive whitespace (> 120px section gaps) | Compact spacing (40–80px section gaps) |
| Center-aligned body text | Left-aligned body text |

## Icons & Copy

| Avoid | Prefer |
|-------|--------|
| Emoji as UI elements, robot/brain/sparkle icons | Unified icon set (Lucide, Heroicons, Phosphor) |
| AI-themed imagery (neural networks, glowing brains) | Task-oriented visuals showing the product in use |
| "Intelligent", "AI-powered", "empower", "unleash" | Task-oriented: "Track orders", "Review pull requests" |
| "Magic" / "one-click" verbs | Precise verbs: "Generate report", "Compare versions" |

## Interaction

| Avoid | Prefer |
|-------|--------|
| Chat-bubble UI as primary interface | Structured panels, tables, forms, dashboards |
| Sparkle animations, glowing loading orbs | Skeleton screens, progress bars, subtle spinners |
| Hidden process — input in, result out | Visible process — steps, previews, editable states |
| Bare "No data" blank page | Empty state with illustration + guidance + CTA |

## Quick Checklist

- [ ] No blue-purple gradient (unless brand-mandated)
- [ ] No hero + 3-column-card layout
- [ ] At least 2 different section structures on the page
- [ ] Icons from a single consistent set, not emoji
- [ ] Copy describes tasks/scenarios, not AI capabilities
- [ ] Primary interaction is structured, not chat
- [ ] Spacing uses 4px-base scale, no arbitrary values
- [ ] Loading states use skeleton or progress bar
- [ ] Empty/error states have illustration + guidance + action
