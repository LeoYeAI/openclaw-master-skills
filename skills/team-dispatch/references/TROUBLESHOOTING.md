# Team Dispatch Troubleshooting

## 1) 404 Requested model is not valid
**原因**：配置的模型在当前 provider/账号不可用。

**建议**：切到稳定基线模型：
```bash
bash ~/skills/team-dispatch/scripts/setup.sh --baseline-models
openclaw gateway restart
```

## 2) zenmux 403 quota limit
**原因**：订阅额度用尽。

**建议**：
- 临时切到 bailian/qwen3.5-plus 或其他可用 provider
- 或等待滚动窗口恢复

## 3) openai/* No API key found
**原因**：openai provider 需要 OPENAI_API_KEY。

**建议**：
- 使用 OAuth 口径：`openai-codex/gpt-5.3-codex`
- 或设置 OPENAI_API_KEY

## 4) 并发上限 5/5
**表现**：spawn 被拒绝（forbidden）。

**建议**：
- 任务进入 queued，等其它任务完成自动出队
- 对大项目拆分多个 project

## 5) Gateway 重启导致 completion event 丢失
**现象**：任务其实已 done，但没有收到事件，项目看起来“卡住”。

**建议**：
- 开启 watcher 做低频兜底（只检测卡死/超时）：
  ```bash
  INTERVAL=300 GRACE=20 bash ~/skills/team-dispatch/scripts/watch.sh
  ```
- 或人工补查：查看最近子任务运行记录，并在项目 JSON 中补录 task.result / task.status
