# Semantic HTML Element Selection Guide

Choosing the right HTML element is the foundation of web accessibility. This guide helps you select the correct semantic element for every use case.

---

## Decision Trees

### Interactive Elements

```
Need user interaction?
│
├─ Navigates to another page/section?
│  └─ <a href="...">Link text</a>
│
├─ Performs action (submit, open, toggle)?
│  ├─ Submits form?
│  │  └─ <button type="submit">Submit</button>
│  │
│  ├─ Resets form?
│  │  └─ <button type="reset">Reset</button>
│  │
│  └─ Other action?
│     └─ <button type="button">Action</button>
│
└─ Do nothing (not interactive)?
   └─ <span> or <div> (no onclick!)
```

### Content Structure

```
Grouping content?
│
├─ Self-contained, reusable content?
│  └─ <article>
│     Examples: Blog post, news article, product card, comment
│
├─ Thematic grouping?
│  └─ <section>
│     Examples: Chapter, tab panel, part of page
│
├─ Navigation links?
│  └─ <nav>
│     Examples: Site nav, breadcrumbs, pagination, TOC
│
├─ Supplementary content?
│  └─ <aside>
│     Examples: Sidebar, callout, related links
│
├─ Main content area?
│  └─ <main> (only one per page)
│
├─ Page header?
│  └─ <header>
│
├─ Page footer?
│  └─ <footer>
│
└─ Generic container (no semantic meaning)?
   └─ <div>
```

### Form Elements

```
Collecting user input?
│
├─ Short text (name, email, search)?
│  └─ <input type="text/email/search">
│
├─ Password?
│  └─ <input type="password">
│
├─ Number?
│  └─ <input type="number">
│
├─ Date/Time?
│  └─ <input type="date/time/datetime-local">
│
├─ File upload?
│  └─ <input type="file">
│
├─ Single choice from list?
│  ├─ Few options (2-5)?
│  │  └─ <input type="radio"> (with same name)
│  │
│  └─ Many options (5+)?
│     └─ <select><option>...</option></select>
│
├─ Multiple choices?
│  ├─ Few options (2-5)?
│  │  └─ <input type="checkbox">
│  │
│  └─ Many options?
│     └─ <select multiple><option>...</option></select>
│
├─ Long text (comments, descriptions)?
│  └─ <textarea>
│
├─ Boolean toggle?
│  ├─ Binary (on/off)?
│  │  └─ <input type="checkbox">
│  │
│  └─ Tri-state (off/mixed/on)?
│     └─ <button aria-pressed="false/mixed/true">
│
└─ Hidden value?
   └─ <input type="hidden">
```

---

## Element Reference

### Sectioning Elements

#### `<article>`

**Use for**: Self-contained, independently distributable content.

```html
<!-- ✅ Blog post -->
<article>
  <h2>Article Title</h2>
  <p>Content...</p>
  <footer>By Author, Jan 1, 2026</footer>
</article>

<!-- ✅ Product card -->
<article>
  <h3>Product Name</h3>
  <img src="product.jpg" alt="Product photo">
  <p>$19.99</p>
  <button>Add to cart</button>
</article>

<!-- ✅ Comment -->
<article>
  <header>
    <h4>John Doe</h4>
    <time datetime="2026-01-14">Jan 14, 2026</time>
  </header>
  <p>Great article!</p>
</article>
```

**Screen reader**: Announces "article" landmark, helps users jump between articles.

#### `<section>`

**Use for**: Thematic grouping of content, usually with a heading.

```html
<!-- ✅ Chapter or topic -->
<section>
  <h2>Getting Started</h2>
  <p>Content about getting started...</p>
</section>

<!-- ✅ Tab panel -->
<div role="tabpanel">
  <section>
    <h3>Overview</h3>
    <p>Overview content...</p>
  </section>
</div>

<!-- ❌ WRONG - no heading -->
<section>
  <p>Random content</p>  <!-- Use div instead -->
</section>
```

**Rule**: Every `<section>` should have a heading (h1-h6).

#### `<nav>`

**Use for**: Navigation links.

