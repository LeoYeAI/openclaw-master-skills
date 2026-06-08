# Dashboard Add-on Spec — Supercharged Daily Briefing

**Price:** $19 one-time
**Requires:** Supercharged Daily Briefing (free skill) installed and configured

---

## Visual Design

**Theme:** Premium dark mode
- **Background:** Slate/charcoal (`#0f172a` base, `#1e293b` cards)
- **Active/accent:** Teal (`#14b8a6`)
- **Alerts/highlights:** Orange (`#f97316`)
- **Text:** White (`#f8fafc`) primary, slate-400 (`#94a3b8`) secondary
- **Typography:** Inter or system-ui, clean and modern

---

## Layout & Navigation

### Sidebar Navigation
| Nav Item | Icon | Description |
|----------|------|-------------|
| Today's Brief | ☀️ | Current day's briefing (default view) |
| Archive | 📁 | Browse all past briefings by date |
| Topic Radar | 🔮 | Topic coverage analytics and trends |
| Source Health | 📡 | Source status, reliability, and management |
| Settings | ⚙️ | Topics, schedule, format preferences |

---

## Page Specifications

### 1. Today's Brief (Main Stage)

**Layout:** Bento-box grid

**Components:**
- **Hero Card** (full width, top): Executive Summary — the 3 macro bullets, large text, teal left-border accent
- **Topic Cards** (2-column grid): One card per topic, showing the top stories with headlines, synthesis, and source badges
- **Radar Card** (full width, bottom): The Radar section with orange accent dots for each signal item
- **Metadata Bar** (subtle, bottom): Generated at [time], [N] sources checked, [N] stories processed

**Interactions:**
- Click any story → expands to show full synthesis + all source links
- Click a source badge → navigates to Source Health panel for that source
- Click "Deep Dive" → opens the primary source URL in a new tab

### 2. Archive

**Layout:** Calendar + list hybrid

**Components:**
- **Month Calendar View:** Visual heatmap showing which days have briefings (teal dots). Days with more stories = brighter dot.
- **Briefing List:** Click a date → see the full briefing rendered in the same bento-box format as Today's Brief
- **Search Bar:** Full-text search across all archived briefings. Returns matching stories with date, topic, and snippet.
- **Export:** Download any briefing as PDF or Markdown

**Interactions:**
- Date picker for navigation
- Filter by topic
- "Compare" mode: view two briefings side-by-side

### 3. Topic Radar

**Layout:** Analytics dashboard

**Components:**
- **Topic Coverage Chart** (bar chart): Stories per topic per week, stacked by source. Shows which topics are getting the most/least coverage.
- **Topic Trend Lines** (line chart): Story volume per topic over time (last 30/60/90 days). Spot emerging trends or declining relevance.
- **Topic Weight Sliders:** Interactive sliders to adjust topic weights. Changes save to `config/briefing-config.json`.
- **Topic Manager:** Add/remove topics with one click. Shows source count per topic.
- **Coverage Gaps:** Alerts when a topic has had fewer than 2 stories for 3+ consecutive briefings — "Your Cybersecurity coverage is thin. Want me to discover more sources?"

### 4. Source Health

**Layout:** Status panel

**Components:**
- **Source Status Grid:** Cards for each source showing:
  - Name and type badge (RSS, Blog, Newsletter, etc.)
  - Topic assignment
  - Reliability score (color-coded: green > 0.8, yellow 0.5-0.8, red < 0.5)
  - Last fetched timestamp with relative time ("2 hours ago")
  - Consecutive failures count (if any)
  - Active/paused status toggle
- **Source Timeline** (sparkline per source): Fetch success/failure over the last 30 days
- **Health Summary Bar:** "12 active sources | 1 warning | 0 critical"
- **Actions:** Deactivate, reactivate, ban domain, test fetch (runs a one-off fetch and shows result)

### 5. Settings

**Components:**
- **Topics:** List with add/remove/reorder
- **Schedule:** Time picker, day selector, timezone dropdown, active toggle
- **Format:** Sliders for max items per topic, radar items, executive summary bullets
- **Banned Domains:** List with add/remove
- **Data Management:** Export all data as JSON, clear archive, reset sources

---

## Database Schema

For dashboard persistence (Supabase/Postgres or local SQLite):

### Tables

