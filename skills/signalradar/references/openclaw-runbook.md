# OpenClaw Runbook

## 1) 真人用户的安装体验（先能跑起来）

> **重要变更（2026-02）：SignalRadar 已与 openclaw cron 解耦。**
> 安装后不再自动创建 cron 作业，用户手动运行或自行配置调度。

在 OpenClaw 对话里直接说自然语言即可，不要求先写命令。建议用这句：

```text
请安装 signalradar skill，阈值 5%，去重关闭，直接推送。
```

如果你的 OpenClaw 环境支持 ClawHub CLI，也可以命令行安装：

```bash
clawhub install signalradar
```

## 2) 关键文件

- 技能入口：`<workspace>/skills/signalradar/SKILL.md`
- 环境模板：`<workspace>/skills/signalradar/.env.example`
- 配置模板：`<workspace>/skills/signalradar/config.example.json`

## 3) 验证技能是否被识别

```bash
openclaw skills list
openclaw skills info signalradar
openclaw skills check
```

## 4) 推荐配置方式（beta）

先准备配置文件：

```bash
WORKSPACE_ROOT=/path/to/your/workspace
mkdir -p "$WORKSPACE_ROOT/config"
cp "$WORKSPACE_ROOT/skills/signalradar/config.example.json" "$WORKSPACE_ROOT/config/signalradar_config.json"
```

然后用 `--config` 启动任务。

## 5) 生产任务命令模板（含 dry-run）

基础监测任务（示例 `ai`）：

```bash
python3 "$WORKSPACE_ROOT/skills/signalradar/scripts/run_signalradar_job.py" --mode ai --workspace-root "$WORKSPACE_ROOT" --config "$WORKSPACE_ROOT/config/signalradar_config.json" --cleanup-expired --cleanup-ttl-days 45
```

建议首次先 dry-run：

```bash
python3 "$WORKSPACE_ROOT/skills/signalradar/scripts/run_signalradar_job.py" --mode ai --workspace-root "$WORKSPACE_ROOT" --config "$WORKSPACE_ROOT/config/signalradar_config.json" --dry-run
```

说明：

- `--dry-run` 跑完整判定与路由封装，但不写 baseline / dedup / digest 状态。
- `--cleanup-expired` 会清理无效或过期 baseline 文件。
- `--mode` 支持：`ai`、`crypto`、`geopolitics`、`watchlist-refresh`。

## 6) Notion 协同（watchlist-refresh）

```bash
python3 "$WORKSPACE_ROOT/skills/signalradar/scripts/run_signalradar_job.py" --mode watchlist-refresh --workspace-root "$WORKSPACE_ROOT" --notion-page-id YOUR_PARENT_PAGE_ID --notion-root-page-title SignalRadar --notion-manual-page-title SignalRadar_Manual_Entries
```

手动条目格式支持：

- `Category | Question | EndDate`
- `Category | Question | EndDate | WatchLevel | ThresholdPP`
- `Polymarket URL`

说明：

- `WatchLevel`: `normal`（默认）/`important`
- `ThresholdPP`: 单条目阈值覆盖（abs_pp）
- 缺少依赖脚本或同步失败时，会返回 JSON error envelope（`error_code` + `message` + `details`）

## 7) Digest 参数说明

- 用户级参数：`digest.frequency=off|daily|weekly|biweekly`（默认 `off`）
- 条目级参数：`watch_level=normal|important`（默认 `normal`）
- 当 `frequency != off` 时，只汇总 `important` 条目
- 如果全部条目都是 `normal`，digest 不推送

## 8) 半自动发现与继任确认

话题发现（候选打分）：

```bash
python3 "$WORKSPACE_ROOT/skills/signalradar/scripts/discover_entries.py" --topic "US-China tech competition" --top-k 20 --out-json "$WORKSPACE_ROOT/cache/signalradar/discover_us_china.json"
```

继任确认计划：

```bash
python3 "$WORKSPACE_ROOT/skills/signalradar/scripts/plan_rollover_actions.py" --rollover-md "$WORKSPACE_ROOT/memory/polymarket_rollover_2026.md" --auto-threshold 0.85 --out-json "$WORKSPACE_ROOT/cache/signalradar/rollover_plan.json"
```

## 9) 发布到 ClawHub（建议 beta）

发布前最小阻断检查（MVP）：

```bash
python3 "$WORKSPACE_ROOT/skills/signalradar/scripts/sr_prepublish_gate.py" --json
# 或者显式指定窗口（例如最近 24 小时）：
python3 "$WORKSPACE_ROOT/skills/signalradar/scripts/sr_prepublish_gate.py" --lookback-hours 24 --json
```

如果输出 `ok=false`，先排障，不发布。

安装后最小连通性冒烟测试（MVP）：

```bash
python3 "$WORKSPACE_ROOT/skills/signalradar/scripts/sr_smoke_test.py" --json
```

只有 `ok=true` 才算安装成功。

```bash
clawhub login
clawhub publish "$WORKSPACE_ROOT/skills/signalradar" --slug signalradar --name "SignalRadar" --version 0.1.0-beta.1 --changelog "beta: config+digest+cleanup+discovery" --tags beta
```

## 10) 更新已安装版本

```bash
clawhub update signalradar
```
