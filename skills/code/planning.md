# Planning Reference

Consult when breaking down a multi-step request.

## When to Plan
- Multiple files or components
- Dependencies between parts
- UI that needs visual verification
- User says "build", "create", "implement"

## Step Format
```
Step N: [What]
- Output: [What exists after]
- Test: [How to verify]
```

## Good Steps
- Clear output (file, endpoint, screen)
- Testable independently
- No ambiguity in what "done" means

## Bad Steps
- "Implement the thing" (vague output)
- No test defined
- Depends on undefined prior step

## Don't Plan
- One-liner functions
- Simple modifications
- Questions about existing code
