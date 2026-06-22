---
name: tencent-docs
description: Tencent Docs - Provides complete Tencent Docs operations. Use this skill when working with Tencent Docs, including: (1) Create various online documents (documents, Word, Excel, slides, mind maps, flowcharts) (2) Manage knowledge base spaces (create spaces, query space lists) (3) Manage space nodes and folder structure (4) Read document content (5) Edit smart sheets (6) Edit documents.
homepage: https://docs.qq.com/home
version: 1.0.11
author: tencent-docs
metadata: {"openclaw":{"primaryEnv":"TENCENT_DOCS_TOKEN","category":"tencent","tencentTokenMode":"custom","tokenUrl":"https://docs.qq.com/open/document/mcp/get-token/","emoji":"📝"}}
---

# SKILL Update

每天使用 SKILL 前进行一次更新检查，按照如下的步骤执行:

1. **查看当前版本version**：读取本文件顶部 frontmatter 中的 `version` 字段；格式为 MAJOR.MINOR.PATCH
2. **查看最新版本latest**：通过命令获取最新版本信息`latest`，输入参数 `version` 为上一步获取的当前版本
```bash
mcporter call "https://docs.qq.com/openapi/mcp" "check_skill_update" --args '{"version": "当前版本"}'
```
JSON 格式数据返回，返回参数示例：
  - `latest`: 最新版本号，格式为 MAJOR.MINOR.PATCH
  - `release_note`: 最新版本发布说明
  - `instruction`: 更新指令

3. **更新版本**：如果当前版本版本`version`低于最新版本`latest`，则遵循 `instruction` 指令进行更新，或提示用户更新

# Tencent Docs MCP Usage Guide

Tencent Docs MCP provides a complete set of online document operations, supporting creation, querying, and editing of various types of online documents.

## 支持的文档类型

| 类型 | doc_type | 推荐度 | 说明 |
|------|----------|--------|------|
| 文档 | smartcanvas | ⭐⭐⭐ **首选** | 排版美观，支持丰富组件 |
| Excel | excel | ⭐⭐⭐ | 数据表格专用 |
| PPT | slide | ⭐⭐⭐ | 幻灯片，演示文稿专用 |
| 思维导图 | mind | ⭐⭐⭐ | 知识图谱专用 |
| 流程图 | flowchart | ⭐⭐⭐ | 流程展示专用 |
| Word | word | ⭐⭐ | 传统格式，排版一般 |
| 收集表 | form | ⭐⭐ | 表单收集 |
| 智能表格 | smartsheet | ⭐⭐⭐ | 高级结构化表格，支持多视图、字段管理 |
| 白板 | board | ⭐⭐ | 在线白板 |

## API详细参考文档

首先需要阅读文件 `references/api_references.md` 查看所有工具的完整API说明，该文件包含工具的完整调用示例、参数说明、返回值说明及API结构、枚举值说明

### 🎯 场景化文档指引
根据您的具体任务场景，选择相应的参考文档进行查阅：

* 场景：报告、笔记、文章、总结等相关场景，选择文档`smartcanvas`
    - 阅读指引文件 `references/smartcanvas_references.md`，支持通过`smartcanvas.*` 系列工具来操作页面、文本、标题、待办事项等元素
* 场景：结构化数据管理相关场景，选择智能表格`smartsheet`
    - 阅读指引文件 `references/smartsheet_references.md`，支持通过`smartsheet.*` 系列工具来操作字段、记录、视图等元素
* 场景：计算、筛选、统计、Excal操作相关场景，选择在线表格`sheet`
    - 阅读指引文件 `references/sheet_references.md`，支持通过`sheet.*` 系列工具来操作表格、范围数据、批量更新单元格等元素
* 场景: 生成论文、作业、公文、合同、通知等专业规范化的文件和样式美化后的文档相关操作，选择Word文档`doc`
    - 阅读入口文件 `doc/entry.md` 了解整体能力和工作流程，支持通过`doc.*` 系列工具执行文档编写、美化等操作
* 场景: PPT文件演示文稿，需要逐页展示、投影演示相关场景，选择演示文稿`slide`
    - 阅读指引文件 `references/api_references.md`，支持通过 `create_slide` 工具创建幻灯片（AI 自动生成内容，异步接口），需配合 `slide_progress` 工具轮询进度（每隔10秒轮询一次，最长等待15分钟）
    - ⚠️ **重要**：幻灯片生成通常需要3~5分钟，每次轮询后**必须立即向用户输出当前状态**，例如：「正在生成中，第N次轮询，请稍候...」，严禁静默等待，避免用户误以为系统无响应
    - 待状态为 `completed` 时从响应中获取 `file_url` 并告知用户
