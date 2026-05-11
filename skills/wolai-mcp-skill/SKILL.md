---
name: wolai
description: 通过 wolai Open API 操作 wolai 笔记，支持读取页面/块内容、创建各类块（文本、标题、代码、待办、列表、媒体等）、获取数据库、向数据库插入数据、获取/刷新 Token、分页遍历。当用户需要读取 wolai 页面、向 wolai 写入内容、操作 wolai 数据库、或与 wolai 进行任何数据交互时使用此 skill。触发场景：「读取 wolai 页面」、「在 wolai 里写入」、「查询 wolai 数据库」、「往 wolai 插入数据」、「获取 wolai token」、「遍历 wolai 所有内容」等。
allowed-tools:
disable: true
runtime: windows-powershell
credentials:
  WOLAI_TOKEN:
    description: "wolai App Token（永久有效，expire_time: -1），通过 POST /token 用 appId+appSecret 换取"
    required: true
source:
  type: github
  url: https://github.com/cizixiu/wolai-api-skill
---

# wolai API Skill

通过 wolai Open API（RESTful）操作 wolai 的块、页面、数据库。

Base URL：`https://openapi.wolai.com/v1`

---

## Setup

### 1. 创建应用并获取 Token

1. 前往 https://www.wolai.com/dev 创建应用（需空间管理员权限）
2. 选择所需**应用能力**（最小权限原则）：
   - 读取页面内容
   - 插入页面内容
   - 更新页面内容
3. 创建后得到 `App ID` 和 `App Secret`
4. 调用 `POST /token` 换取 `app_token`
5. 将 Token 告知 AI 助手，由 AI 负责完成后续配置

> ⚠️ **Token 安全须知**
>
> wolai App Token 设计为永久有效（`expire_time: -1`），这是 wolai 平台的设计。使用时请勿将 Token 泄露给他人或公开到代码库/聊天记录中。如泄露：在 wolai 应用管理页面重置 App Secret，然后重新调用 `POST /token` 获取新 Token（旧 Token 立即失效）。

### 2. 工作空间权限说明

| 空间类型 | 权限规则 |
|--------|--------|
| **个人空间** | 默认拥有全部页面权限，无需额外操作 |
| **团队空间** | 每个页面需单独添加应用：页面右上角 → 页面协作 → 应用权限 → 添加应用 |

---

## 凭证预检

每次调用前先检查 Token：

```powershell
if (-not $env:WOLAI_TOKEN) {
    Write-Error "缺少 WOLAI_TOKEN，请按 Setup 步骤配置"
    exit 1
}
```

---

## API 调用封装

所有请求统一使用 PowerShell（Windows 环境），Token 放在 `Authorization` Header：

```powershell
function Invoke-WolaiApi {
    param(
        [string]$Method = "GET",
        [string]$Path,
        [hashtable]$Body = $null,
        [hashtable]$Query = $null,
        [switch]$RawJson  # 新增：返回原始 JSON 字符串而非对象（避免中文乱码）
    )
    # ⚠️ 必须强制 UTF-8，否则中文内容会变成问号
    [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
    $OutputEncoding = [System.Text.Encoding]::UTF8

    $headers = @{
        "Authorization" = $env:WOLAI_TOKEN
        "Content-Type"  = "application/json; charset=utf-8"
    }

    $uri = "https://openapi.wolai.com/v1$Path"

    # 拼接 Query 参数（用于分页等）
    if ($Query) {
        $qs = ($Query.GetEnumerator() | ForEach-Object {
            # URL 编码值（防止特殊字符问题）
            "$($_.Key)=$([System.Web.HttpUtility]::UrlEncode("$($_.Value)"))"
        }) -join "&"
        $uri = "$uri?$qs"
    }

    try {
        if ($RawJson) {
            # 返回原始 JSON 字符串（适合中文内容）
            $resp = Invoke-WebRequest -Method $Method -Uri $uri -Headers $headers
            if ($Body) {
                $bodyBytes = [System.Text.Encoding]::UTF8.GetBytes(($Body | ConvertTo-Json -Depth 10))
                $resp = Invoke-WebRequest -Method $Method -Uri $uri -Headers $headers -Body $bodyBytes
            }
            return $resp.Content
        } else {
            # 返回解析后的对象
            if ($Body) {
                $bodyBytes = [System.Text.Encoding]::UTF8.GetBytes(($Body | ConvertTo-Json -Depth 10))
                $response = Invoke-RestMethod -Method $Method -Uri $uri -Headers $headers -Body $bodyBytes
            } else {
                $response = Invoke-RestMethod -Method $Method -Uri $uri -Headers $headers
            }
            return $response
        }
    } catch {
        # 解析 wolai API 错误响应
        $errBody = $_.ErrorDetails.Message | ConvertFrom-Json
        if ($errBody.error_code) {
            Write-Error "wolai API 错误 [$($errBody.error_code)]: $($errBody.message)"
        } else {
            Write-Error "请求失败: $($_.Exception.Message)"
        }
        return $null
    }
}
```

