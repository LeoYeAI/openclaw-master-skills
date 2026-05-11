# Platform Conventions — Designer's Eye Reference

## Table of Contents
1. Web/Desktop Applications
2. Mobile (iOS/Android)
3. Social Media Posts
4. Email
5. Dark Mode
6. Accessibility Across Platforms
7. Design System Consistency

---

Design conventions are powerful because users have years of learned patterns. Violate them intentionally for a reason; don't break them by accident.

---

## Web/Desktop Applications

### Layout & Navigation
- **Top navigation:** Primary nav in header, persistent
- **Sidebar:** Secondary nav or filters, collapsible on mobile
- **Footer:** Links, copyright, always visible or sticky
- **Breadcrumbs:** Show hierarchy, allow backtracking; optional on flat sites
- **Search:** Header placement, always accessible

**What to look for:**
- Navigation that moves between pages (confuses users)
- Primary nav hidden on desktop (forces exploration)
- Breadcrumb at bottom of page (place at top)
- Footer that scrolls away on mobile (should be sticky or float)

### Typography & Readability
- **Line length:** 45–75 characters for body copy
- **Font size:** 16px+ for body, high contrast (4.5:1 minimum)
- **Links:** Underlined or obviously distinguishable from body text
- **All-caps headings:** Use sparingly; harder to read than title case

### Interaction Patterns
- **Buttons:** Clearly labelled, obvious affordance, 44px+ touch target
- **Forms:** Labels above inputs, clear required indicators, inline validation
- **Hover states:** Visual feedback (colour change, underline, shadow)
- **Focus states:** Visible focus ring for keyboard navigation
- **Loading states:** Spinner, progress bar, or skeleton screen
- **Empty states:** Not just blank — explain why content is missing, offer next step

**What to look for:**
- Unlabelled buttons ("Click here" instead of descriptive labels)
- Forms with labels to the left of inputs (harder to scan)
- No focus ring — keyboard users can't see where they are
- Hover-only interactions (not available on touch/mobile)

---

## Mobile (iOS/Android)

### Layout & Navigation
- **Bottom tab bar:** Primary nav (iOS convention, Android often uses drawer)
- **Hamburger menu:** Secondary nav or less-used actions
- **Gesture navigation:** Swipe back, long-press for context menu
- **Safe area:** Content inset from notches, home indicators
- **Spacing:** 16px+ margins to avoid thumb zone at bottom

**What to look for:**
- Nav elements at very bottom (blocks thumb access)
- Nav that requires precise clicking (buttons too small)
- Horizontal scrolling as primary interaction (unnatural)
- Inconsistent back button — sometimes top-left, sometimes gesture

### Touch Targets
- **Minimum size:** 44×44 points (iOS), 48×48 dp (Android)
- **Spacing:** 8px minimum between targets to avoid accidental taps
- **Placement:** Interactive elements away from screen edges (easier to hit)

### Screen Space
- **Status bar:** Account for space at top
- **Keyboard:** When input is focused, keyboard covers ~50% of screen
- **One column:** Stack content vertically by default
- **Scroll:** Infinite scroll or pagination; lazy-load as needed

---

## Social Media Posts (Instagram, Twitter, LinkedIn, TikTok)

### Composition & Format
- **Aspect ratio:** Know the platform. Instagram feed (4:5), Stories (9:16), Twitter (16:9 for video)
- **Safe zone:** Assume 80% of screen is visible (bottom 20% may be cut off by UI)
- **Text overlay:** High contrast, readable at thumbnail size (1/4 screen)
- **Thumbnail:** First 1–2 seconds critical; hooks matter

**What to look for:**
- Text small enough to be invisible at thumbnail size
- Text at bottom of image (cut off on mobile feed view)
- Low contrast text on image (unreadable at small size)
- No hook in first frame (video gets scrolled past)

### Engagement & CTAs
- **CTA placement:** Top-right or bottom of post (platform shows these first)
- **Hashtags:** Platform-dependent; Instagram: 3–5 relevant, Twitter: 1–2 max
- **Emoji:** Platform-dependent; Instagram: used naturally, Twitter: sparingly
- **Link placement:** Depends on platform (some hide links, some allow in caption)

**Common mistakes:**
- Burying the CTA in caption text (put first)
- Hashtag abuse (looks spammy; use selectively)
- Same caption across all platforms (tailor per platform norms)

---

## Email

### Layout
- **Width:** 600px max (safe across clients)
- **Single column:** Multi-column designs break in many email clients
- **Mobile:** Responsive stacking, large touch targets
- **Header:** Logo + quick nav; recipients may not scroll
- **CTA:** Button or clear link, placed above the fold

**What to look for:**
- Wide layouts that require horizontal scrolling on mobile
- Text-based links without enough contrast
- CTA button below lots of content (non-subscribers scroll past)
- Buttons with no fallback link (some email clients disable button markup)

### Images & Content
- **Alt text:** Every image needs alt text (images often disabled)
- **Background images:** Not supported in email; avoid relying on them
- **Typography:** Web-safe fonts only (Arial, Verdana, Times New Roman, Georgia)
- **Animated GIFs:** Supported but check client compatibility (Outlook may not animate)

---

## Dark Mode

All platforms now support dark mode. Designs must work in both.

### Colour Challenges
- **White text on black:** High contrast but can cause eye strain
- **Pure black background:** Use #121212 or #1a1a1a instead
- **Images:** May need different treatment (darker overlays, different contrast handling)
- **Transparency:** Becomes more visible on dark backgrounds

**What to look for:**
- Colours that pass contrast test on light but fail on dark
- Light greys that disappear on light backgrounds but glow on dark
- Icons that have no contrast against dark backgrounds
- Design that only accounts for light mode

**Fix pattern:** Test every colour pair in both light and dark. Use CSS custom properties to flip palettes.

---

## Accessibility Across Platforms

### All Platforms
- **Colour contrast:** 4.5:1 minimum for text, 3:1 for UI components (WCAG AA)
- **Keyboard navigation:** All interactive elements keyboard-accessible
- **Focus indicators:** Visible focus ring (don't remove with `outline: none`)
- **Alt text:** Meaningful descriptions for images (not "image" or "picture")
- **Skip links:** Ability to skip navigation and get to main content
- **Semantic HTML:** Proper heading hierarchy (H1, H2, H3), list markup, form labels

### Touch Devices
- **Touch target size:** 44×44px minimum
- **Spacing between targets:** 8px minimum
- **Avoid hover-only:** Hover isn't available on touch

### Keyboard Navigation
- **Tab order:** Logical, left-to-right, top-to-bottom
- **Enter/Space:** Works for buttons and links
- **Escape:** Closes modals, dropdowns, overlays
- **Arrow keys:** Navigate within components (tabs, menus, carousels)

---

## Design System Consistency Across Platforms

When designing for web + mobile + email, patterns should be recognizable but adapted to platform conventions.

**Example:** A CTA button
- **Web:** Full-width or inline, 44px height, shadow on hover
- **Mobile:** Full-width, 48px height, no shadow (touch feedback sufficient)
- **Email:** Fixed width (200px), fallback link below, no hover effects
- **Social post:** Integrated text overlay, no interactive elements

The button is still recognizable, but each platform gets its adapted version.