* 场景: 层次化知识整理（知识图谱、大纲），选择思维导图`mind`
    - 阅读指引文件 `references/api_references.md`，支持通过`mind` 相关工具来操作思维导图、思维导图页、思维导图元素等元素
* 场景: 流程/架构展示（流程图、时序图），选择流程图`flowchart`
    - 阅读指引文件 `references/api_references.md`，支持通过`flowchart` 相关工具来操作流程图、流程图页、流程图元素等元素
* 场景: 白板演示场景，选择白板`board`
    - 阅读指引文件 `references/api_references.md`，支持通过`create_space_node` 工具来创建白板
* 场景: 数据收集填写等场景，选择收集表`form`
    - 阅读指引文件 `references/api_references.md`，支持通过`create_space_node` 工具来创建收集表
* 其他通用场景，选择文档`smartcanvas`

## ⚙️ 快速配置
在 OpenClaw 中使用时，需要先完成本地安装和注册。

**安装步骤：**

1. 运行 setup.sh 完成 MCP 服务注册：

```bash
bash setup.sh
```

> setup.sh 会自动将腾讯文档 MCP 服务注册到 mcporter，并验证配置是否成功。
> 如果未执行 setup，所有工具调用将无法找到 `tencent-docs` 服务。
> ⚠️ **如果 `TENCENT_DOCS_TOKEN` 为空或未配置**，请先访问 [https://docs.qq.com/scenario/open-claw.html](https://docs.qq.com/scenario/open-claw.html) 获取 Token，并配置环境变量：`export TENCENT_DOCS_TOKEN="你的Token值"`，否则所有工具调用将返回鉴权失败。

3. 验证安装是否成功：

```bash
mcporter list | grep tencent-docs
```

## 🔧 调用方式

### 获取完整的工具列表

1. 使用 `mcporter list tencent-docs` 获取工具列表和参数 Schema
2. 阅读 `references/` 目录下的参考文档查看调用示例、返回值结构和注意事项

> ⚠️ 参考文档中的参数说明应与 MCP 工具 Schema 保持一致。
> 如有冲突，以 `mcporter list tencent-docs` 返回的 Schema 为准。

### 工具列表示例

| 工具名称 | 功能说明                                     | 需要阅读的参考文档 |
|---------|------------------------------------------|----------|
| create_smartcanvas_by_markdown | ⭐ 创建文档（首选）                             | `references/api_references.md` |
| create_excel_by_markdown | 创建 Excel 表格                              | `references/api_references.md` |
| create_slide | 创建幻灯片（AI 自动生成，异步接口，需配合 slide_progress 每10秒轮询，**每次轮询后必须向用户输出实时状态**） | `references/api_references.md` |
| create_mind_by_markdown | 创建思维导图                                   | `references/api_references.md` |
| create_flowchart_by_mermaid | 创建流程图                                    | `references/api_references.md` |
| create_word_by_markdown | 创建 Word 文档                               | `references/api_references.md` |
| space_list | 获取知识库空间列表                                | `references/api_references.md` |
| create_space | 创建新的知识库空间                                | `references/api_references.md` |
| query_space_node | 查询空间节点                                   | `references/api_references.md` |
| create_space_node | 创建空间节点                                   | `references/api_references.md` |
| delete_space_node | 删除空间节点                                   | `references/api_references.md` |
| get_content | 获取文档内容                                   | `references/api_references.md` |
| upload_image | 上传图片，获取 image_id 供文档以及智能表格图片字段使用       | `references/api_references.md` |
| scrape_url | 网页剪藏：抓取网页内容并自动保存为文档，返回task_id用于进度查询    | `references/api_references.md` |
| scrape_progress | 查询网页剪藏任务进度，与scrape_url配合使用               | `references/api_references.md` |
| sheet.* | 在线表格操作（查询信息、获取范围、批量更新）                   | `references/sheet_references.md` |
| smartcanvas.* | 文档元素操作（页面/文本/标题/待办事项）                  | `references/smartcanvas_references.md` |
| smartsheet.* | 智能表格操作（工作表/视图/字段/记录）                     | `references/smartsheet_references.md` |
| manage.*  | 文件管理类操作（创建/删除/移动/重命名文档、生成副本、搜索文档、导入导出文档） | `references/manager_references.md`     |

### 调用示例

#### 获取正文内容 get_content

```
mcporter call "tencent-docs" "get_content" --args '{"file_id":"bLkQdUHejxNj"}'
```

#### 创建文档 create_smartcanvas_by_markdown

```
mcporter call "tencent-docs" "create_smartcanvas_by_markdown" --args '{"title": "测试title", "markdown": "# 腾讯文档 MCP 使用指南\n腾讯文档 MCP 提供了一套完整的在线文档操作工具，支持创建、查询、编辑多种类型的在线文档。## 支持的文档类型"}'
```

### 创建智能表格

```
mcporter call "tencent-docs" "create_space_node" --args '{"title": "测试智能表t1","node_type": "wiki_tdoc","wiki_tdoc_node": { "title": "测试智能表t1-1","doc_type": "smartsheet"}}'
```

### 查询智能表中的工作表 

```
mcporter call "tencent-docs" "smartsheet.list_tables" --args '{"file_id":"bDAzsLDGgmqw"}'
```

### 智能表中添加字段

```
mcporter call "tencent-docs" "smartsheet.add_fields" --args '{"file_id":"bEtvncBEcLos","sheet_id": "t00i2h", "fields": [{"field_title":"测试filed1", "field_type": 1}]}'
``` 

#### 创建表格 create_excel_by_markdown

```
mcporter call "tencent-docs" "create_excel_by_markdown" --args '{"title": "我的日程表", "markdown": "| 日期 | 时间 | 事项 | 地点 | 状态 | 备注 |\n|------|------|------|------|------|------|\n| 2024-03-11 | 09:00-10:00 | 团队会议 | 会议室A | 待办 | 准备项目汇报 |\n| 2024-03-11 | - | 项目文档编写 | 远程 | 进行中 | 完成需求文档 |\n| 2024-03-11 | 14:00-15:30 | 客户沟通 | 线上会议 | 已安排 | 准备演示材料 |\n| 2024-03-12 | 10:00-12:00 | 产品评审 | 会议室B | 待办 | 检查产品原型 |\n| 2024-03-12 | 15:00-16:00 | 培训学习 | 培训室 | 已安排 | AI工具使用 |\n| 2024-03-13 | 全天 | 项目开发 | 办公室 | 进行中 | 功能模块开发 |\n| 2024-03-14 | 09:30-11:00 | 周会总结 | 会议室A | 待办 | 整理本周工作 |\n| 2024-03-15 | 13:00-17:00 | 项目演示 | 客户现场 | 已安排 | 最终演示准备 |"}'
```

## 常见工作流

首先阅读 `references`目录下的所有参考文件，理解每个工具的功能和参数

### 创建通用文档（推荐方式）

**📖 参考文档：** `references/api_references.md` - create_smartcanvas_by_markdown

```
1. 优先调用 create_smartcanvas_by_markdown 创建文档
2. 从返回结果中获取 file_id 和 url
```

### 编辑已有文档

**📖 参考文档：** `references/smartcanvas_references.md` - 典型工作流示例

```
1. 调用 smartcanvas.get_top_level_pages 获取文档页面结构
2. 按需调用 smartcanvas.* 工具进行增删改查：
   - 追加内容：smartcanvas.append_insert_smartcanvas_by_markdown（Markdown 方式）
   - 新增元素：smartcanvas.create_smartcanvas_element
   - 查询元素：smartcanvas.get_element_info / smartcanvas.get_page_info
   - 修改元素：smartcanvas.update_element
   - 删除元素：smartcanvas.delete_element
```

### 组织文档到指定目录

**📖 参考文档：** `references/api_references.md` - query_space_node, create_space_node

1. 调用 `query_space_node` 查找目标文件夹
2. 调用 `create_space_node` 在目标位置创建文档节点（doc_type 优先选择 smartcanvas）

### 查找并读取文档

**📖 参考文档：** `references/api_references.md` - query_space_node, get_content

1. 调用 `query_space_node` 遍历节点树查找文档
2. 从结果中获取 `node_id`（即 `file_id`）
3. 调用 `get_content` 获取文档内容

### 智能表格操作工作流

**📖 参考文档：** `references/smartsheet_references.md` - 典型工作流示例

#### 从零搭建任务管理表

```
1. 获取工作表列表 → smartsheet.list_tables（获取 sheet_id）
2. 添加字段（列）→ smartsheet.add_fields（任务名称、优先级、截止日期等）
3. 批量写入数据 → smartsheet.add_records
4. （可选）创建看板视图 → smartsheet.add_view（view_type=2）
5. （可选）删除字段（列） → smartsheet.delete_fields
```

#### 查询并更新数据

```
1. 获取工作表 → smartsheet.list_tables
2. 查询记录   → smartsheet.list_records（获取 record_id）
3. 更新记录   → smartsheet.update_records（传入 record_id 和新字段值）
```

> 📖 更多智能表格工作流示例请参考：`references/smartsheet_references.md` - 典型工作流示例

### 在指定目录创建文档

**📖 参考文档：** `references/manage_references.md` - 典型工作流示例

```
1. 调用 manage.folder_list 获取文件夹目录
2. 按需调用 manage.* 工具进行文档增删改查、重命名、移动文档：
   - 重命名：manage.rename_file_title
   - 删除文档：manage.delete_file
   - 移动文档：manage.move_file
   - 生成副本：manage.copy_file
```

#### 搜索文档

```
1. 按照文档标题搜索文档 → manage.search_file（传入用户指定的关键词和search_type=title）
2. 按照文档创建人名称搜索文档  → manage.search_file（传入用户指定的关键词和search_type=owner）
```

> 📖 更多文件管理工作流示例请参考：`references/manage_references.md` - 典型工作流示例

## 注意事项

- **管理空间**：使用 `space_list` 获取空间列表，使用 `create_space` 创建新空间，使用 `query_space_node` 浏览空间内的节点树
- **默认使用 smartcanvas**：除非用户明确指定其他格式，否则**新增文档**时优先使用 `create_smartcanvas_by_markdown`；**编辑已有文档**时使用 `smartcanvas.*` 系列工具
- **创建文档时支持 `parent_id`**：所有 `create_*_by_markdown` 和 `create_flowchart_by_mermaid` 工具均支持 `parent_id` 参数，可将文档直接创建到指定目录；不填则在根目录创建
- **删除节点**：`delete_space_node` 默认仅删除当前节点（`remove_type=current`），使用 `all` 时会递归删除所有子节点，需谨慎
- Markdown 内容使用 UTF-8 格式，特殊字符无需转义
- **创建幻灯片**：使用 `create_slide` 工具，传入 `description`（用户要求）和可选的 `reference_context`（参考资料），AI 自动生成内容；该接口为**异步接口**，返回 `session_id` 后需每隔 10 秒调用 `slide_progress` 轮询进度，最长等待 15 分钟；⚠️ **每次轮询后必须立即向用户输出当前状态**（如：「正在生成中，第N次轮询，请稍候...」），严禁静默等待，状态为 `completed` 时从响应中获取 `file_url`
- 分页查询每页返回 20-40 条记录，使用 `has_next` 判断是否有更多
- `node_id` 同时也是文档的 `file_id`
- `create_flowchart_by_mermaid` 的 mermaid 内容必须全部使用英文
- **文档元素操作**：`Text`、`Heading`、`Task`、`Image` 必须挂载在 `Page` 下，`parent_id` 必须为 Page 类型元素 ID；操作前先调用 `smartcanvas.get_top_level_pages` 获取页面结构
- **文档分页查询**：`smartcanvas.get_page_info` 使用 `cursor` 分页，`is_over=true` 表示已获取全部内容
- **文档删除注意**：删除 Page 元素时，其下所有子元素也会被一并删除
- **智能表格操作**：所有 smartsheet.* 工具都需要 `file_id` 和 `sheet_id`，操作前先调用 `smartsheet.list_tables` 获取 sheet_id
- **字段类型不可更新**：`update_fields` 时 field_type 不能修改，但必须传入原值
- **记录字段值格式**：不同字段类型的值格式不同，详见 `references/smartsheet_references.md` - 字段值格式参考

## 问题定位指南

### 常见错误码及解决方案

| 错误码 | 错误类型 | 解决方案 |
|--------|----------|----------|
| **400006** | **Token 鉴权失败** | 🔑 **检查 Token 配置**：确认 Header 的 key **必须**使用 `Authorization`；同时确认 Token 值正确，可访问 [https://docs.qq.com/scenario/open-claw.html](https://docs.qq.com/scenario/open-claw.html) 重新获取 |
| **400007** | **VIP权限不足** | ⭐ **立即升级VIP**：访问 [https://docs.qq.com/vip?immediate_buy=1?part_aid=persnlspace_mcp](https://docs.qq.com/vip?immediate_buy=1?part_aid=persnlspace_mcp) 购买VIP服务 |
| **-32601** | **请求接口错误** | 🔍 **检查请求工具** 确认调用的工具是否在工具列表中存在 |
| **-32603** | **请求参数错误** | 🔍 **检查请求参数**：确认请求参数是否正确，例如`file_id`、`content` 等 |
| **11607** | **请求参数错误** | 🔍 **检查请求参数**：确认请求参数是否正确，例如`file_id`、`content` 等 |

### 问题排查步骤

1. **检查错误信息**：查看错误信息，确定错误类型，例如环境变量是否配置正确、网络问题、业务参数问题
2. **检查请求参数**：确认请求参数是否正确，例如`file_id`、`content` 等
3. **阅读参考文档**：`references/` 目录下的参考文档中包含所有工具的参数说明，可帮助快速定位问题
4. **获取工具列表**：使用 `mcporter list tencent-docs` 获取所有工具列表，确认工具是否可用，检查有的参数是否正确