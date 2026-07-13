---
name: discogs-sync
description: >
  Add and remove albums from a Discogs wantlist or collection by artist and album name,
  master ID, or release ID. Search marketplace pricing for vinyl, CD, and other formats.
  List wantlist and collection contents. Use when the user asks to add or remove a record
  from their Discogs wantlist or collection, check what's on their wantlist, look up
  marketplace prices, or find what a record is selling for. Also supports bulk operations
  via CSV/JSON file input.
metadata: {"openclaw":{"emoji":"🎵","requires":{"bins":["python3"]}}}
---

# Discogs Sync — Wantlist, Collection & Marketplace CLI

Add and remove albums from your Discogs wantlist or collection, search marketplace pricing, and list what you have. Identify albums by artist/album name, Discogs master ID, or release ID. For bulk operations, pass a CSV or JSON file.

## Runtime & Dependencies

**Runtime:** Python 3.10+

**Python packages** (installed automatically on first run):
- `python3-discogs-client>=2.8` — Discogs API client
- `click>=8.1` — CLI framework
- `rich>=13.0` — Terminal output formatting

**Installation:** No manual `pip install` needed. On first run, `discogs-sync.py` creates a local `.deps/` virtual environment inside the skill directory and installs dependencies from `requirements.txt`. Subsequent runs reuse the existing venv. This works on macOS (including Homebrew Python), Linux, and Windows without requiring system-level package installation.

To force a clean reinstall of dependencies, delete the `.deps/` directory and run any command again.

## Quick Start

```bash
# Authenticate (one-time setup — also installs dependencies on first run)
python3 /home/claw/.openclaw/workspace/skills/discogs_sync/discogs-sync.py auth

# Add an album to your wantlist by name
python3 /home/claw/.openclaw/workspace/skills/discogs_sync/discogs-sync.py wantlist add --artist "Radiohead" --album "OK Computer"

# Add to your collection by release ID
python3 /home/claw/.openclaw/workspace/skills/discogs_sync/discogs-sync.py collection add --release-id 7890

# Check marketplace prices for a vinyl pressing
python3 /home/claw/.openclaw/workspace/skills/discogs_sync/discogs-sync.py marketplace search --artist "Miles Davis" --album "Kind of Blue" --format Vinyl

# List your wantlist
python3 /home/claw/.openclaw/workspace/skills/discogs_sync/discogs-sync.py wantlist list

# Remove from collection
python3 /home/claw/.openclaw/workspace/skills/discogs_sync/discogs-sync.py collection remove --artist "Nirvana" --album "Nevermind"
```

## Authentication

Run once to authenticate. Two modes are available:

**Personal access token (default)** — simplest option. Generate a token at https://www.discogs.com/settings/developers.

```bash
python3 /home/claw/.openclaw/workspace/skills/discogs_sync/discogs-sync.py auth
python3 /home/claw/.openclaw/workspace/skills/discogs_sync/discogs-sync.py auth --mode token
```

**OAuth 1.0a** — full OAuth flow with consumer key/secret, for apps that need delegated access.

```bash
python3 /home/claw/.openclaw/workspace/skills/discogs_sync/discogs-sync.py auth --mode oauth
```

Credentials are stored in `~/.discogs-sync/config.json`.

```bash
# Verify authentication
python3 /home/claw/.openclaw/workspace/skills/discogs_sync/discogs-sync.py whoami
python3 /home/claw/.openclaw/workspace/skills/discogs_sync/discogs-sync.py whoami --output-format json
```

## Usage

### Wantlist — Add, Remove, List