**解决中文乱码的两种方式：**

```powershell
# 方式1：写入文件（推荐，完美支持中文）
$json = Invoke-WolaiApi -Method GET -Path "/databases/p4NEGH7dgHEvKZDBzaKuRh" -RawJson
[System.IO.File]::WriteAllText("D:\output.json", $json, [System.Text.UTF8Encoding]::new($false))

# 方式2：通过对象属性访问（适合程序处理）
$db = Invoke-WolaiApi -Method GET -Path "/databases/p4NEGH7dgHEvKZDBzaKuRh"
$db.data.rows[0].data  # 直接访问嵌套属性，控制台可能乱码但值正确
```

**频率控制（5次/秒限制保护）：**

```powershell
# 在连续多次调用 API 时，加入间隔避免触发频率限制
# wolai 限制：同一用户 5次/秒，即每次调用至少间隔 200ms
$script:lastWolaiCall = [DateTime]::MinValue

function Wait-WolaiRateLimit {
    param([int]$MinIntervalMs = 250)  # 留 50ms 余量
    $elapsed = ((Get-Date) - $script:lastWolaiCall).TotalMilliseconds
    if ($elapsed -lt $MinIntervalMs) {
        Start-Sleep -Milliseconds ($MinIntervalMs - $elapsed)
    }
    $script:lastWolaiCall = Get-Date
}

# 使用示例：在循环中调用
do {
    Wait-WolaiRateLimit
    $resp = Invoke-WolaiApi -Method GET -Path "/blocks/$pageId/children" -Query $query
    # ...
} while ($resp.has_more)
```

---

## 接口决策表

| 用户意图 | 接口 | 说明 |
|---------|------|------|
| 读取页面/块信息 | `GET /blocks/{id}` | id 为页面 ID 或块 ID |
| 读取页面下所有子块 | `GET /blocks/{id}/children` | 支持分页 `?page_size=&start_cursor=` |
| 向页面写入/追加内容 | `POST /blocks` | 需指定 `parent_id`，一次最多 20 个块 |
| 读取数据库（表格） | `GET /databases/{id}` | 支持分页，每次最多 200 行 |
| 向数据库插入行 | `POST /databases/{id}/rows` | 字段名需与列名完全匹配，一次最多 20 行 |
| 获取 Token | `POST /token` | 需要 `appId` + `appSecret` |
| 刷新 Token（泄露时） | `PUT /token` | 旧 Token 立即失效 |

---

## 接口限制

| 限制类型 | 说明 |
|--------|------|
| **频率** | 同一用户 5 次/秒 |
| **批量获取** | 一次最多 200 条，超出用分页 |
| **批量创建/更新** | 一次最多 20 条 |
| **删除** | 每次只能删除 1 条 |
| **附件上传** | 每次 1 个，最大 1024MB |

**每小时/每月用量限制（按套餐）：**

| 套餐 | 每小时 | 每月 |
|-----|-------|------|
| 个人免费版 | 10次 | 100次 |
| 个人专业版 | 500次 | 10,000次 |
| 家庭版 | 800次 | 20,000次 |
| 小组版 | 1,000次 | 30,000次 |
| 团队版 | 1,500次 | 60,000次 |
| 企业版 | 3,000次 | 200,000次 |

---

## 常用工作流

### 读取页面/块信息

