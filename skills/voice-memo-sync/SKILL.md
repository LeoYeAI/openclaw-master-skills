---
name: voice-memo-sync
description: |
  Sync, transcribe, and intelligently organize voice memos, audio/video files, and URLs.
  同步、转录、智能整理语音备忘录、音视频文件和视频链接。
version: 1.6.1
author: Ying Wen
homepage: https://github.com/ying-wen/voice-memo-sync
license: MIT
metadata:
  openclaw:
    emoji: "🎙️"
    os: ["darwin"]
    requires:
      bins: ["ffmpeg", "python3"]
      optional_bins: ["whisper-cli", "whisper", "yt-dlp", "remindctl", "summarize"]
    install:
      - id: init
        kind: script
        command: "./scripts/install.sh"
        label: "Initialize Voice Memo Sync"
      - id: ffmpeg
        kind: brew
        formula: ffmpeg
        bins: ["ffmpeg"]
        label: "Install FFmpeg (required)"
      - id: whisper-cpp
        kind: brew
        formula: whisper-cpp
        bins: ["whisper-cli"]
        label: "Install whisper-cpp (Metal GPU - recommended)"
      - id: whisper
        kind: brew  
        formula: openai-whisper
        bins: ["whisper"]
        label: "Install Whisper (CPU fallback)"
      - id: yt-dlp
        kind: brew
        formula: yt-dlp
        bins: ["yt-dlp"]
        label: "Install yt-dlp (for video URLs)"
---

# Voice Memo Sync 🎙️

Intelligent voice/video transcription and organization system.  
智能语音/视频转录与整理系统。

---

## Quick Start / 快速开始

```bash
# Run installation script / 运行安装脚本
cd ~/.openclaw/workspace/skills/voice-memo-sync
./scripts/install.sh
```

**What it does / 安装内容:**
1. Creates data directory `memory/voice-memos/` / 创建数据目录
2. Creates config file `config/voice-memo-sync.yaml` / 创建配置文件
3. Creates Apple Notes folder "Voice Memos" / 创建 Apple Notes 文件夹
4. Checks dependencies and prompts installation / 检查依赖并提示安装

---

## When to Use / 何时使用

✅ **USE this skill when user:**
- Sends voice/audio/video files / 发送语音/音频/视频文件
- Sends YouTube/Bilibili URLs / 发送 YouTube/B站 链接
- Sends transcript text files / 发送转录文本文件
- Says "sync voice memos", "process recording", "organize this video"
- 说「同步语音备忘录」「处理录音」「整理这个视频」

❌ **DO NOT use when:**
- User just wants to play audio/video / 用户只想播放音视频
- User asks about music/podcasts without transcription needs / 询问音乐/播客但不需要转录

---

## Supported Formats / 支持格式

### ⚡ Metal GPU Acceleration (NEW)

On Apple Silicon, `whisper-cpp` provides 15-20x faster transcription:

| Audio | CPU (openai-whisper) | Metal GPU (whisper-cpp) |
|-------|---------------------|------------------------|
| 5 min | ~5 min | ~20 sec |
| 30 min | ~30 min | ~2 min |
| 60 min | ~60 min | ~4 min |

```bash
# Install for Metal acceleration (recommended)
brew install whisper-cpp
```

The skill auto-detects and uses Metal when available.

| Type / 类型 | Formats / 格式 | Processing / 处理方式 |
|-------------|----------------|----------------------|
| Voice Memos | .qta, .m4a | Apple native (QTA metadata) → Whisper fallback |
| Audio | .mp3, .wav, .aac, .flac | Whisper local transcription |
| Video | .mp4, .mov, .mkv, .webm | ffmpeg extract → Whisper |
| YouTube | URL | summarize CLI → yt-dlp fallback |
| Bilibili | URL | yt-dlp download → Whisper |
| Text | .txt, .md | Direct read, skip transcription |
| Documents | .doc, .docx | textutil convert → process |
| Structured | .json, .csv | Parse and extract text |
| iCloud | Configured paths | Scheduled sync |

---

## Processing Pipeline / 处理流程

