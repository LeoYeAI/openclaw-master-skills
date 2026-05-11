# ui-config.json 参考

每个需要 HTML 渲染的技能，在其目录下放 `ui-config.json` 即可被 skill-ui-bridge 自动扫描加载。

## 完整字段说明

```json
{
  "version": 1,
  "description": "技能描述（仅供人类阅读）",
  "dompurify": {
    "allowedTags": ["div", "span", "style", "..."],
    "allowedAttrs": ["class", "style", "id", "..."]
  },
  "markdown": {
    "allowRawHTML": true
  },
  "customCSS": "/* 注入到 <head> 的全局 CSS */"
}
```

## 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `version` | number | 固定为 `1` |
| `dompurify.allowedTags` | string[] | 追加到 DOMPurify 默认白名单的 HTML 标签 |
| `dompurify.allowedAttrs` | string[] | 追加到 DOMPurify 默认白名单的 HTML 属性 |
| `markdown.allowRawHTML` | boolean | 是否允许 marked.js 渲染裸 HTML（`true` 推荐） |
| `customCSS` | string | 注入到 `<head>` 的全局 CSS 字符串 |

## 默认已包含的标签（无需重复声明）

```
a b blockquote br code del em h1-h4 hr i img li ol p pre strong table tbody td th thead tr ul video source
```

## 常用扩展示例

### 最小配置（仅开启 raw HTML）
```json
{
  "version": 1,
  "markdown": { "allowRawHTML": true }
}
```

### 标准卡片 UI 配置
```json
{
  "version": 1,
  "dompurify": {
    "allowedTags": ["div", "span", "section", "svg", "path", "circle", "rect", "polyline", "line"],
    "allowedAttrs": ["class", "style", "id", "viewBox", "fill", "stroke", "stroke-width", "d", "cx", "cy", "r"]
  },
  "markdown": { "allowRawHTML": true }
}
```