```sql
-- Briefing archive
CREATE TABLE briefings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    date DATE NOT NULL UNIQUE,
    generated_at TIMESTAMPTZ NOT NULL,
    executive_summary TEXT NOT NULL,
    stories_count INTEGER NOT NULL DEFAULT 0,
    radar_items_count INTEGER NOT NULL DEFAULT 0,
    topics_covered TEXT[] NOT NULL DEFAULT '{}',
    sources_used TEXT[] NOT NULL DEFAULT '{}',
    feedback TEXT,
    raw_markdown TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_briefings_date ON briefings(date DESC);

-- Stories (individual items within briefings)
CREATE TABLE briefing_stories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    briefing_id UUID NOT NULL REFERENCES briefings(id) ON DELETE CASCADE,
    topic TEXT NOT NULL,
    headline TEXT NOT NULL,
    synthesis TEXT NOT NULL,
    source_names TEXT[] NOT NULL DEFAULT '{}',
    primary_url TEXT,
    section TEXT NOT NULL CHECK (section IN ('deep_dive', 'radar')),
    rank INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_stories_briefing ON briefing_stories(briefing_id);
CREATE INDEX idx_stories_topic ON briefing_stories(topic);

-- Sources
CREATE TABLE briefing_sources (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    url TEXT NOT NULL,
    feed_url TEXT,
    type TEXT NOT NULL CHECK (type IN ('rss', 'blog', 'newsletter', 'government', 'social', 'api')),
    topic TEXT NOT NULL,
    reliability_score REAL NOT NULL DEFAULT 0.7,
    discovered_date DATE NOT NULL,
    last_fetched TIMESTAMPTZ,
    last_success BOOLEAN DEFAULT TRUE,
    fetch_failures INTEGER DEFAULT 0,
    user_added BOOLEAN DEFAULT FALSE,
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_sources_topic ON briefing_sources(topic);
CREATE INDEX idx_sources_active ON briefing_sources(active);

-- Feedback
CREATE TABLE briefing_feedback (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    date DATE NOT NULL,
    type TEXT NOT NULL CHECK (type IN ('positive', 'negative', 'topic_increase', 'topic_reduce', 'source_deactivate', 'format_change')),
    comment TEXT,
    action_taken TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_feedback_date ON briefing_feedback(date DESC);

-- Source fetch log (for health sparklines)
CREATE TABLE source_fetch_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id TEXT NOT NULL REFERENCES briefing_sources(id) ON DELETE CASCADE,
    fetched_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    success BOOLEAN NOT NULL,
    status_code INTEGER,
    items_found INTEGER DEFAULT 0,
    error_message TEXT
);

CREATE INDEX idx_fetch_log_source ON source_fetch_log(source_id, fetched_at DESC);
```

### Views

```sql
-- Source health summary
CREATE VIEW source_health AS
SELECT
    s.id,
    s.name,
    s.topic,
    s.reliability_score,
    s.active,
    s.fetch_failures,
    s.last_fetched,
    COUNT(l.id) FILTER (WHERE l.fetched_at > NOW() - INTERVAL '7 days') AS fetches_7d,
    COUNT(l.id) FILTER (WHERE l.success AND l.fetched_at > NOW() - INTERVAL '7 days') AS successes_7d
FROM briefing_sources s
LEFT JOIN source_fetch_log l ON l.source_id = s.id
GROUP BY s.id;

-- Topic coverage stats
CREATE VIEW topic_coverage AS
SELECT
    topic,
    COUNT(*) AS total_stories,
    COUNT(*) FILTER (WHERE b.date > CURRENT_DATE - 7) AS stories_7d,
    COUNT(*) FILTER (WHERE b.date > CURRENT_DATE - 30) AS stories_30d,
    COUNT(DISTINCT bs.briefing_id) AS briefings_with_topic
FROM briefing_stories bs
JOIN briefings b ON b.id = bs.briefing_id
GROUP BY topic;
```

---

## Sync Strategy

The dashboard reads from the same JSON files the skill writes to:
- On page load, sync `data/briefing-sources.json` → `briefing_sources` table
- On page load, sync `data/briefing-archive/*.json` → `briefings` + `briefing_stories` tables
- On page load, sync `data/briefing-feedback.json` → `briefing_feedback` table
- Settings page writes directly to `config/briefing-config.json`

For real-time dashboards, use Supabase Realtime subscriptions on the tables.

---

## Tech Stack Recommendations

- **Framework:** Next.js 14+ (App Router)
- **UI:** Tailwind CSS + shadcn/ui components
- **Charts:** Recharts or Chart.js
- **Database:** Supabase (Postgres) for hosted, SQLite for local-only
- **Deployment:** Vercel
