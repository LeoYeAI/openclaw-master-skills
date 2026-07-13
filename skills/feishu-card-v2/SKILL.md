---
name: feishu-card
description: >
  发送飞书互动卡片（Card JSON 2.0）。当需要让飞书用户填写表单、做选择、确认操作、或查看
  结构化数据时，发送交互卡片代替纯文字问答。需要 feishu-cards 插件工具：
  feishu_send_card / feishu_send_form / feishu_update_card。
metadata:
  {
    "openclaw": {
      "requires": { "tools": ["feishu_send_card", "feishu_send_form", "feishu_update_card"] },
      "install": [
        {
          "id": "npm",
          "kind": "plugin",
          "package": "@openclaw/feishu-cards",
          "label": "Install feishu-cards plugin (npm)"
        }
      ]
    }
  }
---

## 触发场景

**发卡片** 而非纯文字的情况：
- 需要用户做选择（按钮/下拉/人员选择等）
- 需要用户填写表单（输入框 + 提交按钮）
- 需要展示结构化数据（表格、图表、多列布局）
- 需要确认高风险操作（确认/取消双按钮）
- 需要提供快速操作入口（按钮组）

**纯文字**：简单回复、解释说明、无需交互时，无需发卡片。

---

## 工具说明

| 工具 | 用途 | 主要参数 |
|------|------|---------|
| `feishu_send_card` | 发送卡片消息 | `chat_id` / `user_id`，`card`（JSON字符串） |
| `feishu_send_form` | 发送含表单容器的卡片 | 同上，card 内须含 `form` 组件 |
| `feishu_update_card` | 更新已发卡片内容 | `token`（回调中获取），`card`（新JSON） |

---

## 卡片顶层结构

```json
{
  "schema": "2.0",
  "config": { ... },
  "card_link": { "url": "..." },
  "header": { ... },
  "body": { "elements": [ ... ] }
}
```

### config 字段速查

| 字段 | 默认值 | 说明 |
|------|--------|------|
| `streaming_mode` | false | 流式更新模式 |
| `enable_forward` | true | 是否可转发 |
| `update_multi` | true | 共享卡片（JSON 2.0 仅支持 true） |
| `width_mode` | default(600px) | `compact`(400px) / `fill`(撑满) |
| `enable_forward_interaction` | false | 转发后是否仍可交互 |
| `summary.content` | - | 自定义聊天栏预览文案 |

### header 字段速查

| 字段 | 说明 | 枚举/格式 |
|------|------|---------|
| `title.tag` | 标题文本类型 | `plain_text` / `lark_md` |
| `title.content` | 主标题内容 | 字符串，最多4行 |
| `subtitle.content` | 副标题内容 | 字符串，最多1行 |
| `template` | 标题栏颜色 | `blue` `wathet` `turquoise` `green` `yellow` `orange` `red` `carmine` `violet` `purple` `indigo` `grey` `default` |
| `icon.tag` | 图标类型 | `standard_icon` / `custom_icon` |
| `icon.token` | 图标库token | 如 `chat_outlined` |
| `text_tag_list[].color` | 后缀标签颜色 | `neutral` `blue` `turquoise` `lime` `orange` `violet` `indigo` `wathet` `green` `yellow` `red` `purple` `carmine` |
| `padding` | 标题内边距 | 默认 `12px` |

### body 字段速查

| 字段 | 默认值 | 说明 |
|------|--------|------|
| `direction` | `vertical` | `vertical` / `horizontal` |
| `padding` | - | 如 `12px 12px` |
| `horizontal_spacing` | - | `small`(4px) `medium`(8px) `large`(12px) `extra_large`(16px) 或 `Npx` |
| `horizontal_align` | `left` | `left` / `center` / `right` |
| `vertical_spacing` | - | 同 horizontal_spacing |
| `vertical_align` | `top` | `top` / `center` / `bottom` |
| `elements` | [] | 组件数组 |

---

## 组件速查

### 容器组件

#### column_set（分栏）

tag: `column_set`，不可内嵌 `form` 和 `table`

```json
{
  "tag": "column_set",
  "flex_mode": "none",
  "horizontal_spacing": "8px",
  "background_style": "default",
  "columns": [
    {
      "tag": "column",
      "width": "weighted",
      "weight": 1,
      "vertical_align": "top",
      "elements": []
    }
  ]
}
```

关键枚举：
- `flex_mode`: `none` / `stretch` / `flow` / `bisect` / `trisect`
- `column.width`: `auto` / `weighted` / `Npx`([16,600]px)
- `background_style`: `default` 或颜色枚举值


#### form（表单容器）

tag: `form`，只可放在卡片根节点，不可嵌套表格/表单