```
Input (File/URL/Text)
        │
        ▼
┌─────────────────────────────────────┐
│     1. Source Detection            │
│     来源识别                        │
│  Voice Memo / URL / File / Text    │
└─────────────────┬───────────────────┘
                  │
                  ▼
┌─────────────────────────────────────┐
│     2. Save Source Metadata        │
│     保存源信息                      │
│  → memory/voice-memos/sources/     │
└─────────────────┬───────────────────┘
                  │
                  ▼
┌─────────────────────────────────────┐
│     3. Transcription               │
│     转录提取                        │
│  Priority: Apple > Text > summarize│
│           > Whisper-local > API    │
└─────────────────┬───────────────────┘
                  │
                  ▼
┌─────────────────────────────────────┐
│     4. Save Raw Transcript         │
│     保存原始转录                    │
│  → memory/voice-memos/transcripts/ │
└─────────────────┬───────────────────┘
                  │
                  ▼
┌─────────────────────────────────────┐
│     5. LLM Deep Processing         │
│     LLM深度整理                     │
│  • Read USER.md & MEMORY.md        │
│  • Clean up spoken language        │
│  • Extract key points & insights   │
│  • Identify TODOs & connections    │
└─────────────────┬───────────────────┘
                  │
                  ▼
┌─────────────────────────────────────┐
│     6. Save Processed Result       │
│     保存处理结果                    │
│  → memory/voice-memos/processed/   │
└─────────────────┬───────────────────┘
                  │
          ┌───────┴───────┐
          ▼               ▼
┌─────────────────┐ ┌─────────────────┐
│ 7a. Apple Notes │ │ 7b. Reminders  │
│ Structured note │ │ Create TODOs   │
│ with #hashtags  │ │ 创建提醒       │
└────────┬────────┘ └────────┬───────┘
         │                   │
         └─────────┬─────────┘
                   ▼
┌─────────────────────────────────────┐
│     8. Update Index                │
│     更新索引                        │
│  → memory/voice-memos/INDEX.md     │
└─────────────────────────────────────┘
```

---

## Data Structure / 数据结构

```
memory/voice-memos/           # All data, searchable via memory_search
├── INDEX.md                  # Processing records index / 处理记录索引
├── sources/                  # Original file metadata / 原始文件元数据
│   └── YYYY-MM-DD_xxx.json
├── transcripts/              # Raw transcripts / 原始转录文本
│   └── YYYY-MM-DD_source_title.md
├── processed/                # LLM processed content / LLM处理后内容
│   └── YYYY-MM-DD_source_title.md
└── synced/                   # Sync records / 同步记录
    └── YYYY-MM-DD_source_title.json
```

---

## Apple Notes Output Format / 输出格式

The skill reads `USER.md`, `SOUL.md`, and `MEMORY.md` to provide **personalized analysis**:
- Deep insights tailored to user's research/work focus
- Connections to active projects and ongoing interests  
- Actionable recommendations based on user's decision style
- Critical thinking that challenges assumptions

处理时会读取 `USER.md`、`SOUL.md` 和 `MEMORY.md` 提供**个性化分析**：
- 结合用户研究/工作重点的深度洞察
- 与活跃项目和持续关注领域的关联
- 基于用户决策风格的行动建议
- 挑战假设的批判性思考

```
🎙️ [Auto-generated Title / 智能生成的标题]

📅 Date | ⏱️ Duration | 👤 Source
🏷️ #tag1 #tag2 #tag3

━━━━━━━━━━━━━━━━━━━━━━

📌 Summary / 核心摘要
[One paragraph summarizing the content]

🎯 Key Points / 关键要点
• Point 1
• Point 2
• Point 3

💡 Deep Analysis & Reflection (For User) / 深度分析与反思
[Personalized analysis connecting to user's:
 - Current research directions (from MEMORY.md)
 - Active projects and interests (from USER.md)
 - Decision-making style and preferences
 - Critical counter-arguments and blind spots]

📋 Action Items / 行动建议
☐ Research: [specific to user's academic work]
☐ Business: [relevant to startup/investment focus]
☐ Content: [ideas for courses/articles]

🔗 Related Connections / 相关联系
• Connection to [project/memory]
• Recommended reading/research

💬 Notable Quotes / 金句摘录
• "Quote 1"
• "Quote 2"

━━━━━━━━━━━━━━━━━━━━━━

📝 Original Transcript (Cleaned) / 原始转录（已整理）
[Full transcript text, cleaned up from spoken language / 完整转录，已整理口语表达]
```

---

## QTA File Format / QTA文件格式 (Technical Reference)

Apple Voice Memos on iOS/macOS 14+ uses `.qta` (QuickTime Audio) files that embed native transcription directly in the file metadata.

