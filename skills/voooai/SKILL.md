---
name: voooai
description: >
  Short drama & webtoon production, text-to-image, image-to-image, storyboard design,
  text-to-video, image-to-video, video edit, style transfer, batch generation, music & soundtrack.
  Describe your creative needs → backend generates workflow → execute → poll status → download results.
  Upload reference files (images, videos, audio) → workflow uses them as input for generation.
  If a node fails → retry that node with adjusted parameters. Complex tasks (short dramas, full ads) may take 3-5 min.
  Your role: relay user requests verbatim to backend. Backend AI (Analyst + Expert + Reviewer) handles all creative decisions.
  Do NOT rewrite prompts, decompose tasks, or construct workflows yourself — just forward and retrieve.
  Requires VOOOAI_ACCESS_KEY (creative operations only, no billing/admin).
  Use when: users request any visual or audio content creation, generation, editing, or modification.
version: 1.0.2
author: VoooAI Team
license: MIT-0
user-invocable: true
metadata:
  {
    "openclaw": {
      "emoji": "🎨",
      "requires": {
        "env": ["VOOOAI_ACCESS_KEY"],
        "bins": ["python3"]
      },
      "primaryEnv": "VOOOAI_ACCESS_KEY",
      "homepage": "https://voooai.com",
      "tags": [
        "image-generation",
        "video-generation",
        "music-generation",
        "image-edit",
        "video-edit",
        "ai-creative",
        "workflow-automation",
        "text-to-image",
        "text-to-video",
        "image-to-image",
        "image-to-video",
        "video-to-video",
        "audio-to-video",
        "style-transfer",
        "nl2workflow",
        "multimedia",
        "talking-head",
        "storyboard",
        "manga",
        "short-drama",
        "digital-human",
        "batch-generation",
        "webtoon",
        "short-form-video",
        "ai-animation",
        "marketing-video"
      ]
    }
  }
---

# VoooAI - NL2Workflow Creative Platform

## 1. Overview

VoooAI is a **multi-media creative platform** with 70+ built-in AI skills. The Agent acts as a **relay** (搬运工) — forwarding user requests to VoooAI's backend, which handles all creative decisions via its multi-role AI system (Analyst + Expert + Reviewer).

**Core Capabilities:**
- **Image Generation**: Text-to-image, image-to-image, style transfer, concept art, storyboards
- **Video Generation**: Text-to-video, image-to-video, video editing, digital human, AI anchor
- **Music Generation**: Full songs, instrumentals, background music, soundtracks
- **Workflow Orchestration**: Multi-step automated pipelines (script → storyboard → video + music)

### 1.1 Who Should Use This Skill?

| User Type | Use Cases |
|-----------|-----------|
| **Content Creators** | Marketing videos, social media content, product showcases, promotional materials |
| **Designers** | Design assets, style variants, visual concepts, mood boards |
| **Studios** | Multi-step creative pipelines (script → storyboard → video + music) |
| **Businesses** | Advertising, e-commerce product videos, corporate training content |
| **Game Developers** | Game art assets, character concept art, cutscene animations |
| **Educators** | Tutorial videos, course illustrations, animated demonstrations |
| **One-Person Companies** | Full-stack content creation (posters, videos, music — all-in-one) |

### 1.2 When NOT to Use This Skill

This skill is **exclusively for creative workflow operations**. The following are explicitly **out of scope**:

- ❌ User account management (registration, login, profile changes)
- ❌ Billing, subscription, or payment operations
- ❌ Admin panel or system configuration
- ❌ Analytics, statistics, or usage data queries
- ❌ Homepage or dashboard features
- ❌ Direct parameter tuning (let the backend AI system handle optimization)

For these operations, direct users to https://voooai.com

## 2. Authentication

### VOOOAI_ACCESS_KEY
- **Source**: User's VoooAI account page at https://voooai.com
- **Format**: `vooai_` prefix + 40 random alphanumeric characters (46 total)
- **Example**: `vooai_abc123def456ghi789jkl012mno345pqrs678`

