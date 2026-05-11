---
name: gws
description: "Google Workspace CLI. Use when the user mentions Gmail, Google Drive, Calendar, Sheets, Docs, Tasks, People, Slides, Forms, Meet, Classroom, sending email, checking inbox, managing files, reading/writing spreadsheets, viewing schedules, standup reports, or any Google Workspace operation — even if they don't explicitly say 'gws'."
metadata:
  {
    "openclaw":
      {
        "requires":
          {
            "env": ["GOOGLE_WORKSPACE_PROJECT_ID", "GOOGLE_WORKSPACE_CLI_CREDENTIALS_FILE", "GOOGLE_WORKSPACE_CLI_KEYRING_BACKEND"],
            "bins": ["gws", "jq", "base64"]
          }
      }
  }
---

# GWS — Google Workspace CLI

Google's official Workspace CLI (`@googleworkspace/cli`). One tool for Gmail, Drive, Calendar, Sheets, Docs, Tasks, People, Slides, Forms, Meet, Classroom, and more.

GitHub: https://github.com/googleworkspace/cli

## Setup

Each session, set these before using `gws`:

```bash
export GOOGLE_WORKSPACE_PROJECT_ID=<your-project-id>
export GOOGLE_WORKSPACE_CLI_CREDENTIALS_FILE=~/.config/gws/credentials.json
export GOOGLE_WORKSPACE_CLI_KEYRING_BACKEND=file
```

First-time setup and authorization: see **Prerequisites** below.

## Prerequisites

### 1. 安装 gws

```bash
npm install -g @googleworkspace/cli
```

### 2. GCP Console 配置