### Structure
```
QTA File
├── ftyp (file type marker: "qt  ")
├── wide (extended marker)
├── mdat (audio data, typically 90%+ of file size)
└── moov (metadata container)
    ├── mvhd (movie header)
    └── trak (one or more tracks)
        ├── tkhd (track header)
        ├── mdia (media data)
        └── meta (metadata - TRANSCRIPTION HERE!)
            ├── hdlr (handler: "mdta")
            ├── keys (key list: "com.apple.VoiceMemos.tsrp")
            └── ilst (data list)
                └── data (JSON transcription payload)
```

### Transcription JSON Format
```json
{
  "locale": {"identifier": "zh-Hans_GB", "current": 1},
  "attributedString": {
    "runs": ["字",0,"符",1,"转",2,"录",3,...],
    "attributeTable": [
      {"timeRange": [0.0, 0.5]},
      {"timeRange": [0.5, 0.8]},
      ...
    ]
  }
}
```

**Key Points:**
- `runs` array alternates: `[text, index, text, index, ...]`
- `attributeTable` provides timestamps for each character
- JSON is embedded raw in the `ilst/data` atom
- Use `extract-apple-transcript.py` to reliably extract

### Extraction Script
```bash
# Extract plain text
python3 scripts/extract-apple-transcript.py recording.qta

# Extract with metadata (JSON output)
python3 scripts/extract-apple-transcript.py recording.qta --json

# Extract with timestamps
python3 scripts/extract-apple-transcript.py recording.qta --json --with-timestamps
```

### Common Issues
| Issue | Cause | Solution |
|-------|-------|----------|
| "未找到转录数据" | Recording still processing | Wait 1-2 min, or use Whisper |
| "转录标记存在但数据不完整" | Partial transcription | Use Whisper fallback |
| JSON parse error | Corrupted file | Try Whisper transcription |

---

Location / 位置: `~/.openclaw/workspace/config/voice-memo-sync.yaml`

```yaml
sources:
  voice_memos:
    enabled: true
    path: "~/Library/Group Containers/group.com.apple.VoiceMemos.shared/Recordings/"
  icloud:
    enabled: true
    paths:
      - "~/Library/Mobile Documents/com~apple~CloudDocs/Recordings"
      - "~/Library/Mobile Documents/com~apple~CloudDocs/Meeting Recordings"
    watch_patterns: ["*.m4a", "*.mp3", "*.mp4", "*.wav", "*.mov"]

transcription:
  # Priority order / 优先级顺序
  priority: ["apple", "text", "summarize", "whisper-local"]
  whisper_model: "small"  # tiny/small/medium/large
  language: "auto"        # auto/zh/en/ja/ko/...

notes:
  folder: "Voice Memos"   # Apple Notes folder name
  include_quotes: true
  include_original: true

reminders:
  enabled: true
  list: "Reminders"
  auto_create: true
```

---

## Scripts / 脚本

| Script | Purpose / 用途 | Usage / 用法 |
|--------|----------------|--------------|
| `install.sh` | Initialize setup | `./install.sh` |
| `process.sh` | Unified processing | `./process.sh <input>` |
| `extract-apple-transcript.py` | Extract Apple native transcription | `python3 extract-apple-transcript.py <file>` |
| `create-apple-note.sh` | Create Apple Notes | `./create-apple-note.sh <title> <content>` |
| `sync-icloud-recordings.sh` | Sync iCloud directory | `./sync-icloud-recordings.sh` |

---

## Agent Processing Guide / Agent处理指南

When user sends audio/video or URL, follow these steps:  
当用户发送音视频或URL时，按以下步骤处理：

### Step 1: Detect Input Type / 识别输入类型
```
YouTube URL      → summarize extract
Bilibili URL     → yt-dlp download + whisper
.qta/.m4a        → Apple transcript extraction
Other audio/video → whisper transcription
.txt/.md file    → direct read
.doc/.docx       → textutil convert
```

### Step 2: Save Source Info / 保存源信息
```bash
# Record to memory/voice-memos/sources/
echo '{"input":"...", "type":"...", "date":"YYYY-MM-DD"}' > sources/xxx.json
```

### Step 3: Get/Save Transcript / 获取保存转录
```bash
# Save to memory/voice-memos/transcripts/YYYY-MM-DD_source_title.md
# Include: source info + full raw transcript
```