```powershell
# 页面 ID 从 URL 获取：wolai.com/ 后面的部分即为页面 ID
$pageId = "oaBQLqSBaMbS6S4NX4fJU7"

# 获取页面块基本信息（标题、类型等）
$page = Invoke-WolaiApi -Method GET -Path "/blocks/$pageId"
$page.data

# 获取页面第一层子块列表（默认最多 200 条）
$children = Invoke-WolaiApi -Method GET -Path "/blocks/$pageId/children"
$children.data
```

**返回的块对象字段说明：**

| 字段 | 类型 | 说明 |
|-----|-----|------|
| `id` | string | 块唯一 ID |
| `type` | string | 块类型（见块类型表） |
| `content` | array | 富文本内容数组 |
| `parent_id` | string | 父块 ID |
| `page_id` | string | 所在页面 ID |
| `children.ids` | array | 子块 ID 列表 |
| `created_at` | number | 创建时间戳（ms） |
| `edited_at` | number | 最后编辑时间戳（ms） |

---

### 分页遍历所有子块

当页面内容较多时，需要循环分页：

```powershell
$pageId = "your_page_id"
$allBlocks = @()
$cursor = $null

do {
    $query = @{ page_size = 200 }
    if ($cursor) { $query["start_cursor"] = $cursor }

    $resp = Invoke-WolaiApi -Method GET -Path "/blocks/$pageId/children" -Query $query
    $allBlocks += $resp.data
    $cursor = $resp.next_cursor
} while ($resp.has_more)

Write-Host "共获取 $($allBlocks.Count) 个块"
```

---

### 向页面写入内容（创建块）

```powershell
# 在指定页面末尾追加内容（可同时创建多个块，最多 20 个）
$result = Invoke-WolaiApi -Method POST -Path "/blocks" -Body @{
    parent_id = "oaBQLqSBaMbS6S4NX4fJU7"
    blocks = @(
        @{
            type    = "text"
            content = "这是一段普通文字"
        },
        @{
            type    = "heading"
            level   = 1
            content = "这是一级标题"
        },
        @{
            type    = "divider"  # 分隔线，无需 content
        }
    )
}
# 返回：成功时 $result.data 为新块的访问链接
```

---

### 创建富文本内容

`content` 字段（CreateRichText）支持三种写法：

```powershell
# 写法1：纯字符串（最简单）
content = "Hello World"

# 写法2：单个富文本对象（可设置样式）
content = @{
    title      = "加粗红色文字"
    bold       = $true
    front_color = "red"
}

# 写法3：混合数组（字符串和富文本对象混用）
content = @(
    @{ title = "加粗"; bold = $true },
    "普通文字",
    @{ title = "斜体高亮"; italic = $true; highlight = $true }
)
```

**RichText 可用样式属性：**

| 属性 | 类型 | 说明 |
|-----|-----|------|
| `title` | string | 文本内容（必填） |
| `bold` | boolean | 加粗 |
| `italic` | boolean | 斜体 |
| `underline` | boolean | 下划线 |
| `highlight` | boolean | 高亮 |
| `strikethrough` | boolean | 删除线 |
| `inline_code` | boolean | 行内代码 |
| `front_color` | BlockFrontColors | 文字颜色 |
| `back_color` | BlockBackColors | 背景色 |

> ⚠️ 注意：创建块时 RichText 的 `type` 字段暂只支持 `"text"` 和 `"equation"`（纯文本可不传 type）

---

### 各类块的完整创建示例

