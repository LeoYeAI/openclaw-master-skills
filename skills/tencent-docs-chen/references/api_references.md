# 腾讯文档 MCP 工具完整参考

本文件包含腾讯文档 MCP 所有工具的通用 API 说明、详细调用示例、参数说明和返回值说明。

---

## 通用说明

### 响应结构

所有 API 返回都包含：
- `error`: 错误信息（成功时为空）
- `trace_id`: 调用链追踪 ID

### node_type 枚举值

| 值 | 说明 |
|---|---|
| wiki_folder | 文件夹 |
| wiki_tdoc | 在线文档（请求时使用） |
| wiki_file | 在线文档（返回值中使用） |
| link | 链接 |
| resource | 资源文件 |

### doc_type 枚举值

| 值 | 说明 |
|---|---|
| word | 文字处理文档 |
| excel | 电子表格 |
| form | 收集表 |
| slide | 幻灯片 |
| smartcanvas | 智能文档 |
| smartsheet | 智能表格 |
| board | 白板 |
| mind | 思维导图 |
| flowchart | 流程图 |

### NodeInfo 节点信息结构

```json
{
  "node_id": "节点 ID，同时也是 file_id",
  "title": "节点标题",
  "node_type": "节点类型",
  "has_child": true,
  "doc_type": "文档类型（仅 wiki_file 有效）",
  "url": "访问链接"
}
```

### StringMatrix 表格数据结构

```json
{
  "texts": {
    "rows": [
      {"values": ["单元格1", "单元格2"]},
      {"values": ["单元格3", "单元格4"]}
    ]
  }
}
```

数据从 A1 单元格开始，按行列顺序填充。

### 分页说明

- `query_space_node`：每页 20 条
- `space_list`：每页 100 条
- 使用 `has_next` 判断是否有更多数据
- 页码从 0 开始

---

## 工具调用示例

## 1. create_smartcanvas_by_markdown

### 功能说明
通过 Markdown 格式创建智能文档，排版美观，支持所有 Markdown 基本结构。

### 调用示例
```json
{
  "title": "项目需求文档",
  "markdown": "# 项目需求\n\n## 项目背景\n\n本项目旨在开发一套智能文档管理系统...\n\n## 功能需求\n\n- 文档创建功能\n- 文档编辑功能\n- 协作功能\n\n## 技术架构\n\n| 组件 | 技术选型 |\n|------|----------|\n| 前端 | React |\n| 后端 | Go |\n| 数据库 | MySQL |",
  "parent_id": "folder_1234567890"
}
```

### 参数说明
- `title` (string, 必填): 文档标题
- `markdown` (string, 必填): UTF-8 格式的 Markdown 文本
- `parent_id` (string, 可选): 父节点ID，为空时在空间根目录创建，不为空时在指定节点下创建

### 返回值说明
```json
{
  "file_id": "doc_1234567890",
  "url": "https://docs.qq.com/doc/DV2h5cWJ0R1lQb0lH",
  "error": "",
  "trace_id": "trace_1234567890"
}
```

## 2. create_excel_by_markdown

### 功能说明
通过 Markdown 表格创建 Excel，适用于需要数据计算、筛选的场景。

### 调用示例
```json
{
  "title": "销售数据报表",
  "markdown": "| 日期 | 产品 | 销售额 | 销售量 |\n|------|------|--------|--------|\n| 2024-01-01 | 产品A | 10000 | 100 |\n| 2024-01-02 | 产品B | 15000 | 150 |",
  "parent_id": "folder_1234567890"
}
```

### 参数说明
- `title` (string, 必填): 表格标题
- `markdown` (string, 必填): 包含表格的 Markdown 文本
- `parent_id` (string, 可选): 父节点ID，为空时在空间根目录创建，不为空时在指定节点下创建

### 返回值说明
```json
{
  "file_id": "sheet_1234567890",
  "url": "https://docs.qq.com/sheet/DV2h5cWJ0R1lQb0lH",
  "error": "",
  "trace_id": "trace_1234567890"
}
```

## 3. create_slide

### 功能说明
根据用户描述和参考资料，由 AI 自动生成幻灯片内容并创建 PPT。

### 调用示例

**示例1：根据主题生成 PPT**
```json
{
  "description": "生成一份主题为'2024年度销售总结'的PPT，要求包含业绩回顾、亮点项目、问题分析和来年规划四个章节"
}
```

