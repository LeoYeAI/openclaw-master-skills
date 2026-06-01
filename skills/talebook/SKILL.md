---
name: talebook
homepage: https://www.mybooks.top
allowed-tools: Bash(python3:*)
metadata: {"clawdbot":{},"openclaw":{"requires":{"bins":["python3"],"env":["TALEBOOK_HOST","TALEBOOK_USER","TALEBOOK_PASSWORD"]}}}
description: "Talebook(PoxenStudio)是个人书库管理系统，提供电子书及实体书管理，包括存储、分类、搜索和元数据管理功能。你可以帮助用户：查询书库统计信息和阅读统计,搜索/浏览书籍,获取书籍详情,更新书籍元数据（书名、作者、标签、分类、简介等）,自动联网填充书籍信息,发送书籍到邮箱或阅读器设备,上传电子书或通过ISBN添加实体书,管理阅读状态（想读/在读/已读/收藏）,查看作者信息和分类信息"
---

# talebook

## Requirements
```bash
# 需要配置以下三个环境变量后方可使用
export TALEBOOK_HOST="http://127.0.0.1:8082"
export TALEBOOK_USER="admin"
export TALEBOOK_PASSWORD="your_password"

然后按如下方式执行：
<skill-installation-path>/scripts/talebook_api.py <tool-name> '<json-args>'
```

> **安全提示**：请勿将凭据写入共享或全局配置文件（如 `~/.openclaw/.env`），以避免凭据被其他 agent 或进程意外读取。建议通过会话级环境变量或专用密钥管理工具传入凭据。

## 通用响应格式与认证方式

### 通用 JSON 响应结构
所有 API 均返回如下格式：
```json
{
  "err": "ok",       // "ok" 表示成功，其他字符串表示错误码
  "msg": "...",      // 可选，人类可读的成功/错误说明
  "data": { }        // 可选，具体响应数据（因接口而异）
}
```

常见错误码：
| `err` 值 | 含义 |
|----------|------|
| `"ok"` | 操作成功 |
| `"user.need_login"` | 未登录或登录态已过期 |
| `"permission"` | 无权限执行该操作 |
| `"params.invalid"` | 请求参数错误 |
| `"params.book.invalid"` | 书籍不存在或 ID 错误 |
| `"task.running"` | 后台任务正在进行中，稍后重试 |

### 认证方式
- 脚本通过 `TALEBOOK_USER` / `TALEBOOK_PASSWORD` 环境变量自动调用 `/api/user/sign_in` 完成登录
- 服务端通过 **Secure Cookie**（`user_id` + `lt`）维持会话
- 若响应中出现 `err=user.need_login`，脚本会自动重新登录后重试一次；仍失败则报错退出
- **必须**在调用前配置 `TALEBOOK_HOST`、`TALEBOOK_USER`、`TALEBOOK_PASSWORD` 三个环境变量，否则脚本直接报错退出

---

## 工具列表

### `get_user_info` — 用户信息与系统统计

**使用场景**：获取当前登录用户信息，同时返回书库总体统计（书籍数、作者数等）

**参数**：无

**执行脚本**：
```bash
<skill-installation-path>/scripts/talebook_api.py get_user_info '{}'
```

**响应示例**：
```json
{
  "err": "ok",
  "user": { "is_login": true, "nickname": "管理员", "is_admin": true },
  "sys": { "books": 1280, "authors": 342, "tags": 86, "mtime": "2025-03-01" }
}
```

---

### `library_stats` — 书库统计

**使用场景**：获取书库详细统计，包括电子书/实体书数量及本月新增

**参数**：无

**执行脚本**：
```bash
<skill-installation-path>/scripts/talebook_api.py library_stats '{}'
```

**响应示例**：
```json
{
  "err": "ok",
  "stats": {
    "total_books": 1280,
    "ebook_count": 1210,
    "physical_count": 70,
    "month_ebook_count": 12,
    "month_physical_count": 3,
    "current_year": 2025,
    "current_month": 3
  }
}
```

---

### `reading_stats` — 阅读统计

**使用场景**：获取当前用户的阅读统计（在读/已读数量、本月数据）及当前在读书单

**参数**：无

