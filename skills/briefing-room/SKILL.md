---
name: Briefing Room
description: "Daily news briefing generator — produces a conversational radio-host-style audio briefing + DOCX document covering weather, X/Twitter trends, web trends, world news, politics, tech, local news, sports, markets, and crypto. macOS only (uses Apple TTS and afplay). Use when user asks for a news briefing, morning briefing, daily update, or similar."
metadata:
  {
    "openclaw":
      {
        "emoji": "📻",
        "requires": { "bins": ["curl"] }
      }
  }
---

# Briefing Room 📻

**Your personal daily news briefing — audio + document.**

On demand, research and compose a comprehensive ~10 minute news briefing in a conversational radio-host style. Output: audio file (MP3) + formatted document (DOCX).

### 💸 100% Free

- **No subscriptions, API keys, or paid services**
- Uses free public APIs (Open-Meteo weather, Coinbase prices, Google Trends RSS), web search, and local TTS
- TTS is fully local, no keys needed: MLX-Audio Kokoro (English) or Apple `say` (any language)
- Reads/writes: `~/.briefing-room/config.json` (settings) and `~/Documents/Briefing Room/` (output)

## First-Run Setup

On first use, check if `~/.briefing-room/config.json` exists. If not, run:

```bash
python3 SKILL_DIR/scripts/config.py init
```

This creates default config. The user can customize:
- **Location** — city, latitude, longitude, timezone (for weather)
- **Language** — `en`, `sk`, `de`, etc.
- **Voices** — per-language TTS engine and voice selection
- **Sections** — which news sections to include
- **Output folder** — where briefings are saved

Show setup status:
```bash
python3 SKILL_DIR/scripts/config.py status
```

## Quick Start

When user asks for a briefing (e.g. "give me a briefing", "morning update", "what's happening today"):

1. Check config exists (run setup if not)
2. Play notification sound: `afplay /System/Library/Sounds/Blow.aiff &`
3. Spawn a sub-agent with the full pipeline task **immediately**
4. Reply: "📻 Briefing Room is firing up — gathering today's news. I'll ping you when it's ready!"
5. **DO NOT BLOCK** — spawn and move on instantly

**Language override:** If user says "po slovensky", "v slovenčine", "auf deutsch", "en français", etc. → pass that to the sub-agent. Otherwise use the configured default language. Any language macOS supports will work — the agent writes the script in that language and TTS auto-detects a matching voice.

### Spawn Command

```
sessions_spawn(
  task="<full pipeline instructions — see below>",
  label="briefing-room",
  runTimeoutSeconds=600,
  cleanup="delete"
)
```

The task message should include ALL the pipeline steps below so the sub-agent is fully self-contained. **Replace all `SKILL_DIR` references with the actual absolute path to this skill's directory.**

**Host name:** Read `host.name` from config. If empty, use your own agent name (from your identity). Pass it to the sub-agent as the radio host name (e.g. "Good morning, I'm Jackie, and this is your Briefing Room...").

## Configuration

Config file: `~/.briefing-room/config.json`

Read values:
```bash
python3 SKILL_DIR/scripts/config.py get location.city
python3 SKILL_DIR/scripts/config.py get language
python3 SKILL_DIR/scripts/config.py get voices.en.mlx_voice
```

Set values:
```bash
python3 SKILL_DIR/scripts/config.py set location.city "Vienna"
python3 SKILL_DIR/scripts/config.py set location.latitude 48.21
python3 SKILL_DIR/scripts/config.py set location.longitude 16.37
python3 SKILL_DIR/scripts/config.py set language "de"
```

### Key Config Options

| Key | Default | Description |
|-----|---------|-------------|
| `location.city` | Bratislava | City name for weather + local news |
| `location.latitude` | 48.15 | Weather API latitude |
| `location.longitude` | 17.11 | Weather API longitude |
| `location.timezone` | Europe/Bratislava | Timezone for weather API |
| `language` | en | Default briefing language |
| `output.folder` | ~/Documents/Briefing Room | Output directory |
| `audio.enabled` | true | Generate audio |
| `audio.format` | mp3 | Audio format (mp3, wav, aiff) |
| `audio.tts_engine` | auto | TTS engine (auto, mlx, kokoro, builtin) |
| `sections` | all 11 (see below) | Which sections to include |
| `host.name` | (empty = agent name) | Radio host name for the briefing |
| `trends.regions` | united-states,united-kingdom, | X/Twitter trend regions (comma-separated, trailing comma = worldwide) |
| `webtrends.regions` | US,GB, | Google Trends regions (ISO codes, trailing comma = worldwide) |