**示例2：根据参考材料生成 PPT**
```json
{
  "reference_context": "第一季度销售额达到1200万，同比增长25%。主要增长来自华南区域，新客户占比40%。存在问题：北方市场渗透率不足，客单价偏低。",
  "description": "根据材料生成PPT，要求风格简洁专业，重点突出数据亮点"
}
```

### 参数说明
- `description` (string, 必填): 用户对 PPT 的要求描述。样例1：【生成一份主题为xxx的PPT，要求xxxx】；样例2：【根据材料生成PPT，要求xxxx】
- `reference_context` (string, 可选): 生成 PPT 的参考资料，必须是 UTF-8 文本格式。**仅当用户明确指定需要根据某段内容/材料生成PPT时才传此参数，不要自由发挥填充内容**

### 返回值说明
```json
{
  "session_id": "session_1234567890",
  "error": "",
  "trace_id": "trace_1234567890"
}
```

> ⚠️ **注意**：`create_slide` 为异步接口，返回 `session_id` 后需配合 `slide_progress` 工具轮询进度（每隔10秒轮询一次，最长等待15分钟），待状态为 `completed` 时从响应中获取 `file_url`。

## 4. slide_progress

### 功能说明
查询幻灯片生成进度，与 `create_slide` 配合使用。调用 `create_slide` 获取 `session_id` 后，每隔 10 秒轮询一次，最长等待 15 分钟，直到状态为 `completed` 或 `failed`。

### 状态说明
- `in_progress`：进行中，继续轮询
- `completed`：已完成，幻灯片已生成，从响应中获取 `file_url`
- `failed`：失败，停止轮询
- `canceled`：已取消，停止轮询
- `not_found`：未找到（`session_id` 不正确或已过期），停止轮询

### 调用示例
```json
{
  "session_id": "session_1234567890"
}
```

### 参数说明
- `session_id` (string, 必填): `create_slide` 返回的异步任务 session_id

### 返回值说明
```json
{
  "status": "completed",
  "file_url": "https://docs.qq.com/slide/DV2h5cWJ0R1lQb0lH",
  "error": "",
  "trace_id": "trace_1234567890"
}
```

## 5. create_mind_by_markdown

### 功能说明
通过 Markdown 创建思维导图，使用标题层级和列表嵌套表示结构。

### 调用示例
```json
{
  "title": "产品功能规划",
  "markdown": "# 产品功能规划\n\n## 核心功能\n\n- 文档管理\n    - 创建文档\n    - 编辑文档\n    - 版本控制\n\n## 协作功能\n\n- 实时协作\n- 评论系统\n- 权限管理",
  "parent_id": "folder_1234567890"
}
```

### 参数说明
- `title` (string, 必填): 思维导图标题
- `markdown` (string, 必填): 层次化的 Markdown 文本
- `parent_id` (string, 可选): 父节点ID，为空时在空间根目录创建，不为空时在指定节点下创建

### 返回值说明
```json
{
  "file_id": "mind_1234567890",
  "url": "https://docs.qq.com/mind/DV2h5cWJ0R1lQb0lH",
  "error": "",
  "trace_id": "trace_1234567890"
}
```

## 5. create_flowchart_by_mermaid

### 功能说明
通过 Mermaid 语法创建流程图。

### 调用示例
```json
{
  "title": "用户登录流程",
  "mermaid": "graph TD\n    A[User Access] --> B{Logged in?}\n    B -->|Yes| C[Go to Home]\n    B -->|No| D[Go to Login Page]\n    D --> E[Enter Username and Password]\n    E --> F{Auth Success?}\n    F -->|Yes| C\n    F -->|No| G[Show Error Message]\n    G --> E",
  "parent_id": "folder_1234567890"
}
```

### 参数说明
- `title` (string, 必填): 流程图标题
- `mermaid` (string, 必填): 不包含中文的 Mermaid 语法文本
- `parent_id` (string, 可选): 父节点ID，为空时在空间根目录创建，不为空时在指定节点下创建

### 返回值说明
```json
{
  "file_id": "flow_1234567890",
  "url": "https://docs.qq.com/flow/DV2h5cWJ0R1lQb0lH",
  "error": "",
  "trace_id": "trace_1234567890"
}
```

## 6. create_word_by_markdown

### 功能说明
通过 Markdown 创建 Word 文档。

