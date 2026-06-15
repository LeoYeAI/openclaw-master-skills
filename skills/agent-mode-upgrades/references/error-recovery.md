# Semantic Error Recovery

The current retry loop handles auth rotation, failover, and compaction. But for true autonomous operation, the agent should interpret failures and adapt its approach.

## Beyond Retry

Current behavior:
```
Tool fails → Retry same call
Retry fails → Report error to user
```

Target behavior:
```
Tool fails → Diagnose cause
           → Generate alternative approach
           → Adapt and continue
           → Escalate only if alternatives exhausted
```

## Error Diagnosis

### Diagnosis Prompt

```typescript
const ERROR_DIAGNOSIS_PROMPT = `
A tool call failed. Diagnose the cause and suggest recovery.

Tool: {toolName}
Arguments: {arguments}
Error: {errorMessage}
Context: {relevantContext}

Analyze:
1. What likely caused this error?
2. Is this recoverable?
3. What alternative approaches could work?
4. Should we skip this and continue, or is it blocking?

Format:
Cause: [brief diagnosis]
Recoverable: [yes/no/maybe]
Strategy: [alternative_approach | skip_and_continue | escalate | retry_modified]
Alternative: [if strategy is alternative_approach, describe it]
Modified args: [if strategy is retry_modified, new arguments]
Skip reason: [if strategy is skip_and_continue, explain why it's safe]
`;
```

### Recovery Strategies

```typescript
type RecoveryStrategy = 
  | { type: 'alternative_approach'; newPlan: string }
  | { type: 'retry_modified'; modifiedArgs: Record<string, unknown> }
  | { type: 'skip_and_continue'; reason: string }
  | { type: 'escalate'; explanation: string }
  | { type: 'retry_same'; delay?: number };

interface ErrorDiagnosis {
  cause: string;
  recoverable: boolean | 'maybe';
  strategy: RecoveryStrategy;
}

async function diagnoseAndRecover(
  context: Context,
  toolCall: ToolCall,
  error: ToolError
): Promise<ErrorDiagnosis> {
  // First, try pattern matching for common errors
  const knownRecovery = matchKnownErrorPattern(error);
  if (knownRecovery) return knownRecovery;
  
  // For unknown errors, use LLM diagnosis
  const diagnosis = await llmDiagnose(context, toolCall, error);
  return diagnosis;
}
```

## Common Error Patterns

### File Operations

```typescript
const FILE_ERROR_PATTERNS: ErrorPattern[] = [
  {
    match: /ENOENT|no such file/i,
    strategy: async (ctx, tool, err) => {
      // File doesn't exist - check if we should create it
      if (tool.name === 'Read') {
        return {
          type: 'alternative_approach',
          newPlan: `File ${tool.arguments.path} doesn't exist. Check if we need to create it first or use a different path.`,
        };
      }
      if (tool.name === 'Edit') {
        return {
          type: 'retry_modified',
          modifiedArgs: { 
            ...tool.arguments,
            createIfMissing: true,
          },
        };
      }
      return { type: 'escalate', explanation: 'File not found' };
    },
  },
  {
    match: /EACCES|permission denied/i,
    strategy: () => ({
      type: 'alternative_approach',
      newPlan: 'Permission denied. Try with elevated privileges or use a different location.',
    }),
  },
  {
    match: /ENOSPC|no space left/i,
    strategy: () => ({
      type: 'escalate',
      explanation: 'Disk full. Cannot continue without human intervention.',
    }),
  },
];
```

### Network Operations

```typescript
const NETWORK_ERROR_PATTERNS: ErrorPattern[] = [
  {
    match: /ETIMEDOUT|timeout/i,
    strategy: () => ({
      type: 'retry_same',
      delay: 5000,  // Wait 5s before retry
    }),
  },
  {
    match: /ECONNREFUSED/i,
    strategy: (ctx, tool) => ({
      type: 'alternative_approach',
      newPlan: `Service at ${extractUrl(tool)} is not running. Check if it needs to be started first.`,
    }),
  },
  {
    match: /404|not found/i,
    strategy: (ctx, tool) => ({
      type: 'alternative_approach',
      newPlan: `Resource not found at ${extractUrl(tool)}. Verify the URL or search for the correct endpoint.`,
    }),
  },
  {
    match: /401|403|unauthorized|forbidden/i,
    strategy: () => ({
      type: 'escalate',
      explanation: 'Authentication required. Need credentials or permissions.',
    }),
  },
  {
    match: /429|rate limit/i,
    strategy: () => ({
      type: 'retry_same',
      delay: 60000,  // Wait 1 minute
    }),
  },
];
```

### Exec Operations

```typescript
const EXEC_ERROR_PATTERNS: ErrorPattern[] = [
  {
    match: /command not found/i,
    strategy: (ctx, tool) => {
      const cmd = (tool.arguments.command as string).split(' ')[0];
      return {
        type: 'alternative_approach',
        newPlan: `Command '${cmd}' not installed. Try installing it or use an alternative tool.`,
      };
    },
  },
  {
    match: /npm ERR!.*ERESOLVE/i,
    strategy: () => ({
      type: 'retry_modified',
      modifiedArgs: {
        command: 'npm install --legacy-peer-deps',
      },
    }),
  },
  {
    match: /git.*conflict/i,
    strategy: () => ({
      type: 'escalate',
      explanation: 'Git merge conflict requires manual resolution.',
    }),
  },
];
```

## Recovery Execution

```typescript
async function executeWithRecovery(
  context: Context,
  toolCall: ToolCall,
  maxAttempts: number = 3
): Promise<ToolResult> {
  let attempts = 0;
  let currentCall = toolCall;
  const tried = new Set<string>();
  
  while (attempts < maxAttempts) {
    attempts++;
    const callSignature = JSON.stringify(currentCall);
    
    // Prevent infinite loops
    if (tried.has(callSignature)) {
      return { error: true, message: 'Recovery loop detected' };
    }
    tried.add(callSignature);
    
    try {
      const result = await executeTool(currentCall);
      if (!result.error) return result;
      
      // Tool returned an error result
      const diagnosis = await diagnoseAndRecover(context, currentCall, result);
      
      switch (diagnosis.strategy.type) {
        case 'retry_same':
          if (diagnosis.strategy.delay) {
            await sleep(diagnosis.strategy.delay);
          }
          // currentCall stays the same
          break;
          
        case 'retry_modified':
          currentCall = {
            ...currentCall,
            arguments: diagnosis.strategy.modifiedArgs,
          };
          break;
          
        case 'alternative_approach':
          // Inject the new approach into context
          context.messages.push({
            role: 'assistant',
            content: `Previous approach failed. New plan: ${diagnosis.strategy.newPlan}`,
          });
          // Return to planning layer to generate new tool calls
          return {
            needsReplan: true,
            reason: diagnosis.strategy.newPlan,
          };
          
        case 'skip_and_continue':
          return {
            skipped: true,
            reason: diagnosis.strategy.reason,
          };
          
        case 'escalate':
          return {
            error: true,
            needsHuman: true,
            message: diagnosis.strategy.explanation,
          };
      }
      
    } catch (err) {
      // Unexpected exception
      const diagnosis = await diagnoseAndRecover(context, currentCall, {
        error: true,
        message: err.message,
      });
      
      if (diagnosis.strategy.type === 'escalate') {
        throw err;
      }
      // Apply recovery strategy...
    }
  }
  
  return {
    error: true,
    message: `Failed after ${maxAttempts} recovery attempts`,
  };
}
```

## Learning from Errors

Track error patterns for future sessions:

```typescript
interface ErrorRecord {
  toolName: string;
  errorPattern: string;
  successfulRecovery?: RecoveryStrategy;
  context: string;  // Summarized
  timestamp: number;
}

