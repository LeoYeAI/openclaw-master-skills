#!/bin/bash
# post-install.sh - Files Memory System Self-Registration
# 安装后自动向 AGENTS.md 声明自身存在

set -e

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
AGENTS_FILE="/workspace/AGENTS.md"
MARKER="<!-- files-memory-system: installed -->"

echo "📝 Running files-memory-system post-install..."

# 检查 AGENTS.md 是否存在
if [ ! -f "$AGENTS_FILE" ]; then
    echo "⚠️  AGENTS.md not found at $AGENTS_FILE"
    echo "   Please ensure you're installing in /workspace context"
    exit 0
fi

# 检查是否已经注册过
if grep -q "$MARKER" "$AGENTS_FILE" 2>/dev/null; then
    echo "✅ Files memory system already registered in AGENTS.md"
    exit 0
fi

# 添加到 AGENTS.md
cat >> "$AGENTS_FILE" << 'EOF'

<!-- files-memory-system: installed -->
## Files Memory System (Auto-Registered)

This workspace has the **files-memory-system** skill installed.

### Available Memory Locations
- **Global**: `memory/global/` - Cross-group shared memory
- **Group-specific**: `memory/group_<channel>_<id>/` - Isolated per group
- **Private**: `memory/private/` - 1-on-1 chat only

### Key Files
- `MEMORY.md` - Long-term curated memory (private chats only)
- `GLOBAL.md` - Quick reference in each memory directory
- `YYYY-MM-DD.md` - Daily logs

### Session Start - Memory Loading Rules ⭐

**⚠️ 群聊中必须自动加载：**
1. `memory/group_<channel>_<id>/GLOBAL.md` - 群组关键信息
2. `memory/group_<channel>_<id>/YYYY-MM-DD.md` (today) - 今日记录
3. `memory/group_<channel>_<id>/YYYY-MM-DD.md` (yesterday) - 昨日记录
4. `memory/global/GLOBAL.md` - **跨群组全局共享记忆**

**私聊中自动加载：**
1. `memory/private/YYYY-MM-DD.md` (today + yesterday)
2. `memory/global/GLOBAL.md` - **跨群组全局共享记忆**
3. `MEMORY.md` (仅私聊)

**🔴 重要：群聊自动加载失效 Workaround (2026-03-26)**

当前 OpenClaw 版本在群聊中**不会自动加载**群记忆文件。

**Agent 必须在会话开始时手动加载：**
```
IF is_group_chat == true:
  1. 从 metadata 获取 conversation_label (如: oc_a2b821...)
  2. 构建路径: memory/group_feishu_<conversation_label>/
  3. 手动读取:
     - GLOBAL.md
     - YYYY-MM-DD.md (today)
     - YYYY-MM-DD.md (yesterday)  
     - memory/global/GLOBAL.md
```

**检查清单** (群聊中执行任何操作前):
- [ ] 已读取群组 GLOBAL.md?
- [ ] 已读取今日群组日志?
- [ ] 已读取全局 GLOBAL.md?

### When to Use
- User says "remember this" → Write to appropriate location
- User asks "what did we discuss" → Search memory directories
- User wants group isolation → Use group-specific paths
- Cross-group knowledge → Use global/

### Auto-Discovery Note
This section was auto-added by files-memory-system post-install.
<!-- files-memory-system: end -->
EOF

echo "✅ Registered files-memory-system in AGENTS.md"
echo "   Agent will now auto-discover this skill on startup"