### Scope (What the Key Allows)
- ✅ Capability discovery (`check_capabilities.py`)
- ✅ File upload (`upload_file.py`)
- ✅ Workflow generation (`generate_workflow.py`)
- ✅ Workflow execution (`execute_workflow.py`, `execute_single_node.py`)
- ✅ Status query (`get_status.py`)
- ✅ Result download (`download_results.py`)

### Scope (What the Key DOES NOT Allow)
- ❌ Billing / payment / subscription management
- ❌ Admin / system administration
- ❌ User account settings / profile changes
- ❌ Analytics / statistics access

### Storage
- Environment variable: `export VOOOAI_ACCESS_KEY="vooai_..."`
- Never hardcode in source code

## 3. Scope and Restrictions

### Allowed Operations
- Capability discovery, file upload, workflow generation/execution, status query, result download

### Forbidden Operations (Explicit Deny List)
If user requests these, inform them to visit voooai.com directly:
- ❌ Homepage / dashboard features
- ❌ User registration / login / authentication
- ❌ Subscription / payment / billing management
- ❌ Admin panel / system administration
- ❌ Analytics / statistics
- ❌ Account settings / profile management

**Content Moderation (Explicit Deny List)**
- ❌ Creating deepfakes or non-consensual facial/voice mimicry
- ❌ Impersonating real individuals without explicit consent
- ❌ Generating political disinformation or election interference content

> **Content Safety Note**: Digital human and talking-head features are intended for legitimate 
> creative use cases (marketing presenters, educational hosts, fictional characters). 
> Users must label AI-generated content per applicable synthetic media regulations.

## 4. Scope Boundaries

This section provides a clear table-based definition of what this skill can and cannot do.

### Supported Operations

| Operation | Supported | Script | Example |
|-----------|-----------|--------|---------|
| Capability discovery | ✅ | check_capabilities.py | Check available skills and points balance |
| File upload | ✅ | upload_file.py | Upload reference image/video/audio (max 200MB) |
| Workflow generation | ✅ | generate_workflow.py | Generate workflow from natural language description |
| Workflow execution | ✅ | execute_workflow.py | Run generated workflow |
| Single node execution | ✅ | execute_single_node.py | Retry specific failed node |
| Status query | ✅ | get_status.py | Check execution progress |
| Result download | ✅ | download_results.py | Download generated files to local |

### Forbidden Operations

| Operation | Reason |
|-----------|--------|
| User authentication / registration | Out of scope — handled by web frontend |
| Payment / billing / subscription | Out of scope — user manages directly at voooai.com |
| Account settings / profile | Out of scope — user manages directly |
| Analytics / usage statistics | Out of scope — not creative workflow |
| Admin panel / system config | Out of scope — admin only |
| Homepage / dashboard features | Out of scope — not workflow related |
| Direct API calls bypassing scripts | Security risk — use provided scripts only |
| Manual workflow JSON construction | Quality risk — use generate_workflow.py only |
| Deepfakes / non-consensual facial or voice mimicry | Content safety — violates ethical guidelines |
| Impersonating real individuals without consent | Content safety — privacy and legal concerns |
| Political disinformation / election interference | Content safety — harmful content prohibition |

## 5. Available Scripts

All scripts located at `{baseDir}/scripts/`. Required env: `VOOOAI_ACCESS_KEY`.

### check_capabilities.py
Discover platform capabilities and points balance.
```bash
python3 {baseDir}/scripts/check_capabilities.py
python3 {baseDir}/scripts/check_capabilities.py --summary
```

### upload_file.py
Upload image/video/audio file (max 200MB).
```bash
python3 {baseDir}/scripts/upload_file.py /path/to/file.png
python3 {baseDir}/scripts/upload_file.py /path/to/video.mp4
```
- Supported: jpg, png, webp, gif, mp4, mov, avi, mkv, webm, mp3, wav, flac, m4a

