# Jike Publisher - Examples

This file contains real-world examples of posting to Jike.

## Example 1: Simple Text Post

```python
# Content
content = "今天天气真好，适合写代码！"

# Unicode escape
escaped = content.encode('unicode_escape').decode('ascii')
# Result: \u4eca\u5929\u5929\u6c14\u771f\u597d\uff0c\u9002\u5408\u5199\u4ee3\u7801\uff01

# Navigate
browser(action="navigate", targetUrl="https://web.okjike.com/following", targetId=tab_id)

# Snapshot
browser(action="snapshot", targetId=tab_id)
# Result shows: textarea with ref=e42

# Click textbox
browser(action="act", request={"kind": "click", "ref": "e42"}, targetId=tab_id)

# Type content
browser(action="act", request={"kind": "type", "ref": "e42", "text": escaped}, targetId=tab_id)

# Snapshot for send button
browser(action="snapshot", targetId=tab_id)
# Result shows: button "发布" with ref=e58

# Click send
browser(action="act", request={"kind": "click", "ref": "e58"}, targetId=tab_id)

# Wait and verify
sleep(3)
browser(action="snapshot", targetId=tab_id)
```

## Example 2: Post with Hashtags

```python
# Content with hashtag
content = "分享一个好用的 AI 工具 #AI工具"

# Unicode escape
escaped = content.encode('unicode_escape').decode('ascii')

# ... same workflow as Example 1
```

## Example 3: Post with Emoji

```python
# Content with emoji
content = "今天完成了一个功能！💪🎉"

# Unicode escape (emoji works too!)
escaped = content.encode('unicode_escape').decode('ascii')

# ... same workflow
```

## Example 4: Multi-line Post

```python
# Multi-line content
content = """今天做了一个新功能：

1. 用户登录
2. 数据同步
3. 自动发布

感觉效率提升不少！"""

# Unicode escape (includes \n)
escaped = content.encode('unicode_escape').decode('ascii')

# ... same workflow
```

## Example 5: Post with Link

```python
# Content with URL
content = "看到一篇很棒的文章：https://blog.gudong.site/example"

# Unicode escape
escaped = content.encode('unicode_escape').decode('ascii')

# ... same workflow
# URL will be auto-expanded by Jike
```

## Element Reference Examples

These are example refs - **always get fresh refs with snapshot!**

| Element | Example Refs | How to Find |
|---------|--------------|-------------|
| Textarea | e42, e156, e89 | Snapshot + search for textarea |
| Send button | e58, e234, e112 | Snapshot + search for "发布" |

## Error Recovery Examples

### Ref Changed Error

```python
# Try to click with old ref
browser(action="act", request={"kind": "click", "ref": "e42"}, targetId=tab_id)
# Error: element not found

# Solution: Take new snapshot
browser(action="snapshot", targetId=tab_id)
# New ref is e89

# Retry with new ref
browser(action="act", request={"kind": "click", "ref": "e89"}, targetId=tab_id)
```

### Login Expired

```python
# Navigate to Jike
browser(action="navigate", targetUrl="https://web.okjike.com/following", targetId=tab_id)

# Snapshot
browser(action="snapshot", targetId=tab_id)

# Check if login page
# If snapshot shows "登录" button instead of content, login expired
# Solution: Manual login required

# After manual login, retry
```

## State Update Example

```python
import json
from pathlib import Path
from datetime import datetime
import time

# After successful post
state_file = Path.home() / ".openclaw/workspace-distribute/memory/jike-state.json"

state = {
    "lastPublishTime": int(time.time()),
    "lastPublishDate": datetime.now().isoformat(),
    "lastContent": content
}

state_file.parent.mkdir(parents=True, exist_ok=True)
with open(state_file, 'w', encoding='utf-8') as f:
    json.dump(state, f, ensure_ascii=False, indent=2)
```