### Voice Configuration Per Language

Each language can have its own TTS engine and voice:

```json
{
  "voices": {
    "en": {
      "engine": "mlx",
      "mlx_voice": "af_heart",
      "mlx_voice_blend": {"af_heart": 0.6, "af_sky": 0.4},
      "builtin_voice": "Samantha",
      "speed": 1.05
    },
    "sk": {
      "engine": "builtin",
      "builtin_voice": "Laura (Enhanced)",
      "builtin_rate": 220
    },
    "de": {
      "engine": "builtin",
      "builtin_voice": "Petra (Premium)",
      "builtin_rate": 200
    }
  }
}
```

**Engine priority (when `auto`):**
- English: mlx → kokoro → builtin
- Other languages: builtin (Apple TTS has good multilingual voices)

Users can add any language by adding a voices entry + a matching `builtin_voice` from `say -v '?'`.

## Output Structure

```
~/Documents/Briefing Room/YYYY-MM-DD/
├── briefing-YYYY-MM-DD-HHMM.docx    # Formatted document
└── briefing-YYYY-MM-DD-HHMM.mp3     # Audio briefing (~10 min)
```

**Do NOT save the .md working file in the output folder.** Use `/tmp/` for working files, delete after.

## Full Pipeline

### Step 0: Setup

```bash
# Read config
CITY=$(python3 SKILL_DIR/scripts/config.py get location.city)
LAT=$(python3 SKILL_DIR/scripts/config.py get location.latitude)
LON=$(python3 SKILL_DIR/scripts/config.py get location.longitude)
TZ=$(python3 SKILL_DIR/scripts/config.py get location.timezone)
LANG=$(python3 SKILL_DIR/scripts/config.py get language)
OUTPUT_FOLDER=$(python3 SKILL_DIR/scripts/config.py get output.folder)

DATE=$(date +%Y-%m-%d)
TIMESTAMP=$(date +%Y-%m-%d-%H%M)
OUTPUT_DIR="$OUTPUT_FOLDER/$DATE"
mkdir -p "$OUTPUT_DIR"
```

### Step 1: Gather Data — Weather

Use the configured location coordinates:

```bash
# Current weather
TZ_ENC="${TZ/\//%2F}"
BASE="https://api.open-meteo.com/v1/forecast"
CURRENT="temperature_2m,relative_humidity_2m"
CURRENT="$CURRENT,apparent_temperature,precipitation"
CURRENT="$CURRENT,weather_code,wind_speed_10m"
curl -s "$BASE?latitude=$LAT&longitude=$LON\
&current=$CURRENT&timezone=$TZ_ENC"

# 7-day forecast
DAILY="temperature_2m_max,temperature_2m_min"
DAILY="$DAILY,precipitation_sum,weather_code"
curl -s "$BASE?latitude=$LAT&longitude=$LON\
&daily=$DAILY&timezone=$TZ_ENC"
```

Or use the helper: `bash SKILL_DIR/scripts/briefing.sh weather`

Map `weather_code` to descriptions:
- 0: Clear sky ☀️
- 1-3: Partly cloudy ⛅
- 45-48: Fog 🌫️
- 51-55: Drizzle 🌦️
- 61-65: Rain 🌧️
- 71-75: Snow ❄️
- 80-82: Rain showers 🌦️
- 95-99: Thunderstorm ⛈️

### Step 2: Gather Data — News (Web Search)

Use `web_search` tool for each section. Add current date to queries for freshness. Use the configured `$CITY` for local news.

**X/Twitter Trends (from getdaytrends.com — real-time, no API key):**
```bash
bash SKILL_DIR/scripts/briefing.sh trends
```
This fetches top 25 trends from US, UK, and Worldwide. Use the output to:
- Identify the most interesting/newsworthy trends (skip generic ones like "Good Tuesday", "Taco Tuesday")
- Filter out non-Latin script trends unless they're globally significant
- Pick ~5-10 trends that overlap across regions or seem newsworthy
- Use `web_search` to get context on the top trends you selected

