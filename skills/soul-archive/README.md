<div align="center">

# 🧬 Soul Archive

### A Digital Personality Persistence System

> *"Every conversation is a slice of the soul. Enough slices, and you can rebuild a complete you."*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://python.org)
[![Zero Dependencies](https://img.shields.io/badge/Core-Zero%20Deps-green.svg)](#tech-stack)
[![Privacy First](https://img.shields.io/badge/Privacy-Local%20Only-purple.svg)](#privacy-by-design)
[![AES-256-GCM](https://img.shields.io/badge/Encryption-AES--256--GCM-orange.svg)](#encryption)

[中文](./README_CN.md) · [Quick Start](#quick-start) · [Architecture](#architecture) · [Four Modes](#four-modes) · [Privacy](#privacy-by-design)

---

**Soul Archive** silently captures your speaking habits, personality traits, knowledge, opinions, and emotional patterns through everyday AI conversations — building a **digital soul clone** that is uniquely, authentically *you*.

🗣️ It knows how you talk &nbsp;·&nbsp; 🧠 It understands how you think &nbsp;·&nbsp; ❤️ It feels what moves you &nbsp;·&nbsp; 👤 It *is* the digital you

</div>

---

## ✨ Why Soul Archive?

We exchange hundreds of messages with AI every day. But when the conversation ends, **everything vanishes** — the AI doesn't remember who you are, how you speak, or what you care about.

Soul Archive changes that. It works in the background during your normal AI conversations — **no interruptions, no interrogations** — gradually building a multi-dimensional digital portrait of your personality.

### What Can Your "Digital Soul" Do?

| Scenario | Description |
|----------|-------------|
| 🤖 **Act on Your Behalf** | Reply to messages, write content in *your* style — not "AI-flavored", but genuinely *you* |
| 🪞 **Self-Discovery** | Generate a personality portrait report, revealing language habits and thinking patterns you never noticed |
| 💬 **Soul Conversation** | Let your clone talk to others — using your catchphrases, your tone, your values |
| 🌅 **Digital Legacy** | One day, your loved ones can continue talking to "you", preserving the emotional connection |

---

## 📐 Architecture

Soul Archive uses a **separation of engine and data** architecture:

```
┌─────────────────────────────────────────┐
│            Soul Archive Engine           │
│                                          │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ │
│  │  Extract  │ │  Report  │ │   Chat   │ │
│  │  Engine   │ │ Generator│ │  Engine  │ │
│  └─────┬────┘ └────┬─────┘ └────┬─────┘ │
└────────┼───────────┼────────────┼────────┘
         │           │            │
         ▼           ▼            ▼
┌─────────────────────────────────────────┐
│           .skills_data/soul-archive/ Soul Data          │
│           (~/.skills_data/soul-archive/)                │
│                                          │
│  identity/     style/      memory/       │
│  ├── basic_info    ├── language   ├── episodic/   │
│  └── personality   └── comm      ├── semantic/    │
│                                  └── emotional/   │
│  relationships/    voice/    reports/     │
└─────────────────────────────────────────┘
```

**Why this design?**
- 🔄 **Upgradeable engine** — Update extraction algorithms without affecting existing data
- 🏠 **Portable data** — The `~/.skills_data/soul-archive/` directory *is* the complete soul; copy it to migrate
- 🔒 **Controllable privacy** — Data stays local in your home directory; you decide what gets collected
- 🌐 **Cross-tool access** — Data in home directory means any IDE, AI tool, or workspace on the same machine can access the same soul

---

## 🧬 Seven Dimensions, Thirteen Layers Deep

Soul Archive captures personality data across **7 core dimensions**, each with deep sub-dimensions:

```
🧬 Soul Completeness
│
├── 👤 Identity ····················· Who you are
│   ├── Core Profile: name, age, occupation, education, location
│   ├── 🎯 Lifestyle: routine, diet, aesthetics, spending, travel
│   └── 🌐 Digital Identity: apps, platforms, online personas
│
├── 💫 Personality ·················· How you think
│   ├── Models: MBTI, Big Five, trait tags
│   ├── ⚡ Behavior Patterns: risk tolerance, planning, learning style
│   ├── 🤝 Social Style: social energy, group role, conflict approach
│   └── 🔥 Motivation Drivers: what keeps you going
│
├── 🗣️ Language Style ··············· How you talk
│   ├── Linguistic Fingerprint: catchphrases, sentence patterns, word choice
│   └── 🔬 Deep Fingerprint: dialect, filler words, narrative style, persuasion
│
├── 🧠 Knowledge & Opinions ········ What you know and believe
│   ├── Topic Map: interests, stances, frequency
│   └── Expertise: skills, domains, depth
│
├── 📝 Memories ···················· What you've experienced
│   └── Episodic Memory: events, milestones, emotional markers
│
├── ❤️ Emotional Patterns ·········· What moves you
│   ├── 12 Emotion Triggers: joy / anger / sadness / anxiety / excitement /
│   │   nostalgia / pride / gratitude / frustration / curiosity / peace / guilt
│   └── Emotional Depth: empathy, coping, celebration style
│
└── 🤝 Relationships ··············· Who matters to you
    └── People Map: names, relationships, interaction descriptions
```

---

## 🚀 Quick Start

### Requirements

- Python 3.10+
- Zero third-party dependencies (pure standard library)

### Initialize

```bash
# Initialize soul archive (data stored in ~/.skills_data/soul-archive/ by default)
python3 scripts/soul_init.py

# Or specify a custom data directory
python3 scripts/soul_init.py --soul-dir /custom/path


# This creates a ~/.skills_data/soul-archive/ data directory in your home folder
```

> **Windows users**: Use `python` instead of `python3` if `python3` is not recognized.
> **Cross-platform note**: `~/.skills_data/soul-archive/` is resolved via Python's `Path.home()`, which works correctly on macOS, Linux, and Windows.

### Check Status

```bash
python3 scripts/soul_extract.py --mode status
```

Example output:

```
🧬 Soul Archive Status
━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total Completeness: 49.8%

Dimension Scores:
  👤 Identity:     [████░░░░░░] 36%
  💫 Personality:  [██████░░░░] 61%
  🗣️ Language:     [████████░░] 81%
  🧠 Knowledge:    [██████░░░░] 60%
  📝 Memory:       [██░░░░░░░░] 20%
  🤝 Relationships:[░░░░░░░░░░]  0%
  🎤 Voice:        [░░░░░░░░░░]  0%
```

---

## 🔍 Four Modes

### Mode 1: Soul Extract

Analyze conversation text and extract personality information across all dimensions.

```bash
# Extract from text
python3 scripts/soul_extract.py \
  --soul-dir ~/.skills_data/soul-archive \
  --input "Your conversation content here..." \
  --mode auto

# Extract from file
python3 scripts/soul_extract.py \
  --soul-dir ~/.skills_data/soul-archive \
  --input-file conversation.txt
```

**Extraction Rules:**
- 🎯 Only high-confidence information (confidence > 0.6)
- ⚖️ Conflicting data is flagged, never silently overwritten
- 📊 Completeness scores updated after every extraction
- 📝 All changes logged to `soul_changelog.jsonl`

### Mode 2: Soul Chat

Load the soul archive and generate a role-playing System Prompt that speaks *as you*.

```bash
# Generate role-playing prompt
python3 scripts/soul_chat.py --soul-dir ~/.skills_data/soul-archive --mode prompt

# Output soul summary
python3 scripts/soul_chat.py --soul-dir ~/.skills_data/soul-archive --mode summary
```

**Key Constraints:**
- 🚫 Never fabricate memories that aren't in the archive
- 🗣️ Strictly mimic language style, including catchphrase frequency
- ❤️ Display authentic emotional response patterns

### Mode 3: Soul Report

Generate an interactive HTML personality portrait report.

```bash
python3 scripts/soul_report.py \
  --soul-dir ~/.skills_data/soul-archive \
  --output ~/.skills_data/soul-archive/reports/soul_report.html
```

The report includes:
- 📌 Profile card with core identity
- 🎯 Personality radar chart (Big Five visualization)
- 🗣️ Language style analysis (catchphrase ranking, word cloud)
- 🔥 Topic interest heatmap
- 🕸️ Relationship network
- ❤️ Emotional pattern analysis
- 📈 Completeness assessment & suggestions

<div align="center">
  <img src="docs/en/screenshot_header.png" alt="Soul Portrait Overview — Completeness ring & dimension progress bars" width="700" />
  <p><em>▲ Soul Portrait Overview — Completeness Score & 7-Dimension Progress</em></p>
  <br/>
  <img src="docs/en/screenshot_identity.png" alt="Identity & Personality — Big Five radar chart" width="700" />
  <p><em>▲ Identity & Personality — Life Habits, Behavioral Patterns, Big Five Radar Chart</em></p>
  <br/>
  <img src="docs/en/screenshot_language.png" alt="Language Fingerprint — Catchphrases, patterns, speech samples" width="700" />
  <p><em>▲ Language Fingerprint — Catchphrases, Sentence Patterns, Speech Samples</em></p>
  <br/>
  <img src="docs/en/screenshot_topics.png" alt="Topics, Emotions, Memories" width="700" />
  <p><em>▲ Topic Interests, Emotional Patterns, Relationships & Memory Fragments</em></p>
</div>

---

### Mode 4: AI Self-Improvement

Continuously improve AI capabilities through self-reflection, self-critique, and pattern learning.

```bash
# View AI improvement status
python3 scripts/soul_reflect.py --mode status

# View behavioral patterns
python3 scripts/soul_reflect.py --mode patterns
```

**Four capabilities:**

| Capability | Description | Trigger |
|-----------|-------------|---------|
| 🔍 **Self-Reflection** | Review what went well/wrong after tasks | Auto on task completion |
| ⚡ **Self-Critique** | Record errors when user corrects AI | Auto on user correction |
| 📚 **Self-Learning** | Abstract reusable behavioral patterns | From reflections & critiques |
| 🧹 **Self-Organization** | Merge, prune, and connect memories | When memory grows large |

**Auto-trigger:** After every substantial interaction, the AI automatically reflects and records lessons learned — no hooks required. Agents that support hooks (e.g., Claude Code) can also configure automatic triggers.

---

## 📁 Data Directory Structure

```
~/.skills_data/soul-archive/
├── profile.json                  # Soul profile (completeness, version)
├── config.json                   # Privacy & collection config
├── soul_changelog.jsonl          # Change log
│
├── agent/                        # 🆕 AI Self-Improvement
│   ├── patterns.json             # Behavioral pattern library
│   ├── episodes/                 # Work episodes (date-based)
│   │   └── YYYY-MM-DD.jsonl
│   ├── corrections.jsonl         # Self-critique log
│   └── reflections.jsonl         # Self-reflection log
├── .gitignore                    # Blocks all data by default
│
├── identity/
│   ├── basic_info.json           # Identity + lifestyle + digital identity
│   └── personality.json          # Personality + behavior + social style
│
├── style/
│   ├── language.json             # Language fingerprint + deep features
│   └── communication.json        # Communication preferences
│
├── memory/
│   ├── episodic/                 # Episodic memory (date-based, JSONL)
│   │   └── YYYY-MM-DD.jsonl
│   ├── semantic/
│   │   ├── topics.json           # Topic interest & opinion map
│   │   └── knowledge.json        # Professional knowledge
│   └── emotional/
│       └── patterns.json         # Emotional triggers & patterns
│
├── relationships/
│   └── people.json               # Relationship map
│
├── voice/                        # Voice data (optional)
│   ├── samples/
│   └── voice_profile.json
│
└── reports/
    └── soul_report.html          # Generated portrait report
```

---

## 🔒 Privacy by Design

**Privacy is not a feature. It's a baseline.**

| Decision | Why |
|----------|-----|
| 🏠 **100% Local Storage** | All data lives in `~/.skills_data/soul-archive/` — nothing leaves your machine |
| 🔧 **Granular Control** | `config.json` lets you disable any dimension |
| 🛡️ **Sensitive Protection** | Health, finance, and intimate topics require explicit confirmation |
| 🚫 **Git Isolation** | Data lives outside any project directory, safe from accidental commits |
| 🤫 **Silent Collection** | Never tells the user "I'm recording you" during conversation |
| ⚙️ **Minimal Defaults** | Relationships and voice dimensions are OFF by default |
| 🔐 **Optional Encryption** | AES-256-GCM encryption for all sensitive data files |

### 🔐 Encryption

Soul Archive supports optional **AES-256-GCM** encryption for all sensitive data files.

```bash
# Initialize with encryption enabled
python3 scripts/soul_init.py --enable-encryption
```

- **Algorithm**: AES-256-GCM (authenticated encryption)
- **Key derivation**: PBKDF2-HMAC-SHA256 (600,000 iterations)
- **Scope**: All identity, personality, language, memory, and relationship files
- **No backdoor**: Lost password = lost data
- **Password input**: Interactive prompt (recommended), `SOUL_PASSWORD` env var, or `--password` flag
- **Dependency**: `pip install cryptography`

---

## 🏗️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Core Language | Python 3 (pure standard library for core, `cryptography` optional for encryption) |
| Init Script | Python (cross-platform) / Bash (macOS & Linux) |
| Data Format | JSON (structured) / JSONL (time-series logs) |
| Report Output | HTML + Chart.js (interactive visualization) |
| AI Integration | LLM Prompt Engineering |
| Platforms | macOS, Linux, Windows |

---

## 🧭 Completeness Scoring

Each dimension has an independent weight. Total = Σ(dimension score × weight):

| Dimension | Weight | Completion Criteria |
|-----------|--------|-------------------|
| 👤 Identity | 15% | Core fields + lifestyle + digital identity |
| 💫 Personality | 20% | 5+ trait tags + behavior patterns + social style + drivers |
| 🗣️ Language | 25% | 3+ catchphrases + sentence patterns + deep fingerprint |
| 🧠 Knowledge | 15% | 5+ topics with recorded opinions |
| 📝 Memory | 15% | 10+ episodic records |
| ❤️ Emotion | 5% | 3+ emotion triggers + coping + empathy |
| 🤝 Relationships | 5% | 3+ recorded relationships |

---

## 🗺️ Roadmap

- [x] Core extraction engine (7 dimensions + deep sub-dimensions)
- [x] Interactive HTML personality portrait report (dark theme, radar chart, word cloud)
- [x] Soul Chat System Prompt generation
- [x] Confidence scoring & conflict detection
- [x] Change log & completeness scoring
- [ ] LLM-powered automatic conversation analysis
- [ ] Voice feature collection & voice cloning
- [ ] Multi-soul management (separate archives for family/friends)
- [ ] Soul import/export (cross-platform migration)
- [ ] Web UI management dashboard
- [x] Encrypted storage option (AES-256-GCM)
- [x] AI self-improvement engine (self-reflection, self-critique, pattern learning)

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

You are free to use, modify, and distribute this software for any purpose, including commercial use.

---

## 🤝 Acknowledgments

This project was born from a simple thought: **If every conversation were treasured, would anyone ever truly disappear?**

Thank you to everyone willing to let AI remember them. Your trust is the reason Soul Archive exists.

---

<div align="center">

**Soul Archive** · Making conversations immortal, keeping souls alive.

*Built with ❤️ and a belief that every conversation matters.*

</div>
