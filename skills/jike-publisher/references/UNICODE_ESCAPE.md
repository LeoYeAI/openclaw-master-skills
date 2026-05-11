# Unicode Escape Guide for Chinese Content

## The Problem

When posting Chinese content to Jike via browser automation, you may encounter JSON parsing errors:

```
Validation failed for tool "browser": - request: must be object
```

This happens because Chinese quotation marks (""、'') conflict with JSON string delimiters.

## The Solution

Use Unicode escape (`\uXXXX`) for all Chinese characters.

## How It Works

### Converting to Unicode Escape

```python
# Original Chinese text
content = "刚刚解决了一个技术难题"

# Convert to Unicode escape
escaped = content.encode('unicode_escape').decode('ascii')
# Result: \u521a\u521a\u89e3\u51b3\u4e86\u4e00\u4e2a\u6280\u672f\u96be\u9898

# Now safe to use in JSON
browser(action="act", request={"kind": "type", "ref": "e42", "text": escaped})
```

### Why This Works

```
❌ Direct Chinese (with quotes):
{"kind": "type", "ref": "e42", "text": "刚刚解决了"难题""}
                                                        ↑     ↑
                                              These break JSON parsing!

✅ Unicode escaped:
{"kind": "type", "ref": "e42", "text": "\u521a\u521a\u89e3\u51b3\u4e86\u96be\u9898"}
                                                        ↑
                                              Safe ASCII characters only
```

## Examples

### Example 1: Simple Text

```python
content = "今天天气真好"
escaped = content.encode('unicode_escape').decode('ascii')
# \u4eca\u5929\u5929\u6c14\u771f\u597d
```

### Example 2: With Emoji

```python
content = "今天完成了一个功能！💪"
escaped = content.encode('unicode_escape').decode('ascii')
# \u4eca\u5929\u5b8c\u6210\u4e86\u4e00\u4e2a\u529f\u80fd\uff01\ud83d\udcaa
```

### Example 3: Multi-line

```python
content = """第一行
第二行
第三行"""
escaped = content.encode('unicode_escape').decode('ascii')
# \u7b2c\u4e00\u884c\n\u7b2c\u4e8c\u884c\n\u7b2c\u4e09\u884c
```

### Example 4: With Special Characters

```python
content = "价格：¥99.99"
escaped = content.encode('unicode_escape').decode('ascii')
# \u4ef7\u683c\uff1a\uffe599.99
```

## Characters That Need Escaping

| Character | Unicode | Note |
|-----------|---------|------|
| " " | \u201c \u201d | Chinese quotation marks |
| ' ' | \u2018 \u2019 | Chinese apostrophes |
| … | \u2026 | Ellipsis |
| — | \u2014 | Em dash |
| – | \u2013 | En dash |
| ￥ | \uffe5 | Yuan sign |
| 、 | \u3001 | Enumeration comma |
| 。 | \u3002 | Full stop |

## Complete Workflow

```python
import json

# 1. Define your content
content = "今天分享一个好用的工具 #AI工具"

# 2. Convert to Unicode escape
escaped = content.encode('unicode_escape').decode('ascii')

# 3. Use in browser action
request_data = {
    "kind": "type",
    "ref": "e42",
    "text": escaped
}

# 4. This is now safe JSON
browser(action="act", request=request_data, targetId=tab_id)
```

## Quick Helper Function

```python
def escape_chinese(text):
    """Convert Chinese text to Unicode escape."""
    return text.encode('unicode_escape').decode('ascii')

# Usage
content = "今天天气真好"
escaped = escape_chinese(content)
browser(action="act", request={"kind": "type", "ref": "e42", "text": escaped})
```

## Testing Your Escape

```python
# Test that your escaped text is valid ASCII
try:
    escaped = content.encode('unicode_escape').decode('ascii')
    print(f"✅ Safe to use: {escaped[:50]}...")
except Exception as e:
    print(f"❌ Error: {e}")
```

## Troubleshooting

### "request: must be object" Error

**Cause**: Chinese quotes in your text

**Fix**: Use Unicode escape

```python
# ❌ Wrong
content = "他说："你好""
browser(action="act", request={"kind": "type", "ref": "e42", "text": content})

# ✅ Correct
content = "他说："你好""
escaped = content.encode('unicode_escape').decode('ascii')
browser(action="act", request={"kind": "type", "ref": "e42", "text": escaped})
```

### Content Not Appearing Correctly

**Cause**: Double-encoding

**Fix**: Only escape once

```python
# ❌ Wrong - double escape
escaped = content.encode('unicode_escape').decode('ascii')
double_escaped = escaped.encode('unicode_escape').decode('ascii')

# ✅ Correct - single escape
escaped = content.encode('unicode_escape').decode('ascii')
```

## Summary

| Rule | Example |
|------|---------|
| Always escape Chinese | `content.encode('unicode_escape').decode('ascii')` |
| Escape once only | Don't escape already-escaped text |
| Test with ASCII | Verify result is valid ASCII |
| Use escaped in JSON | Pass escaped string to browser tool |
