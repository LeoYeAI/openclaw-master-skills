# Endpoint Params

## generate_speech
- Method: `POST`
- Path: `/cut_jianying/generate_speech`
- 用途：将文案合成为语音并写入草稿，返回音频地址与草稿信息。

### 请求参数
- `text` (string, required): 待合成文本。
- `provider` (string, required): 供应商枚举：`azure` / `volc` / `minimax` / `fish`。
- `voice_id` (string, required): 音色 ID。
- `model` (string, optional): 当前仅 `provider=minimax` 生效，可选 `speech-2.6-turbo` / `speech-2.6-hd`。
- `volume` (number, optional): 音量强度，范围[-100, 100]，默认0，0表示正常音量，-100表示静音。
- `target_start` (number, optional): 目标入轨时间，单位秒，默认0，0表示从开始播放。
- `effect_type` (string, optional): 音效类型，例如 `麦霸`。枚举值来源 `references/enums/audio_effect_types.json` 的 `items.name`。
- `effect_params` (array<number>, optional): 音效参数数组，与所选 `effect_type` 对应的 `items.params` 一一对应；有几个参数项就传几个数值。
- `start`: (number, optional): 生成音频后，添加到轨道时截取生成音频的开始时间，一般不填。
- `end`: (number, optional): 生成音频后，添加到轨道时截取生成音频的结束时间，一般不填。
- `draft_id`: (string, optional): 草稿id, 基于某个草稿继续添加。
- `speed`: (number, optional): 倍速，>1表示加速。
- `track_name`: (string, optional): 目标轨道名称。
- `fade_in_duration`: (number, optional): 音频淡入时间，单位秒，支持小数。
- `fade_out_duration`: (number, optional): 音频淡出时间，单位秒，支持小数。

### 示例请求
```bash
curl --location --request POST 'https://open.vectcut.com/cut_jianying/generate_speech' \
--header 'Authorization: Bearer <token>' \
--header 'Content-Type: application/json' \
--data-raw '{
  "text":"今天的视频，就给大家带来一个福利。",
  "provider":"minimax",
  "model":"speech-2.6-turbo",
  "voice_id":"audiobook_male_1",
  "volume":10,
  "target_start":3,
  "effect_type":"麦霸",
  "effect_params":[45,80]
}'
```

### 关键响应字段
- `success` (boolean)
- `error` (string)
- `output.audio_url` (string，可独立复用)
- `output.draft_id` (string)
- `output.draft_url` (string)
- `output.material_id` (string，表示已成功插入草稿)

### 错误返回
- HTTP 非 2xx：鉴权或服务异常，先检查 `VECTCUT_API_KEY`。
- `success=false` 或 `error` 非空：业务失败，修正参数后重试。
- 响应非 JSON：中止流程并保留原始响应。
- 缺少 `output.audio_url`：视为语音结果不可用。
- 需要确认入稿时，若缺少 `output.material_id`：视为未确认插入草稿成功。

### 枚举引用
- `references/enums/minimax_voiceids.json`
- `references/enums/azure_voiceids.json`
- `references/enums/volc_voiceids.json`
- `references/enums/fish_voiceids.json`

## fish_clone
- Method: `POST`
- Path: `/llm/tts/fish/clone_voice`
- 用途：克隆用户音色并返回可用于 `generate_speech` 的 `voice_id`。

### 请求参数
- `file_url` (string, required): 音频文件链接，需满足：安静人声录音、情感饱满、时长 10~30 秒。
- `title` (string, optional): 音色命名，便于后续检索。

### 示例请求
```bash
curl --location --request POST 'https://open.vectcut.com/llm/tts/fish/clone_voice' \
--header 'Authorization: Bearer <token>' \
--header 'Content-Type: application/json' \
--data-raw '{
  "file_url":"https://oss-jianying-resource.oss-cn-hangzhou.aliyuncs.com/dfd_707531.mp3",
  "title":"我的克隆音色"
}'
```

### 关键响应字段
- `success` (boolean)
- `voice_id` (string)

### 错误返回
- HTTP 非 2xx：鉴权或服务异常。
- `success=false`：克隆失败，先检查音频质量与时长。
- 缺少 `voice_id`：视为不可用结果。

## voice_assets
- Method: `GET`
- Path: `/llm/tts/voice_assets`
- 用途：查看已克隆的音色资产列表。

### 请求参数
- `limit` (integer, optional): 一次请求总数，示例 `20`。
- `offset` (integer, optional): 偏移量，示例 `0`。
- `provider` (string, optional): 克隆模型，`fish` 或 `minimax`；为空时查询全部。

### 示例请求
```bash
curl --location --request GET 'https://open.vectcut.com/llm/tts/voice_assets?limit=20&offset=0&provider=fish' \
--header 'Authorization: Bearer <token>'
```

### 关键响应字段
- 响应体字段以服务端实际返回为准，至少要求响应为合法 JSON。

### 错误返回
- HTTP 非 2xx：鉴权或服务异常。
- 响应非 JSON：中止流程并保留原始响应。