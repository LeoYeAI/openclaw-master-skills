# 预处理端点规则（extract_audio / split_video）

## 适用范围
- `POST /process/extract_audio`
- `POST /process/split_video`

## 调用策略
- 在入草稿前优先做素材预处理：先裁切再编排，可减少时间线修正成本。
- `extract_audio`：从视频提取纯音频，适合做配音重编、B-roll 替换前的音轨保留。
- `split_video`：按时间区间切分视频或音频，常用于混剪切段、节奏重组、片段复用。
- 时间单位统一使用秒（支持小数），并满足 `0 <= start < end`。

## 入参与边界
- `extract_audio` 必填：`video_url`（公网可访问）。
- `split_video` 必填：`video_url`、`start`、`end`。
- `split_video` 约束：`start/end` 必须为数值，且 `end` 不能超过素材总时长。

## 专属异常处理
- HTTP 非 2xx：
  - 含义：鉴权、参数或服务异常。
  - 处理：检查 `VECTCUT_API_KEY` 与请求体后重试 1 次。
- 响应非 JSON：
  - 含义：网关或上游返回异常。
  - 处理：保留原始响应并中止。
- `code != 200` 或 `message` 非 Success：
  - 含义：业务失败（URL 不可访问、时间段非法等）。
  - 处理：修正参数后重试 1 次。
- 缺少 `data.public_url`：
  - 含义：处理结果不可用。
  - 处理：重试 1 次。

## 诊断上下文
失败时至少保留：
- `endpoint`
- `video_url`
- `start`
- `end`
- `status_code`
- `code`
- `message`
- `raw_response`