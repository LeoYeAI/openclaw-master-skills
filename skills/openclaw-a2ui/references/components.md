# A2UI 组件参考（官方 Standard Catalog + OpenClaw 扩展）

基于 A2UI v0.9 官方规范：https://a2ui.org/reference/components/

---

## 布局组件（Standard Catalog）

### Column
垂直排列子元素。

**v0.9（推荐）：**
```json
{"id":"col1","component":"Column","children":["child1","child2"],"gap":8,"align":"stretch","justify":"start"}
```

**v0.8：**
```json
{"id":"col1","component":{"Column":{"children":{"explicitList":["child1","child2"]},"alignment":"stretch","distribution":"start"}}}
```

属性：
- `children`: 子组件 ID 数组（v0.9）或 `{explicitList:[...]}` / `{template:{...}}`（v0.8）
- `justify`: `start` / `end` / `center` / `spaceBetween` / `spaceAround`
- `align`: `start` / `center` / `end` / `stretch`
- `gap`: 间距（px，OpenClaw 扩展）

动态列表（v0.9）：
```json
{"id":"list_col","component":"Column","children":{"componentId":"item_template","path":"/items"}}
```

动态列表（v0.8）：
```json
{"id":"list_col","component":{"Column":{"children":{"template":{"dataBinding":"/items","componentId":"item_template"}}}}}
```

---

### Row
水平排列子元素。

**v0.9：**
```json
{"id":"row1","component":"Row","children":["c1","c2"],"justify":"spaceBetween","align":"center","gap":12}
```

**v0.8：**
```json
{"id":"row1","component":{"Row":{"children":{"explicitList":["c1","c2"]},"distribution":"spaceBetween","alignment":"center"}}}
```

---

### List
可滚动列表，支持静态和动态子元素。

**v0.9：**
```json
{"id":"msg_list","component":"List","children":{"componentId":"msg_item","path":"/messages"},"direction":"vertical"}
```

**v0.8：**
```json
{"id":"msg_list","component":{"List":{"children":{"template":{"dataBinding":"/messages","componentId":"msg_item"}},"direction":"vertical"}}}
```

---

## 展示组件（Standard Catalog）

### Text
显示文本，支持样式提示。

**v0.9：**
```json
{"id":"t1","component":"Text","text":"Hello World","variant":"h1"}
```
数据绑定：
```json
{"id":"t1","component":"Text","text":{"path":"/title"},"variant":"body"}
```

**v0.8：**
```json
{"id":"t1","component":{"Text":{"text":{"literalString":"Hello World"},"usageHint":"h1"}}}
```

`variant` / `usageHint` 选项：`h1` `h2` `h3` `h4` `h5` `caption` `body`

---

### Image
显示图片。

**v0.9：**
```json
{"id":"img1","component":"Image","url":"https://example.com/photo.jpg","fit":"cover","variant":"hero"}
```
数据绑定：
```json
{"id":"img1","component":"Image","url":{"path":"/imageUrl"},"fit":"cover"}
```

**v0.8：**
```json
{"id":"img1","component":{"Image":{"url":{"literalString":"https://example.com/photo.jpg"},"fit":"cover","usageHint":"hero"}}}
```

> ⚠️ 官方属性是 `url`，不是 `src`。`fit` 选项：`cover` / `contain` / `fill`

---

### Icon
显示内置图标（Material Icons）。

**v0.9：**
```json
{"id":"ico1","component":"Icon","name":"check"}
```
数据绑定：
```json
{"id":"ico1","component":"Icon","name":{"path":"/iconName"}}
```

**v0.8：**
```json
{"id":"ico1","component":{"Icon":{"name":{"literalString":"check"}}}}
```

---

### Divider
分隔线。

**v0.9：**
```json
{"id":"div1","component":"Divider","axis":"horizontal"}
```

**v0.8：**
```json
{"id":"div1","component":{"Divider":{"axis":"horizontal"}}}
```

---

## 交互组件（Standard Catalog）

### Button
可点击按钮。

**v0.9：**
```json
{"id":"btn1","component":"Button","child":"btn_text","variant":"primary","action":{"event":{"name":"submit_form"}}}
```

**v0.8：**
```json
{"id":"btn1","component":{"Button":{"child":"btn_text","primary":true,"action":{"name":"submit_form"}}}}
```

> ⚠️ v0.9 action 格式是 `{event: {name: "..."}}`, v0.8 是 `{name: "..."}`

---

### TextField
文本输入框。

**v0.9：**
```json
{"id":"tf1","component":"TextField","label":"Email","value":{"path":"/user/email"},"textFieldType":"shortText"}
```