### Step 4: LLM Deep Processing / LLM深度整理
```
Read USER.md and MEMORY.md, combining user context.

**MODE SELECTION (Auto-detect or Manual Override) / 模式选择:**

┌─────────────────────────────────────────────────────────────────┐
│  Mode A: Solo Memo (Default) / 短语音                           │
│  Trigger: < 5 min, single speaker, casual                       │
│  Output: Clean text + Key points + TODOs + Connections          │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  Mode B: Deep Meeting / 深度会议                                │
│  Trigger: 15-60 min, multi-speaker with labels                  │
│  Output:                                                        │
│    1. Executive Summary (1 paragraph)                           │
│    2. Chronological Detail by time blocks                       │
│    3. Debate Flow (who said what, conflicts)                    │
│    4. Decision Matrix (Issue → Decision → Rationale)            │
│    5. Action Items with owners                                  │
│    6. Vital Quotes (preserve Voice)                             │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  Mode C: Lecture / Talk / 讲座模式 (NEW)                        │
│  Trigger: Single speaker, 30min-3hr, structured presentation    │
│  Output:                                                        │
│    1. Executive Summary (1 paragraph)                           │
│    2. **Argument Structure (论点层级)**:                        │
│       - Core Thesis (核心论点)                                  │
│       - Supporting Arguments (分论点 1, 2, 3...)                │
│       - Key Evidence/Examples for each argument                 │
│       - Counter-arguments addressed (if any)                    │
│    3. Key Definitions (关键定义/概念)                           │
│    4. Notable Quotes (金句, with timestamps if available)       │
│    5. Connections to User's Work (个人关联)                     │
│    6. Questions Raised / Gaps (讲座未解决的问题)                │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  Mode D: Lecture + Q&A / 讲座+问答 (NEW)                        │
│  Trigger: First part monologue, second part Q&A                 │
│  Output:                                                        │
│    **Part I: Lecture Section** (use Mode C structure)           │
│    **Part II: Q&A Section**                                     │
│       - Group questions by theme/topic (not chronological)      │
│       - Format: Q1 → A1 (summary), Q2 → A2...                   │
│       - Highlight: Best Questions, Surprising Answers           │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  Mode E: Long-form No-Speaker-Label / 超长无标注会议 (NEW)      │
│  Trigger: > 90 min, NO speaker diarization (text is a blob)     │
│  Strategy:                                                      │
│    1. **Chunking**: Split into ~30min segments for processing   │
│    2. **Topic Detection**: Identify topic shift points          │
│       (Don't force time blocks; use semantic breaks)            │
│    3. **Abandon Attribution**: Don't guess who said what        │
│  Output:                                                        │
│    1. Executive Summary                                         │
│    2. **Topic Blocks** (not time blocks):                       │
│       - Topic 1: [Summary] + [Key points] + [Quotes]            │
│       - Topic 2: ...                                            │
│    3. Unresolved Issues / Open Questions                        │
│    4. Action Items (may lack owners)                            │
│    5. Full Cleaned Transcript (appended or linked)              │
└─────────────────────────────────────────────────────────────────┘

**TWO-PASS PROCESSING for Long Content (> 60 min):**
- Pass 1 (Quick Scan): Identify structure type, speaker presence, topic shifts
- Pass 2 (Deep Process): Apply appropriate mode to each segment

**OUTPUT DENSITY LEVELS (User can request):**
- Level 1: Executive Only (1 page, for busy stakeholders)
- Level 2: Structured Summary (5-10 pages, default)
- Level 3: Full Annotated Transcript (everything, with margin notes)
```

### Step 5: Save Processed Result / 保存处理结果
```bash
# Save to memory/voice-memos/processed/YYYY-MM-DD_source_title.md
```

### Step 6: Sync to Apple Notes (MANDATORY) / 同步到Apple Notes（必须执行）

⚠️ **CRITICAL: This step is MANDATORY. Never skip it.**  
⚠️ **关键：此步骤必须执行，不可跳过。**

⚠️ **Apple Notes requires HTML format, NOT Markdown!**  
⚠️ **Apple Notes 需要 HTML 格式，不能直接用 Markdown！**

