# OpenClaw 安全巡检定时任务配置指南

## ⚠️ 重要警告（必读）

### 必须使用 `openclaw cron`，禁止使用系统 crontab

❌ **错误做法**：使用 `crontab -e` 或编辑 `/etc/crontab`


✅ **正确做法**：使用 OpenClaw 内置的 cron 系统
```bash
openclaw cron add ...
```

**原因**：
1. 系统 crontab 无法正确初始化 OpenClaw 环境变量和会话
2. 会导致执行失败、权限问题或推送异常
3. `openclaw cron` 自动处理隔离会话、超时、推送等逻辑

## 快速配置

### 使用 OpenClaw Cron 注册

```bash
openclaw cron add \
  --name "changeway-security-audit" \
  --description "每晚安全巡检" \
  --cron "45 23 * * *" \
  --tz "Asia/Shanghai" \
  --session "isolated" \
  --message "Run the security audit script: node <skill-path>/scripts/openclaw-hybrid-audit-changeway.js — then from the output extract and report ONLY these three items: (1) the line containing PASS/FAIL/SKIP counts, (2) the report file path from the line starting with '详细审计报告已保存至'. Do NOT include the full script output." \
  --announce \
  --channel <channel> \
  --to <your-chat-id> \
  --timeout-seconds 900 \
  --thinking off
```

> ❌ **禁止在 cron 的 `--message` 中添加 `--push`**。`--push` 会向远端持续发送设备标识（MAC、主机名、agent_id）和 Skill 清单，不适合在未经每次人工确认的定时任务中使用。如需使用完整检测，请手动运行并在 SKILL.md 第三步选择并确认。

### 参数说明

| 参数 | 说明 | 建议值 |
|------|------|--------|
| `--name` | 任务唯一标识 | `changeway-security-audit` |
| `--cron` | Cron 表达式 | `23 45 * * *` (每天 23:45) |
| `--tz` | 时区 | `Asia/Shanghai` 或你的本地时区 |
| `--session` | 会话类型 | `isolated` (隔离环境更安全) |
| `--message` | 执行命令 | 见下方注意事项 |
| `--timeout-seconds` | 超时时间 | `300` (必须 ≥300s，否则可能超时失败) |

## 注意事项

### 关于 --push 参数

❌ **cron 定时任务中严禁使用 `--push`**。

`--push` 会向远端持续发送设备标识（MAC 地址、主机名、持久化 agent_id）和本机完整 Skill 清单，属于隐私敏感操作，必须每次由用户手动确认后才能执行。将 `--push` 写入 cron 会导致设备信息被长期自动上报，违背知情同意原则。

如需使用完整检测（威胁情报查询），请**手动运行**安全巡检并在第三步选择并完成知情确认。


### ⚠️ 避坑指南

1. **timeout 必须 ≥ 300s**
   - isolated session 需要冷启动 Agent
   - 120s 会因超时被杀

2. **--to 必须用 chatId**
   - 不能用用户名（如 "L"）
   - Telegram 需要数字 chatId

3. **message 不要写"发送给某人"**
   - isolated Agent 无法解析用户名
   - 推送由 `--announce` 框架处理
   - 维持示例写法，cron 的 `--message` 中不得包含 `--push`

4. **推送偶发失败**
   - Telegram 等平台偶发 502/503
   - 报告始终保存在本地：`~/.openclaw/security-reports/`
   - 查看历史：`openclaw cron runs --id <jobId>`

## 查看巡检历史

```bash
# 列出所有 cron 任务
openclaw cron list

# 查看特定任务的执行历史
openclaw cron runs --id <job-id>
```

## 修改/删除定时任务

```bash
# 删除任务
openclaw cron remove --id <job-id>

# 重新添加（先删后加）
openclaw cron remove --id nightly-security-audit
openclaw cron add ...
```

## 手动测试

配置前先手动测试脚本能否正常执行：

```bash
# 进入 skill 目录
cd <skill-path>

# 本地模式（无网络）
node scripts/openclaw-hybrid-audit-changeway.js

# 完整模式（含威胁情报）— ⚠️ 仅限手动运行，不得写入 cron
# 运行前须在 SKILL.md 第三步完成知情确认（回复"2 已了解"）
node scripts/openclaw-hybrid-audit-changeway.js --push
```

## 常见错误及修复

### 错误 1：使用了系统 crontab
**现象**：任务显示在 `crontab -l` 中，但执行失败或没有推送
**修复**：
```bash
# 1. 删除系统 crontab 中的任务
crontab -e  # 删除相关行

# 2. 使用 openclaw cron 重新添加
openclaw cron add \
  --name "changeway-security-audit" \
  --description "每晚安全巡检" \
  --cron "45 23 * * *" \
  --tz "Asia/Shanghai" \
  --session "isolated" \
  --message "Run the security audit script: node <skill-path>/scripts/openclaw-hybrid-audit-changeway.js — then from the output extract and report ONLY these three items: (1) the line containing PASS/FAIL/SKIP counts, (2) the report file path from the line starting with '详细审计报告已保存至'. Do NOT include the full script output." \
  --announce \
  --channel <channel> \
  --to <your-chat-id> \
  --timeout-seconds 900 \
  --thinking off
```

### 错误 2：--message 中使用了相对路径
**现象**：定时任务执行时提示找不到脚本
**修复**：使用绝对路径 `<skill-path>/scripts/openclaw-hybrid-audit-changeway.js`

### 错误 3：--session 未设置为 isolated
**现象**：任务执行时权限错误，或无法访问安全报告
**修复**：必须添加 `--session "isolated"`

### 错误 4：timeout 设置过短
**现象**：任务被强制终止，报告不完整
**修复**：`--timeout-seconds 600`（必须 ≥ 600）
