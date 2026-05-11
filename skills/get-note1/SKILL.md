---
name: Get笔记
description: |
  Get笔记 - 个人笔记和知识库管理工具。

  当用户提到以下意图时使用此技能：
  「记一下」「存到笔记」「保存到Get笔记」「记录到Get笔记」
  「保存这个链接」「保存这张图」「查我的笔记」「找一下笔记」
  「加标签」「删标签」「删笔记」
  「查知识库」「建知识库」「把笔记加到知识库」「从知识库移除」
  「知识库里订阅了哪些博主」「博主发了什么内容」「直播总结」「直播原文」
  「搜一下」「找找我哪些笔记提到了 XX」「在我的 XX 知识库搜一下 XX」

  支持：纯文本笔记、链接笔记（自动抓取网页内容并生成摘要）、图片笔记（OCR识别）、知识库管理（含博主订阅列表、直播总结）、语义搜索召回（全局或指定知识库范围）。
metadata: {"openclaw": {"requires": {}, "optionalEnv": ["GETNOTE_CLIENT_ID", "GETNOTE_OWNER_ID"], "primaryEnv": "GETNOTE_API_KEY", "baseUrl": "https://openapi.biji.com", "homepage": "https://biji.com"}}
---

# Get笔记 API

## ⚠️ 必读约束

### 🌐 Base URL（重要！所有 API 共用）

```
https://openapi.biji.com
```

**所有 API 请求必须使用此 Base URL**，不要使用 `biji.com` 或其他地址。

---

### 🔑 首次安装配置

在 `~/.openclaw/openclaw.json` 中添加：

```json
{
  "skills": {
    "entries": {
      "getnote": {
        "apiKey": "gk_live_你的key",
        "env": {
          "GETNOTE_CLIENT_ID": "cli_你的id",
          "GETNOTE_OWNER_ID": "ou_你的飞书ID（可选，用于权限控制）"
        }
      }
    }
  }
}
```