```html
<!-- ✅ Primary navigation -->
<nav aria-label="Primary">
  <ul>
    <li><a href="/">Home</a></li>
    <li><a href="/about">About</a></li>
  </ul>
</nav>

<!-- ✅ Breadcrumbs -->
<nav aria-label="Breadcrumb">
  <ol>
    <li><a href="/">Home</a></li>
    <li><a href="/products">Products</a></li>
    <li aria-current="page">Widget</li>
  </ol>
</nav>

<!-- ✅ Pagination -->
<nav aria-label="Pagination">
  <a href="?page=1">Previous</a>
  <a href="?page=3">Next</a>
</nav>

<!-- ❌ WRONG - not navigation -->
<nav>
  <button onclick="doThing()">Action</button>  <!-- Use div -->
</nav>
```

**Tip**: Use `aria-label` when multiple `<nav>` on same page.

#### `<aside>`

**Use for**: Content tangentially related to main content.

```html
<!-- ✅ Sidebar -->
<aside>
  <h3>Related Articles</h3>
  <ul>...</ul>
</aside>

<!-- ✅ Callout box -->
<aside class="note">
  <h4>Note</h4>
  <p>This feature requires subscription.</p>
</aside>

<!-- ✅ Pull quote -->
<aside>
  <blockquote>"Accessibility is essential"</blockquote>
</aside>
```

#### `<main>`

**Use for**: Main content area. Only one per page.

```html
<body>
  <header>Site header</header>
  <nav>Navigation</nav>

  <main id="main-content" tabindex="-1">
    <!-- Primary content here -->
  </main>

  <footer>Site footer</footer>
</body>
```

**Critical**: Use `tabindex="-1"` and `id` for skip link target.

#### `<header>` and `<footer>`

**Use for**: Introductory content or group of navigation (header), or closing content (footer).

```html
<!-- ✅ Site header -->
<header>
  <img src="logo.png" alt="Company">
  <nav>...</nav>
</header>

<!-- ✅ Article header -->
<article>
  <header>
    <h2>Article Title</h2>
    <p>By Author, Jan 14</p>
  </header>
  <p>Content...</p>
</article>

<!-- ✅ Site footer -->
<footer>
  <p>&copy; 2026 Company</p>
  <nav aria-label="Footer">...</nav>
</footer>
```

---

### Text Content

#### Headings `<h1>` through `<h6>`

**Critical rule**: Never skip levels.

```html
<!-- ✅ CORRECT - logical hierarchy -->
<h1>Page Title</h1>
  <h2>Section</h2>
    <h3>Subsection</h3>
    <h3>Another Subsection</h3>
  <h2>Another Section</h2>

<!-- ❌ WRONG - skipped h2 -->
<h1>Page Title</h1>
  <h3>Subsection</h3>  <!-- Skipped h2! -->

<!-- ❌ WRONG - using for styling -->
<h1>Title</h1>
<h3 class="looks-like-h2">Not a heading, just want it big</h3>
<!-- Use h2 and style it with CSS -->
```

**Why**: Screen readers use heading hierarchy for navigation.

#### `<p>`, `<span>`, `<div>`

```html
<!-- <p> for paragraphs of text -->
<p>This is a paragraph of text content.</p>

<!-- <span> for inline styling/grouping -->
<p>This is <span class="highlight">important</span> text.</p>

<!-- <div> for block-level grouping with no semantic meaning -->
<div class="card">
  <h2>Title</h2>
  <p>Content</p>
</div>
```

**Rule**: If there's a more semantic element, use it instead of `<div>` or `<span>`.

#### Lists `<ul>`, `<ol>`, `<dl>`

```html
<!-- <ul> for unordered lists -->
<ul>
  <li>Item 1</li>
  <li>Item 2</li>
</ul>

<!-- <ol> for ordered lists -->
<ol>
  <li>First step</li>
  <li>Second step</li>
</ol>

<!-- <dl> for description lists (key-value pairs) -->
<dl>
  <dt>Name</dt>
  <dd>John Doe</dd>

  <dt>Email</dt>
  <dd>john@example.com</dd>
</dl>
```

**Screen reader**: Announces list type and item count.

---

### Interactive Elements

#### `<button>` vs `<a>`

**Decision**: Does it navigate or perform an action?

