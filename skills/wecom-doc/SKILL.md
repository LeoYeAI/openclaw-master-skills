---
name: wecom-doc
description: 文档与智能表格操作。当用户提到企业微信文档、创建文档、编辑文档、新建文档、写文档、智能表格时激活。支持文档创建/写入和智能表格的创建及子表/字段/记录写入。注意：所有文档创建和编辑请求都应使用此 skill，不要尝试用其他方式处理文档操作。
metadata:
  {
    "openclaw":
      {
        "emoji": "📄",
        "always": true,
        "requires":
          {
            "bins": ["mcporter"],
          },
        "install":
          [
            {
              "id": "mcporter",
              "kind": "node",
              "package": "mcporter",
              "bins": ["mcporter"],
              "label": "Install mcporter (npm)",
            },
          ],
      },
  }
---

# 企业微信文档与智能表格工具

通过 mcporter 调用 wecom-doc MCP server 操作企业微信文档和智能表格。

## 意图处理

当用户说"创建文档"、"新建文档"、"帮我写个文档"等**不指定平台**的请求时，默认使用企业微信文档，无需询问用户使用什么平台。

## 前置检查（每次会话首次操作前必须执行）

> **自动续接原则**：前置检查中的任何环节如果需要等待用户确认或操作（安装、配置、授权等），在该操作完成后必须**自动继续执行后续步骤**，最终完成用户的原始请求。不要在中间环节完成后停下来等用户重复发起请求。

### 1. 检查 mcporter 是否安装

```bash
which mcporter
```

如果 `mcporter` **不在 PATH 中**（命令返回空或 not found），**必须原样输出以下提示**（不要修改、不要摘要）：

> 企业微信文档能力依赖 mcporter 工具，当前尚未安装。需要我帮你安装吗？

输出提示后**停止执行并等待用户回复**。

- 如果用户**确认安装**（回复"好"、"是"、"装吧"、"yes"、"ok" 等肯定语义），**立即执行**：

```bash
npm install -g mcporter
```

安装完成后**不要停下来**，直接继续执行后续的「检查 MCP Server 是否配置」步骤，无缝衔接用户原始请求。

- 如果用户**拒绝安装**，回复：

> 好的，你也可以手动执行 `npm install -g mcporter` 安装后再找我。

### 2. 确保 MCP Server 已配置

确认 mcporter 存在后，先检查配置是否已存在，仅在未配置时才尝试自动配置。

**验证配置：**

```bash
mcporter list wecom-doc --output json
```

如果返回正常（包含 tool 列表），说明已配置，**跳过自动配置，直接进入步骤 3**。

如果返回 **server not found**、**unknown server** 或类似错误，执行下方自动配置。

**自动配置（仅在未配置时执行）：**

读取 wecom 运行时配置文件，该文件由 wecom channel 长连接建立时写入：

```bash
cat ~/.openclaw/wecomConfig/config.json
```

检查 JSON 中是否存在 `mcpConfig.doc` 字段（含 `type` 和 `url`），如果存在则执行：

```bash
mcporter config add wecom-doc \
  --type "<mcpConfig.doc.type的值>" \
  --url "<mcpConfig.doc.url的值>"
```

配置完成后**再次执行** `mcporter list wecom-doc --output json` 验证。如果仍然失败，按下方"MCP Server 未配置"章节处理。

> ⚠️ 配置文件不存在或缺少 `mcpConfig.doc` 字段，说明 wecom channel 长连接尚未建立，应引导用户检查 wecom channel 是否正常运行。自动配置失败不应阻断流程，继续引导用户手动配置。

### 3. 获取 Tool 列表

`mcporter list` 成功后，返回的每个 tool 包含 `name`、`description`、`inputSchema`。

**不要硬编码 tool name 和参数**，据此构造 `mcporter call wecom-doc.<tool> --args '{...}' --output json` 调用。

## docid 管理规则（重要）

**仅支持对通过本 skill 创建的文档或智能表格进行编辑。**

### docid 的获取方式

docid **只能**通过 `create_doc` 的返回结果获取。创建成功后需要**保存返回的 docid**，后续编辑操作依赖此 ID。

### 不支持从 URL 解析 docid

从文档 URL（如 `https://doc.weixin.qq.com/doc/...`）中**无法解析到可用的 docid**。如果用户提供了文档 URL 并要求编辑，**不要尝试从 URL 中提取 docid**。

### 编辑操作的 docid 校验

当用户请求编辑文档或智能表格时，如果当前会话中**没有**通过 `create_doc` 获取到的 docid，**必须原样输出以下提示**（不要修改、不要摘要）：

> 仅支持对机器人创建的文档进行编辑

### docid 类型判断

| doc_id 前缀 | 类型 | doc_type |
|-------------|------|----------|
| `w3_` | 文档 | 3 |
| `s3_` | 智能表格 | 10 |

