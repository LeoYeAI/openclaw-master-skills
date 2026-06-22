# Error Code Reference

## API Response Codes

| code | Type | Description | Recommended Action |
|------|------|-------------|-------------------|
| `SUCCESS` | Success | Operation succeeded | - |
| `CREATED` | Success | Resource created successfully | - |
| `VALIDATION_ERROR` | Client Error | Parameter validation failed | Check required parameters |
| `UNAUTHORIZED` | Auth Error | API Key invalid or missing | Check PLUME_API_KEY |
| `FORBIDDEN` | Permission Error | API Key disabled | Contact admin to enable Key |
| `NOT_FOUND` | Client Error | Resource not found | Check if task_id is correct |
| `INSUFFICIENT_CREDITS` | Business Error | Insufficient credits | Prompt user to top up |
| `CREDITS_ACCOUNT_NOT_FOUND` | Business Error | Credits account not found | Contact admin to create credits account |
| `CONCURRENT_MODIFICATION` | Concurrency Conflict | Optimistic lock conflict | Auto-retry |
| `UPLOAD_FAILED` | Server Error | R2 upload failed | Retry |
| `INTERNAL_ERROR` | Server Error | Internal error | Retry or contact admin |

## Task Status Codes

| status | Name | Description | Terminal? |
|--------|------|-------------|----------|
| 1 | Initialized | Task created, awaiting processing | No |
| 2 | Processing | Executor has picked up the task, processing | No |
| 3 | Success | Task completed, result field contains output | Yes |
| 4 | Failed | Task execution failed | Yes |
| 5 | Timeout | Task processing timed out (default 1 hour) | Yes |
| 6 | Cancelled | Task was cancelled | Yes |

## Polling Recommendations

- Polling interval: 3 seconds
- Max polling attempts: 60 (3 minutes total)
- Terminal state check: `status >= 3` means task has ended
- Success check: `status == 3`, result is in `data.result`
- Failure check: `status >= 4`, inform user of the reason

## Common Error Scenarios

### 1. API Key Not Configured
```
Error: PLUME_API_KEY environment variable not set
Action: Remind user to set PLUME_API_KEY in OpenClaw configuration
```

### 2. Insufficient Credits
```json
{ "success": false, "code": "INSUFFICIENT_CREDITS" }
Action: Inform user of insufficient credits, suggest topping up at Portal
```

### 3. Image Upload Failed
```json
{ "success": false, "code": "VALIDATION_ERROR", "error": { "details": { "file": "..." } } }
Possible causes: File too large (>20MB), unsupported format, corrupted file
```

### 4. Task Timeout
```
Polling for 3 minutes without completion
Action: Inform user the task is taking longer than expected, suggest checking back later
```
