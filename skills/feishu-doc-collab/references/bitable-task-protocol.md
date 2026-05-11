# Bitable Task Board Protocol / 多维表格任务协作协议

Optional integration for structured task management alongside document collaboration.

## Overview

- **Document** = content layer (write, discuss, produce deliverables)
- **Bitable** = status layer (who does what, current progress, completion)

They work together: tasks in Bitable link to documents where the actual work happens.

## Bitable Field Schema

| Field Name | Type | Description |
|-----------|------|-------------|
| Task Summary | Text | One-line task description |
| Status | SingleSelect | Unread → Read → In Progress → Done → N/A |
| Created | DateTime | Auto-filled creation time |
| From | SingleSelect | Who created the task |
| To | MultiSelect | Who should handle it (supports multiple) |
| Priority | SingleSelect | Low / Medium / High / Urgent |
| Notes | Text | Details, processing results |
| Related Doc | URL | Link to the Feishu document |

## Status Flow

```
Unread → Read → In Progress → Done
                             → N/A (no action needed)
```

1. **Sender** creates task, status = "Unread"
2. **Receiver** sees it, changes to "Read"
3. **Receiver** starts work, changes to "In Progress"
4. **Receiver** finishes, changes to "Done", writes result in Notes
5. If no action needed, changes to "N/A"

## AI Processing Rules

When the AI receives a `bitable_record_changed` event:

1. Check if it's the receiver and status is "Unread" → auto-change to "Read"
2. If the task involves document work → open the Related Doc, process content
3. When done → update status to "Done", write results in Notes
4. If the change was made by the AI itself → ignore (anti-loop)

## Document + Bitable Linked Workflow

1. Sender creates a task in Bitable, fills in Related Doc URL
2. Sender writes detailed content/instructions in the linked document (using Doc Chat Protocol)
3. Receiver gets notified via Bitable event, opens the document
4. Receiver processes the document content, appends reply
5. Receiver updates Bitable status to "Done"
