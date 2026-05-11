# Accessibility Correction Rules

Common accessibility mistakes and their corrections for Claude Code to apply automatically.

---

## Interactive Elements

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| `<div onclick="doThing()">Click</div>` | `<button type="button" onclick="doThing()">Click</button>` |
| `<span onclick="submit()">Submit</span>` | `<button type="submit">Submit</button>` |
| `<a href="#" onclick="doThing()">Action</a>` | `<button type="button" onclick="doThing()">Action</button>` |
| `<a href="javascript:void(0)">Action</a>` | `<button type="button">Action</button>` |
| `<div class="button">Click</div>` | `<button>Click</button>` |

**Why**: Divs and spans are not keyboard accessible and have no semantic role. Use `<button>` for actions, `<a>` only for navigation.

---

## Focus Indicators

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| `*:focus { outline: none; }` | `*:focus-visible { outline: 2px solid var(--primary); outline-offset: 2px; }` |
| `button:focus { outline: 0; }` | `button:focus-visible { outline: 2px solid var(--primary); }` |
| Removing outline without replacement | Always provide custom focus indicator |

**Why**: Focus indicators are required for keyboard navigation. Use `:focus-visible` to show only on keyboard focus.

---

## Images

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| `<img src="logo.png">` | `<img src="logo.png" alt="Company Name">` |
| `<img src="icon.png" alt="">` in button | `<button aria-label="Close"><img src="icon.png" alt=""></button>` |
| `<div style="background-image: url(...)">` for content image | `<img src="..." alt="Description">` |
| Alt text starting with "Image of" | Describe what image conveys, not that it's an image |

**Why**: All images need alt text. Use `alt=""` only for purely decorative images.

---

## Form Labels

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| `<input placeholder="Email">` | `<label for="email">Email</label><input type="email" id="email" placeholder="name@example.com">` |
| `<input aria-label="Email">` | `<label for="email">Email</label><input type="email" id="email">` (prefer visible label) |
| Label without for/id connection | `<label for="email">Email</label><input id="email">` |

**Why**: Placeholders are not labels. Every input needs a visible, associated label.

---

## Headings

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| `<h1>Title</h1><h3>Subtitle</h3>` | `<h1>Title</h1><h2>Subtitle</h2>` (don't skip levels) |
| `<h3 class="big">Title</h3>` for styling | `<h2 class="smaller">Title</h2>` (use correct level + CSS) |
| Multiple `<h1>` on same page | One `<h1>` per page (page title) |

**Why**: Screen readers use heading hierarchy for navigation. Never skip levels.

---

## Color Contrast

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| Light gray `#999` on white background | Darker `#595959` (4.6:1 contrast) or `#737373` (4.7:1) |
| Blue `#4d90fe` on white (2.9:1) | Darker blue `#0066cc` (5.7:1) or `#004080` (6.5:1) |
| Red `#ef4444` on white (3.3:1) | Darker red `#b91c1c` (6.2:1) |
| Color alone for errors | Icon + text + color |

**Why**: WCAG requires 4.5:1 contrast for normal text, 3:1 for large text and UI components.

---

## ARIA Usage

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| `<button role="button">Click</button>` | `<button>Click</button>` (native element already has role) |
| `<div role="button">Click</div>` | `<button>Click</button>` (use native element) |
| aria-label when visible text exists | Use visible text, omit aria-label |
| `<button aria-hidden="true">Click</button>` | Remove aria-hidden (makes button inaccessible) |

**Why**: No ARIA is better than bad ARIA. Use semantic HTML first.

---

## Keyboard Navigation

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| `tabindex="1"` or other positive numbers | `tabindex="0"` or natural order |
| Interactive div without tabindex | `<button>` (natively keyboard accessible) |
| No Escape key handler for dialogs | Add Escape listener to close dialog |
| No focus trap in modals | Implement focus trap pattern |

**Why**: Positive tabindex breaks natural tab order. All interactive elements must be keyboard accessible.

---

## Semantic HTML

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| `<div class="header">` | `<header>` |
| `<div class="nav">` | `<nav>` |
| `<div class="article">` | `<article>` |
| `<div class="section">` | `<section>` (with heading) |
| `<span onclick="...">` for interactive | `<button>` |

**Why**: Semantic elements provide built-in accessibility and structure.

---

## Link Purpose

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| `<a href="/article">Click here</a>` | `<a href="/article">Read our accessibility guide</a>` |
| `<a href="/more">Read more</a>` | `<a href="/article" aria-label="Read more about accessibility">Read more</a>` |
| Generic "Learn more" links | Descriptive link text or aria-label with context |

**Why**: Link text should describe destination. Screen reader users often navigate by links list.

---

## Form Validation

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| Visual error without aria-invalid | `<input aria-invalid="true" aria-describedby="error">` |
| Error message without role="alert" | `<span id="error" role="alert">Error message</span>` |
| No aria-describedby connection | Link input to error via aria-describedby |
| Required field without indicator | `<input required aria-required="true">` + visual indicator |

**Why**: Screen readers need programmatic error indication and connection to error messages.

---

## Live Regions

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| Dynamic content without announcement | `<div aria-live="polite">New content</div>` |
| Critical error without announcement | `<div role="alert">Error message</div>` |
| Status update not announced | `<div role="status">Update</div>` |

**Why**: Screen readers don't automatically announce dynamic content changes.

---

## Tables

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| `<table>` without headers | `<table><thead><tr><th scope="col">Header</th></tr></thead>` |
| Headers without scope attribute | `<th scope="col">` for columns, `<th scope="row">` for rows |
| Table without caption | `<table><caption>Table description</caption>` |

**Why**: Screen readers use headers to associate data cells with their labels.

---

## Skip Links

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| No skip link | `<a href="#main" class="skip-link">Skip to main content</a>` at top of body |
| Skip link always visible | Hide offscreen, show on focus |
| Skip target not focusable | `<main id="main" tabindex="-1">` |

**Why**: Keyboard users need to skip repeated navigation on every page.

---

## Auto-playing Media

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| `<video autoplay>` | `<video controls>` (require user interaction) |
| `<audio autoplay>` | `<audio controls>` |
| Autoplay without pause | Add controls or pause button |

**Why**: Auto-playing media is disruptive for screen reader users.

---

## Language

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| `<html>` without lang | `<html lang="en">` |
| Foreign language phrase without marking | `<span lang="fr">bonjour</span>` |

**Why**: Screen readers need language to pronounce text correctly.

---

## Testing Prompts

When Claude completes accessibility work, always prompt:

```
✅ Completed. Please test:
1. Tab through with keyboard only
2. Run axe DevTools scan
3. Test with screen reader (NVDA or VoiceOver)
4. Verify 4.5:1 contrast on all text
```

---

**Remember**: Accessibility is not optional. These corrections ensure WCAG 2.1 AA compliance and usable interfaces for everyone.
