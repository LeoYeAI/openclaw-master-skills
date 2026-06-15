# Proactive Context Management

Reactive compaction (triggered on overflow) is a last resort. For long-running autonomous work, proactive context management is critical.

## The Problem

Current approach:
- Keep every tool result in full
- Wait for context overflow error
- Then attempt emergency compaction

This fails because:
- Context fills fast on file-heavy tasks
- Compaction under pressure loses important details
- No relevance filtering — everything stays

## Proactive Strategies

### 1. Sliding Summarization

After every N iterations (or at threshold), summarize completed work:

```typescript
const CONTEXT_THRESHOLD = 0.7;  // 70% of max tokens
const SUMMARIZE_AFTER_ITERATIONS = 5;

async function maybeSummarize(context: Context): Promise<void> {
  const usage = context.tokenCount / context.maxTokens;
  
  if (usage > CONTEXT_THRESHOLD || context.iterationCount % SUMMARIZE_AFTER_ITERATIONS === 0) {
    const completedWork = extractCompletedWork(context);
    const summary = await summarizeWork(completedWork);
    
    // Replace detailed results with summary
    context.messages = [
      ...context.messages.filter(m => !isCompletedToolResult(m)),
      { role: 'system', content: `## Completed Work Summary\n${summary}` },
      ...context.messages.filter(m => isRecentOrActive(m)),
    ];
  }
}
```

### 2. Relevance-Gated Retrieval

Move completed subtask results to external store, retrieve on demand:

```typescript
interface WorkingMemory {
  store: Map<string, StoredContext>;
  
  async store(subtaskId: string, context: SubtaskContext): Promise<void>;
  async retrieve(subtaskIds: string[]): Promise<string>;
  async search(query: string, limit?: number): Promise<StoredContext[]>;
}

// After completing a subtask
if (taskStack.currentSubtask.status === 'complete') {
  const summary = await summarizeSubtaskResults(context, subtask);
  await workingMemory.store(subtask.id, {
    summary,
    artifacts: subtask.result?.artifacts,
    timestamp: Date.now(),
  });
  pruneDetailedResultsFromContext(context, subtask);
}

// Before starting a new subtask
const dependencies = taskStack.currentSubtask.dependencies;
if (dependencies.length > 0) {
  const relevantContext = await workingMemory.retrieve(dependencies);
  context.messages.push({
    role: 'system',
    content: `## Context from Dependencies\n${relevantContext}`,
  });
}
```

### 3. Smart Pruning Rules

```typescript
interface PruneRules {
  // Keep last N messages regardless
  keepLastMessages: number;  // default: 10
  
  // Keep messages newer than X ms
  keepRecentMs: number;  // default: 300000 (5 min)
  
  // Always keep these message types
  alwaysKeep: MessageType[];  // ['plan', 'error', 'human_input']
  
  // Prune tool results older than X ms
  pruneToolResultsAfterMs: number;  // default: 60000 (1 min)
  
  // Summarize instead of delete
  summarizeBeforePrune: boolean;  // default: true
}

function applyPruneRules(
  messages: Message[], 
  rules: PruneRules
): { kept: Message[]; summarized: string } {
  const now = Date.now();
  const kept: Message[] = [];
  const toPrune: Message[] = [];
  
  for (let i = 0; i < messages.length; i++) {
    const msg = messages[i];
    const age = now - msg.timestamp;
    const isRecent = age < rules.keepRecentMs;
    const isLastN = i >= messages.length - rules.keepLastMessages;
    const isProtected = rules.alwaysKeep.includes(msg.type);
    
    if (isRecent || isLastN || isProtected) {
      kept.push(msg);
    } else if (msg.type === 'tool_result' && age > rules.pruneToolResultsAfterMs) {
      toPrune.push(msg);
    } else {
      kept.push(msg);
    }
  }
  
  const summarized = rules.summarizeBeforePrune 
    ? summarizeMessages(toPrune)
    : '';
  
  return { kept, summarized };
}
```

## Token Budget Management

Track token usage proactively:

```typescript
interface TokenBudget {
  max: number;
  used: number;
  reserved: {
    systemPrompt: number;
    responseBuffer: number;  // Leave room for LLM response
    toolResults: number;     // Reserve for pending tool results
  };
  
  get available(): number {
    return this.max - this.used - Object.values(this.reserved).reduce((a, b) => a + b, 0);
  }
}

function canAddToContext(budget: TokenBudget, content: string): boolean {
  const tokens = estimateTokens(content);
  return tokens <= budget.available;
}

function addToContext(
  context: Context, 
  content: string,
  budget: TokenBudget
): boolean {
  const tokens = estimateTokens(content);
  
  if (tokens > budget.available) {
    // Try to make room
    const freed = pruneOldestToolResults(context, tokens - budget.available);
    if (freed < tokens - budget.available) {
      return false;  // Can't fit
    }
  }
  
  context.messages.push(content);
  budget.used += tokens;
  return true;
}
```

## Integration with Knowledge Graph

Use the existing SurrealDB memory for long-term context:

```typescript
// Store important facts from completed work
async function archiveToKnowledgeGraph(
  subtask: Task,
  result: TaskResult
): Promise<void> {
  // Extract facts worth remembering
  const facts = await extractFacts(subtask, result);
  
  for (const fact of facts) {
    await knowledge.store({
      content: fact.content,
      confidence: fact.confidence,
      source: `task:${subtask.id}`,
      tags: ['working_memory', subtask.title],
    });
  }
}

// Retrieve relevant knowledge for new subtask
async function retrieveRelevantKnowledge(
  subtask: Task
): Promise<string> {
  const facts = await knowledge.search(subtask.title, { limit: 5 });
  
  if (facts.length === 0) return '';
  
  return `## Relevant Knowledge\n${facts.map(f => `- ${f.content}`).join('\n')}`;
}
```

## Summarization Prompts

### Tool Result Summarization

```typescript
const TOOL_RESULT_SUMMARY_PROMPT = `
Summarize these tool results concisely.
Keep: errors, key findings, file paths created/modified, important values.
Drop: verbose output, duplicate info, formatting noise.

Tool Results:
{toolResults}

Summary (2-3 sentences max):
`;
```

### Work Session Summarization

```typescript
const WORK_SESSION_SUMMARY_PROMPT = `
Summarize what was accomplished in this work session.

Tasks completed: {completedTasks}
Tools used: {toolsUsed}
Files affected: {filesAffected}

Create a brief summary covering:
1. What was done
2. What was learned
3. What's still pending

Summary:
`;
```

## Implementation Priority

1. **Token tracking**: Know usage before overflow
2. **Tool result pruning**: Biggest context hog
3. **Subtask summarization**: When completing branches
4. **Knowledge graph archival**: For long-term recall
5. **Relevance retrieval**: For complex multi-part tasks

## OpenClaw Integration Points

| File | Change |
|------|--------|
| `src/agents/compaction.ts` | Add proactive triggers |
| `src/agents/pi-embedded-subscribe.ts` | Track tool result tokens |
| `src/agents/system-prompt.ts` | Inject working memory context |
| `src/agents/pi-embedded-runner/run/attempt.ts` | Token budget management |
