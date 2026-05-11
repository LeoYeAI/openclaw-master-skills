# A2UI 卡片模板库（v0.9）

基于 A2UI v0.9 规范。每个模板都是完整的 JSONL，可直接修改数据部分使用。
`<SURFACE_ID>` 替换为唯一 ID（如 `reply_1741491234567`）。

> **v0.9 关键规则：**
> - 所有行加 `"version":"v0.9"`
> - `createSurface` 放第一行（替代 v0.8 的 `beginRendering`）
> - 组件格式：`"component":"Text"` + 属性平铺
> - 字符串直接写，不用 `{"literalString":"..."}` 包裹
> - `children` 直接数组 `["id1","id2"]`
> - `Image` 属性用 `url`（不是 `src`）
> - `updateDataModel` 的 `value` 是普通 JSON 对象

---

## text-card

**适用：** 纯文本摘要、结论、说明段落。

```jsonl
{"version":"v0.9","createSurface":{"surfaceId":"<SURFACE_ID>","catalogId":"openclaw/basic/v1"}}
{"version":"v0.9","updateComponents":{"surfaceId":"<SURFACE_ID>","components":[{"id":"root","component":"Card","child":"col"},{"id":"col","component":"Column","children":["title_row","body_text"],"gap":8},{"id":"title_row","component":"Row","children":["icon","title"],"gap":8,"align":"center"},{"id":"icon","component":"Icon","name":"info"},{"id":"title","component":"Text","text":{"path":"/title"},"variant":"h3"},{"id":"body_text","component":"Text","text":{"path":"/body"},"variant":"body"}]}}
{"version":"v0.9","updateDataModel":{"surfaceId":"<SURFACE_ID>","path":"/","value":{"title":"标题","body":"这里是正文内容。"}}}
```

---

## image-card

**适用：** 单图展示，图片说明。

> ⚠️ `Image` 组件的图片 URL 属性是 `url`，不是 `src`。

```jsonl
{"version":"v0.9","createSurface":{"surfaceId":"<SURFACE_ID>","catalogId":"openclaw/basic/v1"}}
{"version":"v0.9","updateComponents":{"surfaceId":"<SURFACE_ID>","components":[{"id":"root","component":"Card","child":"col"},{"id":"col","component":"Column","children":["image","caption_row"],"gap":0},{"id":"image","component":"Image","url":{"path":"/imageUrl"},"fit":"cover","variant":"hero"},{"id":"caption_row","component":"Column","children":["cap_text"],"gap":0},{"id":"cap_text","component":"Text","text":{"path":"/caption"},"variant":"caption"}]}}
{"version":"v0.9","updateDataModel":{"surfaceId":"<SURFACE_ID>","path":"/","value":{"imageUrl":"https://example.com/photo.jpg","caption":"图片说明文字"}}}
```

**多图画廊版：**
```jsonl
{"version":"v0.9","createSurface":{"surfaceId":"<SURFACE_ID>","catalogId":"openclaw/basic/v1"}}
{"version":"v0.9","updateComponents":{"surfaceId":"<SURFACE_ID>","components":[{"id":"root","component":"Card","child":"col"},{"id":"col","component":"Column","children":["title","gallery"],"gap":8},{"id":"title","component":"Text","text":{"path":"/title"},"variant":"h3"},{"id":"gallery","component":"Row","children":{"componentId":"img_item","path":"/images"},"gap":8},{"id":"img_item","component":"Image","url":{"path":"/url"},"fit":"cover"}]}}
{"version":"v0.9","updateDataModel":{"surfaceId":"<SURFACE_ID>","path":"/","value":{"title":"图片集","images":[{"url":"https://example.com/1.jpg"},{"url":"https://example.com/2.jpg"}]}}}
```

---

## video-card

**适用：** 视频播放（使用 OpenClaw Video 扩展组件）。

```jsonl
{"version":"v0.9","createSurface":{"surfaceId":"<SURFACE_ID>","catalogId":"openclaw/basic/v1"}}
{"version":"v0.9","updateComponents":{"surfaceId":"<SURFACE_ID>","components":[{"id":"root","component":"Card","child":"col"},{"id":"col","component":"Column","children":["player","info_col"],"gap":0},{"id":"player","component":"Video","src":{"path":"/videoSrc"},"poster":{"path":"/poster"},"controls":true,"autoplay":false},{"id":"info_col","component":"Column","children":["vid_title","vid_desc"],"gap":4},{"id":"vid_title","component":"Text","text":{"path":"/title"},"variant":"h3"},{"id":"vid_desc","component":"Text","text":{"path":"/desc"},"variant":"caption"}]}}
{"version":"v0.9","updateDataModel":{"surfaceId":"<SURFACE_ID>","path":"/","value":{"videoSrc":"https://example.com/video.mp4","poster":"https://example.com/thumb.jpg","title":"视频标题","desc":"视频描述"}}}
```