**执行脚本**：
```bash
<skill-installation-path>/scripts/talebook_api.py reading_stats '{}'
```

**响应示例**：
```json
{
  "err": "ok",
  "stats": {
    "total_reading": 5,
    "total_read_done": 42,
    "month_reading": 2,
    "month_read_done": 3
  },
  "current_reading_books": [ /* 书籍对象列表 */ ],
  "month_read_done_books": [ /* 书籍对象列表 */ ]
}
```

---

### `search_books` — 搜索书籍

**使用场景**：
- 按书名或作者名搜索，支持简繁体自动转换
- "有没有余华的书？" / "找一下《三体》"

**参数**：

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `name` | string | ✅ | — | 搜索关键词（书名或作者名） |
| `num` | int | ❌ | 20 | 每页数量 |
| `page` | int | ❌ | 1 | 页码，从 1 开始 |

**执行脚本**：
```bash
<skill-installation-path>/scripts/talebook_api.py search_books '{"name":"三体"}'
```

**响应示例**：
```json
{
  "err": "ok",
  "title": "搜索：三体",
  "total": 3,
  "books": [ /* 书籍对象列表 */ ]
}
```

---

### `search_by_category` — 按分类查询书籍

**使用场景**：查询指定分类下的所有书籍（基于自定义 `#category` 字段）

**参数**：

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `category` | string | ✅ | — | 分类名称，如 "科幻" |
| `num` | int | ❌ | 20 | 每页数量 |
| `page` | int | ❌ | 1 | 页码，从 1 开始 |

**执行脚本**：
```bash
<skill-installation-path>/scripts/talebook_api.py search_by_category '{"category":"科幻"}'
```

---

### `get_book` — 书籍详情

**使用场景**：获取指定书籍的完整信息，包括元数据、可用格式、封面、阅读状态等

**参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `book_id` | int | ✅ | 书籍 ID |

**执行脚本**：
```bash
<skill-installation-path>/scripts/talebook_api.py get_book '{"book_id":42}'
```

**响应示例**：
```json
{
  "err": "ok",
  "book": {
    "id": 42,
    "title": "活着",
    "authors": ["余华"],
    "tags": ["小说", "中国文学"],
    "publisher": "作家出版社",
    "isbn": "9787506365437",
    "pubdate": "2012-08-01",
    "rating": 9,
    "comments": "《活着》讲述了...",
    "category": "现代文学",
    "available_formats": ["epub", "pdf"],
    "fmt_epub": "/path/to/file.epub",
    "cover_url": "/get/cover/42",
    "state": {
      "favorite": 0,
      "wants": 0,
      "read_state": 1
    }
  },
  "kindle_sender": "sender@example.com"
}
```

---

### `edit_book` — 编辑书籍元数据

**使用场景**：
- 手动修改书名、作者、标签、分类等字段
- 修改实体书数量或类型

**参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `book_id` | int | ✅ | 书籍 ID |
| `title` | string | ❌ | 书名 |
| `authors` | array | ❌ | 作者列表，如 `["余华"]` |
| `tags` | array | ❌ | 标签列表，**替换**原有标签（想追加需先 `get_book` 获取现有标签再合并） |
| `publisher` | string | ❌ | 出版社 |
| `isbn` | string | ❌ | ISBN 编号 |
| `series` | string | ❌ | 系列/丛书名 |
| `rating` | number | ❌ | 评分（0–10） |
| `languages` | array | ❌ | 语言代码列表，如 `["zho"]`（中文）、`["eng"]`（英文） |
| `pubdate` | string | ❌ | 出版日期，格式：`"2024-01-15"` / `"2024-01"` / `"2024"` |
| `comments` | string | ❌ | 书籍简介，支持 HTML，请勿将 `<>` 转义为 `&lt;&gt;` |
| `category` | string | ❌ | 自定义分类（最长 80 字符；传 `"清除"` 或 `"clear"` 清空分类） |
| `book_count` | int | ❌ | 实体书数量（需配合 `book_type: 1` 使用） |
| `book_type` | int | ❌ | 书籍类型：`0`=电子书，`1`=实体书 |

**执行脚本**：
```bash
<skill-installation-path>/scripts/talebook_api.py edit_book '{"book_id":42,"tags":["小说","中国文学"],"category":"现代文学"}'
```

