# Knowledge Vault — Dashboard Companion Kit Spec

**Works great in chat alone. Add the Dashboard for the full visual experience.**

This spec defines the visual dashboard for browsing, searching, and managing your Knowledge Vault. Built as a Next.js page that reads from the same database your agent writes to.

---

## Design System

### Color Palette
- **Background:** `#0f172a` (slate-900)
- **Card Background:** `#1e293b` (slate-800)
- **Card Hover:** `#334155` (slate-700)
- **Primary Accent:** `#14b8a6` (teal-500) — links, active states, search highlight
- **Secondary Accent:** `#f97316` (orange-500) — badges, tag counts, CTAs
- **Text Primary:** `#f8fafc` (slate-50)
- **Text Secondary:** `#94a3b8` (slate-400)
- **Success:** `#22c55e` (green-500)
- **Warning:** `#eab308` (yellow-500)
- **Error:** `#ef4444` (red-500)

### Typography
- **Headings:** Inter (700)
- **Body:** Inter (400)
- **Monospace:** JetBrains Mono (code snippets, timestamps)

### Vibe
Premium, modern, dark theme. Feels like a high-end personal research library, not a messy spreadsheet. Clean whitespace, subtle shadows, smooth transitions.

---

## Page Layout

### Top Bar
- **Logo/Title:** "Knowledge Vault" with 📚 icon
- **Search Bar:** Prominent, centered, full-width on mobile. Placeholder: "Search your vault..." Supports natural language queries.
- **Stats Strip:** Inline stats — "47 entries • 12 videos • 8 articles • 3 queued"

### Sidebar (Desktop) / Bottom Sheet (Mobile)
- **Collections List:** Each collection with entry count badge
  - All Items (47)
  - General (32)
  - Work Research (8)
  - Side Projects (5)
  - Read Later (3) — highlighted with orange badge if >0
- **Tag Cloud:** Visual cloud of all tags, sized by frequency. Clickable to filter.
- **Content Type Filter:** Toggleable pills — 📄 Articles, 🎬 Videos, 📑 PDFs, 🐦 Threads, 🎙️ Podcasts, 💻 Repos

### Main Content Area
- **View Toggle:** Grid view (default) | List view
- **Sort:** Newest first (default) | Oldest first | Alphabetical
- **Card Grid:** Responsive masonry/grid layout

---

## Card Component

Each vault entry renders as a card:

```
┌─────────────────────────────────────┐
│ 🎬  VIDEO                    3d ago │
│                                     │
│ Controlling Your Dopamine For       │
│ Motivation, Focus & Satisfaction    │
│                                     │
│ Andrew Huberman • 2:00:14           │
│                                     │
│ Dr. Huberman explains dopamine's    │
│ role in motivation and focus...     │
│                                     │
│ #neuroscience #dopamine #motivation │
│                                     │
│ 📁 health          ✅ Digested      │
└─────────────────────────────────────┘
```

### Card Fields
- **Content type badge** — emoji + label, colored by type
- **Relative date** — "3d ago", "2 weeks ago", etc.
- **Title** — truncated at 2 lines
- **Author/Channel + Duration/Length**
- **Summary snippet** — first 2 lines of executive_summary
- **Tags** — horizontal scroll if many, teal color
- **Collection** — folder icon + name
- **Status** — ✅ Digested | ⏳ Queued | ❌ Failed

### Card Interactions
- **Click** → Opens full detail view
- **Hover** → Subtle elevation + border glow (teal)
- **Long press / right-click** → Context menu: Move to collection, Delete, Re-digest

---

## Full Detail View (Modal or Page)

Clicking a card opens the full entry:

```
← Back to Vault

# Controlling Your Dopamine For Motivation, Focus & Satisfaction
🎬 Video • Andrew Huberman • 2:00:14 • Saved Mar 8, 2026

[Open Original ↗]

## Executive Summary
Dr. Andrew Huberman explains the neuroscience of dopamine...

## Key Takeaways
1. Dopamine drives wanting, not having...
2. Your baseline matters more than peaks...
3. Cold water exposure reliably boosts dopamine...

## Timestamps
⏱️ 00:00 — Introduction
⏱️ 14:32 — The baseline vs. peak framework
⏱️ 42:00 — Cold exposure (the 2.5x study)
...

## Actionable Insights
- Start mornings with sunlight...
- Try 1-3 min cold shower...

## Notable Quotes
> "Dopamine is not about pleasure..." — Andrew Huberman

## Your Notes
good reference for morning routine optimization

---
🏷️ #neuroscience #dopamine #motivation #health #habits
📁 Collection: health
```

### Detail View Actions
- **Edit notes** — inline editable text field
- **Edit tags** — add/remove tags
- **Move collection** — dropdown selector
- **Re-digest** — re-fetch and re-summarize the content
- **Delete** — with confirmation dialog
- **Open original** — external link to source URL

---

## Search Interface

### Search Bar Behavior
- **Instant search** — filters as you type (debounced 300ms)
- **Searches across:** title, executive_summary, key_takeaways, tags, full_text, user_notes
- **Highlight matches** in results with teal background
- **Empty state:** "No results. Try different keywords or browse your collections."

### Search Results
- Same card layout as main grid, but with match highlights
- Show which field matched: "Matched in: key takeaways"

---

## Tag Cloud

- Tags sized proportionally to frequency (min 12px, max 32px)
- Teal color with varying opacity based on frequency
- Click a tag to filter the main grid
- Active tag filter shown as a dismissible pill above the grid

