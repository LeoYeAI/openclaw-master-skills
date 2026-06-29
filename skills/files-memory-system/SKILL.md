---
name: files-memory-system
description: Multi-context memory management system for OpenClaw agents with group-isolated storage, global shared memory, workspace organization, and group-specific skills isolation. Use when initializing or managing memory systems for multi-channel deployments, creating group-specific memory directories, setting up MEMORY.md for long-term cross-group memories, organizing workspace directories (projects/repos), cloning repositories to group-isolated locations, managing group-isolated skills, or handling any file operations in group chat contexts.
---

# ⚠️ CRITICAL RULES

## 群聊中克隆仓库的硬性规定

**❌ 禁止**：直接使用 `git clone` 命令
**✅ 必须**：使用 `auto-clone.sh` 脚本并传入 `--group` 参数

当用户在群聊中要求"克隆仓库"时：
1. **不要**执行 `git clone <url>` → 这会克隆到 `/workspace/repos/`
2. **必须**执行 `./skills/files-memory-system/scripts/auto-clone.sh --group feishu <group_id> <url>` → 这会克隆到群组目录

**Group ID 获取方式**：从 metadata 中的 `conversation_label` 字段获取（如 `oc_a2b821...`）

---

## 🔴 会话开始强制检查清单 (群聊)

**OpenClaw Bug: 群聊不会自动加载群记忆文件**

每次在群聊中收到消息时，**必须**执行以下检查：

```
检查 metadata.is_group_chat:
├── IF true (群聊):
│   ├── 读取 memory/group_<channel>_<conversation_label>/GLOBAL.md
│   ├── 读取 memory/group_<channel>_<conversation_label>/YYYY-MM-DD.md (today)
│   └── 读取 memory/global/GLOBAL.md
│
└── IF false (私聊):
    ├── 读取 memory/private/YYYY-MM-DD.md (today)
    └── 读取 memory/global/GLOBAL.md
```

**禁止在群聊中执行任何操作前跳过此检查！**

---

# Memory System

> 📖 **新用户？** 请先阅读 [用户使用指南](references/USER_GUIDE.md) 了解如何快速上手！

## Installation

### Method 1: Auto-Install with Self-Registration (Recommended)

```bash
cd ~/.openclaw/skills/files-memory-system
./scripts/install.sh
```

This will:
1. ✅ Copy skill to `/workspace/skills/files-memory-system/` (standard location)
2. ✅ Auto-register in `AGENTS.md` so the agent knows this skill exists
3. ✅ Enable auto-discovery on every agent startup

### Method 2: Manual Install

```bash
# 1. Copy to standard location
mkdir -p /workspace/skills
cp -r ~/.openclaw/skills/files-memory-system /workspace/skills/

# 2. Run self-registration
cd /workspace/skills/files-memory-system
./scripts/post-install.sh
```

### Method 3: Using clawhub

```bash
cd /workspace
clawhub install files-memory-system
# Then manually run:
./skills/files-memory-system/scripts/post-install.sh
```

### Self-Registration Mechanism

This skill implements **auto-declaration** - it automatically adds a section to `AGENTS.md` upon installation. This ensures:

- The agent knows `files-memory-system` exists without being told
- Memory locations are documented where the agent reads
- No manual configuration needed after installation

To verify registration:
```bash
grep -A 20 "files-memory-system" /workspace/AGENTS.md
```

To unregister (remove from AGENTS.md):
```bash
sed -i '/<!-- files-memory-system: installed -->/,/<!-- files-memory-system: end -->/d' /workspace/AGENTS.md
```

## Overview

This skill provides a complete memory management system that enables OpenClaw agents to maintain context across multiple chat groups while keeping group-specific memories and skills isolated. It includes:

- **Group-isolated memory**: Separate memory directories per group/channel
- **Group-isolated skills**: Skills installed per group, preventing cross-group pollution
- **Global shared memory**: Cross-group knowledge in `memory/global/`
- **Long-term memory**: `MEMORY.md` for curated, permanent memories
- **Workspace organization**: Structured `projects/` and `repos/` directories

## Session Start - Automatic Memory Loading

⚠️ **重要**: 每次进入会话时，必须自动加载对应的记忆！

### 群聊中的自动加载流程

当收到群聊消息时，按以下顺序加载记忆：

1. **读取群组 GLOBAL.md** - 获取群组关键信息和资源索引
   ```
   memory/group_<channel>_<id>/GLOBAL.md
   ```

2. **读取今日和昨日记录** - 获取最近的对话上下文
   ```
   memory/group_<channel>_<id>/YYYY-MM-DD.md (today)
   memory/group_<channel>_<id>/YYYY-MM-DD.md (yesterday)
   ```

