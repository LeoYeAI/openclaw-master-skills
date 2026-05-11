# Context Restore UX 改进建议

**版本**: v1.1.0  
**日期**: 2026-02-07  
**状态**: 规划中

---

## 📋 目录

1. [概述](#概述)
2. [优先级排序](#优先级排序)
3. [短期改进 (P0)](#短期改进-p0)
4. [中期改进 (P1)](#中期改进-p1)
5. [长期改进 (P2)](#长期改进-p2)
6. [验收标准](#验收标准)
7. [风险评估](#风险评估)

---

## 概述

本文档提供 context-restore 技能的 UX 改进建议，基于 UX_EVALUATION_REPORT.md 中的评估结果。

### 改进目标

1. **用户体验**: 使输出更友好、更直观
2. **信息架构**: 优化信息组织方式
3. **平台适配**: 针对 Telegram 优化输出格式
4. **集成增强**: 与主会话更好地集成

---

## 优先级排序

| 优先级 | 问题 ID | 改进项 | 预期效果 | 工作量 |
|--------|---------|--------|---------|--------|
| P0 | P0-01 | 修复文件路径问题 | 用户可直接运行 | 2h |
| P0 | P0-02 | 统一输出格式 | 文档与实现一致 | 4h |
| P0 | P0-03 | 添加用户确认流程 | 避免跳过重要信息 | 3h |
| P1 | P1-01 | Telegram 消息分块 | 消息不被截断 | 3h |
| P1 | P1-02 | 改进错误信息 | 用户友好 | 2h |
| P1 | P1-03 | 添加操作建议 | 引导用户操作 | 2h |
| P2 | P2-01 | 中文分隔符 | 更好的本地化 | 1h |
| P2 | P2-02 | 格式化时间 | 更直观 | 1h |

---

## 短期改进 (P0)

### P0-01: 修复文件路径问题

**文件**: `scripts/restore_context.py`

```python
# 当前的硬编码路径
DEFAULT_CONTEXT_FILE = './compressed_context/latest_compressed.json'

# 改进后
def find_context_file() -> Optional[str]:
    """
    自动查找上下文文件，支持多种路径配置方式。
    
    Returns:
        找到的文件路径，或 None（表示未找到）
    """
    import os
    from pathlib import Path
    
    # 1. 优先使用环境变量
    env_path = os.environ.get('OPENCLAW_CONTEXT_FILE')
    if env_path and os.path.isfile(env_path):
        return env_path
    
    # 2. 常见路径配置
    possible_paths = [
        # 相对于脚本位置
        Path(__file__).parent.parent / 'compressed_context' / 'latest_compressed.json',
        # 相对于 workspace
        Path('/home/athur/.openclaw/workspace/compressed_context/latest_compressed.json'),
        # 当前工作目录
        Path.cwd() / 'compressed_context' / 'latest_compressed.json',
        # 相对路径
        Path('./compressed_context/latest_compressed.json'),
    ]
    
    for path in possible_paths:
        if path.is_file():
            return str(path)
    
    return None


# 使用新的函数
DEFAULT_CONTEXT_FILE = find_context_file()
```

### P0-02: 统一输出格式

**文件**: `scripts/restore_context.py`

```python
# 新增: 改进的报告格式化函数

def format_timestamp(timestamp: str) -> str:
    """将 ISO 时间格式转换为友好格式"""
    from datetime import datetime
    
    try:
        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        now = datetime.now(dt.tzinfo)
        diff = now - dt
        
        if diff.days == 0:
            if diff.seconds < 3600:
                minutes = diff.seconds // 60
                return f"{minutes} 分钟前"
            else:
                hours = diff.seconds // 3600
                return f"{hours} 小时前"
        elif diff.days == 1:
            return "昨天"
        else:
            return dt.strftime("%m-%d %H:%M")
    except Exception:
        return timestamp


def format_normal_report_v2(content: str) -> str:
    """
    改进后的 Normal 级别报告格式化。
    
    改进点:
    - 添加 "上下文已恢复" 确认消息
    - 使用中文分隔符
    - 友好的时间格式
    - 添加操作建议
    """
    lines = []
    
    # 解析内容
    metadata = parse_metadata(content)
    projects = extract_key_projects(content)
    tasks = extract_ongoing_tasks(content)
    operations = extract_recent_operations(content)
    
    # 1. 确认消息
    lines.append("✅ **上下文已恢复**")
    lines.append("")
    
    # 2. 会话概览
    lines.append("📊 **会话概览**")
    original = metadata.get('original_count', 'N/A')
    compressed = metadata.get('compressed_count', 'N/A')
    ratio = calculate_compression_ratio(
        metadata.get('original_count'),
        metadata.get('compressed_count')
    )
    timestamp = metadata.get('timestamp', 'Unknown')
    friendly_time = format_timestamp(timestamp)
    
    if ratio is not None:
        lines.append(f"• 原始消息: {original} → 压缩后: {compressed} (压缩率 {ratio:.0f}%)")
    else:
        lines.append(f"• 消息: {original} → {compressed}")
    lines.append(f"• 最后活动: {friendly_time}")
    lines.append("")
    
    # 3. 活跃项目
    if projects:
        lines.append(f"🚀 **活跃项目** ({len(projects)})")
        for i, project in enumerate(projects, 1):
            emoji = {'Hermes Plan': '🏛️', 'Akasha Plan': '🌐', 'Morning Brief': '📰'}.get(
                project['name'], '📁'
            )
            lines.append(f"{i}. **{project['name']}** {emoji}")
            lines.append(f"   {project.get('description', '无描述')}")
            if project.get('status'):
                status_emoji = {'Active': '🟢', 'Paused': '🟡', 'Completed': '✅'}.get(
                    project['status'], '⚪'
                )
                lines.append(f"   {status_emoji} 状态: {project['status']}")
        lines.append("")
    
    # 4. 待办任务
    if tasks:
        lines.append(f"📋 **待办任务** ({len(tasks)})")
        priority_map = {'Active': '🔴', 'Running': '🟡', 'Completed': '✅'}
        for task in tasks:
            status_emoji = priority_map.get(task.get('status'), '⚪')
            lines.append(f"{status_emoji} {task['task']}")
            if task.get('detail'):
                lines.append(f"   └ {task['detail']}")
        lines.append("")
    
    # 5. 最近操作
    if operations:
        lines.append(f"🔄 **最近操作** ({len(operations)})")
        for op in operations[:3]:  # 只显示前3个
            lines.append(f"• {op}")
        lines.append("")
    
    # 6. 操作建议
    lines.append("💡 **建议操作**")
    lines.append("• 输入项目名称继续工作")
    lines.append("• 说 \"查看详情\" 获取更多信息")
    lines.append("• 说 \"新任务\" 开始新工作")
    
    return '\n'.join(lines)
```

### P0-03: 添加用户确认流程

**文件**: `scripts/restore_context.py`

```python
class ContextRestoreSession:
    """
    管理上下文恢复会话状态，支持用户确认流程。
    """
    
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.state = 'init'  # init -> summary_shown -> confirmed -> working
        self.context_report = None
        self.confirmed = False
    
    def restore(self, level: str = 'normal') -> dict:
        """
        执行上下文恢复，返回完整报告和交互状态。
        """
        # 加载上下文
        context_file = find_context_file()
        if not context_file:
            return {
                'success': False,
                'error_type': 'file_not_found',
                'message': self._format_file_not_found_error()
            }
        
        # 生成报告
        report = restore_context(context_file, level)
        
        if report.startswith("❌ Error"):
            return {
                'success': False,
                'error_type': 'load_failed',
                'message': report
            }
        
        # 改进格式
        if level == 'normal':
            report = format_normal_report_v2(
                self._extract_content(report)
            )
        
        self.context_report = report
        self.state = 'summary_shown'
        
        return {
            'success': True,
            'state': 'summary_shown',
            'report': report,
            'actions': ['continue', 'detail', 'new_task'],
            'confirmation_required': True
        }
    
    def confirm(self, action: str = 'continue') -> dict:
        """
        用户确认后继续工作。
        """
        self.confirmed = True
        self.state = 'working'
        
        if action == 'continue':
            return {
                'success': True,
                'action': 'continue',
                'message': '好的，开始继续之前的工作。',
                'next_step': 'waiting_for_task_name'
            }
        elif action == 'detail':
            return {
                'success': True,
                'action': 'show_detail',
                'message': '正在获取详细报告...',
                'next_step': 'show_detailed_report'
            }
        else:
            return {
                'success': True,
                'action': 'new_task',
                'message': '好的，开始新任务。',
                'next_step': 'collect_task_info'
            }
    
    def _format_file_not_found_error(self) -> str:
        """格式化文件未找到错误"""
        return """
⚠️ **未找到历史上下文文件**

这可能是以下情况：
• 首次使用 OpenClaw
• 上下文文件已被清理

💡 从新会话开始，我将记录新的上下文。
        """.strip()
    
    def _extract_content(self, report: str) -> str:
        """从报告提取原始内容用于解析"""
        # 移除分隔符和报告头部，提取核心内容
        # 简化实现：返回原始内容
        return report
```

---

## 中期改进 (P1)

### P1-01: Telegram 消息分块

**文件**: `scripts/telegram_formatter.py` (新建)

```python
"""
Telegram 平台专用格式化模块。
"""

import re
from typing import List

MAX_MESSAGE_LENGTH = 4000  # Telegram 消息长度限制


class TelegramFormatter:
    """Telegram 平台消息格式化"""
    
    def chunk_report(self, report: str, level: str = 'normal') -> List[str]:
        """
        将报告分块以适应 Telegram 消息限制。
        
        分块策略:
        1. 按章节分块，保持语义完整性
        2. 每个块包含标题和内容
        3. 块之间用分隔线连接
        """
        if len(report) <= MAX_MESSAGE_LENGTH:
            return [report]
        
        # 提取章节
        sections = self._split_into_sections(report)
        
        chunks = []
        current_chunk = ""
        
        for section in sections:
            if len(current_chunk) + len(section) + 2 > MAX_MESSAGE_LENGTH:
                # 当前块已满，保存并开始新块
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = section
            else:
                current_chunk += "\n\n" + section if current_chunk else section
        
        # 保存最后一个块
        if current_chunk:
            chunks.append(current_chunk)
        
        # 确保每个块都有标题
        return self._ensure_titles(chunks)
    
    def _split_into_sections(self, report: str) -> List[str]:
        """按章节分割报告"""
        # 使用分隔符识别章节
        section_pattern = r'(📊|🚀|📋|🔄|💡|✅).*\n'
        sections = []
        current_section = ""
        
        for line in report.split('\n'):
            if re.match(section_pattern, line):
                if current_section:
                    sections.append(current_section)
                current_section = line
            else:
                current_section += '\n' + line
        
        if current_section:
            sections.append(current_section)
        
        return sections
    
    def _ensure_titles(self, chunks: List[str]) -> List[str]:
        """确保每个块都有标题"""
        titled_chunks = []
        
        for i, chunk in enumerate(chunks):
            if i == 0:
                # 第一个块通常有标题
                titled_chunks.append(chunk)
            else:
                # 后续块添加续标题
                titled_chunks.append(f"--- (接上页) ---\n\n{chunk}")
        
        return titled_chunks
    
    def create_inline_keyboard(self, level: str) -> dict:
        """创建内联键盘按钮"""
        return {
            'inline_keyboard': [
                [
                    {'text': '📋 详细报告', 'callback_data': f'ctx_detail_{level}'},
                    {'text': '📊 项目列表', 'callback_data': 'ctx_projects'}
                ],
                [
                    {'text': '➡️ 继续工作', 'callback_data': 'ctx_continue'},
                    {'text': '❓ 帮助', 'callback_data': 'ctx_help'}
                ]
            ]
        }
    
    def format_for_telegram(self, report: str, level: str = 'normal') -> dict:
        """
        完整格式化以适应 Telegram。
        
        Returns:
            dict with keys:
                - 'chunks': List[str] - 分块后的消息
                - 'keyboard': dict - 内联键盘（可选）
                - 'parse_mode': str - Markdown/HTML
        """
        chunks = self.chunk_report(report, level)
        
        return {
            'chunks': chunks,
            'keyboard': self.create_inline_keyboard(level) if level == 'normal' else None,
            'parse_mode': 'Markdown'
        }
```

### P1-02: 改进错误信息

**文件**: `scripts/restore_context.py`

```python
# 新增错误信息格式化函数

ERROR_MESSAGES = {
    'file_not_found': """
⚠️ **未找到上下文文件**

这可能是以下情况：
• 首次使用 OpenClaw
• 上下文文件已被清理

💡 从新会话开始，我将记录新的上下文。

---
想开始新任务吗？说 "新任务" 开始工作。
    """.strip(),
    
    'permission_denied': """
⚠️ **无法访问上下文文件**

权限不足，无法读取上下文文件。

**可能原因：**
• 文件权限设置不正确
• 文件被其他进程锁定

**解决方案：**
• 检查文件权限: `ls -la /home/athur/.openclaw/workspace/compressed_context/`
• 联系管理员获取帮助

💡 我将使用默认设置继续。
    """.strip(),
    
    'parse_error': """
⚠️ **上下文文件异常**

文件格式损坏或无法解析。

**自动处理：**
• 正在尝试恢复...
• 部分上下文信息可能丢失

💡 如果需要完整上下文，请联系管理员检查日志。
    """.strip(),
    
    'json_decode_error': """
⚠️ **上下文格式错误**

JSON 解析失败，文件可能损坏。

**诊断信息：**
• 文件不是有效的 JSON 格式
• 可能是纯文本格式，请尝试其他方式

💡 我将尝试使用原始内容继续。
    """.strip(),
    
    'empty_context': """
⚠️ **上下文为空**

未找到有效的上下文信息。

**可能原因：**
• 会话刚刚开始
• 上下文已被清除

💡 从新会话开始，我将为您创建新的上下文。
    """.strip()
}


def format_user_friendly_error(error_type: str, details: str = "") -> str:
    """
    格式化用户友好的错误信息。
    
    Args:
        error_type: 错误类型，对应 ERROR_MESSAGES 的键
        details: 额外详情（可选）
    
    Returns:
        格式化后的错误消息
    """
    base_message = ERROR_MESSAGES.get(
        error_type,
        f"❌ 发生错误：{details}"
    )
    
    # 如果有额外详情，添加到末尾
    if details and error_type not in ERROR_MESSAGES:
        base_message += f"\n\n**技术详情：**\n```\n{details}\n```"
    
    return base_message
```

### P1-03: 添加操作建议

**文件**: `scripts/restore_context.py`

```python
def generate_suggestions(context: dict) -> List[str]:
    """
    根据上下文生成操作建议。
    
    Args:
        context: 解析后的上下文信息
    
    Returns:
        建议列表
    """
    suggestions = []
    
    # 基于项目数量
    project_count = len(context.get('projects', []))
    if project_count == 0:
        suggestions.append("说 \"新任务\" 开始新工作")
    elif project_count == 1:
        suggestions.append(f"继续 **{context['projects'][0]['name']}**")
    else:
        suggestions.append("输入项目名称继续工作")
        suggestions.append("说 \"查看项目列表\" 获取详情")
    
    # 基于任务
    task_count = len(context.get('tasks', []))
    if task_count > 0:
        high_priority = [t for t in context.get('tasks', []) if t.get('priority') == 'high']
        if high_priority:
            suggestions.append(f"建议优先处理: {high_priority[0]['task']}")
    
    # 基于最近操作
    recent_ops = context.get('operations', [])
    if recent_ops:
        suggestions.append(f"最近操作: {recent_ops[0]}")
    
    # 通用建议
    suggestions.append("说 \"查看详情\" 获取更多信息")
    
    return suggestions


def format_suggestions_block(suggestions: List[str]) -> str:
    """格式化建议块"""
    lines = ["💡 **建议操作**"]
    
    for suggestion in suggestions:
        lines.append(f"• {suggestion}")
    
    return '\n'.join(lines)
```

---

## 长期改进 (P2)

### P2-01: 中文分隔符

```python
# 使用中文分隔符替代英文
REPORT_SEPARATOR = "═" * 50  # 或使用 "─" * 50
SECTION_SEPARATOR = "─" * 40

# 改进后的格式示例
"""
══════════════════════════════════════════
✅ 上下文已恢复
══════════════════════════════════════════

📊 会话概览
────────────────────────────────────────
• 原始消息: 45 → 12 (27%)
• 最后活动: 2小时前

🚀 活跃项目
────────────────────────────────────────
1. Hermes Plan 🏛️
   数据分析助手，进度 80%
...
"""
```

### P2-02: 格式化时间

```python
def format_context_age(timestamp: str) -> str:
    """计算并格式化上下文年龄"""
    from datetime import datetime
    
    try:
        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        now = datetime.now(dt.tzinfo)
        diff = now - dt
        
        # 返回友好格式
        if diff.days > 0:
            return f"{diff.days} 天前"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} 小时前"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} 分钟前"
        else:
            return "刚刚"
    except Exception:
        return "未知"
```

---

## 验收标准

### 短期改进验收

| 验收项 | 标准 | 测试方法 |
|-------|------|---------|
| 文件路径 | `python restore_context.py` 无需参数即可运行 | 执行脚本，检查是否找到文件 |
| 输出格式 | 与 SKILL.md 示例一致 | 对比实际输出与期望输出 |
| 确认流程 | 输出后等待用户确认 | 测试交互流程 |

### 中期改进验收

| 验收项 | 标准 | 测试方法 |
|-------|------|---------|
| 消息分块 | Normal 级别输出不超过 4000 字符/块 | 发送长报告，检查分块 |
| 错误信息 | 用户能理解错误原因 | 模拟各种错误，检查消息 |
| 建议有用 | 建议与上下文相关 | 测试不同场景 |

### 长期改进验收

| 验收项 | 标准 | 测试方法 |
|-------|------|---------|
| 中文界面 | 所有分隔符为中文 | 检查输出格式 |
| 时间格式 | 显示 "2小时前" 而非时间戳 | 检查时间显示 |

---

## 风险评估

| 风险 | 影响 | 缓解措施 |
|-----|------|---------|
| 格式变更导致兼容性问题 | 中 | 添加版本号，渐进式发布 |
| 分块逻辑复杂化 | 低 | 保持简单，按章节分块 |
| 依赖外部库 | 无 | 仅使用标准库 |

---

## 时间线

| 阶段 | 时间 | 内容 |
|-----|------|------|
| P0 实施 | 第1周 | 文件路径、输出格式、确认流程 |
| P1 实施 | 第2-3周 | Telegram 优化、错误信息、建议 |
| P2 实施 | 第4周 | 中文本地化、时间格式 |
| 测试验收 | 第5周 | 全面测试、文档更新 |

---

## 参考

- [UX 评估报告](./UX_EVALUATION_REPORT.md)
- [SKILL.md](./SKILL.md)
- [restore_context.py](./scripts/restore_context.py)
