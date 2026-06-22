# 文档（SmartCanvas）工具完整参考文档

腾讯文档文档（SmartCanvas）提供了一套完整的文档元素操作 API，支持对页面、文本、标题、待办事项等元素进行增删改查操作。

---

## 目录

- [概念说明](#概念说明)
- [元素操作](#元素操作)
  - [smartcanvas.create_smartcanvas_element - 新增元素](#smartcanvascreatesmartcanvaselement)
  - [smartcanvas.get_element_info - 查询元素信息](#smartcanvasgetelement_info)
  - [smartcanvas.get_page_info - 查询页面内容](#smartcanvasgetpageinfo)
  - [smartcanvas.get_top_level_pages - 查询顶层页面](#smartcanvasgettoplevelpages)
  - [smartcanvas.update_element - 修改元素](#smartcanvasupdateelement)
  - [smartcanvas.delete_element - 删除元素](#smartcanvasdeleteelement)
- [追加内容](#追加内容)
  - [smartcanvas.append_insert_smartcanvas_by_markdown - 追加 Markdown 内容](#smartcanvasappendinsertsmartcanvasbymarkdown-追加)
- [枚举值参考](#枚举值参考)
- [元素类型详细说明](#元素类型详细说明)
- [典型工作流示例](#典型工作流示例)

---

## 概念说明

| 概念 | 说明 |
|------|------|
| `file_id` | 文档的唯一标识符，每个文档有唯一的 file_id |
| `element_id` | 元素 ID，文档中每个元素（页面、文本、标题、任务）都有唯一 ID |
| `page_id` | 页面元素 ID，Page 是文档的基本容器单元 |
| `parent_id` | 父元素 ID，用于确定元素的层级关系 |

**元素层级关系**：

```
file_id（文档）
└── Page（页面）
    ├── Heading（标题，LEVEL_1 ~ LEVEL_6）
    ├── Text（文本）
    └── Task（待办事项）
```

> ⚠️ **重要约束**：
> - `Text`、`Task`、`Heading` 必须挂载在 `Page` 类型的父节点下
> - `Page` 可以不指定父节点（挂载到根节点）
> - 父节点不支持为 `Heading` 类型

---

## 元素操作

### smartcanvas.create_smartcanvas_element

**功能**：在文档中新增元素，支持同时添加页面、文本、标题、待办事项等多种类型元素。

**使用场景**：
- 在文档中追加新页面
- 在已有页面中添加文本、标题、待办事项
- 在指定元素后面插入新内容

**请求参数**：

| 参数 | 类型 | 必填 | 说明                                                                     |
|------|------|------|------------------------------------------------------------------------|
| `file_id` | string | ✅ | 文档的唯一标识符                                                             |
| `parent_id` | string | 条件必填 | 父节点元素 ID。插入 Text/Task/Heading 时必填（父节点必须为 Page 类型）；插入 Page 时可不填（插入到根节点） |
| `after` | string | | 插入到哪个节点之后的元素 ID，不填则作为父节点的最后一个子节点插入                                     |
| `pages` | []Page | | 要添加的页面元素列表                                                             |
| `texts` | []Text | | 要添加的文本元素列表                                                             |
| `tasks` | []Task | | 要添加的待办事项元素列表                                                           |
| `headings` | []Heading | | 要添加的标题元素列表                                                             |
| `image` | []Image | | 要添加的图片元素列表，需先调用 `upload_image` 获取 image_ID                             |

**返回字段**：

| 字段 | 类型 | 说明 |
|------|------|------|
| `element_infos` | array | 创建的元素信息列表，详见 ElementInfo 结构 |
| `error` | string | 错误信息，操作失败时返回 |
| `trace_id` | string | 调用链追踪 ID |

**ElementInfo 结构**：

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | string | 元素唯一标识符 |
| `version` | uint32 | 元素版本号 |
| `type` | string | 元素类型：Page、Text、Heading、Task |
| `element` | string | 元素内容（JSON 格式字符串） |
| `parent_id` | string | 父元素 ID |
| `children` | []string | 子元素 ID 列表 |
| `created_by` | string | 创建者用户 ID |
| `created_at` | uint64 | 创建时间戳（毫秒） |
| `updated_by` | string | 最后更新者用户 ID |
| `updated_at` | uint64 | 最后更新时间戳（毫秒） |

**调用示例（新增页面）**：

```json
{
  "file_id": "your_file_id",
  "pages": [
    {
      "title": "第一章：项目背景"
    }
  ]
}
```

**调用示例（在页面中添加标题和文本）**：

```json
{
  "file_id": "your_file_id",
  "parent_id": "page_element_id",
  "headings": [
    {
      "rich_text": {
        "text": "项目目标",
        "formats": {
          "bold": true
        }
      },
      "level": "LEVEL_1"
    }
  ],
  "texts": [
    {
      "rich_text": {
        "text": "本项目旨在提升用户体验，优化核心流程。"
      }
    }
  ]
}
```

**调用示例（添加待办事项）**：

```json
{
  "file_id": "your_file_id",
  "parent_id": "page_element_id",
  "tasks": [
    {
      "rich_text": {
        "text": "完成需求评审"
      },
      "reminder": {
        "due_time": 1720072890000,
        "reminder_time": 30
      }
    },
    {
      "rich_text": {
        "text": "提交设计稿"
      }
    }
  ]
}
```

**调用示例（添加图片）**：

> ⚠️ 需先调用 `upload_image` 上传图片获取 `image_id`，再传入此处。

```json
{
  "file_id": "your_file_id",
  "parent_id": "page_element_id",
  "image": [
    {
      "image_id": "从 upload_image 返回的 image_id",
      "width": 800,
      "height": 600
    }
  ]
}
```

---

### smartcanvas.get_element_info

**功能**：批量查询指定元素的详细信息，支持同时查询多个元素。

**使用场景**：
- 查询特定元素的内容和属性
- 获取元素的父子关系
- 验证元素是否存在及其当前状态

**请求参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `file_id` | string | ✅ | 文档的唯一标识符 |
| `element_ids` | []string | ✅ | 查询元素 ID 列表，支持批量查询多个元素 |

**返回字段**：

| 字段 | 类型 | 说明 |
|------|------|------|
| `element_infos` | array | 查询到的元素信息列表，详见 ElementInfo 结构 |
| `error` | string | 错误信息 |
| `trace_id` | string | 调用链追踪 ID |

**调用示例**：

```json
{
  "file_id": "your_file_id",
  "element_ids": ["element_id_001", "element_id_002"]
}
```

**返回示例**：

```json
{
  "element_infos": [
    {
      "id": "element_id_001",
      "version": 3,
      "type": "Page",
      "element": "{\"title\": \"第一章：项目背景\"}",
      "parent_id": "",
      "children": ["element_id_003", "element_id_004"],
      "created_by": "user_001",
      "created_at": 1720000000000,
      "updated_by": "user_001",
      "updated_at": 1720086400000
    }
  ],
  "error": "",
  "trace_id": "trace_xyz"
}
```

---

### smartcanvas.get_page_info

**功能**：查询指定页面内的所有元素，支持分页获取。

**使用场景**：
- 读取某个页面下的所有内容（标题、文本、待办事项）
- 分页获取内容较多的页面
- 遍历文档内容进行分析

**请求参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `file_id` | string | ✅ | 文档的唯一标识符 |
| `page_id` | string | ✅ | 要查询的页面元素 ID |
| `cursor` | []CursorItem | | 分页游标，首次查询不传，后续查询使用上次响应返回的 cursor |

**CursorItem 结构**：

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | string | 游标 ID |
| `index` | uint32 | 游标索引位置 |

**返回字段**：

| 字段 | 类型 | 说明 |
|------|------|------|
| `element_infos` | array | 页面内的元素信息列表 |
| `cursor` | []CursorItem | 下次分页的 cursor 信息 |
| `is_over` | bool | 是否已查询完所有内容，为 true 表示分页结束 |
| `error` | string | 错误信息 |
| `trace_id` | string | 调用链追踪 ID |

**调用示例（首次查询）**：

```json
{
  "file_id": "your_file_id",
  "page_id": "page_element_id"
}
```

**调用示例（分页继续查询）**：

```json
{
  "file_id": "your_file_id",
  "page_id": "page_element_id",
  "cursor": [
    { "id": "cursor_id_001", "index": 20 }
  ]
}
```

---

### smartcanvas.get_top_level_pages

**功能**：查询文档的所有顶层页面列表，返回根节点下的直接子页面。

**使用场景**：
- 获取文档的目录结构（顶层页面列表）
- 遍历文档所有页面
- 在操作前先了解文档的页面组织结构

**请求参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `file_id` | string | ✅ | 文档的唯一标识符 |

**返回字段**：

| 字段 | 类型 | 说明 |
|------|------|------|
| `top_level_pages` | array | 顶层页面列表，包含所有顶级页面的基本信息 |
| `error` | string | 错误信息 |
| `trace_id` | string | 调用链追踪 ID |

**调用示例**：

```json
{
  "file_id": "your_file_id"
}
```

**返回示例**：

```json
{
  "top_level_pages": [
    {
      "id": "page_id_001",
      "type": "Page",
      "element": "{\"title\": \"第一章：项目背景\"}",
      "children": ["element_id_003", "element_id_004"]
    },
    {
      "id": "page_id_002",
      "type": "Page",
      "element": "{\"title\": \"第二章：技术方案\"}",
      "children": ["element_id_005"]
    }
  ],
  "error": "",
  "trace_id": "trace_xyz"
}
```

---

### smartcanvas.update_element

**功能**：批量修改元素内容，支持同时更新多个元素的文本、格式、标题级别等属性。

**使用场景**：
- 修改页面标题
- 更新文本内容或格式（加粗、颜色等）
- 修改标题级别
- 更新待办事项内容或截止时间

**请求参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `file_id` | string | ✅ | 文档的唯一标识符 |
| `updates` | []UpdateElementRequest | ✅ | 元素更新请求列表，支持批量更新多个元素 |

**UpdateElementRequest 结构**：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `element_id` | string | ✅ | 要更新的元素 ID |
| `page` | Page | | 更新页面元素（修改标题） |
| `text` | Text | | 更新文本元素 |
| `task` | Task | | 更新待办事项元素 |
| `heading` | Heading | | 更新标题元素 |

**返回字段**：

| 字段 | 类型 | 说明 |
|------|------|------|
| `updated_elements` | array | 更新成功的元素信息列表 |
| `error` | string | 错误信息 |
| `trace_id` | string | 调用链追踪 ID |

**调用示例（修改页面标题）**：

```json
{
  "file_id": "your_file_id",
  "updates": [
    {
      "element_id": "page_element_id",
      "page": {
        "title": "第一章：项目背景（已更新）"
      }
    }
  ]
}
```

**调用示例（修改文本内容和格式）**：

```json
{
  "file_id": "your_file_id",
  "updates": [
    {
      "element_id": "text_element_id",
      "text": {
        "rich_text": {
          "text": "这是更新后的文本内容，支持富文本格式。",
          "formats": {
            "bold": true,
            "text_color": "COLOR_BLUE"
          }
        },
        "block_color": "BG_COLOR_LIGHT_BLUE"
      }
    }
  ]
}
```

**调用示例（修改标题级别）**：

```json
{
  "file_id": "your_file_id",
  "updates": [
    {
      "element_id": "heading_element_id",
      "heading": {
        "rich_text": {
          "text": "技术架构设计"
        },
        "level": "LEVEL_2"
      }
    }
  ]
}
```

**调用示例（更新待办事项截止时间）**：

```json
{
  "file_id": "your_file_id",
  "updates": [
    {
      "element_id": "task_element_id",
      "task": {
        "rich_text": {
          "text": "完成代码评审"
        },
        "reminder": {
          "due_time": 1720159290000,
          "reminder_time": 60
        }
      }
    }
  ]
}
```

---

### smartcanvas.delete_element

**功能**：批量删除元素，支持同时删除多个指定元素。

**使用场景**：
- 删除不再需要的页面或内容块
- 清理文档中的冗余内容
- 批量删除多个元素

> ⚠️ **注意**：删除 Page 元素时，其下的所有子元素（Text、Heading、Task）也会被一并删除，请谨慎操作。

**请求参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `file_id` | string | ✅ | 文档的唯一标识符 |
| `element_ids` | []string | ✅ | 需要批量删除的元素 ID 列表 |

**返回字段**：

| 字段 | 类型 | 说明 |
|------|------|------|
| `error` | string | 错误信息，操作失败时返回 |
| `trace_id` | string | 调用链追踪 ID |

**调用示例**：

```json
{
  "file_id": "your_file_id",
  "element_ids": ["element_id_001", "element_id_002"]
}
```

---

## 追加内容

### smartcanvas.append_insert_smartcanvas_by_markdown 追加

**功能**：通过 Markdown 文本向已有文档追加内容，内容追加到文档末尾。

**使用场景**：
- 快速向文档末尾追加大段 Markdown 内容
- 批量导入 Markdown 格式的文档内容
- 在已有文档基础上继续补充内容

**请求参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `file_id` | string | ✅ | 文档的唯一标识符 |
| `markdown` | string | ✅ | UTF-8 格式的 Markdown 文本，特殊字符不需要转义 |

**返回字段**：

| 字段 | 类型 | 说明 |
|------|------|------|
| `error` | string | 错误信息，操作失败时返回 |
| `trace_id` | string | 调用链追踪 ID |

**调用示例**：

```json
{
  "file_id": "your_file_id",
  "markdown": "## 新增章节\n\n这是通过 Markdown 追加的内容。\n\n- 支持列表\n- 支持**加粗**\n- 支持`代码`"
}
```

---

## 枚举值参考

### 标题级别（HeadingLevel）

| 枚举值 | 说明 |
|--------|------|
| `LEVEL_1` | 一级标题（最大） |
| `LEVEL_2` | 二级标题 |
| `LEVEL_3` | 三级标题 |
| `LEVEL_4` | 四级标题 |
| `LEVEL_5` | 五级标题 |
| `LEVEL_6` | 六级标题（最小） |

### 文本颜色（TextColor）

| 枚举值 | 颜色 |
|--------|------|
| `COLOR_GREY` | 灰色 |
| `COLOR_BLUE` | 蓝色 |
| `COLOR_SKY_BLUE` | 天蓝色 |
| `COLOR_GREEN` | 绿色 |
| `COLOR_YELLOW` | 黄色 |
| `COLOR_ORANGE` | 橙色 |
| `COLOR_RED` | 红色 |
| `COLOR_ROSE_RED` | 玫瑰红 |
| `COLOR_PURPLE` | 紫色 |

### 背景颜色（BackgroundColor）

| 枚举值 | 颜色 |
|--------|------|
| `BG_COLOR_GREY` | 灰色 |
| `BG_COLOR_LIGHT_GREY` | 浅灰色 |
| `BG_COLOR_DARK` | 深色 |
| `BG_COLOR_LIGHT_BLUE` | 浅蓝色 |
| `BG_COLOR_BLUE` | 蓝色 |
| `BG_COLOR_LIGHT_SKY_BLUE` | 浅天蓝色 |
| `BG_COLOR_SKY_BLUE` | 天蓝色 |
| `BG_COLOR_LIGHT_GREEN` | 浅绿色 |
| `BG_COLOR_GREEN` | 绿色 |
| `BG_COLOR_LIGHT_YELLOW` | 浅黄色 |
| `BG_COLOR_YELLOW` | 黄色 |
| `BG_COLOR_LIGHT_ORANGE` | 浅橙色 |
| `BG_COLOR_ORANGE` | 橙色 |
| `BG_COLOR_LIGHT_RED` | 浅红色 |
| `BG_COLOR_RED` | 红色 |
| `BG_COLOR_LIGHT_ROSE_RED` | 浅玫瑰红 |
| `BG_COLOR_ROSE_RED` | 玫瑰红 |
| `BG_COLOR_LIGHT_PURPLE` | 浅紫色 |
| `BG_COLOR_PURPLE` | 紫色 |

---

## 元素类型详细说明

### Page（页面）

页面是文档的基本容器单元，所有内容元素（Text、Heading、Task）都必须挂载在 Page 下。

```json
{
  "title": "页面标题（仅支持纯文本）"
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `title` | string | | 页面标题，仅支持纯文本，不支持富文本格式 |

---

### Text（文本）

普通文本块，支持富文本格式和背景颜色。

```json
{
  "rich_text": {
    "text": "文本内容",
    "formats": {
      "bold": false,
      "italic": false,
      "under_line": false,
      "strike": false,
      "text_color": "COLOR_BLUE",
      "background_color": "BG_COLOR_LIGHT_YELLOW",
      "text_link": {
        "link_url": "https://example.com"
      }
    }
  },
  "block_color": "BG_COLOR_LIGHT_GREY"
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `rich_text` | RichText | ✅ | 富文本内容 |
| `block_color` | BackgroundColor | | 文本块背景颜色 |

---

### Heading（标题）

标题块，支持 1-6 级标题，支持富文本格式和背景颜色。

```json
{
  "rich_text": {
    "text": "标题内容",
    "formats": {
      "bold": true
    }
  },
  "level": "LEVEL_1",
  "block_color": "BG_COLOR_LIGHT_BLUE"
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `rich_text` | RichText | ✅ | 富文本内容 |
| `level` | HeadingLevel | ✅ | 标题级别，枚举值：LEVEL_1 ~ LEVEL_6 |
| `block_color` | BackgroundColor | | 标题块背景颜色 |

---

### Image（图片）

图片块，需先通过 `upload_image` 工具上传图片获取 `image_id`，再插入到文档中。

```json
{
  "image_id": "从 upload_image 返回的 image_id",
  "width": 800,
  "height": 600
}
```

| 字段         | 类型 | 必填 | 说明 |
|------------|------|------|------|
| `image_id` | string | ✅ | 图片 ID，通过 `upload_image` 工具上传图片后获取，有效期为一天 |
| `width`    | float | | 图片显示宽度（像素），不填则使用图片原始宽度 |
| `height`   | float | | 图片显示高度（像素），不填则使用图片原始高度 |

> ⚠️ **注意**：`image_id` 有效期为一天，请在获取后及时使用。

---

### Task（待办事项）

待办事项块，支持设置截止时间和提醒。

```json
{
  "rich_text": {
    "text": "待办事项内容"
  },
  "reminder": {
    "due_time": 1720072890000,
    "reminder_time": 30
  }
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `rich_text` | RichText | ✅ | 待办事项文本内容 |
| `reminder` | Reminder | | 提醒设置 |

**Reminder 结构**：

| 字段 | 类型 | 说明 |
|------|------|------|
| `due_time` | uint64 | 任务截止时间，Unix 时间戳（毫秒），例如 `1720072890000` |
| `reminder_time` | int32 | 提前提醒时间间隔（分钟） |

---

### RichText（富文本）

富文本对象，包含文本内容和格式设置。

```json
{
  "text": "文本内容",
  "formats": {
    "bold": true,
    "italic": false,
    "under_line": true,
    "strike": false,
    "text_color": "COLOR_RED",
    "background_color": "BG_COLOR_LIGHT_YELLOW",
    "text_link": {
      "link_url": "https://docs.qq.com"
    }
  }
}
```

**Formats 格式说明**：

| 字段 | 类型 | 说明 |
|------|------|------|
| `bold` | bool | 粗体 |
| `italic` | bool | 斜体 |
| `under_line` | bool | 下划线 |
| `strike` | bool | 删除线 |
| `text_color` | TextColor | 文本颜色，枚举值见上方 |
| `background_color` | BackgroundColor | 背景颜色，枚举值见上方 |
| `text_link` | TextLink | 文本链接，包含 `link_url` 字段 |

---

## 典型工作流示例

### 工作流一：创建结构化文档

```
步骤 1：创建文档
  → create_smartcanvas_by_markdown（创建文档，获取 file_id）

步骤 2：查询顶层页面
  → smartcanvas.get_top_level_pages（获取已有页面的 page_id）

步骤 3：在页面中添加内容
  → smartcanvas.create_smartcanvas_element（传入 parent_id=page_id，添加标题和文本）

步骤 4：继续追加内容
  → smartcanvas.create_smartcanvas_element（追加更多页面或内容块）
```

### 工作流二：读取文档内容

```
步骤 1：获取顶层页面列表
  → smartcanvas.get_top_level_pages（获取所有顶层页面）

步骤 2：逐页读取内容
  → smartcanvas.get_page_info（传入 page_id，获取页面内所有元素）
  → 若 is_over=false，继续传入 cursor 获取下一页

步骤 3：（可选）查询特定元素详情
  → smartcanvas.get_element_info（传入 element_ids，获取元素详细信息）
```

### 工作流三：更新文档内容

```
步骤 1：获取顶层页面
  → smartcanvas.get_top_level_pages（获取页面列表）

步骤 2：读取页面内容，找到目标元素
  → smartcanvas.get_page_info（获取页面内元素及其 element_id）

步骤 3：更新目标元素
  → smartcanvas.update_element（传入 element_id 和新内容）
```

### 工作流四：追加内容到已有文档

```
步骤 1：获取文档 file_id
  → search_space_file（搜索文档，获取 file_id）

步骤 2：追加 Markdown 内容
  → smartcanvas.append_insert_smartcanvas_by_markdown（传入 file_id 和 markdown 内容）

步骤 3：（可选）精细化追加结构化元素
  → smartcanvas.get_top_level_pages（获取最新页面列表）
  → smartcanvas.create_smartcanvas_element（在指定页面后追加元素）
```

### 工作流五：清理文档内容

```
步骤 1：获取顶层页面
  → smartcanvas.get_top_level_pages

步骤 2：读取页面内容，找到要删除的元素
  → smartcanvas.get_page_info（获取 element_id 列表）

步骤 3：批量删除元素
  → smartcanvas.delete_element（传入 element_ids 数组）
```

---

> 📌 **提示**：
> - 所有操作都需要先获取 `file_id`，可通过 `search_space_file` 搜索文档获取，或在创建文档时从返回结果中获取。
> - 操作元素前，建议先调用 `smartcanvas.get_top_level_pages` 了解文档结构，再调用 `smartcanvas.get_page_info` 获取具体元素 ID。
> - `Text`、`Heading`、`Task` 元素必须挂载在 `Page` 下，创建时 `parent_id` 必须为 Page 类型元素的 ID。
