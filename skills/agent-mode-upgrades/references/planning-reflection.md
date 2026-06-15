# Planning and Self-Reflection

The biggest gap in reactive agentic loops is making one-step-at-a-time decisions without a persistent plan. Modern agents (ReAct, Plan-and-Execute, ADaPT) insert explicit planning phases.

## Why It Matters

Without planning:
- Agent can wander on ambiguous multi-step tasks
- No decomposition of complex goals
- No self-correction until too late
- Burns through tool calls inefficiently

With planning:
- Complex goals become subtask sequences
- Progress is measurable against the plan
- Early detection of off-track execution
- More efficient tool usage

## Planning Phase

### When to Plan

Generate a plan when:
- User request involves 3+ steps
- Task is ambiguous or has multiple valid approaches
- Previous attempt failed and needs restructuring
- Complexity score exceeds threshold

Skip planning when:
- Single-step tasks (file read, simple search)
- Direct questions with clear answers
- Continuation of existing plan

### Plan Generation Prompt

```typescript
const PLAN_GENERATION_PROMPT = `
Given the user's goal, create a structured execution plan.

Goal: {userGoal}

Create a plan with:
1. Clear subtasks (2-7 steps)
2. Dependencies between steps
3. Success criteria for each step
4. Estimated complexity (low/medium/high)

Format:
## Plan
### Step 1: [Title]
- Action: [What to do]
- Dependencies: [None or Step N]
- Success: [How to know it's done]
- Complexity: [low/medium/high]

### Step 2: ...

## Notes
- [Any assumptions or risks]
`;
```

### Plan Structure

```typescript
interface TaskPlan {
  id: string;
  goal: string;
  steps: PlanStep[];
  assumptions: string[];
  createdAt: number;
  status: 'active' | 'completed' | 'abandoned';
}

interface PlanStep {
  id: string;
  title: string;
  action: string;
  dependencies: string[];  // Step IDs
  successCriteria: string;
  complexity: 'low' | 'medium' | 'high';
  status: 'pending' | 'in_progress' | 'complete' | 'failed' | 'skipped';
  result?: string;
}
```

## Reflection Phase

### When to Reflect

After each tool result, run a lightweight reflection:

```typescript
const REFLECTION_PROMPT = `
Given your plan and the last result, assess progress.

Plan: {currentPlan}
Last action: {lastAction}
Result: {toolResult}

Answer concisely:
1. Did the action succeed? (yes/no/partial)
2. Are you on track with the plan? (yes/no)
3. Should you adjust the plan? (continue/replan/escalate)
4. If replan: what changed?
`;
```

### Reflection Output

```typescript
interface ReflectionResult {
  actionSucceeded: boolean | 'partial';
  onTrack: boolean;
  decision: 'continue' | 'replan' | 'escalate';
  reason?: string;
}
```

### Replan Triggers

Trigger replanning when:
- Tool returns unexpected result
- Dependency assumption violated
- Better approach discovered
- User provides new information
- 3+ consecutive failures on same step

## Integration with OpenClaw

### Injection Point

In `src/agents/pi-embedded-runner/run/attempt.ts`, before calling `streamSimple`:

```typescript
// Check if planning is needed
const needsPlan = shouldGeneratePlan(params.prompt, existingPlan);
if (needsPlan) {
  const plan = await generatePlan({
    goal: params.prompt,
    context: sessionHistory,
    config: params.config,
  });
  // Inject plan into context
  sessionManager.addMessage({
    role: 'assistant',
    content: formatPlanForContext(plan),
  });
  // Store plan for reflection
  runState.currentPlan = plan;
}
```

### Reflection Injection

After tool execution completes in `pi-embedded-subscribe.ts`:

```typescript
// In tool result handler
if (runState.currentPlan && toolResult) {
  const reflection = await reflect({
    plan: runState.currentPlan,
    lastAction: toolCall,
    result: toolResult,
  });
  
  if (reflection.decision === 'replan') {
    runState.currentPlan = await replan(runState.currentPlan, reflection.reason);
  } else if (reflection.decision === 'escalate') {
    await requestHumanInput(reflection.reason);
  }
}
```

## Cost Considerations

Planning and reflection add LLM calls. Mitigate with:

1. **Caching**: Cache plans for similar goals
2. **Batching**: Combine reflection with next action prompt
3. **Thresholds**: Only plan for complex tasks
4. **Model selection**: Use faster/cheaper model for reflection

### Token Budget

| Component | Typical Tokens | When |
|-----------|----------------|------|
| Plan generation | 500-1500 | Once per complex task |
| Reflection | 100-300 | After each tool result |
| Replan | 300-800 | When needed (~10% of tasks) |

## Example Flow

```
User: "Deploy the new feature to staging"

[PLANNING]
Plan generated:
  Step 1: Check current branch and uncommitted changes
  Step 2: Run tests locally
  Step 3: Build Docker image
  Step 4: Push to registry
  Step 5: Update staging deployment
  Step 6: Verify deployment health

[EXECUTING Step 1]
Tool: exec "git status"
Result: "On branch feature-x, 2 files modified"

[REFLECTING]
- Action succeeded: yes
- On track: yes
- Decision: continue

[EXECUTING Step 2]
Tool: exec "npm test"
Result: "3 tests failed"

[REFLECTING]
- Action succeeded: no
- On track: no
- Decision: replan
- Reason: Tests failing, need to fix before deployment

[REPLANNING]
Revised plan:
  Step 1: ✓ Check branch (done)
  Step 2: Fix failing tests (new)
  Step 3: Run tests again
  Step 4-7: (original steps 2-5)
```

## Best Practices

1. **Keep plans shallow**: 2-7 steps max, can nest if needed
2. **Make success criteria concrete**: "File exists" not "Looks good"
3. **Include rollback steps**: For risky operations
4. **Time-box reflection**: Don't over-analyze simple results
5. **Log plans for debugging**: Invaluable for understanding agent behavior
