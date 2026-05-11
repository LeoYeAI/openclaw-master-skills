---
name: todo-tracker-safe
description: Secure TODO tracker with input validation and safe file operations. Use for task management across sessions.
homepage: https://github.com/openclaw/openclaw
metadata:
  openclaw:
    emoji: "📋"
    requires:
      bins: ["bash", "grep", "awk", "sed"]
---

# 📋 TODO Tracker (安全版本)

安全的跨会话任务追踪工具，带有输入验证和安全文件操作。

## 安全改进

相比原始版本，此版本包含以下安全增强：

1. **输入验证** - 所有用户输入经过 `sanitize_input()` 过滤
2. **固定字符串匹配** - 使用 `grep -F` 避免正则注入
3. **文件权限检查** - 验证 TODO 文件权限不过于宽松
4. **无动态执行** - 不使用 `eval` 或命令替换执行用户输入
5. **错误处理** - 使用 `set -euo pipefail` 严格模式
6. **长度限制** - 输入限制为 200 字符

## 用法

```bash
# 添加任务
todo.sh add high "完成项目报告"
todo.sh add medium "回复邮件"
todo.sh add low "整理文件"

# 标记完成
todo.sh done "项目报告"

# 删除任务
todo.sh remove "整理文件"

# 列出任务
todo.sh list          # 全部
todo.sh list high     # 高优先级
todo.sh list done     # 已完成

# 摘要（用于 heartbeat）
todo.sh summary
```

## 配置

- `TODO_FILE` - 自定义 TODO 文件路径（默认：`~/.openclaw/workspace/TODO.md`）

## 触发条件

当用户说：
- "添加到 TODO" / "add to TODO"
- "标记 X 完成" / "mark X done"
- "TODO 列表" / "TODO list"
- "还有什么任务" / "what's on the TODO"
- 心跳时自动显示摘要

## 安全审计

- ✅ 无外部 API 调用
- ✅ 无网络请求
- ✅ 无环境变量读取（除 TODO_FILE）
- ✅ 无动态代码执行
- ✅ 输入经过严格过滤
- ✅ 文件操作有权限检查
