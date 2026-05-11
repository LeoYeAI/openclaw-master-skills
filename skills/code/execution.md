# Execution Guidance

Reference for executing multi-step implementations.

## Recommended Flow

When user approves a step:
1. Execute that step
2. Verify it works
3. Report completion to user
4. Wait for user to approve next step

## Progress Tracking

Show user the current state:
```
- [DONE] Step 1 (completed)
- [WIP] Step 2 <- awaiting user approval
- [ ] Step 3
- [ ] Step 4
```

## When to Pause and Ask User

- Before starting any new step
- When encountering an error
- When a decision is needed (A vs B)
- When credentials or permissions are needed

## Error Handling

If an error occurs:
1. Report the error to user
2. Suggest possible fixes
3. Wait for user decision on how to proceed

## Patterns to Follow

- Report completion of each step
- Ask before proceeding to next step
- Let user decide retry strategy
- Keep user informed of progress