**v0.8：**
```json
{"id":"tf1","component":{"TextField":{"label":{"literalString":"Email"},"text":{"path":"/user/email"},"textFieldType":"shortText"}}}
```

> ⚠️ v0.9 值字段是 `value`，v0.8 是 `text`

`textFieldType` 选项：`shortText` `longText` `number` `obscured` `date`

---

### CheckBox
布尔切换。

**v0.9：**
```json
{"id":"cb1","component":"CheckBox","label":"同意条款","value":{"path":"/form/agreed"}}
```

**v0.8：**
```json
{"id":"cb1","component":{"CheckBox":{"label":{"literalString":"同意条款"},"value":{"path":"/form/agreed"}}}}
```

---

### Slider
数字范围输入。

**v0.9：**
```json
{"id":"sl1","component":"Slider","value":{"path":"/settings/volume"},"minValue":0,"maxValue":100}
```

---

### DateTimeInput
日期/时间选择器。

**v0.9：**
```json
{"id":"dp1","component":"DateTimeInput","value":{"path":"/booking/date"},"enableDate":true,"enableTime":false}
```

---

### ChoicePicker（v0.9）/ MultipleChoice（v0.8）
单选或多选。

**v0.9：**
```json
{"id":"sel1","component":"ChoicePicker","options":[{"label":"选项A","value":"a"},{"label":"选项B","value":"b"}],"selections":{"path":"/form/choice"},"maxAllowedSelections":1}
```

**v0.8：**
```json
{"id":"sel1","component":{"MultipleChoice":{"options":[{"label":{"literalString":"选项A"},"value":"a"}],"selections":{"path":"/form/choice"},"maxAllowedSelections":1}}}
```

---

## 容器组件（Standard Catalog）

### Card
带阴影/边框的容器。

**v0.9：**
```json
{"id":"card1","component":"Card","child":"card_content"}
```

**v0.8：**
```json
{"id":"card1","component":{"Card":{"child":"card_content"}}}
```

---

### Modal
弹出覆盖层对话框。

**v0.9：**
```json
{"id":"modal1","component":"Modal","entryPointChild":"open_btn","contentChild":"modal_content"}
```

---

### Tabs
标签页组织内容。

**v0.9：**
```json
{"id":"tabs1","component":"Tabs","tabItems":[{"title":"概览","child":"tab_overview"},{"title":"详情","child":"tab_detail"}]}
```

**v0.8：**
```json
{"id":"tabs1","component":{"Tabs":{"tabItems":[{"title":{"literalString":"概览"},"child":"tab_overview"}]}}}
```

---

## OpenClaw 扩展组件（非标准，仅 OpenClaw 渲染器）

> 以下组件不在 A2UI 官方 Standard Catalog，仅在 OpenClaw webchat canvas 中可用。

### Badge
状态徽章。
```json
{"id":"b1","component":"Badge","label":"成功","color":"success"}
```
`color`: `success` `warning` `error` `info` `neutral`

### Chip
小标签。
```json
{"id":"chip1","component":"Chip","label":"Python","icon":"code"}
```

### ProgressBar
进度条。
```json
{"id":"pb1","component":"ProgressBar","value":{"path":"/progress"},"max":100,"color":"primary"}
```

### CodeBlock
代码块，带语法高亮。
```json
{"id":"code1","component":"CodeBlock","code":{"path":"/code"},"language":"python"}
```

### Video
视频播放器。
```json
{"id":"vid1","component":"Video","src":"https://example.com/video.mp4","poster":"https://example.com/thumb.jpg","autoplay":false,"controls":true}
```
YouTube 支持：`src` 传入 `https://www.youtube.com/embed/<id>` 形式。

### Spacer
空白间距。
```json
{"id":"sp1","component":"Spacer","height":8}
```

---

## 通用属性（所有组件）

- `id`（必填）：组件唯一标识符
- `weight`：弹性增长值，用于 Row/Column 内等比分配宽度
- `accessibility`：无障碍属性 `{label: "...", role: "..."}`

---

## 数据绑定

**字面量（v0.9）：** 直接写值 `"Hello"` 或 `42`
**字面量（v0.8）：** `{"literalString":"Hello"}` / `{"literalNumber":42}` / `{"literalBoolean":true}`
**动态绑定（两版相同）：** `{"path": "/user/name"}`（JSON Pointer 格式）

`updateDataModel`（v0.9）示例：
```json
{"version":"v0.9","updateDataModel":{"surfaceId":"my_surface","path":"/","value":{"title":"欢迎","items":[{"name":"项目A"},{"name":"项目B"}]}}}
```