```powershell
# 文本块（支持富文本）
@{ type = "text"; content = "Hello" }

# 标题块（level 1-4）
@{ type = "heading"; level = 2; content = "二级标题"; toggle = $false }

# 引用块
@{ type = "quote"; content = "这是引用内容" }

# 着重文字块（callout）
@{
    type = "callout"
    content = "重要提示"
    icon = @{ type = "emoji"; icon = "⚠️" }
    # marquee_mode = $true  # 开启跑马灯滚动效果
}

# 代码块
@{
    type = "code"
    language = "python"  # 也可用 "mermaid" 画流程图/时序图
    content  = "print('Hello, wolai!')"
    caption  = "示例代码"
    code_setting = @{
        line_number = $true    # 显示行号
        line_break  = $true    # 自动换行
        ligatures   = $false   # 连字符
    }
}

# 任务列表（todo_list）
@{ type = "todo_list"; content = "待办事项"; checked = $false }

# 高级任务列表（todo_list_pro）
@{
    type        = "todo_list_pro"
    content     = "高级任务"
    task_status = "doing"   # "todo" | "doing" | "done" | "cancel"
}

# 无序列表
@{ type = "bull_list"; content = "• 列表项" }

# 有序列表
@{ type = "enum_list"; content = "有序列表项" }

# 折叠列表
@{ type = "toggle_list"; content = "折叠标题" }

# 分隔线
@{ type = "divider" }

# 进度条
@{ type = "progress_bar"; progress = 75; auto_mode = $false; hide_number = $false }

# 书签
@{ type = "bookmark"; link = "https://www.wolai.com" }

# 图片/视频/音频媒体块
@{ type = "image"; link = "https://example.com/image.png"; caption = "图片说明" }
@{ type = "video"; link = "https://example.com/video.mp4" }
@{ type = "audio"; link = "https://example.com/audio.mp3" }

# 三方嵌入块
@{ type = "embed"; original_link = "https://www.youtube.com/watch?v=xxx" }

# 公式块（LaTeX）
@{ type = "block_equation"; content = "e^{i\pi} + 1 = 0" }

# 页面块（子页面）
@{
    type = "page"
    content = "子页面标题"
    icon = @{ type = "emoji"; icon = "📄" }
    # page_setting = @{ is_full_width = $true; is_small_text = $false; has_floating_catalog = $true }
    # page_cover = @{ type = "link"; url = "https://example.com/cover.jpg" }
}
```

> ❌ **不支持在创建块接口中使用的类型**：`file`、`database`、`meeting`、`reference`、`simple_table`、`template_button`、`row`、`column`

---

### 页面设置（page_setting）

创建子页面时可配置页面属性：

| 属性 | 类型 | 默认值 | 说明 |
|-----|------|-------|------|
| `is_full_width` | boolean | false | 自适应宽度（取消默认左右边距） |
| `is_small_text` | boolean | false | 小字体模式 |
| `has_floating_catalog` | boolean | false | 显示浮动标题目录 |
| `font_family` | string | `"default"` | 字体：`"default"` / `"simsun"`（宋体）/ `"kaiti"`（楷体） |
| `line_spacing` | string | `"default"` | 行距：`"default"` / `"loose"`（宽松）/ `"compact"`（紧凑） |

**示例：创建一个有特殊设置和封面的子页面**
```powershell
@{
    type = "page"
    content = "项目文档"
    icon = @{ type = "emoji"; icon = "📋" }
    page_cover = @{ type = "link"; url = "https://example.com/cover.jpg" }
    page_setting = @{
        is_full_width = $true
        font_family = "kaiti"
        line_spacing = "loose"
    }
}
```

### 图标（icon）格式

页面块和着重文字块支持两种图标类型：

| 类型 | 格式 | 示例 |
|-----|------|------|
| **emoji 图标** | `{ type = "emoji"; icon = "..." }` | `{ type = "emoji"; icon = "📄" }` |
| **网络图标** | `{ type = "fontAwesome"; icon = "fa-github" }` | FontAwesome 图标名称 |
| **链接图标** | `{ type = "link"; icon = "https://..." }` | 图片 URL 作为图标 |

### 代码块（code）完整属性

| 属性 | 类型 | 说明 |
|-----|------|------|
| `type` | `"code"` | 必填 |
| `language` | CodeLanguage | 必填，代码语言（支持 90+ 种，含 `mermaid` 流程图） |
| `content` | string | 代码内容 |
| `caption` | string | 代码块说明文字 |
| `code_setting` | object | 代码显示设置 |

**code_setting 子属性：**

| 属性 | 类型 | 说明 |
|-----|------|------|
| `line_number` | boolean | 显示行号 |
| `line_break` | boolean | 自动换行 |
| `ligatures` | boolean | 启用连字符 |
| `preview_format` | string | 预览格式：`"both"` / `"code"` / `"mermaid"`（仅 mermaid/ybsz 有效） |

### 代码语言（language）

wolai 支持 90+ 种代码语言，常用值：