**YouTube 版：**
`videoSrc` 传入 `https://www.youtube.com/embed/<video_id>`

---

## list-card

**适用：** 要点列表、功能特性、注意事项。

```jsonl
{"version":"v0.9","createSurface":{"surfaceId":"<SURFACE_ID>","catalogId":"openclaw/basic/v1"}}
{"version":"v0.9","updateComponents":{"surfaceId":"<SURFACE_ID>","components":[{"id":"root","component":"Card","child":"col"},{"id":"col","component":"Column","children":["title","divider","items_col"],"gap":8},{"id":"title","component":"Text","text":{"path":"/title"},"variant":"h3"},{"id":"divider","component":"Divider"},{"id":"items_col","component":"Column","children":{"componentId":"item_row","path":"/items"},"gap":6},{"id":"item_row","component":"Row","children":["item_icon","item_text"],"gap":8,"align":"center"},{"id":"item_icon","component":"Icon","name":{"path":"/icon"}},{"id":"item_text","component":"Text","text":{"path":"/text"},"variant":"body"}]}}
{"version":"v0.9","updateDataModel":{"surfaceId":"<SURFACE_ID>","path":"/","value":{"title":"要点列表","items":[{"icon":"check","text":"第一个要点"},{"icon":"check","text":"第二个要点"},{"icon":"check","text":"第三个要点"}]}}}
```

---

## data-card

**适用：** 键值对数据、统计数字、配置信息。

```jsonl
{"version":"v0.9","createSurface":{"surfaceId":"<SURFACE_ID>","catalogId":"openclaw/basic/v1"}}
{"version":"v0.9","updateComponents":{"surfaceId":"<SURFACE_ID>","components":[{"id":"root","component":"Card","child":"col"},{"id":"col","component":"Column","children":["title","divider","kv_list"],"gap":10},{"id":"title","component":"Text","text":{"path":"/title"},"variant":"h3"},{"id":"divider","component":"Divider"},{"id":"kv_list","component":"Column","children":{"componentId":"kv_row","path":"/fields"},"gap":6},{"id":"kv_row","component":"Row","children":["kv_label","kv_value"],"justify":"spaceBetween","align":"center"},{"id":"kv_label","component":"Text","text":{"path":"/label"},"variant":"caption"},{"id":"kv_value","component":"Text","text":{"path":"/value"},"variant":"body"}]}}
{"version":"v0.9","updateDataModel":{"surfaceId":"<SURFACE_ID>","path":"/","value":{"title":"数据信息","fields":[{"label":"状态","value":"正常"},{"label":"版本","value":"v1.2.3"},{"label":"更新时间","value":"2026-03-09"}]}}}
```

---

## code-card

**适用：** 代码片段展示（使用 OpenClaw CodeBlock 扩展）。

```jsonl
{"version":"v0.9","createSurface":{"surfaceId":"<SURFACE_ID>","catalogId":"openclaw/basic/v1"}}
{"version":"v0.9","updateComponents":{"surfaceId":"<SURFACE_ID>","components":[{"id":"root","component":"Card","child":"col"},{"id":"col","component":"Column","children":["header_row","code_block"],"gap":8},{"id":"header_row","component":"Row","children":["lang_text","title_text"],"gap":8,"align":"center"},{"id":"lang_text","component":"Text","text":{"path":"/language"},"variant":"caption"},{"id":"title_text","component":"Text","text":{"path":"/title"},"variant":"body"},{"id":"code_block","component":"CodeBlock","code":{"path":"/code"},"language":{"path":"/language"}}]}}
{"version":"v0.9","updateDataModel":{"surfaceId":"<SURFACE_ID>","path":"/","value":{"title":"示例代码","language":"python","code":"def hello():\n    print('Hello, A2UI!')\n\nhello()"}}}
```

**无扩展组件回退版（标准 Text 组件）：**
```jsonl
{"version":"v0.9","createSurface":{"surfaceId":"<SURFACE_ID>","catalogId":"openclaw/basic/v1"}}
{"version":"v0.9","updateComponents":{"surfaceId":"<SURFACE_ID>","components":[{"id":"root","component":"Card","child":"col"},{"id":"col","component":"Column","children":["title","code_text"],"gap":8},{"id":"title","component":"Text","text":{"path":"/title"},"variant":"h3"},{"id":"code_text","component":"Text","text":{"path":"/code"},"variant":"body"}]}}
{"version":"v0.9","updateDataModel":{"surfaceId":"<SURFACE_ID>","path":"/","value":{"title":"示例代码","code":"def hello():\n    print('Hello!')"}}}
```

