---
name: phy-css-dead-code
description: Unused CSS detector and dead selector auditor. Scans your stylesheet files against all HTML, JSX, TSX, Vue, and template files to find selectors that are defined but never referenced anywhere in your codebase. Detects CSS framework (Tailwind, Bootstrap, CSS Modules, vanilla CSS, Sass/SCSS) and applies the right analysis strategy for each. Reports estimated byte savings per dead rule, finds !important overuse, duplicate selectors, and orphaned media-query blocks. Generates a safe-deletion plan with exact grep verification commands. Works with PostCSS, Sass, Less, and raw CSS. Zero external API — uses npx and grep only. Triggers on "unused CSS", "dead CSS", "CSS bloat", "remove unused styles", "CSS cleanup", "what CSS can I delete", "/css-dead-code".
license: Apache-2.0
metadata:
  author: PHY041
  version: "1.0.0"
  tags:
    - css
    - performance
    - dead-code
    - tailwind
    - frontend
    - developer-tools
    - code-quality
    - bundle-size
    - refactoring
    - sass
---

# CSS Dead Code Auditor

CSS only grows. Every sprint adds new rules; almost none get removed. A feature gets deleted — the styles stay. A component gets renamed — the old class selectors stay. After a year, 30-40% of your stylesheet is dead weight: downloaded by every user, parsed by every browser, doing nothing.

Point this skill at your project and get a complete inventory of dead selectors, their exact file locations, estimated byte savings, and safe-deletion commands.

**Works with any CSS methodology. No config. No build step. Zero external APIs.**

---

## Trigger Phrases

- "unused CSS", "dead CSS selectors", "CSS dead code"
- "CSS bloat", "remove unused styles", "CSS cleanup"
- "what CSS can I delete", "CSS coverage", "unused classes"
- "Tailwind purge", "Bootstrap unused", "CSS audit"
- "stylesheet cleanup", "orphaned selectors"
- "/css-dead-code"

---

## How to Provide Input

```bash
# Option 1: Audit the current directory
/css-dead-code

# Option 2: Specific CSS file or directory
/css-dead-code src/styles/
/css-dead-code assets/main.css

# Option 3: Specify content directory (where HTML/JSX lives)
/css-dead-code --content src/

# Option 4: Specific framework
/css-dead-code --framework tailwind
/css-dead-code --framework vanilla
/css-dead-code --framework bootstrap

# Option 5: Show only selectors that can be safely deleted (high confidence)
/css-dead-code --safe-only

# Option 6: Estimate size savings only (quick mode)
/css-dead-code --size-estimate

# Option 7: Check a single selector
/css-dead-code --check ".btn-legacy-primary"
```

---

## Step 1: Detect CSS Framework and Project Structure

```bash
# Detect CSS framework from project files
FRAMEWORK="unknown"

if [ -f "tailwind.config.js" ] || [ -f "tailwind.config.ts" ] || [ -f "tailwind.config.cjs" ]; then
  FRAMEWORK="tailwind"
elif grep -r "bootstrap" package.json 2>/dev/null | grep -q "\"bootstrap\""; then
  FRAMEWORK="bootstrap"
elif find . -name "*.module.css" -not -path "*/node_modules/*" 2>/dev/null | head -1 | grep -q "."; then
  FRAMEWORK="css-modules"
elif find . -name "*.scss" -o -name "*.sass" -not -path "*/node_modules/*" 2>/dev/null | head -3 | grep -q "."; then
  FRAMEWORK="sass"
else
  FRAMEWORK="vanilla"
fi

echo "Detected framework: $FRAMEWORK"

# Find all CSS/SCSS/SASS/Less files
CSS_FILES=$(find . \( -name "*.css" -o -name "*.scss" -o -name "*.sass" -o -name "*.less" \) \
  -not -path "*/node_modules/*" \
  -not -path "*/dist/*" \
  -not -path "*/.next/*" \
  -not -path "*/build/*" \
  2>/dev/null)

CSS_COUNT=$(echo "$CSS_FILES" | wc -l | tr -d ' ')
echo "Found $CSS_COUNT CSS/SCSS files"

# Find all template/component files
CONTENT_FILES=$(find . \( -name "*.html" -o -name "*.jsx" -o -name "*.tsx" \
  -o -name "*.vue" -o -name "*.svelte" -o -name "*.hbs" \
  -o -name "*.erb" -o -name "*.blade.php" -o -name "*.pug" \) \
  -not -path "*/node_modules/*" \
  -not -path "*/dist/*" \
  2>/dev/null)

CONTENT_COUNT=$(echo "$CONTENT_FILES" | wc -l | tr -d ' ')
echo "Found $CONTENT_COUNT template/component files to cross-reference"
```

