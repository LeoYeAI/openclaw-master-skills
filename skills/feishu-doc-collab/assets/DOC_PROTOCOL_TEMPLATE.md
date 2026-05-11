# 飞书文档对话协议 (Feishu Doc Chat Protocol)

## Message Format

Each message in the document is a message block, separated by `---`, with a header line and body.

### Header Format

```
> **SenderName** → **ReceiverName** | StatusFlag
```

### Status Flags

- 🔴 编辑中 (editing) — AI does NOT process this message (user is still typing)
- 🟢 完成 (done) — AI reads and responds to this message

**Core rule: AI only processes messages with 🟢 status.**

### Routing

- `→ AgentName` — addressed to a specific participant
- `→ all` — broadcast to all participants

### Parsing Rules

1. Read the full document
2. Find the last message block (from the end, delimited by `---`)
3. Extract the header: sender, receiver, status
4. If status is not 🟢 → do nothing
5. If sender is yourself → do nothing (anti-loop)
6. If receiver doesn't match your name and is not "all" → do nothing
7. If all checks pass → process the message and append your reply

## Participant Roster

Fill in your participants below:

| Name | ID | Type |
|------|-----|------|
| (Your name) | (open_id) | Human |
| (Agent name) | (open_id) | AI |

## Example Conversation

```markdown
---
> **Alice** → **MyBot** | 🟢 完成

Please summarize the Q1 sales data.

---
> **MyBot** → **Alice** | 🟢 完成

Here's the Q1 summary:
- Total revenue: ¥2.3M
- Growth: +15% YoY
- Top product: Widget Pro
```