| 类别 | 语言 |
|-----|------|
| **主流** | `python`、`javascript`、`typescript`、`java`、`go`、`rust`、`c`、`cpp`、`csharp` |
| **Web** | `html`、`css`、`scss`、`json`、`xml`、`yaml`、`markdown` |
| **脚本** | `powershell`、`bash`、`dart`、`lua`、`perl`、`ruby` |
| **数据** | `sql`、`graphql`、`protobuf` |
| **可视化** | `mermaid`（流程图/时序图）、`ybsz`（仪表数字） |
| **其他** | `swift`、`kotlin`、`scala`、`matlab`、`r`、`dockerfile`、`nginx` |

---

### 块的颜色值

**文字颜色（`front_color` / `block_front_color`）：**

`"default"` | `"gray"` | `"dark_gray"` | `"brown"` | `"orange"` | `"yellow"` | `"green"` | `"blue"` | `"indigo"` | `"purple"` | `"pink"` | `"red"`

**背景色（`back_color` / `block_back_color`）：**

`"default"` | `"cultured_background"` | `"light_gray_background"` | `"apricot_background"` | `"vivid_tangerine_background"` | `"blond_background"` | `"aero_blue_background"` | `"uranian_blue_background"` | `"lavender_blue_background"` | `"pale_purple_background"` | `"pink_lavender_background"` | `"light_pink_background"` | `"fluorescent_yellow_background"` | `"fluorescent_green_background"` | `"fluorescent_green2_background"` | `"fluorescent_blue_background"` | `"fluorescent_purple_background"` | `"fluorescent_purple2_background"`

**文字对齐（`text_alignment`）：**

`"center"`（居中）

**块对齐（`block_alignment`）：**

`"left"` | `"center"` | `"right"`

---

### 读取数据库（表格）

```powershell
$dbId = "your_database_id"

# 基本查询（默认返回前 200 行）
$db = Invoke-WolaiApi -Method GET -Path "/databases/$dbId"
$db.data  # 返回行数据数组

# 分页查询（适用于数据量大的表格）
$allRows = @()
$cursor = $null

do {
    $query = @{ page_size = 200 }
    if ($cursor) { $query["start_cursor"] = $cursor }

    $resp = Invoke-WolaiApi -Method GET -Path "/databases/$dbId" -Query $query
    $allRows += $resp.data
    $cursor = $resp.next_cursor
} while ($resp.has_more)

Write-Host "共获取 $($allRows.Count) 行数据"

# 输出每一行的字段和值
$allRows | ForEach-Object {
    Write-Host "---" -ForegroundColor Gray
    $_.PSObject.Properties | ForEach-Object {
        Write-Host "$($_.Name): $($_.Value)"
    }
}
```

**数据库响应结构：**

| 字段 | 类型 | 说明 |
|-----|-----|------|
| `data` | array | 行数据数组，每行是一个键值对对象 |
| `next_cursor` | string | 下一页游标，`has_more=true` 时存在 |
| `has_more` | boolean | 是否还有更多数据 |

**每行数据示例：**
```json
{
    "姓名": "张三",
    "年龄": 28,
    "状态": "进行中",
    "创建时间": 1671523112626
}
```

> **数据库限制**：单个数据表最多支持 10,000 行、100 列、10 个视图。

---

### 数据库高级查询

根据 API 规范和常见需求，可能支持的查询方式：

```powershell
# 按页码大小查询
$query = @{ page_size = 50 }
Invoke-WolaiApi -Method GET -Path "/databases/$dbId" -Query $query

# 使用游标分页（官方推荐方式，数据量大时性能更好）
$query = @{ start_cursor = "cursor_from_previous_response"; page_size = 100 }
Invoke-WolaiApi -Method GET -Path "/databases/$dbId" -Query $query
```

> ⚠️ **注意**：API 文档中关于数据库查询的具体筛选/排序参数说明有缺失。如需筛选特定条件（如按状态筛选、按日期排序），请参考 wolai 官方开发者中心最新文档或通过 Apifox 测试接口。

---

### 数据库 ID 获取方式

数据库（表格）本质上也是一种块，可通过以下方式获取 ID：

| 方式 | 说明 |
|-----|------|
| **从 URL 获取** | 打开数据库所在页面，URL 中 `/` 后的部分即为页面 ID（数据库通常嵌入在页面中） |
| **从页面子块中查找** | 调用 `GET /blocks/{pageId}/children`，在返回的块中找到 `type="database"` 的块，其 `id` 即为数据库 ID |