---

## Step 2: Framework-Specific Analysis

### Tailwind CSS

```bash
# Check tailwind.config.js content paths
echo "=== Tailwind Config Check ==="
python3 -c "
import re, json

try:
    with open('tailwind.config.js') as f:
        content = f.read()
    # Extract content array
    content_match = re.search(r'content\s*:\s*\[(.*?)\]', content, re.DOTALL)
    if content_match:
        print('Content paths configured:')
        for line in content_match.group(1).split(','):
            line = line.strip().strip('\"\'')
            if line:
                print(f'  {line}')
    else:
        print('⚠️  No content array found in tailwind.config.js — all classes may be purged!')
except FileNotFoundError:
    print('tailwind.config.js not found')
"

# Find classes actually used in content files
echo ""
echo "=== Tailwind Classes In Use ==="
# Extract all class="" values from content files
grep -rh "class[Name]*=\"[^\"]*\"\|class[Name]*={[^}]*}" . \
  --include="*.jsx" --include="*.tsx" --include="*.html" --include="*.vue" \
  --exclude-dir="node_modules" --exclude-dir="dist" 2>/dev/null | \
  grep -oE '[a-z][a-z0-9:-]+' | sort -u | head -50

# Run Tailwind CLI to see what would be purged
if command -v npx &>/dev/null; then
  echo ""
  echo "Running Tailwind dry-run to check purged classes..."
  npx --yes tailwindcss -i ./input.css -o /tmp/tw-output.css --minify 2>/dev/null
  echo "Output size: $(du -h /tmp/tw-output.css 2>/dev/null | cut -f1)"
fi
```

### Vanilla CSS / SCSS

```python
# Extract all selectors from CSS files and cross-reference with content
import re, os, sys
from pathlib import Path
from collections import defaultdict

def extract_selectors(css_content):
    """Extract all CSS selectors from a stylesheet."""
    # Remove comments
    css = re.sub(r'/\*.*?\*/', '', css_content, flags=re.DOTALL)
    # Remove @-rules (media queries, keyframes) content for now
    css = re.sub(r'@[^{]+\{[^}]+\}', '', css)
    # Extract selectors (before the { block)
    selectors = re.findall(r'([^{}@][^{}]*)\s*\{', css)
    result = []
    for sel_group in selectors:
        # Split on commas for multi-selector rules
        for sel in sel_group.split(','):
            sel = sel.strip()
            if sel and not sel.startswith('@'):
                result.append(sel)
    return result

def extract_class_refs(content):
    """Extract all class and ID references from template/component files."""
    classes = set()
    ids = set()
    # class="foo bar baz"
    for match in re.finditer(r'class(?:Name)?\s*=\s*["\']([^"\']+)["\']', content):
        classes.update(match.group(1).split())
    # className={`...`} dynamic classes
    for match in re.finditer(r'["\']([a-z][a-z0-9-_]+)["\']', content):
        classes.add(match.group(1))
    # id="foo"
    for match in re.finditer(r'\bid\s*=\s*["\']([^"\']+)["\']', content):
        ids.add(match.group(1))
    return classes, ids

# Collect all selectors from CSS files
all_selectors = defaultdict(list)  # selector -> [(file, line_num)]

css_dirs = ['.']
for css_dir in css_dirs:
    for fpath in Path(css_dir).rglob('*.css'):
        if 'node_modules' in str(fpath) or 'dist' in str(fpath):
            continue
        content = fpath.read_text(errors='ignore')
        for sel in extract_selectors(content):
            all_selectors[sel].append(str(fpath))

print(f"Total unique selectors found: {len(all_selectors)}")

# Collect all class/id references from content files
all_classes = set()
all_ids = set()
content_exts = ['.html', '.jsx', '.tsx', '.vue', '.svelte', '.erb', '.hbs']
for root, dirs, files in os.walk('.'):
    dirs[:] = [d for d in dirs if d not in {'node_modules', 'dist', '.next', 'build', '.git'}]
    for fname in files:
        if any(fname.endswith(ext) for ext in content_exts):
            fpath = Path(root) / fname
            content = fpath.read_text(errors='ignore')
            c, i = extract_class_refs(content)
            all_classes.update(c)
            all_ids.update(i)

print(f"Unique class references found in templates: {len(all_classes)}")

# Find unused selectors
unused = []
for selector, locations in all_selectors.items():
    # Extract the class name from the selector
    class_matches = re.findall(r'\.([a-zA-Z][a-zA-Z0-9_-]*)', selector)
    id_matches = re.findall(r'#([a-zA-Z][a-zA-Z0-9_-]*)', selector)

    is_used = False
    for cls in class_matches:
        if cls in all_classes:
            is_used = True
            break
    for id_name in id_matches:
        if id_name in all_ids:
            is_used = True
            break

    # Skip element-only selectors (body, h1, p, etc.) — too risky to flag
    if not class_matches and not id_matches:
        continue  # element selector, skip

    if not is_used:
        unused.append((selector, locations))

print(f"\nUnused selectors: {len(unused)}")
for sel, locs in sorted(unused, key=lambda x: len(x[1]), reverse=True)[:30]:
    print(f"  {sel:50} ({', '.join(set(locs))})")
```

