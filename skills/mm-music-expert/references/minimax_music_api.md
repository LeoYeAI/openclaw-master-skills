# MiniMax Music Generation API

Source: https://platform.minimaxi.com/docs/api-reference/music-generation

## Endpoint

`POST https://api.minimaxi.com/v1/music_generation`

## Auth

`Authorization: Bearer <API_KEY>`

Read from env: `MINIMAX_MUSIC_API_KEY`

## Models

| Model | Recommended | is_instrumental | lyrics_optimizer |
|-------|-------------|-----------------|------------------|
| `music-2.5+` | ✅ Yes | ✅ Supported | ✅ Supported |
| `music-2.5` | | ❌ | ✅ Supported |

## Request Body (JSON)

### Required
- `model`: `"music-2.5+"` (recommended) or `"music-2.5"`

### Conditional
- `lyrics` (string, 1–3500 chars)
  - **Required** for `music-2.5` and `music-2.5+` non-instrumental
  - **Optional** for `music-2.5+` with `is_instrumental: true`
  - When `lyrics_optimizer: true` and `lyrics` is empty, system auto-generates lyrics from prompt
  - Line separator: `\n`
  - Supported structure tags: `[Intro]`, `[Verse]`, `[Pre Chorus]`, `[Chorus]`, `[Post Chorus]`, `[Bridge]`, `[Interlude]`, `[Outro]`, `[Transition]`, `[Break]`, `[Hook]`, `[Build Up]`, `[Inst]`, `[Solo]`
- `prompt` (string, 0–2000 chars)
  - **Required** [1, 2000] for `music-2.5+` with `is_instrumental: true`
  - **Optional** [0, 2000] for `music-2.5` / `music-2.5+` non-instrumental

### Optional
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `is_instrumental` | boolean | false | Pure music without vocals. **music-2.5+ only** |
| `lyrics_optimizer` | boolean | false | Auto-generate lyrics from prompt when lyrics is empty |
| `stream` | boolean | false | Streaming mode (hex output only) |
| `output_format` | string | `"hex"` | `"hex"` or `"url"` (URL valid 24h) |
| `aigc_watermark` | boolean | false | Append watermark. Non-stream only |
| `audio_setting` | object | — | See below |

### audio_setting
| Field | Type | Values |
|-------|------|--------|
| `sample_rate` | integer | 16000, 24000, 32000, 44100 |
| `bitrate` | integer | 32000, 64000, 128000, 256000 |
| `format` | string | `"mp3"`, `"wav"`, `"pcm"` |

## Example Payloads

### Standard Song
```json
{
  "model": "music-2.5+",
  "prompt": "独立民谣,忧郁,内省,渴望,独自漫步,咖啡馆",
  "lyrics": "[verse]\n街灯微亮晚风轻抚\n影子拉长独自漫步\n[chorus]\n推开木门香气弥漫\n熟悉的角落陌生人看",
  "audio_setting": { "sample_rate": 44100, "bitrate": 256000, "format": "mp3" }
}
```

### Pure Music (music-2.5+ only)
```json
{
  "model": "music-2.5+",
  "prompt": "coffee shop, ambient, relaxing, piano",
  "is_instrumental": true
}
```

### Auto-Generated Lyrics
```json
{
  "model": "music-2.5+",
  "prompt": "upbeat pop, summer vibes, happy",
  "lyrics_optimizer": true
}
```

## Response

```json
{
  "data": {
    "audio": "<hex string or URL>",
    "status": 2
  },
  "trace_id": "...",
  "extra_info": {
    "music_duration": 25364,
    "music_sample_rate": 44100,
    "music_channel": 2,
    "bitrate": 256000,
    "music_size": 813651
  },
  "base_resp": {
    "status_code": 0,
    "status_msg": "success"
  }
}
```

### Status Codes
| Code | Meaning |
|------|---------|
| 0 | Success |
| 1002 | Rate limited |
| 1004 | Auth failed |
| 1008 | Insufficient balance |
| 2013 | Invalid parameters |
| 2049 | Invalid API key |

### Generation Status (`data.status`)
| Value | Meaning |
|-------|---------|
| 1 | Generating |
| 2 | Completed |