**响应示例**：
```json
{ "err": "ok", "msg": "更新成功", "books": [42] }
```

---

### `book_fill` — 自动联网填充书籍信息

**使用场景**：
- "帮我更新《XX》的封面和简介"
- "书库里有很多书信息不完整，帮我补全"
- 批量补全多本书的封面、简介、出版社、出版日期、标签等

**权限**：需要管理员权限

**参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `idlist` | array 或 `"all"` | ✅ | 书籍 ID 数组，或 `"all"` 表示全库处理 |

**注意**：任务在后台异步执行，调用后立即返回；书名**默认保留原值不修改**（防止错误覆盖）

**执行脚本**：
```bash
# 更新单本书
<skill-installation-path>/scripts/talebook_api.py book_fill '{"idlist":[42]}'

# 批量更新
<skill-installation-path>/scripts/talebook_api.py book_fill '{"idlist":[42,43,44]}'
```

**响应示例**：
```json
{ "err": "ok", "msg": "任务启动成功！请耐心等待，稍后再来刷新页面" }
```

---

### `mailto` — 发送书籍到邮箱

**使用场景**：将书籍以附件形式发送到指定邮箱（如 Kindle 邮箱）

**格式优先级**：epub > azw3 > pdf > mobi > txt（取首个存在的格式）

**权限**：需要登录，且账号需有推送权限（`can_push`）

**参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `book_id` | int | ✅ | 书籍 ID |
| `email` | string | ✅ | 目标邮箱地址（可以是 Kindle 邮箱） |

**执行脚本**：
```bash
<skill-installation-path>/scripts/talebook_api.py mailto '{"book_id":42,"email":"user@kindle.com"}'
```

**响应示例**：
```json
{ "err": "ok", "msg": "后台正在推送，稍后可以刷新页面，在通知消息中查看结果。" }
```

---

### `send_to_device` — 发送书籍到阅读器设备

**使用场景**：通过 WiFi 将书籍直接推送到阅读器设备（仅支持当前网络内的临时设备）

**支持的设备类型（`device_type`）**：

| 类型 | 设备 | 传输方式 | `device_url` 说明 |
|------|------|----------|-------------------|
| `kindle` | Kindle 系列 | 邮件发送 | 不需填写，改用 `mailbox` 参数 |
| `duokan` | 多看阅读器 | HTTP WiFi 上传 | 设备局域网 IP，如 `192.168.1.100` |
| `ireader` | 掌阅 iReader | HTTP WiFi 上传 | 设备局域网 IP |
| `hanwang` | 汉王电纸书 | HTTP WiFi 上传 | 设备局域网 IP |
| `boox` | 文石 BOOX | HTTP WiFi 上传 | 设备局域网 IP |
| `dangdang` | 当当阅读器 | HTTP WiFi 上传 | 设备局域网 IP |

**WiFi 传输格式优先级**：epub > azw3 > pdf > txt

**参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `book_id` | int | ✅ | 书籍 ID |
| `device_type` | string | ✅ | 设备类型（见上表） |
| `device_url` | string | kindle 以外必填 | 设备局域网 IP 或地址（如 `"192.168.1.100"` 或 `"http://192.168.1.100:80"`） |
| `mailbox` | string | kindle 时必填 | Kindle 邮箱地址 |

**执行脚本**：
```bash
# 发送到多看设备
<skill-installation-path>/scripts/talebook_api.py send_to_device \
  '{"book_id":42,"device_type":"duokan","device_url":"192.168.1.100"}'

# 发送到 Kindle（通过邮件）
<skill-installation-path>/scripts/talebook_api.py send_to_device \
  '{"book_id":42,"device_type":"kindle","mailbox":"mykindle@kindle.cn"}'
```

**响应示例**：
```json
{ "err": "ok", "msg": "书籍发送成功" }
```

---

### `categories` — 查看分类信息

**使用场景**：获取当前书库中所有自定义分类及各分类下的书籍数量

**参数**：无

**执行脚本**：
```bash
<skill-installation-path>/scripts/talebook_api.py categories '{}'
```