### CSS Modules

```bash
# For CSS Modules — check which .module.css files have no corresponding component
echo "=== Orphaned CSS Module Files ==="
find . -name "*.module.css" -not -path "*/node_modules/*" | while read cssfile; do
  # Get basename without extension
  base=$(basename "$cssfile" .module.css)
  # Check if a component with this name exists
  component=$(find . -name "${base}.tsx" -o -name "${base}.jsx" \
    -not -path "*/node_modules/*" 2>/dev/null | head -1)
  if [ -z "$component" ]; then
    echo "  ORPHANED: $cssfile (no ${base}.tsx or ${base}.jsx found)"
  fi
done
```

---

## Step 3: Detect CSS Anti-Patterns

```bash
# Anti-pattern 1: !important overuse
echo "=== !important usage ==="
grep -rn "!important" . \
  --include="*.css" --include="*.scss" --include="*.sass" \
  --exclude-dir="node_modules" | wc -l | xargs echo "Count:"

# Anti-pattern 2: Duplicate selectors (same selector defined twice)
python3 -c "
import re
from collections import Counter
from pathlib import Path

selector_count = Counter()
for fpath in Path('.').rglob('*.css'):
    if 'node_modules' in str(fpath):
        continue
    content = fpath.read_text(errors='ignore')
    content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
    for match in re.finditer(r'([.#][a-zA-Z][^{]*?)\s*\{', content):
        sel = match.group(1).strip()
        selector_count[sel] += 1

duplicates = {sel: count for sel, count in selector_count.items() if count > 1}
if duplicates:
    print('Duplicate selectors:')
    for sel, count in sorted(duplicates.items(), key=lambda x: -x[1])[:15]:
        print(f'  {sel}: defined {count} times')
else:
    print('No duplicate selectors found')
"

# Anti-pattern 3: Overly broad selectors
grep -rn "^\* \{" . --include="*.css" --include="*.scss" --exclude-dir="node_modules" | head -5
grep -rn "^div \{" . --include="*.css" --include="*.scss" --exclude-dir="node_modules" | head -5

# Anti-pattern 4: Empty rules
grep -rn "{[[:space:]]*}" . --include="*.css" --include="*.scss" --exclude-dir="node_modules" | head -10

# Anti-pattern 5: Orphaned @keyframes (animations defined but never used)
echo "=== Orphaned @keyframes ==="
python3 -c "
import re
from pathlib import Path

# Find all defined keyframe names
keyframes = set()
for fpath in Path('.').rglob('*.css'):
    if 'node_modules' in str(fpath): continue
    for m in re.finditer(r'@keyframes\s+(\S+)', fpath.read_text(errors='ignore')):
        keyframes.add(m.group(1))

# Find all animation-name usages
used_animations = set()
for fpath in list(Path('.').rglob('*.css')) + list(Path('.').rglob('*.scss')):
    if 'node_modules' in str(fpath): continue
    for m in re.finditer(r'animation(?:-name)?\s*:\s*([^;]+)', fpath.read_text(errors='ignore')):
        used_animations.update(m.group(1).split())

orphaned = keyframes - used_animations
if orphaned:
    print('Orphaned @keyframes (defined, never used in animation property):')
    for name in sorted(orphaned):
        print(f'  @keyframes {name}')
else:
    print('No orphaned @keyframes')
"
```