---

## steps-card

**适用：** 步骤说明、操作指引、流程图。

```jsonl
{"version":"v0.9","createSurface":{"surfaceId":"<SURFACE_ID>","catalogId":"openclaw/basic/v1"}}
{"version":"v0.9","updateComponents":{"surfaceId":"<SURFACE_ID>","components":[{"id":"root","component":"Card","child":"col"},{"id":"col","component":"Column","children":["title","steps_col"],"gap":12},{"id":"title","component":"Text","text":{"path":"/title"},"variant":"h3"},{"id":"steps_col","component":"Column","children":{"componentId":"step_item","path":"/steps"},"gap":12},{"id":"step_item","component":"Row","children":["step_num","step_content"],"gap":12,"align":"start"},{"id":"step_num","component":"Text","text":{"path":"/num"},"variant":"h4"},{"id":"step_content","component":"Column","children":["step_title","step_desc"],"gap":2},{"id":"step_title","component":"Text","text":{"path":"/title"},"variant":"body"},{"id":"step_desc","component":"Text","text":{"path":"/desc"},"variant":"caption"}]}}
{"version":"v0.9","updateDataModel":{"surfaceId":"<SURFACE_ID>","path":"/","value":{"title":"操作步骤","steps":[{"num":"1","title":"第一步","desc":"执行第一个操作"},{"num":"2","title":"第二步","desc":"执行第二个操作"},{"num":"3","title":"第三步","desc":"完成"}]}}}
```

---

## table-card

**适用：** 表格数据展示（用 Column/Row 模拟，因官方标准无 Table 组件）。

```jsonl
{"version":"v0.9","createSurface":{"surfaceId":"<SURFACE_ID>","catalogId":"openclaw/basic/v1"}}
{"version":"v0.9","updateComponents":{"surfaceId":"<SURFACE_ID>","components":[{"id":"root","component":"Card","child":"col"},{"id":"col","component":"Column","children":["title","header_row","divider","rows_col"],"gap":4},{"id":"title","component":"Text","text":{"path":"/title"},"variant":"h3"},{"id":"header_row","component":"Row","children":["h1","h2","h3"],"gap":8},{"id":"h1","component":"Text","text":{"path":"/headers/0"},"variant":"h5","weight":1},{"id":"h2","component":"Text","text":{"path":"/headers/1"},"variant":"h5","weight":1},{"id":"h3","component":"Text","text":{"path":"/headers/2"},"variant":"h5","weight":1},{"id":"divider","component":"Divider"},{"id":"rows_col","component":"Column","children":{"componentId":"data_row","path":"/rows"},"gap":4},{"id":"data_row","component":"Row","children":["d1","d2","d3"],"gap":8},{"id":"d1","component":"Text","text":{"path":"/0"},"variant":"body","weight":1},{"id":"d2","component":"Text","text":{"path":"/1"},"variant":"body","weight":1},{"id":"d3","component":"Text","text":{"path":"/2"},"variant":"body","weight":1}]}}
{"version":"v0.9","updateDataModel":{"surfaceId":"<SURFACE_ID>","path":"/","value":{"title":"数据表格","headers":["名称","状态","数量"],"rows":[["项目A","正常","42"],["项目B","警告","7"],["项目C","错误","0"]]}}}
```

---

## composite-card

**适用：** 混合内容（图片 + 文字 + 列表 + 按钮）。

> ⚠️ `Image` 属性是 `url`，Button action v0.9 格式是 `{event:{name:"..."}}`

```jsonl
{"version":"v0.9","createSurface":{"surfaceId":"<SURFACE_ID>","catalogId":"openclaw/basic/v1"}}
{"version":"v0.9","updateComponents":{"surfaceId":"<SURFACE_ID>","components":[{"id":"root","component":"Card","child":"col"},{"id":"col","component":"Column","children":["hero_image","content_col"],"gap":0},{"id":"hero_image","component":"Image","url":{"path":"/image"},"fit":"cover","variant":"hero"},{"id":"content_col","component":"Column","children":["main_title","subtitle","divider","feature_list","action_row"],"gap":10},{"id":"main_title","component":"Text","text":{"path":"/title"},"variant":"h2"},{"id":"subtitle","component":"Text","text":{"path":"/subtitle"},"variant":"body"},{"id":"divider","component":"Divider"},{"id":"feature_list","component":"Column","children":{"componentId":"feat_row","path":"/features"},"gap":6},{"id":"feat_row","component":"Row","children":["feat_icon","feat_text"],"gap":8,"align":"center"},{"id":"feat_icon","component":"Icon","name":"star"},{"id":"feat_text","component":"Text","text":{"path":"/text"},"variant":"body"},{"id":"action_row","component":"Row","children":["action_btn"],"justify":"end"},{"id":"action_btn","component":"Button","child":"btn_label","variant":"primary","action":{"event":{"name":"primary_cta"}}},{"id":"btn_label","component":"Text","text":{"path":"/cta"},"variant":"body"}]}}
{"version":"v0.9","updateDataModel":{"surfaceId":"<SURFACE_ID>","path":"/","value":{"image":"https://example.com/hero.jpg","title":"主标题","subtitle":"这是一段描述性文字，介绍内容的核心价值。","features":[{"text":"特性一：高性能"},{"text":"特性二：易使用"},{"text":"特性三：可扩展"}],"cta":"了解更多"}}}
```