---

## Vault Stats Widget

Compact stats bar or expandable panel:

```
📚 47 entries  •  🎬 12 videos  •  📄 18 articles  •  📑 8 PDFs
🏷️ 89 unique tags  •  ⏳ 3 queued  •  📅 Last: 2h ago
```

---

## Ingestion History

A timeline/activity feed showing recent vault activity:

```
Today
  ✅ 10:32 AM — Digested "How to Do Great Work" (article)
  ✅ 10:28 AM — Digested "Huberman: Dopamine" (video)

Yesterday
  ⏳ 3:15 PM — Queued "React Server Components Deep Dive"
  ✅ 11:00 AM — Digested "Cal Newport: Deep Work" (pdf)
```

---

## Database Schema (Supabase)

```sql
-- Main vault entries table
CREATE TABLE vault_entries (
  id TEXT PRIMARY KEY,                    -- v_20260308_001
  title TEXT NOT NULL,
  url TEXT NOT NULL,
  content_type TEXT NOT NULL,             -- article, video, pdf, tweet, reddit, podcast, github
  author TEXT,
  source_date DATE,
  ingested_date DATE NOT NULL DEFAULT CURRENT_DATE,
  duration TEXT,                          -- video/podcast runtime
  executive_summary TEXT,
  key_takeaways JSONB DEFAULT '[]',       -- array of strings
  actionable_insights JSONB DEFAULT '[]', -- array of strings
  timestamps JSONB DEFAULT '[]',          -- array of {time, topic}
  notable_quotes JSONB DEFAULT '[]',      -- array of {quote, speaker}
  tags TEXT[] DEFAULT '{}',               -- postgres array for fast search
  full_text TEXT,                         -- full extracted content
  user_notes TEXT DEFAULT '',
  collection TEXT DEFAULT 'general',
  status TEXT DEFAULT 'digested',         -- digested, queued, failed
  error_reason TEXT,                      -- populated on failure
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Collections table
CREATE TABLE vault_collections (
  name TEXT PRIMARY KEY,
  description TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for fast search
CREATE INDEX idx_vault_tags ON vault_entries USING GIN (tags);
CREATE INDEX idx_vault_content_type ON vault_entries (content_type);
CREATE INDEX idx_vault_collection ON vault_entries (collection);
CREATE INDEX idx_vault_status ON vault_entries (status);
CREATE INDEX idx_vault_ingested ON vault_entries (ingested_date DESC);
CREATE INDEX idx_vault_fulltext ON vault_entries USING GIN (
  to_tsvector('english', coalesce(title, '') || ' ' || coalesce(executive_summary, '') || ' ' || coalesce(full_text, ''))
);

-- Full-text search function
CREATE OR REPLACE FUNCTION search_vault(query TEXT, max_results INT DEFAULT 10)
RETURNS TABLE (
  id TEXT,
  title TEXT,
  content_type TEXT,
  executive_summary TEXT,
  tags TEXT[],
  ingested_date DATE,
  collection TEXT,
  rank REAL
) AS $$
BEGIN
  RETURN QUERY
  SELECT
    v.id, v.title, v.content_type, v.executive_summary,
    v.tags, v.ingested_date, v.collection,
    ts_rank(
      to_tsvector('english', coalesce(v.title, '') || ' ' || coalesce(v.executive_summary, '') || ' ' || coalesce(v.full_text, '')),
      plainto_tsquery('english', query)
    ) AS rank
  FROM vault_entries v
  WHERE
    to_tsvector('english', coalesce(v.title, '') || ' ' || coalesce(v.executive_summary, '') || ' ' || coalesce(v.full_text, ''))
    @@ plainto_tsquery('english', query)
  ORDER BY rank DESC
  LIMIT max_results;
END;
$$ LANGUAGE plpgsql;

-- Default collections
INSERT INTO vault_collections (name, description) VALUES
  ('general', 'Default collection for all entries'),
  ('read-later', 'Queue for unprocessed URLs');

-- RLS policies (if using Supabase auth)
ALTER TABLE vault_entries ENABLE ROW LEVEL SECURITY;
ALTER TABLE vault_collections ENABLE ROW LEVEL SECURITY;
```

---

## API Routes (Next.js)

```
GET    /api/vault              — List entries (supports ?collection=, ?type=, ?tag=, ?status=, ?q=)
GET    /api/vault/[id]         — Get single entry
POST   /api/vault              — Create entry (agent writes here)
PATCH  /api/vault/[id]         — Update entry (notes, tags, collection)
DELETE /api/vault/[id]         — Delete entry

GET    /api/vault/collections  — List collections with counts
POST   /api/vault/collections  — Create collection
DELETE /api/vault/collections/[name] — Delete collection

GET    /api/vault/stats        — Vault statistics
GET    /api/vault/tags         — All tags with counts
GET    /api/vault/search?q=    — Full-text search
GET    /api/vault/history      — Ingestion activity feed
```

---

## Responsive Breakpoints

- **Desktop (≥1024px):** Sidebar + 3-column card grid
- **Tablet (768-1023px):** Collapsible sidebar + 2-column grid
- **Mobile (<768px):** Bottom sheet navigation + single column + search bar prominent

---

## Empty States

- **No entries:** "Your vault is empty. Send a URL to your agent to get started! 🚀"
- **No search results:** "No matches found. Try different keywords or browse your collections."
- **Empty collection:** "This collection is empty. Move items here or send new links."
- **Read later empty:** "Nothing queued. Send a link with 'save for later' to start your reading list."
