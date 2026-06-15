# 素材感知端点规则（get_duration / get_resolution / video_detail）

## 适用范围
- `POST /cut_jianying/get_duration`
- `POST /cut_jianying/get_resolution`
- `POST /cut_jianying/video_detail`

## 专属异常处理
- 当 HTTP 状态码非 2xx：
  - 含义：鉴权失败、参数非法或服务端异常。
  - 处理：记录状态码与响应体；若为鉴权问题先检查 `VECTCUT_API_KEY`，再重试 1 次。
  - 重试上限：1 次。

- 当响应体不是合法 JSON：
  - 含义：网关异常或服务返回格式不符合约定。
  - 处理：保留原始响应体并中止，不做盲目重试。
  - 重试上限：0 次。

- 当 `success=false` 或 `error` 非空：
  - 含义：业务失败（如 URL 不可访问、媒体解析失败）。
  - 处理：保留 `error` 与原始 `url`，更换可访问媒体 URL 后重试 1 次。
  - 重试上限：1 次。

- 当关键字段缺失：
  - `get_duration` 缺少 `output.duration` 或者 `output.duration` 为0。
  - `get_resolution` 缺少 `output.width` 或 `output.height` 或者为0。
  - `video_detail` 缺少 `output` 或 `output.video_detail` 为空
  - 含义：关键字段缺失，无法进入后续编排。
  - 处理：标记为不可继续，要求更换素材 URL 或稍后重试。
  - 重试上限：1 次。

## 诊断上下文
失败时至少保留：
- `endpoint`
- `url`
- `error`
- `status_code`
- `raw_response`