# UX/Usability Heuristics — Designer's Eye Reference

## Table of Contents
1. Visibility of System Status
2. Match Between System & Real World
3. User Control & Freedom
4. System Consistency & Standards
5. Error Prevention
6. Error Recovery
7. Flexibility & Efficiency of Use
8. Aesthetic & Minimalist Design
9. Help & Documentation
10. Recognition vs. Recall
11. Affordance & Discoverability

---

## Nielsen's 10 Usability Heuristics

Based on Jakob Nielsen's foundational work, these heuristics identify common usability problems that create friction or confusion.

---

## 1. Visibility of System Status

The system must keep users informed in real-time. Users should always know what's happening.

**What to look for:**
- No loading indicator on slow operations
- Form submissions without success/error feedback
- Modal that doesn't show what triggered it or what it will do
- Button that doesn't change state when clicked (no disabled/loading appearance)
- No indication of which page/section the user is on

**Common violations:**
- "Submit" button that silently processes without feedback
- Carousel that doesn't indicate current position or progress
- Breadcrumb that doesn't highlight current page
- Search results without indication of search status or query

**Fix pattern:** Show state. Every action should have visible feedback.

---

## 2. Match Between System & Real World

Speak the user's language. Use familiar words, conventions, and real-world metaphors.

**What to look for:**
- Technical jargon in labels ("POST" instead of "Send", "404" instead of "Not Found")
- Metaphors that don't apply (floppy disk icon for "save" — nobody uses floppies anymore)
- Abbreviations without explanation (UX designers understand "CTA", customers don't)
- Icons that don't communicate their function to a typical user

**Common violations:**
- "Dashboard" when it's actually a report view
- Icons that only make sense if you hover (unlabeled icons)
- Use of "404" without explanation of what it means
- Insider language/acronyms in public-facing copy

**Fix pattern:** Use language your users speak. Explain before abbreviating.

---

## 3. User Control & Freedom

Users need undo/redo, escape routes, emergency exits. Let them get out of mistakes.

**What to look for:**
- Destructive actions without confirmation
- No back button or way to cancel an operation
- Modal with no close button (X or Escape key)
- Form with no clear way to reset/start over
- Delete/archive/destructive action without "undo" option

**Common violations:**
- "Delete forever" button without confirmation
- Form that clears all fields on submission without letting user review
- Nested menus that close immediately if you move the mouse wrong
- One-way navigation that requires hitting back button repeatedly

**Fix pattern:** Always confirm destructive actions. Always provide an escape route.

---

## 4. System Consistency & Standards

Users learn from one part of the system and expect it to apply elsewhere. Be consistent.

**What to look for:**
- Button styling that changes arbitrarily (sometimes blue, sometimes green for primary actions)
- Similar interactions with different patterns (some dropdowns open on hover, others on click)
- Icons used for different meanings in different places
- Spacing/padding that varies inconsistently
- Terminology that shifts (search vs. find, delete vs. remove, save vs. store)

**Common violations:**
- Primary actions in different colours across pages
- Inconsistent button placement (sometimes top-right, sometimes bottom-left)
- Text alignment that varies between sections
- Form labels above inputs in some places, left-aligned in others

**Fix pattern:** Create a design system. Consistency is friction reduction.

---

## 5. Error Prevention

Better to prevent problems than require recovery. Design to prevent errors.

**What to look for:**
- Required form fields with no indication they're required
- No validation feedback until form submission
- Dead-end links or 404s without alternative paths
- Tiny clickable targets on mobile
- Dangerous default values (auto-play, auto-subscribe)

**Common violations:**
- Form field marked required but easy to miss the indicator
- Credit card field accepting invalid formats silently
- Hover-only UI (not available on mobile/touch)
- No confirmation before navigating away from unsaved work

**Fix pattern:** Mark required fields clearly. Validate as users type. Confirm before danger.

---

## 6. Error Recovery (Minimize Error Severity)

When errors happen, recovery should be simple. Error messages should be plain language.

**What to look for:**
- Error message that's a cryptic code ("Error 451")
- Error message that doesn't explain how to fix the problem
- Error message in a colour that has low contrast
- Error state that doesn't highlight the problematic field
- Generic message that doesn't diagnose the real problem

**Common violations:**
- "Invalid input" without saying which field or what format is expected
- Error message at the top of the form while problematic field is below
- Red text on red background (contrast failure)
- Link to help page that doesn't exist

**Fix pattern:** Plain language, specific problem, clear solution, highlight the issue, actionable next step.

---

## 7. Flexibility & Efficiency of Use

Design for both novices and experts. Shortcuts for experienced users shouldn't hide core paths.

**What to look for:**
- No keyboard shortcuts for power users
- Forced multi-step processes that could be single-click
- Settings hidden in sub-menus when they're frequently used
- No way to batch-perform actions
- Novice users confused by expert-oriented UI

**Common violations:**
- Only mouse-driven interface (keyboard users struggle)
- Confirmation required for every action
- No way to repeat last action
- Search box only available via menu click

**Fix pattern:** Optimize for common tasks. Allow shortcuts without hiding the main path.

---

## 8. Aesthetic & Minimalist Design

Remove clutter. Every element should serve a purpose. Don't decorate just to decorate.

**What to look for:**
- Distracting animations or effects
- Too many colours competing for attention
- Excessive borders/dividers creating visual noise
- Decorative icons that don't convey information
- Ads or promotional content interfering with primary task
- Background images that reduce text legibility

**Common violations:**
- Auto-playing video in a sidebar while user tries to read
- Excessive drop shadows or gradients adding visual weight
- Too many visual styles mixed (rounded corners, sharp corners, bevels)
- Hover effects that are distracting rather than helpful

**Fix pattern:** Every pixel should work. Remove one element at a time; does it get missed?

---

## 9. Help & Documentation

Documentation should be easy to search, task-focused, and concrete.

**What to look for:**
- No help text for complex interactions
- Help text that's generic instead of specific to this field
- Help documentation at odds with actual UI behavior
- FAQ that doesn't answer common questions
- No way to access help from where the user is confused

**Common violations:**
- Form label with no explanation of what information is required
- Complex interaction with no tooltip or help text
- Help documentation linked to a different section of the site
- "Learn more" links that lead to marketing pages instead of docs

**Fix pattern:** Help should be in context. Assume the user doesn't know.

---

## 10. Recognition vs. Recall

Make objects, actions, and options visible. Minimize the user's memory load.

**What to look for:**
- Required actions hidden in menus (user has to remember them)
- Icon-only buttons without labels
- Too many similar options that look identical (hard to distinguish)
- No visual indication of what was selected
- Steps in a process that need to be memorized

**Common violations:**
- Hamburger menu with items the user saw on the previous page
- Toolbar with 20 icons, no labels, all similar weight
- Dropdown with 50 options, no grouping or labels
- Multi-step form with no indicator of which step is current

**Fix pattern:** Show, don't hide. Label icons. Group related items. Use familiar patterns.

---

## Affordance & Discoverability

**Affordance:** An object's design should suggest its function. A button should look clickable.

**What to look for:**
- Static text that looks clickable (hover effect missing)
- Clickable elements that don't look clickable (no button styling)
- Links that don't look like links (same colour as body text)
- Form fields that don't look interactive
- Interactive areas too small to hit (< 44px for touch targets)

**Common violations:**
- Blue underlined text that isn't a link (causes confusion)
- Links without underline in body text (user can't distinguish)
- Buttons that are plain text (no visual affordance)
- Tiny close button on modal (hard to find / hit)

**Fix pattern:** Make interactive elements look interactive. Meet minimum touch target sizes (44×44px).