### generate_workflow.py
Generate workflow from natural language description.
```bash
python3 {baseDir}/scripts/generate_workflow.py "生成一个咖啡产品宣传视频"
python3 {baseDir}/scripts/generate_workflow.py "基于这张图生成视频" --reference-urls https://example.com/ref.jpg
python3 {baseDir}/scripts/generate_workflow.py "生成分镜图" --skill-id storyboard-basic
python3 {baseDir}/scripts/generate_workflow.py "测试描述" --analyze-only  # analysis only
```

### execute_workflow.py
Execute a generated workflow.
```bash
python3 {baseDir}/scripts/execute_workflow.py '{"nodes": [...], "connections": [...]}'
python3 {baseDir}/scripts/execute_workflow.py /path/to/workflow.json
cat workflow.json | python3 {baseDir}/scripts/execute_workflow.py --from-stdin
python3 {baseDir}/scripts/execute_workflow.py workflow.json --set-param node_1.prompt="新提示词"
```

### execute_single_node.py
Execute/retry a single node (for debugging or partial retry).
```bash
python3 {baseDir}/scripts/execute_single_node.py workflow.json --node-id node_1
cat workflow.json | python3 {baseDir}/scripts/execute_single_node.py --from-stdin --node-id node_2
python3 {baseDir}/scripts/execute_single_node.py workflow.json --node-id node_1 --set-param node_1.prompt="修改后的提示词"
```

### get_status.py
Query execution status.
```bash
python3 {baseDir}/scripts/get_status.py exec_abc123                            # single query
python3 {baseDir}/scripts/get_status.py exec_abc123 --poll                     # poll until complete
python3 {baseDir}/scripts/get_status.py exec_abc123 --poll --timeout 600       # custom timeout
```

### download_results.py
Download execution results to local.
```bash
python3 {baseDir}/scripts/download_results.py exec_abc123
python3 {baseDir}/scripts/download_results.py exec_abc123 --output-dir ~/Downloads/project
python3 {baseDir}/scripts/download_results.py exec_abc123 --prefix "storyboard"
python3 {baseDir}/scripts/download_results.py exec_abc123 --no-download        # list URLs only
python3 {baseDir}/scripts/download_results.py --urls https://a.com/1.png       # direct URL download
```

## 6. Usage Patterns

This section describes common trigger patterns to help the Agent understand when and how to invoke VoooAI.

### Pattern 1: Direct Media Generation

**User expressions:**
- "Generate an image of a sunset over mountains"
- "画一只戴眼镜的猫"
- "做个海报宣传我的产品"
- "Create a video of a dancing robot"
- "帮我做首轻松的背景音乐"

**Execution flow:**
```
check_capabilities → generate_workflow → execute_workflow → get_status (poll) → download_results
```

### Pattern 2: Reference-Based Creation

**User expressions:**
- "Based on this image, generate a video"
- "把这张图变成动画"
- "用这首歌做个MV"
- "Convert this sketch to a realistic image"
- "参考这个风格做一组产品图"

**Execution flow:**
```
upload_file → generate_workflow (with --reference-urls) → execute_workflow → get_status (poll) → download_results
```

### Pattern 3: Complex Multi-Step Workflows

**User expressions:**
- "Create a short drama about a detective"
- "帮我做个产品广告，从脚本到成片"
- "一句话生成短剧"
- "Make a complete promotional video with storyboard and music"
- "从剧本到分镜到视频帮我全流程做出来"

**Execution flow:**
```
generate_workflow (backend handles decomposition) → execute_workflow → get_status (poll, may take 3-5+ min) → download_results
```

### Pattern 4: Failure Recovery & Retry

**User expressions:**
- "Retry with different parameters"
- "这个节点重新执行一下"
- "把提示词改一下再试"
- "换个风格重新生成"

**Execution flow:**
```
get_status (identify failed node) → execute_single_node (with --set-param if needed) → get_status (poll) → download_results
```

### Pattern 5: Exploration & Discovery

**User expressions:**
- "What can you generate?"
- "你能做什么？"
- "有哪些创作能力？"
- "Show me available AI skills"
- "我还有多少积分？"