3. **读取跨群组全局记忆** - 获取跨群组共享的信息
   ```
   memory/global/GLOBAL.md
   ```

### 私聊中的自动加载流程

1. **读取私聊记录** - 今日和昨日
   ```
   memory/private/YYYY-MM-DD.md (today)
   memory/private/YYYY-MM-DD.md (yesterday)
   ```

2. **读取跨群组全局记忆**
   ```
   memory/global/GLOBAL.md
   ```

3. **读取长期精华记忆** (仅私聊)
   ```
   MEMORY.md
   ```

### 记忆加载检查清单

**群聊中必须加载：**
- [ ] 当前群组的 GLOBAL.md
- [ ] 今天的群组日志 (YYYY-MM-DD.md)
- [ ] 昨天的群组日志 (回顾上下文)
- [ ] **跨群组全局记忆 (memory/global/GLOBAL.md)**

**私聊中必须加载：**
- [ ] 私聊今日和昨日日志
- [ ] **跨群组全局记忆 (memory/global/GLOBAL.md)**
- [ ] MEMORY.md (仅私聊)

## Usage Scenarios

### Scenario 1: User Says "Clone This Repo" in a Group Chat

**Context**: User in group "oc_a2b821..." says: "Clone https://github.com/user/project"

**Automatic Actions**:
1. Detect current group context: `group_feishu_oc_a2b821...`
2. Clone to: `memory/group_feishu_oc_a2b821.../repos/project/`
3. Update group's GLOBAL.md with project info
4. Confirm: "✅ Cloned to group repos/project/"

**Manual Commands**:
```bash
# Option 1: Use auto-clone script with --group parameter (推荐)
./scripts/auto-clone.sh --group feishu oc_a2b821... https://github.com/user/project

# Option 2: Direct git clone
cd memory/group_feishu_xxx/repos
git clone https://github.com/user/project

# Option 3: Using environment variables (向后兼容)
GROUP_ID="oc_xxx" CHANNEL="feishu" ./scripts/auto-clone.sh https://github.com/user/project
```

**Agent Implementation (直接执行，无需用户交互)**:

当用户要求克隆仓库时，**先判断当前是否在群聊中**（查看 inbound metadata 中的 `is_group_chat` 字段），然后：

**如果是群聊** (`is_group_chat: true`):
1. 从 metadata 读取 `conversation_label` 作为 group_id
2. 使用 `--group` 参数执行克隆：
```bash
./skills/files-memory-system/scripts/auto-clone.sh \
    --group feishu "<conversation_label>" \
    "https://github.com/user/project"
```

**如果是私聊** (`is_group_chat: false`):
```bash
./skills/files-memory-system/scripts/auto-clone.sh \
    --private \
    "https://github.com/user/project"
```

**关键要点**：
- ⚠️ **群聊中必须使用 `--group` 参数**，否则仓库会克隆到全局目录
- `--group <channel> <group_id>` 必须在 URL 之前
- 群组ID从 `conversation_label` 获取 (如 `oc_a2b821...`)
- 脚本会自动创建缺失的群组记忆目录
- 如果用户没指定项目名称，脚本会自动从 URL 提取

**After Cloning - Update GLOBAL.md**:
```markdown
## 群组项目 (repos/)

| 项目名称 | 类型 | 描述 | 位置 |
|---------|------|------|------|
| project | cloned | 克隆的示例项目 | repos/project/ |
```

### Scenario 2: Create New Project in Group Context

**Context**: User says: "Create a new tool for our group"

**Automatic Actions**:
1. Create project directory: `memory/group_xxx/repos/my-tool/`
2. Initialize with template if needed
3. Update GLOBAL.md
4. Start working in the group-specific location

**Manual Commands**:
```bash
# Create new project in group context
mkdir -p memory/group_feishu_xxx/repos/my-tool
cd memory/group_feishu_xxx/repos/my-tool
# ... create files ...
```

### Scenario 3: Install Skill for Specific Group

**Context**: User says: "Install inkos skill for this group only"

**Automatic Actions**:
1. Install to: `memory/group_xxx/skills/inkos/`
2. Update group's GLOBAL.md
3. Skill is isolated to this group only

**Manual Commands**:
```bash
# Method 1: Using clawhub with --dir
clawhub install inkos --dir memory/group_feishu_xxx/skills

# Method 2: Manual copy
mkdir -p memory/group_feishu_xxx/skills/inkos
cp -r inkos/* memory/group_feishu_xxx/skills/inkos/
```

**Update GLOBAL.md**:
```markdown
## 已安装的群组专属 Skills

| Skill | 版本 | 来源 | 描述 |
|-------|------|------|------|
| inkos | 1.0.0 | clawhub | 小说写作工具 |
```

