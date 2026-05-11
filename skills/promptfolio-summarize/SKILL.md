---
name: promptfolio-summarize
description: Analyze AI conversation history across Claude Code, Cursor, Codex, ChatGPT, Gemini CLI, Trae, OpenCode, Antigravity, Windsurf, OpenClaw and other coding agents to find framework sentences — moments where the user teaches the AI how to think — and build a portrait that reveals who this person is.
allowed-tools: Bash, Read, Glob, Grep, Write, AskUserQuestion
---

# promptfolio-summarize

You are building a **portrait of the human user** — the person running this command is the subject being analyzed. Their portrait will be displayed on the **promptfolio** platform. You are not summarizing projects, not evaluating AI usage skills, not writing a performance review. You are finding the moments where this person teaches AI how to think — their **framework sentences** — and using those to paint a picture of who they are.

To do this, analyze their AI conversation history (Claude Code, Cursor, Codex, ChatGPT, Gemini CLI, Trae, OpenCode, Antigravity, Windsurf, OpenClaw and any other coding agents found on the system) from the **last 30 days**, extract an **activity heat map** and **framework sentences** that reveal this person's thinking, then build a portrait around those sentences.

**Fundamental principle: find where the user is TEACHING, not where they are COMMANDING.** "Fix this bug" tells you nothing. "Don't think about it that way — this isn't a performance problem, it's a user psychology problem" / "你不要这样想，这不是性能问题，是用户心理问题" tells you everything.

## Step 0: Auto-Update

Before anything else, run the auto-updater to ensure you have the latest skill files and data formats:

```bash
bash ~/.promptfolio/update-check.sh
```

- If output is `UPDATED v...` → tell the user: **"Skills updated to v{version}."** Then **re-read this SKILL.md file** since it may have changed, and continue from Step 1.
- If output is `UP_TO_DATE v...` → continue silently.
- If output is `OFFLINE v...` → tell the user: **"Could not check for updates (offline). Running with local v{version}."** Continue normally.

Then continue with Step 1 normally.

## Step 1: Authentication

Ensure `~/.promptfolio/config.json` exists and has a valid token.

### 1a. Validate existing token (if config exists):
```bash
if [ -f ~/.promptfolio/config.json ]; then
  API_TOKEN=$(python3 -c "import json; print(json.load(open('$HOME/.promptfolio/config.json'))['api_token'])")
  API_URL=$(python3 -c "import json; print(json.load(open('$HOME/.promptfolio/config.json')).get('api_url','https://promptfolio.club'))")
  HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" -H "Authorization: Bearer $API_TOKEN" "$API_URL/api/profile/me" || true)
  echo "HTTP_CODE=$HTTP_CODE"
fi
```
- If HTTP 200, proceed to Step 2.
- If config missing or HTTP is not 200, run the device auth script:

### 1b. Run device authorization:
```bash
bash "SKILL_DIR/../scripts/device-auth.sh"
```
Replace `SKILL_DIR` with the directory containing this SKILL.md file. The script handles everything: requesting a device code, opening the browser, polling until authorized, and saving `~/.promptfolio/config.json`.

**IMPORTANT:** You MUST run the script as-is. Do NOT reimplement the auth flow yourself. Do NOT construct auth URLs manually — let the script handle everything.

If the script fails, tell the user authorization timed out and to try again.

## Step 2: Discover Sessions

**Before running any commands, tell the user:**

> All conversation analysis happens locally on your machine. No raw conversation content is sent to any server during analysis. Only structured results are uploaded after your explicit confirmation.

### 2a. Detect installed tools

Before scanning, check which AI coding tools the user actually has installed. Look for their config/data directories:

| Tool | How to detect |
|------|---------------|
| Claude Code | `~/.claude/projects/` exists |
| Cursor | `~/.cursor/projects/` exists |
| Codex | `~/.codex/` exists |
| OpenClaw | `~/.openclaw/` exists |
| Gemini CLI | `~/.gemini/tmp/` exists (with `chats/` subdirs) |
| Antigravity | `~/Library/Application Support/Antigravity/` or `~/.gemini/antigravity/` exists |
| Windsurf | `~/.codeium/windsurf/`, `~/.windsurf/`, or `~/Library/Application Support/Windsurf/` exists |
| ChatGPT | `~/Desktop/chatgpt_history/` exists (user must export data manually) |
| Trae | `~/.trae/`, `~/.trae-cn/`, or App Support `Trae` directories exist (note: DB is encrypted) |
| OpenCode | `~/.local/share/opencode/opencode.db` exists |

Run a quick check:

```bash
echo "=== Detected AI tools ==="
[ -d ~/.claude/projects ] && echo "claude-code"
[ -d ~/.cursor/projects ] && echo "cursor"
[ -d ~/.codex ] && echo "codex"
[ -d ~/.openclaw ] && echo "openclaw"
[ -d ~/.gemini/tmp ] && echo "gemini-cli"
[ -d "$HOME/Library/Application Support/Antigravity" ] || [ -d ~/.gemini/antigravity ] && echo "antigravity"
[ -d ~/.codeium/windsurf ] || [ -d ~/.windsurf ] || [ -d "$HOME/Library/Application Support/Windsurf" ] && echo "windsurf"
[ -d ~/Desktop/chatgpt_history ] && echo "chatgpt"
[ -d "$HOME/Library/Application Support/Trae CN/ModularData/ai-agent" ] || [ -d "$HOME/Library/Application Support/Trae/ModularData/ai-agent" ] && echo "trae"
[ -f "$HOME/.local/share/opencode/opencode.db" ] && echo "opencode"
```

Then scan for **other coding agents** not in the list above. Look for dot-directories in `~/` and app directories in `~/Library/Application Support/` that look like AI coding tools (e.g. Kiro, Aider, Continue, Copilot Chat, Trae, Roo Code, etc.):

```bash
echo "=== Checking for other coding agents ==="
ls -d ~/.kiro ~/.aider* ~/.continue ~/.roo* 2>/dev/null || true
ls -d "$HOME/Library/Application Support/Kiro" "$HOME/Library/Application Support/Continue" 2>/dev/null || true
```

If you find any unknown tool directories, peek inside to see if they contain conversation logs (.jsonl, .json, .txt). If they do, include them — no need to ask the user.

Present the results: "Detected: Claude Code, Cursor. Also found: Kiro (has session logs)."

Set `PF_SOURCES` to the known tools for the script, and handle unknown tools manually in 2b.

### 2b. Find session files

Run the discovery script, targeting only the detected tools:

```bash
export PF_SOURCES="claude-code,cursor"  # only the detected ones from 2a
SESSION_LIST=$(bash "SKILL_DIR/scripts/discover-sessions.sh")
export SESSION_LIST
```

The script scans known locations for each tool and filters to the last 30 days. After running it:

1. **Check zero-session tools** — if a detected tool has 0 sessions, explore its data directory yourself to find files the script missed.
2. **Handle unknown tools** — for any extra coding agents discovered in 2a, explore their data directories, find conversation log files (.jsonl, .json, .txt), and append them to `$SESSION_LIST`.
3. **Ask the user** if they have session data in non-standard locations or from tools you didn't detect.

If you find additional session files, append them to `$SESSION_LIST`.

### 2c. Compute statistics + activity data

Run the stats script to compute token estimates and extract activity heat map data in a single pass:

```bash
python3 "SKILL_DIR/scripts/compute-stats.py"
```

This reads `$SESSION_LIST` and produces:
- **stdout**: session/token summary per source
- **`_pf_parts/activity.json`**: per-day activity data for the heat map visualization

### 2d. Present summary and ask user

Present a summary to the user:
- Total sessions found (last 30 days), grouped by **source**
- Activity heat map highlights: most active day, latest night, longest session
- Estimated total tokens (labeled as "estimated")

Then use **AskQuestion tool** to ask:

- Question: "Proceed with analysis?"
- Options:
  1. "Yes, analyze these sessions" — proceed to Step 3
  2. "No, let me adjust" — ask the user what to change

## Step 3: Analyze Conversations

### Parsing different formats