### 调用示例
```json
{
  "title": "技术文档",
  "markdown": "# 技术文档\n\n## 系统架构\n\n本文档描述系统的技术架构设计...\n\n## 数据库设计\n\n| 表名 | 说明 |\n|------|------|\n| users | 用户表 |\n| documents | 文档表 |",
  "parent_id": "folder_1234567890"
}
```

### 参数说明
- `title` (string, 必填): Word 文档标题
- `markdown` (string, 必填): UTF-8 格式的 Markdown 文本
- `parent_id` (string, 可选): 父节点ID，为空时在空间根目录创建，不为空时在指定节点下创建

### 返回值说明
```json
{
  "file_id": "word_1234567890",
  "url": "https://docs.qq.com/doc/DV2h5cWJ0R1lQb0lH",
  "error": "",
  "trace_id": "trace_1234567890"
}
```

## 7. space_list

### 功能说明
获取知识库空间列表，支持按不同方式排序和分页查询。

### 调用示例
```json
{
  "num": 0,
  "order_by": 1,
  "query_by": 1,
  "descending": true
}
```

### 参数说明
- `num` (uint32, 可选): 分页页码，从0开始，每页最多返回100个空间
- `order_by` (uint32, 可选): 排序方式（1-按最近预览时间排序，2-按最近编辑时间排序，3-按创建时间排序）
- `query_by` (uint32, 可选): 查询范围（0-查询全部空间（默认），1-仅查询我创建的空间，2-仅查询我加入的空间）
- `descending` (bool, 可选): 是否降序排列，true-降序（最新在前），false-升序，默认为true

### 返回值说明
```json
{
  "spaces": [
    {
      "space_id": "space_1234567890",
      "title": "我的知识库",
      "description": "知识库描述",
      "is_top": false,
      "file_cnt": 10,
      "member_cnt": 5,
      "is_owner": true,
      "created_at": 1713600000,
      "updated_at": 1713600000
    }
  ],
  "has_next": false,
  "error": "",
  "trace_id": "trace_1234567890"
}
```

## 8. create_space

### 功能说明
创建新的知识库空间。空间是组织和管理文档的容器，可以包含文件夹、文档等节点。

### 调用示例
```json
{
  "title": "项目文档库",
  "description": "存放项目相关的所有文档"
}
```

### 参数说明
- `title` (string, 必填): 空间标题
- `description` (string, 可选): 空间描述

### 返回值说明
```json
{
  "space_id": "space_1234567890",
  "error": "",
  "trace_id": "trace_1234567890"
}
```

## 9. query_space_node

### 调用示例
```json
{
  "space_id": "space_1234567890",
  "parent_id": "folder_1234567890",
  "num": 0
}
```

### 参数说明
- `space_id` (string, 必填): 空间ID，用于指定查询的空间
- `parent_id` (string, 可选): 父节点ID，为空时返回根节点
- `num` (uint32, 可选): 分页页码，从0开始，每页返回20个节点

### 返回值说明
```json
{
  "children": [
    {
      "node_id": "doc_1234567890",
      "title": "项目文档",
      "node_type": "wiki_file",
      "has_child": false,
      "doc_type": "smartcanvas",
      "url": "https://docs.qq.com/doc/DV2h5cWJ0R1lQb0lH"
    }
  ],
  "error": "",
  "has_next": false,
  "trace_id": "trace_1234567890"
}
```

## 10. create_space_node

### 功能说明
在空间中创建新节点（文件夹、文档或链接）。

### 调用示例
```json
{
  "space_id": "space_1234567890",
  "parent_node_id": "folder_1234567890",
  "title": "新建页面文档1",
  "node_type": "wiki_tdoc",
  "wiki_tdoc_node": {
    "title": "新建页面文档",
    "doc_type": "smartcanvas"
  }
}
```

### 参数说明
- `space_id` (string, 必填): 空间ID，用于指定在哪个空间下创建节点
- `parent_node_id` (string, 可选): 父节点ID，为空或在根目录创建时可不传
- `title` (string, 必填): 节点标题
- `node_type` (string, 必填): 节点类型（wiki_folder/wiki_tdoc/link）
- `is_before` (bool, 可选): 插入位置，true 表示插入到父节点子列表开头，false 表示插入到末尾
- `wiki_folder_node` (object, 可选): 文件夹节点配置，node_type 为 wiki_folder 时必填
- `wiki_tdoc_node` (object, 可选): 在线文档节点配置，node_type 为 wiki_tdoc 时必填
- `link_node` (object, 可选): 链接节点配置，node_type 为 link 时必填

