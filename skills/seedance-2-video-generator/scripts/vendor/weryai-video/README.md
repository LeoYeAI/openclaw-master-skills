# WeryAI Video Runtime

共享视频 runtime（供 `video/weryai-video-generator` 等脚本复用）。

当前包含：

- text/image/multi-image submit 与 wait
- almighty-reference-to-video submit 与 wait 自动路由
- 复用 `core/weryai-core/upload.js` 的通用上传能力（`POST /v1/generation/upload-file`）
- 输入归一化、模型能力校验、dry-run 预览
- `wait` 支持任务超时分级：`short`（5 分钟）与 `long`（20 分钟）
- `task_class=auto` 会按最终提交模式映射：`text_to_video` -> `short`，其余视频模式 -> `long`
- 兼容覆盖：`WERYAI_POLL_TIMEOUT_MS` 优先级高于分级超时
