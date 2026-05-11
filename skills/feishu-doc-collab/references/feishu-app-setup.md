# Feishu App Setup Guide / 飞书应用配置指南

This guide covers the Feishu (Lark) app configuration needed for the doc collaboration skill.

## Prerequisites

You need a Feishu enterprise app with the following:

### 1. App Credentials

- App ID and App Secret (from Feishu Open Platform)
- These should already be configured in OpenClaw's `openclaw.json` under `channels.feishu`

### 2. Event Subscriptions (事件订阅)

Go to your app's **Event Subscriptions** page on [Feishu Open Platform](https://open.feishu.cn/app).

**Required events:**

| Event | Event Key | Purpose |
|-------|-----------|---------|
| File edited | `drive.file.edit_v1` | Detect document edits |

**Optional events:**

| Event | Event Key | Purpose |
|-------|-----------|---------|
| Bitable record changed | `drive.file.bitable_record_changed_v1` | Task board integration |
| Bitable field changed | `drive.file.bitable_field_changed_v1` | Structure change logging |

### 3. Permissions (权限)

Your app needs these scopes:

| Permission | Scope | Purpose |
|------------|-------|---------|
| Read docs | `docx:document:readonly` | Read document content |
| Write docs | `docx:document` | Append replies to documents |
| Read drive events | `drive:drive` | Receive file edit events |

### 4. Connection Mode

The Feishu extension supports two connection modes:
- **WebSocket** (recommended) — persistent connection, real-time events
- **Webhook** — HTTP callback, requires public URL

WebSocket is configured by default in OpenClaw.

## Verification

After setup, edit a Feishu document and check:

1. OpenClaw logs should show: `drive.file.edit event: file=<token>...`
2. If the patch is applied: `triggered /hooks/agent for doc edit on <token>`
3. The AI should read and respond per the Doc Chat Protocol

## Troubleshooting

### No edit events received

- Check event subscriptions are approved (not just submitted)
- Ensure the app has been added to the document's permission list
- Check WebSocket connection status in OpenClaw logs

### Agent doesn't respond

- Verify `hooks.enabled: true` and `hooks.token` in openclaw.json
- Check that DOC_PROTOCOL.md exists in workspace
- Ensure the message uses the correct protocol format with 🟢 status

### Duplicate responses

- The patch includes anti-loop protection (skips bot's own edits)
- If you still see duplicates, check that `botOpenId` is correctly resolved