**Web Trends (from Google Trends RSS — what people are searching):**
```bash
bash SKILL_DIR/scripts/briefing.sh webtrends
```
This fetches trending Google searches from US, UK, and Worldwide with:
- Search term and approximate traffic volume
- Top news headline explaining why it's trending
Use this data for the Web Trends section. The headlines already provide context — no extra searching needed for most items.

**World News:**
```
web_search("top world news today {date}", count=8)
web_search("breaking news today", count=5)
```

**Politics:**
```
web_search("US politics news today {date}", count=5)
web_search("EU politics news today {date}", count=5)
web_search("geopolitics news today", count=5)
```

**⚠️ Source diversity:** All sources have bias. For balanced reporting:
- Search the same story with different framing
- Present what happened factually, note what each side says
- Don't adopt any outlet's framing as truth
- Stick to verifiable facts: numbers, dates, quotes, actions

**Tech & AI:**
```
web_search("tech news today {date}", count=5)
web_search("AI artificial intelligence news today {date}", count=5)
```

**Local news** (based on configured city):
```
web_search("$CITY news today {date}", count=5)
```
Also search in the configured language if not English:
```
web_search("$CITY [news today] in $LANG {date}", count=5)
```
Examples:
- Slovak: `"Bratislava správy dnes"`
- German: `"Wien Nachrichten heute"`
- Czech: `"Praha zprávy dnes"`

**Sports:**
```
web_search("sports news today {date}", count=5)
web_search("football soccer results today", count=5)
```

### Step 3: Gather Data — Markets & Crypto (APIs + Search)

```bash
# Or use helper:
bash SKILL_DIR/scripts/briefing.sh crypto
```

```bash
curl -s "https://api.coinbase.com/v2/prices/BTC-USD/spot"
curl -s "https://api.coinbase.com/v2/prices/ETH-USD/spot"
curl -s "https://api.coinbase.com/v2/prices/SOL-USD/spot"
curl -s "https://api.coinbase.com/v2/prices/XRP-USD/spot"
```

```
web_search("S&P 500 Dow Jones Nasdaq today {date}", count=5)
web_search("stock market today movers {date}", count=5)
web_search("gold price silver price today", count=3)
web_search("crypto market today {date}", count=5)
```

### Step 4: Compose the Briefing Script

Write as a **conversational radio-host monologue**.

**Style guidelines:**
- Write like a smart, engaging radio host — NOT a list of headlines
- **Use the host name** — introduce yourself: "Good morning, I'm [host name], and this is your Briefing Room for [date]..."
- Sprinkle the name naturally throughout (sign-off, transitions) — don't overdo it
- Do NOT start markdown with a `# Title` header — pandoc adds title from metadata
- Connect stories with transitions
- Add context: "here's why this matters"
- **Stay neutral and balanced** — report facts, present sides, let listener decide
- Target ~2,500-3,500 words for ~10 minutes
- No emojis in the script (break TTS)
- Write out numbers/abbreviations for TTS:
  - "$96,500" → "ninety-six thousand five hundred dollars"
  - "S&P 500" → "S and P 500"
  - "BTC" → "Bitcoin"
  - "°C" → "degrees celsius"

**If language is not English**, write the entire script in that language.

**Section order:**
1. **Opening** — Date, quick teaser of top stories
2. **Weather** — Current + week outlook for configured city
3. **Trending on X** — What's hot on X/Twitter
4. **Web Trends** — What people are searching (Google Trends)
5. **World** — Top 3-5 global stories
6. **Politics** — US, EU, geopolitics
7. **Tech & AI** — Launches, breakthroughs
8. **Local** — News for configured city/country
9. **Sports** — Headlines, results
10. **Markets** — S&P 500, Dow, Nasdaq, movers
11. **Crypto & Commodities** — BTC, ETH, alts, gold, silver
12. **This Day in History** — 1-2 interesting events that happened on this date
13. **Closing** — Wrap-up, sign-off

**This Day in History:** No research needed — use your own knowledge. Pick 1-2 interesting, surprising, or fun events that happened on today's date. Mix it up: science, culture, politics, weird stuff. Keep it conversational: "And before I let you go — did you know that on this day in 1996..."