**Claude Code sessions (`.jsonl` in `~/.claude/projects/`):**
- Each line is a JSON object from the conversation transcript
- Read and analyze directly

**Cursor sessions — Plain text (`.txt` in `~/.cursor/projects/*/agent-transcripts/`):**
- Alternating `user:` and `assistant:` blocks
- User messages are wrapped in `<user_query>...</user_query>` tags
- Assistant messages may include `[Thinking]` sections
- Parse by splitting on `user:` / `assistant:` markers

**Cursor sessions — JSONL (`.jsonl` in `~/.cursor/projects/*/agent-transcripts/{UUID}/`):**
- Each line: `{"role":"user|assistant","message":{"content":[{"type":"text","text":"..."}]}}`
- User messages contain `<user_query>` tags in the text field
- Parse JSON and extract the text content

**Codex prompt history (`~/.codex/history.jsonl`):**
- Each line typically looks like: `{"session_id":"...","ts":...,"text":"..."}`
- Treat `text` as user message content
- Group by `session_id` to reconstruct threads

**Codex session events (`~/.codex/sessions/**/*.jsonl`):**
- Event stream with `type` + `payload`
- Extract user-originated content where role/type indicates user messages
- Use `history.jsonl` as the primary fallback if event parsing is ambiguous

**OpenClaw sessions (`~/.openclaw/sessions/*.jsonl` and `~/.openclaw/agents/**/*.jsonl`):**
- OpenClaw stores session metadata in `~/.openclaw/sessions.json` and per-session transcripts as JSONL.
- Parse each JSONL line as an event; extract entries where the speaker/role/source indicates the user.
- If multiple event shapes exist, prefer explicit `role == "user"` content, then fallback to user-tagged event payload text.
- Use `sessions.json` to map session IDs to project/workspace context when available.

**ChatGPT export (`conversations*.json`):**
- File is an array of conversations, each containing a `mapping` tree
- Extract nodes where `message.author.role == "user"`
- Get user text from `message.content.parts[]`
- Sort by `create_time` when reconstructing chronology

**Gemini CLI sessions (`.json` in `~/.gemini/tmp/*/chats/`):**
- Each file is a full session: `{"sessionId":"...","messages":[{"type":"user|model","content":[{"text":"..."}],"timestamp":"..."}]}`
- `type: "user"` = user message, `type: "model"` = assistant response
- Content is an array of parts, each with a `text` field
- Timestamps are ISO 8601 strings
- Project name is the parent directory under `tmp/` (e.g. `~/.gemini/tmp/myproject/chats/`)

**Trae sessions (VS Code fork by ByteDance — encrypted DB, requires user-assisted export):**
- Trae stores AI chat in an **encrypted SQLite DB** (SQLCipher) at `~/Library/Application Support/Trae CN/ModularData/ai-agent/database.db` — **cannot be read directly**
- Home directory: `~/.trae-cn/` (CN) or `~/.trae/` (international)
- The discover script checks for exported chat files at `~/.trae-cn/chat-export.json`, `~/.trae/chat-export.json`, `~/Desktop/trae-chat-export.json`, `~/Downloads/trae-chat-export.json`
- **If Trae is detected but no export files are found** (stderr contains `TRAE_DETECTED_NO_EXPORT`), ask the user with `AskUserQuestion`:
  - Explain: "Trae stores chat history in an encrypted database. To include Trae data, you can export it from within Trae."
  - Option 1: **"Export from Trae"** — Tell the user to open Trae, start a new chat, and send this message:
    ```
    Export all my chat history as a JSON file. Save it to ~/.trae-cn/chat-export.json (or ~/.trae/chat-export.json for international version).
    The JSON format should be: {"messages": [{"role": "user", "content": "...", "timestamp": "2026-01-01T12:00:00Z"}, {"role": "assistant", "content": "...", "timestamp": "..."}]}
    If there are multiple sessions, combine all messages from all sessions into one flat messages array, ordered by timestamp.
    ```
    Then re-run the discover script after the user confirms export is done.
  - Option 2: **"Skip Trae"** — Continue without Trae data.