前往 [Google Cloud Console → APIs & Services → Library](https://console.cloud.google.com/apis/library)，启用以下 API：

| 服务 | API 名称 |
|------|----------|
| Gmail | Gmail API |
| Drive | Google Drive API |
| Calendar | Google Calendar API |
| Sheets | Google Sheets API |
| Docs | Google Docs API |
| Tasks | Tasks API |
| People | People API |
| Slides | Google Slides API |
| Forms | Forms API |
| Meet | Google Meet API |
| Classroom | Google Classroom API |

大部分 API 在 `gws auth login` 时会自动关联，但 Sheets/Docs/Slides 等可能需要手动启用后才能调用。

**重要：启用 API 和 OAuth scope 是两回事。** API 启用决定"能不能调这个服务"，OAuth scope 决定"能做什么操作"，两者都需要。

### 3. OAuth 授权

`gws` 是无头 CLI，授权流程需要用户在浏览器中完成：

```bash
gws auth login
```

1. CLI 输出 OAuth URL
2. **将链接发给用户**，让用户在浏览器中打开并授权
3. 用户将回调页面中的授权码复制回来
4. 在 CLI 中粘贴授权码，完成认证

凭证保存在 `GOOGLE_WORKSPACE_CLI_CREDENTIALS_FILE` 指定的路径。`gws auth login -s <service>` 支持分批授权特定服务，不会覆盖已有 scope。

如果遇到 `insufficient authentication scopes` 错误，重新运行 `gws auth login` 并勾选缺少的权限。

## Troubleshooting

- **`insufficient authentication scopes`** → 见 Prerequisites > Scope 说明，重新授权并勾选缺少的权限
- **`File not found`** → 检查是否使用了绝对路径，改用相对路径（见 Usage Philosophy）
- **上传后文件名为 "Untitled"** → 用 `files update` 重命名（见 Known API Quirks）
- **参数不确定** → `gws schema <api.method>` 查询任意 API 的完整参数结构
- **API 未启用** → 见 Prerequisites > GCP Console，启用对应 API

---

## Gmail

**Gmail** 是最常用的服务，支持完整的邮件 CRUD、搜索、标签、附件、线程、批量操作和设置管理。

每次 `gws` 调用有 ~2-3s 启动延迟，批量操作优先（`batchModify` 每批 ≤100 条）。逐条 get 邮件可用 `&` 并行 + `wait` 加速。

### 搜索与列表

Gmail 搜索语法通过 `q` 参数传递，功能强大：`newer_than:1d`、`is:starred`、`is:unread`、`from:xxx`、`subject:keyword`、`label:xxx`、`has:attachment`、`after:YYYY/MM/DD`、`before:YYYY/MM/DD`、`category:primary`（primary/promotions/social/updates/forums）等。

```bash
gws gmail users messages list --params '{"userId":"me","q":"is:unread","maxResults":20}'
gws gmail users messages list --params '{"userId":"me","q":"is:unread"}' --page-all
```

### 读取邮件

`messages list` 仅返回 ID，需逐条 `get`。只需要摘要用 `format=metadata`（更快省 token），需要正文用 `format=full`。

**注意**：API 返回的 header 顺序不固定（按内部存储顺序，非请求顺序），**必须按 header name 匹配，不能按数组 index 取值。**

邮件正文 parts 结构不固定——有些是单层 `.payload.parts[]`，有些是嵌套 `.payload.parts[].parts[]`，两种写法都要准备好。

```bash
# 提取 headers（按 name 匹配，不要按 index）
gws gmail users messages get --params '{"userId":"me","id":"MSG_ID","format":"metadata","metadataHeaders":["From","Subject","Date"]}'
# → jq '.payload.headers | map({(.name): .value}) | add'

# 纯文本正文（先试单层，为空再试嵌套）
gws gmail users messages get --params '{"userId":"me","id":"MSG_ID","format":"full"}' | jq -r '.payload.parts[] | select(.mimeType == "text/plain") | .body.data' | base64 -d
# 嵌套备选: jq -r '.payload.parts[].parts[]? | select(.mimeType == "text/plain") | .body.data' | base64 -d

# 快速预览（无需 base64，但有长度限制）
gws gmail users messages get --params '{"userId":"me","id":"MSG_ID","format":"metadata"}' | jq -r '.snippet'
```

### 并行批量读取

利用 `&` 后台并行将 N×3s 降到 ~3s：

```bash
IDS=$(gws gmail users messages list --params '{"userId":"me","q":"is:unread","maxResults":10}' 2>/dev/null | jq -r '.messages[].id')
for id in $IDS; do
  gws gmail users messages get --params "{\"userId\":\"me\",\"id\":\"$id\",\"format\":\"metadata\",\"metadataHeaders\":[\"From\",\"Subject\",\"Date\"]}" 2>/dev/null | jq -r '.payload.headers | map({(.name): .value}) | add | "\(.From[:30]) | \(.Subject) — \(.Date)"' &
done; wait
```

### 批量操作

`batchModify` 一次处理最多 100 条，避免逐条循环的延迟开销：

```bash
IDS=$(gws gmail users messages list --params '{"userId":"me","q":"is:unread","maxResults":100}' 2>/dev/null | jq -c '[.messages[].id]')
gws gmail users messages batchModify --params '{"userId":"me"}' --json "{\"ids\":$IDS,\"removeLabelIds\":[\"UNREAD\"]}"
gws gmail users messages batchModify --params '{"userId":"me"}' --json "{\"ids\":$IDS,\"addLabelIds\":[\"STARRED\"]}"
```

### 发送邮件

构造 RFC 2822 格式邮件，Base64 编码后发送：

```bash
# 纯文本
RAW=$(printf "To: recipient@example.com\r\nSubject: Hello\r\nFrom: me@gmail.com\r\nContent-Type: text/plain; charset=utf-8\r\n\r\nBody text here" | base64 -w0)
gws gmail users messages send --json "{\"raw\":\"$RAW\"}" --params '{"userId":"me"}'

# HTML（改 Content-Type 为 text/html）
RAW=$(printf "To: recipient@example.com\r\nSubject: Hello\r\nFrom: me@gmail.com\r\nContent-Type: text/html; charset=utf-8\r\n\r\n<h1>Title</h1><p>Body</p>" | base64 -w0)
gws gmail users messages send --json "{\"raw\":\"$RAW\"}" --params '{"userId":"me"}'
```

### 附件下载

先从 `format=full` 响应中提取 `attachmentId`，再用 `attachments get` 下载（同样受相对路径限制）：

```bash
# 1. 获取附件列表
gws gmail users messages get --params '{"userId":"me","id":"MSG_ID","format":"full"}' | jq '[.payload.parts[] | select(.filename != "") | {filename, body: .body.attachmentId}]'

# 2. 下载（cd 到目标目录）
cd /path/to/target/dir
gws gmail users messages attachments get --params '{"userId":"me","messageId":"MSG_ID","id":"ATTACHMENT_ID"}' --output filename.pdf
```

### 线程 / 回复链

按对话线程查看邮件，避免重复同一封邮件的多个副本：

```bash
gws gmail users threads list --params '{"userId":"me","q":"is:unread","maxResults":10}'
gws gmail users threads get --params '{"userId":"me","id":"THREAD_ID","format":"metadata"}'
```

### 标签管理

```bash
gws gmail users labels list --params '{"userId":"me"}' | jq '.labels[] | {id, name, type}'
gws gmail users labels create --json '{"name":"Projects/AI","labelListVisibility":"labelShow","messageListVisibility":"show"}' --params '{"userId":"me"}'
gws gmail users messages batchModify --params '{"userId":"me"}' --json '{"ids":["MSG_ID"],"addLabelIds":["LABEL_ID"]}'
```

### Trash

```bash
gws gmail users messages trash --params '{"userId":"me","id":"MSG_ID"}'
gws gmail users messages untrash --params '{"userId":"me","id":"MSG_ID"}'
```

### 设置

```bash
gws gmail users settings getVacation --params '{"userId":"me"}'
gws gmail users settings sendAs list --params '{"userId":"me"}'
```

---

## Drive

**Drive** 支持文件和文件夹的完整生命周期管理。所有 `--upload` 和 `--output` 路径仅支持相对路径，必须先 `cd` 到目标目录。

### 浏览与搜索

```bash
gws drive files list --params '{"pageSize":10,"orderBy":"modifiedTime desc"}'
gws drive files list --params '{"q":"mimeType=\"application/vnd.google-apps.spreadsheet\""}'
gws drive files list --params '{"q":"'\''FOLDER_ID'\'' in parents"}'
```

### 上传（两步命名）

`files create` 的 name 参数无效（CLI 未传递给 API），上传后文件名始终为 "Untitled"，必须先上传再 rename。注意：`files copy` 的 name 参数有效，不受此限制。

```bash
cd /path/to/target/dir
gws drive files create --params '{}' --upload file.txt --upload-content-type text/plain
gws drive files update --params '{"fileId":"FILE_ID"}' --json '{"name":"real_name.txt"}'
```

### 创建文件夹

```bash
gws drive files create --params '{}' --json '{"name":"Folder Name","mimeType":"application/vnd.google-apps.folder"}'
```

### 复制与移动

`files copy` 的 name 参数有效（与 upload 不同），可一步完成：

```bash
# 复制（可同时重命名）
gws drive files copy --params '{"fileId":"ID"}' --json '{"name":"Copy of file"}'

# 移动到文件夹
gws drive files update --params '{"fileId":"ID","addParents":"FOLDER_ID","removeParents":"root"}' --json '{}'
```

### 下载与导出

**决策原则**：原生文件（txt, pdf, docx 等）用 `get --alt media`；Google 原生格式（Sheets, Docs, Slides）用 `export` 转换。

```bash
gws drive files get --params '{"fileId":"ID","alt":"media"}' --output file.txt
gws drive files export --params '{"fileId":"ID","mimeType":"application/pdf"}' --output doc.pdf
gws drive files export --params '{"fileId":"ID","mimeType":"text/csv"}' --output data.csv
```

### 权限与存储

```bash
gws drive permissions list --params '{"fileId":"ID","pageSize":10}'
gws drive about get --params '{"fields":"storageQuota"}' | jq '.storageQuota'
```

### 删除

`files delete` 成功时返回 `{"status":"success","saved_file":"download.html"}` 而非空 JSON，忽略即可。

```bash
gws drive files delete --params '{"fileId":"ID"}'
```

---

## Calendar

**Calendar** 支持完整的事件 CRUD、日历管理、忙碌查询和权限控制。所有时间参数使用 RFC 3339 格式。

### 事件管理

```bash
# 查询事件
gws calendar events list --params '{"calendarId":"primary","timeMin":"START_DATETIME","timeMax":"END_DATETIME","maxResults":20}'

# 创建事件
gws calendar events insert --json '{"summary":"Meeting","start":{"dateTime":"DATETIME_START","timeZone":"Asia/Shanghai"},"end":{"dateTime":"DATETIME_END","timeZone":"Asia/Shanghai"}}' --params '{"calendarId":"primary"}'

# 更新/删除事件
gws calendar events update --params '{"calendarId":"primary","eventId":"EVENT_ID"}' --json '{"summary":"Updated"}'
gws calendar events delete --params '{"calendarId":"primary","eventId":"EVENT_ID"}'

# 查看重复事件的所有实例
gws calendar events instances --params '{"calendarId":"primary","eventId":"RECURRING_EVENT_ID"}'
```

### 忙碌查询与权限

```bash
# 查看忙碌/空闲时段
gws calendar freebusy query --json '{"timeMin":"START_DT","timeMax":"END_DT","items":[{"id":"primary"}]}'

# 日历权限
gws calendar acl list --params '{"calendarId":"primary"}'
```

### 日历管理

```bash
# 创建/删除二级日历
gws calendar calendars insert --json '{"summary":"My Calendar"}' --params '{}'
gws calendar calendars delete --params '{"calendarId":"CALENDAR_ID"}'

# 日历列表管理
gws calendar calendarList list --params '{"maxResults":10}'
```

---

## Sheets

**Sheets** 支持完整的电子表格操作：读写单元格、公式、格式化、行列操作、条件格式、冻结等。

Sheet 名称不一定是 "Sheet1"，`+read` 的 range 必须用实际 sheet 名，先 `get` 获取 `.sheets[].properties.title`。

### 创建与读取

```bash
# 创建 Spreadsheet
gws sheets spreadsheets create --json '{"properties":{"title":"My Sheet"}}' --params '{}'

# 获取 sheet 名称
SHEET=$(gws sheets spreadsheets get --params '{"spreadsheetId":"ID"}' 2>/dev/null | jq -r '.sheets[0].properties.title')

# 读取
gws sheets +read --spreadsheet "ID" --range "${SHEET}!A1:C10"
```

### 编辑单元格

```bash
# 更新单元格（RAW = 原样写入）
gws sheets spreadsheets values update --params '{"spreadsheetId":"ID","range":"Sheet1!A1","valueInputOption":"RAW"}' --json '{"values":[["New Value"]]}'

# 输入公式（必须用 USER_ENTERED，不能用 RAW）
gws sheets spreadsheets values update --params '{"spreadsheetId":"ID","range":"Sheet1!C1","valueInputOption":"USER_ENTERED"}' --json '{"values":[["=AVERAGE(B2:B10)"]]}'
gws sheets spreadsheets values update --params '{"spreadsheetId":"ID","range":"Sheet1!D1","valueInputOption":"USER_ENTERED"}' --json '{"values":[["=SUM(B2:B10)"]]}'
gws sheets spreadsheets values update --params '{"spreadsheetId":"ID","range":"Sheet1!E1","valueInputOption":"USER_ENTERED"}' --json '{"values":[["=IF(B2>90,\"A\",\"B\")"]]}'

# 追加行（注意：+append 没有 --range 参数，始终追加到第一个 sheet 末尾）
gws sheets +append --spreadsheet "ID" --values 'col1,col2'
gws sheets +append --spreadsheet "ID" --json-values '[["col1","col2"],["col3","col4"]]'

# 清空单元格（保留格式）
gws sheets spreadsheets values clear --params '{"spreadsheetId":"ID","range":"Sheet1!A1:C10"}'
```

### 行列操作

```bash
# 删除行
gws sheets spreadsheets batchUpdate --params '{"spreadsheetId":"ID"}' --json '{"requests":[{"deleteDimension":{"range":{"sheetId":0,"dimension":"ROWS","startIndex":2,"endIndex":3}}}]}'

# 插入行/列
gws sheets spreadsheets batchUpdate --params '{"spreadsheetId":"ID"}' --json '{"requests":[{"insertDimension":{"range":{"sheetId":0,"dimension":"COLUMNS","startIndex":1,"endIndex":2},"inheritFromBefore":true}}]}'

# 合并单元格
gws sheets spreadsheets batchUpdate --params '{"spreadsheetId":"ID"}' --json '{"requests":[{"mergeCells":{"range":{"sheetId":0,"startRowIndex":0,"endRowIndex":1,"startColumnIndex":0,"endColumnIndex":3},"mergeType":"MERGE_ALL"}}]}'

# 设置列宽/行高
gws sheets spreadsheets batchUpdate --params '{"spreadsheetId":"ID"}' --json '{"requests":[{"updateDimensionProperties":{"range":{"sheetId":0,"dimension":"COLUMNS","startIndex":0,"endIndex":1},"properties":{"pixelSize":200},"fields":"pixelSize"}}]}'
```

### 格式化

```bash
# 单元格背景色
gws sheets spreadsheets batchUpdate --params '{"spreadsheetId":"ID"}' --json '{"requests":[{"repeatCell":{"range":{"sheetId":0,"startRowIndex":0,"endRowIndex":1},"cell":{"userEnteredFormat":{"backgroundColor":{"red":0.2,"green":0.6,"blue":1}},"fields":"userEnteredFormat.backgroundColor"}}}]}'

# 条件格式
gws sheets spreadsheets batchUpdate --params '{"spreadsheetId":"ID"}' --json '{"requests":[{"addConditionalFormatRule":{"rule":{"ranges":[{"sheetId":0,"startRowIndex":1,"endRowIndex":100}],"booleanRule":{"condition":{"type":"NUMBER_GREATER","values":[{"userEnteredValue":"90"}]},"format":{"backgroundColor":{"red":0,"green":1,"blue":0}}}},"index":0}}]}'

# 冻结行/列
gws sheets spreadsheets batchUpdate --params '{"spreadsheetId":"ID"}' --json '{"requests":[{"updateSheetProperties":{"properties":{"sheetId":0,"gridProperties":{"frozenRowCount":1,"frozenColumnCount":1}},"fields":"gridProperties.frozenRowCount,gridProperties.frozenColumnCount"}}]}'
```

---

## Docs

**Docs** 支持创建、读取、编辑文档。文档编辑通过 `batchUpdate` 实现。

```bash
# 创建
gws docs documents create --json '{"title":"My Doc"}' --params '{}'

# 提取纯文本
gws docs documents get --params '{"documentId":"ID"}' | jq '[.body.content[]|select(.paragraph)|.paragraph.elements[]?|select(.textRun)|.textRun.content]|join("")'
```

### 编辑

```bash
# 插入文本（index 1 = 文档开头）
gws docs documents batchUpdate --json '{"requests":[{"insertText":{"location":{"index":1},"text":"Hello World\n"}}]}' --params '{"documentId":"ID"}'

# 设置文本样式（加粗、斜体、字号、颜色等）
gws docs documents batchUpdate --json '{"requests":[{"updateTextStyle":{"range":{"startIndex":1,"endIndex":6},"textStyle":{"bold":true},"fields":"bold"}}]}' --params '{"documentId":"ID"}'

# 设置段落样式（标题、列表等）
gws docs documents batchUpdate --json '{"requests":[{"updateParagraphStyle":{"range":{"startIndex":1,"endIndex":10},"style":{"namedStyleType":"HEADING_1"},"fields":"namedStyleType"}}]}' --params '{"documentId":"ID"}'

# 插入图片
gws docs documents batchUpdate --json '{"requests":[{"insertInlineImage":{"uri":"https://example.com/image.png","location":{"index":1}}}]} --params '{"documentId":"ID"}'

# 创建列表（bullet）
gws docs documents batchUpdate --json '{"requests":[{"createParagraphBullets":{"range":{"startIndex":1,"endIndex":20},"bulletPreset":"BULLET_DISC_CIRCLE_SQUARE"}}]}' --params '{"documentId":"ID"}'
```

---

## Slides

**Slides** 支持创建、读取、编辑演示文稿。编辑通过 `batchUpdate` 实现。

```bash
# 创建
gws slides presentations create --json '{"title":"My Slides"}' --params '{}'

# 获取元数据
gws slides presentations get --params '{"presentationId":"ID"}' | jq '{title, slideCount: (.slides | length)}'
```

### 编辑

```bash
# 创建文本框并插入文本
gws slides presentations batchUpdate --json '{"requests":[{"createShape":{"objectId":"shape1","shapeType":"TEXT_BOX","elementProperties":{"pageObjectId":"p1","size":{"width":{"magnitude":4000000,"unit":"EMU"},"height":{"magnitude":300000,"unit":"EMU"}},"transform":{"scaleX":1,"scaleY":1,"translateX":100000,"translateY":100000,"unit":"EMU"}}}},{"insertText":{"objectId":"shape1","text":"Hello Slides!"}}]}' --params '{"presentationId":"ID"}'

# 设置文本样式（加粗 + 字号）
gws slides presentations batchUpdate --json '{"requests":[{"updateTextStyle":{"objectId":"shape1","style":{"bold":true,"fontSize":{"magnitude":36,"unit":"PT"}},"textRange":{"type":"ALL"},"fields":"bold,fontSize"}}]}' --params '{"presentationId":"ID"}'

# 新增幻灯片
gws slides presentations batchUpdate --json '{"requests":[{"createSlide":{"objectId":"slide2"}}]}' --params '{"presentationId":"ID"}'

# 插入图片
gws slides presentations batchUpdate --json '{"requests":[{"createImage":{"url":"https://example.com/image.png","elementProperties":{"pageObjectId":"p1","size":{"width":{"magnitude":3000000,"unit":"EMU"},"height":{"magnitude":2000000,"unit":"EMU"}},"transform":{"scaleX":1,"scaleY":1,"translateX":500000,"translateY":500000,"unit":"EMU"}}}}]}' --params '{"presentationId":"ID"}'
```

> 注意：`presentations create` 输出的是完整对象，提取 presentationId 需要解析 JSON。Slides 坐标单位为 EMU（1 inch = 914400 EMU）。

---

## Forms

**Forms** 支持创建表单、添加题目和查看回复。`forms create` 只能创建空表单（仅 title 生效），添加题目需要用 `batchUpdate`。

```bash
# 创建空表单
gws forms forms create --json '{"info":{"title":"Survey"}}' --params '{}'

# 添加文本题目（location 是必填字段，放在 createItem 级别）
gws forms forms batchUpdate --json '{"requests":[{"createItem":{"location":{"index":0},"item":{"title":"What is your name?","questionItem":{"question":{"required":true,"textQuestion":{}}}}}}]}' --params '{"formId":"FORM_ID"}'

# 查看回复
gws forms forms responses list --params '{"formId":"FORM_ID"}'
```

---

## Tasks

**Tasks** 支持任务列表 CRUD 和完成状态管理。

```bash
gws tasks tasklists list | jq '.items[]|{title,id}'
gws tasks tasks list --params '{"tasklist":"@default"}' | jq '.items[]|{title,status,due}'
gws tasks tasks insert --json '{"title":"Task","notes":"Details"}' --params '{"tasklist":"@default"}'
gws tasks tasks patch --params '{"tasklist":"@default","task":"TASK_ID"}' --json '{"status":"completed"}'
gws tasks tasks delete --params '{"tasklist":"@default","task":"TASK_ID"}'
gws tasks tasks clear --params '{"tasklist":"@default"}'  # 清除所有已完成任务
```

---

## People

**People** 支持个人资料、联系人搜索/创建和分组管理。`searchContacts` 必须指定 `readMask`，不传会报 400。`connections list` 不需要。

```bash
# 个人资料
gws people people get --params '{"resourceName":"people/me","personFields":"names,emailAddresses"}'

# 搜索联系人（必须指定 readMask）
gws people people searchContacts --params '{"query":"keyword","pageSize":10,"readMask":"names,emailAddresses,phoneNumbers"}'

# 联系人列表
gws people connections list --params '{"resourceName":"people/me","personFields":"names,emailAddresses,phoneNumbers","pageSize":10}'

# 创建联系人
gws people people createContact --json '{"names":[{"givenName":"First","familyName":"Last"}],"emailAddresses":[{"value":"email@example.com"}]}' --params '{"readMask":"names,emailAddresses"}'

# 联系人分组
gws people contactGroups list --params '{"pageSize":10}'
```

---

## Meet / Classroom

**Meet** 支持会议记录查询。**Classroom** 支持课程、学生和作业管理（需要教育账号）。

```bash
# Meet: 会议记录
gws meet conferenceRecords list --params '{"pageSize":10}'
gws meet conferenceRecords get --params '{"name":"RECORD_ID"}'

# Classroom: 课程、学生、作业
gws classroom courses list --params '{"pageSize":10}'
gws classroom courses students list --params '{"courseId":"COURSE_ID"}'
gws classroom courses.courseWork list --params '{"courseId":"COURSE_ID"}'
```

---

## Workflow Helpers

快捷工作流命令，适合日常自动化场景：

```bash
gws workflow +standup-report        # 今日会议 + 待办任务
gws workflow +meeting-prep          # 下一个会议准备
gws workflow +weekly-digest         # 本周会议 + 未读邮件数
gws workflow +email-to-task --message-id "MSG_ID"  # Gmail → Tasks
```

---

## General

```bash
gws schema <service>              # 列出该服务所有方法
gws schema <api.method>           # 查询具体参数结构
gws <service> <method> --params '{}' --format table   # 表格输出（给人类看）
gws <service> <method> --params '{}' --page-all       # 自动翻页
```

不确定参数时先查 schema，不要猜。JSON + jq 是默认输出模式，`--format table` 仅用于给人类看。