```bash
# Add by artist/album name
python3 /home/claw/.openclaw/workspace/skills/discogs_sync/discogs-sync.py wantlist add --artist "Radiohead" --album "OK Computer" [--format Vinyl]

# Add by Discogs master ID (resolves to main release, or filters by --format)
python3 /home/claw/.openclaw/workspace/skills/discogs_sync/discogs-sync.py wantlist add --master-id 3425

# Add by specific release ID
python3 /home/claw/.openclaw/workspace/skills/discogs_sync/discogs-sync.py wantlist add --release-id 7890

# Remove by artist/album name
python3 /home/claw/.openclaw/workspace/skills/discogs_sync/discogs-sync.py wantlist remove --artist "Radiohead" --album "OK Computer"

# Remove by release ID
python3 /home/claw/.openclaw/workspace/skills/discogs_sync/discogs-sync.py wantlist remove --release-id 7890

# List current wantlist
python3 /home/claw/.openclaw/workspace/skills/discogs_sync/discogs-sync.py wantlist list [--search "QUERY"] [--format Vinyl] [--year 1997] [--no-cache] [--output-format json]
```

Duplicate check: skips if the release is already in the wantlist (by release_id, master_id, or fuzzy artist+title match).

### Collection — Add, Remove, List

```bash
# Add by artist/album name
python3 /home/claw/.openclaw/workspace/skills/discogs_sync/discogs-sync.py collection add --artist "Miles Davis" --album "Kind of Blue" [--format Vinyl]

# Add by master ID or release ID
python3 /home/claw/.openclaw/workspace/skills/discogs_sync/discogs-sync.py collection add --master-id 3425 [--folder-id 1]
python3 /home/claw/.openclaw/workspace/skills/discogs_sync/discogs-sync.py collection add --release-id 7890 [--folder-id 1]

# Add a second copy of something already owned
python3 /home/claw/.openclaw/workspace/skills/discogs_sync/discogs-sync.py collection add --release-id 7890 --allow-duplicate

# Remove by artist/album name
python3 /home/claw/.openclaw/workspace/skills/discogs_sync/discogs-sync.py collection remove --artist "Miles Davis" --album "Kind of Blue"

# Remove by release ID
python3 /home/claw/.openclaw/workspace/skills/discogs_sync/discogs-sync.py collection remove --release-id 7890

# List collection (all folders)
python3 /home/claw/.openclaw/workspace/skills/discogs_sync/discogs-sync.py collection list [--search "QUERY"] [--format CD] [--year 1959] [--folder-id 0] [--no-cache] [--output-format json]
```

Duplicate check: by default, `add` skips if the release is already in the collection (by release_id, master_id, or fuzzy artist+title match). Use `--allow-duplicate` to add another copy.

### Marketplace — Search Pricing

```bash
# Search by artist/album name
python3 /home/claw/.openclaw/workspace/skills/discogs_sync/discogs-sync.py marketplace search --artist "Radiohead" --album "OK Computer" [--format Vinyl] [--country US] [--output-format json]

# Search by master ID
python3 /home/claw/.openclaw/workspace/skills/discogs_sync/discogs-sync.py marketplace search --master-id 3425 [--format Vinyl] [--country US]

# Search by specific release ID (skips master version scan)
python3 /home/claw/.openclaw/workspace/skills/discogs_sync/discogs-sync.py marketplace search --release-id 7890

# Filter by price range and country
python3 /home/claw/.openclaw/workspace/skills/discogs_sync/discogs-sync.py marketplace search --artist "Pink Floyd" --album "The Dark Side of the Moon" --format Vinyl --country US --min-price 10 --max-price 50 --currency USD

# Show detailed progress and condition grade price suggestions
python3 /home/claw/.openclaw/workspace/skills/discogs_sync/discogs-sync.py marketplace search --artist "Radiohead" --album "OK Computer" --verbose --details
```

Returns release versions sorted by lowest price, with number of copies for sale. Single-item results are cached for 1 hour by lookup parameters. With `--details`, a separate details cache entry is used; if only the base cache is warm the tool fetches just the condition-grade price suggestions rather than re-running the full search. Pass `--no-cache` to force a live fetch (result is still written to cache).

### Bulk Operations via File

For batch operations, pass a CSV or JSON file instead of individual `--artist`/`--album` flags.