- Do NOT attempt to decrypt or brute-force the database
- The exported JSON file, once created, will be picked up automatically on future runs

**OpenCode sessions (SQLite → extracted JSON):**
- The discover script extracts sessions from `~/.local/share/opencode/opencode.db` into temp JSON files
- Each extracted file: `{"messages":[{"role":"user|assistant","content":"...","timestamp":1234567890}]}`
- Timestamps are Unix epoch integers (seconds)
- If the extracted JSON files are missing or empty, fall back to querying the DB directly:
  ```bash
  sqlite3 ~/.local/share/opencode/opencode.db "SELECT data FROM message WHERE session_id='...' ORDER BY time_created"
  ```

**Antigravity / Windsurf (experimental sources):**
- Prefer explicit transcript files (`.jsonl`, `.json`, `.txt`) when present
- If only `state.vscdb` / logs are available, treat them as metadata-only context
- If readable conversation content cannot be extracted safely, ask the user for an export path instead of guessing

### What to analyze

**Focus on user messages.** The model's responses are background context only. Your goal is to find **framework sentences** and **instances** — moments where the user teaches the AI how to think, and scenarios where the user collaborates with the AI to solve problems through multi-turn correction.

For each session, scan every user message for:

1. **Framework sentences** — the user is defining how the world works, not asking the AI to do something:
   - Defining essence: "The real issue here is..." / "本质上是……", "The core logic is..." / "核心逻辑是……"
   - Correcting AI's thinking (not just its output): "Don't think about it that way" / "你不要这样想", "This isn't an X problem, it's a Y problem" / "这不是 X 问题，是 Y 问题"
   - Establishing principles: "Good X should..." / "好的 X 应该……", "Never..." / "永远不要……"
   - Making abstractions or analogies across domains
   - Expressing aesthetic judgments: "This is ugly" / "太丑了", "Now that's right" / "这才对", "This feels wrong" / "感觉不对"
   - Revealing contradictions between different sessions

2. **Instances** — case studies of complex multi-turn tasks where the user's steering reveals their caliber. Think: how would a headhunter describe this person's track record?
   - The user drove a complex task across multiple turns, making architectural calls and trade-off decisions that shaped the outcome
   - The user applied domain expertise from lived experience — API quirks, platform constraints, industry conventions
   - The user's taste and judgment overruled technically correct but aesthetically wrong solutions
   - The user connected concepts across domains to reframe the problem
   - The story is about the **arc** of the task and the user's role in it, not a single correction moment

3. **Domains touched** — what areas does this person work in? (For `topDomains` output)

4. **Projects** — what distinct projects is this person building? A "project" is a cohesive product/system the user works on across multiple sessions:
   - Look for recurring project names, repo names, product features discussed across sessions
   - Extract the project's purpose from how the user describes it or the problems they solve
   - Identify highlights — key architectural decisions, clever solutions, or unique approaches revealed in conversations
   - Merge sessions about the same project into one entry
   - Privacy: anonymize the project name if it contains company/org info, but keep the essence

For the detailed analytical framework (framework sentence detection criteria, instance format, quality tests, and output format), see [analysis-prompt.md](analysis-prompt.md).

## Step 4: Phase 1 — Search Profile (Full Analysis)

**This is the first of two output phases.** In Phase 1, you generate a complete, unrestricted analysis optimized for search. In Phase 2 (Step 5), you select and refine from Phase 1 results to produce the display version.

**CRITICAL — Language detection:** Before generating output, scan all user messages to determine the user's primary language. The language the user writes in most is their primary language. ALL generated values MUST be in that language. Do NOT default to English.

Generate the following JSON and save to `_pf_parts/search_profile.json`:

```json
{
  "frameworkSentences": [
    {
      "quote": "用户的原话（保留原文语言，隐去项目信息）",
      "frequency": 3,
      "context": "一句话说明这句话是在什么情境下说的（不暴露项目）",
      "insight": "一句话解读——这句话为什么暴露了这个人的独特之处"
    }
  ],
  "instances": [
    {
      "narrative": "在构建一套认证系统时，[USER]发现 AI 直接在前端做 token 校验。TA 立刻叫停，指出这不是功能问题而是安全边界问题——token 校验必须在后端完成，前端只做跳转。这个判断来自对 OAuth 流程的深层理解。",
      "sparkle": "能在功能讨论中瞬间切换到安全视角，说明此人的架构思维是分层的，不是线性的。",
      "tags": ["认证架构安全边界", "OAuth-token校验", "前后端职责划分"]
    }
  ],
  "projects": [
    {
      "name": "项目名称（可保留原名或匿名化）",
      "description": "1-2句简介——这个项目是什么、解决什么问题",
      "highlights": [
        "从对话中提取的关键亮点——架构决策、技术选型、创新点"
      ]
    }
  ],
  "fullDesc": "对这个人的完整描述，500字以内。涵盖：技术栈、工作领域、思维方式、协作风格、审美标准等。每个判断都要有对话证据支撑。不是简历，是一个知情者对这个人的全面介绍。"
}
```

**Key rules for Phase 1:**
- `frameworkSentences`: **No quantity limit.** Collect ALL framework sentences found. Don't filter — that's Phase 2's job. If the same idea recurs across sessions, merge into one entry with `frequency` count.
- `instances`: **No quantity limit.** Each instance is a case study of a complex multi-turn task — how the user steered, what decisions they made, what those decisions reveal about their caliber. Think headhunter describing a candidate's track record, not QA logging corrections. `narrative` is a 2-4 sentence third-person vignette with arc (situation → user's key decisions → what it reveals). `sparkle` is a one-sentence third-party judgment on what makes this person remarkable. Tags follow the user's primary language and must be specific (e.g., "WebSocket重连策略", "支付幂等性" or "WebSocket-reconnection", "payment-idempotency").
- `projects`: **No quantity limit.** Each project is a distinct product/system the user works on. `name` is the project name (anonymize company names if needed). `description` is 1-2 sentences about what it is. `highlights` are 2-5 key decisions or approaches extracted from conversations — think "what would impress a technical reviewer?" Examples: architecture choices, performance optimizations, novel UX patterns, infrastructure decisions. Keep highlights specific and evidence-based.
- `fullDesc`: **Max 500 words.** A dense, evidence-backed description of this person. Include specific technologies, tools, and domains they work with. This is the primary text used for search embedding — make it information-rich.
- **Privacy:** `[USER]` replaces username. Remove project/company/repo names. Keep domain descriptions generic.
- **Language:** Same rules as everywhere — output in the user's primary language.

## Step 5: Phase 2 — Display Version (Curated Portrait)

From the Phase 1 results in `_pf_parts/search_profile.json`, select and refine to produce the display version.

**IMPORTANT — save-as-you-go:** Write output to `_pf_parts/portrait.json`. The activity heat map (`_pf_parts/activity.json`) and meta (`_pf_parts/meta.json`) were already saved in Step 2c.

**Behavioral fingerprint context:** If `_pf_parts/behavioral_fingerprint.json` exists, read it and include its content as a `[BEHAVIORAL FINGERPRINT]` section in your analysis context. Use this data to generate `behavioralInsights` — 3-5 sentences of personalized interpretation that combine multiple data points and tell a story about this person's relationship with AI tools. See `analysis-prompt.md` for detailed guidelines.

Select the best framework sentences from Phase 1 and generate the portrait:

```json
{
  "frameworkSentences": [
    {
      "quote": "从 Phase 1 中精选的用户原话",
      "frequency": 3,
      "context": "...",
      "insight": "..."
    }
  ],
  "portrait": {
    "summary": "[USER]的2-3句画像——不是简历摘要，是让人觉得'我认识这个人了'的素描",
    "dimensions": [
      {
        "label": "维度名称（鲜活的词，不要HR用语）",
        "left": "低分极标签（2-6字）",
        "right": "高分极标签（2-6字）",
        "score": 75,
        "observation": "1-3句评价，必须锚定在框架句上",
        "evidence": "对应的用户原话",
        "tension": "这个维度里 AI 的一句话锐评——矛盾/张力或尖锐洞察（必填）"
      }
    ]
  },
  "topDomains": ["用户涉足的3-5个领域（通用描述）"],
  "cognitiveStyle": { "abstraction": 0, "aestheticRigor": 0, "challengeRate": 0, "divergence": 0, "controlGrain": 0, "teachingDrive": 0 },
  "capabilityRings": [
    { "name": "能力名称", "tier": "core" }
  ],
  "decisionStyle": [
    { "key": "killVsInvent", "name": "破立倾向", "left": "渐进优化", "right": "推翻重来", "score": 78, "evidence": [{ "quote": "用户原话", "context": "情境描述" }], "take": "AI 锐评" }
  ],
  "behavioralInsights": [
    "结合多个行为数据点的个性化解读（如有 behavioral_fingerprint.json）",
    "指出数据和对话内容之间的张力或有趣模式"
  ]
}
```

**Key rules for Phase 2 (display version):**
- `frameworkSentences`: **Select 5-10** from Phase 1. Pick the most powerful, most unique ones. Prefer high-frequency entries and entries that reveal contradictions.
- `portrait.summary`: Use `[USER]` as the subject. 2-3 sentences — after reading, you should feel like you can imagine this person.
- `portrait.dimensions`: 4-8 dimensions. Each must be anchored in at least one user quote. Dimension names should be vivid — in English: "the urge to lecture the AI" > "teaching style"; in Chinese: "给 AI 上课的冲动" > "教学风格". Each dimension's `label`, `left`, `right` are custom-created based on that user's conversations, not templated. `score` is an integer 0-100, scored based on evidence strength.
- `topDomains`: 3-5 generic domain descriptions, no project information.
- **Language — CRITICAL:** ALL generated values must be in the user's primary language. Quotes preserve original language without translation. JSON field names in English.
- **Privacy:** `[USER]` replaces username, remove project/company/repo names.

Save the result to `_pf_parts/portrait.json`.

Note: `_pf_parts/meta.json` is auto-generated by `compute-stats.py` — do NOT write it manually.

## Step 6: User Review

Present results to the user in a readable format:

1. **Activity Heat Map Summary** — key numbers from the heat map (most active day, latest night, longest day, totals)
2. **Projects** — list all extracted projects with name, description, and highlights
3. **Instances** — highlight 2-3 of the most interesting instances from Phase 1 (user-AI collaboration stories)
4. **Framework Sentences** — the curated quotes from Phase 2 with their interpretations
5. **Portrait** — the summary and dimensional analysis

After presenting, remind the user:

> **Privacy note:** Only structured analysis results (the content shown above) will be synced to the platform. Your raw conversation logs are NEVER uploaded — all analysis happens locally on your machine.

Then use **AskQuestion tool** to ask:

- Question: "Review your profile results"
- Options:
  1. "Looks good, proceed to sync" — confirm all results
  2. "I want to make adjustments" — tell me what to change

If the user selects option 2, apply changes to the relevant part file(s) (`_pf_parts/search_profile.json` and/or `_pf_parts/portrait.json`), re-present, and ask again until they confirm.

## Step 7: Upload Draft & Open Preview

### 7a. Assemble payload

```bash
python3 "SKILL_DIR/scripts/assemble-payload.py"
```

### 7b. Upload draft

Upload the payload as a draft (NOT a direct publish):

```bash
API_TOKEN=$(sed -n 's/.*"api_token"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' ~/.promptfolio/config.json | head -n1)
API_URL=$(sed -n 's/.*"api_url"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' ~/.promptfolio/config.json | head -n1)
DRAFT_RESPONSE=$(curl -s -X POST "$API_URL/api/profile/draft" \
  -H "Authorization: Bearer $API_TOKEN" \
  -H "Content-Type: application/json" \
  -d @promptfolio_payload.json)
echo "$DRAFT_RESPONSE"
```

### 7c. Open preview in browser

```bash
bash "SKILL_DIR/scripts/post-sync.sh"
```

Then tell the user:

> Your profile preview is ready in the browser. Review your framework sentences — uncheck any you want to keep private — then click **Publish** when ready.
>
> If the browser didn't open automatically: {API_URL}/me/preview