## 工作流

### 文档操作流

1. 如需新建文档 → `create_doc`（`doc_type: 3`）→ **保存返回的 `docid`**
2. 如需编辑内容 → 先确认当前会话中有通过 `create_doc` 获取的 `docid`，若无则提示"仅支持对机器人创建的文档进行编辑" → `edit_doc_content`（`content_type: 1` 使用 markdown，全量覆写）

> `edit_doc_content` 是**全量覆写**操作。如需追加内容，应先了解原有内容再拼接。

### 智能表格操作流

操作层级：**文档（docid）→ 子表（sheet_id）→ 字段（field_id）/ 记录（record_id）**

1. 如需新建智能表 → `create_doc`（`doc_type: 10`）→ **保存返回的 `docid`**
2. 如需编辑已有智能表 → 先确认当前会话中有通过 `create_doc` 获取的 `docid`，若无则提示"仅支持对机器人创建的文档进行编辑"
3. 查询已有子表 → `smartsheet_get_sheet` → 获取 `sheet_id`
4. 如需新建子表 → `smartsheet_add_sheet` → 获取新的 `sheet_id`
5. 查询已有字段 → `smartsheet_get_fields` → 获取 `field_id`、`field_title`、`field_type`
6. 如需添加字段 → `wedoc_smartsheet_add_fields`
7. 如需更新字段 → `wedoc_smartsheet_update_fields`（**不能改变字段类型**）
8. 添加数据记录 → `smartsheet_add_records`（values 的 key **必须**使用字段标题 field_title，不能用 field_id）

### 从零创建智能表完整流程

```
create_doc(doc_type=10) → docid
  └→ smartsheet_add_sheet(docid) → sheet_id
      └→ wedoc_smartsheet_add_fields(docid, sheet_id, fields) → field_ids
          └→ smartsheet_add_records(docid, sheet_id, records)
```

### 向已有智能表添加数据流程

```
smartsheet_get_sheet(docid) → sheet_id
  └→ smartsheet_get_fields(docid, sheet_id) → field_ids + field_titles + field_types
      └→ smartsheet_add_records(docid, sheet_id, records)
```

> **重要**：添加记录前**必须**先通过 `smartsheet_get_fields` 获取字段信息，确保 `values` 中的 key 和 value 格式正确。

## 业务知识（MCP Schema 中缺失的上下文）

以下信息是 MCP tool 的 inputSchema 中没有的，Agent 构造参数时必须参考。

### FieldType 枚举（16 种）

| 类型 | 说明 | 使用场景建议 |
|------|------|-------------|
| `FIELD_TYPE_TEXT` | 文本 | 通用文本内容；当用户只提供了成员**姓名**（而非 user_id）时，也应使用 TEXT 而非 USER |
| `FIELD_TYPE_NUMBER` | 数字 | 数值型数据（金额、数量、评分等） |
| `FIELD_TYPE_CHECKBOX` | 复选框 | 是/否、完成/未完成等布尔状态 |
| `FIELD_TYPE_DATE_TIME` | 日期时间 | 日期、截止时间、创建时间等 |
| `FIELD_TYPE_IMAGE` | 图片 | 需要展示图片的场景 |
| `FIELD_TYPE_USER` | 成员 | **仅**在明确知道成员 user_id 时使用；若用户只提供了姓名，应使用 TEXT 代替 |
| `FIELD_TYPE_URL` | 链接 | 网址、外部链接 |
| `FIELD_TYPE_SELECT` | 多选 | 标签、多分类等允许多选的场景 |
| `FIELD_TYPE_SINGLE_SELECT` | 单选 | 状态、优先级、严重程度、分类等有固定选项的字段 |
| `FIELD_TYPE_PROGRESS` | 进度 | 完成进度、完成百分比（值为 0-100 整数） |
| `FIELD_TYPE_PHONE_NUMBER` | 手机号 | 手机号码 |
| `FIELD_TYPE_EMAIL` | 邮箱 | 邮箱地址 |
| `FIELD_TYPE_LOCATION` | 位置 | 地理位置信息 |
| `FIELD_TYPE_CURRENCY` | 货币 | 金额（带货币符号） |
| `FIELD_TYPE_PERCENTAGE` | 百分比 | 百分比数值（值为 0~1） |
| `FIELD_TYPE_BARCODE` | 条码 | 条形码、ISBN 等 |

### FieldType ↔ CellValue 对照表

添加记录（`smartsheet_add_records`）时，`values` 中每个字段的 **key 必须使用字段标题（field_title），不能使用 field_id**。value 必须匹配其字段类型：

