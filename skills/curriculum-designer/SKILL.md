---
name: curriculum-designer
description: "Design customized curricula for PODs with REAL resource links. Staged implementation with checkpointing and fallback logic. Use when user says 'Design curriculum', 'Create curriculum for POD', or 'Build learning plan'."
---

# Curriculum Designer

Design customized curricula for Apni Pathshala PODs with **real YouTube video links**.

**FEATURES:**
- ✅ Staged execution with checkpointing (recovery from failures)
- ✅ YouTube link verification with **fallback logic** (no blank URLs)
- ✅ Context capping per lesson (reduced token usage)
- ✅ Every topic gets a valid video OR search query fallback

---

## ⚡ Quick Start

### How This Skill Works

When invoked, the agent follows a **5-stage workflow** with checkpointing:

| Stage | What Happens | Checkpoint File |
|--------|--------------|-----------------|
| 1 | Gather requirements | `requirements.json` |
| 2 | Research YouTube videos | `research-results.json` |
| 3 | Verify videos + **fallback logic** | `validated-resources.json` |
| 4 | Design curriculum (one lesson at a time) | `curriculum-structure.json` |
| 5 | Create Google Sheet | `final-sheet-url.txt` |

### Checkpoint Behavior
- Each stage saves its output to a checkpoint file
- If checkpoint exists, stage loads it and **skips processing**
- If checkpoint doesn't exist, stage runs from scratch
- Re-running resumes from first **incomplete stage**

---

## Trigger

User message contains:
- **"Design curriculum"** → Start curriculum creation
- **"Create curriculum for [POD name]"** → Start with POD context
- **"Build learning plan"** → Start curriculum creation
- **"Curriculum for [subject/topic]"** → Start with topic context

---

## Target User

This skill is designed for **Madhur** (Academic Associate) who designs curricula for PODs.

---

## Configuration

- **API Keys:** Stored locally in `~/.openclaw/workspace/skills/curriculum-designer/.env` (NOT in git)
- **Output Folder:** `1upJQu-IVmZRJQsNGmJNRzq9IwL67MVL9` (Curriculum Designer)
- **Checkpoint Directory:** `~/.openclaw/workspace/curriculum-designer-checkpoints/`

**YouTube API Key:**
```
YOUTUBE_API_KEY=your_key_here
```

Get from: https://console.cloud.google.com/apis/credentials

---

## Agent Workflow Instructions
## Model Allocation for Stages

**Action:** Use different LLM models for different stages to optimize cost and performance.

### Stage-Specific Model Assignment

| Stage | Recommended Model | Reason |
|--------|------------------|--------|
| Stage 1: Requirements Collection | glm-4.7 | Quick reasoning, sufficient for form filling |
| Stage 2: YouTube Research | **glm-5** | Fast research, needs latest web knowledge |
| Stage 3: Video Validation | glm-4.7 | Pattern matching, simple logic |
| Stage 4: Curriculum Design | **glm-4.7** | Structured generation, cost-effective for lessons |
| Stage 5: Sheet Creation | glm-4.7 | JSON formatting, simple transformations |

### How to Set Models

**Option 1: Specify model when calling agent**
```bash
# Use glm-5 for research stage
agent.chat --model glm-5 --message "Research YouTube videos for..."

# Use glm-4.7 for design stage
agent.chat --model glm-4.7 --message "Generate lesson structure..."
```

**Option 2: Configure in SKILL.md**
Each stage should include model recommendation in its instructions:

```
### Stage 2: Research YouTube Resources

**Action:** Search YouTube for videos based on requirements

**Recommended Model:** glm-5 (fast research, latest web knowledge)

**Why:** Research needs up-to-date information and fast processing.
```

---

## Agent Workflow Instructions

### Stage 1: Gather Requirements

**Action:** Ask the user these questions (from SOP):

#### Basic Information
1. **POD Name** - Which POD is this curriculum for?
2. **Target Audience** - Grade level or age group of students?
3. **Subject Areas** - What subjects/topics should be covered?
4. **Duration** - How long is the program? (e.g., 1 month, 3 months, 6 months)
5. **Frequency** - How many classes per week?
6. **Daily Lab Hours** - How many hours will the lab operate?
7. **Previous Exposure** - Have students done digital learning before?

#### Teacher Context
8. **Teacher Capability** - Can teachers operate computers independently?
9. **Teacher Training Needed** - Do teachers need any training?

#### Learning Outcomes
10. **Learning Area Focus** - Which area(s) to prioritize?
    - Digital Literacy
    - Academic Empowerment
    - Skill Development
    - Employment Readiness