### Scenario 4: Record Information to Group Memory ⭐

**Context**: User in group chat says: "记录到群记忆里: 项目信息" / "记录到全局记忆里: API密钥" / "记住这个"

**Automatic Actions** (Agent Must Do):
1. **Detect the intent**: User wants to record information to group memory
2. **Determine target location** (按优先级匹配):
   - If "记录到群记忆里" → `memory/group_<channel>_<id>/GLOBAL.md`
   - If "记录到全局记忆里"/"记录到跨群记忆里" → `memory/global/GLOBAL.md`
   - If "记录到私聊里" → `memory/private/GLOBAL.md`
   - If "群文档"/"群组" (模糊指令) → `memory/group_<channel>_<id>/GLOBAL.md`
3. **Write to file immediately**: Do not just say "I remember", actually write to file!
4. **Confirm**: "✅ 已记录到群记忆" / "✅ 已保存到全局记忆"

**Example 1: Record Project Info**
```
User: "记录到群记忆里: 项目信息"
项目名称: MyApp
技术栈: React + Node.js
负责人: 张三

Agent Action:
1. Detect "记录到群记忆里" → Target: memory/group_xxx/GLOBAL.md
2. Format as table and append:

## 活跃项目

| 项目名称 | 技术栈 | 负责人 | 更新时间 |
|---------|--------|--------|----------|
| MyApp | React + Node.js | 张三 | 2026-03-23 |

3. Confirm: "✅ 已记录到群记忆"
```

**Example 2: Record API Key (⚠️ Not Recommended)**
```
User: "记录到全局记忆里：API密钥 sk-abc123"

⚠️ **SECURITY WARNING**:
Storing API keys in plain text in memory files is NOT recommended.
**Recommended approach: Use environment variables**

export API_KEY="sk-xxx"

Alternative (if environment variables not possible):
- Use a secrets manager
- Use encrypted storage

If user insists on storing in memory:
1. Warn: "⚠️ 存储 API 密钥到记忆文件存在安全风险，建议仅用于测试环境"
2. Detect target location based on user command
3. Format as table and append
4. Confirm: "✅ 已记录 (⚠️ 安全风险)"
```

**Recommended User Commands**:
- "记录到群记忆里: [内容]" → 仅当前群可见
- "记录到全局记忆里: [内容]" → 所有群共享
- "记录到跨群记忆里: [内容]" → 同全局记忆
- "记录到私聊里: [内容]" → 仅私聊可见

**Critical Rules**:
- ❌ DO NOT just say "I remember" without writing to file
- ❌ DO NOT store sensitive info without clarifying scope
- ✅ ALWAYS confirm the location where info is stored
- ✅ Use tables in GLOBAL.md for structured info
- ✅ Add timestamps for time-sensitive info

### Scenario 5: Create Files in Group Chat ⭐

**Context**: User in group chat says: "帮我写一篇文章" / "创建一个文档" / "生成xxx文件"

**Automatic Actions** (Agent Must Do):
1. **Detect the intent**: User wants to create a file in group context
2. **Determine correct location**:
   - Default: `memory/group_<channel>_<id>/articles/` (for articles/docs)
   - Code: `memory/group_<channel>_<id>/repos/` (for code projects)
3. **Create the file**: Write to the correct group-specific path
4. **Auto-update GLOBAL.md**: ⚠️ **CRITICAL** - After creating file, auto-append to GLOBAL.md
5. **Confirm**: "✅ 已创建并记录到群文档"

### Scenario 6: Working Across Multiple Groups

**Context**: Same user in different groups

**Group A (小说创作)**:
- Skills: `memory/group_A/skills/inkos/`
- Projects: `memory/group_A/repos/novel-tools/`

**Group B (编程学习)**:
- Skills: `memory/group_B/skills/code-helper/`
- Projects: `memory/group_B/repos/exercises/`

**Behavior**:
- In Group A: Only sees `inkos`, not `code-helper`
- In Group B: Only sees `code-helper`, not `inkos`
- No pollution between groups!

### Scenario 5: Migrate Information to Global

**Context**: Information becomes relevant to multiple groups

**Migration Process**:
1. Move from: `memory/group_A/GLOBAL.md`
2. To: `memory/global/GLOBAL.md`
3. Update Group A with reference
4. All groups can now access

**Example**:
```bash
# Original in group_A/GLOBAL.md
## Project Configuration
Config: xxx

# After migration - in global/GLOBAL.md
## Shared Project Configuration
Config: xxx

# In group_A/GLOBAL.md - add reference
## 跨群组资源
See: memory/global/GLOBAL.md
```

