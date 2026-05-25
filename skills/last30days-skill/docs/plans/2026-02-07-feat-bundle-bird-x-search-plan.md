---
title: "feat: Bundle Bird X search client to eliminate npm dependency"
type: feat
date: 2026-02-07
---

# feat: Bundle Bird X search client to eliminate npm dependency

## Overview

Replace the `subprocess.run(["bird", "search", ...])` dependency in `bird_x.py` with a vendored Node.js module that calls Twitter's GraphQL search API directly. This eliminates the need for users to `npm install -g @steipete/bird` and protects against the package being removed from npm.

Bird is MIT-licensed. We have the full compiled package archived at `vendor/steipete-bird-0.8.0.tgz` and forked to `github.com/mvanhorn/bird-cli-archive`.

## Problem Statement

@steipete deleted Bird's GitHub repo on 2026-02-07. The npm package still works today, but if he unpublishes it from npm:
- New users can't `npm install -g @steipete/bird`
- The `bird` binary disappears from PATH on fresh installs
- `bird_x.py` returns 0 X results for everyone without an xAI API key
- /last30days V2's headline feature ("free X search") stops working for new users

## Proposed Solution

**Vendor Bird's search-only subset as a Node.js module inside /last30days, called from Python via `subprocess.run(["node", ...])`.**

This is the minimal-change approach:
- Keep Python as the orchestrator (bird_x.py stays mostly the same)
- Replace `subprocess.run(["bird", "search", ...])` with `subprocess.run(["node", "vendor/bird-search.mjs", ...])`
- Extract only the search-related code from Bird (not posting, bookmarks, lists, etc.)
- Cookie auth stays the same (environment variables or browser extraction)

### Why not rewrite in pure Python?

Bird's search client uses Twitter's internal GraphQL API with:
- Rotating QueryIDs (hardcoded + runtime refresh from x.com)
- Specific request header construction (bearer token, csrf, client UUIDs)
- Cursor-based pagination with Twitter-specific response parsing
- The `@steipete/sweet-cookie` dependency for browser cookie extraction

Porting all of this to Python is ~1000 lines of fragile reverse-engineering. Vendoring the working JS code is faster, safer, and easier to maintain since the archive includes source maps for debugging.

## Technical Approach

### What we need from Bird

Only 8 files from `dist/lib/` (out of 30+):

1. `twitter-client-base.js` - HTTP client, auth headers, rate limiting
2. `twitter-client-search.js` - Search mixin (the core feature)
3. `twitter-client-utils.js` - Tweet parsing, cursor extraction
4. `twitter-client-constants.js` - API endpoints, QueryIDs
5. `twitter-client-types.js` - TypeScript type stubs
6. `cookies.js` - Cookie resolution (env vars, browser extraction)
7. `runtime-query-ids.js` - QueryID refresh from x.com
8. `paginate-cursor.js` - Cursor pagination helper

Plus:
- `features.json` - GraphQL feature flags
- `query-ids.json` - Hardcoded QueryID fallbacks

### What we DON'T need

Posting, bookmarks, lists, timelines, engagement, follow, media, news, user lookup, user tweets - all the non-search mixins. This cuts the vendored code roughly in half.

### Architecture

```
scripts/
  lib/
    bird_x.py              # MODIFIED - calls node instead of bird binary
    vendor/
      bird-search/
        bird-search.mjs    # NEW - thin CLI wrapper, ~40 lines
        lib/                # VENDORED - subset of Bird's dist/lib/
          twitter-client-base.js
          twitter-client-search.js
          twitter-client-utils.js
          twitter-client-constants.js
          twitter-client-types.js
          cookies.js
          runtime-query-ids.js
          paginate-cursor.js
          features.json
          query-ids.json
        node_modules/       # VENDORED - sweet-cookie only
          @steipete/
            sweet-cookie/
        package.json        # Minimal, points to bird-search.mjs
        LICENSE             # Bird's MIT license (required by MIT terms)
```

### Implementation

#### 1. Create `bird-search.mjs` wrapper (~40 lines)

A minimal Node.js script that:
- Accepts: `node bird-search.mjs <query> --count <n> --json`
- Creates a TwitterClient with search mixin only
- Resolves cookies (env vars first, then browser extraction)
- Calls `client.search(query, count)`
- Outputs JSON to stdout
- Exits with code 0 on success, 1 on error

This replaces the full `bird` CLI binary. Same interface, fraction of the code.

#### 2. Modify `bird_x.py` - change subprocess target

```python
# BEFORE (current)
cmd = ["bird", "search", query, "-n", str(count), "--json"]

# AFTER (vendored)
bird_search = Path(__file__).parent / "vendor" / "bird-search" / "bird-search.mjs"
cmd = ["node", bird_search, query, "--count", str(count), "--json"]
```

Same subprocess pattern. Same JSON output format. Minimal diff.

#### 3. Update auth check functions