**获取凭证**：前往 [Get笔记开放平台](https://www.biji.com/openapi) 创建应用获取。

---

### 🔢 笔记 ID 处理规则（重要！）

笔记 ID（`id`、`note_id`、`next_cursor` 等）是 **64 位整数（int64）**，超出 JavaScript `Number.MAX_SAFE_INTEGER`（2^53-1）范围，直接用 `JSON.parse` 会**静默丢失精度**，导致 ID 错误，后续操作（加入知识库、删除等）会报「笔记不存在」。

**正确做法**：
- **始终把 ID 当字符串处理**，不要做数值运算
- 代码中使用 `JSON.parse` 时，**先把响应文本中的 ID 数字替换为字符串**：
  ```javascript
  // 替换顶层数字型 ID 字段为字符串（在 JSON.parse 之前）
  const safe = text.replace(/"(id|note_id|next_cursor|parent_id|follow_id|live_id)"\s*:\s*(\d+)/g, '"$1":"$2"');
  const data = JSON.parse(safe);
  ```
- Python / Go 等语言原生支持大整数，无此问题
- **发请求时**：`note_id` 字段传字符串或数字均可，服务端兼容两种格式

**验证方法**：取到 ID 后，检查 `String(id).length >= 16`，若满足说明是 int64，必须用字符串保存。

---

### 🔒 安全规则

- 笔记数据属于用户隐私，不在群聊中主动展示笔记内容
- 若配置了 `GETNOTE_OWNER_ID`，检查 sender_id 是否匹配；不匹配时回复「抱歉，笔记是私密的，我无法操作」；未配置则不检查
- API 返回 `error.reason: "not_member"` 或错误码 `10201` 时，引导开通会员：https://www.biji.com/checkout?product_alias=6AydVpYeKl
- 创建笔记建议间隔 1 分钟以上，避免触发限流

---

## 认证

请求头：
- `Authorization: $GETNOTE_API_KEY`（格式：`gk_live_xxx`）
- `X-Client-ID: $GETNOTE_CLIENT_ID`（格式：`cli_xxx`）

### Scope 权限

| Scope | 说明 |
|-------|------|
| note.content.read | 笔记列表、内容读取 |
| note.content.write | 文字/链接/图片笔记写入 |
| note.tag.write | 添加、删除笔记标签 |
| note.content.trash | 笔记移入回收站 |
| topic.read | 知识库列表 |
| topic.write | 创建知识库 |
| note.topic.read | 笔记所属知识库查询 |
| note.topic.write | 笔记加入/移出知识库 |
| note.image.upload | 获取上传图片签名 |
| topic.blogger.read | 读取知识库订阅博主列表和博主内容 |
| topic.live.read | 读取知识库已完成直播列表和直播详情 |
| note.recall.read | 语义召回笔记（全局） |
| note.topic.recall.read | 语义召回知识库内容 |

---

## 快速决策

Base URL: `https://openapi.biji.com`

| 用户意图 | 接口 | 关键点 |
|---------|------|--------|
| 「记一下」「保存笔记」 | POST /open/api/v1/resource/note/save | 同步返回 |
| 「保存这个链接」 | POST /open/api/v1/resource/note/save | note_type:"link" → **必须轮询** |
| 「保存这张图」 | 见「图片笔记流程」 | **4 步流程，必须轮询** |
| 「查我的笔记」 | GET /open/api/v1/resource/note/list | since_id=0 起始 |
| 「看原文/转写内容」 | GET /open/api/v1/resource/note/detail | audio.original / web_page.content |
| 「加标签」 | POST /open/api/v1/resource/note/tags/add | |
| 「删标签」 | POST /open/api/v1/resource/note/tags/delete | system 类型不可删 |
| 「删笔记」 | POST /open/api/v1/resource/note/delete | 移入回收站 |
| 「查知识库」 | GET /open/api/v1/resource/knowledge/list | 含统计数据（笔记数、文件数、博主数、直播数）|
| 「建知识库」 | POST /open/api/v1/resource/knowledge/create | 每天限 50 个 |
| 「笔记加入知识库」 | POST /open/api/v1/resource/knowledge/note/batch-add | 每批最多 20 条 |
| 「从知识库移除」 | POST /open/api/v1/resource/knowledge/note/remove | |
| 「查任务进度」 | POST /open/api/v1/resource/note/task/progress | 链接/图片笔记轮询用 |
| 「订阅了哪些博主」 | GET /open/api/v1/resource/knowledge/bloggers | 按 topic_id 查 |
| 「博主发了什么内容」 | GET /open/api/v1/resource/knowledge/blogger/contents | 需要 follow_id，列表只含摘要 |
| 「博主内容原文/详情」 | GET /open/api/v1/resource/knowledge/blogger/content/detail | 需要 post_id，含原文 |
| 「有哪些已完成直播」 | GET /open/api/v1/resource/knowledge/lives | 按 topic_id 查 |
| 「直播总结/直播原文」 | GET /open/api/v1/resource/knowledge/live/detail | 需要 live_id |
| 「搜一下」「找找笔记里提到 XX 的」 | POST /open/api/v1/resource/recall | 全局语义召回，见「笔记召回」章节 |
| 「在 XX 知识库搜 XX」 | POST /open/api/v1/resource/recall/knowledge | 知识库语义召回，见「知识库召回」章节 |

---

## 核心功能：记笔记 & 查笔记

### 笔记列表

```
GET /open/api/v1/resource/note/list?since_id=0
```

参数：
- since_id (int64, 必填) - 游标，首次传 0，后续用 next_cursor

返回：notes[], has_more, next_cursor, total（每次固定 20 条）

> ⚠️ **响应 JSON 可能包含未转义的控制字符**（笔记 content 中的原始换行符），建议用支持容错解析的 JSON 库处理，或在解析前对 content 字段做预处理。

> ⚠️ **`id`、`next_cursor`、`parent_id` 均为 int64**，JavaScript 环境必须在 `JSON.parse` 前做字符串化处理（见「笔记 ID 处理规则」）。**务必用字符串保存这些值**，不要做数值运算，后续调详情、加知识库等操作直接透传字符串即可。

**笔记类型 note_type**：
- `plain_text` - 纯文本
- `img_text` - 图片笔记
- `link` - 链接笔记
- `audio` - 即时录音
- `meeting` - 会议录音
- `local_audio` - 本地音频
- `internal_record` - 内录音频
- `class_audio` - 课堂录音
- `recorder_audio` - 录音卡长录
- `recorder_flash_audio` - 录音卡闪念

---

### 笔记详情

```
GET /open/api/v1/resource/note/detail?id={note_id}
```

参数：id (int64, 必填) - 笔记 ID

**详情独有字段**（列表不返回）：`audio.original`、`audio.play_url`、`audio.duration`、`web_page.content`、`web_page.url`、`web_page.excerpt`、`attachments[]`。详见 [references/api-details.md](references/api-details.md)。

---

### 新建笔记

```
POST /open/api/v1/resource/note/save
Content-Type: application/json
```

**仅支持新建，不支持编辑**。

请求体：
```json
{
  "title": "笔记标题",
  "content": "Markdown 内容",
  "note_type": "plain_text",
  "tags": ["标签1", "标签2"],
  "parent_id": 0,
  "link_url": "https://...",
  "image_urls": ["https://..."]
}
```

- `plain_text`：同步返回，立即完成
- `link` / `img_text`：返回 task_id，**必须轮询** /task/progress

详细字段说明见 [references/api-details.md](references/api-details.md)。

---

### 查询任务进度

```
POST /open/api/v1/resource/note/task/progress
Content-Type: application/json
```

请求体：
```json
{"task_id": "task_abc123xyz"}
```

返回：
- status: pending | processing | success | failed
- note_id: 成功时返回笔记 ID
- error_msg: 失败时返回错误信息

> ⚠️ **note_id 是 int64**，JavaScript 环境须按「笔记 ID 处理规则」做字符串化，拿到后直接当字符串透传。

**建议 10-30 秒间隔轮询，直到 success 或 failed**。

---

### 删除笔记

```
POST /open/api/v1/resource/note/delete
Content-Type: application/json
```

请求体：
```json
{"note_id": 123456789}
```

笔记移入回收站，需要 note.content.trash scope。

---

## 异步任务流程

> ⚠️ **必须遵循的体验流程**：链接笔记和图片笔记是异步生成的，必须按以下方式与用户沟通。

### 链接笔记完整流程

**步骤 1**：提交任务
```
POST /open/api/v1/resource/note/save {note_type:"link", link_url:"https://..."}
```
返回 task_id 后，**立即发消息给用户**：
> ✅ 链接已保存，正在抓取原文和生成总结，稍后告诉你结果...

> ⚠️ **重复链接处理**：若响应中包含 `duplicate_count > 0` 且没有 `task_id`，说明该链接已存在于你的笔记中，无需轮询，直接告知用户「该链接已存在于你的笔记中」。

**步骤 2**：后台轮询（10-30 秒间隔）
```
POST /open/api/v1/resource/note/task/progress {task_id} → 直到 status=success/failed
```

**步骤 3**：任务完成后，**调详情接口展示价值**
```
GET /open/api/v1/resource/note/detail?id={note_id}
```
然后发第二条消息，包含具体内容：
> ✅ 笔记生成完成！
> - 📄 **原文**：已保存 {web_page.content 字数} 字
> - 📝 **总结**：{content 内容，即 AI 生成的摘要}
> - 🔗 **来源**：{web_page.url}

### 图片笔记完整流程

**步骤 1-3**：获取凭证 → 上传 OSS → 提交任务
```
1. GET /open/api/v1/resource/image/upload_token?mime_type=jpg → 获取上传凭证
2. POST {host} 上传文件到 OSS
3. POST /open/api/v1/resource/note/save {note_type:"img_text", image_urls:[access_url]} → 返回 task_id
```
拿到 task_id 后，**立即发消息给用户**：
> ✅ 图片已保存，正在识别内容，稍后告诉你结果...

**步骤 4**：后台轮询
```
POST /open/api/v1/resource/note/task/progress {task_id} → 直到 status=success/failed
```

**步骤 5**：任务完成后，**调详情接口展示价值**
```
GET /open/api/v1/resource/note/detail?id={note_id}
```
然后发第二条消息：
> ✅ 图片笔记生成完成！
> - 📝 **识别内容**：{content 内容}
> - 🏷️ **标签**：{tags}

### 图片上传凭证

```
GET /open/api/v1/resource/image/upload_token?mime_type=jpg&count=1
```

参数：
- mime_type: jpg | png | gif | webp，默认 png
- count: 需要的 token 数量，默认 1，最大 9

⚠️ **mime_type 必须与实际文件格式一致**，否则 OSS 签名失败。

返回字段说明见 [references/api-details.md](references/api-details.md)。

### OSS 上传示例

> ⚠️ **字段顺序必须严格遵守**，否则 OSS 签名验证失败。正确顺序：`key → OSSAccessKeyId → policy → signature → callback → Content-Type → file`

```bash
curl -X POST "$host" \
  -F "key=$object_key" \
  -F "OSSAccessKeyId=$accessid" \
  -F "policy=$policy" \
  -F "signature=$signature" \
  -F "callback=$callback" \
  -F "Content-Type=$oss_content_type" \
  -F "file=@/path/to/image.jpg"
```

---

## 笔记召回（全局语义搜索）

> 适用场景：「搜一下」「找找我哪些笔记提到了 XX」

**所需 scope**: `note.recall.read`

```
POST /open/api/v1/resource/recall
Content-Type: application/json
```

请求体：
```json
{
  "query": "搜索关键词",
  "top_k": 3
}
```

| 参数 | 类型 | 说明 |
|------|------|------|
| query | string, 必填 | 搜索关键词或语义描述 |
| top_k | int, 可选 | 返回数量，默认 **3**，最大 **10** |

返回结构（结果已按相关度**从高到低**排序）：

```json
{
  "results": [
    {
      "note_id": "1896830231705320746",
      "note_type": "NOTE",
      "title": "笔记标题",
      "content": "笔记内容片段",
      "created_at": "2025-12-24 15:20:15"
    }
  ]
}
```

---

## 知识库召回（指定知识库语义搜索）

> 适用场景：「在我的 XX 知识库搜一下 XX」

**所需 scope**: `note.topic.recall.read`

```
POST /open/api/v1/resource/recall/knowledge
Content-Type: application/json
```

请求体：
```json
{
  "topic_id": "知识库 alias id",
  "query": "搜索关键词",
  "top_k": 3
}
```

| 参数 | 类型 | 说明 |
|------|------|------|
| topic_id | string, 必填 | 知识库 ID（alias id，来自 /knowledge/list 的 topic_id_alias） |
| query | string, 必填 | 搜索关键词或语义描述 |
| top_k | int, 可选 | 返回数量，默认 **3**，最大 **10** |

返回结构同笔记召回。

---

## 召回结果说明

| 字段 | 说明 |
|------|------|
| note_id | 笔记 ID（string）；**仅 `NOTE` 类型有值**，其余类型均为空 |
| note_type | 内容类型，见下表 |
| title | 笔记/文档标题 |
| content | 相关内容片段 |
| created_at | 创建/发布时间（YYYY-MM-DD HH:MM:SS）|
| page_no | `FILE` 类型时表示文件页码，其余类型省略 |

**note_type 类型**：

| note_type | 说明 | note_id |
|-----------|------|---------|
| NOTE | 笔记（含知识库笔记） | ✅ 有值 |
| FILE | 知识库文件 | ❌ 无值 |
| BLOGGER | 博主内容 | ❌ 无值 |
| LIVE | 直播 | ❌ 无值 |
| URL | 全网内容 | ❌ 无值 |
| DEDAO | 得到内容 | ❌ 无值 |

### 后续操作

- **`NOTE` 类型**：可调 `GET /open/api/v1/resource/note/detail?id={note_id}` 获取笔记全文
- **其余类型**：无 `note_id`，只能展示召回的内容片段（`content`）；`FILE` 类型可额外展示页码（`page_no`）

### 示例对话

> 用户：「找找我哪些笔记提到了大模型 API」
> → `POST /recall` `{ "query": "大模型 API", "top_k": 3 }`

> 用户：「在我的 AI 学习知识库里搜一下 RAG」
> → 先调 `/knowledge/list` 找到 `topic_id_alias`，再 `POST /recall/knowledge` `{ "topic_id": "xxx", "query": "RAG", "top_k": 3 }`

---

## 笔记整理

### 添加标签

```
POST /open/api/v1/resource/note/tags/add
Content-Type: application/json
```

请求体：
```json
{
  "note_id": 123456789,
  "tags": ["工作", "重要"]
}
```

**标签类型 type**：
- ai - AI 自动生成
- manual - 用户手动添加
- system - 系统标签（**不可删除**）

---

### 删除标签

```
POST /open/api/v1/resource/note/tags/delete
Content-Type: application/json
```

请求体：
```json
{
  "note_id": 123456789,
  "tag_id": "123"
}
```

⚠️ system 类型标签不允许删除。

---

### 知识库列表

```
GET /open/api/v1/resource/knowledge/list?page=1
```

参数：
- page: 页码，从 1 开始，默认 1（固定每页 20 条）

返回：topics[], has_more, total

每个 topic 包含：
- `topic_id` / `topic_id_alias`：知识库 ID
- `name`、`description`、`cover`
- `created_at` / `updated_at`：时间字符串（YYYY-MM-DD HH:MM:SS）
- `stats`：统计数据
  - `note_count`：笔记数
  - `file_count`：文件数
  - `blogger_count`：订阅博主数
  - `live_count`：已完成直播数

---

### 创建知识库

```
POST /open/api/v1/resource/knowledge/create
Content-Type: application/json
```

请求体：
```json
{
  "name": "知识库名称",
  "description": "描述",
  "cover": ""
}
```

⚠️ 每天最多创建 50 个知识库（北京时间 00:00 重置）。

---

### 知识库笔记列表

```
GET /open/api/v1/resource/knowledge/notes?topic_id=abc123&page=1
```

参数：
- topic_id (string, 必填) - 知识库 ID（alias id）
- page: 页码，从 1 开始

每页固定 20 条，用 has_more 判断是否有下一页。

---

### 知识库选择逻辑

当用户说「存到对应的知识库」或「存到相关知识库」时：
1. 先调用 GET /knowledge/list 获取所有知识库列表
2. 根据笔记标题、内容、标签，与知识库名称和描述做模糊匹配
3. 匹配置信度高时直接执行，并告知用户存入了哪个知识库
4. 置信度低或有歧义时，列出候选知识库让用户选择
5. 用户未提及知识库时，**不要擅自存入**任何知识库

---

### 添加笔记到知识库

```
POST /open/api/v1/resource/knowledge/note/batch-add
Content-Type: application/json
```

请求体：
```json
{
  "topic_id": "abc123",
  "note_ids": [123456789, 123456790]
}
```

⚠️ 每批最多 20 条。已存在的笔记会跳过。

---

### 从知识库移除笔记

```
POST /open/api/v1/resource/knowledge/note/remove
Content-Type: application/json
```

请求体：
```json
{
  "topic_id": "abc123",
  "note_ids": [123456789]
}
```

---

## 知识库：博主订阅

### 博主列表

```
GET /open/api/v1/resource/knowledge/bloggers?topic_id={alias_id}&page=1
```

参数：
- topic_id (string, 必填) - 知识库 AliasID（来自 /knowledge/list 的 topic_id_alias）
- page: 页码，从 1 开始

每页固定 20 条，用 has_more 判断。

返回 bloggers[]，每项字段：

| 字段 | 说明 |
|------|------|
| follow_id | 订阅关系 ID，**查博主内容时必用** |
| account_name | 博主名称 |
| account_icon | 博主头像 |
| platform | 平台（如 DEDAO）|
| account_url | 博主主页链接 |
| follow_time | 订阅时间（YYYY-MM-DD HH:MM:SS）|

---

### 博主内容列表

```
GET /open/api/v1/resource/knowledge/blogger/contents?topic_id={alias_id}&follow_id={follow_id}&page=1
```

参数：
- topic_id (string, 必填) - 知识库 AliasID
- follow_id (int64, 必填) - 博主订阅 ID（来自 /bloggers 的 follow_id）
- page: 页码，从 1 开始

每页固定 20 条，用 has_more 判断。

返回 contents[]，每项字段：

| 字段 | 说明 |
|------|------|
| post_id_alias | 内容 ID，**查详情/原文时必用** |
| post_name | 内容名称（原标题）|
| post_type | 类型：video / audio / article / live |
| post_cover | 封面图 |
| post_title | AI 生成标题 |
| post_summary | AI 摘要（Markdown）|
| post_url | 原文链接 |
| post_icon | 博主头像 |
| post_subtitle | 副标题 |
| post_create_time | 创建时间（YYYY-MM-DD HH:MM:SS）|
| post_publish_time | 发布时间（YYYY-MM-DD HH:MM:SS）|

> 列表不含原文（`post_media_text`），需要原文请调 `/blogger/content/detail`。

---

### 博主内容详情（含原文）

```
GET /open/api/v1/resource/knowledge/blogger/content/detail?topic_id={alias_id}&post_id={post_id_alias}
```

参数：
- topic_id (string, 必填) - 知识库 AliasID
- post_id (string, 必填) - 内容 ID（来自 /blogger/contents 的 post_id_alias）

返回字段：

| 字段 | 说明 |
|------|------|
| post_id_alias | 内容 ID |
| post_name | 内容名称（原标题）|
| post_type | 类型：video / audio / article / live |
| post_cover | 封面图 |
| post_subtitle | 副标题 |
| post_url | 原文链接 |
| post_title | AI 生成标题 |
| post_summary | AI 摘要（Markdown）|
| post_media_text | 原文内容（全文转写/文章正文）|
| post_create_time | 创建时间（YYYY-MM-DD HH:MM:SS）|
| post_publish_time | 发布时间（YYYY-MM-DD HH:MM:SS）|

---

## 知识库：直播订阅

### 已完成直播列表

```
GET /open/api/v1/resource/knowledge/lives?topic_id={alias_id}&page=1
```

参数：
- topic_id (string, 必填) - 知识库 AliasID
- page: 页码，从 1 开始

每页固定 20 条，用 has_more 判断。**只返回已结束且 AI 已处理完的直播。**

返回 lives[]，每项字段：

| 字段 | 说明 |
|------|------|
| live_id | 直播 ID，**查直播详情时必用** |
| follow_id | 订阅关系 ID |
| name | 直播名称 |
| cover | 封面图 |
| sub_title | 副标题 |
| link | 直播链接 |
| platform | 平台（如 DEDAO）|
| status | 直播状态（已结束为 FINISHED）|
| follow_time | 订阅时间（YYYY-MM-DD HH:MM:SS）|

---

### 直播详情（总结 + 原文）

```
GET /open/api/v1/resource/knowledge/live/detail?topic_id={alias_id}&live_id={live_id}
```

参数：
- topic_id (string, 必填) - 知识库 AliasID
- live_id (int64, 必填) - 直播 ID（来自 /lives 的 live_id）

返回字段：

| 字段 | 说明 |
|------|------|
| post_id_alias | 内容 ID |
| post_name | 直播名称（原标题）|
| post_cover | 封面图 |
| post_subtitle | 副标题（如开播时间）|
| post_url | 直播原始链接 |
| post_title | AI 生成标题 |
| post_summary | AI 摘要（Markdown，含章节纪要、金句）|
| post_media_text | 直播原文转写文本 |
| post_create_time | 创建时间（YYYY-MM-DD HH:MM:SS）|
| post_publish_time | 直播时间（YYYY-MM-DD HH:MM:SS）|

---

## 错误处理

> 详细错误码和限流结构见 [references/api-details.md](references/api-details.md)

### 响应结构

```json
{
  "success": false,
  "error": {
    "code": 10001,
    "message": "unauthorized",
    "reason": "not_member"
  },
  "request_id": "xxx"
}
```

### 常见错误码

| 错误码 | 说明 | 处理方式 |
|--------|------|---------|
| 10001 | 鉴权失败 | 检查 API Key 和 Client ID |
| 10201 | 非会员 | 引导开通：https://www.biji.com/checkout?product_alias=6AydVpYeKl |
| 20001 | 笔记不存在 | 确认笔记 ID 正确 |
| 42900 | 限流 | 降低频率，查看 rate_limit 字段 |
| 50000 | 系统错误 | 稍后重试 |
