# Team Dispatch Config (C option)

## Where

- Built-in default (single source): `~/skills/team-dispatch/config.json`

## Paths

- `paths.projectsRoot` (default: `~/work`)
  - Real code/projects live here.
  - Recommendation: agents create project folders like: `~/work/<project>`
- User override: `~/.openclaw/configs/team-dispatch.json`

Generate user override:
```bash
bash ~/skills/team-dispatch/scripts/setup-config.sh
```

## Goals

- Keep `agentId` portable and stable across machines.
- Allow per-agent presentation and notification routing:
  - `displayName` (human-friendly)
  - `username` (optional)
  - `notify.telegram.chatId` (optional)

## Notification policy

`notifyPolicy`:
- `failures-only` (recommended): only notify on `failed/timeout/blocked`
- `project-complete`: notify when project becomes `completed`
- `all-tasks`: notify on every task completion

## Watcher（后台周期任务）

- `team.watcher.enabled` (default: `true`)
- `team.watcher.backend` (default: `auto`)
  - `auto`: 系统调度优先（launchd/systemd/cron），失败才 fallback 到 openclaw-cron（更省 token）
  - `openclaw-cron`: OpenClaw 内置 cron（统一管理，开箱即用；但会消耗模型 token）
  - `launchd|systemd|cron`: 强制指定具体系统调度器
- `team.watcher.interval` (seconds)
- `team.watcher.grace` (seconds)

## Daily Summary（每日总结）

- `team.dailySummary.enabled` (default: `true`)
- `team.dailySummary.backend` (default: `openclaw-cron`)
- `team.dailySummary.cron` (default: `0 22 * * *`)
  - Cron 表达式，5 字段标准格式：`分 时 日 月 周`
  - 默认每天 22:00 执行
  - 示例：`0 9 * * 1-5` 表示工作日每天早上 9 点
- `team.dailySummary.timezone` (default: 空，使用系统时区)
  - 可选：IANA 时区标识符，如 `Asia/Shanghai`、`America/New_York`
- `team.dailySummary.jobName` (default: `team-dispatch.daily-summary`)
- `team.dailySummary.jobDescription`

功能：每天定时生成 Team Dispatch 日报，汇总：
- 当天完成的任务（根据 completedAt 判断）
- 进行中的任务状态
- 失败或卡住的任务

## Telegram notification

Dispatcher-level behavior (not subagent):
- Based on `notifyPolicy`, when a task/project hits the matching state, the main agent reads config and sends a message to the configured Telegram chat.

Recommended payload:
- project name
- task id
- agentId + displayName
- status + short result/error
- deliverables (paths)

## Example
```json
{
  "team": {
    "agents": {
      "coder": {
        "displayName": "闪电",
        "notify": { "telegram": { "enabled": true, "chatId": "telegram:569110000" } }
      }
    }
  }
}
```
