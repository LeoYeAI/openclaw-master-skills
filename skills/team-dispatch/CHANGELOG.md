# Changelog

## Unreleased

## v1.0.8 (2026-03-09)
- feat: Add `shield` security audit agent (🛡️ 盾卫)
- feat: New workflow templates include security audit stage
- feat: Watcher now sends detailed alerts directly to main agent via `openclaw sessions send`
- feat: Watcher includes full task context (project, agent, description, error, retries) in alerts
- refactor: Enhanced `watch.py` with structured TaskDetail and rich alert messages
- config: Change default watcher interval from 120s to 300s (5 minutes)
- docs: Update agent count from 6 to 7 in all references
- docs: Update all interval references from 120 to 300 seconds

## v1.0.7 (2026-03-09)
- fix(setup.sh): Fix `set -e` exit on `openclaw gateway restart` failure (use `|| true`)
- chore: Add `scripts/publish-clawhub.mjs` workaround publisher for ClawHub CLI `acceptLicenseTerms` incompatibility
- docs: Document the local ClawHub publish flow in README

## v1.0.6 (2026-03-09)
- feat: Add daily summary cron job (configurable via `team.dailySummary`)
- feat: Configurable periodic tasks with `enabled` flag in config.json
- refactor: All config languages switched to English
- refactor: Rename plist to `openclaw.team-dispatch.watch.plist` for consistency
- fix: Path expansion for `~/work` directory creation
- fix: Default backend changed from `openclaw-cron` to `auto` (system scheduler preferred)
- chore: Update default models to `gpt-5.4` (general agents) and `gpt-5.3-codex` (coder)
- chore: Update default watcher interval to 300 seconds (5 minutes)

## v1.0.5 (2026-03-09)
- fix(Clawhub): 将 plist 改为模板 `assets/launchd/openclaw.team-dispatch.watch.plist.xml`，安装时渲染到 `~/Library/LaunchAgents/` 再 bootstrap（避免 Clawhub 过滤 .plist）
- fix(Clawhub): 将 Windows watcher 安装脚本改为 `assets/windows/watch-install.ps1.txt`（避免 Clawhub 过滤 .ps1），文档说明复制改名后执行

## v1.0.4 (2026-03-09)
- refactor: watcher 安装资产归档到 `assets/`（launchd plist / Windows ps1），避免发布包缺文件
- fix: watcher 默认使用 `openclaw-cron`（用户可覆盖），watcher 配置读取改为“默认+用户覆盖 merge”
- chore: 脚本安全/一致性（去掉 `eval`；uninstall purge 更安全；setup 输出版本号动态读取）
- test: verify 增加必备资产检查（避免用户安装时才炸）

## v1.0.3 (2026-03-09)
- fix(macOS): watcher 安装改为先渲染绝对路径 LaunchAgent plist 到 `~/Library/LaunchAgents/` 再 bootstrap
- fix(macOS): 避免 launchd 因 plist 中使用 `~` 路径导致 `Bootstrap failed: 5: Input/output error`

## v1.0.2 (2026-03-09)
- watcher 默认改为 `openclaw-cron`（仍可配置切换到 `auto-system-first`/launchd/systemd/cron）
- 修复 `paths.projectsRoot` 的 `~/` 展开（避免在技能目录下创建字面 `~/work`）
- watcher 文档补齐（CONFIG.md）
- macOS LaunchAgent plist 的 watch.sh 路径改为 `~/.openclaw/skills/team-dispatch/...`（更符合软链接加载路径）

## v1.0.1 (2026-03-08)
- Publish to ClawHub (version bump only; content unchanged from v1.0.0)


## v1.0.0 (2026-03-07)
- 🌍 **Add i18n support (English/Chinese)** — Default English, switch via config
- 🌍 **添加国际化支持（中英文双语）** — 默认英文，可通过配置切换
- Add low-frequency watcher (event + scan fallback)
- Add per-agent configurable displayName/username + Telegram notify routing (configs/team-dispatch.json)
- Add doctor + baseline model shortcut
- Add postmortem template + troubleshooting docs
- Raise recommended concurrency to 10 (configurable)

### i18n Configuration / 国际化配置

```json
{
  "language": "zh"  // "en" for English, "zh" for Chinese
}
```

### Output Messages / 输出消息

| English | 中文 |
|---------|------|
| ✅ Project completed! | ✅ 项目完成！ |
| 📤 Dispatched to {agent} | 📤 已派发至 {agent} |
| ❌ Task failed: {reason} | ❌ 任务失败：{reason} |
| 📦 Final deliverables: | 📦 最终交付清单： |
| 🔎 Preview: {path} | 🔎 预览方式：{path} |

## v3.0 (2026-03-06)
- DAG-based dispatching, auto decomposition, retries/fallbacks, result injection