**Execution flow:**
```
check_capabilities → present results to user
```

## 7. Typical Workflows

### Scenario 1: Basic Image/Video Generation
```bash
# 1. Check capabilities and points
python3 {baseDir}/scripts/check_capabilities.py --summary

# 2. Generate workflow (user confirms points_cost before proceeding)
python3 {baseDir}/scripts/generate_workflow.py "一个宇航员在月球上弹吉他"
# → Review estimated_points, ask user to confirm

# 3. Execute workflow
python3 {baseDir}/scripts/execute_workflow.py '<template_data_json>'

# 4. Poll status
python3 {baseDir}/scripts/get_status.py EXEC_ID --poll

# 5. Download results
python3 {baseDir}/scripts/download_results.py EXEC_ID --output-dir ./output
```

### Scenario 2: With Reference Media (URL)
```bash
python3 {baseDir}/scripts/generate_workflow.py "根据这张图生成视频" \
  --reference-urls https://example.com/reference.jpg
# Then execute, poll, download as above
```

### Scenario 3: With Local File Upload
```bash
# 1. Upload local file first
python3 {baseDir}/scripts/upload_file.py /path/to/reference.png
# → Returns file_url

# 2. Generate workflow with uploaded URL
python3 {baseDir}/scripts/generate_workflow.py "基于这张图生成视频" \
  --reference-urls <file_url_from_upload>
# Then execute, poll, download as above
```

### Scenario 4: Failed Node Retry
```bash
# 1. Check which node failed
python3 {baseDir}/scripts/get_status.py EXEC_ID
# → Identify failed node_id from node_statuses

# 2. Retry single node (optionally adjust params)
python3 {baseDir}/scripts/execute_single_node.py workflow.json \
  --node-id failed_node_id \
  --set-param failed_node_id.some_param="adjusted_value"

# 3. Poll new execution
python3 {baseDir}/scripts/get_status.py NEW_EXEC_ID --poll
```

### Scenario 5: Multi-Step Creative Pipeline (Short Drama / Product Ad)
```bash
# Complex workflow: script → storyboard → video + music (all handled by backend)
# Example: "帮我做个咖啡产品广告，从脚本到成片"

# 1. Check capabilities and points (complex workflows cost more)
python3 {baseDir}/scripts/check_capabilities.py --summary

# 2. Generate multi-step workflow (backend auto-decomposes)
python3 {baseDir}/scripts/generate_workflow.py "制作一个30秒的咖啡产品广告，包含脚本、分镜、视频和背景音乐"
# → Backend returns multi-node workflow (script → storyboard → video → music → composite)
# → Review estimated_points (typically 80-200+ for complex pipelines), ask user to confirm

# 3. Execute full pipeline
python3 {baseDir}/scripts/execute_workflow.py '<template_data_json>'

# 4. Poll status (complex workflows take 3-5+ minutes)
python3 {baseDir}/scripts/get_status.py EXEC_ID --poll --timeout 600

# 5. Download all outputs (storyboard images, video clips, music, final composite)
python3 {baseDir}/scripts/download_results.py EXEC_ID --output-dir ./output/product_ad
```

## 8. User Interaction Guidelines

### Points Confirmation (CRITICAL)
When `generate_workflow.py` returns `points_warning` or `estimated_points`:
1. **MUST show** estimated cost to user before execution
2. **MUST wait** for user confirmation
3. **NEVER auto-execute** when points_warning exists

**Example interaction:**
```
Agent: "This workflow will cost approximately 45 points. You have 50 points available. Proceed? (yes/no)"
User: "yes"
Agent: [Then execute]
```

### Multiple Options
When backend returns multiple plans or options:
- Present all options to user with clear descriptions
- Let user choose, do not auto-select

### Ambiguous Parameters
When user description is vague:
- Ask clarifying questions about key parameters (duration, style, resolution)
- Do not guess or fill in creative details yourself