11. **Specific Skills** - What specific skills should students acquire?
12. **Assessment Method** - How will learning be measured?

**Output:** Save to checkpoint as JSON:
```json
{
  "pod_name": "Example POD",
  "target_audience": "Grade 8-10",
  "subject_areas": ["Digital Literacy", "Computer Basics"],
  "duration": "1 month",
  "frequency": "3 days/week",
  "daily_lab_hours": 2,
  "previous_exposure": "None",
  "teacher_capability": "Basic",
  "teacher_training_needed": true,
  "learning_area_focus": ["Digital Literacy"],
  "specific_skills": ["Basic computer operations", "Internet safety"],
  "assessment_method": "Practical exercises and quizzes"
}
```

**Checkpoint:** `~/.openclaw/workspace/curriculum-designer-checkpoints/<timestamp>-<session-id>/requirements.json`

---

### Stage 2: Research YouTube Resources

**Action:** Search YouTube for videos based on requirements

**API:** Use YouTube Data API v3 with key from `.env`

**Search Queries (Default):**
```python
search_queries = [
    "computer basics tutorial hindi beginners",
    "typing practice hindi tutorial",
    "internet browser basics hindi",
    "gmail email tutorial hindi beginners",
    "google docs tutorial hindi",
    "google sheets tutorial hindi",
    "chatgpt tutorial hindi beginners 2024",
    "ai tools for students hindi"
]
```

**Search Parameters:**
- `part=snippet`
- `q=<query>`
- `type=video`
- `maxResults=5`
- `videoDuration=medium` (5-10 minutes preferred)
- `relevanceLanguage=hi` (Hindi preference)

**Output Structure:**
```json
{
  "resources": [
    {
      "topic": "computer basics",
      "videos": [
        {
          "title": "Computer Basics for Beginners in Hindi",
          "channel": "TechGuruji",
          "url": "https://youtube.com/watch?v=ABC123",
          "video_id": "ABC123"
        }
      ]
    }
  ]
}
```

#### Research Summary (Before Validation)

After completing all searches, **summarize the research results** before passing to validation stage.

**Why summarize?**
- Reduces token usage when passing to Stage 3 (validation)
- Provides cleaner input for validation logic
- Allows easy review of what was researched

**Summary Structure:**
```json
{
  "research_summary": {
    "total_searches": 8,
    "topics_researched": [
      "computer basics",
      "typing practice",
      "internet browser basics",
      "gmail email tutorial",
      "google docs tutorial",
      "google sheets tutorial",
      "chatgpt tutorial",
      "ai tools for students"
    ],
    "total_videos_found": 24,
    "video_channels": ["TechGuruji", "LearnWithMe", "DigitalSkills", "HindiTechTutorials"],
    "search_language": "Hindi preference",
    "video_duration_preference": "5-10 minutes",
    "notes": "Most videos from 2023-2024. Good variety of channels. Some topics have fewer results, may need fallback search."
  }
}
```

**Save summary:**
- Append `research_summary` to `research-results.json`
- Validation stage uses summary for context, not raw results

**Checkpoint:** `~/.openclaw/workspace/curriculum-designer-checkpoints/<timestamp>-<session-id>/research-results.json`

---

### Stage 3: Verify Videos + Fallback Logic

**Action:** Verify each video via YouTube oEmbed API. If invalid, retry with alternative search terms.

#### Verification Method

Use oEmbed endpoint (fast, lightweight):
```
https://www.youtube.com/oembed?url=https://youtube.com/watch?v=VIDEO_ID
```

- HTTP 200 = Valid video
- HTTP 404 = Invalid/deleted video
- HTTP 4xx/5xx = Try again (rate limit or temporary error)

#### Fallback Logic (CRITICAL)

For **each topic**, follow this logic:

```
For each video in topic:
  1. Verify via oEmbed
  2. If valid → Add to validated list, done with topic
  3. If invalid → Try next video in topic

If NO valid videos found for topic:
  1. Retry search with alternative queries:
     - Original query + "part 2"
     - Original query + "for students"
     - Original query + "in english" (if Hindi failed)
  2. Verify new results
  3. If still no valid videos → ADD FALLBACK:
     - "search_query": "<original query> tutorial hindi beginners"
     - "fallback_reason": "No valid videos found, please search manually"
```

#### Output Structure (With Fallbacks)