```html
<!-- ✅ Navigates → use <a> -->
<a href="/products">View products</a>
<a href="#section">Jump to section</a>

<!-- ✅ Performs action → use <button> -->
<button type="submit">Submit form</button>
<button type="button" onclick="openModal()">Open modal</button>
<button type="button" aria-pressed="false">Toggle</button>

<!-- ❌ WRONG - action with <a> -->
<a href="#" onclick="openModal()">Open modal</a>
<!-- Use <button> instead -->

<!-- ❌ WRONG - navigation with <button> -->
<button onclick="location.href='/products'">View products</button>
<!-- Use <a> instead -->
```

**Why**:
- `<a>` has "link" role, expected to navigate
- `<button>` has "button" role, expected to perform action
- Screen readers announce role to set user expectations

#### Button Types

```html
<!-- Submit form -->
<button type="submit">Submit</button>

<!-- Reset form to defaults -->
<button type="reset">Reset</button>

<!-- Generic action (default if type omitted) -->
<button type="button" onclick="doThing()">Do thing</button>
```

**Critical**: Always specify `type="button"` for non-submit buttons in forms to prevent accidental submission.

---

### Form Elements

#### `<label>`

**Critical**: Every form input must have an associated label.

```html
<!-- ✅ Explicit association (preferred) -->
<label for="email">Email address</label>
<input type="email" id="email" name="email">

<!-- ✅ Implicit association -->
<label>
  Email address
  <input type="email" name="email">
</label>

<!-- ❌ WRONG - no label -->
<input type="email" placeholder="Email">  <!-- Placeholder is NOT a label -->

<!-- ✅ CORRECT - label + placeholder -->
<label for="email">Email address</label>
<input type="email" id="email" placeholder="name@example.com">
```

#### `<input>` Types

```html
<!-- Text inputs -->
<input type="text" name="name">
<input type="email" name="email" autocomplete="email">
<input type="tel" name="phone" autocomplete="tel">
<input type="url" name="website">
<input type="search" name="q">
<input type="password" name="password" autocomplete="current-password">

<!-- Numbers and dates -->
<input type="number" name="quantity" min="1" max="10">
<input type="range" name="volume" min="0" max="100">
<input type="date" name="birthday">
<input type="time" name="appointment">
<input type="datetime-local" name="meeting">

<!-- Choices -->
<input type="checkbox" name="agree" id="agree">
<input type="radio" name="size" value="small" id="size-small">
<input type="file" name="upload" accept="image/*">

<!-- Hidden (no label needed) -->
<input type="hidden" name="csrf" value="token">
```

**Tip**: Use correct `type` for mobile keyboard optimization.

#### `<select>`

```html
<!-- Single selection -->
<label for="country">Country</label>
<select id="country" name="country">
  <option value="">Choose a country</option>
  <option value="us">United States</option>
  <option value="uk">United Kingdom</option>
</select>

<!-- Multiple selection -->
<label for="interests">Interests</label>
<select id="interests" name="interests" multiple>
  <option value="design">Design</option>
  <option value="dev">Development</option>
</select>

<!-- Grouped options -->
<label for="pet">Pet</label>
<select id="pet" name="pet">
  <optgroup label="4-legged">
    <option value="dog">Dog</option>
    <option value="cat">Cat</option>
  </optgroup>
  <optgroup label="Flying">
    <option value="bird">Bird</option>
  </optgroup>
</select>
```

#### `<textarea>`

```html
<label for="comments">Comments</label>
<textarea
  id="comments"
  name="comments"
  rows="5"
  maxlength="500"
></textarea>
```

#### Fieldsets and Legends

**Use for**: Grouping related form controls.

```html
<fieldset>
  <legend>Shipping address</legend>

  <label for="street">Street</label>
  <input type="text" id="street" name="street">

  <label for="city">City</label>
  <input type="text" id="city" name="city">
</fieldset>

<fieldset>
  <legend>Payment method</legend>

  <label>
    <input type="radio" name="payment" value="card">
    Credit card
  </label>

  <label>
    <input type="radio" name="payment" value="paypal">
    PayPal
  </label>
</fieldset>
```

**Screen reader**: Reads legend before each field in the group.

---

### Media Elements