### Post-Failure Decisions
When execution fails:
- Present failure reason clearly
- Offer options: retry, adjust parameters, change engine, or abort
- Let user decide next action

### Core Principle
**Agent MUST NOT make any points-consuming decision on behalf of the user.**

## 9. Failure Handling and Retry

### Diagnosis Steps
1. Run `get_status.py EXEC_ID` to get detailed error info
2. Check `failed_nodes` list and `error_message`
3. Review `node_statuses` for per-node status

### Retry Strategies

| Strategy | When to Use | Command |
|----------|-------------|---------|
| Single-node retry | One node failed, others succeeded | `execute_single_node.py --node-id <failed_node>` |
| Parameter adjustment | Engine rejected params | Add `--set-param` to modify |
| Full retry | Multiple nodes failed or workflow error | Re-run `execute_workflow.py` |

### Common Failure Scenarios

| Error Code | Cause | Resolution |
|------------|-------|------------|
| `INSUFFICIENT_POINTS` | Not enough credits | User adds credits at voooai.com/subscription |
| `ENGINE_TIMEOUT` | Engine took too long | Retry, or try different engine |
| `INVALID_PARAMS` | Bad parameters | Adjust params with `--set-param` |
| `CONTENT_BLOCKED` | Content safety filter | Modify description to comply with guidelines |
| `ENGINE_UNAVAILABLE` | Engine temporarily down | Wait and retry, or use alternative engine |

### Known Limitations
- Status synchronization may lag — poll with patience
- Complex workflows (short dramas) may take 3-5+ minutes
- After 5-minute timeout, tell user to check results at voooai.com

## 10. Output Formats

**check_capabilities.py**: `{success, points_balance, points_warning, available_engines, available_skills}`

**generate_workflow.py**: `{success, template_data, explanation, metadata: {node_count, engine_nodes, estimated_points}, points_warning}`

**execute_workflow.py**: `{success, execution_id, status, message}`

**get_status.py**: `{success, execution_id, status, progress, result_urls[]}`  
Status values: `pending` | `running` | `completed` | `failed`

**download_results.py**: `{success, output_dir, downloaded_files[], total_count}`

## 11. Core Principles

### Agent is a Relay (搬运工)
- **Forward** user descriptions verbatim to the API
- **NEVER** rewrite, expand, embellish, or translate user prompts
- **NEVER** decompose tasks yourself (send "make 5 episodes" as ONE request)
- **NEVER** construct workflow JSON manually — always use `generate_workflow.py`

### Trust the Backend
VoooAI's PlannerAgent (Analyst + Expert + Reviewer) handles:
- Task decomposition and planning
- Engine/model selection
- Prompt engineering and optimization
- Workflow structure design

### Points Awareness
- **ALWAYS** check `points_warning` before execution
- **ALWAYS** inform user of estimated cost
- **ALWAYS** get user confirmation for costly operations

### Scope Awareness
- **ONLY** operate workflow-related features
- **NEVER** attempt homepage, billing, admin, or account operations
- If user requests out-of-scope operation → direct them to voooai.com

## 12. Polling Strategy

- **Interval**: 10 seconds (do not poll more frequently)
- **Timeout**: 300 seconds (5 minutes default)
- **Completion**: `status: "completed"` → results in `outputs`
- **Failure**: `status: "failed"` → check `error_message`
- **Post-timeout**: Tell user to check at https://voooai.com

## 13. Error Reference

**HTTP Codes**: 400 (bad request) | 401 (unauthorized) | 403 (forbidden) | 429 (rate limit) | 500 (server error)

**Error Codes**:
- `INVALID_ACCESS_KEY` — Key must start with `vooai_`
- `INSUFFICIENT_POINTS` — Add credits at voooai.com/subscription
- `MEMBERSHIP_REQUIRED` — Engine requires higher tier
- `RATE_LIMIT_EXCEEDED` — Wait and retry
- `ENGINE_UNAVAILABLE` — Try alternative engine

---

**Website**: https://voooai.com | **Support**: support@voooai.com
