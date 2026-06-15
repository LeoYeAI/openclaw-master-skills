# Parallel Tool Execution

When the LLM emits multiple tool calls in a single response, executing them sequentially wastes time. Independent operations should run concurrently.

## The Win

For tasks like "read these 5 files" or "check these 3 APIs":
- Sequential: 5 × 500ms = 2500ms
- Parallel: max(500ms) = 500ms
- **5x speedup** for independent operations

## Dependency Classification

Before parallelizing, classify tool calls:

```typescript
interface ToolCall {
  id: string;
  name: string;
  arguments: Record<string, unknown>;
}

interface ClassifiedTools {
  parallel: ToolCall[];     // Can run concurrently
  sequential: ToolCall[];   // Must run in order
  dependencyGraph: Map<string, string[]>;  // toolId -> depends on toolIds
}

function classifyToolDependencies(toolCalls: ToolCall[]): ClassifiedTools {
  const graph = new Map<string, string[]>();
  const sequential: ToolCall[] = [];
  const parallel: ToolCall[] = [];
  
  for (let i = 0; i < toolCalls.length; i++) {
    const tool = toolCalls[i];
    const deps = findDependencies(tool, toolCalls.slice(0, i));
    
    if (deps.length > 0) {
      graph.set(tool.id, deps);
      sequential.push(tool);
    } else if (hasSideEffects(tool)) {
      // Side-effecting tools run sequentially for safety
      sequential.push(tool);
    } else {
      parallel.push(tool);
    }
  }
  
  return { parallel, sequential, dependencyGraph: graph };
}
```

## Dependency Detection

### Output → Input Dependencies

```typescript
function findDependencies(
  tool: ToolCall, 
  previousTools: ToolCall[]
): string[] {
  const deps: string[] = [];
  const argValues = Object.values(tool.arguments).map(String).join(' ');
  
  for (const prev of previousTools) {
    // Check if this tool's args reference previous tool's outputs
    if (referencesOutput(argValues, prev)) {
      deps.push(prev.id);
    }
    
    // Check for file path dependencies
    if (hasFileConflict(tool, prev)) {
      deps.push(prev.id);
    }
  }
  
  return deps;
}

function referencesOutput(args: string, prevTool: ToolCall): boolean {
  // Pattern: tool result placeholder
  if (args.includes(`{{${prevTool.id}}}`)) return true;
  if (args.includes(`result_of_${prevTool.name}`)) return true;
  return false;
}

function hasFileConflict(a: ToolCall, b: ToolCall): boolean {
  const aPath = extractFilePath(a);
  const bPath = extractFilePath(b);
  
  if (!aPath || !bPath) return false;
  
  // Same file = dependency
  if (aPath === bPath) return true;
  
  // Write after read on same file = dependency
  if (isWriteOp(a) && isReadOp(b) && aPath === bPath) return true;
  
  return false;
}
```

### Side Effect Classification

```typescript
const SIDE_EFFECT_TOOLS = new Set([
  'Write',
  'Edit', 
  'exec',  // Most exec commands have side effects
  'message',
  'browser',  // Can modify page state
]);

const READ_ONLY_TOOLS = new Set([
  'Read',
  'web_search',
  'web_fetch',
  'image',
  'session_status',
  'sessions_list',
  'sessions_history',
  'cron:list',
  'cron:status',
]);

function hasSideEffects(tool: ToolCall): boolean {
  if (READ_ONLY_TOOLS.has(tool.name)) return false;
  if (SIDE_EFFECT_TOOLS.has(tool.name)) return true;
  
  // exec is nuanced - check the command
  if (tool.name === 'exec') {
    return !isReadOnlyCommand(tool.arguments.command as string);
  }
  
  // Default: assume side effects (safer)
  return true;
}

function isReadOnlyCommand(cmd: string): boolean {
  const readOnlyPatterns = [
    /^(ls|cat|head|tail|grep|find|which|echo|pwd|date|whoami)/,
    /^git (status|log|diff|show|branch)/,
    /^(npm|yarn|pnpm) (list|outdated|info)/,
  ];
  return readOnlyPatterns.some(p => p.test(cmd.trim()));
}
```

## Execution Strategy

