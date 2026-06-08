# Outline Template

## Standard Outline Format

```yaml
---
strategy: a  # a, b, or c
name: [Strategy Name]
style: [style name]
style_reason: "[Why this style fits the product]"
scene: [scene type]
platform: [platform name]
image_count: [number]
elements:
  background: [background type]
  decorations: [decoration elements]
  emphasis: [emphasis style]
  typography: [text style]
---
```

## Image Types

### Hero

**Purpose**: Main product image, first impression

```markdown
## P1 Hero
**Type**: hero
**Purpose**: [Main impression to create]
**Visual**: [Description of composition]
**Layout**: [studio/lifestyle/contextual]
**Platform**: [Platform compliance notes]
```

### Angle

**Purpose**: Show product from different perspective

```markdown
## P2 Angle
**Type**: angle
**Purpose**: [What this angle shows]
**Visual**: [45-degree, side, top, etc.]
**Visual**: [Key features visible from this angle]
```

### Detail

**Purpose**: Highlight quality, features, materials

```markdown
## P3 Detail
**Type**: detail
**Purpose**: [Feature or quality to highlight]
**Visual**: [Macro/close-up description]
**Focus**: [Specific area of attention]
```

### Lifestyle

**Purpose**: Show product in use, create emotional connection

```markdown
## P4 Lifestyle
**Type**: lifestyle
**Purpose**: [Emotional benefit or use case]
**Setting**: [Environment description]
**Action**: [How product is being used]
```

### Infographic

**Purpose**: Communicate features, specs, benefits with text

```markdown
## P5 Infographic
**Type**: infographic
**Purpose**: [Information to convey]
**Callouts**: [Key points to highlight]
**Layout**: [How information is organized]
```

### Comparison

**Purpose**: Show before/after or vs alternatives

```markdown
## P6 Comparison
**Type**: comparison
**Purpose**: [What is being compared]
**Layout**: [Split, side-by-side, etc.]
**Message**: [Key takeaway]
```

### Exploded

**Purpose**: Show components, assembly, internal features

```markdown
## P7 Exploded
**Type**: exploded
**Purpose**: [What the exploded view shows]
**Components**: [Parts to highlight]
**Arrangement**: [How components are displayed]
```

### Ending

**Purpose**: Call to action, packaging, what's included

```markdown
## P8 Ending
**Type**: ending
**Purpose**: [Final impression or CTA]
**Visual**: [Packaging, bundle, etc.]
**Message**: [Final takeaway]
```

## Strategy Templates

### Strategy A: Product-Focused

```yaml
---
strategy: a
name: Product-Focused
style: minimal
scene: studio
image_count: 5
---

## P1 Hero
**Type**: hero
**Purpose**: Clean main product image
**Visual**: Product on pure white background
**Layout**: studio

## P2 Angle
**Type**: angle
**Purpose**: Show product from 45-degree angle
**Visual**: Three-quarter view with depth
**Layout**: studio

## P3 Detail
**Type**: detail
**Purpose**: Highlight [key feature]
**Visual**: Close-up of [specific area]
**Layout**: studio

## P4 Detail
**Type**: detail
**Purpose**: Show [another feature]
**Visual**: Close-up of [specific area]
**Layout**: studio

## P5 Infographic
**Type**: infographic
**Purpose**: Summarize key features
**Callouts**: [Feature 1, 2, 3]
**Layout**: clean-infographic
```

### Strategy B: Lifestyle-Focused

```yaml
---
strategy: b
name: Lifestyle-Focused
style: lifestyle
scene: lifestyle
image_count: 5
---

## P1 Hero
**Type**: hero
**Purpose**: Product in aspirational setting
**Visual**: [Setting] with product as hero
**Layout**: lifestyle

## P2 Lifestyle
**Type**: lifestyle
**Purpose**: Show product in natural use
**Setting**: [Environment]
**Action**: [Usage scenario]

## P3 Contextual
**Type**: contextual
**Purpose**: Product in complementary setting
**Visual**: [Description]
**Layout**: contextual

## P4 Detail
**Type**: detail
**Purpose**: Quality close-up
**Visual**: Macro of [material/feature]
**Layout**: studio

## P5 Ending
**Type**: ending
**Purpose**: Call to action
**Visual**: Lifestyle hero with product
**Layout**: lifestyle
```

### Strategy C: Information-Focused

```yaml
---
strategy: c
name: Information-Focused
style: bold
scene: infographic
image_count: 5
---

## P1 Hero
**Type**: hero
**Purpose**: Product with key benefit headline
**Visual**: Clean product + headline
**Layout**: studio-infographic

## P2 Infographic
**Type**: infographic
**Purpose**: Feature breakdown
**Callouts**: [Features 1-4]
**Layout**: grid-infographic

## P3 Infographic
**Type**: infographic
**Purpose**: Specifications
**Details**: [Specs to highlight]
**Layout**: list-infographic

## P4 Comparison
**Type**: comparison
**Purpose**: Before/after or vs alternatives
**Layout**: split-comparison
**Message**: [Key benefit]

## P5 Ending
**Type**: ending
**Purpose**: Summary + CTA
**Visual**: Product hero + benefits
**Layout**: sparse-infographic
```

## Layout Guide

| Layout Type | Description | Best For |
|-------------|-------------|----------|
| sparse | Minimal elements, maximum impact | Hero, ending |
| balanced | Standard product presentation | Angles, details |
| dense | High information density | Infographics |
| list | Enumeration format | Features, specs |
| comparison | Side-by-side layout | Before/after |
| grid | Organized sections | Multiple features |
| flow | Sequential layout | Process, steps |