```json
{
  "tag": "form",
  "name": "form_1",
  "elements": [
    { "tag": "input", "name": "reason", "required": true },
    {
      "tag": "button",
      "text": { "tag": "plain_text", "content": "提交" },
      "type": "primary_filled",
      "form_action_type": "submit",
      "name": "btn_submit"
    }
  ]
}
```

- 表单内交互组件必须有 `name` 字段（唯一标识）
- 按钮 `form_action_type`: `submit`（提交）/ `reset`（重置）


#### interactive_container（交互容器）

tag: `interactive_container`，不可内嵌 `form` 和 `table`

```json
{
  "tag": "interactive_container",
  "width": "fill",
  "height": "auto",
  "has_border": true,
  "border_color": "grey",
  "corner_radius": "8px",
  "background_style": "default",
  "behaviors": [{ "type": "callback", "value": { "key": "val" } }],
  "elements": []
}
```

关键字段：
- `background_style`: `default` / `laser` / 颜色枚举
- `behaviors.type`: `callback` / `open_url`


#### collapsible_panel（折叠面板）

tag: `collapsible_panel`，不可内嵌 `form`，仅支持 JSON 代码（不支持搭建工具）

```json
{
  "tag": "collapsible_panel",
  "expanded": false,
  "header": {
    "title": { "tag": "plain_text", "content": "面板标题" },
    "icon": { "tag": "standard_icon", "token": "down-small-ccm_outlined", "size": "16px 16px" },
    "icon_position": "right",
    "icon_expanded_angle": -180
  },
  "border": { "color": "grey", "corner_radius": "5px" },
  "elements": []
}
```

- `icon_position`: `left` / `right` / `follow_text`
- `icon_expanded_angle`: `-180` / `-90` / `90` / `180`

---

### 内容组件

#### title（标题组件）

位于 `header` 字段，非 body elements，每卡只能有一个。见上方 header 速查。


#### div（普通文本）

tag: `div`

```json
{
  "tag": "div",
  "text": {
    "tag": "plain_text",
    "content": "文本内容",
    "text_size": "normal",
    "text_color": "default",
    "text_align": "left"
  }
}
```

- `text.tag`: `plain_text` / `lark_md`
- `text_size`: `heading-0`(30px) `heading-1`(24px) `heading-2`(20px) `heading-3`(18px) `heading-4`(16px) `heading`(16px) `normal`(14px) `notation`(12px)
- `text_color`: `default` 或颜色枚举


#### markdown（富文本）

tag: `markdown`

```json
{
  "tag": "markdown",
  "content": "**粗体** *斜体* ~~删除线~~\n- 列表\n`code`\n> 引用",
  "text_align": "left",
  "text_size": "normal"
}
```

支持语法：`**粗体**`、`*斜体*`、`~~删除线~~`、`[链接](url)`、`<at id=open_id></at>`、`<at id=all></at>`、`<font color=red>彩色</font>`、`<text_tag color='blue'>标签</text_tag>`、`# 标题`、有序/无序列表、代码块、表格（Markdown表格语法）、`<hr>`分割线
- `text_size`: 同 div 枚举


#### img（图片）

tag: `img`，img_key 通过上传图片接口获取

```json
{
  "tag": "img",
  "img_key": "img_v3_xxx",
  "scale_type": "crop_center",
  "size": "200px 150px",
  "corner_radius": "8px",
  "preview": true
}
```

- `scale_type`: `crop_center` / `crop_top` / `fit_horizontal`
- `size`: `Wpx Hpx` 或预设值，通栏用 `margin: "0 -12px"`


#### img_combination（多图混排）

tag: `img_combination`

```json
{
  "tag": "img_combination",
  "combination_mode": "bisect",
  "img_list": [
    { "img_key": "img_v3_aaa" },
    { "img_key": "img_v3_bbb" }
  ]
}
```

- `combination_mode`: `double`(双图) / `triple`(三图) / `bisect`(六宫格) / `trisect`(九宫格)


#### person（人员）

tag: `person`

```json
{
  "tag": "person",
  "user_id": "ou_xxx",
  "size": "medium",
  "show_avatar": true,
  "show_name": true,
  "style": "normal"
}
```

- `size`: `extra_small` / `small` / `medium` / `large`
- `style`: `normal` / `capsule`


#### person_list（人员列表）

tag: `person_list`

```json
{
  "tag": "person_list",
  "persons": [{ "id": "ou_xxx" }, { "id": "ou_yyy" }],
  "show_avatar": true,
  "show_name": true,
  "size": "medium"
}
```


#### chart（图表）

tag: `chart`，基于 VChart 定义