```python
# BEFORE
def is_bird_installed() -> bool:
    return shutil.which("bird") is not None

# AFTER
def is_bird_installed() -> bool:
    bird_search = Path(__file__).parent / "vendor" / "bird-search" / "bird-search.mjs"
    return bird_search.exists() and shutil.which("node") is not None
```

`is_bird_authenticated()` changes from `bird whoami` to a quick Node.js cookie check or environment variable check.

`install_bird()` becomes a no-op (already vendored) or removes itself entirely.

#### 4. Vendor sweet-cookie

`@steipete/sweet-cookie` is the only runtime dependency. It handles browser cookie extraction on macOS/Linux. Options:

**Option A (recommended):** Vendor sweet-cookie into `vendor/bird-search/node_modules/`. It's small (one file). This makes the skill fully self-contained with zero npm installs.

**Option B:** Fall back to environment variables only (no browser cookie extraction). Users would need to manually set `AUTH_TOKEN` and `CT0` env vars. Simpler but worse UX.

Recommend Option A - vendor it.

#### 5. Update user-facing docs

- `README.md` - Remove "Install Bird CLI" section, replace with "Requires Node.js 22+"
- `SKILL.md` - Remove Bird CLI installation instructions
- Keep the fallback chain: vendored Bird search -> xAI API key -> web-only

## Acceptance Criteria

- [ ] `bird_x.py` calls vendored Node.js module instead of `bird` binary
- [ ] `search_x()` returns identical JSON format (no downstream changes needed)
- [ ] `search_handles()` works with vendored module
- [ ] Cookie auth works via environment variables (`AUTH_TOKEN`, `CT0`)
- [ ] Cookie auth works via browser extraction (sweet-cookie)
- [ ] `is_bird_installed()` checks for vendored module + Node.js
- [ ] `install_bird()` removed or returns success immediately
- [ ] No `npm install -g @steipete/bird` required anywhere
- [ ] Bird's MIT LICENSE included in vendor directory
- [ ] README updated to remove Bird CLI install steps
- [ ] SKILL.md updated to remove Bird CLI references
- [ ] Works on macOS (primary) and Linux
- [ ] Fallback to xAI API key still works if vendored search fails

## Files Changed

| File | Action | Description |
|------|--------|-------------|
| `scripts/lib/bird_x.py` | MODIFY | Replace `["bird", ...]` subprocess calls with `["node", "vendor/bird-search/bird-search.mjs", ...]` |
| `scripts/lib/vendor/bird-search/bird-search.mjs` | CREATE | Thin Node.js wrapper that imports Bird's search client and outputs JSON |
| `scripts/lib/vendor/bird-search/lib/*.js` | VENDOR | 8 files from Bird's dist/lib/ (search subset only) |
| `scripts/lib/vendor/bird-search/lib/features.json` | VENDOR | GraphQL feature flags |
| `scripts/lib/vendor/bird-search/lib/query-ids.json` | VENDOR | Hardcoded QueryID fallbacks |
| `scripts/lib/vendor/bird-search/node_modules/` | VENDOR | sweet-cookie package |
| `scripts/lib/vendor/bird-search/package.json` | CREATE | Minimal package.json for module resolution |
| `scripts/lib/vendor/bird-search/LICENSE` | COPY | Bird's MIT license |
| `README.md` | MODIFY | Remove Bird CLI install section, add Node.js 22+ requirement |
| `SKILL.md` | MODIFY | Remove Bird CLI references |

## Dependencies & Risks

**Node.js 22+ required** - Users who had Bird CLI already have Node.js. This is not a new dependency, just a version requirement. Claude Code environments typically have Node.js.

**Twitter API changes** - The GraphQL QueryIDs may rotate. Bird includes a runtime refresh mechanism (`runtime-query-ids.js`) that fetches new IDs from x.com. This is vendored and will continue working.

**sweet-cookie platform support** - Browser cookie extraction only works on macOS (Safari, Chrome, Firefox) and Linux (Chrome, Firefox). Windows users need manual env vars. This matches Bird CLI's existing behavior.

**Legal** - Bird is MIT licensed. MIT requires including the license notice in copies. We include `LICENSE` in the vendor directory. Using Twitter's internal API is the same legal gray area Bird always operated in - user accepted this when they used Bird.

## What This Does NOT Change

- Python remains the orchestrator - bird_x.py still does query construction, retry logic, response parsing
- The fallback chain stays: vendored search -> xAI API -> web-only
- Cookie auth mechanism is identical (env vars or browser extraction)
- JSON output format is identical - no changes needed in score.py or format.py
- xai_x.py is completely untouched

## References

- Bird CLI archive: `github.com/mvanhorn/bird-cli-archive`
- Local vendor tarball: `vendor/steipete-bird-0.8.0.tgz`
- Bird search implementation: `bird-cli-archive/dist/lib/twitter-client-search.js`
- Current bird_x.py: `scripts/lib/bird_x.py`
- Fallback chain: `scripts/lib/env.py:get_x_source()`