#### `<img>`

```html
<!-- Informative image -->
<img src="diagram.png" alt="Workflow diagram showing 3 steps: Plan, Build, Deploy">

<!-- Decorative image -->
<img src="decoration.png" alt="">

<!-- Image that is a link -->
<a href="/products">
  <img src="products.jpg" alt="View our products">
</a>

<!-- Complex image -->
<figure>
  <img src="chart.png" alt="Bar chart showing sales data">
  <figcaption>
    Monthly sales increased from $10k in Jan to $15k in Jun.
  </figcaption>
</figure>
```

**Alt text rules**:
- Describe what the image conveys, not what it looks like
- Don't start with "Image of" or "Picture of"
- Use `alt=""` for purely decorative images
- Include text if image contains text

#### `<figure>` and `<figcaption>`

```html
<!-- Image with caption -->
<figure>
  <img src="photo.jpg" alt="Sunset over ocean">
  <figcaption>Sunset at Santa Monica Beach, 2026</figcaption>
</figure>

<!-- Code snippet with caption -->
<figure>
  <pre><code>function hello() { ... }</code></pre>
  <figcaption>Example of a JavaScript function</figcaption>
</figure>
```

#### `<audio>` and `<video>`

```html
<!-- Audio -->
<audio controls>
  <source src="podcast.mp3" type="audio/mpeg">
  <source src="podcast.ogg" type="audio/ogg">
  <a href="podcast.mp3">Download audio</a>
</audio>

<!-- Video with captions -->
<video controls>
  <source src="video.mp4" type="video/mp4">
  <track kind="captions" src="captions.vtt" srclang="en" label="English">
  <track kind="descriptions" src="descriptions.vtt" srclang="en">
</video>
```

---

## Common Anti-Patterns

### ❌ Clickable Divs

```html
<!-- ❌ WRONG -->
<div onclick="doThing()" class="button">
  Click me
</div>

<!-- ✅ CORRECT -->
<button type="button" onclick="doThing()">
  Click me
</button>
```

**Why wrong**: Div is not focusable, not keyboard accessible, no semantic role.

### ❌ Divs for Everything

```html
<!-- ❌ WRONG -->
<div class="header">
  <div class="nav">
    <div class="link" onclick="navigate()">Home</div>
  </div>
</div>

<!-- ✅ CORRECT -->
<header>
  <nav>
    <a href="/">Home</a>
  </nav>
</header>
```

### ❌ Headings for Styling

```html
<!-- ❌ WRONG - h3 used just for size -->
<h1>Title</h1>
<h3>This should be h2 but h3 looks better</h3>

<!-- ✅ CORRECT - use correct heading + CSS -->
<h1>Title</h1>
<h2 class="smaller">This is correctly h2, styled smaller</h2>

<style>
.smaller { font-size: 1.2rem; }
</style>
```

### ❌ Links Without href

```html
<!-- ❌ WRONG -->
<a class="button">Click me</a>
<a href="javascript:void(0)" onclick="doThing()">Action</a>

<!-- ✅ CORRECT -->
<button type="button">Click me</button>
<button type="button" onclick="doThing()">Action</button>
```

---

## Quick Reference Table

| Purpose | Correct Element | Wrong Element |
|---------|----------------|---------------|
| Navigate to page | `<a href>` | `<button>`, `<div onclick>` |
| Perform action | `<button>` | `<a href="#">`, `<div onclick>` |
| Submit form | `<button type="submit">` | `<a>`, `<input type="button">` |
| Text input | `<input>`, `<textarea>` | `<div contenteditable>` |
| Group content | `<article>`, `<section>` | `<div class="article">` |
| Navigation | `<nav>` | `<div class="nav">` |
| List | `<ul>`, `<ol>` | `<div>` with `<div>` children |
| Heading | `<h1>`-`<h6>` | `<div class="heading">`, `<strong>` |
| Image | `<img>` with `alt` | `<div>` with background-image |
| Toggle | `<button aria-pressed>` or `<input type="checkbox">` | `<div onclick>` |

---

**Golden Rule**: Use the most semantic element that fits the purpose. If you're using `<div>` or `<span>` for anything interactive, you're probably doing it wrong.
