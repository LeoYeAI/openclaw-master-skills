# Jike Publisher - Troubleshooting

Common issues and their solutions.

## Issue 1: "element not found" Error

### Symptoms
```
Error: Cannot find element with ref "e42"
```

### Cause
Element references change between sessions. The ref you're using is outdated.

### Solution
Take a fresh snapshot before each operation:

```python
# ✅ Correct - Get fresh ref
browser(action="snapshot", targetId=tab_id)
# Now use the ref from the new snapshot

# ❌ Wrong - Using old cached ref
browser(action="act", request={"kind": "click", "ref": "e42"})
```

---

## Issue 2: "request: must be object" Validation Error

### Symptoms
```
Validation failed for tool "browser": - request: must be object
```

### Cause
Chinese quotation marks (""、'') in your content are breaking JSON parsing.

### Solution
Use Unicode escape for all Chinese content:

```python
# ❌ Wrong - Direct Chinese
content = "刚刚解决了"问题""

# ✅ Correct - Unicode escape
content = "刚刚解决了"问题""
escaped = content.encode('unicode_escape').decode('ascii')
browser(action="act", request={"kind": "type", "ref": "e42", "text": escaped})
```

---

## Issue 3: Send Button Disabled

### Symptoms
The send button has `disabled` attribute and won't click.

### Possible Causes
1. Textbox is empty
2. Content is too short
3. Content violates Jike's rules

### Solution
Check that content was actually typed:

```python
# After typing, verify content exists
browser(action="snapshot", targetId=tab_id)
# Check if the textbox now has your content

# If empty, try typing again
# If content exists but button disabled, check content length
```

---

## Issue 4: Login Expired

### Symptoms
- Redirected to login page
- Snapshot shows "登录" instead of content
- Can't find post textbox

### Solution
Manually log in via browser, then retry:

1. Open https://web.okjike.com/ in browser
2. Log in to your account
3. Retry the post

---

## Issue 5: Post Not Appearing

### Symptoms
No error message, but post doesn't show in timeline.

### Possible Causes
1. Content under review
2. Network delay
3. Page not refreshed

### Solution
Wait and refresh:

```python
# Wait after clicking send
sleep(5)

# Refresh page
browser(action="navigate", targetUrl="https://web.okjike.com/following", targetId=tab_id)

# Check if post appears
browser(action="snapshot", targetId=tab_id)
```

---

## Issue 6: Rate Limiting

### Symptoms
- Posting fails repeatedly
- "发布中" status persists
- Error messages about rate limit

### Solution
Add delay between posts:

```python
# Wait between posts
sleep(60)  # 60 seconds minimum
```

---

## Issue 7: Browser Not Responding

### Symptoms
- Commands timeout
- No response from browser

### Solution
Check browser status:

```python
# Check status
browser(action="status")

# Check tabs
browser(action="tabs")

# If needed, navigate to Jike again
browser(action="navigate", targetUrl="https://web.okjike.com/following", targetId=tab_id)
```

---

## Issue 8: Content Too Long

### Symptoms
Content gets truncated or rejected.

### Solution
Check content length:

```python
if len(content) > 2000:
    # Truncate or split
    content = content[:2000]
```

---

## Debugging Tips

### 1. Always Snapshot First

```python
# Before any operation, snapshot to see current state
browser(action="snapshot", targetId=tab_id)
```

### 2. Check Page State

```python
# After navigation, verify you're on the right page
browser(action="snapshot", targetId=tab_id)
# Look for expected elements (post button, etc.)
```

### 3. Verify Login Status

```python
# Check if username appears in snapshot
browser(action="snapshot", targetId=tab_id)
# If you see "登录" instead of username, not logged in
```

### 4. Step-by-Step Verification

```python
# After each step, verify
browser(action="act", request={"kind": "click", "ref": "e42"}, targetId=tab_id)
sleep(1)
browser(action="snapshot", targetId=tab_id)
# Did the click work? Is the textbox focused?
```

---

## Getting Help

If issues persist:

1. Check the [SKILL.md](../SKILL.md) for detailed instructions
2. Review [EXAMPLES.md](EXAMPLES.md) for working examples
3. Check Jike's current page structure (they may have updated UI)
4. Enable browser logging if available