---

## Step 4: Estimate Size Savings

```bash
python3 -c "
import re, os
from pathlib import Path

# Get total CSS size
total_size = 0
css_files = list(Path('.').rglob('*.css'))
css_files = [f for f in css_files if 'node_modules' not in str(f) and 'dist' not in str(f)]

for fpath in css_files:
    total_size += fpath.stat().st_size

print(f'Total CSS size: {total_size / 1024:.1f} KB ({len(css_files)} files)')

# Rough estimate: unused selectors are typically 20-40% of legacy codebases
# For Tailwind: purging can reduce from 3.7MB to 5-20KB (99% reduction)
# For vanilla CSS: typically 15-30% reduction
print()
print('Estimated savings by project type:')
print(f'  Tailwind (unpurged → purged): up to {total_size * 0.98 / 1024:.0f} KB → {total_size * 0.02 / 1024:.0f} KB')
print(f'  Bootstrap (if tree-shaking): up to {total_size * 0.7 / 1024:.0f} KB savings')
print(f'  Vanilla CSS (typical): {total_size * 0.25 / 1024:.0f} KB savings estimate')
"
```

---

## Step 5: Output Report

```markdown
## CSS Dead Code Report
Project: my-app | Framework: vanilla CSS + SCSS | Date: 2026-03-18
CSS files: 12 (48.3 KB total) | Template files scanned: 89

---

### Summary

| Category | Count | Est. Savings |
|----------|-------|-------------|
| 🔴 Unused class selectors (never referenced) | 34 | ~12 KB |
| 🔴 Orphaned CSS Module files (no component) | 2 | ~3 KB |
| 🟠 Duplicate selectors (defined 2+ times) | 8 | ~2 KB |
| 🟠 Orphaned @keyframes (never animated) | 3 | ~0.5 KB |
| 🟡 !important overuse (reduces cascading) | 14 | — |
| 🟡 Empty rules {} | 6 | ~0.3 KB |
| ✅ Used selectors | 156 | — |

**Estimated total savings: ~18 KB (37% reduction)**
After gzip: ~6 KB reduction in transfer size

---

### 🔴 Unused Selectors — Safe to Delete

High confidence (class never appears anywhere in templates):

```css
/* src/styles/legacy.scss — 18 unused selectors from old redesign */
.btn-legacy-primary    { ... }  /* never referenced */
.btn-legacy-secondary  { ... }  /* never referenced */
.card-old-style        { ... }  /* never referenced */
.modal-v1              { ... }  /* never referenced */
.modal-v1__header      { ... }  /* never referenced */
.modal-v1__body        { ... }  /* never referenced */

/* src/styles/marketing.css — leftover from old landing page */
.hero-gradient-bg      { ... }  /* never referenced */
.testimonial-bubble    { ... }  /* never referenced */
.pricing-card-v1       { ... }  /* never referenced */
```

Verify before deleting:
```bash
# Confirm .btn-legacy-primary is truly absent from all templates
grep -rn "btn-legacy-primary" . \
  --include="*.jsx" --include="*.tsx" --include="*.html" --include="*.vue" \
  --exclude-dir="node_modules"