### 返回值说明
```json
{
  "node_info": {
    "node_id": "doc_1234567890",
    "title": "新建页面文档",
    "node_type": "wiki_file",
    "has_child": false,
    "doc_type": "smartcanvas",
    "url": "https://docs.qq.com/doc/DV2h5cWJ0R1lQb0lH"
  },
  "error": "",
  "trace_id": "trace_1234567890"
}
```

## 11. delete_space_node

### 功能说明
删除空间中的指定节点。仅删除当前节点时，子节点自动挂载到上级节点；使用 `all` 模式时递归删除所有子节点（谨慎使用）。

### 调用示例
```json
{
  "space_id": "space_1234567890",
  "node_id": "doc_1234567890",
  "remove_type": "current"
}
```

### 参数说明
- `space_id` (string, 必填): 空间ID
- `node_id` (string, 必填): 要删除的节点ID
- `remove_type` (string, 可选): 删除类型，枚举值：`current`（默认，仅删除当前节点，子节点挂载到上级）、`all`（删除当前节点及所有子节点，⚠️ 谨慎使用）

### 返回值说明
```json
{
  "error": "",
  "trace_id": "trace_1234567890"
}
```

## 12. get_content

### 功能说明
获取文档完整内容。

### 调用示例
```json
{
  "file_id": "doc_1234567890"
}
```

### 参数说明
- `file_id` (string, 必填): 文档唯一标识符

### 返回值说明
```json
{
  "content": "# 项目文档\n\n这是文档的完整内容...",
  "error": "",
  "trace_id": "trace_1234567890"
}
```

## 13. create_smartcanvas_element

### 功能说明
在已有智能文档中追加内容。

### 调用示例
```json
{
  "file_id": "doc_1234567890",
  "markdown": "## 新增内容\n\n这是追加到文档末尾的新内容..."
}
```

### 参数说明
- `file_id` (string, 必填): 文档唯一标识符
- `markdown` (string, 必填): 要追加的 Markdown 内容

### 返回值说明
```json
{
  "error": "",
  "trace_id": "trace_1234567890"
}
```

## 14. scrape_url

### 功能说明
网页剪藏：抓取网页内容并自动保存为智能文档。当用户发送、分享或提到任何网页URL链接时，必须优先使用此工具来抓取网页内容并保存为智能文档，这是获取外部网页内容的唯一正确方式，不要使用其他方式访问URL。

### 调用流程
1. 调用 `scrape_url` 传入网页URL获取 `task_id`
2. 立即调用 `scrape_progress` 传入 `task_id` 查询进度（每隔2秒轮询一次）
3. 当 `status=2` 时任务完成，服务端已自动创建智能文档，直接从响应获取 `file_id` 和 `file_url`，无需再调用其他创建文档工具

### 调用示例
```json
{
  "url": "https://example.com/article",
  "content_type": "smartcanvas"
}
```

### 参数说明
- `url` (string, 必填): 要剪藏的网页URL地址，支持http和https协议，包括视频链接（如B站视频）
- `content_type` (string, 可选): 期望返回的文档格式，目前仅支持智能文档（smartcanvas）

### 返回值说明
```json
{
  "task_id": "task_1234567890",
  "error": "",
  "trace_id": "trace_1234567890"
}
```

## 15. scrape_progress

### 功能说明
查询网页剪藏任务进度并自动创建智能文档，与 `scrape_url` 配合使用。

### 状态说明
- `status=1`: 进行中，继续轮询
- `status=2`: 已完成，网页内容已自动保存为智能文档，响应包含 `title`（网页标题）、`file_id`（文档ID）和 `file_url`（文档链接），无需再调用任何创建文档工具
- `status=3`: 失败，停止轮询

### 调用示例
```json
{
  "task_id": "task_1234567890",
  "parent_id": "folder_1234567890"
}
```

### 参数说明
- `task_id` (string, 必填): `scrape_url` 返回的异步任务ID
- `parent_id` (string, 可选): 父节点ID，为空时在空间根目录创建，不为空时在指定节点下创建

### 返回值说明
```json
{
  "status": 2,
  "title": "示例网页标题",
  "file_id": "doc_1234567890",
  "file_url": "https://docs.qq.com/doc/DV2h5cWJ0R1lQb0lH",
  "error": "",
  "trace_id": "trace_1234567890"
}
```