---

## tabs-card

**适用：** 多标签页内容组织。

```jsonl
{"version":"v0.9","createSurface":{"surfaceId":"<SURFACE_ID>","catalogId":"openclaw/basic/v1"}}
{"version":"v0.9","updateComponents":{"surfaceId":"<SURFACE_ID>","components":[{"id":"root","component":"Card","child":"tabs"},{"id":"tabs","component":"Tabs","tabItems":[{"title":"概览","child":"tab_overview"},{"title":"详情","child":"tab_detail"}]},{"id":"tab_overview","component":"Text","text":{"path":"/overview"},"variant":"body"},{"id":"tab_detail","component":"Text","text":{"path":"/detail"},"variant":"body"}]}}
{"version":"v0.9","updateDataModel":{"surfaceId":"<SURFACE_ID>","path":"/","value":{"overview":"概览内容在这里。","detail":"详细内容在这里。"}}}
```

---

## form-card

**适用：** 表单（输入框 + 提交按钮）。

```jsonl
{"version":"v0.9","createSurface":{"surfaceId":"<SURFACE_ID>","catalogId":"openclaw/basic/v1"}}
{"version":"v0.9","updateComponents":{"surfaceId":"<SURFACE_ID>","components":[{"id":"root","component":"Card","child":"col"},{"id":"col","component":"Column","children":["title","name_field","email_field","submit_btn"],"gap":12},{"id":"title","component":"Text","text":"请填写信息","variant":"h3"},{"id":"name_field","component":"TextField","label":"姓名","value":{"path":"/form/name"},"textFieldType":"shortText"},{"id":"email_field","component":"TextField","label":"邮箱","value":{"path":"/form/email"},"textFieldType":"shortText"},{"id":"submit_btn","component":"Button","child":"btn_text","variant":"primary","action":{"event":{"name":"submit_form","context":[{"key":"name","value":{"path":"/form/name"}},{"key":"email","value":{"path":"/form/email"}}]}}},{"id":"btn_text","component":"Text","text":"提交","variant":"body"}]}}
{"version":"v0.9","updateDataModel":{"surfaceId":"<SURFACE_ID>","path":"/","value":{"form":{"name":"","email":""}}}}
```

---

## v0.8 回退版模板（TextCard）

如果渲染器不支持 v0.9，可使用 v0.8 格式（无 `version` 字段）：

```jsonl
{"surfaceUpdate":{"surfaceId":"<SURFACE_ID>","components":[{"id":"root","component":{"Card":{"child":"col"}}},{"id":"col","component":{"Column":{"children":{"explicitList":["title","body_text"]}}}},{"id":"title","component":{"Text":{"text":{"literalString":"标题"},"usageHint":"h3"}}},{"id":"body_text","component":{"Text":{"text":{"path":"/body"},"usageHint":"body"}}}]}}
{"dataModelUpdate":{"surfaceId":"<SURFACE_ID>","contents":[{"key":"body","valueString":"正文内容在这里。"}]}}
{"beginRendering":{"surfaceId":"<SURFACE_ID>","root":"root"}}
```

---

## 回退方案：纯 HTML canvas

当 `a2ui_push` 不可用时，生成自包含 HTML 写入 workspace：

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Rich Reply</title>
<style>
  body { font-family: -apple-system, sans-serif; padding: 16px; background: #f5f5f5; }
  .card { background: #fff; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.12); padding: 20px; max-width: 600px; margin: 0 auto; }
  h2 { margin: 0 0 12px; color: #1a1a1a; }
  p { color: #555; line-height: 1.6; }
  img { width: 100%; border-radius: 8px; }
</style>
</head>
<body>
<div class="card">
  <!-- 内容插入这里 -->
</div>
</body>
</html>
```

步骤：
1. 写入 `~/.openclaw/workspace/canvas/reply.html`
2. `canvas(action=present, url=http://127.0.0.1:18793/__openclaw__/canvas/reply.html)`