**示例：从页面中查找数据库块**
```powershell
$pageId = "your_page_id"
$children = Invoke-WolaiApi -Method GET -Path "/blocks/$pageId/children"

# 查找类型为 database 的块
$databaseBlock = $children.data | Where-Object { $_.type -eq "database" }
$dbId = $databaseBlock.id
Write-Host "数据库 ID: $dbId"
```

---

### 向数据库插入行

```powershell
$dbId = "your_database_id"

# 插入单行：字段名需与数据库列名完全匹配（中文列名也支持）
$result = Invoke-WolaiApi -Method POST -Path "/databases/$dbId/rows" -Body @{
    rows = @(
        @{
            "任务名称" = "完成项目报告"
            "负责人"   = "张三"
            "状态"     = "进行中"
            "截止日期" = "2026-03-31"
        }
    )
}
# 返回：成功时 $result.data 为新行的访问链接

# 批量插入（一次最多 20 行）
$result = Invoke-WolaiApi -Method POST -Path "/databases/$dbId/rows" -Body @{
    rows = @(
        @{ "姓名" = "张三"; "分数" = 90 },
        @{ "姓名" = "李四"; "分数" = 85 },
        @{ "姓名" = "王五"; "分数" = 92 }
    )
}
```

**插入数据注意事项：**

| 注意事项 | 说明 |
|---------|------|
| **列名匹配** | 字段名必须与数据库中定义的列名完全一致（包括空格、大小写） |
| **必填字段** | 数据库中标记为必填的列必须在插入时提供值 |
| **字段类型** | 确保插入的数据类型与列类型匹配（文本/数字/日期/选项等） |
| **选项字段** | 选项类型的列，值必须是预定义的选项之一 |
| **批量限制** | 一次最多插入 20 行，超出需分批调用 |

---

### 数据库常见操作示例

**场景1：从 CSV 批量导入数据到 wolai 数据库**
```powershell
$dbId = "your_database_id"

# 读取 CSV 文件
$csvData = Import-Csv "D:\data\users.csv"

# 批量插入（每次最多 20 行）
$batchSize = 20
$total = $csvData.Count

for ($i = 0; $i -lt $total; $i += $batchSize) {
    $batch = $csvData | Select-Object -Skip $i -First $batchSize
    $rows = $batch | ForEach-Object {
        # 将 CSV 行转为自定义对象
        $obj = @{}
        $_.PSObject.Properties | ForEach-Object {
            $obj[$_.Name] = $_.Value
        }
        $obj
    }

    Invoke-WolaiApi -Method POST -Path "/databases/$dbId/rows" -Body @{ rows = $rows }
    Write-Host "已插入 $([Math]::Min($i + $batchSize, $total)) / $total 行"
}
```

**场景2：根据条件查询数据库**
```powershell
$dbId = "your_database_id"

# 获取所有数据
$allRows = @()
$cursor = $null

do {
    $query = @{ page_size = 200 }
    if ($cursor) { $query["start_cursor"] = $cursor }
    $resp = Invoke-WolaiApi -Method GET -Path "/databases/$dbId" -Query $query
    $allRows += $resp.data
    $cursor = $resp.next_cursor
} while ($resp.has_more)

# 筛选：查找状态为"进行中"的任务
$inProgressTasks = $allRows | Where-Object { $_.状态 -eq "进行中" }
Write-Host "找到 $($inProgressTasks.Count) 个进行中的任务"

# 筛选：查找截止日期在 7 天内的任务
$deadline = (Get-Date).AddDays(7).ToString("yyyy-MM-dd")
$urgentTasks = $allRows | Where-Object {
    $_.截止日期 -and [DateTime]::Parse($_.截止日期) -le (Get-Date).AddDays(7)
}
Write-Host "有 $($urgentTasks.Count) 个任务将在 7 天内截止"
```