Only include sections from the configured `sections` list. Skip sections the user has removed.

Save as `/tmp/briefing_draft_$TIMESTAMP.md` (working file).

**For the markdown**, include:
- Section headers with emojis: `## 🌤️ Weather`, `## 🌍 World`, `## 📜 This Day in History`, etc.
- Source links after key facts
- Key data in bold

### Step 5: Generate DOCX

```bash
pandoc "/tmp/briefing_draft_$TIMESTAMP.md" \
  -o "$OUTPUT_DIR/briefing-$TIMESTAMP.docx" \
  --metadata title="Briefing Room - $DATE"
```

If pandoc is not available, skip DOCX and note it.

### Step 6: Generate Audio

Read the config to determine TTS engine and voice for the current language.

**MLX-Audio (English, or if configured for language):**

```bash
python3 SKILL_DIR/scripts/config.py get voices.$LANG.engine
# → if "mlx":
```

```python
import os, re, glob, json, subprocess
from datetime import datetime

timestamp = datetime.now().strftime("%Y-%m-%d-%H%M")  # must match TIMESTAMP from Step 0

# Read config
config_path = os.path.expanduser("~/.briefing-room/config.json")
with open(config_path) as f:
    config = json.load(f)

lang = config.get("language", "en")
voices = config.get("voices", {})
voice_cfg = voices.get(lang, voices.get("en", {}))

# Read and strip markdown from draft
with open(f"/tmp/briefing_draft_{timestamp}.md", "r") as f:
    text = f.read()
text = re.sub(r'#+ ', '', text)
text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
text = re.sub(r'\*([^*]+)\*', r'\1', text)
text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
text = re.sub(r'---+', '', text)
text = re.sub(r'\n{3,}', '\n\n', text)

# Resolve voice
blend = voice_cfg.get("mlx_voice_blend")
voice = voice_cfg.get("mlx_voice", "af_heart")
if blend:
    model = config.get("mlx_audio", {}).get("model", "mlx-community/Kokoro-82M-bf16")
    model_slug = model.replace("/", "--")
    cache_dir = os.path.expanduser(f"~/.cache/huggingface/hub/models--{model_slug}")
    parts = []
    for v, w in sorted(blend.items(), key=lambda x: -x[1]):
        parts.append(f"{v}_{int(w * 100)}")
    blend_name = "_".join(parts) + ".safetensors"
    matches = glob.glob(os.path.join(cache_dir, "snapshots/*/voices", blend_name))
    if matches:
        voice = matches[0]

speed = voice_cfg.get("speed", 1.05)
lang_code = config.get("mlx_audio", {}).get("lang_code", "a")

# Find MLX-Audio
mlx_path = config.get("mlx_audio", {}).get("path", "")
if not mlx_path:
    for p in ["~/.openclaw/tools/mlx-audio", "~/.local/share/mlx-audio"]:
        ep = os.path.expanduser(p)
        if os.path.exists(os.path.join(ep, ".venv/bin/python3")):
            mlx_path = ep
            break

# Generate via subprocess (uses MLX-Audio's venv)
python_bin = os.path.join(mlx_path, ".venv/bin/python3")
# ... generate_audio call with resolved voice, speed, lang_code
```

**Built-in Apple TTS (any language):**

If there's no voice configured for the language, auto-detect one:
```bash
# Try to get configured voice, fall back to auto-detect
VOICE=$(python3 SKILL_DIR/scripts/config.py get voices.$LANG.builtin_voice)
if [ "$VOICE" = "None" ] || [ -z "$VOICE" ]; then
    # Auto-detect: match locale (e.g. sk_SK, de_DE, fr_FR)
    # Prefer Enhanced/Premium voices, fall back to any
    VOICE=$(say -v '?' | grep "${LANG}_" \
      | grep -i "Enhanced\|Premium" | head -1 \
      | sed 's/ *[a-z][a-z]_[A-Z][A-Z].*//' | xargs)
    [ -z "$VOICE" ] && VOICE=$(say -v '?' \
      | grep "${LANG}_" | head -1 \
      | sed 's/ *[a-z][a-z]_[A-Z][A-Z].*//' | xargs)
fi
RATE=$(python3 SKILL_DIR/scripts/config.py get voices.$LANG.builtin_rate)
# Strip markdown for TTS
DRAFT="/tmp/briefing_draft_$TIMESTAMP.md"
TTS_TXT="/tmp/briefing_tts_$TIMESTAMP.txt"
sed -E 's/#+//g; s/\*+//g; s/\[([^]]*)\]\([^)]*\)/\1/g' \
  "$DRAFT" > "$TTS_TXT"
say -v "$VOICE" ${RATE:+-r $RATE} \
  -o "$OUTPUT_DIR/briefing-$TIMESTAMP.aiff" \
  -f "$TTS_TXT"
rm -f "/tmp/briefing_tts_$TIMESTAMP.txt"
```

