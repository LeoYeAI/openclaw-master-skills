# Changelog

## 1.0.3 - 2026-02-10

### Security
- **Path traversal fix** — `output.folder` config now validated against safe directories (~/Documents, ~/Desktop, ~/Downloads, ~/.briefing-room, /tmp). Rejects arbitrary paths like /etc or ~/.ssh.

## 1.0.2 - 2026-02-10

### Added
- **Real-time X/Twitter trends** — `briefing.sh trends` fetches live trending topics from getdaytrends.com
  - Default regions: US, UK, Worldwide (configurable via `trends.regions`)
  - No API key or login required
  - Sub-agent picks newsworthy trends, skips noise, searches for context
- **Web Trends section** — `briefing.sh webtrends` fetches Google Trends RSS
  - Trending searches with traffic volume + news headlines (context built-in!)
  - Default regions: US, UK, Worldwide (configurable via `webtrends.regions`)
  - No API key required (public RSS feed)
- **This Day in History section** — 1-2 interesting events from today's date, no API needed
- **Host personality** — `host.name` config sets the radio host name (default: auto-uses agent's own name)
- **Configurable trend regions** — `trends.regions` and `webtrends.regions` in config
- Auto-detect macOS voice for any language (prefers Enhanced/Premium variants)
- Any language macOS supports now works out of the box
- OpenClaw metadata (`requires.bins`, emoji)

### Changed
- Now 11 sections (was 9): split Social into "Trending on X" + "Web Trends", added "This Day in History"
- X/Twitter section now uses real trend data instead of generic web searches
- Description: "100% Free" — no misleading locality claims
- Description: explicitly states macOS only
- Clarified TTS is fully local (no keys needed)
- Listed all external endpoints (Open-Meteo, Coinbase, Google Trends RSS)
- Documented file paths read/written
- Updated README: no pip packages required (stdlib only)
- Removed unused color variables from briefing.sh
- Full User-Agent string for Cloudflare compatibility
- Trend fetch handles errors gracefully (shows "(failed to fetch)" per region)

### Fixed
- Trends command works on macOS (no `grep -P` dependency)

## 1.0.1

### Added
- **Configuration system** — `~/.briefing-room/config.json` with all settings
  - Configurable location (city, lat/lon, timezone) for weather
  - Configurable language (en, sk, de, or any macOS-supported)
  - Per-language voice settings (engine, voice, speed, blend)
  - Configurable sections list
  - Configurable output folder
- **Multi-language TTS** — per-language engine selection
  - English: MLX-Audio Kokoro (fast, local)
  - Slovak: Apple Laura (Enhanced)
  - German: Apple Petra (Premium)
  - Any language: add a `voices` entry + pick from `say -v '?'`
- **Auto-detect TTS engines** — finds mlx-audio and kokoro automatically
- **Config CLI** — `scripts/config.py` with status, get, set, init, reset
- **Voice blend support** — resolves pre-blended .safetensors from HF cache
- **Helper script uses config** — weather/crypto commands read location from config

### Changed
- Removed all hardcoded paths and coordinates
- Weather API uses configured location instead of hardcoded Bratislava
- Local news section uses configured city name
- SKILL.md uses `SKILL_DIR` placeholder for portable paths
- Broke long curl/command lines to prevent horizontal overflow
- Updated README with multi-language examples and config docs

### Fixed
- Long code lines causing horizontal scroll on ClawHub
- Silent config corruption now warns on stderr
- `init` command uses deep_copy to avoid mutating defaults
- `set` CLI verifies write succeeded (no false "Set" on failure)
- Moved `glob` and `shutil` imports to top-level (consistent, errors surface at import)
- Added `sys` to top-level imports (was inline in error handler)

## 1.0.0

- Initial release
- 9 sections: Weather, Social, Local, World, Politics, Tech, Sports, Markets, Crypto
- MLX-Audio Kokoro TTS (English)
- Apple Laura TTS (Slovak)
- DOCX + MP3 output
- Sub-agent pattern for non-blocking generation
