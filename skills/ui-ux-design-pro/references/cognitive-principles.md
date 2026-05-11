# Cognitive Principles

## Hick's Law

**Time to decide increases logarithmically with the number of choices.**

### Application

- Limit visible options to 5-7 per group
- Use progressive disclosure: show advanced options on demand
- Primary action should be visually dominant, reducing decision time
- Categorize long lists into groups
- Provide smart defaults so users rarely need to choose

### Interface Examples

- Settings: group by section, show 4-6 items per section
- Navigation: max 7 top-level items, nest others
- Form selects: group options, most common first
- Action menus: 5-7 items max, separator between groups

---

## Fitts's Law

**Time to reach a target depends on distance and size. Large, close targets are easiest to hit.**

### Application

- Primary actions should be large and close to the user's current focus
- Destructive actions should be smaller and farther from primary
- Navigation targets at screen edges are effectively infinite width (use it)
- Touch targets: 44px minimum (Apple), 48px (Material Design)

### Interface Examples

- Submit buttons: full-width on mobile, prominent size on desktop
- Cancel/Delete: smaller, secondary styling, farther from submit
- Toolbar actions: near the content they affect
- Mobile: primary CTA at thumb-reach bottom of screen

---

## Miller's Law

**Working memory holds 7 ± 2 items.**

### Application

- Chunk information into groups of 5-9 items
- Break long forms into multi-step flows (3-5 steps)
- Phone numbers: grouped as (123) 456-7890
- Credit cards: display as 4-digit groups
- Paginate large result sets: 10-25 items per page

### Interface Examples

- Dashboard: 3-4 metric cards per row
- Navigation: 5-7 primary items
- Data tables: group columns logically, hide non-essential
- Progress: show 3-5 steps, not 12

---

## Visual Hierarchy Patterns

### F-Pattern

**Desktop reading:** users scan horizontally across the top, then down the left side with shorter horizontal movements.

Apply to: dashboards, settings, data-heavy pages.

- Place key content in the top 20% of the page
- Left-align labels and primary information
- Use bold headings to create scan entry points

### Z-Pattern

**Landing / overview pages:** eyes move diagonally from top-left through center to bottom-right.

Apply to: overview screens, onboarding, summary pages.

- Logo / brand top-left
- Key action top-right
- Supporting content in center
- Primary CTA bottom-right

---

## Gestalt Principles

### Proximity

**Elements close together are perceived as related.**

- Group related form fields
- Separate unrelated sections with space, not borders
- Navigation items in the same group need consistent gaps
- Less space between label and its control, more space between field groups

```
[Label]        ← 4px gap
[Input Field]
               ← 16px gap
[Label]        ← 4px gap
[Input Field]
               ← 32px gap (section break)
[Label]        ← 4px gap
[Input Field]
```

### Similarity

**Elements that look alike are perceived as the same type.**

- All buttons of the same type look identical
- All cards at the same hierarchy level use the same style
- All status indicators use the same visual language
- Don't style different functions identically

### Common Region

**Elements within a shared boundary are perceived as grouped.**

- Cards group related content
- Backgrounds define sections
- Borders create visual containers
- Use backgrounds instead of borders when possible — softer grouping

### Closure

**The mind completes incomplete shapes.**

- Progress indicators suggest completion even when partial
- Partially visible content suggests scrollability
- Truncated text with "..." implies more content
- Partially visible cards at edges invite horizontal scroll

### Figure-Ground

**Users instinctively separate foreground from background.**

- Modals over dimmed backdrops
- Active elements over elevated surfaces
- Selected state over neutral background
- Dropdown menus floating above content

### Continuity

**The eye follows smooth paths and lines.**

- Align elements on clear grid lines
- Timeline components follow a vertical line
- Step indicators follow a horizontal line
- Table columns create vertical reading lines

### Common Fate

**Elements moving together are perceived as a group.**

- Items that animate together belong together
- Drag a card and its children move with it
- Collapse a section and all its children disappear
- Scroll content together within a same scroll container

---

## Progressive Disclosure

**Show only what's needed at each moment. Reveal complexity on demand.**

### Levels

1. **Essential:** always visible (primary actions, key data, navigation)
2. **Optional:** one interaction away (settings, filters, advanced options)
3. **Specialist:** behind explicit request (admin tools, debug info, raw data)

### Patterns

- Accordion: expand sections as needed
- "Show more" / "Advanced" toggles
- Tooltips for supplementary info
- Modal for complex actions
- Drawer for secondary workflows
- Inline expansion for detail rows

---

## Von Restorff Effect

**Distinct elements are better remembered than common ones.**

### Application

- Make the primary CTA visually distinct (color, size, weight)
- Important notifications use color + icon, not just text
- Key metrics larger than supporting data
- Active navigation item must stand out from siblings
- Use one accent color — multiple dilutes the effect

---

## Cognitive Load Theory

### Types of Load

**Intrinsic:** complexity inherent in the task (can't reduce).
**Extraneous:** complexity from poor design (must reduce).
**Germane:** effort spent understanding and learning (should support).

### Reduction Strategies

- Remove visual clutter that doesn't serve function
- Consistent patterns reduce learning curve
- Familiar icons and interactions reduce recall demand
- Whitespace reduces processing effort
- Progressive disclosure hides complexity until needed
- Default values reduce decision fatigue
- Smart sorting (most recent, most used) reduces search effort