| 字段类型 | CellValue 格式 | 示例 |
|---------|---------------|------|
| `TEXT` | CellTextValue 数组 | `[{"type": "text", "text": "内容"}]` |
| `NUMBER` | number | `85` |
| `CHECKBOX` | boolean | `true` |
| `DATE_TIME` | 日期时间**字符串** | `"2023-01-01 12:00:00"`、`"2023-01-01 12:00"`、`"2023-01-01"` |
| `URL` | CellUrlValue 数组（限 1 个） | `[{"type": "url", "text": "百度", "link": "https://baidu.com"}]` |
| `USER` | CellUserValue 数组 | `[{"user_id": "zhangsan"}]` |
| `IMAGE` | CellImageValue 数组 | `[{"image_url": "https://..."}]`（`id`、`title` 可选） |
| `SELECT` | Option 数组（多选） | `[{"text": "选项A"}, {"text": "选项B"}]` |
| `SINGLE_SELECT` | Option 数组（限 1 个） | `[{"text": "选项A"}]` |
| `PROGRESS` | number（0~100 整数） | `85`（表示 85%） |
| `CURRENCY` | number | `99.5` |
| `PERCENTAGE` | number（0~1） | `0.85` |
| `PHONE_NUMBER` | string | `"13800138000"` |
| `EMAIL` | string | `"user@example.com"` |
| `BARCODE` | string | `"978-3-16-148410-0"` |
| `LOCATION` | CellLocationValue 数组（限 1 个） | `[{"source_type": 1, "id": "xxx", "latitude": "39.9", "longitude": "116.3", "title": "北京"}]` |

> **Option 格式说明**：`SINGLE_SELECT`/`SELECT` 的选项支持 `style` 字段（1~27 对应不同颜色），如 `[{"text": "紧急", "style": 1}]`。`style` 为可选字段，不传则使用默认颜色。

### 易错点

- `DATE_TIME` 的值是**日期时间字符串**，支持 `"YYYY-MM-DD HH:MM:SS"`（精确到秒）、`"YYYY-MM-DD HH:MM"`（精确到分）、`"YYYY-MM-DD"`（精确到天），系统自动按东八区转换为时间戳，无需手动计算
- `CellUrlValue` 的链接字段名是 **`link`**，不是 `url`
- `TEXT` 类型的值**必须**使用数组格式 `[{"type": "text", "text": "内容"}]`，外层方括号不可省略，不能传单个对象 `{"type":"text","text":"内容"}`
- `SINGLE_SELECT`/`SELECT` 类型的值**必须**使用数组格式 `[{"text": "选项内容"}]`，不能直接传字符串
- `PROGRESS` 的值范围是 **0~100 整数**（85 = 85%）；`PERCENTAGE` 的值范围是 **0~1**（0.85 = 85%），两者不同注意区分
- `wedoc_smartsheet_update_fields` **不能更改字段类型**，只能改标题和属性
- `values` 的 key **必须**使用**字段标题**（field_title），**不能**使用 field_id
- 不可写入的字段类型：创建时间、最后编辑时间、创建人、最后编辑人

## 错误处理

### MCP 错误响应处理（重要）

当 `mcporter call` 返回结果中 `errcode` 不为 0 且 `help_message` 有值时，将 `help_message` 中面向用户的内容输出给用户。

**输出原则：**

- **完整性**：不截断、不摘要
- **原样性**：不改写、不重新排版
- **用户可读性**：只输出面向用户的内容，过滤掉给 Agent 的元指令（如"将以下内容告知用户"等引导语）；直接以 markdown 形式输出，不要包裹在代码块中

### 错误码 850001：需要用户提供配置

当 `errcode` 为 `850001` 时：

1. 将 `help_message` 中面向用户的内容**原样输出**（遵循上方输出原则）
2. 输出后**等待用户回复**，后续流程与「MCP Server 未配置」的场景 A / B / C 一致。配置成功后**不要停下来**，立即回到「前置检查」的步骤 2 重新验证配置，验证通过后继续执行用户的原始请求。

### MCP Server 未配置

如果 `mcporter call wecom-doc.*` 或 `mcporter list wecom-doc` 返回 **server not found**、**unknown server** 或类似错误，说明 wecom-doc MCP server 尚未配置。

此时需要**检测运行环境**以提供针对性的提示。按以下步骤执行：

#### 步骤一：检测是否在 OpenClaw 运行时中

通过检测 `OPENCLAW_SHELL` 环境变量判断当前是否运行在 OpenClaw 中。该变量是 OpenClaw **运行时自动注入到子进程**中的标记，不会因为机器上安装了 openclaw 就存在——只有 skill 确实在 OpenClaw 中被调用时，exec 执行的命令才会携带此变量。

```bash
echo "OPENCLAW_SHELL=${OPENCLAW_SHELL:-}" && command -v openclaw 2>/dev/null && echo "OPENCLAW_CLI=FOUND" || echo "OPENCLAW_CLI=NOT_FOUND"
```

