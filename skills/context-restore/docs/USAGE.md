# Context Restore 使用指南

本指南涵盖从基础到高级的所有用法场景，帮助你充分发挥 Context Restore 的功能。

---

## 目录

- [基础用法](#基础用法)
- [高级用法](#高级用法)
- [自动触发集成](#自动触发集成)
- [Telegram 集成](#telegram-集成)
- [Cron 定时任务](#cron-定时任务)
- [常见问题](#常见问题)

---

## 基础用法

### 1. 普通报告（默认模式）

```bash
# 使用默认配置运行
python restore_context.py
```

**输出示例：**
```
✅ 上下文已恢复

📊 压缩信息:
- 原始消息: 150
- 压缩后: 25
- 压缩率: 16.7%

🔄 最近操作:
- 完成数据清洗模块
- 添加 3 个新 cron 任务

🚀 项目:
- Hermes Plan - 数据分析助手
```

### 2. JSON 摘要输出

获取结构化数据供其他程序使用：

```bash
# 输出 JSON 格式摘要
python restore_context.py --summary
```

**输出示例：**
```json
{
  "success": true,
  "metadata": {
    "original_count": 150,
    "compressed_count": 25,
    "compression_ratio": 16.7
  },
  "operations": ["完成数据清洗模块", "添加 cron 任务"],
  "projects": [{"name": "Hermes Plan", "status": "Active"}],
  "tasks": [{"task": "测试数据管道", "status": "Pending"}]
}
```

### 3. 恢复级别选择

| 级别 | 参数 | 适用场景 |
|------|------|---------|
| 极简 | `--level minimal` | 快速确认状态 |
| 标准 | `--level normal` | 日常继续工作 |
| 详细 | `--level detailed` | 深度回顾/汇报 |

```bash
# 极简模式
python restore_context.py --level minimal

# 标准模式
python restore_context.py --level normal

# 详细模式
python restore_context.py --level detailed
```

---

## 高级用法

### 1. 时间线视图

按不同周期查看历史操作：

```bash
# 按天显示（默认）
python restore_context.py --timeline --period daily

# 按周显示
python restore_context.py --timeline --period weekly

# 按月显示
python restore_context.py --timeline --period monthly
```

**输出示例（weekly）：**
```
📅 Week 6 (Feb 2-8)
├── 完成数据管道测试
├── 部署新功能到生产环境
└── 项目: Hermes Plan, Akasha Plan

📅 Week 5 (Jan 26 - Feb 1)
├── 启动 Akasha UI 改进
└── 项目: Hermes Plan
```

### 2. 内容过滤

只显示匹配特定条件的内容：

```bash
# 只显示与 Hermes 相关的内容
python restore_context.py --filter "Hermes"

# 只显示项目相关信息
python restore_context.py --filter "project"

# 多个条件
python restore_context.py --filter "Hermes" --level detailed
```

### 3. 上下文对比

比较两个版本的上下文差异：

```bash
# 基本对比
python restore_context.py --diff old.json new.json

# 对比并显示详细差异
python restore_context.py --diff old.json new.json --level detailed

# 对比并输出到文件
python restore_context.py --diff old.json new.json --output diff_report.txt
```

**输出示例：**
```
CONTEXT DIFF REPORT
============================================================
📁 Old: context_2026-02-05.json
📁 New: context_2026-02-06.json

⏱️  Time difference: 24.0 hours

🚀 Projects:
   ➕ Added (1):
      - Akasha Plan
   (No task changes)

🔄 Operations:
   ➕ Added (2):
      - 完成数据管道测试
      - 部署新功能
   (No operation removals)

📊 Message Counts:
   Old: 150 → 25 (compressed)
   New: 180 → 30 (compressed)

============================================================
Total changes detected: 3
============================================================
```

### 4. 自定义文件路径

```bash
# 使用指定文件
python restore_context.py --file /path/to/context.json

# 输出到指定文件
python restore_context.py --output /path/to/report.txt

# 组合使用
python restore_context.py --file ./context.json --output ./report.txt --level detailed
```

### 5. 日期过滤

```bash
# 只显示今天之后的内容
python restore_context.py --since 2026-02-07

# 只显示本周内容
python restore_context.py --since 2026-02-02

# 结合时间线使用
python restore_context.py --timeline --since 2026-01-01 --period weekly
```

---

## 自动触发集成

### 1. 自动检测并恢复

当检测到上下文变化时自动恢复，无需手动确认：

```bash
# 自动模式（标准输出）
python restore_context.py --auto

# 自动模式（静默输出）
python restore_context.py --auto --quiet

# 自动模式（详细级别）
python restore_context.py --auto --level detailed
```

**静默模式说明：**
- `--quiet` 只显示必要信息
- 适合在脚本或 cron 中运行
- 不显示详细报告，只显示状态变化

### 2. 仅检查变化

用于外部监控系统，不执行恢复操作：

```bash
# 检查是否有变化
python restore_context.py --check-only

# 检查并根据结果执行操作
if python restore_context.py --check-only; then
    echo "无变化"
else
    echo "检测到变化，自动恢复..."
    python restore_context.py --auto
fi
```

**退出码说明：**
- `0`: 无变化
- `1`: 检测到变化

### 3. 用户确认流程

在执行恢复前询问用户：

```bash
# 添加确认步骤
python restore_context.py --confirm
```

**输出示例：**
```
✅ 上下文已恢复

当前项目：
1. Hermes Plan - 进行中

是否继续之前的工作？(y/n)
```

---

## Telegram 集成

### 1. Telegram 消息分块

长消息自动分割发送：

```bash
# Telegram 模式（自动分块）
python restore_context.py --telegram

# Telegram + 详细模式
python restore_context.py --telegram --level detailed

# Telegram + 自动模式
python restore_context.py --telegram --auto --quiet
```

**工作原理：**
- 消息超过 4000 字符时自动分块
- 每块带有 `[1/3]`, `[2/3]` 等标记
- 保持消息完整性，不丢失内容

### 2. 分块参数调整

```bash
# 自定义最大长度
python restore_context.py --telegram --max-length 3000

# 自定义前缀和后缀
python restore_context.py --telegram --chunk-prefix "【续】" --chunk-suffix "【完】"
```

### 3. Telegram + 外部通知

```bash
#!/bin/bash
# 通知脚本示例

# 检测变化并通知
python restore_context.py --auto --quiet

# 如果有变化，发送 Telegram 通知
if [ $? -eq 0 ]; then
    curl -s -X POST "https://api.telegram.org/bot$TOKEN/sendMessage" \
        -d "chat_id=$CHAT_ID" \
        -d "text=上下文已更新，请查看详情"
fi
```

---

## Cron 定时任务

### 1. 安装自动监控

```bash
# 使用脚本安装（默认每5分钟）
python restore_context.py --install-cron

# 自定义检查间隔（10分钟）
python restore_context.py --install-cron --cron-interval 10

# 每30分钟检查
python restore_context.py --install-cron --cron-interval 30
```

**输出示例：**
```
✅ Cron script created: /home/athur/.openclaw/workspace/skills/context-restore/scripts/auto_context_monitor.sh
ℹ️  To install, run:
  echo "*/5 * * * * /home/athur/.openclaw/workspace/skills/context-restore/scripts/auto_context_monitor.sh >> /var/log/context_monitor.log 2>&1" >> ~/.crontab
  crontab ~/.crontab
```

### 2. 手动安装 Cron

```bash
# 方法1：直接添加到 crontab
echo "*/5 * * * * /home/athur/.openclaw/workspace/skills/context-restore/scripts/restore_context.py --auto --quiet >> ~/.context_restore.log 2>&1" | crontab -

# 方法2：编辑 crontab
crontab -e
# 添加：
# */5 * * * * /home/athur/.openclaw/workspace/skills/context-restore/scripts/restore_context.py --auto --quiet >> ~/.context_restore.log 2>&1
```

### 3. Cron 输出配置

```bash
# 输出到日志文件
python restore_context.py --auto --quiet >> /var/log/context_restore.log 2>&1

# 每天轮转日志
0 0 * * * mv /var/log/context_restore.log /var/log/context_restore_$(date +\%Y\%m\%d).log

# 输出到 syslog
python restore_context.py --auto --quiet | logger -t context-restore
```

### 4. 监控脚本示例

```bash
#!/bin/bash
# auto_context_monitor.sh

CONTEXT_FILE="/home/athur/.openclaw/workspace/compressed_context/latest_compressed.json"
LOG_FILE="/var/log/context_monitor.log"

echo "[$(date)] Checking for context changes..."

if python3 /home/athur/.openclaw/workspace/skills/context-restore/scripts/restore_context.py --check-only --file "$CONTEXT_FILE"; then
    echo "[$(date)] No changes detected"
else
    echo "[$(date)] Context changed! Restoring..."
    python3 /home/athur/.openclaw/workspace/skills/context-restore/scripts/restore_context.py \
        --auto --quiet --file "$CONTEXT_FILE" >> "$LOG_FILE" 2>&1
fi
```

---

## 常见问题

### Q1: 文件找不到错误

**问题：** `FileNotFoundError: [Errno 2] No such file or directory`

**解决：**
```bash
# 检查文件是否存在
ls -la /home/athur/.openclaw/workspace/compressed_context/latest_compressed.json

# 使用绝对路径
python restore_context.py --file /home/athur/.openclaw/workspace/compressed_context/latest_compressed.json
```

### Q2: JSON 解析错误

**问题：** `JSONDecodeError: Expecting value`

**解决：**
```bash
# 检查文件内容
cat /path/to/context.json | head -20

# 可能是空文件，尝试使用默认文件
python restore_context.py
```

### Q3: 权限错误

**问题：** `PermissionError: [Errno 13] Permission denied`

**解决：**
```bash
# 检查文件权限
ls -la /path/to/context.json

# 修改权限
chmod 644 /path/to/context.json
```

### Q4: 静默模式无输出

**问题：** `--quiet` 模式下完全没有输出

**解决：** 这是正常行为，静默模式只输出错误或警告：
```bash
# 检查错误日志
python restore_context.py --auto --quiet 2>&1 | cat

# 临时切换到详细模式调试
python restore_context.py --auto --level detailed
```

### Q5: Cron 不执行

**问题：** 设置了 cron 但没有执行

**解决：**
```bash
# 检查 cron 服务状态
systemctl status cron

# 检查 crontab 配置
crontab -l

# 检查 cron 日志
grep CRON /var/log/syslog

# 手动测试脚本
/home/athur/.openclaw/workspace/skills/context-restore/scripts/restore_context.py --check-only
```

### Q6: 对比功能无结果

**问题：** `--diff` 对比两个文件但显示无差异

**解决：**
```bash
# 检查两个文件是否不同
diff /path/to/old.json /path/to/new.json

# 使用详细模式查看
python restore_context.py --diff old.json new.json --level detailed

# 确保文件格式正确
cat old.json | python -m json.tool
```

---

## 性能优化

### 1. 缓存哈希

自动检测会缓存文件哈希，避免重复读取：

```bash
# 哈希缓存目录
ls -la /home/athur/.openclaw/workspace/tmp/context_hashes/

# 手动清除缓存（强制重新检测）
rm /home/athur/.openclaw/workspace/tmp/context_hashes/latest_hash.json
python restore_context.py --check-only
```

### 2. 大文件优化

```bash
# 使用极简模式减少处理
python restore_context.py --level minimal

# 跳过时间线提取
python restore_context.py --level minimal --timeline false

# 只处理最近的内容
python restore_context.py --since 2026-01-01
```

---

## 最佳实践

### 1. 日常使用流程

```bash
# 1. 快速检查当前状态
python restore_context.py --level minimal

# 2. 查看详细进展
python restore_context.py --level normal

# 3. 如果需要，对比昨天
python restore_context.py --diff yesterday.json today.json --level minimal
```

### 2. 会话结束时

```bash
# 保存上下文（确保有最新内容）
# 触发 context-save（由系统自动执行）

# 验证保存成功
ls -la /home/athur/.openclaw/workspace/compressed_context/latest_compressed.json
```

### 3. 自动化建议

```bash
# 建议的 cron 配置（每5分钟检查）
*/5 * * * * /home/athur/.openclaw/workspace/skills/context-restore/scripts/restore_context.py --auto --quiet >> ~/.context_restore.log 2>&1
```

---

## 相关链接

- [SKILL.md](../SKILL.md) - 完整技能文档
- [API.md](./API.md) - API 参考
- [README.md](../README.md) - 项目说明