```json
{
  "tag": "chart",
  "aspect_ratio": "16:9",
  "color_theme": "brand",
  "chart_spec": {
    "type": "bar",
    "data": [{ "id": "data", "values": [{ "x": "A", "y": 10 }] }],
    "xField": "x",
    "yField": "y"
  }
}
```

- `color_theme`: `brand` / `rainbow` / `complementary` / `diverging` / `ordinal`


#### table（表格）

tag: `table`，只可放在卡片根节点，不支持内嵌其它组件

```json
{
  "tag": "table",
  "page_size": 5,
  "row_height": "low",
  "columns": [
    { "name": "col1", "display_name": "名称", "data_type": "text", "width": "auto" },
    { "name": "col2", "display_name": "数量", "data_type": "number" }
  ],
  "rows": [
    { "col1": "项目A", "col2": 100 }
  ]
}
```

- `data_type`: `text` / `lark_md` / `number` / `options` / `persons` / `date`
- `row_height`: `low` / `middle` / `high` / `auto`
- `number.format`: `{ symbol, precision, separator }`


#### audio（音频）

tag: `audio`，仅支持 JSON 代码，需 `enable_forward: false`，仅飞书 V7.49+

```json
{ "tag": "audio", "file_key": "file_v3_xxx", "show_time": true }
```

#### hr（分割线）

tag: `hr`

```json
{ "tag": "hr" }
```

---

### 交互组件

#### input（输入框）

tag: `input`

```json
{
  "tag": "input",
  "name": "reason",
  "placeholder": { "tag": "plain_text", "content": "请输入" },
  "required": false,
  "max_length": 200,
  "input_type": "text",
  "width": "fill"
}
```

- `input_type`: `text` / `multiline_text` / `password` / `number` / `telephone` / `email`
- `width`: `default` / `fill` / `[100,∞)px`
- 表单外使用时，需配 `behaviors` 触发回调


#### button（按钮）

tag: `button`

```json
{
  "tag": "button",
  "type": "primary_filled",
  "size": "medium",
  "text": { "tag": "plain_text", "content": "确认" },
  "behaviors": [{ "type": "callback", "value": { "action": "confirm" } }]
}
```

- `type`: `default` `primary` `danger` `text` `primary_text` `danger_text` `primary_filled` `danger_filled` `laser`
- `size`: `tiny` / `small` / `medium` / `large`
- `width`: `default` / `fill` / `Npx`
- `behaviors.type`: `callback` / `open_url`


#### overflow（折叠按钮组）

tag: `overflow`

```json
{
  "tag": "overflow",
  "options": [
    { "text": { "tag": "plain_text", "content": "选项1" }, "value": "opt1" },
    { "text": { "tag": "plain_text", "content": "跳转" }, "multi_url": { "url": "https://..." } }
  ]
}
```


#### select_static（下拉单选）

tag: `select_static`

```json
{
  "tag": "select_static",
  "name": "priority",
  "placeholder": { "tag": "plain_text", "content": "请选择" },
  "options": [
    { "text": { "tag": "plain_text", "content": "高" }, "value": "high" },
    { "text": { "tag": "plain_text", "content": "低" }, "value": "low" }
  ],
  "behaviors": [{ "type": "callback", "value": { "k": "v" } }]
}
```

- `type`: `default` / `text`（边框样式）


#### multi_select_static（下拉多选）

tag: `multi_select_static`，**必须**在 `form` 容器内

```json
{
  "tag": "multi_select_static",
  "name": "tags",
  "placeholder": { "tag": "plain_text", "content": "请选择" },
  "options": [
    { "text": { "tag": "plain_text", "content": "标签A" }, "value": "a" }
  ]
}
```


#### select_person（人员单选）

tag: `select_person`

```json
{
  "tag": "select_person",
  "name": "assignee",
  "placeholder": { "tag": "plain_text", "content": "选择负责人" },
  "options": [{ "value": "ou_xxx" }],
  "behaviors": [{ "type": "callback", "value": {} }]
}
```


#### multi_select_person（人员多选）

tag: `multi_select_person`，**必须**在 `form` 容器内

```json
{
  "tag": "multi_select_person",
  "name": "reviewers",
  "placeholder": { "tag": "plain_text", "content": "选择审核人" },
  "options": [{ "value": "ou_xxx" }, { "value": "ou_yyy" }]
}
```


#### date_picker（日期选择器）

tag: `date_picker`

```json
{
  "tag": "date_picker",
  "name": "due_date",
  "initial_date": "2025-01-01",
  "placeholder": { "tag": "plain_text", "content": "请选择日期" }
}
```


#### picker_time（时间选择器）

tag: `picker_time`