**响应示例**：
```json
{
  "err": "ok",
  "categories": [
    { "name": "现代文学", "count": 128 },
    { "name": "科幻", "count": 56 }
  ]
}
```

---

### `list_authors` — 查看作者列表

**使用场景**：获取所有有在库书籍的作者及其书籍数量

**参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `show` | string | ❌ | 传 `"all"` 显示全部，否则返回前 N 条 |

**执行脚本**：
```bash
<skill-installation-path>/scripts/talebook_api.py list_authors '{}'
```

**响应示例**：
```json
{
  "err": "ok",
  "meta": "author",
  "title": "全部作者",
  "items": [
    { "name": "余华", "count": 5 },
    { "name": "刘慈欣", "count": 8 }
  ],
  "total": 342
}
```

---

### `get_author_books` — 查询作者的在库书籍

**使用场景**：获取指定作者在书库中的所有书籍

**参数**：

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `author_name` | string | ✅ | — | 作者名 |
| `num` | int | ❌ | 20 | 每页数量 |
| `page` | int | ❌ | 1 | 页码，从 1 开始 |

**执行脚本**：
```bash
<skill-installation-path>/scripts/talebook_api.py get_author_books '{"author_name":"余华"}'
```

---

### `book_upload` — 上传电子书

**使用场景**：上传本地电子书文件到书库，支持 epub/mobi/azw/azw3/pdf/txt/lrf/rtf/djvu/docx 等格式

**权限**：需要登录，且账号需有上传权限（`can_upload`）

**参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `file_path` | string | ✅ | 本地文件的绝对路径 |

**执行脚本**：
```bash
<skill-installation-path>/scripts/talebook_api.py book_upload '{"file_path":"/path/to/book.epub"}'
```

**响应示例**：
```json
{ "err": "ok", "book_id": 123 }
```

---

### `book_add_by_isbn` — 通过 ISBN 添加实体书

**使用场景**：
- 扫描实体书的 ISBN 条码后，将书入库
- 若该 ISBN 书籍已存在，则自动将实体书数量 +1

**参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `isbn` | string | ✅ | ISBN 编号，如 `"9787020024759"` |

**执行脚本**：
```bash
<skill-installation-path>/scripts/talebook_api.py book_add_by_isbn '{"isbn":"9787020024759"}'
```

**响应示例**（新增）：
```json
{ "err": "ok", "msg": "图书添加成功", "book_id": 456 }
```

**响应示例**（已存在，更新数量）：
```json
{ "err": "ok", "msg": "实体书数量已更新，当前数量：2", "book_id": 123 }
```

---

### `wants` — 标记/取消想读

**使用场景**：将书籍加入/移出"想读（待读）"清单

**参数**：

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `book_id` | int | ✅ | — | 书籍 ID |
| `wants` | bool | ❌ | `true` | `true`=标记想读，`false`=取消 |

**执行脚本**：
```bash
<skill-installation-path>/scripts/talebook_api.py wants '{"book_id":42}'
```

---

### `list_wants` — 想读清单

**使用场景**：获取当前用户的"想读（待读）"书籍列表

**参数**：无

**执行脚本**：
```bash
<skill-installation-path>/scripts/talebook_api.py list_wants '{}'
```

---

### `favorite` — 收藏/取消收藏

**使用场景**：收藏或取消收藏指定书籍

**参数**：

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `book_id` | int | ✅ | — | 书籍 ID |
| `favorite` | bool | ❌ | `true` | `true`=收藏，`false`=取消收藏 |

**执行脚本**：
```bash
<skill-installation-path>/scripts/talebook_api.py favorite '{"book_id":42}'
```

---

### `list_favorites` — 收藏列表

**使用场景**：获取当前用户的所有收藏书籍

**参数**：无

**执行脚本**：
```bash
<skill-installation-path>/scripts/talebook_api.py list_favorites '{}'
```

---

### `reading` — 设置阅读状态

**使用场景**：标记某本书的阅读状态（未读/在读/已读完）

**参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `book_id` | int | ✅ | 书籍 ID |
| `read_state` | int | ✅ | 阅读状态：`0`=未读，`1`=在读，`2`=已读完 |

**执行脚本**：
```bash
# 标记为在读
<skill-installation-path>/scripts/talebook_api.py reading '{"book_id":42,"read_state":1}'
```