```typescript
async function executeToolCalls(
  toolCalls: ToolCall[],
  executor: (tool: ToolCall) => Promise<ToolResult>
): Promise<Map<string, ToolResult>> {
  const { parallel, sequential, dependencyGraph } = classifyToolDependencies(toolCalls);
  const results = new Map<string, ToolResult>();
  
  // Execute parallel tools concurrently
  if (parallel.length > 0) {
    const parallelResults = await Promise.all(
      parallel.map(async (tool) => {
        const result = await executor(tool);
        return { id: tool.id, result };
      })
    );
    
    for (const { id, result } of parallelResults) {
      results.set(id, result);
    }
  }
  
  // Execute sequential tools in dependency order
  const executed = new Set<string>();
  
  while (executed.size < sequential.length) {
    // Find tools whose dependencies are satisfied
    const ready = sequential.filter(tool => {
      if (executed.has(tool.id)) return false;
      const deps = dependencyGraph.get(tool.id) ?? [];
      return deps.every(d => results.has(d) || executed.has(d));
    });
    
    if (ready.length === 0 && executed.size < sequential.length) {
      throw new Error('Circular dependency detected in tool calls');
    }
    
    // Execute ready tools (could parallelize within this batch too)
    for (const tool of ready) {
      const result = await executor(tool);
      results.set(tool.id, result);
      executed.add(tool.id);
    }
  }
  
  return results;
}
```

## Concurrency Limits

Don't overwhelm the system:

```typescript
const MAX_CONCURRENT_TOOLS = 5;  // Configurable

async function executeParallelWithLimit(
  tools: ToolCall[],
  executor: (tool: ToolCall) => Promise<ToolResult>,
  limit: number = MAX_CONCURRENT_TOOLS
): Promise<Map<string, ToolResult>> {
  const results = new Map<string, ToolResult>();
  
  // Process in batches
  for (let i = 0; i < tools.length; i += limit) {
    const batch = tools.slice(i, i + limit);
    const batchResults = await Promise.all(
      batch.map(async (tool) => {
        const result = await executor(tool);
        return { id: tool.id, result };
      })
    );
    
    for (const { id, result } of batchResults) {
      results.set(id, result);
    }
  }
  
  return results;
}
```

## Error Handling

```typescript
async function executeWithErrorIsolation(
  tools: ToolCall[],
  executor: (tool: ToolCall) => Promise<ToolResult>
): Promise<Map<string, ToolResult>> {
  const results = await Promise.allSettled(
    tools.map(async (tool) => {
      const result = await executor(tool);
      return { id: tool.id, result };
    })
  );
  
  const resultMap = new Map<string, ToolResult>();
  
  for (const settled of results) {
    if (settled.status === 'fulfilled') {
      resultMap.set(settled.value.id, settled.value.result);
    } else {
      // Create error result for failed tool
      const toolId = /* extract from error context */;
      resultMap.set(toolId, {
        error: true,
        message: settled.reason.message,
      });
    }
  }
  
  return resultMap;
}
```

## OpenClaw Integration

### In `pi-embedded-subscribe.ts`

The current tool execution is in `pi-embedded-subscribe.handlers.tools.ts`. Modify to batch:

```typescript
// Current: sequential execution
for (const toolCall of toolCalls) {
  const result = await executeTool(toolCall);
  // ...
}

// New: parallel where possible
const classified = classifyToolDependencies(toolCalls);
const results = await executeToolCalls(toolCalls, executeTool);
// ...
```

### Configuration

Add to config schema:

```typescript
interface AgentConfig {
  // ...
  execution?: {
    parallelTools?: boolean;  // default: true
    maxConcurrentTools?: number;  // default: 5
    parallelizeReadOnly?: boolean;  // default: true
    parallelizeSideEffects?: boolean;  // default: false
  };
}
```

## Measurement

Track parallel execution efficiency:

```typescript
interface ExecutionMetrics {
  totalTools: number;
  parallelBatches: number;
  sequentialTools: number;
  wallTimeMs: number;
  sumToolTimeMs: number;  // If run sequentially
  speedup: number;  // sumToolTimeMs / wallTimeMs
}
```

Log for debugging:
```
Executed 5 tools: 3 parallel (1 batch), 2 sequential
Wall time: 650ms, Sequential would be: 2100ms, Speedup: 3.2x
```
