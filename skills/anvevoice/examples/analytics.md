# Example: Pulling Analytics

## User Prompt
> "How is my Support Bot performing this month?"

## Agent Actions

### Step 1: Get analytics overview

```json
{
  "tool": "get_analytics_overview",
  "arguments": {
    "bot_id": "abc-123",
    "from_date": "2025-02-01"
  }
}
```

### Step 2: Get feedback stats

```json
{
  "tool": "get_feedback_stats",
  "arguments": { "bot_id": "abc-123", "from_date": "2025-02-01" }
}
```

## Expected Responses

### Analytics Overview
```json
{
  "success": true,
  "data": {
    "bot_id": "abc-123",
    "totals": {
      "total_sessions": 342,
      "completed_sessions": 298,
      "abandoned_sessions": 44,
      "total_messages": 2156,
      "unique_visitors": 187
    }
  }
}
```

### Feedback Stats
```json
{
  "success": true,
  "data": {
    "total_rated": 89,
    "average_rating": 4.2,
    "satisfaction_rate": 78,
    "distribution": { "1": 3, "2": 5, "3": 12, "4": 31, "5": 38 }
  }
}
```

## Agent Response
> 📊 **Support Bot — February Performance**
>
> | Metric | Value |
> |--------|-------|
> | Total Sessions | 342 |
> | Completed | 298 (87%) |
> | Abandoned | 44 (13%) |
> | Unique Visitors | 187 |
> | Avg Rating | ⭐ 4.2/5 |
> | Satisfaction | 78% |
>
> The bot has a solid completion rate. The 13% abandonment rate could be improved — want me to run an improvement analysis?