```json
{
  "tag": "picker_time",
  "name": "meeting_time",
  "initial_time": "09:00",
  "placeholder": { "tag": "plain_text", "content": "请选择时间" }
}
```


#### picker_datetime（日期时间选择器）

tag: `picker_datetime`

```json
{
  "tag": "picker_datetime",
  "name": "event_datetime",
  "initial_datetime": "2025-01-01 09:00",
  "placeholder": { "tag": "plain_text", "content": "请选择" }
}
```


#### select_img（多图选择）

tag: `select_img`，仅支持 JSON 代码；不在 form 内时仅单选点击即提交

```json
{
  "tag": "select_img", "name": "choice", "multi_select": false,
  "layout": "bisect", "aspect_ratio": "16:9",
  "options": [{ "img_key": "img_v3_aaa", "value": "pic1" }],
  "behaviors": [{ "type": "callback", "value": {} }]
}
```

- `layout`: `bisect` / `trisect` / `compact`


#### checker（勾选器）

tag: `checker`，仅支持 JSON 代码

```json
{
  "tag": "checker", "name": "task_done", "checked": false,
  "text": { "tag": "plain_text", "content": "任务已完成" },
  "behaviors": [{ "type": "callback", "value": { "task_id": "123" } }]
}
```

---

## 常用模板

### 1. 确认操作（双按钮）

```json
{
  "schema": "2.0",
  "header": { "title": { "tag": "plain_text", "content": "确认操作" }, "template": "orange" },
  "body": {
    "elements": [
      { "tag": "markdown", "content": "确定要执行此操作吗？此操作**不可撤销**。" },
      {
        "tag": "column_set", "horizontal_spacing": "8px",
        "columns": [
          { "tag": "column", "width": "auto", "elements": [{
            "tag": "button", "type": "primary_filled",
            "text": { "tag": "plain_text", "content": "确认" },
            "behaviors": [{ "type": "callback", "value": { "action": "confirm" } }]
          }]},
          { "tag": "column", "width": "auto", "elements": [{
            "tag": "button", "type": "default",
            "text": { "tag": "plain_text", "content": "取消" },
            "behaviors": [{ "type": "callback", "value": { "action": "cancel" } }]
          }]}
        ]
      }
    ]
  }
}
```

---

### 2. 快捷选择（按钮组）

```json
{
  "schema": "2.0",
  "header": { "title": { "tag": "plain_text", "content": "请选择优先级" }, "template": "blue" },
  "body": {
    "elements": [
      { "tag": "markdown", "content": "请为该任务设置优先级：" },
      {
        "tag": "column_set", "horizontal_spacing": "8px",
        "columns": [
          { "tag": "column", "width": "auto", "elements": [{
            "tag": "button", "type": "danger_filled",
            "text": { "tag": "plain_text", "content": "🔴 紧急" },
            "behaviors": [{ "type": "callback", "value": { "priority": "urgent" } }]
          }]},
          { "tag": "column", "width": "auto", "elements": [{
            "tag": "button", "type": "primary",
            "text": { "tag": "plain_text", "content": "🟡 普通" },
            "behaviors": [{ "type": "callback", "value": { "priority": "normal" } }]
          }]},
          { "tag": "column", "width": "auto", "elements": [{
            "tag": "button", "type": "default",
            "text": { "tag": "plain_text", "content": "🟢 低" },
            "behaviors": [{ "type": "callback", "value": { "priority": "low" } }]
          }]}
        ]
      }
    ]
  }
}
```

---

### 3. 数据展示（table + 操作按钮）

```json
{
  "schema": "2.0",
  "header": { "title": { "tag": "plain_text", "content": "待处理工单" }, "template": "blue" },
  "body": {
    "elements": [
      {
        "tag": "table", "page_size": 5, "row_height": "low",
        "columns": [
          { "name": "id", "display_name": "工单号", "data_type": "text", "width": "80px" },
          { "name": "title", "display_name": "标题", "data_type": "text" },
          { "name": "status", "display_name": "状态", "data_type": "options" },
          { "name": "assignee", "display_name": "负责人", "data_type": "persons" }
        ],
        "rows": [
          { "id": "T001", "title": "登录异常", "status": [{ "name": "处理中", "color": "orange" }], "assignee": [{ "id": "ou_xxx" }] }
        ]
      },
      { "tag": "hr" },
      {
        "tag": "column_set", "horizontal_align": "right",
        "columns": [{ "tag": "column", "width": "auto", "elements": [{
          "tag": "button", "type": "primary_filled",
          "text": { "tag": "plain_text", "content": "查看全部" },
          "behaviors": [{ "type": "open_url", "default_url": "https://your-app.com/tickets" }]
        }]}]
      }
    ]
  }
}
```