**场景3：数据统计分析**
```powershell
$dbId = "your_database_id"

# 获取所有数据（分页）
$allRows = @()
$cursor = $null

do {
    $query = @{ page_size = 200 }
    if ($cursor) { $query["start_cursor"] = $cursor }
    $resp = Invoke-WolaiApi -Method GET -Path "/databases/$dbId" -Query $query
    $allRows += $resp.data
    $cursor = $resp.next_cursor
} while ($resp.has_more)

# 按状态分组统计
$byStatus = $allRows | Group-Object "状态" | ForEach-Object {
    [PSCustomObject]@{
        状态  = $_.Name
        数量  = $_.Count
        占比 = [Math]::Round($_.Count * 100 / $allRows.Count, 2)
    }
}

Write-Host "任务状态分布："
$byStatus | Format-Table -AutoSize

# 按负责人统计任务数
$byAssignee = $allRows | Group-Object "负责人" | Sort-Object Count -Descending
Write-Host "`n各负责人任务数："
$byAssignee | ForEach-Object {
    Write-Host "$($_.Name): $($_.Count) 个任务"
}
```

---

### 获取 Token（首次配置）

```powershell
$resp = Invoke-RestMethod -Method POST `
    -Uri "https://openapi.wolai.com/v1/token" `
    -Headers @{ "Content-Type" = "application/json; charset=utf-8" } `
    -Body (@{ appId = "your_app_id"; appSecret = "your_app_secret" } | ConvertTo-Json)

$token = $resp.appToken.app_token
Write-Host "Token: $token"
# 将此值配置为 WOLAI_TOKEN
```

**返回结构：**
```json
{
    "appToken": {
        "app_token": "2e6db3fc...",
        "app_id": "qGPon7ra...",
        "create_time": 1671523112626,
        "expire_time": -1,
        "update_time": 1671523112626
    }
}
```

> Token 永久有效（`expire_time: -1`），泄露后调用 `PUT /token` 刷新，旧 Token 立即失效。

---

### 刷新 Token（泄露时使用）

```powershell
# 使用相同的 appId + appSecret，PUT 方法刷新
$resp = Invoke-RestMethod -Method PUT `
    -Uri "https://openapi.wolai.com/v1/token" `
    -Headers @{ "Content-Type" = "application/json; charset=utf-8" } `
    -Body (@{ appId = "your_app_id"; appSecret = "your_app_secret" } | ConvertTo-Json)

$newToken = $resp.appToken.app_token
# 更新环境变量
$env:WOLAI_TOKEN = $newToken
```

---

## 错误处理

| 错误码 | HTTP状态码 | 含义 | 建议处理 |
|-------|----------|------|---------|
| 17001 | 400 | 缺少参数 | 检查必填字段 |
| 17002 | 400 | 参数错误 | 检查参数格式和类型 |
| 17003 | 401 | 无效 Token | 检查 WOLAI_TOKEN 是否正确，或重新获取 |
| 17004 | 404 | 获取资源失败 | 检查 ID 是否正确 |
| 17005 | 404 | 资源未找到 | 检查页面/块 ID 是否存在 |
| 17006 | 500 | 服务器内部错误 | 稍后重试 |
| 17007 | 429 | 请求过于频繁 | 降低调用频率（≤5次/秒） |
| 17008 | 413 | 请求体过大 | 拆分为多次请求（每次≤20条） |
| 17009 | 415 | 不支持的媒体类型 | 检查 Content-Type Header |
| 17010 | 400 | 暂不支持的块类型 | 检查 type 字段，见块类型说明 |
| 17011 | 403 | 权限不足 | 团队空间需在页面添加应用权限 |

**错误响应统一格式：**
```json
{
    "message": "错误描述（含解决建议）",
    "error_code": 17003,
    "status_code": 401
}
```

---

## 注意事项

- **页面 ID**：从 URL 获取，`wolai.com/` 后面的部分即为 ID（如 `wolai.com/oaBQLq...` → ID 为 `oaBQLq...`）
- **块 ID**：从块菜单内「复制块 ID」获取
- **Token 永久有效**（`expire_time: -1`），泄露后调用 `PUT /token` 刷新，旧 Token 立即失效
- **App Secret 泄露**：在应用管理页面重置 App Secret，然后重新调用 `POST /token` 获取新 Token
- **团队空间**每个页面都需单独添加应用，个人空间无需此操作
- **UTF-8 编码**：PowerShell 默认编码可能导致中文乱码，封装函数已处理，直接使用 Invoke-WolaiApi 即可
- **创建块后**：接口返回新块的可访问链接（`data` 字段），格式为 `https://www.wolai.com/pageId#blockId`