⚠️ **Security Note**: Do NOT migrate API keys, passwords, or other sensitive credentials to global memory. Keep secrets in environment variables or private memory only.

## Memory Architecture

### Directory Structure

```
/workspace/
├── memory/
│   ├── global/
│   │   ├── GLOBAL.md              # Shared key information
│   │   └── YYYY-MM-DD.md          # Daily logs
│   ├── group_feishu_<id>/         # Feishu group memories
│   │   ├── GLOBAL.md              # Group key information
│   │   ├── YYYY-MM-DD.md          # Daily logs
│   │   ├── skills/                # ⭐ Group-specific skills
│   │   └── repos/                 # ⭐ Group-specific projects
│   └── private/
│       ├── GLOBAL.md
│       └── YYYY-MM-DD.md
├── MEMORY.md
├── skills/                        # Global shared skills
├── projects/
└── repos/
```

### Automation Scripts

**scripts/init-group-memory.sh** - Initialize group memory structure:
```bash
./scripts/init-group-memory.sh feishu oc_xxx "小说创作群组"
```

**scripts/ensure-group-memory.sh** - Ensure group memory directory exists (on-demand):
```bash
# Auto-initializes group memory with all subdirectories
./scripts/ensure-group-memory.sh feishu oc_xxx "小说创作群组"
```

**scripts/ensure-private-memory.sh** - Ensure private memory directory exists:
```bash
# Auto-initializes private memory when in private chat context
./scripts/ensure-private-memory.sh
```

**scripts/ensure-global-memory.sh** - Ensure global memory directory exists:
```bash
# Auto-initializes global memory for cross-group information
./scripts/ensure-global-memory.sh
```

**scripts/auto-clone.sh** - Clone repo to correct location:
```bash
# Auto-detects context and clones to appropriate location
./scripts/auto-clone.sh https://github.com/user/repo
```

## Group-Isolated Skills System

| Scope | Location | Access | Priority |
|-------|----------|--------|--------|
| **Group-specific** | `memory/group_<id>/skills/` | Only current group | High |
| **Global** | `/workspace/skills/` | All groups | Low |

## Promoting Cross-Group Memory Awareness

### 1. Include Reference in Group GLOBAL.md

Every group's GLOBAL.md should include:

```markdown
## Cross-Group Resources

📚 **Cross-Group Global Memory**: `memory/global/GLOBAL.md`

Contains information shared across all groups.
```

### 2. Key Information to Store Globally

- Relevant to multiple groups
- Common standards or conventions
- Shared resources (non-sensitive)
- Tool documentation and links

⚠️ **Security Note**: Do NOT store API keys, passwords, or other sensitive credentials in global memory. Use environment variables or private memory for secrets.

### 3. Migration from Group to Global

When information becomes relevant to multiple groups:
1. Move to `memory/global/GLOBAL.md`
2. Update original with reference link
3. Notify affected groups

## Memory Auto-Initialization

All memory directories are automatically initialized using a dual approach (A + B):

### Approach A: Installation-Time Setup
When installing files-memory-system, the following directories are automatically created:
- `memory/private/` with `GLOBAL.md`
- `memory/global/` with `GLOBAL.md`

### Approach B: On-Demand Setup
When using `auto-clone.sh` or other scripts, the system automatically detects and initializes missing directories:
- **Group context**: Calls `ensure-group-memory.sh`
- **Private context**: Calls `ensure-private-memory.sh`
- **Global operations**: Calls `ensure-global-memory.sh`

This ensures all memory locations are always available when needed, even if:
- The installation step was skipped
- The directory was accidentally deleted
- Working in a new workspace

### Memory Directory Comparison

| Feature | Private Memory | Group Memory | Global Memory |
|---------|----------------|--------------|---------------|
| **Location** | `memory/private/` | `memory/group_<id>/` | `memory/global/` |
| **Auto-init A** | ✅ Install-time | ❌ No | ✅ Install-time |
| **Auto-init B** | ✅ On-demand | ✅ On-demand | ✅ On-demand |
| **Skills** | Uses global | Can isolate | N/A |
| **Projects** | Uses global | Can isolate | N/A |
| **Scope** | 1-on-1 chats | Specific group | All groups |
| **Ensure Script** | `ensure-private-memory.sh` | `ensure-group-memory.sh` | `ensure-global-memory.sh` |
| **Scope** | 1-on-1 chats only | Specific to one group |
| **Auto-init** | ✅ Yes (A+B) | ✅ Yes (B only) |

## Security Notes

- `MEMORY.md` only loaded in private chats
- Group skills completely isolated
- Preserve group memory on disband