```json
{
  "resources": [
    {
      "topic": "computer basics",
      "video": {
        "title": "Computer Basics for Beginners in Hindi",
        "channel": "TechGuruji",
        "url": "https://youtube.com/watch?v=ABC123",
        "video_id": "ABC123",
        "status": "valid"
      }
    },
    {
      "topic": "advanced excel",
      "fallback": {
        "search_query": "advanced excel tutorial hindi beginners",
        "reason": "No valid videos found after 3 retry attempts"
      }
    }
  ]
}
```

**IMPORTANT:** Every topic MUST have either:
- A valid video URL, OR
- A search query fallback

**Checkpoint:** `~/.openclaw/workspace/curriculum-designer-checkpoints/<timestamp>-<session-id>/validated-resources.json`

---

### Stage 4: Design Curriculum (Context Capping + Summarization)

**Action:** Generate curriculum structure, processing **one lesson at a time** with summarization and context cleanup.

#### How Context Capping + Summarization Works

**Instead of:**
```
Pass entire curriculum (all lessons) to LLM at once → High token usage
```

**Do this:**
```
For each lesson (1, 2, 3, ... N):
  1. Load lesson N context only (this lesson's topic + resources)
  2. Generate lesson content
  3. SUMMARIZE lesson N context
  4. Save lesson + summary to curriculum structure
  5. WIPE lesson N context from memory
  6. Continue to next lesson

When all lessons complete:
  1. Summarize entire curriculum
  2. Save summary to curriculum structure
  3. Save summary to Stage 2 checkpoint (research-results.json)
```

#### Lesson-by-Lesson Process

**For lesson N:**

1. **Load context:**
   - Lesson N topic
   - Lesson N resources (from validated-resources.json)
   - Previous lesson summary (if N > 1)

2. **Generate lesson:**
   - Daily learning objectives
   - Daily assessment
   - Module content
   - YouTube link/fallback

3. **Summarize lesson:**
   - Create concise summary of lesson N
   - Focus on: key skills, tools used, assessment type

