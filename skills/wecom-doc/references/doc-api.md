# 企业微信文档 API 参考

## 文档类型

| doc_type | 类型 | doc_id 前缀 | URL 路径 |
|----------|------|------------|---------|
| 3 | 文档 | `w3_` | `/doc/` |
| 10 | 智能表格 | `s3_` | `/smartsheet/` |

## URL 格式

### 文档

```
https://doc.weixin.qq.com/doc/{doc_id}?scode=xxx
```

示例：
```
https://doc.weixin.qq.com/doc/w3_AMEA4QYkACkCNN7hNRzRzQkaElHbQ?scode=AJEAIQdfAAodYknI73AMEA4QYkACk
→ doc_id = w3_AMEA4QYkACkCNN7hNRzRzQkaElHbQ
```

### 智能表格

```
https://doc.weixin.qq.com/smartsheet/{doc_id}
```

示例：
```
https://doc.weixin.qq.com/smartsheet/s3_ATAA_QaoAKQCNIQ6XYeEYQ3q5Rv05
→ doc_id = s3_ATAA_QaoAKQCNIQ6XYeEYQ3q5Rv05
```

> 始终忽略 `?` 之后的查询参数。

## 智能表格字段类型（FieldType）

完整 16 种类型：

| 枚举值 | 说明 |
|--------|------|
| `FIELD_TYPE_TEXT` | 文本 |
| `FIELD_TYPE_NUMBER` | 数字 |
| `FIELD_TYPE_CHECKBOX` | 复选框 |
| `FIELD_TYPE_DATE_TIME` | 日期时间 |
| `FIELD_TYPE_IMAGE` | 图片 |
| `FIELD_TYPE_USER` | 成员 |
| `FIELD_TYPE_URL` | 链接 |
| `FIELD_TYPE_SELECT` | 多选 |
| `FIELD_TYPE_SINGLE_SELECT` | 单选 |
| `FIELD_TYPE_PROGRESS` | 进度 |
| `FIELD_TYPE_PHONE_NUMBER` | 手机号 |
| `FIELD_TYPE_EMAIL` | 邮箱 |
| `FIELD_TYPE_LOCATION` | 位置 |
| `FIELD_TYPE_CURRENCY` | 货币 |
| `FIELD_TYPE_PERCENTAGE` | 百分比 |
| `FIELD_TYPE_BARCODE` | 条码 |

## CellValue 类型完整对照

### CellTextValue — 文本字段

```json
[
  {"type": "text", "text": "普通文本"},
  {"type": "url", "text": "链接文本", "link": "https://example.com"}
]
```

- `type`（必填）：`"text"` 或 `"url"`
- `text`（必填）：文本内容
- `link`（当 type 为 url 时）：链接跳转 URL

适用：`FIELD_TYPE_TEXT`

### 数字类 — number

直接传 number 值。

```json
85
```

适用：`FIELD_TYPE_NUMBER`、`FIELD_TYPE_PROGRESS`、`FIELD_TYPE_CURRENCY`、`FIELD_TYPE_PERCENTAGE`

### 布尔值 — boolean

```json
true
```

适用：`FIELD_TYPE_CHECKBOX`

### 字符串类 — string

直接传字符串。

适用场景：
- `FIELD_TYPE_DATE_TIME`：毫秒 unix 时间戳字符串，如 `"1672531200000"`
- `FIELD_TYPE_PHONE_NUMBER`：手机号字符串，如 `"13800138000"`
- `FIELD_TYPE_EMAIL`：邮箱字符串，如 `"user@example.com"`
- `FIELD_TYPE_BARCODE`：条码字符串，如 `"978-3-16-148410-0"`

### CellUrlValue — 链接字段

```json
[{"type": "url", "text": "显示文本", "link": "https://example.com"}]
```

- `type`（必填）：固定 `"url"`
- `link`（必填）：链接跳转 URL
- `text`（可选）：链接显示文本

> 注意：字段名是 **`link`** 不是 `url`。数组为预留能力，目前只支持 1 个链接。

适用：`FIELD_TYPE_URL`

### CellUserValue — 成员字段

```json
[{"user_id": "zhangsan"}]
```

- `user_id`（必填）：成员 ID

适用：`FIELD_TYPE_USER`

### CellImageValue — 图片字段

```json
[{
  "id": "img1",
  "title": "截图",
  "image_url": "https://...",
  "width": 800,
  "height": 600
}]
```

- `id`：图片 ID（自定义）
- `title`：图片标题
- `image_url`：图片链接（通过上传图片接口获取）
- `width` / `height`：图片尺寸

适用：`FIELD_TYPE_IMAGE`

### CellAttachmentValue — 文件字段

```json
[{
  "name": "文件名",
  "size": 1024,
  "file_ext": "DOC",
  "file_id": "xxx",
  "file_url": "https://...",
  "file_type": "50"
}]
```

- `file_ext` 取值：`DOC`、`SHEET`、`SLIDE`、`MIND`、`FLOWCHART`、`SMARTSHEET`、`FORM`，或文件扩展名
- `file_type` 取值：`Folder`（文件夹）、`Wedrive`（微盘文件）、`30`（收集表）、`50`（文档）、`51`（表格）、`52`（幻灯片）、`54`（思维导图）、`55`（流程图）、`70`（智能表）

### Option — 选项（单选/多选字段）

```json
[{"text": "选项A", "style": 1}, {"text": "选项B", "style": 5}]
```

- `text`：选项内容。新增选项时填写，已存在时优先匹配
- `id`（可选）：选项 ID，已存在的选项通过 ID 识别
- `style`（可选）：选项颜色，1-27

适用：`FIELD_TYPE_SELECT`（多选，可传多个）、`FIELD_TYPE_SINGLE_SELECT`（单选，建议传 1 个）

### CellLocationValue — 位置字段

```json
[{
  "source_type": 1,
  "id": "地点ID",
  "latitude": "39.9042",
  "longitude": "116.4074",
  "title": "北京天安门"
}]
```

- `source_type`（必填）：固定 `1`（腾讯地图）
- `id`（必填）：地点 ID
- `latitude`（必填）：纬度（字符串）
- `longitude`（必填）：经度（字符串）
- `title`（必填）：地点名称

> 数组长度不大于 1。

适用：`FIELD_TYPE_LOCATION`

## 选项样式（Style）

取值 1-27 对应颜色：

| 值 | 颜色 | 值 | 颜色 | 值 | 颜色 |
|----|------|----|------|----|------|
| 1 | 浅红 | 10 | 浅蓝 | 19 | 浅橙 |
| 2 | 浅橙 | 11 | 浅蓝 | 20 | 橙 |
| 3 | 浅天蓝 | 12 | 蓝 | 21 | 浅黄 |
| 4 | 浅绿 | 13 | 浅天蓝 | 22 | 浅黄 |
| 5 | 浅紫 | 14 | 天蓝 | 23 | 黄 |
| 6 | 浅粉红 | 15 | 浅绿 | 24 | 浅紫 |
| 7 | 浅灰 | 16 | 绿 | 25 | 紫 |
| 8 | 白 | 17 | 浅红 | 26 | 浅粉红 |
| 9 | 灰 | 18 | 红 | 27 | 粉红 |

## 限制

| 维度 | 限制 |
|------|------|
| 文档名称 | 最多 255 字符 |
| 子表字段数 | 单表最多 150 个 |
| 记录数 | 单表最多 100,000 行 |
| 单元格数 | 单表最多 15,000,000 个 |
| 单次添加记录 | 建议 500 行内 |
| 不可写入字段 | 创建时间、最后编辑时间、创建人、最后编辑人 |