```bash
# Sync wantlist from file (preview first with --dry-run)
python3 /home/claw/.openclaw/workspace/skills/discogs_sync/discogs-sync.py wantlist sync albums.csv --dry-run
python3 /home/claw/.openclaw/workspace/skills/discogs_sync/discogs-sync.py wantlist sync albums.csv [--remove-extras] [--threshold 0.7] [--output-format json]

# Sync collection from file
python3 /home/claw/.openclaw/workspace/skills/discogs_sync/discogs-sync.py collection sync albums.csv [--folder-id 1] [--remove-extras] [--dry-run]

# Batch marketplace search from file
python3 /home/claw/.openclaw/workspace/skills/discogs_sync/discogs-sync.py marketplace search albums.csv [--format Vinyl] [--country US] [--max-price 50] [--max-versions 25] [--output-format json]
```

**CSV format** (header row required, `artist` and `album` required):

```csv
artist,album,format,year,notes
Radiohead,OK Computer,Vinyl,,Must have
Miles Davis,Kind of Blue,,1959,Original pressing
Nirvana,Nevermind,CD,1991,
```

**JSON format** (array of objects with the same fields):

```json
[
    {"artist": "Radiohead", "album": "OK Computer", "format": "Vinyl"},
    {"artist": "Miles Davis", "album": "Kind of Blue", "year": 1959}
]
```

Format synonyms are normalized automatically: `LP`/`record`/`12"` → Vinyl, `compact disc` → CD, `tape`/`mc` → Cassette.

## Options

| Option | Applies To | Description |
|--------|-----------|-------------|
| `--output-format` | All | `table` (default) or `json` for machine-readable output |
| `--threshold` | add, remove, search, sync | Match score threshold 0.0–1.0 (default: 0.7) |
| `--format` | add, list, marketplace search | Filter by format: Vinyl, CD, Cassette (synonyms like LP, record are normalized) |
| `--year` | list | Filter by release year (exact match) |
| `--folder-id` | collection | Target folder (default: 1 for adds, 0 for reads) |
| `--allow-duplicate` | collection add | Allow adding another copy of an album already in collection |
| `--country` | marketplace search | Filter by country of pressing (exact match: US, UK, Germany, etc.) |
| `--release-id` | marketplace search | Fetch stats for a specific release (bypasses master version scan) |
| `--min-price` | marketplace | Minimum price filter |
| `--max-price` | marketplace | Maximum price filter |
| `--currency` | marketplace | Currency code (default: USD) |
| `--max-versions` | marketplace | Max release versions to check per master (default: 25) |
| `--details` | marketplace search | Include suggested prices by condition grade |
| `--no-cache` | list, marketplace search | Bypass local cache; fresh results are still written back to cache |
| `--verbose` | sync, marketplace search | Show detailed progress and API call logging |
| `--search` | list | Filter results by artist or title (case-insensitive substring match) |
| `--dry-run` | sync | Preview changes without modifying Discogs |
| `--remove-extras` | sync | Remove wantlist/collection items not in the input file |

## Output Format

### Text (Default)

**wantlist list / collection list:**

```
                           Wantlist
┌────────────┬───────────┬─────────────┬─────────────┬────────┬──────┐
│ Release ID │ Master ID │ Artist      │ Title       │ Format │ Year │
├────────────┼───────────┼─────────────┼─────────────┼────────┼──────┤
│ 7890       │ 3425      │ Radiohead   │ OK Computer │ Vinyl  │ 1997 │
│ 1234       │ 1000      │ Miles Davis │ Kind of Blue│ Vinyl  │ 1959 │
└────────────┴───────────┴─────────────┴─────────────┴────────┴──────┘

Total: 2
```

**marketplace search:**

```
                               Marketplace Results
┌───────────┬────────────┬───────────┬─────────────┬────────┬──────────┬──────────────┐
│ Master ID │ Release ID │ Artist    │ Title       │ Format │ For Sale │ Lowest Price │
├───────────┼────────────┼───────────┼─────────────┼────────┼──────────┼──────────────┤
│ 3425      │ 7890       │ Radiohead │ OK Computer │ Vinyl  │ 42       │ 25.99 USD    │
│ 3425      │ 15432      │ Radiohead │ OK Computer │ Vinyl  │ 18       │ 32.50 USD    │
└───────────┴────────────┴───────────┴─────────────┴────────┴──────────┴──────────────┘
```

