---
name: phy-bundle-size-audit
description: JavaScript bundle size auditor and budget enforcer. Parses webpack stats JSON, Vite bundle report, Rollup output, or Next.js build output to identify largest chunks, flag chunks that exceed configurable size budgets, detect duplicate dependencies across chunks, find treeshaking failures (packages that should be side-effect-free but aren't), and generate CI fail-gate commands. Outputs a GitHub PR annotation-ready summary with per-chunk size, gzip estimate, and actionable optimization suggestions. Zero external API — pure local file analysis. Triggers on "bundle too large", "webpack stats", "chunk size", "bundle budget", "treeshaking", "bundle analyzer", "/bundle-size-audit".
license: Apache-2.0
metadata:
  author: PHY041
  version: "1.0.0"
  tags:
    - webpack
    - vite
    - bundler
    - performance
    - treeshaking
    - developer-tools
    - javascript
    - nextjs
    - rollup
---

# Bundle Size Auditor

You added one import. Your Lighthouse score dropped 12 points. Your LCP went from 1.8s to 3.1s.

This skill parses your bundler's output — webpack stats JSON, Vite build report, or Next.js `.next/` directory — identifies the largest chunks, finds which packages are bloating them, detects treeshaking failures, and gives you the exact code changes to fix it.

**Supports webpack, Vite, Rollup, Next.js. Zero external API.**

---

## Trigger Phrases

- "bundle too large", "my bundle is huge", "reduce bundle size"
- "webpack stats", "analyze webpack output", "chunk size"
- "bundle budget", "size limit", "bundle regression"
- "treeshaking not working", "dead code in bundle"
- "which package is largest", "find large dependencies"
- "Next.js bundle", "Vite build report"
- "/bundle-size-audit"

---

## How to Provide Input

```bash
# Option 1: Webpack stats JSON (most detailed)
webpack --profile --json > stats.json
/bundle-size-audit stats.json

# Option 2: Vite build (auto-detected)
vite build
/bundle-size-audit dist/

# Option 3: Next.js build (auto-detected)
next build
/bundle-size-audit .next/

# Option 4: Rollup stats
rollup -c --bundleConfigAsCjs
/bundle-size-audit rollup-stats.json

# Option 5: Set size budgets
/bundle-size-audit --max-chunk 250kb --max-initial 500kb

# Option 6: Focus on a specific chunk or package
/bundle-size-audit --chunk main --package lodash

# Option 7: Generate CI fail-gate only
/bundle-size-audit --ci-config
```

---

## Step 1: Detect Build Artifacts

```bash
python3 -c "
import os, json
from pathlib import Path

# Priority order for detection
checks = [
    ('webpack stats', ['stats.json', 'webpack-stats.json', 'build/stats.json']),
    ('Next.js', ['.next/build-manifest.json', '.next/server/pages-manifest.json']),
    ('Vite', ['dist/', 'dist/assets/']),
    ('Rollup', ['dist/', 'build/']),
    ('Create React App', ['build/static/js/', 'build/asset-manifest.json']),
]

found = []
for name, paths in checks:
    for p in paths:
        if os.path.exists(p):
            found.append((name, p))
            break

if found:
    for name, path in found:
        size = 0
        if os.path.isfile(path):
            size = os.path.getsize(path)
            print(f'Detected {name}: {path} ({size:,} bytes)')
        else:
            # Directory — count JS files
            js_files = list(Path(path).rglob('*.js'))
            total = sum(f.stat().st_size for f in js_files)
            print(f'Detected {name}: {path}/ ({len(js_files)} JS files, {total/1024:.0f} KB total)')
else:
    print('No build artifacts found.')
    print('Run your build first:')
    print('  webpack --profile --json > stats.json')
    print('  vite build')
    print('  next build')
"
```

---

## Step 2: Parse Bundle Data

### For Webpack Stats JSON

```python
import json
from pathlib import Path

def parse_webpack_stats(stats_path):
    """Parse webpack stats.json into chunk/asset summary."""
    with open(stats_path) as f:
        stats = json.load(f)

    assets = []
    for asset in stats.get('assets', []):
        name = asset['name']
        size = asset['size']
        # Only JS and CSS assets
        if not any(name.endswith(ext) for ext in ['.js', '.css', '.mjs']):
            continue
        assets.append({
            'name': name,
            'size': size,
            'size_kb': round(size / 1024, 1),
            'gzip_estimate_kb': round(size / 1024 * 0.3, 1),  # ~30% compression typical
            'chunks': asset.get('chunkNames', []),
            'initial': asset.get('isOverSizeLimit', False),
        })

    # Sort by size desc
    assets.sort(key=lambda x: x['size'], reverse=True)

    # Module analysis — find largest modules
    modules = []
    for module in stats.get('modules', []):
        if module.get('size', 0) > 10 * 1024:  # >10KB only
            modules.append({
                'name': module.get('name', 'unknown'),
                'size': module.get('size', 0),
                'size_kb': round(module.get('size', 0) / 1024, 1),
                'reasons': [r.get('moduleName', '') for r in module.get('reasons', [])[:3]],
            })
    modules.sort(key=lambda x: x['size'], reverse=True)

    return assets, modules[:50]  # top 50 modules


def parse_webpack_chunks(stats_path):
    """Identify chunks and their composition."""
    with open(stats_path) as f:
        stats = json.load(f)

    chunks = []
    for chunk in stats.get('chunks', []):
        chunks.append({
            'id': chunk.get('id'),
            'names': chunk.get('names', []),
            'size': chunk.get('size', 0),
            'size_kb': round(chunk.get('size', 0) / 1024, 1),
            'initial': chunk.get('initial', False),
            'entry': chunk.get('entry', False),
            'module_count': len(chunk.get('modules', [])),
            'files': chunk.get('files', []),
        })

    chunks.sort(key=lambda x: x['size'], reverse=True)
    return chunks
```

### For Vite / CRA (dist/ directory)

```python
import os
from pathlib import Path

def parse_dist_directory(dist_path):
    """Parse build output directory for Vite/CRA/Rollup."""
    js_dir = Path(dist_path)

    # Find all JS files
    js_files = []
    for fpath in js_dir.rglob('*.js'):
        if 'node_modules' in str(fpath):
            continue
        size = fpath.stat().st_size
        js_files.append({
            'name': str(fpath.relative_to(dist_path)),
            'path': str(fpath),
            'size': size,
            'size_kb': round(size / 1024, 1),
            'gzip_estimate_kb': round(size / 1024 * 0.3, 1),
            'is_chunk': 'chunk' in fpath.name.lower() or fpath.parent.name == 'assets',
            'is_vendor': 'vendor' in fpath.name.lower(),
        })

    js_files.sort(key=lambda x: x['size'], reverse=True)

    # CSS files
    css_files = []
    for fpath in js_dir.rglob('*.css'):
        size = fpath.stat().st_size
        css_files.append({
            'name': str(fpath.relative_to(dist_path)),
            'size_kb': round(size / 1024, 1),
        })

    return js_files, css_files


def estimate_gzip(size_bytes):
    """Estimate gzip size. JS typically compresses 65-75%."""
    return round(size_bytes * 0.30 / 1024, 1)
```

### For Next.js (.next/ directory)

```bash
# Next.js provides build-manifest.json and .next/analyze/ if ANALYZE=true
python3 -c "
import json, os
from pathlib import Path

next_dir = Path('.next')
if not next_dir.exists():
    print('No .next/ directory found. Run: next build')
    exit(1)

# Read build-manifest
manifest_path = next_dir / 'build-manifest.json'
if manifest_path.exists():
    manifest = json.loads(manifest_path.read_text())

    # Collect all JS files referenced
    all_files = set()
    for page, files in manifest.get('pages', {}).items():
        for f in files:
            all_files.add(f)

    print(f'Pages: {len(manifest.get(\"pages\", {}))}')
    print(f'Unique JS chunks: {len(all_files)}')

# Read static/chunks/
chunks_dir = next_dir / 'static' / 'chunks'
if chunks_dir.exists():
    chunks = []
    for fpath in chunks_dir.rglob('*.js'):
        size = fpath.stat().st_size
        chunks.append((fpath.name, size))
    chunks.sort(key=lambda x: x[1], reverse=True)

    total = sum(s for _, s in chunks)
    print(f'\\nTotal chunks: {len(chunks)} ({total/1024:.0f} KB)')
    print('\\nTop 10 chunks:')
    for name, size in chunks[:10]:
        print(f'  {name}: {size/1024:.1f} KB (~{size*0.3/1024:.1f} KB gzip)')
"
```

---

## Step 3: Detect Duplicate Dependencies

```python
import re
from pathlib import Path

def find_duplicate_modules(stats_path):
    """Find the same package duplicated across chunks (common with npm hoisting issues)."""
    with open(stats_path) as f:
        stats = json.load(f)

    # Track package versions seen in different chunks
    package_chunks = {}

    for module in stats.get('modules', []):
        name = module.get('name', '')
        # Extract package name from ./node_modules/package/...
        match = re.search(r'node_modules/(@[^/]+/[^/]+|[^/]+)', name)
        if not match:
            continue
        pkg = match.group(1)

        # Which chunks contain this module?
        chunk_ids = module.get('chunks', [])
        if pkg not in package_chunks:
            package_chunks[pkg] = set()
        package_chunks[pkg].update(chunk_ids)

    # Find packages in 3+ chunks (likely duplicated)
    duplicates = {
        pkg: chunks
        for pkg, chunks in package_chunks.items()
        if len(chunks) >= 3
    }

    return sorted(duplicates.items(), key=lambda x: len(x[1]), reverse=True)


def find_heavy_packages(stats_path, threshold_kb=50):
    """Find packages over threshold_kb in the bundle."""
    with open(stats_path) as f:
        stats = json.load(f)

    package_sizes = {}

    for module in stats.get('modules', []):
        name = module.get('name', '')
        size = module.get('size', 0)
        match = re.search(r'node_modules/(@[^/]+/[^/]+|[^/]+)', name)
        if not match:
            continue
        pkg = match.group(1)
        package_sizes[pkg] = package_sizes.get(pkg, 0) + size

    heavy = {
        pkg: size
        for pkg, size in package_sizes.items()
        if size / 1024 > threshold_kb
    }
    return sorted(heavy.items(), key=lambda x: x[1], reverse=True)
```

---

## Step 4: Detect Treeshaking Failures

```python
# Known packages with treeshaking issues + their lightweight alternatives
TREESHAKING_ALERTS = {
    'lodash': {
        'issue': 'lodash CommonJS bundle cannot be treeshaken. Full ~70KB always included.',
        'fix': 'Use lodash-es OR import individual functions: import debounce from "lodash/debounce"',
        'savings': '60-68 KB',
    },
    'moment': {
        'issue': 'moment.js includes all 160+ locale files (~290KB). Treeshaking does NOT work.',
        'fix': 'Replace with date-fns (treeshakeable, ~13KB used) or dayjs (~2KB)',
        'savings': '270-290 KB',
    },
    'antd': {
        'issue': 'antd without babel-plugin-import bundles the entire component library.',
        'fix': 'Add babel-plugin-import or use antd/es/{component} imports',
        'savings': '500+ KB',
    },
    '@mui/material': {
        'issue': 'MUI default import (@mui/material) may bundle unused components.',
        'fix': 'Use named imports: import Button from "@mui/material/Button"',
        'savings': '100-200 KB',
    },
    'rxjs': {
        'issue': 'import { Observable } from "rxjs" bundles the full library if not configured.',
        'fix': 'Use rxjs/operators and ensure sideEffects: false in your bundler config',
        'savings': '50-100 KB',
    },
    'aws-sdk': {
        'issue': 'aws-sdk v2 cannot be treeshaken — it bundles every AWS service.',
        'fix': 'Migrate to @aws-sdk/client-{service} (v3, fully treeshakeable)',
        'savings': '200+ KB',
    },
    'firebase': {
        'issue': 'firebase/app includes all modules unless modular API is used.',
        'fix': 'Use modular imports: import { getAuth } from "firebase/auth"',
        'savings': '100-400 KB',
    },
}

def check_treeshaking_failures(stats_path):
    """Find packages known to have treeshaking issues."""
    with open(stats_path) as f:
        stats = json.load(f)

    found_packages = set()
    for module in stats.get('modules', []):
        name = module.get('name', '')
        for pkg in TREESHAKING_ALERTS:
            if f'node_modules/{pkg}' in name or f'node_modules/{pkg}/' in name:
                found_packages.add(pkg)

    alerts = []
    for pkg in found_packages:
        alerts.append({
            'package': pkg,
            **TREESHAKING_ALERTS[pkg]
        })

    return alerts
```

---

## Step 5: Check Against Budgets

```python
DEFAULT_BUDGETS = {
    'initial_js': 250 * 1024,    # 250 KB initial JS (gzipped target)
    'initial_css': 50 * 1024,     # 50 KB initial CSS
    'any_chunk': 500 * 1024,      # 500 KB max any single chunk
    'total_js': 1000 * 1024,      # 1 MB total JS
}

def check_budgets(assets, custom_budgets=None):
    """Check assets against size budgets."""
    budgets = {**DEFAULT_BUDGETS, **(custom_budgets or {})}
    violations = []

    total_js = sum(a['size'] for a in assets if a['name'].endswith('.js'))
    initial_js = sum(
        a['size'] for a in assets
        if a['name'].endswith('.js') and a.get('initial', False)
    )

    if initial_js > budgets['initial_js']:
        violations.append({
            'type': 'INITIAL_JS',
            'actual_kb': round(initial_js / 1024, 1),
            'budget_kb': round(budgets['initial_js'] / 1024, 1),
            'overage_kb': round((initial_js - budgets['initial_js']) / 1024, 1),
            'severity': 'HIGH',
        })

    for asset in assets:
        if asset['size'] > budgets['any_chunk']:
            violations.append({
                'type': 'CHUNK_SIZE',
                'chunk': asset['name'],
                'actual_kb': asset['size_kb'],
                'budget_kb': round(budgets['any_chunk'] / 1024, 1),
                'overage_kb': round((asset['size'] - budgets['any_chunk']) / 1024, 1),
                'severity': 'MEDIUM',
            })

    if total_js > budgets['total_js']:
        violations.append({
            'type': 'TOTAL_JS',
            'actual_kb': round(total_js / 1024, 1),
            'budget_kb': round(budgets['total_js'] / 1024, 1),
            'overage_kb': round((total_js - budgets['total_js']) / 1024, 1),
            'severity': 'LOW',
        })

    return violations
```

---

## Step 6: Output Report

```markdown
## Bundle Size Audit
Project: my-app | Bundler: webpack 5.89 | Build: production

---

### Size Summary

| Chunk | Raw | Gzip Est. | Type | Status |
|-------|-----|-----------|------|--------|
| main.abc123.js | 312 KB | 94 KB | initial | 🔴 OVER BUDGET |
| vendor.def456.js | 489 KB | 147 KB | initial | 🟠 WARNING |
| dashboard.ghi789.js | 95 KB | 29 KB | async | ✅ OK |
| settings.jkl012.js | 41 KB | 12 KB | async | ✅ OK |

**Total JS: 937 KB (281 KB gzipped)**
**Initial JS: 801 KB — 🔴 EXCEEDS 500 KB budget (301 KB over)**

---

### 🔴 Budget Violations

| Violation | Actual | Budget | Overage | Impact |
|-----------|--------|--------|---------|--------|
| Initial JS | 801 KB | 500 KB | +301 KB | Slow LCP, fails Core Web Vitals |
| main.js chunk | 312 KB | 250 KB | +62 KB | Blocking parse time |

---

### 🔴 Treeshaking Failures (High Impact)

**lodash** — 68 KB that could be 4 KB
```
Problem: import { debounce } from 'lodash' bundles the entire library (CommonJS)
Fix:     import debounce from 'lodash/debounce'
         OR: replace with lodash-es
Savings: ~64 KB
```

**moment** — 287 KB that could be 13 KB
```
Problem: moment.js bundles all 160+ locale files
Fix:     Replace with date-fns (treeshakeable):
         import { format, parseISO } from 'date-fns'
Savings: ~274 KB
```

---

### 🟠 Duplicate Dependencies (Same Package in 3+ Chunks)

```
Package              Chunk Count    Issue
react-dom            6 chunks       Included in vendor + 5 async chunks
lodash               4 chunks       Not deduplicated — CommonJS import in multiple files
styled-components    3 chunks       Multiple versions? Run: npm ls styled-components
```

**Fix:** Ensure these packages are in `optimization.splitChunks.cacheGroups.vendor`:
```js
// webpack.config.js
optimization: {
  splitChunks: {
    cacheGroups: {
      vendor: {
        test: /[\\/]node_modules[\\/](react|react-dom|lodash-es)[\\/]/,
        name: 'vendors',
        chunks: 'all',
      },
    },
  },
},
```

---

### Top 10 Heaviest Modules

| Package | Size | % of Bundle | Treeshakeable? |
|---------|------|-------------|----------------|
| moment | 287 KB | 30.6% | ❌ No |
| lodash | 68 KB | 7.3% | ⚠️ Only with lodash-es |
| @mui/icons-material | 61 KB | 6.5% | ✅ Yes, if named imports |
| draft-js | 58 KB | 6.2% | ⚠️ Partial |
| highlight.js | 49 KB | 5.2% | ✅ Use registerLanguage() |
| ... | | | |

---

### 💡 Optimization Recommendations (Ordered by Impact)

**#1 — Replace moment.js → date-fns** (~274 KB savings)
```bash
npm uninstall moment
npm install date-fns
# Then: find . -name "*.ts" | xargs grep -l "from 'moment'"
# Replace: import { format } from 'date-fns'
```

**#2 — Fix lodash imports** (~64 KB savings)
```bash
# Find all lodash imports:
grep -r "from 'lodash'" src/ --include="*.ts" --include="*.tsx"
# Change to: import debounce from 'lodash/debounce'
# OR install lodash-es: npm install lodash-es
```

**#3 — Lazy-load dashboard route** (~95 KB off initial bundle)
```tsx
// Before:
import Dashboard from './Dashboard'
// After:
const Dashboard = React.lazy(() => import('./Dashboard'))
```

**Estimated total savings: 433 KB raw / ~130 KB gzipped**
**After fixes: Initial JS ~368 KB ✅ (under 500 KB budget)**

---

### CI Fail-Gate

Add to your CI pipeline to prevent bundle regressions:

```bash
# Option 1: bundlesize (npm package)
npx bundlesize
# Requires .bundlesizerc in repo:
# {"files": [{"path": "dist/js/*.js", "maxSize": "250 kB"}]}

# Option 2: size-limit
npx size-limit
# Requires .size-limit.json:
# [{"path": "dist/js/main.*.js", "limit": "250 KB"}]

# Option 3: Pure bash check (no npm package needed)
python3 -c "
import os, sys
from pathlib import Path

budgets = {
    'dist/js/main': 250 * 1024,
    'dist/js/vendor': 500 * 1024,
}

failed = False
for pattern, limit in budgets.items():
    matches = list(Path('.').glob(f'{pattern}*.js'))
    for f in matches:
        size = f.stat().st_size
        if size > limit:
            print(f'FAIL: {f} is {size/1024:.0f} KB (limit: {limit/1024:.0f} KB)')
            failed = True
        else:
            print(f'PASS: {f} is {size/1024:.0f} KB')

sys.exit(1 if failed else 0)
"
```

Add to `.github/workflows/build.yml`:
```yaml
- name: Check bundle size
  run: python3 scripts/check-bundle-size.py
```

---

### Webpack Bundle Analyzer (Visual)

For interactive visualization:

```bash
# Install once
npm install --save-dev webpack-bundle-analyzer

# Generate report
npx webpack-bundle-analyzer stats.json dist/ --no-open --report report.html
# Opens interactive treemap — look for unexpectedly large node_modules blocks

# Next.js
ANALYZE=true next build
# Opens browser with interactive bundle analysis
```
```

---

## Quick Mode Output

```
Bundle Audit: my-app (webpack 5, production)

Initial JS: 801 KB gzip → 🔴 OVER 500 KB budget
Total JS:   937 KB (281 KB gzip)
Chunks: 4 (2 initial, 2 async)

🔴 moment.js: 287 KB — replace with date-fns → -274 KB
🔴 lodash: 68 KB — fix imports → -64 KB
🟠 @mui/icons-material: 61 KB — use named imports
🟡 6 duplicate react-dom instances — fix splitChunks

Estimated savings: 433 KB → Initial JS drops to ~368 KB ✅
Run /bundle-size-audit --ci-config for CI fail-gate
```
