# CANN Review Skill 安装指南

## 安装步骤

### 1. 安装 Skill

```bash
# 从本地安装
cd /Users/zj/.openclaw/workspace/skills/cann-review
claw install .

# 或从 ClawHub 安装（如果已发布）
claw install cann-review
```

### 2. 配置自动审查（可选）

如果你想启用定时自动审查功能，需要配置 cron 任务。

#### 方法一：使用 OpenClaw Cron 工具

1. **查看当前 cron 状态**
```bash
claw cron status
```

2. **添加定时任务**

编辑 cron.yaml 文件，根据需要调整调度时间：

```yaml
auto_review:
  schedule: "0 */2 * * *"  # 每 2 小时执行一次
  enabled: true
```

3. **应用 cron 配置**

使用 OpenClaw 的 cron 工具添加任务：

```bash
# 添加自动审查任务
claw cron add \
  --name "cann-auto-review" \
  --schedule "0 */2 * * *" \
  --skill "cann-review" \
  --params '{"auto_mode": true, "max_reviews": 5}'
```

或者手动配置（需要管理员权限）：

```bash
# 编辑 crontab
crontab -e

# 添加以下行（每 2 小时执行一次）
0 */2 * * * cd /Users/zj/.openclaw && claw run cann-review --auto-mode --max-reviews 5
```

#### 方法二：使用 OpenClaw Gateway Cron

如果你使用 OpenClaw Gateway，可以通过 API 添加 cron 任务：

```bash
curl -X POST http://localhost:3000/api/cron/add \
  -H "Content-Type: application/json" \
  -d '{
    "name": "cann-auto-review",
    "schedule": {"kind": "cron", "expr": "0 */2 * * *"},
    "payload": {
      "kind": "agentTurn",
      "message": "使用 cann-review skill 审查未读 MR",
      "params": {
        "auto_mode": true,
        "max_reviews": 5
      }
    },
    "sessionTarget": "isolated",
    "enabled": true
  }'
```

### 3. 验证安装

```bash
# 测试手动审查
claw run cann-review --pr-url "https://gitcode.com/cann/runtime/pull/472"

# 测试自动审查（干运行）
claw run cann-review --auto-mode --max-reviews 1 --dry-run
```

## 配置选项

### Cron 调度表达式

常用调度示例：

| 表达式 | 说明 |
|--------|------|
| `0 */2 * * *` | 每 2 小时 |
| `0 9,15 * * *` | 每天 9:00 和 15:00 |
| `0 9 * * 1-5` | 周一到周五 9:00 |
| `0 10 * * 0,6` | 周末 10:00 |
| `*/30 * * * *` | 每 30 分钟 |

### 审查参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `focus_areas` | all | 审查重点（memory/security/readability/all） |
| `severity_threshold` | medium | LGTM 阈值（low/medium/high） |
| `max_reviews` | 5 | 单次最大审查数量 |
| `send_summary` | true | 是否发送汇总通知 |

## 故障排查

### 浏览器无法启动

确保 OpenClaw 内置浏览器可用：

```bash
claw browser status
claw browser start
```

### Cron 任务未执行

检查 cron 日志：

```bash
# 查看 OpenClaw cron 日志
tail -f /Users/zj/.openclaw/logs/cron.log

# 或查看系统 cron 日志
grep CRON /var/log/syslog
```

### 无法访问 GitCode

确保已登录 GitCode：

```bash
# 使用浏览器登录
claw browser open "https://gitcode.com"
```

## 卸载

```bash
# 移除 skill
claw uninstall cann-review

# 移除 cron 任务
claw cron remove --name "cann-auto-review"
```

## 更新

```bash
# 更新 skill
claw update cann-review

# 或从源码更新
cd /Users/zj/.openclaw/workspace/skills/cann-review
git pull
claw install .
```