# Should return zero results before deleting
```

---

### 🔴 Orphaned CSS Module Files

```
src/components/OldCheckout.module.css  ← no OldCheckout.tsx or OldCheckout.jsx
src/components/LegacyModal.module.css  ← no LegacyModal.tsx
```

These module files have no corresponding component — they're safe to delete entirely.

---

### 🟠 Duplicate Selectors

| Selector | Files | Occurrences |
|----------|-------|------------|
| `.container` | base.css:12, layout.css:8 | 2x |
| `.btn-primary` | buttons.css:3, components.css:44 | 2x |
| `.text-muted` | typography.css:22, utils.css:15 | 2x |

When the same selector is defined twice, the second definition silently overwrites the first. Keep only the later one (or merge intentionally).

---

### 🟠 Orphaned @keyframes

```css
/* defined in animations.css but no animation property references it */
@keyframes oldSlideIn { ... }     /* search: animation: oldSlideIn → 0 results */
@keyframes deprecatedFadeUp { ... }   /* search: animation: deprecatedFadeUp → 0 results */
@keyframes v1Bounce { ... }       /* search: animation: v1Bounce → 0 results */
```

Verify and delete:
```bash
grep -rn "oldSlideIn\|deprecatedFadeUp\|v1Bounce" . --include="*.css" --include="*.scss" --include="*.jsx" --include="*.tsx" --exclude-dir="node_modules"
```

---

### 🟡 !important Overuse (14 occurrences)

```
src/styles/overrides.css:  7 uses — all in .admin-panel scope
src/styles/legacy.scss:    4 uses — 3 on z-index
src/components/Button.module.css: 3 uses — all overriding Bootstrap
```

Replace with higher-specificity selectors instead of `!important`. Example:
```css
/* Before */
.btn { color: red !important; }

/* After — higher specificity, same result */
.my-app .btn { color: red; }
```

---

### Cleanup Commands

```bash
# 1. Delete orphaned CSS Modules
rm src/components/OldCheckout.module.css
rm src/components/LegacyModal.module.css

# 2. Remove dead selectors from legacy.scss (verify first with grep above)
# Edit src/styles/legacy.scss — remove the 18 selectors listed above

# 3. Remove orphaned keyframes from animations.css
# Edit src/styles/animations.css — remove @keyframes oldSlideIn, deprecatedFadeUp, v1Bounce

# 4. After cleanup, verify no regressions
# Run your visual regression tests, or:
npx percy snapshot --dry-run  # if using Percy
```

---

### Tailwind-Specific: Purge Configuration

If using Tailwind and your CSS bundle is large (> 100 KB), the issue is likely an incomplete `content` config:

```javascript
// tailwind.config.js
module.exports = {
  content: [
    './src/**/*.{js,jsx,ts,tsx}',  // ← must include ALL files that use Tailwind classes
    './pages/**/*.{js,jsx,ts,tsx}',
    './components/**/*.{js,jsx,ts,tsx}',
    './app/**/*.{js,jsx,ts,tsx}',
    // Add any template files here too
  ],
  // ...
}
```

With a correct content config, Tailwind purges from 3.7 MB (full library) down to 5-20 KB.
```

---

## Quick Mode

Fast one-line summary:

```
CSS Dead Code: my-app (vanilla CSS)
📦 48.3 KB total CSS | Est. savings: ~18 KB (37%)
🔴 34 unused selectors | 2 orphaned CSS modules
🟠 8 duplicates | 3 orphaned @keyframes
🟡 14 !important uses

Run /css-dead-code --detail for file locations and deletion commands
```

---

## Why CSS Grows Without Bound

The CSS growth pattern is predictable:

1. Developer adds `.feature-card-v2` for a redesign
2. `.feature-card-v1` is "deprecated" but never deleted ("maybe we'll revert")
3. Component is deleted from JSX — selector stays in CSS (no compiler warning)
4. 18 months later: 200 dead selectors, no one knows which are safe

Unlike JavaScript (where tree-shaking removes unused exports at build time), CSS has no equivalent dead-code elimination by default. This audit fills that gap.
