---
name: jike-publisher
description: Publish posts to Jike (即刻) using browser automation. Use when the user wants to post content to Jike, share updates on Jike, or automate Jike posting. Supports text posts with emoji, hashtags, and topics. No API key required - uses browser automation with managed browser profile.
---

# Jike Publisher

Automate posting to Jike (即刻) using browser automation through OpenClaw's managed browser.

## Prerequisites

- Jike account must be logged in via managed browser (profile="openclaw")
- Browser must have active session with valid cookies
- Navigate to https://web.okjike.com/ first to ensure login

## Quick Start

### Basic Post

```python
# 1. Prepare content with Unicode escape (for Chinese text)
content = "刚刚看到一篇很棒的技术文章！"
escaped_content = content.encode('unicode_escape').decode('ascii')

# 2. Navigate to Jike homepage
browser(action="navigate", targetUrl="https://web.okjike.com/following", targetId=<tab_id>)

# 3. Get page snapshot to find elements
browser(action="snapshot", targetId=<tab_id>)

# 4. Click the post textbox (ref from snapshot)
# Look for: textarea or contenteditable div
browser(action="act", request={"kind": "click", "ref": "<textbox_ref>"}, targetId=<tab_id>)

# 5. Type content with Unicode escape
browser(action="act", request={"kind": "type", "ref": "<textbox_ref>", "text": escaped_content}, targetId=<tab_id>)

# 6. Get fresh snapshot to find send button
browser(action="snapshot", targetId=<tab_id>)

# 7. Click send button (ref from snapshot, usually "发布" text)
browser(action="act", request={"kind": "click", "ref": "<send_ref>"}, targetId=<tab_id>)

# 8. Wait and verify
sleep(3)
browser(action="snapshot", targetId=<tab_id>)
```

## Element References (需要实际获取)

即刻的页面元素引用需要通过 snapshot 实际获取，常见元素：

- **Post textbox**: 通常在页面顶部的输入框
- **Send button**: "发布" 按钮
- **Topic button**: 话题选择按钮（可选）

**重要**: 元素引用会频繁变化，**每次操作前都要先 snapshot**！

## Content Features

### 支持的内容类型

1. **纯文本**: 直接输入
2. **Emoji**: 可以直接使用 (如 💪🎉)
3. **话题**: 使用 #话题# 格式
4. **链接**: 直接粘贴 URL 会自动展开
5. **换行**: 使用 \n

### 内容限制

- 最大长度: 即刻没有严格字数限制，建议 200-500 字
- 推荐长度: 100-200 字更易互动

## Workflows

### Workflow 1: 简单发布

1. 打开 https://web.okjike.com/following
2. Snapshot 获取元素引用
3. 点击输入框
4. 输入内容
5. 点击发布
6. 验证成功

### Workflow 2: 带话题发布

1. 同 Workflow 1
2. 输入内容时包含 #话题#
3. 发布

## State Management

记录发布历史到 `memory/jike-state.json`:

```json
{
  "lastPublishTime": 1740880260,
  "lastPublishDate": "2026-03-16T12:38:00+08:00",
  "lastContent": "Your last post content..."
}
```

## Error Handling

### 常见问题

1. **登录过期**
   - 症状: 跳转到登录页
   - 解决: 手动登录后重试

2. **找不到元素**
   - 症状: ref 无效
   - 解决: 重新 snapshot 获取最新 ref

3. **发布按钮禁用**
   - 症状: 按钮不可点击
   - 解决: 检查内容是否为空

4. **内容未出现**
   - 症状: 无错误但看不到内容
   - 解决: 等待几秒，刷新页面

## Best Practices

1. **Unicode 转义**: 中文内容使用转义
2. **先 snapshot**: 元素引用会变化
3. **分步操作**: 点击 → 输入 → snapshot → 发布
4. **验证**: 发布后检查是否成功
5. **速率限制**: 建议间隔 60 秒以上
6. **状态记录**: 更新 jike-state.json

## Technical Details

### 浏览器自动化

- **Profile**: openclaw (托管浏览器)
- **方法**: Chrome DevTools Protocol (CDP)
- **会话**: 基于 Cookie，重启后保持
- **无需 API**: 纯浏览器自动化

### Request 格式

```javascript
// ✅ 正确
request={"kind": "type", "ref": "eXXX", "text": "content"}

// ❌ 错误
request="{\"kind\": \"type\", \"ref\": \"eXXX\", \"text\": \"content\"}"
```

### Unicode 转义（重要！）

**问题**: 中文引号（""、''）会导致 JSON 解析错误

**解决**: 使用 Unicode 转义:

```python
# 转换中文为 Unicode 转义
text = "刚刚看到一篇很棒的技术文章"
escaped = text.encode('unicode_escape').decode('ascii')
# 结果: \u521a\u521a\u770b\u5230\u4e00\u7bc87\u5f88\u68d2\u7684\u6280\u672f\u6587\u7ae0
```

## Reference Files

- **[EXAMPLES.md](references/EXAMPLES.md)**: 实际发布示例
- **[TROUBLESHOOTING.md](references/TROUBLESHOOTING.md)**: 详细错误解决方案
- **[UNICODE_ESCAPE.md](references/UNICODE_ESCAPE.md)**: Unicode 转义完整指南

## Scripts

- **[post_jike.py](scripts/post_jike.py)**: 独立 Python 脚本（可选）
