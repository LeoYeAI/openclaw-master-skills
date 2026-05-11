# Block Types Reference

The internal API uses a specific block format. Here are all supported types:

## Headings

```json
{"type": "header", "properties": {"title": [["Heading 1"]]}}
{"type": "sub_header", "properties": {"title": [["Heading 2"]]}}
{"type": "sub_sub_header", "properties": {"title": [["Heading 3"]]}}
```

## Text

```json
{"type": "text", "properties": {"title": [["Plain text paragraph"]]}}
```

## Lists

```json
{"type": "bulleted_list", "properties": {"title": [["Bullet item"]]}}
{"type": "numbered_list", "properties": {"title": [["Numbered item"]]}}
```

## Nested Children

List blocks support nested children via the `children` property:

```json
{"type": "bulleted_list", "properties": {"title": [["Parent"]]}, "children": [{"type": "bulleted_list", "properties": {"title": [["Child"]]}}]}
```

## To-Do / Checkbox

```json
{"type": "to_do", "properties": {"title": [["Task item"]], "checked": [["Yes"]]}}
{"type": "to_do", "properties": {"title": [["Unchecked task"]], "checked": [["No"]]}}
```

## Code Block

```json
{"type": "code", "properties": {"title": [["console.log('hello')"]], "language": [["javascript"]]}}
```

## Quote

```json
{"type": "quote", "properties": {"title": [["Quoted text"]]}}
```

## Divider

```json
{"type": "divider"}
```

## Rich Text Formatting

Rich text uses nested arrays with formatting codes:

| Format | Syntax | Example |
|--------|--------|---------|
| Plain | `[["text"]]` | `[["Hello"]]` |
| Bold | `["text", [["b"]]]` | `["Hello", [["b"]]]` |
| Italic | `["text", [["i"]]]` | `["Hello", [["i"]]]` |
| Strikethrough | `["text", [["s"]]]` | `["Hello", [["s"]]]` |
| Inline code | `["text", [["c"]]]` | `["Hello", [["c"]]]` |
| Link | `["text", [["a", "url"]]]` | `["Click", [["a", "https://example.com"]]]` |
| Bold + Italic | `["text", [["b"], ["i"]]]` | `["Hello", [["b"], ["i"]]]` |

Multiple segments: `[["plain "], ["bold", [["b"]]], [" more plain"]]`
