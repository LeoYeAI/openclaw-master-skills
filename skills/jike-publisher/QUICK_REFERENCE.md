# Jike Publishing Quick Reference

## 🚀 Quick Start (Copy-Paste Template)

```python
# 1. Prepare content with Unicode escape
content = """你的中文内容"""
escaped = content.encode('unicode_escape').decode('ascii')

# 2. Navigate to Jike
browser(action="navigate", targetUrl="https://web.okjike.com/following", targetId="<TAB_ID>")
exec(command="sleep 2")

# 3. Snapshot to find textbox
browser(action="snapshot", compact=True, targetId="<TAB_ID>")
# Look for: textarea or contenteditable div

# 4. Click textbox
browser(action="act", request={"kind": "click", "ref": "eXX"}, targetId="<TAB_ID>")

# 5. Type content
browser(action="act", request={"kind": "type", "ref": "eXX", "text": escaped}, targetId="<TAB_ID>")

# 6. Snapshot to find send button
browser(action="snapshot", compact=True, targetId="<TAB_ID>")
# Look for: button "发布" [ref=eXX]

# 7. Click send
browser(action="act", request={"kind": "click", "ref": "eXX"}, targetId="<TAB_ID>")

# 8. Verify
exec(command="sleep 3")
browser(action="snapshot", compact=True, targetId="<TAB_ID>")
```

## ⚠️ Critical Rules

### 1. ALWAYS Use Unicode Escape for Chinese
```python
# ✅ Correct
escaped = content.encode('unicode_escape').decode('ascii')
browser(action="act", request={"kind": "type", "ref": "eXX", "text": escaped})

# ❌ Wrong - Will fail with JSON parsing errors
browser(action="act", request={"kind": "type", "ref": "eXX", "text": "中文内容"})
```

### 2. ALWAYS Snapshot Before Each Operation
```python
# ✅ Correct - Fresh snapshot
browser(action="snapshot", targetId=tab_id)
browser(action="act", request={"kind": "click", "ref": "eXX"})

# ❌ Wrong - Hardcoded ref (will break when refs change)
browser(action="act", request={"kind": "click", "ref": "e123"})
```

### 3. ALWAYS Separate Operations
```python
# ✅ Correct - Separate click and type
browser(action="act", request={"kind": "click", "ref": "eXX"})
browser(action="act", request={"kind": "type", "ref": "eXX", "text": escaped})

# ❌ Wrong - Combined operations (unreliable)
browser(action="act", request={"kind": "click", "ref": "eXX", "text": escaped})
```

## 📋 Common Element Patterns (需要实际获取)

| Element | 查找方式 |
|---------|---------|
| Post textbox | 搜索 textarea 或 contenteditable |
| Send button | 搜索 "发布" 文本 |

**Note**: Refs change frequently! Always snapshot first.

## 🐛 Common Errors

### Error: JSON parsing failed
**Cause**: 中文引号导致
**Fix**: 使用 Unicode escape

### Error: Element not found
**Cause**: Element ref changed
**Fix**: 重新 snapshot 获取新 ref

### Error: Send button disabled
**Cause**: 输入框为空或内容违规
**Fix**: 检查内容是否正确输入

## ✅ Verification Checklist

发布后检查:
- [ ] 等待 3 秒
- [ ] 刷新页面或 snapshot
- [ ] 确认内容出现在动态中
- [ ] 更新 `memory/jike-state.json`

## 📊 State File Format

```json
{
  "lastPublishTime": 1772635680,
  "lastPublishDate": "2026-03-16T15:08:00+08:00",
  "lastContent": "Your last post content..."
}
```

## 🎯 Best Practices

1. **Unicode escape**: 中文内容必须用
2. **Snapshot first**: 不要硬编码 ref
3. **Separate ops**: 点击 → 输入 → snapshot → 发布
4. **Verify**: 检查是否发布成功
5. **Rate limit**: 建议间隔 60 秒
6. **State tracking**: 更新 JSON 记录

## 📚 Full Documentation

- [SKILL.md](../SKILL.md) - 完整指南
- [EXAMPLES.md](EXAMPLES.md) - 实际案例
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - 错误解决

## 🔗 Quick Links

- 即刻首页: https://web.okjike.com/
- 关注动态: https://web.okjike.com/following
- Browser tab ID: 用 `browser(action="tabs")` 查看

## 💡 Pro Tips

1. **Emoji support**: Unicode escape 支持 emoji
2. **Hashtags**: 使用 #话题# 格式
3. **Line breaks**: 转义前包含 \n
4. **Links**: 直接粘贴 URL 会自动展开
5. **Content length**: 100-200 字最佳

## 🚨 Emergency Recovery

如果发布失败:
1. 检查浏览器状态: `browser(action="status")`
2. 检查标签: `browser(action="tabs")`
3. 导航到即刻: `browser(action="navigate", targetUrl="https://web.okjike.com/following")`
4. 快照: `browser(action="snapshot")`
5. 验证登录: 检查快照中是否有用户名
6. 用最新 ref 重试

## 📅 Last Updated

2026-03-16 - 初始版本