4. **Save to curriculum:**
   - Full lesson details
   - Lesson summary (for next lesson's context)

5. **Context cleanup:**
   - Remove lesson N's full context from memory
   - Keep only lesson N's summary for N+1

#### Lesson Summary Template

```json
{
  "lesson_number": 1,
  "summary": "Students learned basic computer components, mouse/keyboard operations, and system navigation. Introduced primary computer parts and basic troubleshooting. Assessment involved identifying components and practicing typing.",
  "key_skills": [
    "Identifying computer parts",
    "Mouse and keyboard basics",
    "System navigation"
  ],
  "tools_used": ["Computer", "Mouse", "Keyboard"],
  "assessment_type": "Practical exercise and observation"
}
```

#### Lesson Generation Template

For each lesson, generate:

| Field | Description |
|--------|-------------|
| Day | Lesson number (1, 2, 3, ...) |
| Subject | Subject area / Learning area |
| Module | Module/Topic name |
| Daily Learning Objectives | What students learn that day |
| Daily Assessment | How to assess understanding |
| YouTube Link | Valid video URL OR search query fallback |
| YouTube Title | Video title (if applicable) |
| Tools Used | Required software/platforms |
| Fallback Search Query | Search query if no valid video (or blank) |
| **Lesson Summary** | **Concise summary for next lesson's context** |

#### Sample Lesson Output (With Summary)

```json
{
  "day": 1,
  "subject": "Digital Literacy",
  "module": "Module 1: Introduction to Computers",
  "daily_learning_objectives": "Understand basic computer components, learn to use mouse and keyboard",
  "daily_assessment": "Practical exercise: Identify computer parts, practice typing",
  "youtube_link": "https://youtube.com/watch?v=ABC123",
  "youtube_title": "Computer Basics for Beginners in Hindi",
  "tools_used": "Computer, Mouse, Keyboard",
  "fallback_search_query": "",
  "lesson_summary": {
    "summary": "Students learned basic computer components, mouse/keyboard operations, and system navigation.",
    "key_skills": ["Identifying computer parts", "Mouse and keyboard basics", "System navigation"],
    "tools_used": ["Computer", "Mouse", "Keyboard"],
    "assessment_type": "Practical exercise and observation"
  }
}
```

#### With Fallback Example

```json
{
  "day": 5,
  "subject": "Skill Development",
  "module": "Module 5: Advanced Spreadsheets",
  "daily_learning_objectives": "Learn Excel formulas and data analysis",
  "daily_assessment": "Create a budget spreadsheet using formulas",
  "youtube_link": "",
  "youtube_title": "",
  "tools_used": "Google Sheets",
  "fallback_search_query": "advanced excel formulas tutorial hindi beginners",
  "lesson_summary": {
    "summary": "Students advanced from basic Google Sheets to formulas and data analysis. Learned SUM, AVERAGE, IF functions, and chart creation.",
    "key_skills": ["Google Sheets formulas", "Data analysis basics", "Chart creation"],
    "tools_used": ["Google Sheets"],
    "assessment_type": "Project-based: Budget spreadsheet"
  }
}
```

#### Final Curriculum Summary (When All Lessons Complete)

After generating all lessons:

1. **Summarize entire curriculum:**
   - Total lessons
   - Subject areas covered
   - Key skills progression
   - Assessment approach
   - Tools/software used

2. **Save to curriculum structure:**

```json
{
  "curriculum_summary": {
    "total_lessons": 12,
    "duration": "1 month",
    "frequency": "3 days/week",
    "subject_areas": ["Digital Literacy", "Skill Development"],
    "skills_progression": [
      "Week 1: Computer basics and navigation",
      "Week 2: Internet and email fundamentals",
      "Week 3: Document creation and editing",
      "Week 4: Spreadsheets and data analysis"
    ],
    "assessment_methods": ["Practical exercises", "Quizzes", "Projects"],
    "tools_used": ["Computer", "Google Docs", "Google Sheets", "YouTube videos"],
    "learning_outcomes": "Students will gain basic computer literacy, internet safety awareness, and productivity tool proficiency."
  }
}
```

3. **Update Stage 2 checkpoint:**
   - Add `curriculum_summary` field to `research-results.json`
   - This keeps summary alongside research results for reference

**Checkpoint:** `~/.openclaw/workspace/curriculum-designer-checkpoints/<timestamp>-<session-id>/curriculum-structure.json`

**Also updates:** `~/.openclaw/workspace/curriculum-designer-checkpoints/<timestamp>-<session-id>/research-results.json` (adds curriculum_summary)

---

### Stage 5: Create Google Sheet

**Action:** Create Google Sheet with curriculum data using gog CLI.

#### Step 1: Create Sheet
```bash
# Use gog CLI to create new spreadsheet
SHEET_ID=$(gog drive spreadsheet create \
  --name "Curriculum_[POD]_[YYYY-MM-DD]" \
  --parent-folder "$GOG_FOLDER_ID" \
  --json | python3 -c "import sys, json; print(json.load(sys.stdin).get('id', ''))")

echo "Sheet ID: $SHEET_ID"
```

#### Step 2: Add Headers
```bash
# Add header row
gog sheets update "$SHEET_ID" "Sheet1!A1:H1" \
  --values-json '[["Day","Subject","Module","Daily Learning Objectives","Daily Assessment","YouTube Link","YouTube Title","Tools Used","Fallback Search Query"]]'
```

#### Step 3: Populate with Lessons
```bash
# Read curriculum structure and convert to gog format
# For each lesson, create a row array
# Then append all rows at once

# Format each lesson as: [Day, Subject, Module, Objectives, Assessment, URL, Title, Tools, Fallback]
gog sheets append "$SHEET_ID" "Sheet1!A2:H" \
  --values-json '[
    ["1","Digital Literacy","Module 1: Introduction","Understand basic components","Practical exercise","https://youtube.com/watch?v=ABC123","Computer Basics","Computer,Mouse",""],
    ["2","Digital Literacy","Module 2: File Management","Learn to organize files","Create folders","https://youtube.com/watch?v=DEF456","File Management","File Explorer",""],
    ...
  ]' \
  --insert INSERT_ROWS
```

**Data format:**
- Column A: Day (1, 2, 3, ...)
- Column B: Subject
- Column C: Module
- Column D: Daily Learning Objectives
- Column E: Daily Assessment
- Column F: YouTube Link
- Column G: YouTube Title
- Column H: Tools Used
- Column I: Fallback Search Query

**Validation:**
- One row per lesson
- Include fallback search queries (if any)
- Ensure no blank YouTube Links OR populated Fallback Search Query

#### Step 4: Share Sheet
```bash
# ⚠️ CRITICAL: Always share with public view access
gog drive share "$SHEET_ID" --to anyone --role reader
```

#### Step 5: Save URL
```bash
# Construct public URL and save
PUBLIC_URL="https://docs.google.com/spreadsheets/d/${SHEET_ID}"
echo "$PUBLIC_URL" > "<checkpoint-dir>/final-sheet-url.txt"
```

**Checkpoint:** `~/.openclaw/workspace/curriculum-designer-checkpoints/<timestamp>-<session-id>/final-sheet-url.txt`

---

## Learning Areas Framework

| Learning Area | Focus |
|---------------|-------|
| Digital Literacy | Basic computer skills, internet safety, AI tools |
| Academic Empowerment | Study skills, exam prep, note-taking |
| Skill Development | Programming, design, content creation |
| Employment Readiness | Resume, communication, job skills |

---

## Video Selection Criteria

- ✅ **5-10 minutes max** - keeps engagement high
- ✅ **Clear explanations** - no jargon-heavy content
- ✅ **Hindi or bilingual** - accessible for all students
- ✅ **Recent content** - prefer 2023+ videos
- ❌ **Long lectures** - students lose interest
- ❌ **Advanced content** - match to target audience level

---

## Important Guidelines

### ⚠️ CRITICAL: Sharing Permissions
- **ALWAYS share sheet** with `--to anyone --role reader` before returning link
- **NEVER return a restricted link** - user cannot view it
- Command: `gog drive share <SHEET_ID> --to anyone --role reader`

### ⚠️ CRITICAL: No Blank URLs
- Every topic MUST have either:
  - A valid YouTube URL, OR
  - A search query fallback
- Never leave both fields blank

### Assessment Design
- **Formative** (daily): Quick quizzes, practice exercises, short tasks
- **Summative** (end): Projects, presentations, comprehensive tests
- Keep assessments **practical and hands-on**

---

## Folder Reference

| Resource | Link |
|----------|------|
| Curriculum Designer Folder | `https://drive.google.com/drive/folders/1upJQu-IVmZRJQsNGmJNRzq9IwL67MVL9` |
| Example Curriculum (AI Tools) | `https://docs.google.com/spreadsheets/d/1hYC2Q2KlW8dM71biC97RPSvFnxTQa-zN` |
| SOP Document | `https://docs.google.com/document/d/1Y5qetW8S4RWsTg7hycIyujgTwTCFn9VV` |

---

## Security Note

⚠️ **API keys are stored locally in `.env` file - NEVER commit this file to git!**

---

## Future Improvements

1. **Resume from specific stage** - Ability to jump to any stage, not just first failed one

---

## Automatic Checkpoint Cleanup (Cron Job)

### Purpose
Delete checkpoint directories older than 7 days to prevent disk space bloat while keeping recent sessions for debugging.

### Cron Job Configuration

#### Option 1: Add to User Crontab
```bash
# Edit crontab
crontab -e

# Add this line (runs daily at midnight)
0 0 * * * find ~/.openclaw/workspace/curriculum-designer-checkpoints/ -type d -mtime +7 -exec rm -rf {} \;
```

#### Option 2: Using OpenClaw Cron
```bash
# Create cron job via OpenClaw
openclaw cron create \
  --name "checkpoint-cleanup" \
  --schedule "0 0 * * *" \
  --command "find ~/.openclaw/workspace/curriculum-designer-checkpoints/ -type d -mtime +7 -exec rm -rf {} \;" \
  --description "Delete curriculum-designer checkpoints older than 7 days"
```

#### Cron Schedule Options

| Schedule | Crontab Format | Description |
|-----------|----------------|--------------|
| Daily at midnight | `0 0 * * *` | Every day at 00:00 |
| Weekly on Sunday | `0 0 * * 0` | Every Sunday at 00:00 |
| Every 6 hours | `0 */6 * * *` | Every 6 hours (may be too frequent) |
| Twice daily | `0 0,12 * * *` | At 00:00 and 12:00 |

### Verification

After setting up cron, verify it's working:

```bash
# List cron jobs (crontab)
crontab -l

# List cron jobs (OpenClaw)
openclaw cron list
```

### Manual Cleanup Test

Test the cleanup command manually before setting up cron:

```bash
# Dry run (see what would be deleted)
find ~/.openclaw/workspace/curriculum-designer-checkpoints/ -type d -mtime +7 -ls

# Actual cleanup
find ~/.openclaw/workspace/curriculum-designer-checkpoints/ -type d -mtime +7 -exec rm -rf {} \;

# Verify
ls ~/.openclaw/workspace/curriculum-designer-checkpoints/
```

### Notes

- **`-mtime +7`**: Files/directories modified more than 7 days ago
- **`-type d`**: Only directories (sessions), not individual files
- **`-exec rm -rf {} \;`**: Remove directory and all contents
- Checkpoints are preserved after completion for review, then auto-cleaned after 7 days
- Adjust `+7` to a different value if you want different retention period (+3, +14, +30)

---

## Notes

- Always search for REAL video URLs before creating curriculum
- Save curriculum sheets in the designated folder
- Share viewable link at the end
- Consider teacher training needs if curriculum requires new tools
- Checkpoints are preserved after completion for review
- Every topic in final curriculum must have valid video OR search query fallback
