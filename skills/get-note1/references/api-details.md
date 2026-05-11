# Get笔记 API 详细参考

## 目录

1. [错误码表](#错误码表)
2. [error.reason 取值表](#errorreason-取值表)
3. [限流响应结构](#限流响应结构)
4. [笔记详情独有字段](#笔记详情独有字段)
5. [新建笔记字段说明](#新建笔记字段说明)
6. [图片上传凭证返回字段](#图片上传凭证返回字段)

---

## 错误码表

| 错误码 | 说明 |
|--------|------|
| 10000 | 参数错误 |
| 10001 | 鉴权失败 |
| 10201 | 非会员 |
| 20001 | 笔记不存在 |
| 30000 | 服务调用失败 |
| 42900 | 限流 |
| 50000 | 系统错误 |

---

## error.reason 取值表

| reason | 说明 |
|--------|------|
| not_member | 非会员，引导开通：https://www.biji.com/checkout?product_alias=6AydVpYeKl |
| qps_global | 全局 QPS 超限 |
| qps_bucket | 桶级 QPS 超限 |
| quota_day | 当日配额用尽 |
| quota_month | 当月配额用尽 |

---

## 限流响应结构

429 错误时，`error` 字段中包含 `rate_limit` 对象：

```json
{
  "success": false,
  "error": {
    "code": 42900,
    "message": "rate limited",
    "reason": "quota_day",
    "rate_limit": {
      "read": {
        "daily":   {"limit": 1000,  "used": 1000, "remaining": 0,    "reset_at": 1741190400},
        "monthly": {"limit": 10000, "used": 3000, "remaining": 7000, "reset_at": 1743811200}
      },
      "write": {
        "daily":   {"limit": 200,  "used": 200, "remaining": 0,    "reset_at": 1741190400},
        "monthly": {"limit": 2000, "used": 600, "remaining": 1400, "reset_at": 1743811200}
      },
      "write_note": {
        "daily":   {"limit": 50,  "used": 50,  "remaining": 0,   "reset_at": 1741190400},
        "monthly": {"limit": 500, "used": 150, "remaining": 350, "reset_at": 1743811200}
      }
    }
  },
  "request_id": "xxx"
}
```

字段说明：
- `limit` - 配额上限
- `used` - 已使用量
- `remaining` - 剩余量
- `reset_at` - 重置时间（Unix 时间戳，秒）

---

## 笔记详情独有字段

调用 `GET /open/api/v1/resource/note/detail?id={note_id}` 时返回，列表接口不包含这些字段：

| 字段 | 类型 | 说明 |
|------|------|------|
| `audio.original` | string | 语音转写原文 |
| `audio.play_url` | string | 音频播放地址（有效期限制） |
| `audio.duration` | int | 音频时长（秒） |
| `web_page.content` | string | 链接网页完整原文 |
| `web_page.url` | string | 原始链接地址 |
| `web_page.excerpt` | string | AI 生成的摘要 |
| `attachments[]` | array | 附件列表 |
| `attachments[].type` | string | 附件类型：audio \| image \| link \| pdf |

---

## 新建笔记字段说明

`POST /open/api/v1/resource/note/save` 请求体字段：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `title` | string | 否 | 笔记标题 |
| `content` | string | 否 | Markdown 格式正文 |
| `note_type` | string | 否 | 笔记类型，默认 `plain_text`：<br>• `plain_text` - 纯文本（同步）<br>• `link` - 链接笔记（异步，须轮询）<br>• `img_text` - 图片笔记（异步，须轮询） |
| `tags` | string[] | 否 | 标签名称列表 |
| `parent_id` | int64 | 否 | 父笔记 ID，创建子笔记时填写，默认 0 |
| `link_url` | string | link 类型必填 | 要保存的链接 URL |
| `image_urls` | string[] | img_text 类型必填 | 图片访问地址列表，使用上传凭证中的 `access_url` |

**返回说明**：
- `plain_text`：同步返回，`data.note_id` 即为笔记 ID
- `link` / `img_text`：返回 `data.task_id`，需轮询 `/task/progress` 至 `status=success` 或 `failed`

---

## 图片上传凭证返回字段

`GET /open/api/v1/resource/image/upload_token?mime_type=jpg&count=1` 返回 `data.tokens[]`，每个 token 包含：

| 字段 | 说明 |
|------|------|
| `host` | OSS 上传地址（POST 目标 URL） |
| `object_key` | 文件在 OSS 上的路径 |
| `accessid` | OSS AccessKey ID |
| `policy` | 上传策略（Base64 编码） |
| `signature` | 请求签名 |
| `callback` | 回调参数（Base64 编码，必须包含在上传请求中） |
| `access_url` | 上传成功后的文件访问地址，**创建图片笔记时填入 `image_urls`** |
| `oss_content_type` | 上传时需设置的 Content-Type（与 mime_type 对应） |

⚠️ `mime_type` 必须与实际文件格式一致，否则 OSS 签名验证失败。