async function recordErrorRecovery(
  toolCall: ToolCall,
  error: ToolError,
  recovery: RecoveryStrategy,
  succeeded: boolean
): Promise<void> {
  if (succeeded && recovery.type !== 'escalate') {
    // Store successful recovery for future reference
    await knowledge.store({
      content: `When ${toolCall.name} fails with "${summarizeError(error)}", recovery strategy "${recovery.type}" works.`,
      confidence: 0.8,
      tags: ['error_recovery', toolCall.name],
    });
  }
}

async function findPreviousRecovery(
  toolCall: ToolCall,
  error: ToolError
): Promise<RecoveryStrategy | null> {
  const facts = await knowledge.search(
    `${toolCall.name} error recovery ${summarizeError(error)}`,
    { limit: 3, tags: ['error_recovery'] }
  );
  
  // Parse successful recovery from facts
  for (const fact of facts) {
    const strategy = parseRecoveryFromFact(fact.content);
    if (strategy) return strategy;
  }
  
  return null;
}
```

## OpenClaw Integration

### Error Handler Hook

In `pi-embedded-subscribe.handlers.tools.ts`:

```typescript
// Replace simple error handling
if (toolResult.error) {
  // Old: just report error
  // return { error: true, message: toolResult.message };
  
  // New: attempt recovery
  const recovery = await diagnoseAndRecover(context, toolCall, toolResult);
  
  switch (recovery.strategy.type) {
    case 'alternative_approach':
      // Signal to outer loop that replanning is needed
      state.needsReplan = true;
      state.replanReason = recovery.strategy.newPlan;
      break;
    // ... handle other strategies
  }
}
```

### Configuration

```yaml
agents:
  defaults:
    errorRecovery:
      enabled: true
      maxAttempts: 3
      learnFromErrors: true
      escalateAfterAttempts: 2
      retryDelayMs: 1000
```

## Best Practices

1. **Pattern match first**: Common errors have known solutions
2. **LLM diagnose second**: For novel errors
3. **Limit retry loops**: Max 3 attempts before escalating
4. **Track what works**: Build knowledge base of successful recoveries
5. **Fail gracefully**: Always have an escalation path
6. **Preserve context**: Don't lose work when recovering