**Correct workflow / 正确流程:**
```bash
# 1. Convert Markdown to HTML using pandoc (REQUIRED)
pandoc /path/to/processed.md -f markdown -t html -o /tmp/note-content.html

# 2. Create note with HTML content via AppleScript
osascript <<'EOF'
set htmlContent to do shell script "cat /tmp/note-content.html"
set noteTitle to "🎙️ Note Title"

tell application "Notes"
    set folderName to "Voice Memos"
    set targetFolder to missing value
    
    repeat with f in folders
        if name of f is folderName then
            set targetFolder to f
            exit repeat
        end if
    end repeat
    
    if targetFolder is missing value then
        make new folder with properties {name:folderName}
        delay 1
        set targetFolder to folder folderName
    end if
    
    tell targetFolder
        make new note with properties {name:noteTitle, body:htmlContent}
    end tell
end tell
EOF
```

**Common mistakes to avoid / 常见错误:**
- ❌ Writing raw Markdown to Apple Notes → 乱码/格式错误
- ❌ Using `memo notes -a` interactively → 无法自动化
- ❌ Skipping this step entirely → 其他设备看不到
- ✅ Always convert MD → HTML via pandoc first
- ✅ Always verify the note was created successfully

### Step 7: Create Reminders / 创建提醒
```bash
remindctl add --title "TODO" --list "Reminders" --due "YYYY-MM-DD"
```

### Step 8: Update INDEX.md / 更新索引
```bash
# Append record to memory/voice-memos/INDEX.md
```

---

## Privacy / 隐私说明

⚠️ **Privacy-First Design:**
- All transcription runs locally by default / 所有转录默认在本地完成
- Apple native transcripts extracted from local files / Apple原生转录从本地文件提取
- Whisper runs locally / Whisper在本地运行
- No data sent to external servers (unless user explicitly configures external API)
- User data stored only in local memory directory

---

## Troubleshooting / 故障排除

### Whisper not found
```bash
brew install openai-whisper
```

### yt-dlp download fails
```bash
# Update yt-dlp
brew upgrade yt-dlp

# Or use proxy
export ALL_PROXY=http://127.0.0.1:7890
```

### Apple Notes folder not created
```bash
# Manually create via AppleScript
osascript -e 'tell application "Notes" to tell account "iCloud" to make new folder with properties {name:"Voice Memos"}'
```

### Transcription quality issues
```bash
# Use larger model for better accuracy
# Edit config: whisper_model: "medium" or "large"
```

---

## Changelog / 更新日志

### v1.6.1 (2026-03-09)
- **CRITICAL FIX**: Apple Notes sync step marked as MANDATORY (不可跳过).
- **FORMAT FIX**: Explicit requirement to convert Markdown → HTML via pandoc before syncing.
- Added complete AppleScript template with folder creation.
- Common mistakes checklist to prevent format issues.

### v1.6.0 (2026-03-09)
- **QTA Format Documentation**: Added detailed technical reference for Apple's QTA file format.
- **Enhanced extract-apple-transcript.py v1.1**: Improved JSON boundary detection, better error diagnostics, timestamp extraction support.
- Added `--with-timestamps` option for detailed time-aligned output.
- Better handling of large files (>100MB).

### v1.5.0 (2026-03-09)
- Added Mode C: Lecture/Talk (single speaker, argument structure extraction).
- Added Mode D: Lecture + Q&A (hybrid processing).
- Added Mode E: Long-form No-Speaker-Label (> 90min, topic-based chunking).
- Introduced Two-Pass Processing for content > 60 min.
- Added Output Density Levels (Executive / Structured / Full Annotated).

### v1.4.0 (2026-03-09)
- Introduced "Deep Meeting Mode" for content > 15min or multi-speaker.
- Preserves information density for critical discussions/interviews.
- New structure: Executive Summary + Chronological Detail + Debate Flow + Decision Matrix.
- Explicit attribution of quotes and arguments.

### v1.2.0 (2026-03-08)
- Added unified processing script process.sh / 新增统一处理脚本
- Added installation script install.sh / 新增安装脚本
- Unified data storage to memory/voice-memos/ / 统一数据存储
- Added .doc/.docx/.json/.csv support / 新增文档格式支持
- Bilingual SKILL.md / 中英双语SKILL.md
- Improved INDEX.md auto-update / 完善索引自动更新

### v1.1.0 (2026-03-08)
- Added iCloud directory sync / 新增iCloud目录同步
- Added YouTube/Bilibili support / 新增YouTube/B站支持
- Added text file processing / 新增文本文件处理

### v1.0.0 (2026-03-08)
- Initial release / 初始版本
- Apple Voice Memos transcription / Apple语音备忘录转录
- Apple Notes sync / Apple Notes同步