判断规则：
- **`OPENCLAW_SHELL` 为空**（输出 `OPENCLAW_SHELL=`）→ 当前不在 OpenClaw 运行时中，跳到**「通用提示」**。
- **`OPENCLAW_SHELL` 非空**（如 `exec`、`tui-local` 等）**且** `OPENCLAW_CLI=FOUND` → 确认在 OpenClaw 中且 CLI 可用，继续步骤二。
- **`OPENCLAW_SHELL` 非空但 `OPENCLAW_CLI=NOT_FOUND`** → 虽然在 OpenClaw 中但 CLI 不可用，跳到**「通用提示」**。

> 为什么不能仅用 `command -v openclaw`：同一台机器可能同时安装了 openclaw 和 claude 等其他 AI 工具。仅检测 CLI 是否存在无法区分"装了 openclaw"和"正在 openclaw 中运行"。`OPENCLAW_SHELL` 是进程级的运行时标记，从根本上解决此问题。

#### 步骤二：查询 wecom channel 的 botId 配置

```bash
openclaw config get channels.wecom.botId 2>&1
```

- 如果命令返回了**具体的 botId 值**（非空、非报错），保存该值，跳到**「OpenClaw 场景 + 有 botId 提示」**。
- 如果返回 `Config path not found`、报错或为空，跳到**「通用提示」**。

#### 异常容错

如果上述任何命令执行失败（如 exec 工具不可用、命令超时等），一律跳到**「通用提示」**。

---

#### OpenClaw 场景 + 有 botId 提示

当确认是 OpenClaw 环境且获取到了 botId 时，**必须原样输出以下提示**（不要修改、不要摘要），将 `XXXX` 替换为实际获取到的 botId 值：

> 若你是智能机器人创建者，可以[点击这里](https://work.weixin.qq.com/ai/aiHelper/authorizationPage?str_aibotid=XXXX&from=chat&forceInnerBrowser=1)授权当前机器人文档使用权限；
> 若你不是机器人创建者，可联系该机器人创建者，前往企业微信「工作台-智能机器人」找到对应机器人进行授权
> 若你已授权，可将对应机器人文档MCP的接入配置（StreamableHttp URL或者JSON Config）发送给我

输出提示后**等待用户回复**，后续流程与下方「通用提示」的后续流程一致（场景 A / B / C）。配置成功后**不要停下来**，立即回到「前置检查」的步骤 2 重新验证配置，验证通过后继续执行用户的原始请求。

---

#### 通用提示

当非 OpenClaw 环境、无法判断环境、或 OpenClaw 环境但未配置 wecom channel / botId 时，**必须原样输出以下提示文案**（不要修改、不要摘要）：

> 机器人可通过MCP方式调用文档相关能力，当前暂未完成所需配置。请参考以下配置指引：
>
> 1. 请前往「企业微信-工作台-智能机器人应用」，以API模式创建机器人（如已创建，可忽略该步骤）
>
> 2. 授权该机器人「文档」使用权限。授权后，可自行选择StreamableHttp URL 或 JSON Config 进行配置。

输出提示后**等待用户回复**。用户可能：

**场景 A：用户提供了 StreamableHttp URL**

从用户消息中提取 URL，执行：

```bash
mcporter config add wecom-doc \
  --type streamable-http \
  --url "<用户提供的URL>"
```

配置完成后**不要停下来**，立即回到「前置检查」的步骤 2 重新验证配置，验证通过后继续执行用户的原始请求。

**场景 B：用户提供了 JSON 配置**

如果用户提供了类似以下格式的 JSON：

```json
{
  "name": "wecom-doc",
  "type": "streamable-http",
  "url": "http://xxx"
}
```

从 JSON 中提取 `url` 字段，执行：

```bash
mcporter config add wecom-doc \
  --type streamable-http \
  --url "<从JSON提取的url>"
```

配置完成后**不要停下来**，立即回到「前置检查」的步骤 2 重新验证配置，验证通过后继续执行用户的原始请求。

**场景 C：用户自行完成了配置**

用户可能在管理后台或其他途径自行完成配置后告知已配置好，此时直接继续执行原来的操作。

> **配置检测**：当用户输入的内容包含 URL（如 `http://...`）或 JSON（含 `"type": "streamable-http"`），应判断用户意图是在提供 MCP server 配置信息，自动执行配置命令。

### Daemon 未启动

如果返回 **connection refused** 或 **daemon not running** 错误，提示用户：

```bash
mcporter daemon start
```


## 注意事项

- 所有调用通过 `mcporter call wecom-doc.<tool>` 执行，不要直接调用企业微信 API
- `create_doc` 返回的 `docid` 需要保存，后续操作依赖此 ID
- 添加记录前**必须**先 `smartsheet_get_fields` 获取字段元信息