**add / remove result:**

```
Sync Report
  Total input: 1
  Added:   1
  Removed: 0
  Skipped: 0
  Errors:  0
```

### JSON (`--output-format json`)

**wantlist list / collection list:**

```json
{
  "items": [
    {
      "release_id": 7890,
      "master_id": 3425,
      "title": "OK Computer",
      "artist": "Radiohead",
      "format": "Vinyl",
      "year": 1997
    }
  ],
  "total": 1
}
```

**marketplace search:**

```json
{
  "results": [
    {
      "master_id": 3425,
      "release_id": 7890,
      "title": "OK Computer",
      "artist": "Radiohead",
      "format": "Vinyl",
      "country": "US",
      "year": 1997,
      "num_for_sale": 42,
      "lowest_price": 25.99,
      "currency": "USD"
    }
  ],
  "total": 1
}
```

**add / remove / sync report:**

```json
{
  "summary": {
    "total_input": 1,
    "added": 1,
    "removed": 0,
    "skipped": 0,
    "errors": 0
  },
  "actions": [
    {
      "action": "add",
      "artist": "Radiohead",
      "title": "OK Computer",
      "release_id": 7890,
      "master_id": 3425,
      "reason": null,
      "error": null
    }
  ]
}
```

## Output Fields

- **release_id** — Unique Discogs release identifier
- **master_id** — Discogs master release identifier (groups all versions of an album)
- **title** — Album title
- **artist** — Artist name
- **format** — Physical format (Vinyl, CD, Cassette, etc.)
- **year** — Release year
- **country** — Country of release
- **num_for_sale** — Number of copies currently for sale on the marketplace
- **lowest_price** — Lowest listed price for the release
- **currency** — Price currency code
- **instance_id** — Collection-specific instance identifier (for duplicate copies)
- **folder_id** — Collection folder identifier
- **action** — Sync action taken: `add`, `remove`, `skip`, or `error`

## Release Matching

When using `--artist` and `--album`, the tool runs a multi-pass search to find the best Discogs match:

1. **Structured search** — artist, album, format, and year
2. **Relaxed search** — drops format and year constraints
3. **Free text search** — searches `"artist album"` as plain text

Each result is scored 0.0–1.0: 40% artist similarity + 40% title similarity + 10% year match + 10% format match. Results below `--threshold` (default 0.7) are rejected. Lower the threshold for fuzzy matches.

When using `--master-id` or `--release-id`, no search is needed — the ID is used directly.

## Exit Codes

- **0** — Success (all items processed)
- **1** — Partial failure (some items failed)
- **2** — Complete failure (no items processed, or auth/config error)

## Notes

- Authentication supports personal access tokens (default) and OAuth 1.0a. Run `python3 /home/claw/.openclaw/workspace/skills/discogs_sync/discogs-sync.py auth` once.
- The Discogs API is rate-limited to 60 requests/minute for authenticated users. The tool throttles automatically — no manual pacing needed.
- Batch operations are resilient: individual item failures are collected and reported without aborting the entire batch.
- Use `--dry-run` before any sync to preview what would change. This makes no API writes.
- The `--remove-extras` flag on sync commands will remove items from your wantlist/collection that are not in the input file. Use with caution.
- Collection allows multiple instances of the same release (e.g., two copies of the same LP). By default, `collection add` skips duplicates with a message. Use `--allow-duplicate` to add another copy.
- Cache files are stored in `~/.discogs-sync/` alongside `config.json`: `wantlist_cache.json`, `collection_cache.json`, and `marketplace_<type>_<hash>.json` (plus `…_details.json` variants). Delete any of these files to manually clear a stale cache entry.
- Credentials in `~/.discogs-sync/config.json` contain your Discogs tokens. On Linux/macOS, restrict permissions: `chmod 600 ~/.discogs-sync/config.json`. Revoke tokens at https://www.discogs.com/settings/developers if compromised.