---

### `list_reading` — 在读书单

**使用场景**：获取当前用户的"正在阅读"书籍列表

**参数**：无

**执行脚本**：
```bash
<skill-installation-path>/scripts/talebook_api.py list_reading '{}'
```

---

### `read_done` — 标记已读完

**使用场景**：快捷将某本书标记为已读完（即 `reading` 工具中 `read_state=2` 的简化版）

**参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `book_id` | int | ✅ | 书籍 ID |

**执行脚本**：
```bash
<skill-installation-path>/scripts/talebook_api.py read_done '{"book_id":42}'
```

---

### `list_read_done` — 已读清单

**使用场景**：获取当前用户的"已读完"书籍列表

**参数**：无

**执行脚本**：
```bash
<skill-installation-path>/scripts/talebook_api.py list_read_done '{}'
```

---

## 使用场景决策指南

```
用户请求
│
├─ "书库有多少书？" / "统计书库"
│   → library_stats（详细分类统计）
│   → 或 get_user_info（快速总数）
│
├─ "我读了多少书？" / "阅读情况"
│   → reading_stats
│
├─ "找一下 XX 书" / "搜索 YY 作者"
│   → search_books（按关键词）
│
├─ "找 XX 分类下的书"
│   → search_by_category
│
├─ "查看书籍详情"
│   → get_book
│
├─ "更新/补全《XX》的封面、简介、标签信息"（自动从网上获取）
│   → book_fill（需要管理员权限，传入 book_id 数组）
│
├─ "手动修改《XX》的标签/分类/书名等字段"
│   → 先 search_books 确认 book_id → 再 edit_book
│
├─ "把书发给我的 Kindle / 发到邮箱"
│   → mailto（发邮箱附件）
│
├─ "把书发到我的多看/掌阅/BOOX 设备"
│   → send_to_device（需设备在同一局域网并开启 WiFi 接收）
│
├─ "上传这本书" / "添加实体书"
│   → book_upload（电子书文件）
│   → book_add_by_isbn（实体书 ISBN）
│
├─ "这本书想读" / "加入待读清单"
│   → wants
│
├─ "收藏这本书"
│   → favorite
│
├─ "标记正在读" / "标记已读完"
│   → reading（read_state: 1 或 2）
│   → read_done（快捷标记已读完）
│
└─ "有哪些分类？" / "XX 作者有哪些书？"
    → categories / list_authors / get_author_books
```

---

## 错误处理规范

| `err` 值 | 含义 | 建议处理 |
|----------|------|----------|
| `"ok"` | 操作成功 | 展示结果 |
| `"user.need_login"` | 未登录或登录态过期 | 脚本自动重登录，仍失败则检查环境变量 |
| `"permission"` | 无权限 | 说明当前账号权限不足，需管理员协助 |
| `"params.book.invalid"` | 书籍不存在 | 建议用 `search_books` 重新确认 book_id |
| `"task.running"` | 后台有任务在运行 | 等待当前任务完成后重试 |
| `"book.notfound"` | ISBN 对应的书籍未在网上找到 | 换其他数据源或手动添加 |
| `"connection.failed"` | 无法连接到设备 | 检查设备 IP 和 WiFi 接收功能是否开启 |

---

## 注意事项

1. **认证**：每次调用前脚本会自动登录，无需手动管理 Cookie；若未配置环境变量，脚本立即报错退出。
2. **book_id**：书籍的唯一整数标识符，可通过 `search_books` 或 `get_book` 获取。
3. **book_fill 异步性**：联网填充任务在后台运行，调用后立即返回；可通过 `get_book` 查看更新结果。
4. **edit_book 标签替换**：`tags` 参数会**完整替换**原有标签，如需追加请先 `get_book` 获取现有标签再合并传入。
5. **send_to_device 限制**：仅支持本地临时推送，不支持通过服务器中转到远程设备。
6. **在线数据源**：`book_fill` 依赖豆瓣（douban）、百科（baike）等在线源，网络不可用或书籍较冷门时可能无结果。
7. **批量 book_fill**：建议每批不超过 10 本，避免触发后台任务冲突（`task.running` 错误）。
