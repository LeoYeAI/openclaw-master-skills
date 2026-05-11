# Verification Reference

Consult when verifying implementations visually or with tests.

## Screenshots
- Wait for full page load (no spinners)
- Review yourself before sending
- Split long pages into 3-5 sections (~800px each)
- Caption each: "Hero", "Features", "Footer"

## Before Sending
```
[ ] Content loaded
[ ] Shows the specific change
[ ] No visual bugs
[ ] Caption explains what user sees
```

## Fix-Before-Send
If screenshot shows problem:
1. Fix code
2. Re-deploy
3. New screenshot
4. Still broken? -> back to 1
5. Fixed? -> now send

Never send "I noticed X is wrong, will fix" - fix first.

## No UI? Show Output

When verifying API endpoints, show actual output:
```
GET /api/users -> {"id": 1, "name": "test"}
```

Include actual response, not just "it works".

## Flows
Number sequential states: "1/4: Form", "2/4: Loading", "3/4: Error", "4/4: Success"