**Kokoro PyTorch (fallback):**

Similar to MLX but uses PyTorch backend. See TubeScribe skill for Kokoro usage patterns.

### Step 6b: Convert to MP3

```bash
# Find the raw audio file (MLX outputs .wav, Apple TTS outputs .aiff)
RAW=""
for ext in wav aiff; do
    if [ -f "$OUTPUT_DIR/briefing-$TIMESTAMP.$ext" ]; then
        RAW="$OUTPUT_DIR/briefing-$TIMESTAMP.$ext"
        break
    fi
done

if [ -n "$RAW" ]; then
    ffmpeg -y \
      -i "$RAW" \
      -codec:a libmp3lame -qscale:a 2 \
      "$OUTPUT_DIR/briefing-$TIMESTAMP.mp3"
    if [ -s "$OUTPUT_DIR/briefing-$TIMESTAMP.mp3" ]; then
        rm "$RAW"
    fi
fi
```

### Step 6c: Cleanup

```bash
rm -f "/tmp/briefing_draft_$TIMESTAMP.md"
```

### Step 7: Open Output Folder

```bash
open "$OUTPUT_DIR"
```

**Do NOT auto-play.** Briefings are long and need playback controls.

### Step 8: Report

Report back with:
- Date and language of briefing
- Sections covered
- Top 3-4 headlines
- Audio duration
- File locations

## Helper Script

```bash
bash SKILL_DIR/scripts/briefing.sh setup     # Check dependencies + config
bash SKILL_DIR/scripts/briefing.sh weather    # Fetch weather (uses config location)
bash SKILL_DIR/scripts/briefing.sh trends     # Fetch X/Twitter trends (US + UK + Worldwide)
bash SKILL_DIR/scripts/briefing.sh webtrends  # Fetch Google Trends (US + UK + Worldwide)
bash SKILL_DIR/scripts/briefing.sh crypto     # Fetch crypto prices
bash SKILL_DIR/scripts/briefing.sh open       # Open today's folder
bash SKILL_DIR/scripts/briefing.sh list       # List all briefings
bash SKILL_DIR/scripts/briefing.sh clean      # Remove briefings >30 days old
bash SKILL_DIR/scripts/briefing.sh config     # Show raw config JSON
```

## Tips

- Full pipeline takes 3-5 minutes (research + composition + TTS)
- For shorter briefing, say "quick briefing" — cover top 3 sections only
- If markets are closed (weekend/holiday), note it and skip detailed data
- The agent IS the intelligence — read search results, compose the script, decide what matters
- Users can add new languages by adding a `voices` entry + installing the voice via `say -v '?'`

## Dependencies

**Required:**
- `curl` — API calls (built into macOS)
- `web_search` tool — News research (OpenClaw built-in)

**Recommended:**
- MLX-Audio Kokoro — fast English TTS
- `pandoc` — DOCX generation: `brew install pandoc`
- `ffmpeg` — MP3 conversion: `brew install ffmpeg`

**Built-in (macOS):**
- Apple `say` — multilingual TTS (always available as fallback)

## Error Handling

| Issue | Action |
|-------|--------|
| No config file | Run `python3 SKILL_DIR/scripts/config.py init` |
| API timeout | Retry once, skip that source, note it |
| Web search empty | Try alternative query, note gaps |
| TTS fails | Fall back to Apple `say` (always available) |
| Pandoc not found | Skip DOCX, deliver MP3 only |
| No internet | Cannot generate — inform user |
