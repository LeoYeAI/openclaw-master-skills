# Error Handling Guide

When errors occur, diagnose and act — never just show a raw error message to the user.

## API Error Codes

| Code | Meaning | Action |
|------|---------|--------|
| `4100` | Credit not enough | Tell user their balance is insufficient. Show current balance, suggest recharging at [topview.ai](https://www.topview.ai/dashboard/home). |
| `4007` | Exists unfinished task | A previous task is still running. Wait 30s and retry, or ask user if they want to cancel the previous task. |
| `4000` / `4001` / `4003` | Parameter error | Check the model's supported parameters (aspect ratio, resolution, duration). Fix and retry. |
| `5003` | Server busy | Wait 10–30s and retry. If persistent, suggest trying a different model. |
| `5000` / `5001` | Internal server error | Retry once. If it persists, suggest the user try again later or use the web UI. |
| `6001` | Security problem | The content may have triggered a safety filter. Suggest revising the prompt. |

## Task-Level Failures

| Situation | Action |
|-----------|--------|
| Task `status: fail` | Read `errorMsg`. Common causes: model service unavailable (try a different model), content policy violation (revise prompt). |
| Task timeout (exit code 2) | The task is likely still running. Resume polling with `query --task-id <id> --timeout 1200`. Do NOT resubmit — that wastes credits. |
| Partial success (`generatingCount > 1`) | Some sub-tasks may fail while others succeed. Check each video's `status`. Offer to retry only the failed ones. |
| Upload failure | Check file format (must be png/jpg/jpeg/bmp/webp/mp3/wav/m4a/mp4/avi/mov) and file size. Retry once. |

## Recovery Decision Tree

```
Error occurred
├─ API error code?
│  ├─ 4100 → Inform user: insufficient credits
│  ├─ 4007 → Wait and retry
│  ├─ 400x → Fix parameters, retry
│  └─ 500x → Retry once, then suggest trying later
├─ Task status = fail?
│  ├─ "Model service unavailable" → Try a different model
│  ├─ Content policy → Revise prompt
│  └─ Unknown → Retry once with same params
└─ Timeout?
   → Use `query --task-id <id>` to resume polling (NOT resubmit)
```
